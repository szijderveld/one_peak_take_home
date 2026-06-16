import type { Space } from '../types'

export function DataConfidence({ space }: { space: Space }) {
  return (
    <div className="card bg-canvas/40 p-5">
      <h3 className="font-bold">Data confidence</h3>
      <ul className="mt-3 space-y-1.5 text-sm text-muted">
        {space.notes.map((note, i) => (
          <li key={i} className="flex gap-2">
            <span className="text-amber-500">⚠</span>
            <span>{note}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
