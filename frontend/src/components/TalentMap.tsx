import { useMemo } from 'react'
import { geoNaturalEarth1, geoPath } from 'd3-geo'
import { feature } from 'topojson-client'
import worldData from 'world-atlas/countries-110m.json'
import type { GeoShare } from '../types'

// d3-geo / topojson typings vs the raw atlas object aren't worth fighting here.
/* eslint-disable @typescript-eslint/no-explicit-any */
const world = worldData as unknown as any
const land = feature(world, world.objects.countries) as any

// Our cleaned country names → the names used in world-atlas (lowercased).
const ALIASES: Record<string, string> = {
  'united states': 'united states of america',
  'czech republic': 'czechia',
  'south korea': 'south korea',
  'bosnia and herzegovina': 'bosnia and herz.',
  'dominican republic': 'dominican rep.',
}

const WIDTH = 640
const HEIGHT = 280

export function TalentMap({ geography }: { geography: GeoShare[] }) {
  const shares = useMemo(() => {
    const m = new Map<string, number>()
    for (const g of geography) {
      if (g.country.toLowerCase() === 'other') continue
      const key = ALIASES[g.country.toLowerCase()] ?? g.country.toLowerCase()
      m.set(key, g.percent)
    }
    return m
  }, [geography])

  const path = useMemo(() => geoPath(geoNaturalEarth1().fitSize([WIDTH, HEIGHT], land)), [])

  return (
    <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full" role="img" aria-label="Talent footprint map">
      {land.features.map((f: any, i: number) => {
        const name = String(f.properties?.name ?? '').toLowerCase()
        const share = shares.get(name)
        const fill = share
          ? `color-mix(in srgb, var(--color-accent) ${Math.round(25 + share * 75)}%, white)`
          : '#e7e9ee'
        return <path key={i} d={path(f) ?? ''} fill={fill} stroke="#fff" strokeWidth={0.4} />
      })}
    </svg>
  )
}
