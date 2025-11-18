import { defineStore } from 'pinia'

interface UserInfo {
  id: number
  username: string
}

interface AuthState {
  token: string | null
  user: UserInfo | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    setAuth(token: string, user: UserInfo) {
      this.token = token
      this.user = user
      localStorage.setItem('auth_token', token)
      localStorage.setItem('auth_user', JSON.stringify(user))
    },
    hydrate() {
      const storedToken = localStorage.getItem('auth_token')
      const storedUser = localStorage.getItem('auth_user')
      this.token = storedToken
      this.user = storedUser ? (JSON.parse(storedUser) as UserInfo) : null
    },
    clearAuth() {
      this.token = null
      this.user = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
    },
  },
})
