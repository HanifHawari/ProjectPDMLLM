import { Suspense, lazy, useState } from 'react'
import Sidebar from '../components/Sidebar'
import api from '../api'

const HeroScene = lazy(() => import('../components/HeroScene'))

const zoneColors = {
  'Zone 1 (Recovery)': '#a3a3a3',
  'Zone 2 (Fat Burn)': '#22c55e',
  'Zone 3 (Cardio)': '#f59e0b',
  'Zone 4 (Anaerobic)': '#f97316',
  'Zone 5 (Max)': '#ef4444',
}

const bmiColorMap = { Normal: '#22c55e', Underweight: '#f59e0b', Overweight: '#f97316', Obese: '#ef4444' }

export default function DashboardPage({ user }) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar username={user?.username} />
      <main style={{ marginLeft: 220, flex: 1, padding: '32px 36px' }}>

        {/* Hero */}
        <section style={{
          position: 'relative', marginBottom: 40, minHeight: 220,
          overflow: 'hidden', borderRadius: 16,
          background: '#111111', border: '1px solid #2a2a2a',
        }}>
          <Suspense fallback={null}>
            <HeroScene />
          </Suspense>
          <div style={{ position: 'relative', zIndex: 2, padding: '40px 40px' }}>
            <p style={{ fontSize: 12, color: '#a3a3a3', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>
              Selamat datang kembali
            </p>
            <h1 style={{ fontSize: 36, fontWeight: 700, letterSpacing: '-0.03em', marginBottom: 10 }}>
              {user?.username || 'Athlete'}
            </h1>
            <p style={{ fontSize: 14, color: '#a3a3a3', maxWidth: 380 }}>
              Tanyakan apa saja kepada FitMind AI — dari program latihan hingga informasi nutrisi.
            </p>
          </div>
        </section>

        {/* Section label */}
        <h2 style={{ fontSize: 12, fontWeight: 600, color: '#525252', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
          Kalkulator Cepat
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>
          <BMICard />
          <CaloriesCard />
          <BPMCard />
        </div>
      </main>
    </div>
  )
}

/* ─── BMI Card ─────────────────────────────────────────── */
function BMICard() {
  const [weight, setWeight] = useState('')
  const [height, setHeight] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function calculate() {
    if (!weight || !height) return
    setLoading(true)
    try {
      const res = await api.get('/dashboard/calculate-bmi', {
        params: { weight_kg: parseFloat(weight), height_m: parseFloat(height) / 100 },
      })
      setResult(res.data.data)
    } catch (_) {}
    setLoading(false)
  }

  const color = result ? (bmiColorMap[result.category] || '#a3a3a3') : '#22c55e'

  return (
    <div className="card animate-fadeinup" style={{ padding: 24 }}>
      <SectionHeader label="Kalkulator BMI" />
      {result && (
        <div style={{ textAlign: 'center', marginBottom: 18 }}>
          <div className="metric-value" style={{ color }}>{result.bmi}</div>
          <div className="metric-label">{result.category}</div>
          <div style={{ fontSize: 12, color: '#525252', marginTop: 6 }}>
            Berat ideal: {result.ideal_weight_range.min} – {result.ideal_weight_range.max} kg
          </div>
          {result.dataset_avg_bmi && (
            <div style={{ fontSize: 12, color: '#525252', marginTop: 2 }}>
              Rata-rata dataset: {result.dataset_avg_bmi}
            </div>
          )}
        </div>
      )}
      <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
        <input className="input-field" placeholder="Berat (kg)" type="number" value={weight} onChange={e => setWeight(e.target.value)} />
        <input className="input-field" placeholder="Tinggi (cm)" type="number" value={height} onChange={e => setHeight(e.target.value)} />
      </div>
      <button className="btn-primary" style={{ width: '100%' }} onClick={calculate} disabled={loading}>
        {loading ? 'Menghitung...' : 'Hitung BMI'}
      </button>
    </div>
  )
}

/* ─── Calories Card ─────────────────────────────────────── */
function CaloriesCard() {
  const [age, setAge] = useState('')
  const [weight, setWeight] = useState('')
  const [bpm, setBpm] = useState('')
  const [duration, setDuration] = useState('')
  const [type, setType] = useState('Cardio')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function calculate() {
    if (!age || !weight || !bpm || !duration) return
    setLoading(true)
    try {
      const res = await api.get('/dashboard/estimate-calories', {
        params: {
          age: parseInt(age),
          weight_kg: parseFloat(weight),
          avg_bpm: parseInt(bpm),
          duration_hours: parseFloat(duration) / 60,
          workout_type: type,
        },
      })
      setResult(res.data.data)
    } catch (_) {}
    setLoading(false)
  }

  return (
    <div className="card animate-fadeinup" style={{ padding: 24 }}>
      <SectionHeader label="Estimasi Kalori Terbakar" />
      {result && (
        <div style={{ textAlign: 'center', marginBottom: 18 }}>
          <div className="metric-value" style={{ color: '#ef4444' }}>{result.estimated_calories}</div>
          <div className="metric-label">kkal terbakar</div>
          {result.dataset_avg_calories_burned && (
            <div style={{ fontSize: 12, color: '#525252', marginTop: 6 }}>
              Rata-rata gym member: {result.dataset_avg_calories_burned} kkal
            </div>
          )}
        </div>
      )}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 10 }}>
        <input className="input-field" placeholder="Usia" type="number" value={age} onChange={e => setAge(e.target.value)} />
        <input className="input-field" placeholder="Berat (kg)" type="number" value={weight} onChange={e => setWeight(e.target.value)} />
        <input className="input-field" placeholder="BPM rata-rata" type="number" value={bpm} onChange={e => setBpm(e.target.value)} />
        <input className="input-field" placeholder="Durasi (menit)" type="number" value={duration} onChange={e => setDuration(e.target.value)} />
      </div>
      <select className="input-field" value={type} onChange={e => setType(e.target.value)} style={{ marginBottom: 10, cursor: 'pointer' }}>
        {['HIIT', 'Cardio', 'Strength', 'Yoga'].map(t => <option key={t} value={t}>{t}</option>)}
      </select>
      <button className="btn-primary" style={{ width: '100%' }} onClick={calculate} disabled={loading}>
        {loading ? 'Menghitung...' : 'Estimasi Kalori'}
      </button>
    </div>
  )
}

