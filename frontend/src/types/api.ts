export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

export type PaginationMeta = {
  page: number
  pageSize: number
  total: number
}
