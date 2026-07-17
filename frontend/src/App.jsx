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

function ProtectedRoute({ children, user }) {
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  const [user, setUser] = useState(null)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('fitmind_user')
    if (stored) {
      try { setUser(JSON.parse(stored)) } catch (_) {}
    }
    setLoaded(true)
  }, [])

  function handleProfileSaved() {
    const stored = localStorage.getItem('fitmind_user')
    if (stored) setUser(JSON.parse(stored))
  }

  if (!loaded) return null

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
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
