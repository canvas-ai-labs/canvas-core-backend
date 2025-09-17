"use client"
import { useId, useState, PropsWithChildren, ReactNode } from "react"

export function Tabs({ tabs, initial = 0, onChange }: { tabs: { label: string; content: ReactNode }[]; initial?: number; onChange?: (i:number)=>void }) {
  const [idx, setIdx] = useState(initial)
  const id = useId()
  return (
    <div>
      <div role="tablist" aria-label="Tabs" className="flex gap-2 p-1 bg-neutral-900/60 rounded-xl border border-neutral-800">
        {tabs.map((t, i) => (
          <button
            key={i}
            id={`${id}-tab-${i}`}
            role="tab"
            aria-selected={idx === i}
            aria-controls={`${id}-panel-${i}`}
            tabIndex={idx === i ? 0 : -1}
            onClick={() => { setIdx(i); onChange?.(i) }}
            className={`px-3 py-2 rounded-lg text-sm ${idx===i? 'bg-indigo-500 text-white':'text-neutral-300 hover:bg-neutral-800'}`}
          >{t.label}</button>
        ))}
      </div>
      <div className="mt-3">
        {tabs.map((t, i) => (
          <div key={i} id={`${id}-panel-${i}`} role="tabpanel" aria-labelledby={`${id}-tab-${i}`} hidden={idx!==i}>
            {t.content}
          </div>
        ))}
      </div>
    </div>
  )
}
