export function SectionHeading({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string
  title: string
  subtitle?: string
}) {
  return (
    <div className="border-t border-line pt-8">
      <div className="eyebrow">{eyebrow}</div>
      <h2 className="mt-2 text-3xl font-bold tracking-tight">{title}</h2>
      {subtitle && <p className="mt-1 max-w-3xl text-muted">{subtitle}</p>}
    </div>
  )
}
