import { patientProfile } from '../data/patient'

export function ClinicalNotesTasks() {
  return (
    <section className="animate-fade-up rounded-xl border border-hairline bg-surface-card p-5">
      <p className="text-xs uppercase tracking-[0.2em] text-muted">
        Generated clinical note & tasks
      </p>
      <h2 className="mt-2 text-2xl font-normal tracking-tight text-ink">
        Medication timeline overview
      </h2>
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
        <p className="text-xs uppercase tracking-[0.2em] text-muted">Next steps</p>
        <ul className="mt-2 space-y-2 text-sm text-body">
          {patientProfile.nextSteps.map((step) => (
            <li key={step} className="flex items-start gap-3">
              <span className="mt-1 h-2 w-2 rounded-full bg-accent-amber" />
              <span>{step}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
