export type Assignment = {
  course_id: number
  assignment_id: number
  name?: string
  due_at?: string
  html_url?: string
}

export type Todo = {
  id: string
  title: string
  done: boolean
  createdAt: string
}

export type Course = {
  id: number
  name?: string | null
  term: string
  account_id?: number | null
}
