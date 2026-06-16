import type { Space } from './types'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export async function fetchLandscape(domain: string): Promise<Space> {
  const res = await fetch('/api/landscape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ domain }),
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => null)
    throw new Error(detail?.detail ?? `Request failed (${res.status})`)
  }
  return res.json()
}

/** POST the landscape + history to /api/chat and stream assistant text deltas. */
export async function streamChat(
  space: Space,
  messages: ChatMessage[],
  onDelta: (text: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ space, messages }),
    signal,
  })
  if (!res.ok || !res.body) {
    const detail = await res.json().catch(() => null)
    throw new Error(detail?.detail ?? `Chat failed (${res.status})`)
  }
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''
    for (const part of parts) {
      const line = part.trim()
      if (!line.startsWith('data:')) continue
      const payload = JSON.parse(line.slice(5).trim())
      if (payload.delta) onDelta(payload.delta)
      else if (payload.error) throw new Error(payload.error)
    }
  }
}
