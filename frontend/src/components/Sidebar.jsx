import { NavLink, useNavigate } from 'react-router-dom'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '▣' },
  { to: '/chat', label: 'AI Chat', icon: '◈' },
  { to: '/nutrition', label: 'Nutrition', icon: '◉' },
  { to: '/workout', label: 'Workout', icon: '◆' },
  { to: '/profile', label: 'Profile', icon: '◎' },
]

export default function Sidebar({ username }) {
  const navigate = useNavigate()

  function handleLogout() {
    localStorage.removeItem('fitmind_user')
    localStorage.removeItem('fitmind_profile')
    window.location.href = '/login'
  }

  return (
    <aside style={{
      width: 220,
      minHeight: '100vh',
      background: '#111111',
      borderRight: '1px solid #2a2a2a',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 12px',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 100,
    }}>
      {/* Logo */}
      <div style={{ paddingLeft: 14, marginBottom: 32 }}>
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
  )
}
