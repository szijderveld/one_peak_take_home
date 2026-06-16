import type { Mode } from '../types'

function Logo() {
  return (
    <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden>
      <path d="M13 3 L23 21 L3 21 Z" fill="var(--color-accent)" />
    </svg>
  )
}

function ModeToggle({ mode, onMode }: { mode: Mode; onMode: (m: Mode) => void }) {
  return (
    <div className="flex rounded-full border border-line bg-white p-0.5 text-sm">
      {(['demo', 'live'] as Mode[]).map((m) => (
        <button
          key={m}
          onClick={() => onMode(m)}
          className={`rounded-full px-3 py-1 capitalize transition ${
            mode === m ? 'bg-ink text-white' : 'text-muted hover:text-ink'
          }`}
        >
          {m === 'live' ? 'Live API' : 'Demo'}
        </button>
      ))}
    </div>
  )
}

export function Header({ mode, onMode }: { mode: Mode; onMode: (m: Mode) => void }) {
  return (
    <header className="flex items-center justify-between py-4">
      <div className="flex items-center gap-3">
        <Logo />
        <div className="leading-tight">
          <div className="text-sm font-extrabold tracking-tight">PULSE</div>
          <div className="text-xs text-muted">Competitive Landscape</div>
        </div>
      </div>
      <ModeToggle mode={mode} onMode={onMode} />
    </header>
  )
}
