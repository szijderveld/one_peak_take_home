import { useState } from 'react'
import type { Company, Space } from '../types'
import { money, num, pct } from '../lib/format'
import { AISummary } from './AISummary'

type Tier = 'established' | 'incumbent'
const CAP = 12

function PlayerTable({ rows, onOpen }: { rows: Company[]; onOpen: (c: Company) => void }) {
  if (!rows.length) {
    return <p className="mt-4 text-sm text-muted">No companies fall in this tier for this space.</p>
  }
  const shown = rows.slice(0, CAP)
  return (
    <div className="mt-4 overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-[11px] uppercase tracking-wide text-gray-400">
            <th className="pb-2 font-semibold">Company</th>
            <th className="pb-2 pl-3 text-right font-semibold">Funding</th>
            <th className="pb-2 pl-3 text-right font-semibold">Employees</th>
            <th className="pb-2 pl-3 text-right font-semibold">Growth 12m</th>
            <th className="pb-2 pl-3 text-right font-semibold">Stage</th>
          </tr>
        </thead>
        <tbody>
          {shown.map((c) => (
            <tr
              key={c.domain}
              onClick={() => onOpen(c)}
              className="cursor-pointer border-t border-line align-top transition hover:bg-canvas"
            >
              <td className="py-2.5 pr-3">
                <div className="font-semibold">{c.display_name}</div>
                <div className="line-clamp-1 text-xs text-muted">{c.ai_blurb || c.description}</div>
              </td>
              <td className="whitespace-nowrap pl-3 text-right font-medium">{money(c.total_funding_m)}</td>
              <td className="whitespace-nowrap pl-3 text-right">{num(c.employees)}</td>
              <td className="whitespace-nowrap pl-3 text-right">{pct(c.growth_12m)}</td>
              <td className="whitespace-nowrap pl-3 text-right text-muted">{c.funding_stage ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > CAP && (
        <p className="mt-3 text-xs text-gray-400">+{rows.length - CAP} more in this tier</p>
      )}
    </div>
  )
}

export function KeyPlayers({ space, onOpen }: { space: Space; onOpen: (c: Company) => void }) {
  const [tab, setTab] = useState<Tier>('established')

  const byTier = (t: Tier) =>
    space.companies
      .filter((c) => c.market_tier === t)
      .sort((a, b) => (b.total_funding_m ?? 0) - (a.total_funding_m ?? 0))

  const established = byTier('established')
  const incumbents = byTier('incumbent')
  const rows = tab === 'established' ? established : incumbents
  const summary = tab === 'established' ? space.established_summary : space.incumbents_summary

  const tabs: { id: Tier; label: string; count: number }[] = [
    { id: 'established', label: 'Established players', count: established.length },
    { id: 'incumbent', label: 'Incumbents', count: incumbents.length },
  ]

  return (
    <div className="card p-6">
      <h3 className="font-bold">Key players</h3>
      <p className="text-sm text-muted">The field split into incumbents and established players — click any row to open its card.</p>

      <div className="mt-4 inline-flex rounded-lg bg-canvas p-1 text-sm">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`rounded-md px-3 py-1.5 transition ${
              tab === t.id ? 'bg-white font-semibold shadow-sm' : 'text-muted hover:text-ink'
            }`}
          >
            {t.label} <span className="text-gray-400">({t.count})</span>
          </button>
        ))}
      </div>

      <div className="mt-4">
        <AISummary text={summary} />
      </div>
      <PlayerTable rows={rows} onOpen={onOpen} />
    </div>
  )
}
