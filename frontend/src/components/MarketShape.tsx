import type { Space } from '../types'
import { money, num } from '../lib/format'
import { RelevanceBar } from './RelevanceBar'
import { Stat, StatGrid } from './StatGrid'

export function MarketShape({ space }: { space: Space }) {
  return (
    <div className="card p-5">
      <h3 className="font-bold">Market shape</h3>
      <p className="text-sm text-muted">Size, maturity and density of the space.</p>

      <div className="mt-4">
        <StatGrid cols={4}>
          <Stat value={space.num_credible_peers} label="Companies" sub={space.intensity_label} />
          <Stat value={space.median_founded_year ?? '—'} label="Median founded" sub={space.maturity_label} />
          <Stat value={money(space.total_capital_m)} label="Capital in space" />
          <Stat value={num(space.total_headcount)} label="Total headcount" />
        </StatGrid>
      </div>

      <div className="mt-4">
        <RelevanceBar space={space} />
      </div>

      {space.themes.length > 0 && (
        <div className="mt-4">
          <div className="text-xs font-semibold text-gray-500">What defines this space</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {space.themes.map((t) => (
              <span key={t} className="pill">{t}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
