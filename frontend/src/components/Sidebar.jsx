import { NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '▣' },
  { to: '/chat', label: 'AI Chat', icon: '◈' },
  { to: '/nutrition', label: 'Nutrition', icon: '◉' },
  { to: '/workout', label: 'Workout', icon: '◆' },
  { to: '/profile', label: 'Profile', icon: '◎' },
]

export default function Sidebar({ username }) {
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  function handleLogout() {
    localStorage.removeItem('fitmind_user')
    localStorage.removeItem('fitmind_profile')
    setMobileOpen(false)
    // Memaksa reload halaman agar state React (user) benar-benar terhapus
    window.location.href = '/login'
  }

  return (
    <>
      {/* ── Mobile Top Bar ──────────────────────────────────── */}
      <div className="sidebar-mobile-bar">
        <div style={{ fontSize: 18, fontWeight: 700 }}>
          FitMind<span style={{ color: '#22c55e' }}>AI</span>
        </div>
        <button
          onClick={() => setMobileOpen(prev => !prev)}
          style={{
            background: 'none', border: '1px solid #2a2a2a', color: '#f5f5f5',
            borderRadius: 8, padding: '6px 12px', cursor: 'pointer', fontSize: 20,
          }}
          aria-label="Toggle menu"
        >
          {mobileOpen ? '✕' : '☰'}
        </button>
      </div>

      {/* ── Mobile Drawer Overlay ───────────────────────────── */}
      {mobileOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className={`sidebar-aside ${mobileOpen ? 'sidebar-open' : ''}`}>
        {/* Logo (Desktop) */}
        <div className="sidebar-logo">
          <div style={{ fontSize: 20, fontWeight: 700, color: '#f5f5f5', letterSpacing: '-0.02em' }}>
            FitMind<span style={{ color: '#22c55e' }}>AI</span>
          </div>
          {username && (
            <div style={{ fontSize: 12, color: '#525252', marginTop: 4 }}>
              {username}
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1 }}>
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/dashboard'}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setMobileOpen(false)}
            >
              <span style={{ fontSize: 14 }}>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="btn-ghost"
          style={{ width: '100%', textAlign: 'left', marginTop: 16 }}
        >
          Logout
        </button>
      </aside>

      <style>{`
        /* ── Desktop Sidebar ── */
        .sidebar-aside {
          width: 220px;
          min-height: 100vh;
          background: #111111;
          border-right: 1px solid #2a2a2a;
          display: flex;
          flex-direction: column;
          padding: 24px 12px;
          position: fixed;
          top: 0;
          left: 0;
          z-index: 200;
          overflow-y: auto;
          box-sizing: border-box;
        }
        .sidebar-logo {
          padding-left: 14px;
          margin-bottom: 32px;
        }
        .sidebar-mobile-bar {
          display: none;
        }
        .sidebar-overlay {
          display: none;
        }

        /* ── Mobile ── */
        @media (max-width: 768px) {
          .sidebar-aside {
            top: 56px; /* di bawah top bar */
            height: calc(100dvh - 56px); /* gunakan dvh agar tidak tertutup browser UI bawah */
            transform: translateX(-100%);
            transition: transform 0.3s ease;
            padding-bottom: 24px; /* sesuaikan padding agar pas */
          }
          .sidebar-aside.sidebar-open {
            transform: translateX(0);
          }
          .sidebar-logo {
            display: none; /* Logo sudah ada di top bar */
          }
          .sidebar-mobile-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 56px;
            background: #111111;
            border-bottom: 1px solid #2a2a2a;
            padding: 0 16px;
            z-index: 300;
          }
          .sidebar-overlay {
            display: block;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.6);
            z-index: 150;
          }
        }
      `}</style>
    </>
  )
}
