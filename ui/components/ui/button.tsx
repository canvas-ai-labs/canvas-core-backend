import { ButtonHTMLAttributes, forwardRef } from "react"
import { clsx } from "clsx"

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "outline" | "ghost"
  size?: "sm" | "md" | "lg"
}

export const Button = forwardRef<HTMLButtonElement, Props>(
  ({ className, variant = "default", size = "md", ...props }, ref) => {
    const base = "inline-flex items-center justify-center font-medium rounded-xl transition-transform focus:outline-none focus:ring-2 focus:ring-indigo-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
    const variants = {
      default: "bg-indigo-500 text-white hover:bg-indigo-400 active:scale-[0.99]",
      outline: "border border-neutral-800 bg-transparent hover:bg-neutral-900/50",
      ghost: "hover:bg-neutral-900/50",
    } as const
    const sizes = {
      sm: "h-8 px-3 text-sm",
      md: "h-10 px-4",
      lg: "h-12 px-6 text-lg",
    } as const
    return (
      <button ref={ref} className={clsx(base, variants[variant], sizes[size], className)} {...props} />
    )
  }
)
Button.displayName = "Button"
