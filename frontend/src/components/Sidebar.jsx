import { NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'

// SVG Icons — transparan seperti sketsa outline
const Icons = {
  dashboard: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.45">
      <rect x="3" y="3" width="7" height="7" rx="1"/>
      <rect x="14" y="3" width="7" height="7" rx="1"/>
      <rect x="3" y="14" width="7" height="7" rx="1"/>
      <rect x="14" y="14" width="7" height="7" rx="1"/>
    </svg>
  ),
  chat: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.45">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      <line x1="9" y1="10" x2="15" y2="10"/>
      <line x1="9" y1="14" x2="13" y2="14"/>
    </svg>
  ),
  nutrition: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.45">
      <path d="M12 2a9 9 0 0 1 9 9c0 4.97-4.03 9-9 9S3 15.97 3 11a9 9 0 0 1 9-9z"/>
      <path d="M12 2c0 4-2 7-2 9s2 5 2 9"/>
      <path d="M5.5 9h13"/>
    </svg>
  ),
  workout: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.45">
      <path d="M6 5v14"/>
      <path d="M18 5v14"/>
      <path d="M3 8h3"/>
      <path d="M3 16h3"/>
      <path d="M18 8h3"/>
      <path d="M18 16h3"/>
      <path d="M6 12h12"/>
    </svg>
  ),
  profile: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.45">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
      <circle cx="12" cy="7" r="4"/>
    </svg>
  ),
}

const navItems = [
  { to: '/dashboard', label: 'Dashboard', iconKey: 'dashboard' },
  { to: '/chat',      label: 'AI Chat',   iconKey: 'chat'      },
  { to: '/nutrition', label: 'Nutrition', iconKey: 'nutrition' },
  { to: '/workout',   label: 'Workout',   iconKey: 'workout'   },
  { to: '/profile',   label: 'Profile',   iconKey: 'profile'   },
]

export default function Sidebar({ username }) {
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  function handleLogout() {
    localStorage.removeItem('fitmind_user')
    localStorage.removeItem('fitmind_profile')
    setMobileOpen(false)
    window.location.href = '/'
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
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/dashboard'}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setMobileOpen(false)}
            >
              {/* Icon transparan background besar */}
              <span className="nav-icon-bg">
                {Icons[item.iconKey]}
              </span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="btn-ghost sidebar-logout"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
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
        .sidebar-logout {
          width: 100%;
          text-align: left;
          margin-top: 16px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        /* Nav icon background */
        .nav-icon-bg {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 30px;
          height: 30px;
          border-radius: 8px;
          background: rgba(163,163,163,0.06);
          flex-shrink: 0;
          transition: background 0.2s;
        }
        .nav-item.active .nav-icon-bg {
          background: rgba(34,197,94,0.12);
        }
        .nav-item.active .nav-icon-bg svg {
          stroke: #22c55e;
          opacity: 0.8;
        }
        .nav-item:hover .nav-icon-bg {
          background: rgba(163,163,163,0.1);
        }

        /* ── Mobile ── */
        @media (max-width: 768px) {
          .sidebar-aside {
            top: 56px;
            height: calc(100dvh - 56px);
            transform: translateX(-100%);
            transition: transform 0.3s ease;
            /* Padding bottom agar ada sedikit ruang saat scroll sampai bawah */
            padding-bottom: 16px;
          }
          .sidebar-aside.sidebar-open {
            transform: translateX(0);
          }
          .sidebar-logo {
            display: none;
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
