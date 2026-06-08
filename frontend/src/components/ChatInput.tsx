import type { QuickStartIntent } from '../types/chat'

interface ChatInputProps {
  value: string
  activeIntent?: QuickStartIntent
  onChange: (value: string) => void
  onSend: () => void
  onClearIntent: () => void
  isSending: boolean
}

export function ChatInput({
  value,
  activeIntent,
  onChange,
  onSend,
  onClearIntent,
  isSending,
}: ChatInputProps) {
  return (
    <div className="rounded-lg border border-hairline bg-canvas p-3">
      {activeIntent && (
        <div className="mb-2 flex items-center justify-between rounded-pill bg-surface-card px-3 py-1">
          <span className="text-[11px] font-semibold uppercase tracking-[0.2em] text-ink">
            {activeIntent}
          </span>
          <button
            type="button"
            onClick={onClearIntent}
            className="text-xs font-medium text-muted"
          >
            Clear
          </button>
        </div>
      )}
      <div className="flex items-center gap-3">
        <input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Ask Here..."
          className="flex-1 bg-transparent text-sm text-body outline-none"
        />
        <button
          type="button"
          onClick={onSend}
          disabled={isSending}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-on-primary transition disabled:cursor-not-allowed disabled:bg-primary-disabled"
        >
          Send
        </button>
      </div>
    </div>
  )
}
