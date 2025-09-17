"use client"
import { useMemo, useState } from "react"
import { addDays, endOfMonth, fmt, inRange, startOfToday } from "@/lib/date"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"

type Assignment = { course_id:number; assignment_id:number; name?:string; due_at?:string }

const ranges = [
  { key: "day", label: "Day", days: 1 },
  { key: "3d", label: "3-Day", days: 3 },
  { key: "7d", label: "7-Day", days: 7 },
  { key: "month", label: "Month", days: "month" as const },
] as const

export function Calendar({ assignments }: { assignments: Assignment[] }) {
  const [sel, setSel] = useState<typeof ranges[number]["key"]>("7d")
  const { from, to } = useMemo(() => {
    const today = startOfToday()
    const r = ranges.find(r => r.key===sel)!
    if (r.days === "month") return { from: today, to: endOfMonth(today) }
    return { from: today, to: addDays(today, r.days as number) }
  }, [sel])

  const grouped = useMemo(() => {
    const map = new Map<string, Assignment[]>()
    for (const a of assignments) {
      if (!a.due_at || !inRange(a.due_at, from, to)) continue
      const d = new Date(a.due_at)
      const k = d.toISOString().slice(0,10)
      if (!map.has(k)) map.set(k, [])
      map.get(k)!.push(a)
    }
    return Array.from(map.entries()).sort(([a],[b]) => a.localeCompare(b))
  }, [assignments, from, to])

  return (
    <div>
      <div className="flex gap-2 mb-3">
        {ranges.map(r => (
          <Button key={r.key} variant={sel===r.key?"default":"outline"} size="sm" onClick={()=>setSel(r.key)} aria-label={`Show ${r.label}`}>
            {r.label}
          </Button>
        ))}
      </div>

      {grouped.length === 0 ? (
        <div className="text-neutral-400 text-sm flex items-center justify-center h-24">No assignments in this range</div>
      ) : (
        <ul className="space-y-4">
          {grouped.map(([date, items]) => (
            <li key={date} className="space-y-2">
              <div className="text-sm text-neutral-400">{new Date(date).toLocaleDateString()}</div>
              <ul className="space-y-2">
                {items.map((a) => (
                  <li key={a.assignment_id} className="bg-neutral-800 px-4 py-3 rounded-xl hover:bg-neutral-700 transition">
                    <div className="flex items-center justify-between">
                      <div className="truncate font-medium">{a.name ?? `Assignment`}</div>
                      <div className="text-neutral-400 text-xs ml-3">{fmt(a.due_at) || "No due date"}</div>
                    </div>
                    <div className="text-indigo-400 text-sm mt-1">Course {a.course_id}</div>
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
