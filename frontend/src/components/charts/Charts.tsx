import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area } from 'recharts'
import { Card, CardHeader } from '../ui/Card'

const COLORS = ['#2563eb', '#059669', '#d97706', '#dc2626', '#7c3aed']

interface ChartProps {
  title?: string
  data: Record<string, unknown>[]
  dataKey: string
  xKey: string
  color?: string
  height?: number
}

export function AttendanceTrendChart({ title = 'Attendance Trend', data, height = 280 }: { title?: string; data: { month: string; rate: number }[]; height?: number }) {
  const formatted = data.map((d) => ({ ...d, rate: Math.round(d.rate * 100) }))
  return (
    <Card>
      <CardHeader title={title} />
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={formatted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#9ca3af" />
          <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" domain={[0, 100]} unit="%" />
          <Tooltip formatter={(v: number) => [`${v}%`, 'Rate']} />
          <Area type="monotone" dataKey="rate" stroke="#2563eb" fill="#dbeafe" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  )
}

export function LeaveTrendChart({ title = 'Leave Trend', data, height = 280 }: { title?: string; data: { month: string; count: number }[]; height?: number }) {
  return (
    <Card>
      <CardHeader title={title} />
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#9ca3af" />
          <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
          <Tooltip />
          <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}

export function DepartmentChart({ title = 'Department Absenteeism', data, height = 280 }: { title?: string; data: { department: string; rate: number }[]; height?: number }) {
  const formatted = data.map((d) => ({ ...d, rate: Math.round(d.rate * 100) }))
  return (
    <Card>
      <CardHeader title={title} />
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={formatted} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis type="number" unit="%" tick={{ fontSize: 12 }} stroke="#9ca3af" />
          <YAxis type="category" dataKey="department" tick={{ fontSize: 12 }} stroke="#9ca3af" width={90} />
          <Tooltip formatter={(v: number) => [`${v}%`, 'Absenteeism']} />
          <Bar dataKey="rate" fill="#d97706" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}

export function DistributionChart({ title, data, height = 260 }: { title: string; data: { name: string; value: number }[]; height?: number }) {
  return (
    <Card>
      <CardHeader title={title} />
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={4} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
            {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}

export function WorkingHoursChart({ title = 'Working Hours', data, height = 240 }: { title?: string; data: { week: string; avg_hours: number }[]; height?: number }) {
  return (
    <Card>
      <CardHeader title={title} />
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="week" tick={{ fontSize: 12 }} stroke="#9ca3af" />
          <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" domain={[0, 10]} />
          <Tooltip />
          <Line type="monotone" dataKey="avg_hours" stroke="#2563eb" strokeWidth={2} dot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  )
}

export function TeamAvailabilityChart({ title = 'Team Availability', data, height = 280 }: { title?: string; data: { date: string; availability_rate: number }[]; height?: number }) {
  const formatted = data.map((d) => ({ ...d, rate: Math.round(d.availability_rate * 100) }))
  return (
    <Card>
      <CardHeader title={title} />
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={formatted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#9ca3af" />
          <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" domain={[0, 100]} unit="%" />
          <Tooltip formatter={(v: number) => [`${v}%`, 'Available']} />
          <Bar dataKey="rate" fill="#059669" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}

export function SimpleBarChart({ title = 'Chart', data, dataKey, xKey, color = '#2563eb', height = 240 }: ChartProps) {
  return (
    <Card>
      <CardHeader title={title} />
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey={xKey} tick={{ fontSize: 12 }} stroke="#9ca3af" />
          <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
          <Tooltip />
          <Bar dataKey={dataKey} fill={color} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}
