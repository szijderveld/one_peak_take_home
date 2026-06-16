import { useState } from 'react'
import { fetchLandscape } from './api'
import type { Company, Space } from './types'
import { Header } from './components/Header'
import { SearchBar } from './components/SearchBar'
import { CompanySection } from './components/CompanySection'
import { SpaceSection } from './components/SpaceSection'
import { MarketPositionSection } from './components/MarketPositionSection'
import { CompanyModal } from './components/CompanyModal'
import { ChatPanel } from './components/ChatPanel'

function Loading() {
  return (
    <div className="card mt-6 p-8 text-center text-muted">
      <div className="mx-auto mb-3 h-6 w-6 animate-spin rounded-full border-2 border-line border-t-accent" />
      Fetching competitors, cleaning the data, and running the analysis…
    </div>
  )
}

export default function App() {
  const [domain, setDomain] = useState('pandadoc.com')
  const [space, setSpace] = useState<Space | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<Company | null>(null)
  const [chatOpen, setChatOpen] = useState(false)

  async function analyse(d: string) {
    const target = d.trim()
    if (!target || loading) return
    setLoading(true)
    setError(null)
    try {
      setSpace(await fetchLandscape(target))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.')
      setSpace(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 pb-24">
      <Header />
      <SearchBar value={domain} onChange={setDomain} onAnalyse={analyse} loading={loading} />

      {error && (
        <div className="card mt-6 border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
      )}
      {loading && <Loading />}

      {space && !loading && (
        <div className="mt-8 space-y-10">
          <CompanySection space={space} />
          <SpaceSection space={space} onOpen={setSelected} />
          <MarketPositionSection space={space} onOpen={setSelected} />
          <footer className="border-t border-line pt-6 text-center text-xs text-gray-400">
            PULSE Competitive Landscape · prototype for the One Peak Product Data Engineer task.
          </footer>
        </div>
      )}

      <CompanyModal company={selected} onClose={() => setSelected(null)} />

      {space && !chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className="fixed bottom-6 right-6 z-30 rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white shadow-lg transition hover:brightness-125"
        >
          ✦ Ask the research agent
        </button>
      )}
      {space && <ChatPanel space={space} open={chatOpen} onClose={() => setChatOpen(false)} />}
    </div>
  )
}
