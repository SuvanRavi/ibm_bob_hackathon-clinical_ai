import { patientProfile } from '../data/patient'

export function PostAppointmentHub() {
  return (
    <section id="follow-up" className="mt-6 animate-fade-up space-y-4">
      <div className="rounded-xl border border-hairline bg-canvas p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-muted">
              Post-Appointment Hub
            </p>
            <h2 className="mt-2 text-2xl font-normal tracking-tight text-ink">
              Follow-up uploads
            </h2>
          </div>
          <span className="rounded-pill bg-surface-card px-3 py-1 text-xs font-semibold text-ink">
            New
          </span>
        </div>

        <div className="mt-4 grid gap-3">
          <div className="flex items-center justify-between rounded-lg border border-hairline bg-surface-card p-4">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-canvas">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M12 3a4 4 0 0 1 4 4v4a4 4 0 1 1-8 0V7a4 4 0 0 1 4-4Z"
                    stroke="#141413"
                    strokeWidth="1.5"
                  />
                  <path
                    d="M6 11a6 6 0 0 0 12 0"
                    stroke="#141413"
                    strokeWidth="1.5"
                  />
                  <path
                    d="M12 17v4"
                    stroke="#141413"
                    strokeWidth="1.5"
                  />
                </svg>
              </span>
              <div>
                <p className="text-sm font-medium text-ink">
                  Appointment voice recordings
                </p>
                <p className="text-xs text-muted">
                  Upload speech-to-text audio notes
                </p>
              </div>
            </div>
            <button className="rounded-md border border-hairline px-3 py-1 text-xs font-medium text-body">
              Upload
            </button>
          </div>

          <div className="flex items-center justify-between rounded-lg border border-hairline bg-surface-card p-4">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-canvas">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6Z"
                    stroke="#141413"
                    strokeWidth="1.5"
                  />
                  <path
                    d="M8 14l2.5-2.5 3 3L16 12l4 4"
                    stroke="#141413"
                    strokeWidth="1.5"
                  />
                  <circle cx="9" cy="9" r="1.5" fill="#141413" />
                </svg>
              </span>
              <div>
                <p className="text-sm font-medium text-ink">Symptom analysis</p>
                <p className="text-xs text-muted">
                  Upload an image of a rash or symptom
                </p>
              </div>
            </div>
            <button className="rounded-md border border-hairline px-3 py-1 text-xs font-medium text-body">
              Upload
            </button>
          </div>
        </div>
      </div>

      <div
        id="notes"
        className="rounded-xl border border-hairline bg-surface-card p-5"
      >
        <p className="text-xs uppercase tracking-[0.2em] text-muted">
          Generated clinical note & tasks
        </p>
        <h3 className="mt-2 text-xl font-normal tracking-tight text-ink">
          Medication timeline overview
        </h3>
        <p className="mt-2 text-sm text-body">
          Summary generated from appointment audio and intake forms.
        </p>
        <div className="mt-4 rounded-lg border border-hairline bg-canvas p-4">
          <ul className="space-y-3 text-sm text-body">
            {patientProfile.medications.map((med) => (
              <li key={med.name} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary" />
                <div>
                  <p className="font-medium text-ink">
                    {med.name} {med.dose}
                  </p>
                  <p className="text-xs text-muted">{med.schedule}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div className="mt-4 rounded-lg border border-hairline bg-surface-cream-strong p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-muted">
            Next steps
          </p>
          <ul className="mt-2 space-y-2 text-sm text-body">
            {patientProfile.nextSteps.map((step) => (
              <li key={step} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-accent-amber" />
                <span>{step}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
