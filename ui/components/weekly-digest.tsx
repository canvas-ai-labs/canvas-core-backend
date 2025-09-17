"use client"
"use client"
import { useMemo, useState } from "react"
import type { Todo } from "@/hooks/use-checklist"

type Assignment = { assignment_id:number; course_id:number; name?:string; due_at?:string; html_url?:string }

function fmtDate(s?: string) {
  if (!s) return ""
  const d = new Date(s)
  return d.toLocaleString(undefined, { weekday:"short", month:"short", day:"numeric", hour:"2-digit", minute:"2-digit" })
}

function buildHtml(assignments: Assignment[], todos: Todo[]): string {
  const upcoming = assignments
    .filter(a => a.due_at && new Date(a.due_at) <= new Date(Date.now()+7*86400000))
    .sort((a,b) => new Date(a.due_at ?? 0).getTime() - new Date(b.due_at ?? 0).getTime())

  const todoList = todos.filter(t => !t.done)

  const items = upcoming.map(a => `
    <li>
    <strong>${a.name ?? `Assignment #${a.assignment_id}`}</strong>
      ${a.html_url ? ` - <a href="${a.html_url}">link</a>` : ""}
      <div style="color:#6b7280;font-size:12px">Due: ${fmtDate(a.due_at)}</div>
    </li>
  `).join("\n")

  const todoItems = todoList.map(t => `<li>${t.title}</li>`).join("\n")

  return `<!doctype html>
  <html>
  <head><meta charSet="utf-8"><title>Weekly Digest</title></head>
  <body style="font-family:ui-sans-serif,system-ui;line-height:1.4;padding:16px;background:#0b0b0c;color:#e5e7eb">
    <h1 style="font-size:20px;margin:0 0 8px">Your Weekly Digest</h1>
    <p style="color:#9ca3af;margin:0 0 16px">Here’s what’s coming up this week.</p>
    <h2 style="font-size:16px;margin:16px 0 8px">Upcoming Assignments</h2>
    ${upcoming.length ? `<ul>${items}</ul>` : `<div style="color:#9ca3af">No assignments due this week.</div>`}
    <h2 style="font-size:16px;margin:16px 0 8px">Todo</h2>
    ${todoList.length ? `<ul>${todoItems}</ul>` : `<div style="color:#9ca3af">No open todos.</div>`}
  </body>
  </html>`
}

export function WeeklyDigest({ assignments, todos }: { assignments: Assignment[]; todos: Todo[] }) {
  const [copied, setCopied] = useState(false)
  const [downloaded, setDownloaded] = useState(false)
  const html = useMemo(() => buildHtml(assignments, todos), [assignments, todos])

  const onCopy = async () => {
    await navigator.clipboard.writeText(html)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }
  const onDownload = () => {
    const blob = new Blob([html], { type: "text/html" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "weekly-digest.html"
    a.click()
    URL.revokeObjectURL(url)
    setDownloaded(true)
    setTimeout(() => setDownloaded(false), 1500)
  }

  return (
    <div className="space-x-2 relative">
      <button onClick={onCopy} className="px-4 py-2 rounded-full bg-neutral-800 hover:bg-neutral-700 text-sm transition">{copied ? "Copied" : "Copy HTML"}</button>
      <button onClick={onDownload} className="px-4 py-2 rounded-full bg-neutral-800 hover:bg-neutral-700 text-sm transition">Download .html</button>
      <div className="absolute right-0 -top-8 text-xs text-neutral-300">
        {copied ? <span className="bg-neutral-800/80 px-2 py-1 rounded-md">Copied to clipboard</span> : null}
        {downloaded ? <span className="bg-neutral-800/80 px-2 py-1 rounded-md">Download started</span> : null}
      </div>
    </div>
  )
}
