<template>
  <el-container class="app-layout">
    <div class="grid-overlay" />
    <el-aside width="280px" class="app-aside glass-panel">
      <div class="brand">
        <div class="logo-mark">Δ</div>
        <div>
          <p class="brand-title">D-AgentHub</p>
          <p class="brand-subtitle">Multi-Agent Room</p>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="menu"
        @select="handleSelect"
        background-color="transparent"
        text-color="#1f2a37"
        active-text-color="#0f172a"
      >
        <el-menu-item index="workflows">
          <el-icon><DataAnalysis /></el-icon>
          <span>Workflow board</span>
        </el-menu-item>
        <el-menu-item index="workflow-new">
          <el-icon><EditPen /></el-icon>
          <span>Create workflow</span>
        </el-menu-item>
      </el-menu>
      <div class="aside-footer text-muted">
        <p>Need help?</p>
        <small>Press <kbd>F1</kbd> or visit our docs.</small>
      </div>
    </el-aside>
    <el-container>
      <el-header class="app-header glass-panel">
        <div class="header-copy">
          <p class="eyebrow">Live mission control</p>
          <h1>Agent Orchestration Console</h1>
          <p class="text-muted">
            Monitor, iterate and deploy multi-agent workflows with real-time telemetry.
          </p>
        </div>
        <div class="user-actions">
          <el-tag type="success" effect="plain">Online</el-tag>
          <el-divider direction="vertical" />
          <el-dropdown>
            <span class="el-dropdown-link">
              {{ userLabel }}
              <el-icon class="caret"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">Sign out</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="app-main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, DataAnalysis, EditPen } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const activeMenu = computed(() => {
  if (!route.name) return 'workflows'
  if (route.name === 'workflow-detail') return 'workflows'
  return route.name as string
})

const userLabel = computed(() => auth.user?.username ?? 'Guest')

const handleSelect = (index: string) => {
  if (index === route.name) return
  router.push({ name: index as never }).catch(() => {})
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('Sign out from current account?', 'Confirm', {
      confirmButtonText: 'Sign out',
      cancelButtonText: 'Cancel',
      type: 'warning',
    })
    auth.clearAuth()
    ElMessage.success('Signed out')
    router.replace({ name: 'login' })
  } catch (error) {
    // user canceled
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  position: relative;
}

.app-aside {
  margin: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  background: linear-gradient(180deg, #fefefe 0%, #f6faf6 100%);
  padding: 1.5rem 1.75rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 0.5rem;
}

.logo-mark {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #8dd6c2, #8bb8ff);
  display: grid;
  place-items: center;
  font-weight: 700;
  font-size: 1.25rem;
  color: #0f172a;
}

.brand-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: var(--brand-ink);
}

.brand-subtitle {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(31, 42, 55, 0.55);
}

.brand-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.4rem;
  font-size: 0.8rem;
  color: rgba(31, 42, 55, 0.7);
}

.brand-meta > p {
  margin: 0 0.5rem 0 0;
  line-height: 1;
}

.brand-meta :deep(.el-tag) {
  border-radius: 999px;
  border-color: rgba(31, 42, 55, 0.15);
  color: var(--brand-ink);
  display: inline-flex;
  align-items: center;
  height: 24px;
  line-height: 24px;
  padding: 0 10px;
  vertical-align: middle;
}

.menu {
  border-right: none;
  flex: 1;
  background: transparent;
}

.menu :deep(.el-menu-item) {
  border-radius: 12px;
}

.menu :deep(.el-menu-item.is-active) {
  background: rgba(77, 172, 138, 0.25);
}

.aside-footer {
  font-size: 0.85rem;
  line-height: 1.4;
}

.app-header {
  margin: 1.25rem 1.25rem 0.5rem 1.25rem;
  padding: 2rem 1.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  min-width: 0; /* 允许 flex 容器收缩 */
  overflow: visible; /* 允许内容可见 */
  min-height: 120px; /* 确保有足够的高度 */
}

.header-copy {
  min-width: 0; /* 允许 flex 子元素收缩 */
  flex: 1; /* 允许在需要时收缩 */
  overflow: visible; /* 确保内容可见 */
  position: relative; /* 确保定位正常 */
  z-index: 1; /* 确保在最上层 */
}

.header-copy .eyebrow {
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.8rem;
  color: rgba(31, 42, 55, 0.7);
  word-break: break-word;
  overflow-wrap: break-word;
  font-weight: 600;
  display: block;
  visibility: visible;
  line-height: 1.5;
}

.header-copy h1 {
  margin: 0.2rem 0;
  font-size: 1.6rem;
  font-weight: 600;
  color: var(--brand-ink);
  word-break: break-word;
  overflow-wrap: break-word;
  line-height: 1.3;
}

.header-copy p {
  margin: 0.35rem 0 0;
  line-height: 1.4;
  overflow-wrap: break-word;
  word-spacing: normal;
}

.header-copy p.text-muted {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

@media (max-width: 1000px) {
  .header-copy p.text-muted {
    white-space: normal;
    word-break: keep-all;
    overflow-wrap: anywhere;
  }
}

 .user-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--brand-ink);
}

.caret {
  font-size: 0.9rem;
}

.app-main {
  padding: 0.75rem 1.25rem 1.25rem 1.25rem;
}

@media (max-width: 960px) {
  .app-layout {
    flex-direction: column;
  }

  .app-aside {
    margin: 1rem;
  }

  .app-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .header-copy {
    max-width: 100%;
  }

  .header-copy h1 {
    font-size: 1.4rem;
  }
}

@media (max-width: 768px) {
  .header-copy h1 {
    font-size: 1.2rem;
  }

  .header-copy p {
    font-size: 0.9rem;
  }
}
</style>
