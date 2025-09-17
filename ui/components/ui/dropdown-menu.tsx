"use client"
import { PropsWithChildren, useState } from "react"

export function DropdownMenu({ trigger, children }: PropsWithChildren<{ trigger: React.ReactNode }>) {
  const [open, setOpen] = useState(false)
  return (
    <div className="relative inline-block text-left">
      <span onClick={()=>setOpen(o=>!o)} className="cursor-pointer inline-flex">{trigger}</span>
      {open && (
        <div className="absolute right-0 mt-2 w-48 rounded-xl border border-neutral-800 bg-neutral-900/60 shadow-lg p-1">
          {children}
        </div>
      )}
    </div>
  )
}

export function DropdownItem({ onSelect, children }: { onSelect?: ()=>void; children: React.ReactNode }) {
  return (
    <button onClick={onSelect} className="w-full text-left px-3 py-2 rounded-lg hover:bg-neutral-800 text-sm">
      {children}
    </button>
  )
}
