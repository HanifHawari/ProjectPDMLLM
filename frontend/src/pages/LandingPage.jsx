import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import './LandingPage.css'

function DevNoticeModal({ onClose }) {
  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handleKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handleKey)
      document.body.style.overflow = ''
    }
  }, [onClose])

  return (
    <div className="dev-modal-backdrop" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="dev-modal-title">
      <div className="dev-modal" onClick={e => e.stopPropagation()}>
        <div className="dev-modal-icon" aria-hidden="true">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        </div>
        <h2 id="dev-modal-title">Sedang dalam pengembangan</h2>
        <p>Sistem sedang dalam pengembangan. Data dan tampilan dapat berubah sewaktu-waktu.</p>
        <button className="dev-modal-close" onClick={onClose}>Mengerti</button>
      </div>
    </div>
  )
}

const navItems = [
  { label: 'Manfaat', href: '#manfaat' },
  { label: 'Fitur', href: '#fitur' },
  { label: 'AI Chat', href: '#ai-chat' },
  { label: 'FAQ', href: '#faq' },
]

const problems = [
  {
    title: 'Bingung memilih latihan',
    solution: 'Buat rencana latihan berdasarkan tujuan, level, jumlah hari, dan peralatanmu.',
  },
  {
    title: 'Sulit mengatur makanan',
    solution: 'Cari makanan, gunakan filter alergen, dan susun meal plan dari satu tempat.',
  },
  {
    title: 'Informasi tersebar',
    solution: 'Akses AI Chat, kalkulator kebugaran, workout, dan nutrisi melalui satu aplikasi.',
  },
]

const features = [
  {
    title: 'AI Chat',
    description: 'Tanyakan hal seputar latihan, nutrisi, dan kebugaran. Kamu juga dapat membuka kembali riwayat percakapan.',
    to: '/chat',
    image: '/foto6.jpg',
  },
  {
    title: 'AI Plan',
    description: 'Buat rencana workout atau meal plan dengan pilihan tujuan, tingkat pengalaman, peralatan, dan preferensi makan.',
    to: '/plan',
    image: '/foto7.jpg',
  },
  {
    title: 'Nutrisi & Alergen',
    description: 'Cari informasi makanan, jelajahi makanan sehat, dan saring hasil berdasarkan pantangan tertentu.',
    to: '/nutrition',
    image: '/foto9.jpg',
  },
  {
    title: 'Workout',
    description: 'Temukan gerakan berdasarkan nama atau bagian tubuh, lalu jelajahi daftar program menurut level.',
    to: '/workout',
    image: '/foto8.jpg',
  },
  {
    title: 'Smart Tools',
    description: 'Gunakan kalkulator BMI, estimasi kalori latihan, dan analisis zona detak jantung di dashboard.',
    to: '/dashboard',
    image: '/foto10.jpg',
  },
]

const highlights = [
  { image: '/foto1.jpg', to: '/workout', label: 'Jelajahi Workout' },
  { image: '/foto2.jpg', to: '/plan', label: 'Buat AI Plan' },
  { image: '/foto4.jpg', to: '/chat', label: 'Buka AI Chat' },
]

const gallery = [
  { image: '/foto3.jpg', title: 'Mulai bergerak', to: '/workout' },
  { image: '/foto5.jpg', title: 'Tentukan tujuan', to: '/plan' },
  { image: '/foto11.jpg', title: 'Bangun kebiasaan', to: '/dashboard' },
  { image: '/foto12.jpg', title: 'Terus berkembang', to: '/workout' },
  { image: '/foto13.jpg', title: 'Temukan ritmemu', to: '/workout' },
]

