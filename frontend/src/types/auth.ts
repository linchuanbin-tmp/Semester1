export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload extends LoginPayload {
  email?: string
}

export interface AuthUser {
  id: number
  username: string
}

export interface AuthResponse {
  token: string
  user: AuthUser
}
