<template>
  <div class="page">
    <div class="page-toolbar glass-panel">
      <div>
        <p class="eyebrow">Live overview</p>
        <h2>Workflow dashboard</h2>
        <p class="text-muted">Keep an eye on agent pipelines, status signals and turn-around time.</p>
      </div>
      <el-space wrap>
        <el-button :loading="loading" @click="fetchWorkflows" plain>
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-divider direction="vertical" />
        <el-button type="primary" @click="goCreate">
          <el-icon><Plus /></el-icon>
          New workflow
        </el-button>
      </el-space>
    </div>

    <div class="insights">
      <div v-for="metric in metrics" :key="metric.title" class="insight-card glass-panel">
        <p class="title">{{ metric.title }}</p>
        <p class="value">{{ metric.value }}</p>
        <p class="caption text-muted">{{ metric.caption }}</p>
      </div>
    </div>

    <el-card shadow="hover" class="glass-panel">
      <el-empty v-if="!loading && workflows.length === 0" description="No workflows yet" />
      <el-table v-else :data="workflows" stripe :loading="loading">
        <el-table-column prop="name" label="Name" min-width="180" />
        <el-table-column label="Strategy" min-width="150">
          <template #default="{ row }">
            <el-tag>{{ formatStrategy(row.strategy) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Latest status" min-width="160">
          <template #default="{ row }">
            <el-tag :type="statusTag(displayStatus(row))">
              {{ displayStatus(row) ?? 'n/a' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created" label="Created" min-width="200">
          <template #default="{ row }">
            {{ formatDate(row.created) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button size="small" :disabled="!row.latest_task_id" @click="openDetail(row)">
                <el-icon><View /></el-icon>
                Detail
              </el-button>
              <el-button size="small" type="danger" plain @click="confirmDelete(row)">
                <el-icon><Delete /></el-icon>
                Delete
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import { Delete, Plus, Refresh, View } from "@element-plus/icons-vue"
import type { Workflow } from "@/types/workflow"
import { workflowService } from "@/services/workflows"

const router = useRouter()
const workflows = ref<Workflow[]>([])
const loading = ref(false)

const metrics = computed(() => {
  const total = workflows.value.length
  const running = workflows.value.filter((w) => w.latest_task_status === "running").length
  const completed = workflows.value.filter((w) => w.latest_task_status === "completed").length
  const singleAgent = workflows.value.filter((w) => w.strategy === "single_agent").length
  const diversity = new Set(workflows.value.map((w) => w.strategy)).size
  return [
    { title: "Active workflows", value: running, caption: "Currently executing across agents" },
    { title: "Completed today", value: completed, caption: "Latest runs marked as completed" },
    { title: "Single agent ratio", value: total ? `${Math.round((singleAgent / total) * 100)}%` : "0%", caption: "Lightweight requests routed to a single brain" },
    { title: "Strategy diversity", value: diversity, caption: "Distinct collaboration patterns online" },
  ]
})

const strategyLabels: Record<string, string> = {
  round_robin: "Round-Robin",
  react_group: "ReAct Group",
  debate: "Debate",
  single_agent: "Single Agent",
}

const statusTag = (status?: string) => {
  switch (status) {
    case "running":
      return "warning"
    case "completed":
      return "success"
    case "failed":
      return "danger"
    default:
      return "info"
  }
}

const displayStatus = (row: Workflow) => row.latest_task_status ?? row.status ?? undefined

const formatStrategy = (strategy: string) => strategyLabels[strategy] ?? strategy

const formatDate = (value: string) => {
  if (!value) return "--"
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date)
}

const fetchWorkflows = async () => {
  try {
    loading.value = true
    workflows.value = await workflowService.list()
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load workflows"
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const goCreate = () => {
  router.push({ name: "workflow-new" })
}

const openDetail = (row: Workflow) => {
  if (!row.latest_task_id) {
    ElMessage.warning("This workflow has not generated a task yet")
    return
  }
  router.push({ name: "workflow-detail", params: { id: row.latest_task_id } })
}

const confirmDelete = async (row: Workflow) => {
  try {
    await ElMessageBox.confirm(`Delete workflow "${row.name}"?`, "Confirm", {
      confirmButtonText: "Delete",
      cancelButtonText: "Cancel",
      type: "warning",
    })
    await workflowService.remove(row.id)
    ElMessage.success("Workflow deleted")
    fetchWorkflows()
  } catch (error) {
    if (error === "cancel") return
    const message = error instanceof Error ? error.message : "Deletion aborted"
    ElMessage.error(message)
  }
}

onMounted(fetchWorkflows)
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
}

.page-toolbar .eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.75rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.65);
}

.page-toolbar h2 {
  margin: 0.2rem 0;
  color: var(--brand-ink);
}

.page-toolbar :deep(.el-space) {
  align-items: center;
}

.insights {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 1rem;
}

.insight-card {
  padding: 1.25rem;
}

.insight-card .title {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(31, 42, 55, 0.7);
}

.insight-card .value {
  margin: 0.35rem 0 0.1rem;
  font-size: 2rem;
  font-weight: 600;
  color: var(--brand-ink);
}

.insight-card .caption {
  margin: 0;
  font-size: 0.8rem;
}

:deep(.el-card) {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(15, 23, 42, 0.05);
}

:deep(.el-table),
:deep(.el-table__inner-wrapper) {
  background: transparent;
  color: var(--brand-ink);
}

:deep(.el-table tr) {
  background: transparent;
}

:deep(.el-table th.el-table__cell) {
  background: transparent;
  color: rgba(31, 42, 55, 0.6);
  border-bottom-color: rgba(15, 23, 42, 0.08);
}

:deep(.el-table td.el-table__cell) {
  border-bottom-color: rgba(15, 23, 42, 0.05);
}
</style>
