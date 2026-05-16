import type { QuickStartIntent } from '../types/chat'

const intents: QuickStartIntent[] = [
  'Admin & Logistics',
  'General Medication',
  'Basic Symptom Education',
]

interface QuickStartPillsProps {
  activeIntent?: QuickStartIntent
  onSelect: (intent: QuickStartIntent) => void
}

export function QuickStartPills({ activeIntent, onSelect }: QuickStartPillsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {intents.map((intent) => {
        const isActive = intent === activeIntent
        return (
          <button
            key={intent}
            type="button"
            onClick={() => onSelect(intent)}
            className={`rounded-pill border px-3 py-1 text-xs font-semibold transition ${
              isActive
                ? 'border-transparent bg-surface-cream-strong text-ink'
                : 'border-hairline bg-canvas text-muted hover:text-ink'
            }`}
          >
            {intent}
          </button>
        )
      })}
    </div>
  )
}
