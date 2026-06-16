/** The tinted "✦ AI summary" box. Renders nothing until enrichment fills it. */
export function AISummary({ text }: { text?: string | null }) {
  if (!text) return null
  return (
    <div className="rounded-xl border border-indigo-100 bg-accent-soft/70 p-4">
      <div className="eyebrow flex items-center gap-1">✦ AI summary</div>
      <p className="mt-2 text-sm leading-relaxed text-gray-700">{text}</p>
    </div>
  )
}
