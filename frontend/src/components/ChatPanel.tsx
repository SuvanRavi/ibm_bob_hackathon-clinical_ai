import { useMemo, useState } from 'react'
import type { ChatMessage, QuickStartIntent } from '../types/chat'
import { mockOrchestrateService } from '../services/mockOrchestrateService'
import { patientProfile } from '../data/patient'
import { ChatInput } from './ChatInput'
import { ChatMessage as ChatBubble } from './ChatMessage'
import { EmergencyModal } from './EmergencyModal'
import { QuickStartPills } from './QuickStartPills'

const redFlagTerms = ['chest pain', 'bleeding', 'unconscious']

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'intro',
      role: 'assistant',
      content:
        'Welcome back. I am here to help summarize your visit and answer questions about medications, symptoms, or logistics.',
      createdAt: new Date().toISOString(),
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [activeIntent, setActiveIntent] = useState<QuickStartIntent>()
  const [isSending, setIsSending] = useState(false)
  const [showEmergency, setShowEmergency] = useState(false)
  const [escalationStatus, setEscalationStatus] = useState<string | null>(null)

  const isRedFlag = useMemo(() => {
    const content = inputValue.toLowerCase()
    return redFlagTerms.some((term) => content.includes(term))
  }, [inputValue])

  const handleChange = (value: string) => {
    setInputValue(value)
    if (value && redFlagTerms.some((term) => value.toLowerCase().includes(term))) {
      setShowEmergency(true)
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim() || isSending) {
      return
    }

    const userMessage: ChatMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      content: inputValue.trim(),
      intentTag: activeIntent,
      createdAt: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setIsSending(true)

    const response = await mockOrchestrateService({
      message: userMessage.content,
      intentTag: activeIntent,
      medications: patientProfile.medications,
      patientName: patientProfile.name,
    })

    setMessages((prev) => [
      ...prev,
      {
        id: `${Date.now()}-assistant`,
        role: 'assistant',
        content: response,
        createdAt: new Date().toISOString(),
      },
    ])

    setIsSending(false)
    setActiveIntent(undefined)
  }

  const handleEscalate = () => {
    setEscalationStatus(
      'Transferring complete chat transcript to a human pharmacist/nurse...'
    )
  }

  return (
    <section
      id="chat"
      className="flex h-full flex-col rounded-xl bg-surface-dark p-6 text-on-dark animate-fade-up"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-on-dark-soft">
            Personalized AI Chatbox
          </p>
          <h2 className="mt-2 text-2xl font-normal tracking-tight">
            Session guidance
          </h2>
        </div>
        <button
          type="button"
          onClick={handleEscalate}
          className="rounded-md border border-on-dark/30 px-3 py-2 text-xs font-semibold text-on-dark"
        >
          Escalate to Clinician
        </button>
      </div>

      {escalationStatus && (
        <div className="mt-4 rounded-lg border border-on-dark/20 bg-surface-dark-elevated px-4 py-3 text-sm text-on-dark">
          {escalationStatus}
        </div>
      )}

      <div className="mt-6 flex-1 space-y-4 overflow-y-auto rounded-lg bg-surface-dark-soft p-4">
        {messages.map((message) => (
          <ChatBubble key={message.id} message={message} />
        ))}
        {isSending && (
          <div className="text-xs text-on-dark-soft">Clinician Copilot is typing...</div>
        )}
      </div>

      <div className="mt-6 space-y-3">
        <QuickStartPills
          activeIntent={activeIntent}
          onSelect={setActiveIntent}
        />
        <ChatInput
          value={inputValue}
          activeIntent={activeIntent}
          onChange={handleChange}
          onSend={handleSend}
          onClearIntent={() => setActiveIntent(undefined)}
          isSending={isSending}
        />
        {isRedFlag && (
          <p className="text-xs text-warning">
            Red-flag symptom detected. Emergency guidance will appear.
          </p>
        )}
      </div>

      <EmergencyModal isOpen={showEmergency} onClose={() => setShowEmergency(false)} />
    </section>
  )
}
