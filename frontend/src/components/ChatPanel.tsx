import { useEffect, useRef, useState } from 'react'
import { streamChat, type ChatMessage } from '../api'
import type { Space } from '../types'

export function ChatPanel({ space, open, onClose }: { space: Space; open: boolean; onClose: () => void }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  const seed = space.seed.display_name
  const suggestions = [
    'How crowded is this market?',
    `What's ${seed}'s moat?`,
    'Which competitor is growing fastest, and why?',
  ]

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  async function send(text: string) {
    const q = text.trim()
    if (!q || busy) return
    const history: ChatMessage[] = [...messages, { role: 'user', content: q }]
    setMessages([...history, { role: 'assistant', content: '' }])
    setInput('')
    setBusy(true)
    const append = (delta: string) =>
      setMessages((m) => {
        const copy = [...m]
        copy[copy.length - 1] = { role: 'assistant', content: copy[copy.length - 1].content + delta }
        return copy
      })
    try {
      await streamChat(space, history, append)
    } catch (e) {
      append(`\n\n⚠ ${e instanceof Error ? e.message : 'Chat failed.'}`)
    } finally {
      setBusy(false)
    }
  }

  if (!open) return null
  return (
    <div className="fixed inset-y-0 right-0 z-40 flex w-full max-w-md flex-col border-l border-line bg-white shadow-2xl">
      <div className="flex items-center justify-between border-b border-line px-4 py-3">
        <div>
          <div className="text-sm font-bold">✦ PULSE Research Agent</div>
          <div className="text-xs text-muted">Grounded in this landscape · can search the web</div>
        </div>
        <button onClick={onClose} className="rounded-full px-2 py-1 text-muted hover:bg-canvas">✕</button>
      </div>

      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="space-y-3">
            <p className="text-sm text-gray-600">
              Hi — I'm the PULSE research agent. I can dig deeper into {seed}'s landscape: ask me about
              competitors, funding, positioning, or anything I can find on the web.
            </p>
            <div className="flex flex-col gap-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-xl border border-line px-3 py-2 text-left text-sm transition hover:border-accent hover:text-accent"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-right' : ''}>
            <div
              className={`inline-block max-w-[85%] whitespace-pre-wrap rounded-2xl px-3 py-2 text-sm ${
                m.role === 'user' ? 'bg-accent text-white' : 'bg-canvas text-ink'
              }`}
            >
              {m.content || (busy ? '…' : '')}
            </div>
          </div>
        ))}
      </div>

      <div className="border-t border-line p-3">
        <div className="flex items-center gap-2 rounded-xl border border-line px-3 focus-within:border-accent">
          <input
            className="w-full bg-transparent py-2.5 text-sm outline-none"
            placeholder={`Ask about ${seed}…`}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send(input)}
            disabled={busy}
          />
          <button
            onClick={() => send(input)}
            disabled={busy || !input.trim()}
            className="text-sm font-semibold text-accent disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
