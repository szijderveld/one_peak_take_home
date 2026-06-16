import type { Company, Space } from '../types'

/** USD millions → "$67M" / "$1.3B". */
export function money(m: number | null | undefined): string {
  if (m === null || m === undefined) return '—'
  if (m >= 1000) return `$${(m / 1000).toFixed(1)}B`
  if (m >= 10) return `$${Math.round(m)}M`
  return `$${m.toFixed(1)}M`
}

export function pct(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined) return '—'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(digits)}%`
}

export function num(n: number | null | undefined): string {
  return n === null || n === undefined ? '—' : n.toLocaleString('en-US')
}

export function location(c: Company): string | null {
  return [c.hq_city, c.hq_country].filter(Boolean).join(', ') || null
}

/** Lookup of every company in the space (seed + peers) by domain. */
export function companyIndex(space: Space): Map<string, Company> {
  const idx = new Map<string, Company>()
  for (const c of [space.seed, ...space.companies]) {
    if (c.domain) idx.set(c.domain, c)
  }
  return idx
}

export function resolve(space: Space, domains: string[]): Company[] {
  const idx = companyIndex(space)
  return domains.map((d) => idx.get(d)).filter((c): c is Company => Boolean(c))
}
