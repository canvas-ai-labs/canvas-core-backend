import { PropsWithChildren } from "react"

export function ScrollArea({ children, className }: PropsWithChildren<{ className?: string }>) {
  return <div className={`overflow-auto ${className ?? ''}`}>{children}</div>
}
