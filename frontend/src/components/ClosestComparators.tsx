import type { Company, Space } from '../types'
import { money, num, pct, resolve } from '../lib/format'

export function ClosestComparators({ space, onOpen }: { space: Space; onOpen: (c: Company) => void }) {
  const comparators = resolve(space, space.closest_comparators).slice(0, 4)

  return (
    <div className="card p-5">
      <h3 className="font-bold">Closest comparators</h3>
      <p className="text-sm text-muted">Most similar companies — click to open the card.</p>
      <div className="mt-4 space-y-3">
        {comparators.map((c) => (
          <button
            key={c.domain}
            onClick={() => onOpen(c)}
            className="block w-full rounded-xl border border-line p-3 text-left transition hover:border-accent hover:shadow-sm"
          >
            <div className="flex items-baseline justify-between gap-2">
              <span className="font-semibold">{c.display_name}</span>
              <span className="text-xs font-semibold text-accent">{Math.round(c.similarity * 100)}% match</span>
            </div>
            <p className="mt-1 line-clamp-2 text-xs text-muted">{c.ai_blurb || c.description}</p>
            <div className="mt-2 text-xs text-gray-500">
              <span className="font-semibold text-ink">{money(c.total_funding_m)}</span> raised ·{' '}
              <span className="font-semibold text-ink">{num(c.employees)}</span> emp ·{' '}
              <span className="font-semibold text-ink">{pct(c.growth_12m)}</span> 12m
              {c.funding_stage ? ` · ${c.funding_stage}` : ''}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
