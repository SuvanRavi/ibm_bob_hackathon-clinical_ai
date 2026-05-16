export function ClinicAccessCard() {
  return (
    <section
      id="clinic"
      className="mt-6 rounded-xl border border-hairline bg-canvas p-5"
    >
      <p className="text-xs uppercase tracking-[0.2em] text-muted">
        Clinic access
      </p>
      <h3 className="mt-2 text-xl font-normal tracking-tight text-ink">
        Nearby clinics & appointments
      </h3>
      <p className="mt-2 text-sm text-body">
        Find a clinic near the patient or schedule a follow-up appointment.
      </p>
      <div className="mt-4 grid gap-3">
        <div className="rounded-lg border border-hairline bg-surface-card p-4">
          <p className="text-sm font-medium text-ink">Downtown Health Center</p>
          <p className="text-xs text-muted">2.1 km • Next available: Tue 10:30</p>
        </div>
        <div className="rounded-lg border border-hairline bg-surface-card p-4">
          <p className="text-sm font-medium text-ink">Riverside Clinic</p>
          <p className="text-xs text-muted">3.8 km • Next available: Wed 14:15</p>
        </div>
      </div>
      <div className="mt-4 flex gap-3">
        <button className="rounded-md border border-hairline px-3 py-2 text-xs font-semibold text-body">
          View map
        </button>
        <button className="rounded-md bg-primary px-3 py-2 text-xs font-semibold text-on-primary">
          Book appointment
        </button>
      </div>
    </section>
  )
}
