/**
 * Toast — Komponen notifikasi custom FitMind AI.
 * Tema: dark mode (#0a0a0a), aksen hijau (#22c55e), merah (#ef4444).
 * Responsif mobile & desktop, auto-dismiss, slide-in animation.
 *
 * Usage:
 *   import { useToast, ToastContainer } from './Toast'
 *
 *   function App() {
 *     const { toasts, showToast } = useToast()
 *     showToast('Berhasil!', 'success')
 *     showToast('Token habis!', 'error')
 *     showToast('Memproses...', 'info')
 *     return <ToastContainer toasts={toasts} />
 *   }
 */
import { useState, useCallback } from 'react'

// ── Icons ───────────────────────────────────────────────────────────────────
const icons = {
  success: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  ),
  error: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="15" y1="9" x2="9" y2="15" />
      <line x1="9" y1="9" x2="15" y2="15" />
    </svg>
  ),
  info: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  ),
  warning: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  ),
}

// ── Theme per type ────────────────────────────────────────────────────────
const theme = {
  success: {
    color: '#22c55e',
    bg: 'rgba(34,197,94,0.08)',
    border: 'rgba(34,197,94,0.25)',
    bar: '#22c55e',
  },
  error: {
    color: '#ef4444',
    bg: 'rgba(239,68,68,0.08)',
    border: 'rgba(239,68,68,0.25)',
    bar: '#ef4444',
  },
  info: {
    color: '#60a5fa',
    bg: 'rgba(96,165,250,0.08)',
    border: 'rgba(96,165,250,0.25)',
    bar: '#60a5fa',
  },
  warning: {
    color: '#f59e0b',
    bg: 'rgba(245,158,11,0.08)',
    border: 'rgba(245,158,11,0.25)',
    bar: '#f59e0b',
  },
}

// ── Single Toast Item ─────────────────────────────────────────────────────
function ToastItem({ toast, onDismiss }) {
  const t = theme[toast.type] || theme.info

  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'flex-start',
        gap: 12,
        padding: '14px 16px',
        background: '#161616',
        border: `1px solid ${t.border}`,
        borderRadius: 12,
        boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
        minWidth: 280,
        maxWidth: 380,
        width: '100%',
        overflow: 'hidden',
        animation: 'toastSlideIn 0.3s cubic-bezier(0.34,1.56,0.64,1) both',
        backdropFilter: 'blur(8px)',
      }}
    >
      {/* Accent bar kiri */}
      <div style={{
        position: 'absolute',
        left: 0, top: 0, bottom: 0,
        width: 3,
        background: t.bar,
        borderRadius: '12px 0 0 12px',
      }} />

      {/* Icon */}
      <div style={{
        color: t.color,
        flexShrink: 0,
        marginTop: 1,
        display: 'flex',
        background: t.bg,
        padding: 6,
        borderRadius: 8,
      }}>
        {icons[toast.type] || icons.info}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        {toast.title && (
          <div style={{
            fontSize: 13,
            fontWeight: 700,
            color: t.color,
            marginBottom: 2,
            letterSpacing: '-0.01em',
          }}>
            {toast.title}
          </div>
        )}
        <div style={{
          fontSize: 13,
          color: '#d4d4d4',
          lineHeight: 1.5,
          wordBreak: 'break-word',
        }}>
          {toast.message}
        </div>
      </div>

      {/* Close button */}
      <button
        onClick={() => onDismiss(toast.id)}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          color: '#525252',
          padding: 2,
          display: 'flex',
          alignItems: 'center',
          flexShrink: 0,
          transition: 'color 0.15s',
          borderRadius: 4,
        }}
        onMouseEnter={e => e.currentTarget.style.color = '#a3a3a3'}
        onMouseLeave={e => e.currentTarget.style.color = '#525252'}
        aria-label="Tutup notifikasi"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>

      {/* Progress bar auto-dismiss */}
      <div style={{
        position: 'absolute',
        bottom: 0, left: 0,
        height: 2,
        background: t.bar,
        borderRadius: '0 0 12px 12px',
        opacity: 0.5,
        animation: `toastProgress ${toast.duration || 4000}ms linear both`,
      }} />
    </div>
  )
}

// ── Toast Container ───────────────────────────────────────────────────────
export function ToastContainer({ toasts, onDismiss }) {
  if (!toasts || toasts.length === 0) return null

  return (
    <>
      <style>{`
        @keyframes toastSlideIn {
          from { opacity: 0; transform: translateX(100%) scale(0.9); }
          to   { opacity: 1; transform: translateX(0) scale(1); }
        }
        @keyframes toastProgress {
          from { width: 100%; }
          to   { width: 0%; }
        }
        @media (max-width: 480px) {
          .toast-container {
            left: 12px !important;
            right: 12px !important;
            bottom: 80px !important;
            align-items: stretch !important;
          }
          .toast-container > div {
            max-width: 100% !important;
            min-width: unset !important;
          }
        }
      `}</style>
      <div
        className="toast-container"
        style={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
          alignItems: 'flex-end',
          pointerEvents: 'none',
        }}
      >
        {toasts.map(toast => (
          <div key={toast.id} style={{ pointerEvents: 'all', width: '100%', display: 'flex', justifyContent: 'flex-end' }}>
            <ToastItem toast={toast} onDismiss={onDismiss} />
          </div>
        ))}
      </div>
    </>
  )
}

// ── Hook useToast ─────────────────────────────────────────────────────────
export function useToast() {
  const [toasts, setToasts] = useState([])

  const dismiss = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  /**
   * showToast(message, type, options)
   * @param {string} message  - Pesan utama
   * @param {'success'|'error'|'info'|'warning'} type - Tipe notifikasi
   * @param {{ title?: string, duration?: number }} options
   */
  const showToast = useCallback((message, type = 'info', options = {}) => {
    const id = Date.now() + Math.random()
    const duration = options.duration || 4000
    const toast = { id, message, type, duration, title: options.title }

    setToasts(prev => [...prev, toast])

    // Auto dismiss
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, duration + 300) // +300ms untuk animasi keluar
  }, [])

  return { toasts, showToast, dismiss }
}
