import { InputHTMLAttributes, forwardRef } from "react"
import { clsx } from "clsx"

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input ref={ref} className={clsx("bg-neutral-900/60 border border-neutral-800 rounded-xl px-3 h-10 text-sm outline-none focus:ring-2 focus:ring-indigo-500/50", className)} {...props} />
  )
)
Input.displayName = "Input"
