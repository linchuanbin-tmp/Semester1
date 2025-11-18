<template>
  <div class="register-page">
    <el-card class="register-card">
      <h2>Create an account</h2>
      <el-alert
        title="Fill in the fields below to start using the orchestration console."
        type="info"
        show-icon
        class="mb-3"
      />
      <el-form
        ref="formRef"
        label-position="top"
        :model="form"
        :rules="rules"
        status-icon
        @submit.prevent
      >
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" placeholder="Choose a unique username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" placeholder="Optional contact email" autocomplete="email" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="At least 6 characters"
            autocomplete="new-password"
          />
        </el-form-item>
        <el-form-item>
          <el-space>
            <el-button type="primary" :loading="loading" @click="handleSubmit">Create account</el-button>
            <el-button link type="primary" @click="goLogin">Back to sign in</el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { authService } from '@/services/auth'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({
  username: '',
  email: '',
  password: '',
})

const rules: FormRules = {
  username: [
    { required: true, message: 'Username is required', trigger: 'blur' },
    { min: 3, message: 'At least 3 characters', trigger: 'blur' },
  ],
  email: [{ type: 'email', message: 'Please enter a valid email', trigger: 'blur' }],
  password: [
    { required: true, message: 'Password is required', trigger: 'blur' },
    { min: 6, message: 'At least 6 characters', trigger: 'blur' },
  ],
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
      const payload = {
        username: form.username.trim(),
        password: form.password,
        ...(form.email.trim() ? { email: form.email.trim() } : {}),
      }
      const result = await authService.register(payload)
      auth.setAuth(result.token, result.user)
      ElMessage.success('Account created')
      router.replace({ name: 'workflows' })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Registration failed'
      ElMessage.error(message)
    } finally {
      loading.value = false
    }
  })
}

const goLogin = () => {
  router.push({ name: 'login' })
}
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f9fafb;
}

.register-card {
  width: 420px;
  padding: 1.5rem 2rem 2rem;
}

.register-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.mb-3 {
  margin-bottom: 1rem;
}
</style>
