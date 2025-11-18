import axios from "axios"

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE ?? "/api",
  timeout: 20000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token")
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = "Bearer " + token
  }
  return config
})

http.interceptors.response.use(
  (response) => {
    const payload = response.data
    if (payload && typeof payload === "object" && "code" in payload) {
      if ((payload as { code: number }).code === 0) {
        return (payload as { data: unknown }).data
      }
      const message = (payload as { msg?: string }).msg ?? "Request failed"
      return Promise.reject(new Error(message))
    }
    return payload
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth_token")
      localStorage.removeItem("auth_user")
    }
    return Promise.reject(error)
  },
)

export default http
