"use client"
import { useEffect, useRef, useState } from "react"

export function CountUp({ value, duration = 600, className }: { value: number; duration?: number; className?: string }) {
  const [display, setDisplay] = useState(0)
  const startRef = useRef<number | null>(null)
  const fromRef = useRef(0)

  useEffect(() => {
    let raf = 0
    fromRef.current = display
    startRef.current = null
    const start = (ts: number) => {
      if (startRef.current == null) startRef.current = ts
      const elapsed = ts - startRef.current
      const t = Math.min(1, elapsed / duration)
      // ease-out cubic
      const eased = 1 - Math.pow(1 - t, 3)
      const next = Math.round(fromRef.current + (value - fromRef.current) * eased)
      setDisplay(next)
      if (t < 1) raf = requestAnimationFrame(start)
    }
    raf = requestAnimationFrame(start)
    return () => cancelAnimationFrame(raf)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, duration])

  return <span className={className}>{display}</span>
}
