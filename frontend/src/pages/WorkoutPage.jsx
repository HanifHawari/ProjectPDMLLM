import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import api from '../api'

// SVG ilustrasi orang melakukan gerakan per body part
const ExerciseSVG = {
  Chest: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
      {/* Kepala */}
      <circle cx="60" cy="14" r="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Badan */}
      <line x1="60" y1="22" x2="60" y2="55" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Push up: tangan di lantai */}
      <line x1="60" y1="35" x2="30" y2="55" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="35" x2="90" y2="55" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Kaki lurus */}
      <line x1="60" y1="55" x2="45" y2="80" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="55" x2="75" y2="80" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Lantai */}
      <line x1="15" y1="82" x2="105" y2="82" stroke="#2a2a2a" strokeWidth="1" strokeDasharray="4 3" opacity="0.6"/>
      {/* Label */}
      <text x="60" y="97" textAnchor="middle" fontSize="8" fill="#525252" fontFamily="Inter, sans-serif">Push Position</text>
    </svg>
  ),
  Back: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
      <circle cx="60" cy="14" r="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Badan condong */}
      <line x1="60" y1="22" x2="55" y2="55" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Tangan menarik barbel */}
      <line x1="57" y1="35" x2="30" y2="28" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="57" y1="35" x2="85" y2="28" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Barbel */}
      <line x1="22" y1="28" x2="93" y2="28" stroke="#a3a3a3" strokeWidth="2.5" opacity="0.4"/>
      <circle cx="22" cy="28" r="5" stroke="#a3a3a3" strokeWidth="1.5" opacity="0.4"/>
      <circle cx="93" cy="28" r="5" stroke="#a3a3a3" strokeWidth="1.5" opacity="0.4"/>
      {/* Kaki */}
      <line x1="55" y1="55" x2="45" y2="80" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="55" y1="55" x2="68" y2="80" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="15" y1="82" x2="105" y2="82" stroke="#2a2a2a" strokeWidth="1" strokeDasharray="4 3" opacity="0.6"/>
      <text x="60" y="97" textAnchor="middle" fontSize="8" fill="#525252" fontFamily="Inter, sans-serif">Row Position</text>
    </svg>
  ),
  Legs: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
      <circle cx="60" cy="12" r="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="20" x2="60" y2="48" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Tangan terentang */}
      <line x1="60" y1="30" x2="35" y2="36" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="30" x2="85" y2="36" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Posisi squat: lutut ditekuk */}
      <line x1="60" y1="48" x2="42" y2="68" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="48" x2="78" y2="68" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="42" y1="68" x2="38" y2="82" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="78" y1="68" x2="82" y2="82" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="15" y1="82" x2="105" y2="82" stroke="#2a2a2a" strokeWidth="1" strokeDasharray="4 3" opacity="0.6"/>
      <text x="60" y="97" textAnchor="middle" fontSize="8" fill="#525252" fontFamily="Inter, sans-serif">Squat Position</text>
    </svg>
  ),
  Arms: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
      <circle cx="60" cy="14" r="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="22" x2="60" y2="58" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Curl: siku ditekuk */}
      <line x1="60" y1="32" x2="32" y2="40" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="32" y1="40" x2="28" y2="24" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="32" x2="88" y2="40" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="88" y1="40" x2="92" y2="24" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Dumbbell */}
      <circle cx="28" cy="22" r="4" stroke="#a3a3a3" strokeWidth="1.5" opacity="0.4"/>
      <circle cx="92" cy="22" r="4" stroke="#a3a3a3" strokeWidth="1.5" opacity="0.4"/>
      {/* Kaki */}
      <line x1="60" y1="58" x2="50" y2="82" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="58" x2="70" y2="82" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="15" y1="82" x2="105" y2="82" stroke="#2a2a2a" strokeWidth="1" strokeDasharray="4 3" opacity="0.6"/>
      <text x="60" y="97" textAnchor="middle" fontSize="8" fill="#525252" fontFamily="Inter, sans-serif">Curl Position</text>
    </svg>
  ),
  Shoulders: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
      <circle cx="60" cy="14" r="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="22" x2="60" y2="58" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Shoulder press: tangan angkat ke atas */}
      <line x1="60" y1="28" x2="30" y2="22" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="30" y1="22" x2="22" y2="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="28" x2="90" y2="22" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="90" y1="22" x2="98" y2="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Barbel atas */}
      <line x1="15" y1="6" x2="105" y2="6" stroke="#a3a3a3" strokeWidth="2" opacity="0.35"/>
      <circle cx="15" cy="6" r="4" stroke="#a3a3a3" strokeWidth="1.5" opacity="0.35"/>
      <circle cx="105" cy="6" r="4" stroke="#a3a3a3" strokeWidth="1.5" opacity="0.35"/>
      {/* Kaki */}
      <line x1="60" y1="58" x2="50" y2="82" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="58" x2="70" y2="82" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="15" y1="82" x2="105" y2="82" stroke="#2a2a2a" strokeWidth="1" strokeDasharray="4 3" opacity="0.6"/>
      <text x="60" y="97" textAnchor="middle" fontSize="8" fill="#525252" fontFamily="Inter, sans-serif">Press Position</text>
    </svg>
  ),
  Abs: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
      <circle cx="60" cy="20" r="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Crunch: badan ditekuk */}
      <path d="M 60 28 Q 55 45 50 55" stroke="#22c55e" strokeWidth="1.5" opacity="0.5" fill="none"/>
      {/* Tangan di belakang kepala */}
      <line x1="60" y1="32" x2="40" y2="24" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="32" x2="80" y2="24" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Kaki ditekuk */}
      <line x1="50" y1="55" x2="35" y2="72" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="35" y1="72" x2="50" y2="80" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="50" y1="55" x2="70" y2="68" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="70" y1="68" x2="82" y2="78" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="15" y1="82" x2="105" y2="82" stroke="#2a2a2a" strokeWidth="1" strokeDasharray="4 3" opacity="0.6"/>
      <text x="60" y="97" textAnchor="middle" fontSize="8" fill="#525252" fontFamily="Inter, sans-serif">Crunch Position</text>
    </svg>
  ),
  Bicep: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
      <circle cx="60" cy="14" r="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="22" x2="60" y2="58" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Satu tangan curl */}
      <line x1="60" y1="30" x2="88" y2="38" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="88" y1="38" x2="84" y2="20" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Tangan lain lurus */}
      <line x1="60" y1="30" x2="35" y2="42" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <circle cx="84" cy="18" r="5" stroke="#a3a3a3" strokeWidth="1.5" opacity="0.4"/>
      {/* Kaki */}
      <line x1="60" y1="58" x2="50" y2="82" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="58" x2="70" y2="82" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="15" y1="82" x2="105" y2="82" stroke="#2a2a2a" strokeWidth="1" strokeDasharray="4 3" opacity="0.6"/>
      <text x="60" y="97" textAnchor="middle" fontSize="8" fill="#525252" fontFamily="Inter, sans-serif">Bicep Curl</text>
    </svg>
  ),
  Tricep: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
      <circle cx="60" cy="14" r="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="22" x2="60" y2="58" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Tricep: tangan di atas kepala ditekuk */}
      <line x1="60" y1="25" x2="74" y2="16" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="74" y1="16" x2="70" y2="5" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="25" x2="46" y2="36" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <circle cx="70" cy="4" r="4" stroke="#a3a3a3" strokeWidth="1.5" opacity="0.4"/>
      {/* Kaki */}
      <line x1="60" y1="58" x2="50" y2="82" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="58" x2="70" y2="82" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="15" y1="82" x2="105" y2="82" stroke="#2a2a2a" strokeWidth="1" strokeDasharray="4 3" opacity="0.6"/>
      <text x="60" y="97" textAnchor="middle" fontSize="8" fill="#525252" fontFamily="Inter, sans-serif">Tricep Extension</text>
    </svg>
  ),
  Core: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
      <circle cx="60" cy="14" r="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Plank position */}
      <line x1="60" y1="22" x2="58" y2="52" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="58" y1="32" x2="28" y2="46" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="58" y1="32" x2="88" y2="46" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      {/* Kaki lurus ke belakang */}
      <line x1="58" y1="52" x2="42" y2="68" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="58" y1="52" x2="76" y2="68" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="15" y1="70" x2="105" y2="70" stroke="#2a2a2a" strokeWidth="1" strokeDasharray="4 3" opacity="0.6"/>
      <text x="60" y="85" textAnchor="middle" fontSize="8" fill="#525252" fontFamily="Inter, sans-serif">Plank Position</text>
    </svg>
  ),
  default: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
      <circle cx="60" cy="14" r="8" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="22" x2="60" y2="55" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="32" x2="38" y2="44" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="32" x2="82" y2="44" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="55" x2="48" y2="78" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="60" y1="55" x2="72" y2="78" stroke="#22c55e" strokeWidth="1.5" opacity="0.5"/>
      <line x1="15" y1="80" x2="105" y2="80" stroke="#2a2a2a" strokeWidth="1" strokeDasharray="4 3" opacity="0.6"/>
      <text x="60" y="97" textAnchor="middle" fontSize="8" fill="#525252" fontFamily="Inter, sans-serif">Exercise Position</text>
    </svg>
  ),
}

