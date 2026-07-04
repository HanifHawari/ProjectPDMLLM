import { useNavigate } from 'react-router-dom'
import '../components/buttons.css'

const features = [
  {
    title: 'AI Personal Trainer',
    desc: 'Dapatkan rencana latihan yang dibuat khusus untukmu oleh AI berdasarkan tujuan, level, dan peralatanmu.',
    color: '#22c55e',
  },
  {
    title: 'Nutrisi Cerdas',
    desc: 'Temukan makanan, hitung kalori, dan dapatkan meal plan yang disesuaikan dengan preferensi dan alergimu.',
    color: '#ef4444',
  },
  {
    title: 'Tracking Kebugaran',
    desc: 'Pantau BMI, zona detak jantung, dan estimasi kalori harian secara real-time dari dashboard kamu.',
    color: '#22c55e',
  },
]

const stats = [
  { value: '35K+', label: 'Data Nutrisi' },
  { value: '2,500+', label: 'Program Latihan' },
  { value: '24/7', label: 'AI Siap Membantu' },
  { value: '100%', label: 'Dipersonalisasi' },
]

const steps = [
  { step: '01', title: 'Daftar Tanpa Ribet', desc: 'Cukup masukkan username pilihanmu. Tidak perlu email atau password.' },
  { step: '02', title: 'Personalisasi Profil', desc: 'Ceritakan sedikit tentang dirimu: tinggi, berat, dan tujuan fitness (Turun BB / Bentuk Otot).' },
  { step: '03', title: 'Terima Rencana AI', desc: 'AI akan langsung menyusun program latihan harian dan menu nutrisi khusus untukmu.' },
]

