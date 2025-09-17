"use client"
import { PropsWithChildren } from "react"

export function Tooltip({ content, children }: PropsWithChildren<{ content: string }>) {
  // Minimal, accessible fallback using native title
  return <span title={content}>{children}</span>
}
