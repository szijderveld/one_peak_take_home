function Logo() {
  return (
    <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden>
      <path d="M13 3 L23 21 L3 21 Z" fill="var(--color-accent)" />
    </svg>
  )
}

export function Header() {
  return (
    <header className="flex items-center py-4">
      <div className="flex items-center gap-3">
        <Logo />
        <div className="leading-tight">
          <div className="text-sm font-extrabold tracking-tight">PULSE</div>
          <div className="text-xs text-muted">Competitive Landscape</div>
        </div>
      </div>
    </header>
  )
}
