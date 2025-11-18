<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>Sign in to D-AgentHub</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="form.password" type="password" show-password autocomplete="current-password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            Sign in
          </el-button>
          <el-button link type="primary" @click="goRegister">Create account</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { authService } from '@/services/auth'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: 'Username is required', trigger: 'blur' }],
  password: [{ required: true, message: 'Password is required', trigger: 'blur' }],
}

watchEffect(() => {
  if (auth.isAuthenticated) {
    router.replace({ name: 'workflows' })
  }
})

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      loading.value = true
      const result = await authService.login({ ...form })
      auth.setAuth(result.token, result.user)
      const redirect = (route.query.redirect as string) ?? '/'
      router.replace(redirect)
      ElMessage.success('Signed in')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Sign-in failed'
      ElMessage.error(message)
    } finally {
      loading.value = false
    }
  })
}

const goRegister = () => {
  router.push({ name: 'register' })
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: radial-gradient(circle at top, #2563eb22, transparent 60%);
}

.login-card {
  width: 380px;
  padding: 1.5rem 2rem 2rem;
}

.login-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  font-weight: 600;
}
</style>
