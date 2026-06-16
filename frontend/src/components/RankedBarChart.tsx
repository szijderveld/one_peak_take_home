import type { Company } from '../types'

/** A horizontal ranked-bar chart over the field, with the seed starred and
 * highlighted. Used for both "capital raised" and "number of employees". */
export function RankedBarChart({
  title,
  subtitle,
  field,
  get,
  format,
  onOpen,
  top = 8,
}: {
  title: string
  subtitle: string
  field: Company[]
  get: (c: Company) => number | null
  format: (n: number) => string
  onOpen: (c: Company) => void
  top?: number
}) {
  const withValue = field.filter((c) => c.domain && get(c) !== null)
  const sorted = [...withValue].sort((a, b) => (get(b) as number) - (get(a) as number))
  let items = sorted.slice(0, top)
  const seed = sorted.find((c) => c.is_seed)
  if (seed && !items.includes(seed)) items = [...items, seed] // always show where the seed sits
  const max = sorted.length ? (get(sorted[0]) as number) : 1

  return (
    <div className="card p-6">
      <h3 className="font-bold">{title}</h3>
      <p className="text-sm text-muted">{subtitle}</p>
      <div className="mt-5 space-y-2.5">
        {items.map((c) => (
          <div key={c.domain} className="flex items-center gap-3">
            <button
              onClick={() => onOpen(c)}
              className={`w-28 shrink-0 truncate text-left text-sm transition hover:text-accent ${c.is_seed ? 'font-bold' : ''}`}
            >
              {c.is_seed ? '★ ' : ''}
              {c.display_name}
            </button>
            <div className="h-3 flex-1 rounded-full bg-line">
              <div
                className={`h-3 rounded-full ${c.is_seed ? 'bg-accent' : 'bg-blue-300'}`}
                style={{ width: `${Math.max(2, ((get(c) as number) / max) * 100)}%` }}
              />
            </div>
            <div className="w-16 text-right text-sm font-medium">{format(get(c) as number)}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
