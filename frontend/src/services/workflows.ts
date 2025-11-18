import http from "./http"
import type {
  CreateWorkflowPayload,
  CreateWorkflowResponse,
  Message,
  Task,
  Workflow,
} from "@/types/workflow"

export const workflowService = {
  list(): Promise<Workflow[]> {
    return http.get<Workflow[]>("/workflows") as unknown as Promise<Workflow[]>
  },
  create(payload: CreateWorkflowPayload): Promise<CreateWorkflowResponse> {
    return http.post<CreateWorkflowResponse>("/workflows", payload) as unknown as Promise<CreateWorkflowResponse>
  },
  get(id: number): Promise<Workflow> {
    return http.get(`/workflows/${id}/detail`) as Promise<Workflow>
  },
  remove(id: number): Promise<void> {
    return http.delete(`/workflows/${id}`) as unknown as Promise<void>
  },
  getTask(taskId: number): Promise<Task> {
    return http.get<Task>(`/tasks/${taskId}`) as unknown as Promise<Task>
  },
  getTaskMessages(taskId: number, page = 1, pageSize = 50): Promise<Message[]> {
    return http.get<Message[]>(`/tasks/${taskId}/messages`, {
      params: { page, page_size: pageSize },
    }) as unknown as Promise<Message[]>
  },
  stopTask(taskId: number): Promise<void> {
    return http.post(`/tasks/${taskId}/stop`) as unknown as Promise<void>
  },

  // 追问
  continueTask(taskId: number, newQuestion: string, context?: Message[]): Promise<CreateWorkflowResponse> {
    return http.post<CreateWorkflowResponse>(`/tasks/${taskId}/continue`, {
      question: newQuestion,
      context: context,
    }) as unknown as Promise<CreateWorkflowResponse>
  },
}