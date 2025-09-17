import { PropsWithChildren } from "react"
import { clsx } from "clsx"

export function Badge({ children, className }: PropsWithChildren<{ className?: string }>) {
  return <span className={clsx("inline-flex items-center rounded-md bg-neutral-800 px-2 py-0.5 text-xs text-neutral-300", className)}>{children}</span>
}
