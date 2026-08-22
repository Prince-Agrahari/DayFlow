import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../context/ToastContext'

export default function LoginPage() {
  const [email, setEmail] = useState('jane@dayflow.com')
  const [password, setPassword] = useState('employee123')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const { showToast } = useToast()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password)
      const user = JSON.parse(localStorage.getItem('dayflow_user') ?? '{}')
      const dest = from ?? (user.role === 'ADMIN' ? '/admin/dashboard' : '/employee/dashboard')
      navigate(dest, { replace: true })
      showToast('Welcome back!', 'success')
    } catch {
      showToast('Invalid email or password', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:w-1/2 bg-primary-600 items-center justify-center p-12">
        <div className="text-white max-w-md">
          <h1 className="text-4xl font-bold mb-4">DayFlow</h1>
          <p className="text-primary-100 text-lg">Intelligent HR Command Center</p>
          <p className="text-primary-200 mt-4 text-sm">Transform HR data into actionable intelligence. AI supports decisions — humans decide.</p>
        </div>
      </div>
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Sign in</h2>
          <p className="text-gray-500 mb-8">Enter your credentials to access DayFlow</p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
            <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" />
            <Button type="submit" className="w-full" loading={loading}>Sign in</Button>
          </form>
          <p className="mt-6 text-center text-sm text-gray-500">
            Demo: jane@dayflow.com / employee123 or admin@dayflow.com / admin123
          </p>
          <p className="mt-2 text-center text-sm text-gray-500">
            No account? <Link to="/signup" className="text-primary-600 hover:underline font-medium">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
