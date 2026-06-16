import { useState } from 'react'
import type { Company, Space } from '../types'
import { money, num, pct } from '../lib/format'

interface Point {
  domain: string
  name: string
  value: number
  isSeed: boolean
}

function DimRow({
  label,
  points,
  low,
  high,
  rank,
  of,
  valueLabel,
  invert = false,
  log = false,
  hovered,
  onHover,
}: {
  label: string
  points: Point[]
  low: string
  high: string
  rank: number | null
  of: number
  valueLabel: string
  invert?: boolean
  log?: boolean
  hovered: string | null
  onHover: (domain: string | null) => void
}) {
  // Funding/headcount are heavily right-skewed → log axis; growth/maturity linear.
  const tx = (v: number) => (log ? Math.log10(Math.max(v, 1)) : v)
  const vals = points.map((p) => tx(p.value))
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  const pos = (v: number) => {
    const t = max === min ? 0.5 : (tx(v) - min) / (max - min)
    return (invert ? 1 - t : t) * 100
  }

  return (
    <div className="flex items-center gap-3">
      <div className="w-24 shrink-0 text-right text-sm text-muted">{label}</div>
      <div className="relative h-9 flex-1 rounded-lg bg-canvas">
        <span className="pointer-events-none absolute left-2 top-1/2 -translate-y-1/2 text-[10px] uppercase tracking-wide text-gray-400">{low}</span>
        <span className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-[10px] uppercase tracking-wide text-gray-400">{high}</span>
        {points.map((p) => {
          const active = p.domain === hovered
          const dot = p.isSeed
            ? 'h-3.5 w-3.5 border-2 border-accent bg-white'
            : active
              ? 'h-3 w-3 bg-accent'
              : 'h-1.5 w-1.5 bg-gray-300'
          return (
            <span
              key={p.domain}
              onMouseEnter={() => onHover(p.domain)}
              onMouseLeave={() => onHover(null)}
              className="absolute top-1/2 flex h-5 w-5 -translate-x-1/2 -translate-y-1/2 cursor-pointer items-center justify-center"
              style={{ left: `${pos(p.value)}%`, zIndex: active || p.isSeed ? 20 : 1 }}
            >
              <span className={`rounded-full transition-all ${dot}`} />
              {active && !p.isSeed && (
                <span className="pointer-events-none absolute -top-5 z-30 whitespace-nowrap rounded bg-ink px-1.5 py-0.5 text-[10px] font-medium text-white">
                  {p.name}
                </span>
              )}
            </span>
          )
        })}
      </div>
      <div className="w-24 shrink-0 text-right">
        <div className="text-sm font-bold">{valueLabel}</div>
        <div className="text-xs text-muted">{rank ? `#${rank} of ${of}` : '—'}</div>
      </div>
    </div>
  )
}

export function PositionVsField({ space }: { space: Space }) {
  const [hovered, setHovered] = useState<string | null>(null)
  const field = [space.seed, ...space.companies]

  const pts = (get: (c: Company) => number | null): Point[] =>
    field
      .filter((c) => c.domain && get(c) !== null)
      .map((c) => ({ domain: c.domain!, name: c.display_name, value: get(c) as number, isSeed: c.is_seed }))

  const dims = [
    { label: 'Funding', points: pts((c) => c.total_funding_m), low: 'Lower', high: 'Higher', rank: space.funding_rank, of: space.funding_of, valueLabel: money(space.seed.total_funding_m), log: true },
    { label: 'Headcount', points: pts((c) => c.employees), low: 'Smaller', high: 'Larger', rank: space.headcount_rank, of: space.headcount_of, valueLabel: num(space.seed.employees), log: true },
    { label: 'Growth 12m', points: pts((c) => c.growth_12m), low: 'Slower', high: 'Faster', rank: space.growth_rank, of: space.growth_of, valueLabel: pct(space.seed.growth_12m) },
    { label: 'Maturity', points: pts((c) => c.founded_year), low: 'Newer', high: 'Established', rank: space.maturity_rank, of: space.maturity_of, valueLabel: String(space.seed.founded_year ?? '—'), invert: true },
  ]

  const hoveredCompany = hovered ? field.find((c) => c.domain === hovered) : null

  return (
    <div className="card p-6" onMouseLeave={() => setHovered(null)}>
      <h3 className="font-bold">Position vs the field</h3>
      <p className="text-sm text-muted">Where {space.seed.display_name} ranks against credible peers — hover any dot to track a competitor across all four.</p>

      <div className="mt-4 flex items-center gap-3">
        <span className="inline-flex items-center gap-1 rounded-full bg-accent-soft px-3 py-1 text-sm font-semibold text-accent">
          ◆ {space.archetype}
        </span>
        {hoveredCompany && !hoveredCompany.is_seed && (
          <span className="truncate text-xs text-muted">
            <span className="font-semibold text-ink">{hoveredCompany.display_name}</span> ·{' '}
            {money(hoveredCompany.total_funding_m)} · {num(hoveredCompany.employees)} emp ·{' '}
            {pct(hoveredCompany.growth_12m)} · founded {hoveredCompany.founded_year ?? '—'}
          </span>
        )}
      </div>

      <div className="mt-5 space-y-3">
        {dims.map((d) => (
          <DimRow key={d.label} {...d} points={d.points.length ? d.points : []} hovered={hovered} onHover={setHovered} />
        ))}
      </div>

      <div className="mt-4 flex items-center gap-4 text-xs text-muted">
        <span className="inline-flex items-center gap-1"><span className="h-3 w-3 rounded-full border-2 border-accent bg-white" /> {space.seed.display_name}</span>
        <span className="inline-flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-gray-300" /> peer · hover to reveal</span>
      </div>
    </div>
  )
}
