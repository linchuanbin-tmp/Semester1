<template>
  <div class="page">
    <el-page-header content="Launch new workflow" :icon="null" @back="goBack" />
    <div class="composer glass-panel">
      <div class="form-panel">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="140" status-icon>
          <el-form-item label="Workflow name" prop="name">
            <el-input v-model="form.name" placeholder="Give it a friendly name" maxlength="100" show-word-limit />
          </el-form-item>
          <el-form-item label="Strategy" prop="strategy">
            <el-select v-model="form.strategy" placeholder="Select a coordination strategy">
              <el-option
                v-for="option in strategyOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              >
                <div class="option">
                  <strong>{{ option.label }}</strong>
                  <small>{{ option.desc }}</small>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="Task description" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="5"
              maxlength="1500"
              show-word-limit
              placeholder="Describe the user goal or attach instructions"
            />
          </el-form-item>
          <el-form-item>
            <el-space>
              <el-button type="primary" :loading="submitting" @click="handleSubmit">
                Submit task
              </el-button>
              <el-button @click="resetForm">Reset</el-button>
            </el-space>
          </el-form-item>
        </el-form>
      </div>
      <aside class="insight-panel">
        <h3>Strategy tips</h3>
        <ul>
          <li><strong>Single agent:</strong> Quick responses, ideal for FAQs or brief analysis.</li>
          <li><strong>Round-Robin:</strong> Sequential story building for long-form outputs.</li>
          <li><strong>ReAct Group:</strong> Pair with datasets for tool-assisted reasoning.</li>
          <li><strong>Debate:</strong> Capture contrasting opinions before judging.</li>
        </ul>
        <p class="text-muted">All workflows inherit auditing, status tracking and stop controls automatically.</p>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue"
import { useRouter } from "vue-router"
import type { FormInstance, FormRules } from "element-plus"
import { ElMessage } from "element-plus"
import type { CreateWorkflowPayload, Strategy } from "@/types/workflow"
import { workflowService } from "@/services/workflows"

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)

const strategyOptions: Array<{ value: Strategy; label: string; desc: string }> = [
  { value: "single_agent", label: "Single Agent", desc: "Direct LLM chat" },
  { value: "round_robin", label: "Round-Robin", desc: "Multi-agent relay for long documents" },
  { value: "react_group", label: "ReAct Group", desc: "Structured data cleanup with tool calls" },
  { value: "debate", label: "Debate", desc: "Pro/Con agents argue and judge summarizes" },
]

const form = reactive<CreateWorkflowPayload>({
  name: "",
  strategy: "single_agent",
  description: "",
})

const rules: FormRules = {
  name: [{ required: true, message: "Name is required", trigger: "blur" }],
  strategy: [{ required: true, message: "Select a strategy", trigger: "change" }],
  description: [{ required: true, message: "Please describe the task", trigger: "blur" }],
}

const goBack = () => {
  router.back()
}

const resetForm = () => {
  form.name = ""
  form.strategy = "single_agent"
  form.description = ""
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      submitting.value = true
      const payload: CreateWorkflowPayload = {
        name: form.name,
        strategy: form.strategy,
        description: form.description,
      }
      const response = await workflowService.create(payload)
      const taskId = response?.task_id
      if (taskId) {
        ElMessage.success("Workflow submitted")
        router.push({ name: "workflow-detail", params: { id: taskId } })
      } else {
        ElMessage.warning("Backend did not return a task id yet")
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Submission failed"
      ElMessage.error(message)
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.composer {
  padding: 1.5rem;
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(250px, 1fr);
  gap: 2rem;
}

.form-panel :deep(.el-form-item__label) {
  color: rgba(31, 42, 55, 0.9);
  font-weight: 500;
}
.option {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.option small {
  color: rgba(255, 255, 255, 0.55);
}

.insight-panel {
  background: rgba(255, 255, 255, 0.9);
  border: 1px dashed rgba(15, 23, 42, 0.12);
  border-radius: 16px;
  padding: 1.25rem;
  color: var(--brand-ink);
}

.insight-panel h3 {
  margin-top: 0;
  color: var(--brand-ink);
}

.insight-panel ul {
  margin: 0 0 1rem;
  padding-left: 1.1rem;
  color: rgba(31, 42, 55, 0.8);
  line-height: 1.5;
}

.insight-panel li {
  margin-bottom: 0.5rem;
}

@media (max-width: 900px) {
  .composer {
    grid-template-columns: 1fr;
  }
}
</style>