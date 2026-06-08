import { patientProfile } from '../data/patient'

export function PatientProfile() {
  return (
    <section
      id="profile"
      className="animate-fade-up rounded-xl border border-hairline bg-surface-card p-6"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted">
            Patient Profile
          </p>
          <h1 className="mt-2 text-3xl font-normal tracking-tight text-ink">
            {patientProfile.name}
          </h1>
          <p className="mt-1 text-sm text-body">Age {patientProfile.age}</p>
        </div>
        <span className="rounded-pill bg-surface-cream-strong px-3 py-1 text-xs font-semibold text-ink">
          Active
        </span>
      </div>

      <div className="mt-6 grid gap-4">
        <div className="rounded-lg border border-hairline bg-canvas p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-muted">
            Active Conditions
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {patientProfile.conditions.map((condition) => (
              <span
                key={condition}
                className="rounded-pill bg-surface-card px-3 py-1 text-sm text-ink"
              >
                {condition}
              </span>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-hairline bg-canvas p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-muted">Allergies</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {patientProfile.allergies.map((allergy) => (
              <span
                key={allergy}
                className="rounded-pill bg-surface-card px-3 py-1 text-sm text-ink"
              >
                {allergy}
              </span>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-hairline bg-canvas p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-muted">
            Medications
          </p>
          <ul className="mt-3 space-y-2 text-sm text-body">
            {patientProfile.medications.map((med) => (
              <li key={med.name} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-accent-teal" />
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
      </div>
    </section>
  )
}
