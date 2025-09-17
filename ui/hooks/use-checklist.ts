"use client"
import { useEffect, useMemo, useState } from "react"

export type Todo = { id:string; title:string; done:boolean; createdAt:string }

const KEY = "canvas-ai-checklist"

export function useChecklist() {
  const [items, setItems] = useState<Todo[]>([])
  useEffect(() => {
    try {
      const raw = localStorage.getItem(KEY)
      if (raw) setItems(JSON.parse(raw))
    } catch {}
  }, [])
  useEffect(() => {
    try { localStorage.setItem(KEY, JSON.stringify(items)) } catch {}
  }, [items])

  const api = useMemo(() => ({
    items,
    add(title: string) {
      const t: Todo = { id: crypto.randomUUID(), title, done: false, createdAt: new Date().toISOString() }
      setItems(prev => [t, ...prev])
    },
    toggle(id: string) { setItems(prev => prev.map(t => t.id===id? { ...t, done: !t.done }: t)) },
    remove(id: string) { setItems(prev => prev.filter(t => t.id!==id)) },
    update(id: string, patch: Partial<Todo>) { setItems(prev => prev.map(t => t.id===id? { ...t, ...patch }: t)) },
    clear() { setItems([]) },
  }), [items])

  return api
}
