import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input, Select } from '../../components/ui/Input'
import { authService } from '../../services/authService'
import { useToast } from '../../context/ToastContext'

export default function SignupPage() {
  const [form, setForm] = useState({ full_name: '', email: '', password: '', role: 'EMPLOYEE' as 'EMPLOYEE' | 'ADMIN' })
  const [loading, setLoading] = useState(false)
  const { showToast } = useToast()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await authService.signup(form)
      showToast('Account created! Please sign in.', 'success')
      navigate('/login')
    } catch {
      showToast('Signup failed. Please try again.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-xl border border-gray-200 shadow-sm p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Create account</h2>
        <p className="text-gray-500 mb-8">Join DayFlow HR platform</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
          <Input label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <Input label="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={6} />
          <Select label="Role" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value as 'EMPLOYEE' | 'ADMIN' })}>
            <option value="EMPLOYEE">Employee</option>
            <option value="ADMIN">Admin / HR</option>
          </Select>
          <Button type="submit" className="w-full" loading={loading}>Create account</Button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-500">
          Already have an account? <Link to="/login" className="text-primary-600 hover:underline font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
