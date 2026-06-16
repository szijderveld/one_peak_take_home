import type { ReactNode } from 'react'

const COLS: Record<number, string> = {
  2: 'grid-cols-2',
  3: 'grid-cols-3',
  4: 'grid-cols-2 sm:grid-cols-4',
}

/** A lined grid of stat cells — the 1px lines are the `bg-line` showing through
 * a `gap-px`. Used by the company metric grid and the market-shape stats. */
export function StatGrid({ cols = 3, children }: { cols?: number; children: ReactNode }) {
  return (
    <div className={`grid gap-px overflow-hidden rounded-xl border border-line bg-line ${COLS[cols] ?? 'grid-cols-3'}`}>
      {children}
    </div>
  )
}

export function Stat({ value, label, sub }: { value: ReactNode; label: string; sub?: string }) {
  return (
    <div className="bg-white p-4">
      <div className="metric-value">{value}</div>
      <div className="metric-label">{label}</div>
      {sub && <div className="mt-0.5 text-[11px] text-gray-400">{sub}</div>}
    </div>
  )
}