function getExerciseSVG(bodyPart) {
  if (!bodyPart) return ExerciseSVG.default
  const key = Object.keys(ExerciseSVG).find(
    k => k.toLowerCase() === bodyPart.toLowerCase()
  )
  return key ? ExerciseSVG[key] : ExerciseSVG.default
}

export default function WorkoutPage({ user }) {
  const [query, setQuery] = useState('')
  const [bodyPart, setBodyPart] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [tab, setTab] = useState('exercises')

  async function search() {
    setLoading(true)
    setSearched(true)
    try {
      const res = await api.get('/workout/search', {
        params: { q: query || undefined, body_part: bodyPart || undefined, limit: 24 },
      })
      setResults(res.data.data || [])
    } catch (_) { setResults([]) }
    setLoading(false)
  }

  const bodyParts = ['Chest', 'Back', 'Legs', 'Arms', 'Shoulders', 'Abs', 'Bicep', 'Tricep', 'Core']

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar username={user?.username} />
      <main className="dashboard-main">
        <div style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 4 }}>Workout</h1>
          <p style={{ fontSize: 14, color: '#a3a3a3' }}>Temukan latihan berdasarkan kelompok otot atau tipe gerakan.</p>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 4, marginBottom: 28, borderBottom: '1px solid #2a2a2a', paddingBottom: 1 }}>
          {[{ key: 'exercises', label: 'Latihan' }, { key: 'programs', label: 'Program' }].map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              style={{
                padding: '9px 18px', background: 'none', border: 'none', cursor: 'pointer',
                fontSize: 14, fontWeight: 500, fontFamily: 'Inter, sans-serif',
                color: tab === t.key ? '#22c55e' : '#a3a3a3',
                borderBottom: tab === t.key ? '2px solid #22c55e' : '2px solid transparent',
                marginBottom: -1, transition: 'all 0.2s',
              }}>
              {t.label}
            </button>
          ))}
        </div>

        {tab === 'exercises' && (
          <div>
            {/* Search */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 14 }}>
              <input className="input-field" placeholder="Cari gerakan (contoh: push up, squat)..." value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && search()} />
              <button className="btn-primary" onClick={search} disabled={loading} style={{ flexShrink: 0 }}>
                {loading ? 'Mencari...' : 'Cari'}
              </button>
            </div>

            {/* Body part filter */}
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 24 }}>
              <button className={!bodyPart ? 'badge-green' : 'badge-gray'} onClick={() => { setBodyPart(''); }}
                style={{ cursor: 'pointer' }}>
                Semua
              </button>
              {bodyParts.map(bp => (
                <button key={bp} className={bodyPart === bp ? 'badge-red' : 'badge-gray'}
                  onClick={() => { setBodyPart(bp); }}
                  style={{ cursor: 'pointer' }}>
                  {bp}
                </button>
              ))}
            </div>

            {loading && <LoadingSpinner />}
            {!loading && searched && results.length === 0 && (
              <div style={{ textAlign: 'center', color: '#525252', padding: 40 }}>Tidak ada latihan ditemukan.</div>
            )}
            {!loading && results.length > 0 && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 14 }}>
                {results.map((ex, i) => <ExerciseCard key={i} exercise={ex} />)}
              </div>
            )}
            {!searched && (
              <div style={{ textAlign: 'center', color: '#525252', padding: 60 }}>
                Masukkan kata kunci atau pilih kelompok otot untuk mulai mencari.
              </div>
            )}
          </div>
        )}

        {tab === 'programs' && <ProgramsTab />}
      </main>
    </div>
  )
}

