import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles } from 'lucide-react'
import { AdminLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { aiService } from '../../services/aiService'
import type { ChatMessage } from '../../types/api'

const SUGGESTIONS = [
  'Who needs attention today?',
  'Which employees have unusual attendance?',
  'Which department has highest absenteeism?',
  'What should I prioritize today?',
]

export default function AdminCopilot() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: '0', role: 'assistant', content: 'Hello! I\'m your DayFlow HR Copilot. I can help you identify priorities, analyze attendance patterns, and provide workforce insights based on your HR data.', timestamp: new Date().toISOString() },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (text: string) => {
    if (!text.trim() || loading) return
    setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'user', content: text, timestamp: new Date().toISOString() }])
    setInput('')
    setLoading(true)
    try {
      const res = await aiService.askCopilot(text)
      setMessages((prev) => [...prev, { id: `${Date.now()}-a`, role: 'assistant', content: res.answer, timestamp: new Date().toISOString() }])
    } catch {
      setMessages((prev) => [...prev, { id: `${Date.now()}-e`, role: 'assistant', content: 'Unable to process request. Please try again.', timestamp: new Date().toISOString() }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <AdminLayout>
      <PageHeader title="AI HR Copilot" subtitle="Intelligent workforce insights powered by your HR data" />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <Card className="lg:col-span-1 h-fit">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="h-5 w-5 text-primary-600" />
            <p className="text-sm font-medium text-gray-700">Suggested questions</p>
          </div>
          <div className="space-y-2">
            {SUGGESTIONS.map((q) => (
              <button key={q} onClick={() => send(q)} className="w-full text-left text-sm p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
                {q}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-4">AI provides recommendations — HR makes final decisions.</p>
        </Card>

        <Card className="lg:col-span-3 flex flex-col" padding={false}>
          <div className="flex-1 overflow-y-auto p-6 space-y-4 max-h-[550px] min-h-[450px]">
            {messages.map((m) => (
              <div key={m.id} className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${m.role === 'user' ? 'bg-primary-600' : 'bg-gray-200'}`}>
                  {m.role === 'user' ? <User className="h-4 w-4 text-white" /> : <Bot className="h-4 w-4 text-gray-600" />}
                </div>
                <div className={`max-w-[85%] rounded-xl px-4 py-3 text-sm ${m.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                  <p className="whitespace-pre-wrap">{m.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-3">
                <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center"><Bot className="h-4 w-4" /></div>
                <div className="bg-gray-100 rounded-xl px-4 py-3"><div className="flex gap-1"><span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" /><span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.1s]" /><span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" /></div></div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <div className="border-t border-gray-200 p-4 flex gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send(input)}
              placeholder="Ask about workforce priorities, anomalies, absenteeism..."
              className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
            <Button onClick={() => send(input)} disabled={loading || !input.trim()}><Send className="h-4 w-4" /></Button>
          </div>
        </Card>
      </div>
    </AdminLayout>
  )
}
