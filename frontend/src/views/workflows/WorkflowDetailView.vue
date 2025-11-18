<template>
  <div class="page">
    <div class="page-toolbar glass-panel">
      <el-page-header :content="title" :icon="null" @back="goBack" />
      <el-space>
        <el-button :loading="loading" plain @click="refresh">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button
          type="danger"
          plain
          :disabled="!canStop"
          :loading="stopping"
          @click="confirmStop"
        >
          <el-icon><Close /></el-icon>
          Stop task
        </el-button>
      </el-space>
    </div>

    <el-alert
      v-if="errorMessage"
      type="error"
      show-icon
      :closable="false"
      :title="errorMessage"
    />

    <el-skeleton :loading="loading" animated :rows="5">
      <template #template>
        <el-card shadow="never" class="meta-card">
          <el-skeleton-item variant="h3" style="width: 40%" />
          <el-skeleton-item variant="text" />
          <el-skeleton-item variant="text" />
        </el-card>
        <el-card class="messages-card">
          <el-skeleton-item variant="h3" style="width: 30%" />
          <el-skeleton-item v-for="n in 4" :key="n" variant="text" />
        </el-card>
      </template>

      <template #default>
        <!-- Task info section - full width on top -->
        <div class="meta-card glass-panel">
          <h3 class="section-title">Task info</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Task ID">{{ task?.id ?? "--" }}</el-descriptions-item>
            <el-descriptions-item label="Workflow">{{ workflow?.name ?? "--" }}</el-descriptions-item>
            <el-descriptions-item label="Strategy">{{ strategyLabel }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="statusTag(task?.status)">{{ task?.status ?? "--" }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Created">{{ formatDate(task?.created) }}</el-descriptions-item>
            <el-descriptions-item label="Finished">{{ formatDate(task?.finished) }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Conversation log section - full width below -->
        <div class="messages-card glass-panel">
          <div class="card-header">
            <div>
              <p class="eyebrow">Conversation log</p>
              <h3>Agent dialogue</h3>
            </div>
            <el-tag v-if="pollingActive" type="warning">Live</el-tag>
          </div>

          <el-empty v-if="displayMessages.length === 0" description="Waiting for agents" />
          <div v-else class="conversation-feed">
            <article
              v-for="(msg, index) in displayMessages"
              :key="msg.id"
              class="message-bubble"
              :class="{ 'user-message': isUserMessage(msg) }"
            >
              <div class="message-meta">
                <strong>{{ msg.agent_name }}</strong>
                <span class="role">{{ msg.agent_role }}</span>
                <span class="timestamp">{{ formatDate(msg.timestamp) }}</span>
              </div>
              <p class="message-copy">{{ msg.content }}</p>
            </article>
          </div>

          <!-- 追问功能区域 -->
          <div v-if="canFollowUp" class="follow-up-section">
            <el-divider>
              <el-icon><ChatDotRound /></el-icon>
              Continue conversation
            </el-divider>
            <div class="follow-up-input">
              <el-input
                v-model="followUpQuestion"
                type="textarea"
                :rows="3"
                placeholder="Ask a follow-up question based on the conversation above..."
                :disabled="submittingFollowUp"
                maxlength="1000"
                show-word-limit
                @keydown="handleKeydown"
              />
              <el-button
                type="primary"
                :loading="submittingFollowUp"
                :disabled="!canSubmitFollowUp"
                @click="submitFollowUp"
              >
                <el-icon><Promotion /></el-icon>
                Send
              </el-button>
            </div>
            <p class="follow-up-hint">
              <el-icon><Warning /></el-icon>
              Your follow-up question will be sent with {{ displayMessages.length }} previous messages to continue the dialogue.
            </p>
          </div>
        </div>
      </template>
    </el-skeleton>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import { Close, Refresh, ChatDotRound, Promotion, Warning } from "@element-plus/icons-vue"
import { usePolling } from "@/utils/polling"
import { workflowService } from "@/services/workflows"
import type { Message, Task, Workflow } from "@/types/workflow"

/* props & router */
const props = defineProps<{ id: string | number }>()
const router = useRouter()
const taskId = computed(() => Number(props.id))

/* 数据 */
const task   = ref<Task | null>(null)
const workflow = ref<Workflow | null>(null)
const messages = ref<Message[]>([])  // 从后端获取的原始消息
const displayMessages = ref<Message[]>([])  // 用于显示的消息（包含用户追问）
const loading  = ref(true)
const stopping = ref(false)
const errorMessage = ref("")

/* 追问功能相关 */
const followUpQuestion = ref("")
const submittingFollowUp = ref(false)

/* 轮询 */
const { start: startPolling, stop: stopPolling, isActive: pollingActive } = usePolling(async () => {
  await loadMessages()
})

/* 工具函数 */
const statusTag = (status?: string) => {
  switch (status) {
    case "running": return "warning"
    case "completed": return "success"
    case "failed":  return "danger"
    default:        return "info"
  }
}
const strategyLabel = computed(() => {
  const map: Record<string, string> = {
    round_robin: "Round-Robin",
    react_group: "ReAct Group",
    debate: "Debate",
    single_agent: "Single Agent",
  }
  return map[workflow.value?.strategy ?? ""] ?? "--"
})
const formatDate = (value?: string) => {
  if (!value) return "--"
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString("en")
}
const title = computed(() => `Task #${taskId.value || "--"}`)
const canStop = computed(() => ["pending", "running"].includes(task.value?.status ?? ""))

/* 判断是否为用户消息 - 用户消息显示在右侧，AI消息显示在左侧 */
const isUserMessage = (msg: Message) => {
  // 可以根据 agent_role 或 agent_name 来判断
  // 如果 agent_role 包含 "USER" 或者是特定的用户标识，则为用户消息
  return msg.agent_role?.toUpperCase().includes('USER') ||
         msg.agent_name?.toUpperCase().includes('USER')
}

/* 判断是否可以追问：任务已完成且有对话记录 */
const canFollowUp = computed(() =>
  task.value?.status === "completed" && displayMessages.value.length > 0
)

/* 判断是否可以提交追问 */
const canSubmitFollowUp = computed(() =>
  followUpQuestion.value.trim().length > 0 && !submittingFollowUp.value
)

/* 处理键盘快捷键 */
const handleKeydown = (event: KeyboardEvent) => {
  if (event.ctrlKey && event.key === 'Enter') {
    event.preventDefault()
    if (canSubmitFollowUp.value) {
      submitFollowUp()
    }
  }
}

/* 方法 */
const goBack = () => router.push({ name: "workflows" })

const loadTask = async () => {
  if (!taskId.value) return
  try {
    const t = await workflowService.getTask(taskId.value)
    task.value = t
    workflow.value = await workflowService.get(t.workflow)
  } catch (e: any) {
    errorMessage.value = e?.message ?? "Failed to load task"
  }
}

const loadMessages = async () => {
  if (!taskId.value) return
  try {
    const newMessages = await workflowService.getTaskMessages(taskId.value)

    // 🔧 过滤掉不应该显示的消息
    const filteredMessages = newMessages.filter(msg => {
      // 排除系统生成的初始提示消息
      const isSystemPrompt =
        msg.agent_role?.toUpperCase() === 'USER' &&
        (msg.content?.toLowerCase().includes("i'm ready to help") ||
         msg.content?.toLowerCase().includes("what would you like to talk about") ||
         msg.content?.toLowerCase().includes("how can i help") ||
         msg.content?.toLowerCase().includes("how may i assist"))

      // 排除时间戳异常的用户消息（用户消息不应该和AI消息同时出现）
      const hasAbnormalTimestamp = msg.agent_role?.toUpperCase() === 'USER' &&
        newMessages.some(otherMsg =>
          otherMsg.id !== msg.id &&
          otherMsg.agent_role !== 'USER' &&
          Math.abs(new Date(otherMsg.timestamp).getTime() -
                   new Date(msg.timestamp).getTime()) < 1000 // 1秒内
        )

      return !isSystemPrompt && !hasAbnormalTimestamp
    })

    messages.value = filteredMessages

    // 检查后端是否返回了用户消息（message_type === 'USER'）
    const hasUserMessages = filteredMessages.some(msg =>
      msg.agent_role?.toUpperCase() === 'USER' ||
      (msg as any).message_type === 'USER'
    )

    if (hasUserMessages) {
      // 后端已经保存了用户消息，直接使用后端数据
      displayMessages.value = [...filteredMessages]
    } else {
      // 后端没有保存用户消息，使用前端维护的 displayMessages
      if (displayMessages.value.length === 0) {
        displayMessages.value = [...filteredMessages]
      } else {
        // 找出新增的消息并去重添加
        filteredMessages.forEach(msg => {
          // 检查消息是否已存在（通过ID或内容+时间戳判断）
          const exists = displayMessages.value.some(dm =>
            dm.id === msg.id ||
            (dm.content === msg.content &&
             Math.abs(new Date(dm.timestamp).getTime() - new Date(msg.timestamp).getTime()) < 5000)
          )

          if (!exists) {
            displayMessages.value.push(msg)
          }
        })

        // 按时间戳重新排序
        displayMessages.value.sort((a, b) =>
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        )
      }
    }
  } catch (e: any) {
    errorMessage.value = e?.message ?? "Failed to load messages"
  }
}

const refresh = async () => {
  errorMessage.value = ""
  loading.value = true
  try {
    await loadTask()
    await loadMessages()
  } finally {
    loading.value = false
  }
}

const confirmStop = async () => {
  if (!taskId.value) return
  try {
    await ElMessageBox.confirm("Stop this task immediately?", "Confirm", { type: "warning" })
    stopping.value = true
    await workflowService.stopTask(taskId.value)
    ElMessage.success("Stop signal sent")
    refresh()
  } catch (e: any) {
    if (e === "cancel") return
    ElMessage.error(e?.message ?? "Stop failed")
  } finally {
    stopping.value = false
  }
}

/* 提交追问 */
const submitFollowUp = async () => {
  if (!followUpQuestion.value.trim() || !taskId.value) return

  const tempMessageId = Date.now() // 生成临时ID
  const userQuestion = followUpQuestion.value.trim()

  try {
    submittingFollowUp.value = true

    // 立即添加用户消息到显示列表（优化用户体验）
    const userMessage: Message = {
      id: tempMessageId,
      agent_name: 'You',
      agent_role: 'USER',
      content: userQuestion,
      timestamp: new Date().toISOString()
    }
    displayMessages.value.push(userMessage)

    // 清空输入框
    followUpQuestion.value = ""

    // 调用 continueTask 接口
    await workflowService.continueTask(
      taskId.value,
      userQuestion,
      messages.value
    )

    ElMessage.success("Follow-up question submitted successfully")

    // 刷新任务和消息
    // loadMessages 会自动处理去重
    await refresh()

  } catch (e: any) {
    ElMessage.error(e?.message ?? "Failed to submit follow-up question")

    // 如果失败，移除刚添加的用户消息
    displayMessages.value = displayMessages.value.filter(msg => msg.id !== tempMessageId)
  } finally {
    submittingFollowUp.value = false
  }
}

/* 生命周期 & 监听 */
watch(
  () => task.value?.status,
  (st) => {
    if (st && ["pending", "running"].includes(st)) startPolling()
    else stopPolling()
  },
  { immediate: true }
)

onMounted(refresh)
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1rem 1.5rem;
}

/* Task info section styles */
.meta-card {
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.section-title {
  margin: 0 0 1.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--brand-ink);
}

.meta-card :deep(.el-descriptions__body) {
  background: transparent;
}

/* Messages card styles */
.messages-card {
  min-height: 320px;
  padding: 1.25rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h3 {
  margin: 0.2rem 0 0;
  color: var(--brand-ink);
}

.conversation-feed {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* AI messages on the left, user messages on the right */
.message-bubble {
  padding: 1rem 1.25rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(15, 23, 42, 0.05);
  max-width: 75%;
  align-self: flex-start; /* AI messages default to left */
}

.message-bubble.user-message {
  align-self: flex-end; /* User messages on the right */
  background: rgba(77, 172, 138, 0.18);
  border-color: rgba(77, 172, 138, 0.35);
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  margin-bottom: 0.35rem;
  color: rgba(31, 42, 55, 0.7);
}

.message-meta .role {
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.7rem;
  color: rgba(31, 42, 55, 0.5);
}

.message-meta .timestamp {
  margin-left: auto;
  font-size: 0.75rem;
  color: rgba(31, 42, 55, 0.4);
}

.message-copy {
  margin: 0;
  white-space: pre-wrap;
  font-family: 'Inter', 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.95rem;
  color: var(--brand-ink);
}

/* 追问功能样式 */
.follow-up-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
}

.follow-up-section .el-divider {
  margin: 0 0 1.5rem 0;
}

.follow-up-section .el-divider__text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.95);
  padding: 0 1rem;
  color: var(--brand-ink);
  font-weight: 500;
}

.follow-up-input {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.follow-up-input .el-textarea {
  flex: 1;
}

.follow-up-input .el-button {
  flex-shrink: 0;
  height: auto;
  padding: 0.75rem 1.5rem;
}

.follow-up-hint {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  color: rgba(31, 42, 55, 0.6);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.follow-up-hint .el-icon {
  font-size: 1rem;
  color: rgba(77, 172, 138, 0.8);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .follow-up-input {
    flex-direction: column;
  }

  .follow-up-input .el-button {
    width: 100%;
  }

  .message-bubble {
    max-width: 85%;
  }
}
</style>