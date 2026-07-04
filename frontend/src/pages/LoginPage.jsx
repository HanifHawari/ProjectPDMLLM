import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleLogin(e) {
    e.preventDefault()
    if (!username.trim()) return
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/users/login', { username: username.trim() })
      const user = res.data
      localStorage.setItem('fitmind_user', JSON.stringify({
        username: user.username,
        id: user.id,
        is_new: user.is_new,
        has_profile: user.has_profile,
      }))
      // Always redirect to dashboard on successful login
      window.location.href = '/dashboard'
    } catch (err) {
      if (err.response?.status === 404) {
        setError('username belum terdaftar')
      } else {
        setError('Gagal masuk. Pastikan backend berjalan.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0a0a0a',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background gradient blobs */}
      <div style={{
        position: 'absolute', width: 500, height: 500,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(34,197,94,0.08) 0%, transparent 70%)',
        top: '-100px', right: '-100px', pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute', width: 400, height: 400,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(239,68,68,0.07) 0%, transparent 70%)',
        bottom: '-80px', left: '-80px', pointerEvents: 'none',
      }} />

      <div className="card animate-fadeinup" style={{ width: 400, padding: 40 }}>
        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 28, fontWeight: 700, letterSpacing: '-0.03em', marginBottom: 8 }}>
            FitMind<span style={{ color: '#22c55e' }}>AI</span>
          </div>
          <p style={{ color: '#a3a3a3', fontSize: 14 }}>
            Masuk ke akun Anda
          </p>
        </div>

        {/* Divider line */}
        <div style={{ height: 1, background: '#2a2a2a', marginBottom: 28 }} />

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <label style={{ fontSize: 12, color: '#a3a3a3', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 8 }}>
              Username
            </label>
            <input
              className="input-field"
              type="text"
              placeholder="Masukkan username..."
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoFocus
            />
          </div>

          {error && (
            <div style={{ fontSize: 13, color: '#ef4444', padding: '8px 12px', background: 'rgba(239,68,68,0.08)', borderRadius: 6, border: '1px solid rgba(239,68,68,0.2)' }}>
              {error}
            </div>
          )}

          <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%', padding: '12px 20px', marginTop: 4 }}>
            {loading ? 'Memproses...' : 'Masuk'}
          </button>
        </form>

        <p style={{ marginTop: 20, fontSize: 13, color: '#a3a3a3', textAlign: 'center' }}>
          Belum punya akun?{' '}
          <button 
            onClick={() => navigate('/register')}
            style={{ background: 'none', border: 'none', color: '#22c55e', cursor: 'pointer', fontWeight: 600 }}
          >
            Daftar di sini
          </button>
        </p>
      </div>
    </div>
  )
}
