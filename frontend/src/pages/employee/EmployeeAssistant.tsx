import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User } from 'lucide-react'
import { EmployeeLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { aiService } from '../../services/aiService'
import type { ChatMessage } from '../../types/api'

const SUGGESTIONS = [
  'How many leaves do I have?',
  'Show my attendance.',
  'What is my leave status?',
  'What is my salary?',
]

export default function EmployeeAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: '0', role: 'assistant', content: 'Hello! I\'m your DayFlow assistant. I can help with your leaves, attendance, salary, and leave status.', timestamp: new Date().toISOString() },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (text: string) => {
    if (!text.trim() || loading) return
    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', content: text, timestamp: new Date().toISOString() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)
    try {
      const res = await aiService.askAssistant(text)
      setMessages((prev) => [...prev, { id: `${Date.now()}-a`, role: 'assistant', content: res.answer, timestamp: new Date().toISOString() }])
    } catch {
      setMessages((prev) => [...prev, { id: `${Date.now()}-e`, role: 'assistant', content: 'Sorry, I couldn\'t process that request. Please try again.', timestamp: new Date().toISOString() }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <EmployeeLayout>
      <PageHeader title="AI Assistant" subtitle="Get answers about your leaves, attendance, and salary" />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <Card className="lg:col-span-1 h-fit">
          <p className="text-sm font-medium text-gray-700 mb-3">Suggested questions</p>
          <div className="space-y-2">
            {SUGGESTIONS.map((q) => (
              <button key={q} onClick={() => send(q)} className="w-full text-left text-sm p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
                {q}
              </button>
            ))}
          </div>
        </Card>

        <Card className="lg:col-span-3 flex flex-col" padding={false}>
          <div className="flex-1 overflow-y-auto p-6 space-y-4 max-h-[500px] min-h-[400px]">
            {messages.map((m) => (
              <div key={m.id} className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${m.role === 'user' ? 'bg-primary-600' : 'bg-gray-200'}`}>
                  {m.role === 'user' ? <User className="h-4 w-4 text-white" /> : <Bot className="h-4 w-4 text-gray-600" />}
                </div>
                <div className={`max-w-[80%] rounded-xl px-4 py-3 text-sm ${m.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                  <p className="whitespace-pre-wrap">{m.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-3">
                <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center"><Bot className="h-4 w-4 text-gray-600" /></div>
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
              placeholder="Ask about your leaves, attendance, salary..."
              className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
            <Button onClick={() => send(input)} disabled={loading || !input.trim()}><Send className="h-4 w-4" /></Button>
          </div>
        </Card>
      </div>
    </EmployeeLayout>
  )
}
