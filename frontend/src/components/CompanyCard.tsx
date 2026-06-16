import type { Company } from '../types'
import { location, money, num, pct } from '../lib/format'
import { AISummary } from './AISummary'
import { Stat, StatGrid } from './StatGrid'
import { TalentFootprint } from './TalentFootprint'

function Avatar({ name }: { name: string }) {
  return (
    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-accent-soft text-lg font-bold text-accent">
      {name.charAt(0).toUpperCase()}
    </div>
  )
}

function Actions() {
  // Visual only — wired to nothing by design.
  return (
    <div className="flex shrink-0 gap-2">
      <button className="inline-flex items-center gap-1.5 rounded-lg border border-line px-3 py-1.5 text-sm font-medium transition hover:border-accent hover:text-accent">
        ✉ Share via email
      </button>
      <button className="rounded-lg bg-accent px-3 py-1.5 text-sm font-semibold text-white transition hover:brightness-110">
        Reach out
      </button>
    </div>
  )
}

/** The full company profile — used in the Company section and the modal. */
export function CompanyCard({
  company,
  showFootprint = true,
  showAISummary = true,
}: {
  company: Company
  showFootprint?: boolean
  showAISummary?: boolean
}) {
  const c = company
  const tags = [c.domain, c.funding_stage, location(c)].filter(Boolean) as string[]
  const lastRoundLabel = c.last_round_date ? `Last round · ${c.last_round_date.slice(0, 7)}` : 'Last round'

  return (
    <div className="card p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-4">
          <Avatar name={c.display_name} />
          <div>
            <h3 className="text-2xl font-bold tracking-tight">{c.display_name}</h3>
            <div className="mt-2 flex flex-wrap gap-2">
              {tags.map((t) => (
                <span key={t} className="pill">{t}</span>
              ))}
            </div>
          </div>
        </div>
        <Actions />
      </div>

      {showAISummary && c.ai_summary ? (
        <div className="mt-4">
          <AISummary text={c.ai_summary} />
        </div>
      ) : c.ai_blurb || c.description ? (
        <p className="mt-4 text-sm leading-relaxed text-gray-600">{c.ai_blurb || c.description}</p>
      ) : null}

      <div className="mt-5">
        <StatGrid cols={3}>
          <Stat value={money(c.total_funding_m)} label="Total funding" />
          <Stat value={money(c.last_round_m)} label={lastRoundLabel} />
          <Stat value={num(c.employees)} label="Employees" sub={c.employees && !c.employees_reliable ? 'estimate — down-weighted' : undefined} />
          <Stat value={pct(c.growth_12m)} label="Growth 12m" />
          <Stat value={c.founded_year ?? '—'} label="Founded" />
          <Stat value={c.funding_stage ?? '—'} label="Stage" />
        </StatGrid>
      </div>

      {c.industries.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {c.industries.slice(0, 6).map((t) => (
            <span key={t} className="pill">{t}</span>
          ))}
        </div>
      )}

      {showFootprint && <TalentFootprint company={c} />}
    </div>
  )
}
