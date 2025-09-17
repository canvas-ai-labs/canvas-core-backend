"use client"
import { PropsWithChildren, useState } from "react"

export function Dialog({ trigger, children }: PropsWithChildren<{ trigger: React.ReactNode }>) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <span onClick={()=>setOpen(true)} className="inline-flex cursor-pointer">{trigger}</span>
      {open && (
        <div role="dialog" aria-modal className="fixed inset-0 flex items-center justify-center bg-black/70">
          <div className="card max-w-3xl w-full" onClick={e=>e.stopPropagation()}>
            <div className="p-4">
              <button aria-label="Close" onClick={()=>setOpen(false)} className="float-right text-neutral-400 hover:text-white">✕</button>
              <div className="clear-both" />
              {children}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
