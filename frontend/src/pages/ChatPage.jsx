import { useState, useRef, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import ReactMarkdown from 'react-markdown'
import api from '../api'

export default function ChatPage({ user }) {
  const [sessions, setSessions] = useState([])
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef(null)
  const username = user?.username

  useEffect(() => {
    if (username) loadSessions()
  }, [username])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function loadSessions() {
    try {
      const res = await api.get(`/users/${username}/sessions`)
      setSessions(res.data.data || [])
    } catch (_) {}
  }

  async function loadSessionMessages(sessionId) {
    setActiveSessionId(sessionId)
    try {
      const res = await api.get(`/users/${username}/sessions/${sessionId}/messages`)
      const data = res.data.data
      const msgs = (data.messages || []).map(m => ({ role: m.role, content: m.content, intent: m.intent }))
      setMessages(msgs)
    } catch (_) {}
  }

  async function sendMessage() {
    if (!input.trim() || streaming) return
    const text = input.trim()
    setInput('')

    const userMsg = { role: 'user', content: text }
    const aiMsg = { role: 'assistant', content: '' }
    setMessages(prev => [...prev, userMsg, aiMsg])
    setStreaming(true)

    // Build history (exclude the last 2 just added)
    const history = messages.map(m => ({ role: m.role, content: m.content }))

    try {
      const body = {
        username,
        message: text,
        session_id: activeSessionId,
        history,
        user_profile: JSON.parse(localStorage.getItem('fitmind_profile') || 'null'),
      }

      const response = await fetch('/api/chat/session/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let newSessionId = activeSessionId

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          if (raw === '[DONE]') continue
          try {
            const json = JSON.parse(raw)
            if (json.chunk) {
              setMessages(prev => {
                const updated = [...prev]
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  content: updated[updated.length - 1].content + json.chunk,
                }
                return updated
              })
            }
            if (json.session_id) {
              newSessionId = json.session_id
              setActiveSessionId(json.session_id)
            }
          } catch (_) {}
        }
      }
      await loadSessions()
    } catch (err) {
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { ...updated[updated.length - 1], content: 'Terjadi error saat menghubungi AI.' }
        return updated
      })
    } finally {
      setStreaming(false)
    }
  }

  function newChat() {
    setActiveSessionId(null)
    setMessages([])
  }

  async function deleteSession(sessionId, e) {
    e.stopPropagation()
    try {
      await api.delete(`/users/${username}/sessions/${sessionId}`)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      if (activeSessionId === sessionId) newChat()
    } catch (_) {}
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar username={user?.username} />

      {/* Sessions sidebar */}
      <aside className="chat-sessions-sidebar">
        <div style={{ paddingLeft: 2, marginBottom: 16 }}>
          <div style={{ fontSize: 12, color: '#525252', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 10 }}>
            Riwayat Chat
          </div>
          <button className="btn-primary" style={{ width: '100%', padding: '8px 12px' }} onClick={newChat}>
            Chat Baru
          </button>
        </div>
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 4 }}>
          {sessions.map(s => (
            <div key={s.id}
              onClick={() => loadSessionMessages(s.id)}
              style={{
                padding: '10px 12px', borderRadius: 8, cursor: 'pointer',
                background: activeSessionId === s.id ? 'rgba(34,197,94,0.08)' : 'transparent',
                border: `1px solid ${activeSessionId === s.id ? 'rgba(34,197,94,0.2)' : 'transparent'}`,
                transition: 'all 0.15s',
                display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: 13, color: activeSessionId === s.id ? '#22c55e' : '#f5f5f5',
                  whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', marginBottom: 2,
                }}>
                  {s.title || 'Sesi tanpa judul'}
                </div>
                <div style={{ fontSize: 11, color: '#525252' }}>{s.message_count} pesan</div>
              </div>
              <button
                onClick={(e) => deleteSession(s.id, e)}
                style={{ background: 'none', border: 'none', color: '#525252', cursor: 'pointer', fontSize: 14, padding: '0 0 0 6px', lineHeight: 1 }}
              >
                x
              </button>
            </div>
          ))}
          {sessions.length === 0 && (
            <div style={{ fontSize: 13, color: '#525252', textAlign: 'center', marginTop: 20 }}>
              Belum ada riwayat chat.
            </div>
          )}
        </div>
      </aside>

      {/* Chat area */}
      <main className="chat-main" style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '32px 40px', display: 'flex', flexDirection: 'column', gap: 20 }}>
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', marginTop: '25vh' }}>
              <div style={{ fontSize: 28, fontWeight: 700, letterSpacing: '-0.03em', marginBottom: 10 }}>
                FitMind<span style={{ color: '#22c55e' }}>AI</span>
              </div>
              <p style={{ fontSize: 15, color: '#a3a3a3', maxWidth: 360, margin: '0 auto' }}>
                Tanyakan tentang latihan, nutrisi, program gym, atau analisis tubuh Anda.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', marginTop: 24 }}>
                {[
                  'Latihan untuk otot dada',
                  'Berapa kalori dalam 100g ayam?',
                  'Rekomendasikan program untuk pemula',
                  'Makanan tinggi protein bebas gluten',
                ].map(suggestion => (
                  <button key={suggestion}
                    onClick={() => { setInput(suggestion) }}
                    className="btn-ghost" style={{ fontSize: 13 }}>
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              animation: 'fadeInUp 0.3s ease',
            }}>
              {msg.role === 'assistant' && (
                <div style={{
                  width: 28, height: 28, borderRadius: '50%', background: 'rgba(34,197,94,0.15)',
                  border: '1px solid rgba(34,197,94,0.3)', display: 'flex', alignItems: 'center',
                  justifyContent: 'center', fontSize: 12, color: '#22c55e', marginRight: 10, flexShrink: 0, marginTop: 2,
                }}>
                  AI
                </div>
              )}
              <div style={{
                maxWidth: '68%',
                background: msg.role === 'user' ? 'rgba(239,68,68,0.12)' : '#161616',
                border: `1px solid ${msg.role === 'user' ? 'rgba(239,68,68,0.25)' : '#2a2a2a'}`,
                borderRadius: msg.role === 'user' ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
                padding: '12px 16px',
                fontSize: 14,
                lineHeight: 1.65,
              }}>
                {msg.role === 'assistant' ? (
                  <div className="prose-chat">
                    <ReactMarkdown>{msg.content || (streaming && i === messages.length - 1 ? '...' : '')}</ReactMarkdown>
                  </div>
                ) : (
                  <span style={{ color: '#f5f5f5' }}>{msg.content}</span>
                )}
                {streaming && i === messages.length - 1 && msg.role === 'assistant' && msg.content === '' && (
                  <span style={{ color: '#22c55e' }}>...</span>
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={{
          padding: '16px 40px 28px',
          borderTop: '1px solid #2a2a2a',
          background: '#0a0a0a',
        }}>
          <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end', maxWidth: 760, margin: '0 auto' }}>
            <textarea
              className="input-field"
              rows={1}
              placeholder="Tanyakan sesuatu kepada FitMind AI..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              style={{ resize: 'none', minHeight: 44, maxHeight: 120, overflowY: 'auto', lineHeight: '1.5' }}
            />
            <button className="btn-primary" onClick={sendMessage} disabled={streaming || !input.trim()}
              style={{ padding: '11px 20px', flexShrink: 0 }}>
              Kirim
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
