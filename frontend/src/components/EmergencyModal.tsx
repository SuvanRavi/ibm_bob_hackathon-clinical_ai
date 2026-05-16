interface EmergencyModalProps {
  isOpen: boolean
  onClose: () => void
}

export function EmergencyModal({ isOpen, onClose }: EmergencyModalProps) {
  if (!isOpen) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/60 px-6">
      <div className="w-full max-w-md rounded-xl bg-surface-dark p-6 text-on-dark">
        <p className="text-xs uppercase tracking-[0.2em] text-on-dark-soft">
          Emergency Alert
        </p>
        <h2 className="mt-2 text-2xl font-normal tracking-tight">
          EMERGENCY: Please call 999 or proceed to the nearest ER immediately.
        </h2>
        <p className="mt-4 text-sm text-on-dark-soft">
          This assistant is not a substitute for urgent care. If you are in
          immediate danger, contact local emergency services.
        </p>
        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md bg-on-dark px-4 py-2 text-sm font-semibold text-surface-dark"
          >
            I Understand
          </button>
          <button
            type="button"
            className="rounded-md border border-on-dark/30 px-4 py-2 text-sm font-semibold text-on-dark"
          >
            Call 999
          </button>
        </div>
      </div>
    </div>
  )
}
