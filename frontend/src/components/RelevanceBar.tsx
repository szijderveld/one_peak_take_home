import type { Space } from '../types'

/** How many of ALL returned competitors are Direct / Adjacent / Peripheral by
 * similarity — a stacked bar that reads "how crowded is this space, really". */
export function RelevanceBar({ space }: { space: Space }) {
  const segments = [
    { label: 'Direct', hint: '≥0.70', n: space.relevance_direct, bg: 'var(--color-accent)', fg: '#fff' },
    { label: 'Adjacent', hint: '0.61–0.69', n: space.relevance_adjacent, bg: '#7da2f0', fg: '#fff' },
    { label: 'Peripheral', hint: '≤0.60', n: space.relevance_peripheral, bg: '#d7e1f9', fg: '#1f2937' },
  ]
  const total = segments.reduce((s, x) => s + x.n, 0) || 1

  return (
    <div>
      <div className="text-xs font-semibold text-gray-500">
        How crowded, by relevance to {space.seed.display_name}
      </div>
      <div className="mt-2 flex h-7 w-full overflow-hidden rounded-lg bg-canvas">
        {segments.map((s) =>
          s.n > 0 ? (
            <div
              key={s.label}
              className="flex items-center justify-center text-xs font-semibold"
              style={{ width: `${(s.n / total) * 100}%`, minWidth: '2rem', background: s.bg, color: s.fg }}
              title={`${s.label} (${s.hint}): ${s.n}`}
            >
              {s.n}
            </div>
          ) : null,
        )}
      </div>
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted">
        {segments.map((s) => (
          <span key={s.label} className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ background: s.bg }} />
            {s.label} <span className="text-gray-400">{s.hint}</span>
          </span>
        ))}
      </div>
    </div>
  )
}
