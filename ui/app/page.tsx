"use client"
import { useEffect, useMemo, useState } from "react"
import { Calendar } from "@/components/calendar"
import { Checklist } from "@/components/checklist"
import { WorkloadChart } from "@/components/workload-chart"
import { WeeklyDigest } from "@/components/weekly-digest"
import { useChecklist } from "@/hooks/use-checklist"
import { getAssignments, getCourses } from "@/lib/api"
import { CountUp } from "@/components/count-up"
import type { Course } from "@/types"

// Types per spec
type Assignment = { course_id:number; assignment_id:number; name?:string; due_at?:string }
type Todo = { id:string; title:string; done:boolean; createdAt:string }

export default function Page() {
  const checklist = useChecklist()
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string|undefined>()

  const fetchAll = async () => {
    try {
      setLoading(true)
  const [c, a] = await Promise.all([getCourses(), getAssignments()])
  const listA: Assignment[] = Array.isArray(a?.assignments) ? a.assignments : (a ?? [])
  const listC: Course[] = Array.isArray(c?.courses) ? c.courses as Course[] : []
  setAssignments(listA)
  setCourses(listC)
      setError(undefined)
    } catch (e:any) {
      setError(e?.message ?? "Failed to load")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAll()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const upcoming = useMemo(() => {
    const now = Date.now()
    const week = now + 7*86400000
    return assignments.filter(a => a.due_at && new Date(a.due_at).getTime() <= week)
  }, [assignments])

  const coursesCount = courses.length
  const assignmentsCount = assignments.length
  const upcomingCount = upcoming.length

  return (
    <main className="bg-neutral-950 text-neutral-200 min-h-screen">
      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div>
            <h1 className="text-3xl md:text-4xl font-semibold tracking-tight">Canvas AI Labs</h1>
            <p className="text-neutral-400 mt-1 text-sm">Your coursework, at a glance.</p>
          </div>
          <button
            className="bg-indigo-500 hover:bg-indigo-400 text-white rounded-full px-4 py-2 text-sm transition"
            onClick={fetchAll}
          >Refresh</button>
        </div>
        {error ? (
          <div className="bg-red-500/10 text-red-400 border border-red-500/30 rounded-xl p-3 text-sm flex items-center justify-between">
            <span>Failed to fetch data: {error}</span>
            <button
              className="px-2 py-1 rounded-lg border border-red-500/30 text-red-300 hover:bg-red-500/10 transition"
              onClick={() => { setError(undefined); fetchAll() }}
            >Retry</button>
          </div>
        ) : null}

      {/* Stats row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 shadow-sm hover:border-neutral-700 hover:bg-neutral-900 transition">
            <div className="text-sm text-neutral-400">Courses</div>
            <div className="mt-1 text-3xl font-semibold">
              {loading ? <span className="inline-block w-12 h-7 bg-neutral-800/60 rounded" /> : <CountUp value={coursesCount} />}
            </div>
          </div>
          <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 shadow-sm hover:border-neutral-700 hover:bg-neutral-900 transition">
            <div className="text-sm text-neutral-400">Assignments</div>
            <div className="mt-1 text-3xl font-semibold">
              {loading ? <span className="inline-block w-12 h-7 bg-neutral-800/60 rounded" /> : <CountUp value={assignmentsCount} />}
            </div>
          </div>
          <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 shadow-sm hover:border-neutral-700 hover:bg-neutral-900 transition">
            <div className="text-sm text-neutral-400">Upcoming Deadlines</div>
            <div className="mt-1 text-3xl font-semibold">
              {loading ? <span className="inline-block w-12 h-7 bg-neutral-800/60 rounded" /> : <CountUp value={upcomingCount} />}
            </div>
          </div>
          <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 shadow-sm hover:border-neutral-700 hover:bg-neutral-900 transition">
            <div className="text-sm text-neutral-400">Scheduled Jobs</div>
            <div className="mt-1 text-3xl font-semibold">3</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <section className="md:col-span-2 rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 shadow-sm hover:border-neutral-700 hover:bg-neutral-900 transition">
          <h2 className="text-lg font-medium mb-3">Calendar</h2>
          {loading ? (
            <div className="space-y-2">
              <div className="h-8 bg-neutral-800/60 rounded-md" />
              <div className="h-20 bg-neutral-800/60 rounded-md" />
            </div>
          ) : (
            <Calendar assignments={assignments} />
          )}
          </section>
          <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 shadow-sm hover:border-neutral-700 hover:bg-neutral-900 transition">
            <h2 className="text-lg font-medium mb-3">Checklist</h2>
            <Checklist assignments={assignments} />
          </section>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 shadow-sm hover:border-neutral-700 hover:bg-neutral-900 transition md:col-span-2">
          <h2 className="text-lg font-medium mb-3">Workload (next 8 weeks)</h2>
          <WorkloadChart assignments={assignments} />
          </section>
          <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 shadow-sm hover:border-neutral-700 hover:bg-neutral-900 transition">
            <h2 className="text-lg font-medium mb-3">Weekly Digest</h2>
            <WeeklyDigest assignments={upcoming} todos={checklist.items as unknown as Todo[]} />
          </section>
        </div>
      </div>
    </main>
  )
}
