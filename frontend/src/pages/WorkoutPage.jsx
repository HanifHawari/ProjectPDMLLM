import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import api from '../api'

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
      <main style={{ marginLeft: 220, flex: 1, padding: '32px 36px' }}>
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
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
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

function ExerciseCard({ exercise }) {
  const name = exercise.exercise_name || exercise.name || 'Gerakan'
  return (
    <div className="card" style={{ padding: 18 }}>
      <div style={{ fontSize: 14, fontWeight: 600, color: '#f5f5f5', marginBottom: 8 }}>{name}</div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        {exercise.body_part && <span className="badge-red">{exercise.body_part}</span>}
        {exercise.equipment && <span className="badge-gray">{exercise.equipment}</span>}
        {exercise.difficulty && <span className="badge-gray">{exercise.difficulty}</span>}
      </div>
      {exercise.description && (
        <div style={{ fontSize: 12, color: '#525252', marginTop: 10, lineHeight: 1.5 }}>
          {exercise.description.substring(0, 100)}{exercise.description.length > 100 ? '...' : ''}
        </div>
      )}
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
