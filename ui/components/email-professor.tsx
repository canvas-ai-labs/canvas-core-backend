"use client"
import { Button } from "./ui/button"
import { Mail } from "lucide-react"
import { getCourseStaffEmails } from "@/lib/api"

export function EmailProfessor({ courseId, assignmentName }: { courseId: number; assignmentName?: string }) {
  const onClick = async () => {
    try {
      const { emails } = await getCourseStaffEmails(courseId)
      const to = encodeURIComponent((emails ?? []).join(","))
      const subject = encodeURIComponent(`[Course ${courseId}] Question about ${assignmentName ?? "assignment"}`)
      const body = encodeURIComponent(
        `Hello Professor/TA,%0D%0A%0D%0AI have a question about ${assignmentName ?? "the assignment"} in course ${courseId}.%0D%0A%0D%0A[Your question here]%0D%0A%0D%0AThanks,%0D%0A[Your Name]`
      )
      const href = `mailto:${to}?subject=${subject}&body=${body}`
      window.location.href = href
    } catch {
      // Fallback even if emails call fails
      const subject = encodeURIComponent(`[Course ${courseId}] Question about ${assignmentName ?? "assignment"}`)
      const body = encodeURIComponent(`Hello Professor/TA,%0D%0A%0D%0AI have a question...`)
      window.location.href = `mailto:?subject=${subject}&body=${body}`
    }
  }
  return (
    <Button variant="outline" size="sm" onClick={onClick} aria-label="Email Professor">
      <Mail size={16} className="mr-2" /> Email
    </Button>
  )
}