const creators = [
  { name: 'M Hanif Hawari', role: 'Backend Developer', image: '/foto1.png' },
  { name: 'M Dian Fauzi', role: 'Frontend Developer', image: '/foto2.png' },
  { name: 'Adhitya Surya Handika', role: 'AI Engineer', image: '/foto3.png' },
]

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div style={{ background: '#0a0a0a', color: '#f5f5f5', fontFamily: "'Inter', system-ui, sans-serif", overflowX: 'hidden' }}>

      {/* ── HERO SECTION ─────────────────────────────────── */}
      <section style={{ position: 'relative', minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start', overflow: 'hidden' }}>

        {/* Background video */}
        <video
          autoPlay
          loop
          muted
          playsInline
          poster="/gym_hero_bg.png"
          style={{
            position: 'absolute', inset: 0,
            width: '100%', height: '100%', objectFit: 'cover',
            filter: 'brightness(0.45)',
            zIndex: 0,
          }}
        >
          <source src="/gym_bg.mp4" type="video/mp4" />
        </video>

        {/* Color overlay */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(120deg, rgba(0,0,0,0.85) 0%, rgba(10,10,10,0.6) 50%, rgba(34,197,94,0.08) 100%)',
          zIndex: 1,
        }} />

        {/* Green bottom gradient */}
        <div style={{
          position: 'absolute', bottom: 0, left: 0, right: 0, height: 3,
          background: 'linear-gradient(90deg, transparent, #22c55e, transparent)',
          zIndex: 2,
        }} />

        {/* Navbar */}
        <nav className="nav-container" style={{
          position: 'absolute', top: 0, left: 0, right: 0,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          zIndex: 10,
        }}>
          <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: '-0.02em' }}>
            FitMind<span style={{ color: '#22c55e' }}>AI</span>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <button onClick={() => navigate('/login')}
              style={{
                background: 'none', border: '1px solid rgba(255,255,255,0.2)',
                color: '#f5f5f5', padding: '9px 22px', borderRadius: 8,
                cursor: 'pointer', fontSize: 14, fontWeight: 500, fontFamily: 'inherit',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { e.target.style.borderColor = '#22c55e'; e.target.style.color = '#22c55e' }}
              onMouseLeave={e => { e.target.style.borderColor = 'rgba(255,255,255,0.2)'; e.target.style.color = '#f5f5f5' }}
            >
              Masuk
            </button>
            <button onClick={() => navigate('/register')} className="btn-charger">
              Daftar Gratis
            </button>
          </div>
        </nav>

        {/* Hero content */}
        <div className="section-px" style={{ position: 'relative', zIndex: 5, maxWidth: 760 }}>
          <div style={{ fontSize: 12, letterSpacing: '0.18em', color: '#22c55e', textTransform: 'uppercase', marginBottom: 20, fontWeight: 600 }}>
            Platform Kebugaran Berbasis AI
          </div>
          <h1 style={{
            fontSize: 'clamp(42px, 6vw, 80px)', fontWeight: 800,
            lineHeight: 1.05, letterSpacing: '-0.04em', marginBottom: 24,
          }}>
            Latihan Lebih
            <span style={{
              display: 'block',
              background: 'linear-gradient(90deg, #22c55e, #16a34a)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            }}>
              Cerdas Bersama AI
            </span>
          </h1>
          <p style={{ fontSize: 18, color: '#a3a3a3', maxWidth: 540, lineHeight: 1.7, marginBottom: 40 }}>
            Program latihan personal, nutrisi tepat sasaran, dan pendampingan AI aktif 24 jam. Capai tubuh impianmu lebih cepat.
          </p>
          <div style={{ display: 'flex', gap: 14 }}>
            <button onClick={() => navigate('/register')} className="btn-charger btn-charger-large">
              Mulai Sekarang
            </button>
            <button onClick={() => document.getElementById('fitur').scrollIntoView({ behavior: 'smooth' })}
              style={{
                background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.15)',
                color: '#f5f5f5', padding: '14px 36px', borderRadius: 10,
                cursor: 'pointer', fontSize: 16, fontWeight: 500, fontFamily: 'inherit',
                backdropFilter: 'blur(8px)',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => e.target.style.background = 'rgba(255,255,255,0.12)'}
              onMouseLeave={e => e.target.style.background = 'rgba(255,255,255,0.07)'}
            >
              Pelajari Fitur
            </button>
          </div>
        </div>

        {/* Scroll indicator */}
        <div style={{
          position: 'absolute', bottom: 36, left: '50%', transform: 'translateX(-50%)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
          zIndex: 5, animation: 'bounce 2s infinite',
        }}>
          <div style={{ width: 1, height: 48, background: 'linear-gradient(to bottom, transparent, #22c55e)' }} />
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e' }} />
        </div>
      </section>

      {/* ── STATS ─────────────────────────────────────────── */}
      <section className="section-px py-12" style={{
        background: '#111111',
        borderTop: '1px solid #1e1e1e',
        borderBottom: '1px solid #1e1e1e',
        display: 'flex',
        justifyContent: 'space-around',
        flexWrap: 'wrap',
        gap: 24,
      }}>
        {stats.map((s, i) => (
          <div key={i} style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 40, fontWeight: 800, letterSpacing: '-0.03em', color: '#ffffff' }}>
              {s.value}
            </div>
            <div style={{ fontSize: 13, color: '#525252', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 4 }}>
              {s.label}
            </div>
          </div>
        ))}
      </section>

      {/* ── FEATURES ──────────────────────────────────────── */}
      <section id="fitur" className="section-px py-24" style={{ maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 64 }}>
          <div style={{ fontSize: 12, letterSpacing: '0.18em', color: '#22c55e', textTransform: 'uppercase', marginBottom: 14, fontWeight: 600 }}>
            Fitur Unggulan
          </div>
          <h2 style={{ fontSize: 'clamp(28px, 4vw, 48px)', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.1 }}>
            Satu Platform, Semua
            <span style={{ color: '#22c55e' }}> yang Kamu Butuhkan</span>
          </h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 }}>
          {features.map((f, i) => (
            <FeatureCard key={i} {...f} />
          ))}
        </div>
      </section>

      {/* ── HOW IT WORKS ──────────────────────────────────── */}
      <section className="section-px py-24" style={{ background: '#0a0a0a', borderTop: '1px solid #1e1e1e' }}>
        <div style={{ textAlign: 'center', marginBottom: 64 }}>
          <div style={{ fontSize: 12, letterSpacing: '0.18em', color: '#22c55e', textTransform: 'uppercase', marginBottom: 14, fontWeight: 600 }}>
            Proses Sederhana
          </div>
          <h2 style={{ fontSize: 'clamp(28px, 4vw, 48px)', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.1 }}>
            Cara Kerja <span style={{ color: '#22c55e' }}>FitMind AI</span>
          </h2>
        </div>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 40,
          maxWidth: 1000, margin: '0 auto', position: 'relative'
        }}>
          {steps.map((s, i) => (
            <div key={i} style={{ textAlign: 'center', position: 'relative', zIndex: 2 }}>
              <div style={{
                width: 64, height: 64, borderRadius: '50%', background: '#111', border: '1px solid #22c55e',
                display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px',
                fontSize: 24, fontWeight: 800, color: '#22c55e', boxShadow: '0 0 20px rgba(34,197,94,0.15)'
              }}>
                {s.step}
              </div>
              <h3 style={{ fontSize: 20, fontWeight: 700, marginBottom: 12 }}>{s.title}</h3>
              <p style={{ fontSize: 15, color: '#a3a3a3', lineHeight: 1.6 }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CREATORS ──────────────────────────────────── */}
      <section className="section-px py-24" style={{ background: '#111111', borderTop: '1px solid #1e1e1e' }}>
        <div style={{ textAlign: 'center', marginBottom: 64 }}>
          <div style={{ fontSize: 12, letterSpacing: '0.18em', color: '#22c55e', textTransform: 'uppercase', marginBottom: 14, fontWeight: 600 }}>
            Tim Pengembang
          </div>
          <h2 style={{ fontSize: 'clamp(28px, 4vw, 48px)', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.1 }}>
            Di Balik <span style={{ color: '#22c55e' }}>FitMind AI</span>
          </h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 40, maxWidth: 900, margin: '0 auto' }}>
          {creators.map((c, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div style={{
                width: 200, height: 200, margin: '0 auto 24px',
                borderRadius: '16px', background: '#1a1a1a', border: '2px solid #2a2a2a',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 12px 30px rgba(0,0,0,0.5)',
                overflow: 'hidden',
                position: 'relative'
              }}>
                {/* Gunakan gambar dari data array c.image */}
                <img src={c.image} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt={c.name} />
              </div>
              <h3 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8, color: '#f5f5f5' }}>{c.name}</h3>
              <div style={{ fontSize: 14, color: '#22c55e', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{c.role}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA SECTION ───────────────────────────────────── */}
      <section className="section-px py-24" style={{
        background: 'linear-gradient(135deg, #111 0%, #0a1a10 50%, #111 100%)',
        borderTop: '1px solid #1e1e1e',
        borderBottom: '1px solid #1e1e1e',
        textAlign: 'center',
      }}>
        <div style={{
          display: 'inline-block',
          padding: '4px 14px', borderRadius: 20,
          background: 'rgba(34,197,94,0.1)',
          border: '1px solid rgba(34,197,94,0.25)',
          fontSize: 12, color: '#22c55e',
          textTransform: 'uppercase', letterSpacing: '0.12em',
          marginBottom: 24, fontWeight: 600,
        }}>
          Gratis Selamanya
        </div>
        <h2 style={{ fontSize: 'clamp(28px, 4vw, 52px)', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 16 }}>
          Siap Mulai Transformasimu?
        </h2>
        <p style={{ fontSize: 17, color: '#a3a3a3', marginBottom: 40, maxWidth: 480, margin: '0 auto 40px' }}>
          Daftar dengan username pilihanmu. Tidak perlu email atau password, mulai dalam 10 detik.
        </p>
        <button onClick={() => navigate('/register')} className="btn-charger btn-charger-xl">
          Daftar Sekarang
        </button>
      </section>

      {/* ── FOOTER ────────────────────────────────────────── */}
      <footer className="section-px py-8" style={{ background: '#0a0a0a', borderTop: '1px solid #1a1a1a', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div style={{ fontSize: 18, fontWeight: 700 }}>
          FitMind<span style={{ color: '#22c55e' }}>AI</span>
        </div>
        <div style={{ fontSize: 12, color: '#525252' }}>
          Platform Kebugaran dan Nutrisi Berbasis Kecerdasan Buatan
        </div>

      </footer>

      {/* ── FLOATING CHAT BUTTON ──────────────────────────── */}
      <button
        onClick={() => navigate('/login')}
        title="Mulai Chat dengan AI"
        style={{
          position: 'fixed', bottom: 32, right: 32, zIndex: 999,
          width: 58, height: 58, borderRadius: '50%',
          background: '#22c55e', border: 'none',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', boxShadow: '0 0 24px rgba(34,197,94,0.5)',
          transition: 'all 0.2s',
        }}
        onMouseEnter={e => { e.currentTarget.style.background = '#16a34a'; e.currentTarget.style.transform = 'scale(1.1)'; e.currentTarget.style.boxShadow = '0 0 36px rgba(34,197,94,0.7)' }}
        onMouseLeave={e => { e.currentTarget.style.background = '#22c55e'; e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = '0 0 24px rgba(34,197,94,0.5)' }}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="#000" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      <style>{`
        .nav-container { padding: 24px 60px; }
        .section-px { padding-left: 60px; padding-right: 60px; }
        .py-12 { padding-top: 48px; padding-bottom: 48px; }
        .py-24 { padding-top: 100px; padding-bottom: 100px; }
        .py-8 { padding-top: 36px; padding-bottom: 36px; }

        @media (max-width: 768px) {
          .nav-container { padding: 16px 20px; }
          .section-px { padding-left: 20px; padding-right: 20px; }
          .py-12 { padding-top: 32px; padding-bottom: 32px; }
          .py-24 { padding-top: 60px; padding-bottom: 60px; }
          .py-8 { padding-top: 24px; padding-bottom: 24px; }
        }

        @keyframes bounce {
          0%, 100% { transform: translateX(-50%) translateY(0); }
          50% { transform: translateX(-50%) translateY(8px); }
        }
      `}</style>
    </div>
  )
}

function FeatureCard({ title, desc, color }) {
  return (
    <div
      style={{
        background: `linear-gradient(rgba(17,17,17,0.92), rgba(17,17,17,0.92)), url(/gym_hero_bg.png)`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        border: '1px solid #1e1e1e',
        borderRadius: 16, padding: 32,
        transition: 'all 0.3s',
        cursor: 'default',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = color
        e.currentTarget.style.transform = 'translateY(-4px)'
        e.currentTarget.style.boxShadow = `0 12px 40px ${color}18`
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = '#1e1e1e'
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      <div style={{ width: 3, height: 28, background: color, borderRadius: 2, marginBottom: 20 }} />
      <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 12, letterSpacing: '-0.01em' }}>{title}</div>
      <div style={{ fontSize: 14, color: '#525252', lineHeight: 1.65 }}>{desc}</div>
    </div>
  )
}
