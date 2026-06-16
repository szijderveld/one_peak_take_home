import type { Company, Space } from '../types'
import { AISummary } from './AISummary'
import { ClosestComparators } from './ClosestComparators'
import { DataConfidence } from './DataConfidence'
import { PositionVsField } from './PositionVsField'
import { SectionHeading } from './Section'

export function MarketPositionSection({ space, onOpen }: { space: Space; onOpen: (c: Company) => void }) {
  return (
    <section className="space-y-4">
      <SectionHeading
        eyebrow="Market position"
        title={`Where ${space.seed.display_name} sits`}
        subtitle={`${space.seed.display_name}'s position relative to the space, and its closest comparators.`}
      />
      <AISummary text={space.position_summary} />
      <div className="grid gap-4 lg:grid-cols-2">
        <PositionVsField space={space} />
        <ClosestComparators space={space} onOpen={onOpen} />
      </div>
      <DataConfidence space={space} />
    </section>
  )
}