const questions = [
  {
    question: 'Apakah saya memerlukan email untuk mendaftar?',
    answer: 'Tidak. Form pendaftaran saat ini meminta username, nomor WhatsApp, dan password.',
  },
  {
    question: 'Apakah rencana latihan langsung dibuat setelah daftar?',
    answer: 'Setelah masuk, buka AI Plan dan pilih tujuan, level, hari latihan, serta peralatan. Rencana dibuat ketika kamu menekan tombol Generate.',
  },
  {
    question: 'Bisakah saya mencari makanan sesuai pantangan?',
    answer: 'Pencarian makanan menyediakan filter untuk gluten, susu, kacang, kedelai, telur, dan ikan. Tetap periksa informasi produk sebelum dikonsumsi.',
  },
  {
    question: 'Apa saja yang ada di dashboard?',
    answer: 'Dashboard menyediakan kalkulator BMI, estimasi kalori latihan, dan analisis zona detak jantung. Masukkan data yang diminta untuk melihat hasilnya.',
  },
]

const iconPaths = {
  arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
  check: <><path d="m5 12 4 4L19 6" /></>,
  chat: <><path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H6l-3 2v-6.5A7.5 7.5 0 1 1 20 11.5Z" /><path d="M8 11h8M8 14h5" /></>,
  menu: <><path d="M4 7h16M4 12h16M4 17h16" /></>,
  close: <><path d="M5 5l14 14M19 5 5 19" /></>,
}

function Icon({ name, size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {iconPaths[name]}
    </svg>
  )
}
function SectionHeading({ title, description }) {
  return (
    <div className="landing-section-heading landing-reveal" data-reveal>
      <h2>{title}</h2>
      {description && <p>{description}</p>}
    </div>
  )
}

