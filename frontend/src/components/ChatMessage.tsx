import type { ChatMessage as ChatMessageType } from '../types/chat'

interface ChatMessageProps {
  message: ChatMessageType
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[75%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-primary text-on-primary'
            : 'bg-surface-dark-soft text-on-dark'
        }`}
      >
        {message.intentTag && isUser && (
          <span className="mb-2 inline-flex rounded-pill bg-on-primary/20 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.2em]">
            {message.intentTag}
          </span>
        )}
        <p>{message.content}</p>
      </div>
    </div>
  )
}
