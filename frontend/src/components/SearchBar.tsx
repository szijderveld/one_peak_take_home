import type { Mode } from '../types'

const EXAMPLES = ['pandadoc.com', 'gocardless.com', 'groundcover.com']

export function SearchBar({
  value,
  onChange,
  onAnalyse,
  loading,
  mode,
}: {
  value: string
  onChange: (v: string) => void
  onAnalyse: (domain: string) => void
  loading: boolean
  mode: Mode
}) {
  return (
    <div className="card p-5">
      <div className="flex gap-3">
        <div className="flex flex-1 items-center rounded-xl border border-line px-4 focus-within:border-accent">
          <span className="select-none text-muted">https://</span>
          <input
            className="w-full bg-transparent px-1 py-3 outline-none"
            placeholder="company.com"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onAnalyse(value)}
          />
        </div>
        <button
          onClick={() => onAnalyse(value)}
          disabled={loading || !value.trim()}
          className="rounded-xl bg-accent px-6 font-semibold text-white transition hover:brightness-110 disabled:opacity-50"
        >
          {loading ? 'Analysing…' : 'Analyse'}
        </button>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2 text-sm text-muted">
        <span>Try:</span>
        {EXAMPLES.map((d) => (
          <button key={d} className="pill transition hover:border-accent hover:text-accent" onClick={() => { onChange(d); onAnalyse(d) }}>
            {d}
          </button>
        ))}
      </div>
      {mode === 'demo' && (
        <p className="mt-3 text-xs text-gray-400">
          Demo mode replays bundled real responses (pandadoc.com, gocardless.com, groundcover.com) through the full
          pipeline — no key or network needed.
        </p>
      )}
    </div>
  )
}
