"use client"
import { useState } from "react"
import { useChecklist } from "@/hooks/use-checklist"

type Assignment = { assignment_id:number; name?:string }

export function Checklist({ assignments }: { assignments: Assignment[] }) {
  const list = useChecklist()
  const [title, setTitle] = useState("")

  const add = () => {
    const t = title.trim()
    if (!t) return
    list.add(t)
    setTitle("")
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          className="flex-1 bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 text-sm outline-none focus:border-neutral-600"
          placeholder="Add a task…"
          value={title}
          onChange={e=>setTitle(e.target.value)}
          onKeyDown={e=> e.key==='Enter' && add()}
          aria-label="Add todo"
        />
        <button className="bg-indigo-500 hover:bg-indigo-400 text-white rounded-full px-4 py-2 text-sm transition" onClick={add}>Add</button>
      </div>

      {list.items.length === 0 ? (
        <div className="text-neutral-400 text-sm">No todos yet. Add your first task.</div>
      ) : (
        <ul className="space-y-2">
          {list.items.map(item => (
            <li key={item.id} className="flex items-center gap-2">
              <input id={`todo-${item.id}`} aria-label="Mark done" type="checkbox" checked={item.done} onChange={()=>list.toggle(item.id)} className="peer h-4 w-4" />
              <input
                className="flex-1 bg-transparent border-b border-transparent focus:border-neutral-700 outline-none text-sm peer-checked:line-through peer-checked:text-neutral-500"
                value={item.title}
                onChange={e=>list.update(item.id, { title: e.target.value })}
              />
              <button
                className="px-2 py-1 rounded-lg text-neutral-300 hover:bg-neutral-800 transition"
                onClick={()=>list.remove(item.id)}
                aria-label="Delete"
              >Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
