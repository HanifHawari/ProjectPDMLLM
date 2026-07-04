import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import api from '../api'

const allergenList = [
  { key: 'no_gluten', label: 'Gluten' },
  { key: 'no_dairy', label: 'Dairy' },
  { key: 'no_nuts', label: 'Kacang' },
  { key: 'no_soy', label: 'Kedelai' },
  { key: 'no_eggs', label: 'Telur' },
  { key: 'no_fish', label: 'Ikan' },
]

export default function NutritionPage({ user }) {
  const [tab, setTab] = useState('search')

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar username={user?.username} />
      <main className="dashboard-main">
        <div style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 4 }}>Nutrisi</h1>
          <p style={{ fontSize: 14, color: '#a3a3a3' }}>Cari makanan, cek kandungan nutrisi, dan rencanakan meal plan harian.</p>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 4, marginBottom: 28, borderBottom: '1px solid #2a2a2a', paddingBottom: 1 }}>
          {[
            { key: 'search', label: 'Cari Makanan' },
            { key: 'healthy', label: 'Makanan Sehat' },
            { key: 'meal', label: 'Meal Plan' },
          ].map(t => (
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

        {tab === 'search' && <FoodSearchTab />}
        {tab === 'healthy' && <HealthyFoodsTab />}
        {tab === 'meal' && <MealPlanTab />}
      </main>
    </div>
  )
}

/* ─── Food Search Tab ───────────────────────────────────── */
function FoodSearchTab() {
  const [query, setQuery] = useState('')
  const [allergens, setAllergens] = useState({
    no_gluten: false, no_dairy: false, no_nuts: false,
    no_soy: false, no_eggs: false, no_fish: false,
  })
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  async function search() {
    setLoading(true)
    setSearched(true)
    try {
      const res = await api.get('/nutrition/search', { params: { q: query, ...allergens, limit: 20 } })
      setResults(res.data.data || [])
    } catch (_) { setResults([]) }
    setLoading(false)
  }

  function toggleAllergen(key) {
    setAllergens(prev => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <div>
      {/* Search bar */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 14 }}>
        <input className="input-field" placeholder="Nama makanan (contoh: ayam, nasi, tofu)..." value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && search()} />
        <button className="btn-primary" onClick={search} disabled={loading} style={{ flexShrink: 0 }}>
          {loading ? 'Mencari...' : 'Cari'}
        </button>
      </div>

      {/* Allergen filters */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 24 }}>
        <span style={{ fontSize: 12, color: '#525252', alignSelf: 'center' }}>Filter alergen:</span>
        {allergenList.map(a => (
          <button key={a.key} onClick={() => toggleAllergen(a.key)}
            className={allergens[a.key] ? 'badge-red' : 'badge-gray'}
            style={{ cursor: 'pointer', background: 'none', border: allergens[a.key] ? '1px solid rgba(239,68,68,0.3)' : '1px solid rgba(163,163,163,0.2)' }}>
            Bebas {a.label}
          </button>
        ))}
      </div>

      {/* Results */}
      {loading && <LoadingSpinner />}
      {!loading && searched && results.length === 0 && (
        <div style={{ textAlign: 'center', color: '#525252', padding: 40 }}>Tidak ada hasil ditemukan.</div>
      )}
      {!loading && results.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
          {results.map((food, i) => <FoodCard key={i} food={food} />)}
        </div>
      )}
    </div>
  )
}

/* ─── Healthy Foods Tab ─────────────────────────────────── */
function HealthyFoodsTab() {
  const [foods, setFoods] = useState([])
  const [foodTypes, setFoodTypes] = useState([])
  const [selectedType, setSelectedType] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadFoodTypes(); loadFoods() }, [])

  async function loadFoodTypes() {
    try {
      const res = await api.get('/nutrition/food-types')
      setFoodTypes(res.data.data || [])
    } catch (_) {}
  }

  async function loadFoods(type = '') {
    setLoading(true)
    try {
      const res = await api.get('/nutrition/healthy', { params: { food_type: type || undefined, limit: 30 } })
      setFoods(res.data.data || [])
    } catch (_) {}
    setLoading(false)
  }

  function filterByType(type) {
    setSelectedType(type)
    loadFoods(type)
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 24 }}>
        <button className={!selectedType ? 'badge-green' : 'badge-gray'}
          onClick={() => filterByType('')} style={{ cursor: 'pointer' }}>
          Semua
        </button>
        {foodTypes.slice(0, 12).map(t => (
          <button key={t} className={selectedType === t ? 'badge-green' : 'badge-gray'}
            onClick={() => filterByType(t)} style={{ cursor: 'pointer' }}>
            {t}
          </button>
        ))}
      </div>
      {loading ? <LoadingSpinner /> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
          {foods.map((food, i) => <FoodCard key={i} food={food} />)}
        </div>
      )}
    </div>
  )
}

