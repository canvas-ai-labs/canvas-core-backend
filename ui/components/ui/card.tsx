import { PropsWithChildren } from "react"
import { clsx } from "clsx"

export function Card({ children, className }: PropsWithChildren<{ className?: string }>) {
  return <div className={clsx("bg-neutral-900/60 border border-neutral-800 rounded-2xl", className)}>{children}</div>
}

export function CardHeader({ children, className }: PropsWithChildren<{ className?: string }>) {
  return <div className={clsx("p-5 border-b border-neutral-800", className)}>{children}</div>
}

export function CardContent({ children, className }: PropsWithChildren<{ className?: string }>) {
  return <div className={clsx("p-5", className)}>{children}</div>
}
