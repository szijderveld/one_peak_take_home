// Mirrors the backend domain model (app/models/domain.py).

export interface GeoShare {
  country: string
  percent: number // 0..1
  confidence: string | null
}

export interface Company {
  domain: string | null
  display_name: string
  is_seed: boolean
  identity_ok: boolean
  similarity: number
  description: string | null
  ai_blurb: string | null
  ai_summary: string | null
  employees: number | null
  employees_reliable: boolean
  growth_12m: number | null
  founded_year: number | null
  founded_precision: string
  hq_city: string | null
  hq_country: string | null
  industries: string[]
  business_models: string[]
  funding_stage: string | null
  total_funding_m: number | null
  last_round_m: number | null
  last_round_date: string | null
  market_tier: 'incumbent' | 'established'
  geography: GeoShare[]
}

export interface Space {
  seed: Company
  companies: Company[]
  name: string
  num_credible_peers: number
  median_founded_year: number | null
  maturity_label: string
  total_capital_m: number
  total_headcount: number
  intensity_label: string
  relevance_direct: number
  relevance_adjacent: number
  relevance_peripheral: number
  themes: string[]
  capital_ranking: string[]
  archetype: string
  funding_rank: number | null
  funding_of: number
  headcount_rank: number | null
  headcount_of: number
  growth_rank: number | null
  growth_of: number
  maturity_rank: number | null
  maturity_of: number
  closest_comparators: string[]
  unreliable_headcount_count: number
  quarantined_count: number
  notes: string[]
  summary: string | null
  position_summary: string | null
  incumbents_summary: string | null
  established_summary: string | null
  cache_hit: boolean
  count: number
  mode: string
}

export type Mode = 'live' | 'demo'
