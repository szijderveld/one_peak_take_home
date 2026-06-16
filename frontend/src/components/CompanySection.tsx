import type { Space } from '../types'
import { AISummary } from './AISummary'
import { CompanyCard } from './CompanyCard'
import { SectionHeading } from './Section'

export function CompanySection({ space }: { space: Space }) {
  return (
    <section className="space-y-4">
      <SectionHeading
        eyebrow="Company"
        title={space.seed.display_name}
        subtitle="At-a-glance profile of the company you searched. Any company mentioned elsewhere is clickable for its own card."
      />
      <AISummary text={space.seed.ai_summary} />
      <CompanyCard company={space.seed} showAISummary={false} />
    </section>
  )
}