/* ─── Meal Plan Tab ─────────────────────────────────────── */
function MealPlanTab() {
  const [calories, setCalories] = useState('2000')
  const [dietType, setDietType] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function generate() {
    setLoading(true)
    try {
      const res = await api.get('/nutrition/meal-plan', {
        params: { target_calories: parseInt(calories), diet_type: dietType || undefined },
      })
      setResult(res.data.data)
    } catch (_) {}
    setLoading(false)
  }

  const mealColors = { Breakfast: '#22c55e', Lunch: '#f59e0b', Dinner: '#ef4444', Snack: '#a3a3a3' }

  return (
    <div>
      <div className="card" style={{ padding: 24, marginBottom: 24, maxWidth: 500 }}>
        <div style={{ fontSize: 12, color: '#a3a3a3', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 4 }}>
          Target Harian
        </div>
        <div style={{ height: 1, background: '#2a2a2a', marginBottom: 16 }} />
        <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
          <input className="input-field" type="number" placeholder="Target kalori (kkal)" value={calories}
            onChange={e => setCalories(e.target.value)} />
          <select className="input-field" value={dietType} onChange={e => setDietType(e.target.value)} style={{ cursor: 'pointer' }}>
            <option value="">Semua jenis</option>
            {['vegan', 'vegetarian', 'keto'].map(d => <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>)}
          </select>
        </div>
        <button className="btn-primary" onClick={generate} disabled={loading} style={{ width: '100%' }}>
          {loading ? 'Membuat...' : 'Buat Meal Plan'}
        </button>
      </div>

      {result && (
        <div>
          <div style={{ fontSize: 13, color: '#a3a3a3', marginBottom: 16 }}>
            Target: <span style={{ color: '#22c55e', fontWeight: 600 }}>{result.target_calories} kkal</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 14 }}>
            {Object.entries(result.breakdown).map(([meal, data]) => (
              <div key={meal} className="card" style={{ padding: 20 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: mealColors[meal] || '#f5f5f5' }}>{meal}</div>
                  <div style={{ fontSize: 12, color: '#525252' }}>{data.target_kcal} kkal</div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {(data.foods || []).map((food, j) => (
                    <div key={j} style={{ fontSize: 13, color: '#a3a3a3', padding: '6px 10px', background: '#111111', borderRadius: 6 }}>
                      {food.food_name || food.name || 'Makanan'}
                      {food.calories && <span style={{ color: '#525252', fontSize: 11, marginLeft: 6 }}>{Math.round(food.calories)} kkal/100g</span>}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

/* ─── Food Card ─────────────────────────────────────────── */
function FoodCard({ food }) {
  const name = food.food_name || food.name || 'Makanan'
  const calories = food.calories ? Math.round(food.calories) : null
  const protein = food.protein_g ? Math.round(food.protein_g * 10) / 10 : null
  const carbs = food.carbs_g ? Math.round(food.carbs_g * 10) / 10 : null
  const fat = food.fat_g ? Math.round(food.fat_g * 10) / 10 : null
  const score = food.health_score ? Math.round(food.health_score) : null

  return (
    <div className="card" style={{ padding: 18 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#f5f5f5', flex: 1 }}>{name}</div>
        {score && <span className="badge-green" style={{ marginLeft: 8, flexShrink: 0 }}>{score}</span>}
      </div>
      {food.food_type && (
        <div style={{ fontSize: 11, color: '#525252', marginBottom: 8 }}>{food.food_type}</div>
      )}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        {calories !== null && <Macro label="kkal" value={calories} color="#ef4444" />}
        {protein !== null && <Macro label="protein" value={`${protein}g`} color="#22c55e" />}
        {carbs !== null && <Macro label="karbo" value={`${carbs}g`} color="#f59e0b" />}
        {fat !== null && <Macro label="lemak" value={`${fat}g`} color="#a3a3a3" />}
      </div>
    </div>
  )
}

function Macro({ label, value, color }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: 14, fontWeight: 600, color }}>{value}</div>
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