/* ─── BPM Zone Card ─────────────────────────────────────── */
function BPMCard() {
  const [age, setAge] = useState('')
  const [bpm, setBpm] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function analyze() {
    if (!age || !bpm) return
    setLoading(true)
    try {
      const res = await api.get('/dashboard/bpm-analysis', {
        params: { age: parseInt(age), avg_bpm: parseInt(bpm) },
      })
      setResult(res.data.data)
    } catch (_) {}
    setLoading(false)
  }

  return (
    <div className="card animate-fadeinup" style={{ padding: 24 }}>
      <SectionHeader label="Zona Detak Jantung" />
      {result && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 2 }}>
            <div className="metric-value" style={{ color: zoneColors[result.current_zone] || '#22c55e' }}>
              {result.avg_bpm}
            </div>
            <div style={{ fontSize: 13, color: '#a3a3a3' }}>BPM</div>
          </div>
          <div style={{ fontSize: 13, color: zoneColors[result.current_zone] || '#22c55e', fontWeight: 600, marginBottom: 10 }}>
            {result.current_zone}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {result.zones && Object.entries(result.zones).map(([zone, range]) => (
              <div key={zone} style={{
                display: 'flex', justifyContent: 'space-between', fontSize: 12,
                padding: '5px 8px', borderRadius: 5,
                background: zone === result.current_zone ? 'rgba(34,197,94,0.08)' : 'transparent',
                border: `1px solid ${zone === result.current_zone ? 'rgba(34,197,94,0.2)' : 'transparent'}`,
              }}>
                <span style={{ color: zone === result.current_zone ? '#22c55e' : '#a3a3a3' }}>{zone}</span>
                <span style={{ color: '#525252' }}>{range.min_bpm}–{range.max_bpm}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
        <input className="input-field" placeholder="Usia" type="number" value={age} onChange={e => setAge(e.target.value)} />
        <input className="input-field" placeholder="BPM rata-rata" type="number" value={bpm} onChange={e => setBpm(e.target.value)} />
      </div>
      <button className="btn-primary" style={{ width: '100%' }} onClick={analyze} disabled={loading}>
        {loading ? 'Menganalisis...' : 'Analisis BPM'}
      </button>
    </div>
  )
}

function SectionHeader({ label }) {
  return (
    <>
      <div style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#a3a3a3', marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ height: 1, background: '#2a2a2a', marginBottom: 18 }} />
    </>
  )
}
