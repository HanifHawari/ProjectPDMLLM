import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ChatPage from './pages/ChatPage'
import NutritionPage from './pages/NutritionPage'
import WorkoutPage from './pages/WorkoutPage'
import ProfilePage from './pages/ProfilePage'
import PlanGeneratorPage from './pages/PlanGeneratorPage'
import api from './api'

// Komponen Wrapper untuk membatasi akses halaman hanya untuk user yang sudah login/terdaftar
function ProtectedRoute({ children, user }) {
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  const [user, setUser] = useState(null)
  const [loaded, setLoaded] = useState(false) // Flag untuk memastikan pengecekan localStorage selesai sebelum merender halaman

  // Mengambil data pengguna dari localStorage saat aplikasi pertama kali dimuat
  useEffect(() => {
    const stored = localStorage.getItem('fitmind_user')
    const token = localStorage.getItem('fitmind_token')
    if (!stored || !token) {
      localStorage.removeItem('fitmind_user')
      setLoaded(true)
      return
    }
    api.get('/users/me')
      .then(({ data }) => setUser(data))
      .catch(() => {
        localStorage.removeItem('fitmind_token')
        localStorage.removeItem('fitmind_user')
        localStorage.removeItem('fitmind_profile')
      })
      .finally(() => setLoaded(true))
  }, [])

  // Callback untuk sinkronisasi state user ketika ada perubahan profil (misal: berat badan, tinggi badan)
  async function handleProfileSaved() {
    try {
      const { data } = await api.get('/users/me')
      setUser(data)
    } catch {
      // The profile page keeps its own saved state if the refresh fails.
    }
  }

  if (!loaded) return null // Menghindari flash halaman login jika user sebenarnya sudah terautentikasi

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        {/* Jika user sudah login, redirect otomatis dari login/register ke dashboard */}
        <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
        <Route path="/register" element={user ? <Navigate to="/dashboard" replace /> : <RegisterPage />} />
        <Route path="/dashboard" element={
          <ProtectedRoute user={user}>
            <DashboardPage user={user} />
          </ProtectedRoute>
        } />
        <Route path="/chat" element={
          <ProtectedRoute user={user}>
            <ChatPage user={user} />
          </ProtectedRoute>
        } />
        <Route path="/nutrition" element={
          <ProtectedRoute user={user}>
            <NutritionPage user={user} />
          </ProtectedRoute>
        } />
        <Route path="/workout" element={
          <ProtectedRoute user={user}>
            <WorkoutPage user={user} />
          </ProtectedRoute>
        } />
        <Route path="/plan" element={
          <ProtectedRoute user={user}>
            <PlanGeneratorPage user={user} />
          </ProtectedRoute>
        } />
        <Route path="/profile" element={
          <ProtectedRoute user={user}>
            <ProfilePage user={user} onProfileSaved={handleProfileSaved} />
          </ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
