import { Routes, Route } from 'react-router-dom'

function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-600 to-primary-900">
      <div className="text-center text-white px-6">
        <h1 className="text-5xl font-bold mb-4">DayFlow</h1>
        <p className="text-xl text-primary-100 mb-2">Intelligent HR Command Center</p>
        <p className="text-primary-200 text-sm">
          Architecture scaffold ready — UI implementation on feature/frontend-ui
        </p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
    </Routes>
  )
}
