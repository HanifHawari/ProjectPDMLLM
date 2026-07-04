import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import api from '../api'

const goals = ['Weight Loss', 'Muscle Gain', 'Endurance', 'Maintenance', 'Flexibility']
const levels = ['Beginner', 'Intermediate', 'Advanced']
const workoutTypes = ['Strength', 'Cardio', 'HIIT', 'Yoga', 'Mixed']
const equipments = ['None', 'Dumbbells', 'Barbell', 'Machine', 'Full Gym']
const dietTypes = ['', 'vegan', 'vegetarian', 'keto', 'paleo', 'halal']

export default function ProfilePage({ user, onProfileSaved }) {
  const [form, setForm] = useState({
    age: '', gender: 'Male', weight_kg: '', height_m: '',
    goal: 'Weight Loss', experience_level: 'Beginner',
    workout_frequency: '', session_duration: '',
    workout_type: 'Strength', equipment: 'None', diet_type: '',
    no_gluten: false, no_dairy: false, no_nuts: false,
    no_soy: false, no_eggs: false, no_fish: false,
  })
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)
  const [saved, setSaved] = useState(false)
  const [bmi, setBmi] = useState(null)
  const navigate = useNavigate()
  const username = user?.username

  useEffect(() => {
    if (username) loadProfile()
  }, [username])

  async function loadProfile() {
    setFetching(true)
    try {
      const res = await api.get(`/users/${username}/profile`)
      const data = res.data.data
      if (data) {
        setForm({
          age: data.age || '',
          gender: data.gender || 'Male',
          weight_kg: data.weight_kg || '',
          height_m: data.height_m ? Math.round(data.height_m * 100) : '',
          goal: data.goal || 'Weight Loss',
          experience_level: data.experience_level || 'Beginner',
          workout_frequency: data.workout_frequency || '',
          session_duration: data.session_duration || '',
          workout_type: data.workout_type || 'Strength',
          equipment: data.equipment || 'None',
          diet_type: data.diet_type || '',
          no_gluten: data.allergens?.no_gluten || false,
          no_dairy: data.allergens?.no_dairy || false,
          no_nuts: data.allergens?.no_nuts || false,
          no_soy: data.allergens?.no_soy || false,
          no_eggs: data.allergens?.no_eggs || false,
          no_fish: data.allergens?.no_fish || false,
        })
        if (data.bmi) setBmi(data.bmi)
      }
    } catch (_) {}
    setFetching(false)
  }

  async function saveProfile() {
    setLoading(true)
    setSaved(false)
    try {
      const payload = {
        ...form,
        age: form.age ? parseInt(form.age) : null,
        weight_kg: form.weight_kg ? parseFloat(form.weight_kg) : null,
        height_m: form.height_m ? parseFloat(form.height_m) / 100 : null,
        workout_frequency: form.workout_frequency ? parseInt(form.workout_frequency) : null,
        session_duration: form.session_duration ? parseInt(form.session_duration) : null,
      }
      const res = await api.put(`/users/${username}/profile`, payload)
      if (res.data.data?.bmi) setBmi(res.data.data.bmi)

      // Save profile to localStorage for AI context
      localStorage.setItem('fitmind_profile', JSON.stringify(payload))

      const storedUser = JSON.parse(localStorage.getItem('fitmind_user') || '{}')
      localStorage.setItem('fitmind_user', JSON.stringify({ ...storedUser, has_profile: true }))
      if (onProfileSaved) onProfileSaved()

      setSaved(true)
      setTimeout(() => navigate('/'), 1200)
    } catch (_) {}
    setLoading(false)
  }

  function set(key, value) {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  if (fetching) {
    return (
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        <Sidebar username={username} />
        <main className="dashboard-main" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ color: '#525252' }}>Memuat profil...</div>
        </main>
      </div>
    )
  }

  const allergenList = [
    { key: 'no_gluten', label: 'Gluten' },
    { key: 'no_dairy', label: 'Dairy' },
    { key: 'no_nuts', label: 'Kacang' },
    { key: 'no_soy', label: 'Kedelai' },
    { key: 'no_eggs', label: 'Telur' },
    { key: 'no_fish', label: 'Ikan' },
  ]

  const bmiColor = bmi
    ? bmi < 18.5 ? '#f59e0b' : bmi < 25 ? '#22c55e' : bmi < 30 ? '#f97316' : '#ef4444'
    : '#a3a3a3'
  const bmiCategory = bmi
    ? bmi < 18.5 ? 'Underweight' : bmi < 25 ? 'Normal' : bmi < 30 ? 'Overweight' : 'Obese'
    : null

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar username={username} />
      <main className="dashboard-main" style={{ maxWidth: 800 }}>
        <div style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 4 }}>Profil Kebugaran</h1>
          <p style={{ fontSize: 14, color: '#a3a3a3' }}>Data ini digunakan oleh AI untuk memberikan rekomendasi yang lebih personal.</p>
        </div>

        {/* BMI indicator */}
        {bmi && (
          <div className="card" style={{ padding: 20, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 20 }}>
            <div>
              <div style={{ fontSize: 32, fontWeight: 700, color: bmiColor, lineHeight: 1 }}>{bmi}</div>
              <div style={{ fontSize: 11, color: '#525252', textTransform: 'uppercase', letterSpacing: '0.06em' }}>BMI</div>
            </div>
            <div style={{ height: 40, width: 1, background: '#2a2a2a' }} />
            <div>
              <div style={{ fontSize: 16, fontWeight: 600, color: bmiColor }}>{bmiCategory}</div>
              <div style={{ fontSize: 13, color: '#525252' }}>Dihitung otomatis dari berat dan tinggi</div>
            </div>
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Personal Info */}
          <Section title="Informasi Dasar">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
              <Field label="Usia">
                <input className="input-field" type="number" placeholder="Tahun" value={form.age} onChange={e => set('age', e.target.value)} />
              </Field>
              <Field label="Berat (kg)">
                <input className="input-field" type="number" placeholder="kg" value={form.weight_kg} onChange={e => set('weight_kg', e.target.value)} />
              </Field>
              <Field label="Tinggi (cm)">
                <input className="input-field" type="number" placeholder="cm" value={form.height_m} onChange={e => set('height_m', e.target.value)} />
              </Field>
            </div>
            <Field label="Jenis Kelamin">
              <div style={{ display: 'flex', gap: 8 }}>
                {['Male', 'Female'].map(g => (
                  <button key={g} onClick={() => set('gender', g)}
                    className={form.gender === g ? 'badge-green' : 'badge-gray'}
                    style={{ cursor: 'pointer', padding: '7px 18px', borderRadius: 8 }}>
                    {g === 'Male' ? 'Pria' : 'Wanita'}
                  </button>
                ))}
              </div>
            </Field>
          </Section>

          {/* Fitness Goals */}
          <Section title="Tujuan dan Level">
            <Field label="Tujuan Utama">
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {goals.map(g => (
                  <button key={g} onClick={() => set('goal', g)}
                    className={form.goal === g ? 'badge-green' : 'badge-gray'}
                    style={{ cursor: 'pointer', padding: '7px 14px', borderRadius: 8 }}>
                    {g}
                  </button>
                ))}
              </div>
            </Field>
            <Field label="Level Pengalaman">
              <div style={{ display: 'flex', gap: 8 }}>
                {levels.map(l => (
                  <button key={l} onClick={() => set('experience_level', l)}
                    className={form.experience_level === l ? 'badge-green' : 'badge-gray'}
                    style={{ cursor: 'pointer', padding: '7px 16px', borderRadius: 8 }}>
                    {l}
                  </button>
                ))}
              </div>
            </Field>
          </Section>

          {/* Training */}
          <Section title="Preferensi Latihan">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <Field label="Frekuensi per Minggu">
                <input className="input-field" type="number" placeholder="Hari/minggu" value={form.workout_frequency} onChange={e => set('workout_frequency', e.target.value)} />
              </Field>
              <Field label="Durasi per Sesi (menit)">
                <input className="input-field" type="number" placeholder="Menit" value={form.session_duration} onChange={e => set('session_duration', e.target.value)} />
              </Field>
            </div>
            <Field label="Tipe Latihan">
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {workoutTypes.map(t => (
                  <button key={t} onClick={() => set('workout_type', t)}
                    className={form.workout_type === t ? 'badge-green' : 'badge-gray'}
                    style={{ cursor: 'pointer', padding: '7px 14px', borderRadius: 8 }}>
                    {t}
                  </button>
                ))}
              </div>
            </Field>
            <Field label="Peralatan">
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {equipments.map(e => (
                  <button key={e} onClick={() => set('equipment', e)}
                    className={form.equipment === e ? 'badge-green' : 'badge-gray'}
                    style={{ cursor: 'pointer', padding: '7px 14px', borderRadius: 8 }}>
                    {e}
                  </button>
                ))}
              </div>
            </Field>
          </Section>

          {/* Diet */}
          <Section title="Diet dan Alergen">
            <Field label="Tipe Diet">
              <select className="input-field" value={form.diet_type} onChange={e => set('diet_type', e.target.value)} style={{ cursor: 'pointer' }}>
                <option value="">Tidak ada preferensi khusus</option>
                {['vegan', 'vegetarian', 'keto', 'paleo', 'halal'].map(d => (
                  <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
                ))}
              </select>
            </Field>
            <Field label="Alergi / Pantangan Makanan">
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {allergenList.map(a => (
                  <button key={a.key} onClick={() => set(a.key, !form[a.key])}
                    className={form[a.key] ? 'badge-red' : 'badge-gray'}
                    style={{ cursor: 'pointer', padding: '7px 14px', borderRadius: 8 }}>
                    {form[a.key] ? 'Bebas ' : ''}{a.label}
                  </button>
                ))}
              </div>
            </Field>
          </Section>

          {/* Save button */}
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <button className="btn-primary" onClick={saveProfile} disabled={loading} style={{ padding: '12px 32px' }}>
              {loading ? 'Menyimpan...' : 'Simpan Profil'}
            </button>
            {saved && <span style={{ fontSize: 14, color: '#22c55e' }}>Profil berhasil disimpan.</span>}
          </div>
        </div>
      </main>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div className="card" style={{ padding: 24 }}>
      <div style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#a3a3a3', marginBottom: 4 }}>{title}</div>
      <div style={{ height: 1, background: '#2a2a2a', marginBottom: 18 }} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {children}
      </div>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <div>
      <label style={{ fontSize: 12, color: '#525252', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: 8 }}>
        {label}
      </label>
      {children}
    </div>
  )
}
