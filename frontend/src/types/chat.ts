export type ChatRole = 'user' | 'assistant' | 'system'

export type QuickStartIntent =
  | 'Admin & Logistics'
  | 'General Medication'
  | 'Basic Symptom Education'

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  intentTag?: QuickStartIntent
  createdAt: string
}
