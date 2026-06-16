import type { Company } from '../types'
import { TalentMap } from './TalentMap'

/** Where a company's staff sit, derived from the structured locations array:
 * a geographic map plus labelled %-bars. */
export function TalentFootprint({ company }: { company: Company }) {
  const geo = company.geography
  if (!geo.length) return null
  return (
    <div className="mt-5 rounded-xl border border-line bg-canvas/50 p-4">
      <div className="eyebrow text-gray-400">Talent footprint</div>
      <div className="mt-3 overflow-hidden rounded-lg">
        <TalentMap geography={geo} />
      </div>
      <div className="mt-3 space-y-2">
        {geo.map((g) => {
          const p = Math.round(g.percent * 100)
          return (
            <div key={g.country} className="flex items-center gap-3">
              <div className="w-32 shrink-0 truncate text-xs text-gray-600">{g.country}</div>
              <div className="h-2 flex-1 rounded-full bg-line">
                <div className="h-2 rounded-full bg-accent" style={{ width: `${p}%` }} />
              </div>
              <div className="w-9 text-right text-xs font-semibold">{p}%</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
