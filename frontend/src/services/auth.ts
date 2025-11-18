import http from "./http"
import type { AuthResponse, LoginPayload, RegisterPayload } from "@/types/auth"

export const authService = {
  async login(payload: LoginPayload): Promise<AuthResponse> {
    const data = await http.post<AuthResponse>("/auth/login", payload)
    return data as unknown as AuthResponse
  },
  async register(payload: RegisterPayload): Promise<AuthResponse> {
    const data = await http.post<AuthResponse>("/auth/register", payload)
    return data as unknown as AuthResponse
  },
}