/* ─── Programs Tab ──────────────────────────────────────── */
function ProgramsTab() {
  const [programs, setPrograms] = useState([])
  const [loading, setLoading] = useState(true)
  const [level, setLevel] = useState('')

  useEffect(() => { loadPrograms() }, [])

  async function loadPrograms(lvl = '') {
    setLoading(true)
    try {
      const res = await api.get('/programs', { params: { level: lvl || undefined, limit: 20 } })
      setPrograms(res.data.data || [])
    } catch (_) {}
    setLoading(false)
  }

  function filterByLevel(lvl) {
    setLevel(lvl)
    loadPrograms(lvl)
  }

  const levelColors = { Beginner: '#22c55e', Intermediate: '#f59e0b', Advanced: '#ef4444' }

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
        <button className={!level ? 'badge-green' : 'badge-gray'} onClick={() => filterByLevel('')} style={{ cursor: 'pointer' }}>Semua Level</button>
        {['Beginner', 'Intermediate', 'Advanced'].map(l => (
          <button key={l} className={level === l ? 'badge-red' : 'badge-gray'} onClick={() => filterByLevel(l)} style={{ cursor: 'pointer' }}>{l}</button>
        ))}
      </div>

      {loading ? <LoadingSpinner /> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 14 }}>
          {programs.map((prog, i) => (
            <div key={i} className="card" style={{ padding: 22 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <div style={{ fontSize: 15, fontWeight: 600, color: '#f5f5f5', flex: 1 }}>{prog.title}</div>
                {prog.level && (
                  <span className="badge-gray" style={{
                    marginLeft: 8, flexShrink: 0,
                    color: levelColors[prog.level] || '#a3a3a3',
                    borderColor: 'transparent', background: `rgba(${prog.level === 'Beginner' ? '34,197,94' : prog.level === 'Advanced' ? '239,68,68' : '245,158,11'},0.1)`,
                  }}>
                    {prog.level}
                  </span>
                )}
              </div>
              {prog.goal && <div style={{ fontSize: 13, color: '#a3a3a3', marginBottom: 10 }}>{prog.goal}</div>}
              {prog.description && (
                <div style={{ fontSize: 12, color: '#525252', marginBottom: 12, lineHeight: 1.5 }}>
                  {prog.description.substring(0, 120)}{prog.description.length > 120 ? '...' : ''}
                </div>
              )}
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                {prog.program_length && <Stat label="Durasi" value={prog.program_length} />}
                {prog.time_per_workout && <Stat label="Per Sesi" value={prog.time_per_workout} />}
                {prog.total_exercises && <Stat label="Gerakan" value={prog.total_exercises} />}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/* ─── Exercise Card dengan Gambar Placeholder ──────────── */
function ExerciseCard({ exercise }) {
  const name = exercise.exercise_name || exercise.name || exercise.Workout || 'Gerakan'
  const bodyPart = exercise.body_part || exercise['Body Part'] || ''

  // Membuat format nama file yang aman (huruf kecil, ganti spasi/karakter khusus dengan strip)
  const imageFileName = name.toLowerCase().replace(/[^a-z0-9]+/g, '-') + '.webp'
  const imageUrl = `/workouts/${imageFileName}`
  
  // State untuk melacak jika gambar gagal dimuat (belum ada gambarnya)
  const [imgError, setImgError] = useState(false)

  return (
    <div className="card exercise-card" style={{ overflow: 'hidden' }}>
      {/* Area Gambar / Ilustrasi */}
      <div style={{
        width: '100%',
        height: 130,
        background: 'linear-gradient(135deg, #0f1f15 0%, #111111 50%, #0a1a10 100%)',
        borderBottom: '1px solid #2a2a2a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '12px 20px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Glow efek di belakang */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse at center, rgba(34,197,94,0.04) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        
        {/* Area Gambar 3D atau SVG (Fallback) */}
        <div style={{ width: 110, height: 110, position: 'relative', zIndex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          {!imgError ? (
            <img 
              src={imageUrl} 
              alt={name}
              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
              onError={() => setImgError(true)}
            />
          ) : (
            <div style={{ width: 90, height: 90 }}>
              {getExerciseSVG(bodyPart)}
            </div>
          )}
        </div>
      </div>

      {/* Info */}
      <div style={{ padding: '14px 16px' }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#f5f5f5', marginBottom: 8, lineHeight: 1.3 }}>{name}</div>

        {exercise.description && (
          <div style={{ fontSize: 12, color: '#525252', lineHeight: 1.5 }}>
            {exercise.description.substring(0, 90)}{exercise.description.length > 90 ? '...' : ''}
          </div>
        )}
      </div>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div>
      <div style={{ fontSize: 13, fontWeight: 600, color: '#f5f5f5' }}>{value}</div>
      <div style={{ fontSize: 10, color: '#525252', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</div>
    </div>
  )
}

function LoadingSpinner() {
  return (
    <div style={{ textAlign: 'center', padding: 60 }}>
      <div style={{ width: 24, height: 24, border: '2px solid #2a2a2a', borderTop: '2px solid #22c55e', borderRadius: '50%', animation: 'spin 0.7s linear infinite', margin: '0 auto' }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