export default function LandingPage() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [showDevModal, setShowDevModal] = useState(false)
  const pageRef = useRef(null)

  const handleAuthClick = (e) => {
    e.preventDefault()
    setMenuOpen(false)
    setShowDevModal(true)
  }

  useEffect(() => {
    const page = pageRef.current
    if (!page || !('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    const observer = new IntersectionObserver((entries, activeObserver) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          activeObserver.unobserve(entry.target)
        }
      })
    }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' })

    page.classList.add('has-scroll-animations')
    page.querySelectorAll('[data-reveal]').forEach(element => observer.observe(element))

    return () => {
      observer.disconnect()
      page.classList.remove('has-scroll-animations')
    }
  }, [])

  useEffect(() => {
    const videos = pageRef.current?.querySelectorAll('[data-play-on-view]')
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      pageRef.current?.querySelectorAll('video').forEach(item => item.pause())
      return
    }
    if (!videos?.length) return

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) entry.target.play().catch(() => {})
        else entry.target.pause()
      })
    }, { rootMargin: '120px 0px' })

    videos.forEach(video => observer.observe(video))
    return () => {
      observer.disconnect()
      videos.forEach(video => video.pause())
    }
  }, [])

  return (
    <div className="landing-page" ref={pageRef}>
      {showDevModal && <DevNoticeModal onClose={() => setShowDevModal(false)} />}
      <header className="landing-header">
        <div className="landing-shell landing-header-inner">
          <Link className="landing-brand" to="/" aria-label="FitMindAI, beranda">
            FitMind<span>AI</span>
          </Link>

          <nav id="landing-navigation" className={'landing-nav' + (menuOpen ? ' is-open' : '')} aria-label="Navigasi landing page">
            {navItems.map(item => (
              <a key={item.href} href={item.href} onClick={() => setMenuOpen(false)}>{item.label}</a>
            ))}
            <div className="landing-mobile-actions">
              <a href="/login" onClick={handleAuthClick}>Masuk</a>
              <a href="/register" className="landing-button landing-button-primary" onClick={handleAuthClick}>Daftar Gratis</a>
            </div>
          </nav>

          <div className="landing-header-actions">
            <a className="landing-login-link" href="/login" onClick={handleAuthClick}>Masuk</a>
            <a className="landing-button landing-button-primary" href="/register" onClick={handleAuthClick}>Daftar Gratis</a>
          </div>
          <button
            className="landing-menu-button"
            type="button"
            aria-label={menuOpen ? 'Tutup menu' : 'Buka menu'}
            aria-controls="landing-navigation"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen(open => !open)}
          >
            <Icon name={menuOpen ? 'close' : 'menu'} />
          </button>
        </div>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-hero-videos" aria-hidden="true">
            <video src="/vid2.mp4" autoPlay loop muted playsInline preload="metadata" />
            <video src="/vid3.mp4" autoPlay loop muted playsInline preload="metadata" />
            <video src="/vid4.mp4" autoPlay loop muted playsInline preload="metadata" />
          </div>
          <div className="landing-shell landing-hero-grid">
            <div className="landing-hero-copy">
              <h1>GO FURTHER IN LIFE<br />LATIH LEBIH <span>CERDAS</span><br />BERSAMA AI</h1>
              <p>Program latihan terukur, perencanaan nutrisi spesifik bebas alergen, dan asisten sains olahraga.</p>
              <div className="landing-hero-actions">
                <a className="landing-button landing-button-primary landing-button-large" href="/register" onClick={handleAuthClick}>
                  Daftar Sekarang
                </a>
                <a className="landing-button landing-button-secondary landing-button-large" href="#fitur">Pelajari Fitur</a>
              </div>
            </div>
          </div>
        </section>

        <section className="landing-highlights" aria-label="Jelajahi FitMindAI">
          <div className="landing-shell landing-highlight-grid" data-reveal>
            {highlights.map((item, index) => (
              <a className={'landing-highlight-card landing-highlight-card-' + (index + 1)} key={item.to} href={item.to} aria-label={item.label} onClick={handleAuthClick}>
                <img className="landing-highlight-media" src={item.image} alt="" loading="lazy" />
              </a>
            ))}
          </div>
        </section>

        <section id="manfaat" className="landing-section landing-section-alt">
          <div className="landing-shell landing-benefit-grid">
            <div className="landing-benefit-copy landing-reveal" data-reveal>
              <h2>Hentikan latihan tanpa arah dan <span>Mulai dengan rencana yang jelas</span></h2>
              <p className="landing-benefit-intro">FitMindAI membantu menghubungkan pilihan latihan, nutrisi, dan informasi kebugaran dalam satu alur.</p>
              <div className="landing-benefit-list landing-cascade" data-reveal>
                {problems.map(problem => (
                  <article className="landing-benefit-item" key={problem.title}>
                    <span className="landing-benefit-check"><Icon name="check" size={19} /></span>
                    <div>
                      <h3>{problem.title}</h3>
                      <p>{problem.solution}</p>
                    </div>
                  </article>
                ))}
              </div>
              <a className="landing-button landing-button-primary" href="#fitur">Jelajahi fitur</a>
            </div>
            <div className="landing-benefit-photo landing-reveal" data-reveal>
              <video src="/vid1.mp4" poster="/foto3.jpg" muted loop playsInline preload="none" aria-hidden="true" data-play-on-view />
            </div>
          </div>
        </section>

        <section id="fitur" className="landing-section">
          <div className="landing-shell">
            <SectionHeading
              title="SEMUA KEBUTUHAN KEBUGARANMU DALAM SATU PLATFORM"
              description="Pilih fitur yang kamu perlukan, dari mencari gerakan hingga membuat rencana latihan dan makan."
            />
            <div className="landing-marquee-outer" aria-label="Fitur FitMindAI">
              <div className="landing-marquee-track">
                {[...features, ...features].map((feature, i) => (
                  <a className="landing-feature-card" href={feature.to} key={feature.title + i} onClick={handleAuthClick}>
                    <img className="landing-feature-media" src={feature.image} alt="" loading="lazy" />
                    <span className="landing-feature-shade" aria-hidden="true" />
                    <span className="landing-feature-content">
                      <h3>{feature.title}</h3>
                      <p>{feature.description}</p>
                    </span>
                  </a>
                ))}
              </div>
            </div>
          </div>
        </section>





        <section id="ai-chat" className="landing-section landing-chat-section">
          <video className="landing-chat-video" src="/gym_bg.mp4" poster="/foto4.jpg" muted loop playsInline preload="none" aria-hidden="true" data-play-on-view />
          <div className="landing-shell landing-chat-grid">
            <div className="landing-chat-copy landing-reveal" data-reveal>
              <h2>Ada pertanyaan tentang latihan atau nutrisi?</h2>
              <p>Buka AI Chat untuk mengajukan pertanyaan. Percakapanmu tersimpan sehingga dapat dibaca kembali saat dibutuhkan.</p>
              <a className="landing-button landing-button-primary" href="/chat" onClick={handleAuthClick}>Buka AI Chat</a>
            </div>
            <div className="landing-chat-preview landing-reveal" data-reveal>
              <div className="landing-chat-preview-header">
                <span className="landing-chat-avatar"><Icon name="chat" size={20} /></span>
                <div><strong>FitMindAI Chat</strong><small>Contoh topik yang bisa ditanyakan</small></div>
              </div>
              <div className="landing-chat-preview-body">
                <p>Mulai dari pertanyaan yang paling dekat dengan rutinitasmu.</p>
                <div className="landing-chat-suggestions">
                  <span>Bagaimana memilih latihan untuk pemula?</span>
                  <span>Apa informasi nutrisi makanan ini?</span>
                  <span>Bagaimana menyusun jadwal latihan?</span>
                </div>
              </div>
              <div className="landing-chat-preview-input">Tulis pertanyaanmu di AI Chat <Icon name="arrow" size={18} /></div>
            </div>
          </div>
        </section>

        <section className="landing-section landing-gallery" aria-label="Inspirasi aktivitas">
          <div className="landing-shell">
            <SectionHeading
              title="Temukan ritme yang cocok untukmu."
              description="Pilih titik awalmu, susun rencana, lalu gunakan fitur yang kamu perlukan sepanjang perjalanan."
            />
            <div className="landing-gallery-grid landing-cascade" data-reveal>
              {gallery.map(item => (
                <a className="landing-gallery-card" href={item.to} key={item.title} onClick={handleAuthClick}>
                  <img src={item.image} alt="" loading="lazy" />
                  <span>{item.title}</span>
                </a>
              ))}
            </div>
          </div>
        </section>

        <section id="faq" className="landing-section landing-section-alt">
          <div className="landing-shell">
            <SectionHeading
              title="Hal yang sering ditanyakan."
              description="Kenali alur aplikasi sebelum memulai."
            />
            <div className="landing-faq-list landing-cascade" data-reveal>
              {questions.map((item, index) => (
                <details key={item.question} open={index === 0}>
                  <summary>{item.question}<span aria-hidden="true">+</span></summary>
                  <p>{item.answer}</p>
                </details>
              ))}
            </div>
          </div>
        </section>

      </main>

      <footer className="landing-footer">
        <div className="landing-shell landing-footer-grid landing-reveal" data-reveal>
          <div>
            <Link className="landing-brand" to="/">FitMind<span>AI</span></Link>
            <p>Platform kebugaran berbasis AI untuk latihan, nutrisi, dan rencana yang lebih terarah.</p>
          </div>
          <div><h3>Jelajahi</h3><a href="#fitur">Fitur</a><a href="#personalisasi">Personalisasi</a></div>
          <div><h3>Fitur aplikasi</h3><a href="/plan" onClick={handleAuthClick}>AI Plan</a><a href="/nutrition" onClick={handleAuthClick}>Nutrisi</a><a href="/workout" onClick={handleAuthClick}>Workout</a></div>
          <div><h3>Akun & bantuan</h3><a href="/login" onClick={handleAuthClick}>Masuk</a><a href="/register" onClick={handleAuthClick}>Daftar</a><a href="#faq">Pertanyaan Umum</a></div>
        </div>
        <div className="landing-shell landing-footer-bottom"><span>© {new Date().getFullYear()} FitMindAI</span><span>Dibuat untuk langkah yang lebih terarah.</span></div>
      </footer>

      <a className="landing-floating-chat" href="/chat" aria-label="Buka AI Chat" title="Buka AI Chat" onClick={handleAuthClick}>
        <img src="/pp-ai.png" alt="" />
      </a>
    </div>
  )
}
