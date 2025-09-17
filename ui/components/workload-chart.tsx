"use client"
"use client"
import { useMemo } from "react"

type Assignment = { course_id:number; assignment_id:number; name?:string; due_at?:string }

function isoWeek(d: Date) {
  const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
  const dayNum = date.getUTCDay() || 7
  date.setUTCDate(date.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(),0,1))
  return `${date.getUTCFullYear()}-W${String(Math.ceil((((date.getTime()-yearStart.getTime())/86400000)+1)/7)).padStart(2,'0')}`
}

export function WorkloadChart({ assignments }: { assignments: Assignment[] }) {
  const data = useMemo(() => {
    const map = new Map<string, Map<number, number>>()
    const now = new Date()
    const weeks: string[] = []
    for (let i=0;i<8;i++) { // next 8 weeks
      const d = new Date(now); d.setDate(d.getDate() + i*7)
      weeks.push(isoWeek(d))
    }
    for (const a of assignments) {
      if (!a.due_at) continue
      const w = isoWeek(new Date(a.due_at))
      if (!weeks.includes(w)) continue
      if (!map.has(w)) map.set(w, new Map())
      const courseMap = map.get(w)!
      courseMap.set(a.course_id, (courseMap.get(a.course_id) ?? 0)+1)
    }
    return weeks.map(w => ({ week: w, totals: map.get(w) ?? new Map<number, number>() }))
  }, [assignments])

  const courses = useMemo(() => {
    const set = new Set<number>()
    for (const a of assignments) set.add(a.course_id)
    return Array.from(set.values()).sort()
  }, [assignments])

  return (
    <div>
      {data.length === 0 ? (
        <div className="text-neutral-400 text-sm">No workload data available.</div>
      ) : (
        <div>
          <div className="flex items-center gap-2 mb-2 text-xs">
            {courses.map(cid => (
              <span key={cid} className="inline-flex items-center gap-1"><span className="inline-block w-3 h-3 rounded-sm" style={{backgroundColor: `hsl(${(cid*53)%360} 70% 50%)`}} /> Course {cid}</span>
            ))}
          </div>
          <div className="grid grid-cols-8 gap-3">
            {data.map(d => (
              <div key={d.week} className="flex flex-col items-stretch">
                <div className="h-28 w-7 bg-neutral-800 rounded-md overflow-hidden flex flex-col-reverse hover:border hover:border-neutral-700 transition">
                  {courses.map(cid => {
                    const v = d.totals.get(cid) ?? 0
                    if (!v) return null
                    return <div key={cid} className="w-full" style={{height: `${v*14}px`, backgroundColor: `hsl(${(cid*53)%360} 70% 50%)`}} title={`Week ${d.week} • Course ${cid}: ${v}`} />
                  })}
                </div>
                <div className="text-[10px] text-neutral-400 mt-1 text-center">{d.week.replace("-W"," W")}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
