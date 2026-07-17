import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

export default function RegisterPage() {
  const [username, setUsername] = useState('')
  const [phone, setPhone] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  async function handleRegister(e) {
    e.preventDefault()
    if (!username.trim() || !phone.trim()) return
    setLoading(true)
    setError('')
    setSuccess(false)
    try {
      await api.post('/users/register', { username: username.trim(), phone: phone.trim() })
      setSuccess(true)
      // Do not auto-login or redirect, so the user can see the success message

    } catch (err) {
      if (err.response?.status === 400) {
        setError('Username sudah terdaftar. Silakan gunakan nama lain atau masuk.')
      } else {
        setError('Gagal mendaftar. Pastikan backend berjalan.')
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
      padding: '0 20px',
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

      <div className="card animate-fadeinup" style={{ width: '100%', maxWidth: 400, padding: 40 }}>
        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 28, fontWeight: 700, letterSpacing: '-0.03em', marginBottom: 8 }}>
            FitMind<span style={{ color: '#22c55e' }}>AI</span>
          </div>
          <p style={{ color: '#a3a3a3', fontSize: 14 }}>
            Daftar akun baru
          </p>
        </div>

        {/* Divider line */}
        <div style={{ height: 1, background: '#2a2a2a', marginBottom: 28 }} />

        <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <label style={{ fontSize: 12, color: '#a3a3a3', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 8 }}>
              Username
            </label>
            <input
              className="input-field"
              type="text"
              placeholder="Masukkan username pilihanmu..."
              value={username}
              onChange={e => {
                setUsername(e.target.value)
                setSuccess(false)
                setError('')
              }}
              autoFocus
            />
          </div>

          <div>
            <label style={{ fontSize: 12, color: '#a3a3a3', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 8 }}>
              Nomor WhatsApp
            </label>
            <input
              className="input-field"
              type="text"
              placeholder="Contoh: 08123456789"
              value={phone}
              onChange={e => {
                setPhone(e.target.value)
                setSuccess(false)
                setError('')
              }}
            />
          </div>

          {error && (
            <div style={{ fontSize: 13, color: '#ef4444', padding: '8px 12px', background: 'rgba(239,68,68,0.08)', borderRadius: 6, border: '1px solid rgba(239,68,68,0.2)' }}>
              {error}
            </div>
          )}

          {success && (
            <div style={{ fontSize: 13, color: '#22c55e', padding: '8px 12px', background: 'rgba(34,197,94,0.08)', borderRadius: 6, border: '1px solid rgba(34,197,94,0.2)' }}>
              berhasil daftar username
            </div>
          )}

          <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%', padding: '12px 20px', marginTop: 4 }}>
            {loading ? 'Memproses...' : 'Daftar Username'}
          </button>
        </form>

        <p style={{ marginTop: 20, fontSize: 13, color: '#a3a3a3', textAlign: 'center' }}>
          Sudah punya akun?{' '}
          <button 
            onClick={() => navigate('/login')}
            style={{ background: 'none', border: 'none', color: '#22c55e', cursor: 'pointer', fontWeight: 600 }}
          >
            Masuk
          </button>
        </p>
      </div>
    </div>
  )
}
