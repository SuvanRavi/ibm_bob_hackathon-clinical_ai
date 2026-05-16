import type { QuickStartIntent } from '../types/chat'

interface MockServiceInput {
  message: string
  intentTag?: QuickStartIntent
  medications: Array<{ name: string; dose: string; schedule: string }>
  patientName: string
}

export async function mockOrchestrateService({
  message,
  intentTag,
  medications,
  patientName,
}: MockServiceInput): Promise<string> {
  const medSummary = medications
    .map((med) => `${med.name} ${med.dose}`)
    .slice(0, 2)
    .join(' and ')

  const normalizedMessage = message.toLowerCase()
  const response = (() => {
    switch (intentTag) {
      case 'Admin & Logistics':
        return `Got it, ${patientName}. I can help with scheduling, referrals, and after-visit paperwork. Would you like me to reschedule your follow-up or send a summary to your portal?`
      case 'General Medication':
        return `Thanks for checking in. Based on your current plan (${medSummary}), do you want a refill timeline or dosing reminder for this week?`
      case 'Basic Symptom Education':
        return `I can share general education on symptoms and what to monitor. What symptom or change are you noticing right now?`
      default:
        if (normalizedMessage.includes('refill')) {
          return `I can help map your refill timing. Would you like me to align it with ${medSummary}?`
        }
        return `I am here to help. Tell me what feels most urgent today and I will organize next steps.`
    }
  })()

  return new Promise((resolve) => {
    setTimeout(() => resolve(response), 1500)
  })
}
