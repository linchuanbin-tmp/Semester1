<template>
  <div class="not-found">
    <el-result icon="warning" title="Page not found" sub-title="The route you visited does not exist.">
      <template #extra>
        <el-button type="primary" @click="goHome">Back to dashboard</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push({ name: 'workflows' })
}
</script>

<style scoped>
.not-found {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f9fafb;
}
</style>
