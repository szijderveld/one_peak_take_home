import type { Company, Space } from '../types'
import { money, num } from '../lib/format'
import { AISummary } from './AISummary'
import { KeyPlayers } from './KeyPlayers'
import { MarketShape } from './MarketShape'
import { RankedBarChart } from './RankedBarChart'
import { SectionHeading } from './Section'

export function SpaceSection({ space, onOpen }: { space: Space; onOpen: (c: Company) => void }) {
  const field = [space.seed, ...space.companies]
  return (
    <section className="space-y-4">
      <SectionHeading
        eyebrow="The space"
        title={space.name}
        subtitle={`The market ${space.seed.display_name} operates in — who the key players are, and how large, mature and crowded it is.`}
      />
      <AISummary text={space.summary} />
      <MarketShape space={space} />
      <KeyPlayers space={space} onOpen={onOpen} />
      <div className="grid gap-4 lg:grid-cols-2">
        <RankedBarChart
          title="Capital raised across the field"
          subtitle="Who holds the war chest — click any name to open its card."
          field={field}
          get={(c) => c.total_funding_m}
          format={money}
          onOpen={onOpen}
        />
        <RankedBarChart
          title="Number of employees"
          subtitle="Headcount across the field — click any name to open its card."
          field={field}
          get={(c) => (c.employees_reliable ? c.employees : null)}
          format={num}
          onOpen={onOpen}
        />
      </div>
    </section>
  )
}
