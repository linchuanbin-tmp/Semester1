export type Strategy = "round_robin" | "react_group" | "debate" | "single_agent"

export interface Agent {
  id: number
  name: string
  role: string
  prompt_template: string
}

export interface Workflow {
  id: number
  name: string
  strategy: Strategy
  created: string
  status?: string
  task_count?: number
  latest_task_id?: number
  latest_task_status?: string
}

export interface Task {
  id: number
  workflow: number
  description: string
  status: string
  created: string
  finished?: string
}

export interface Message {
  id: number
  agent_name: string
  agent_role: string
  content: string
  timestamp: string
}

export interface CreateWorkflowPayload {
  name: string
  strategy: Strategy
  description: string
  file_url?: string
}

export type CreateWorkflowResponse = Workflow & { task_id: number }
