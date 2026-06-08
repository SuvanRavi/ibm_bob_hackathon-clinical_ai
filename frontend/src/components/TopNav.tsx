import { NavLink } from 'react-router-dom'
import { BrandMark } from './BrandMark'

export function TopNav() {
  return (
    <header className="sticky top-0 z-20 border-b border-hairline bg-canvas/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <NavLink to="/" className="flex items-center gap-3">
          <BrandMark />
          <span className="font-display text-lg tracking-tight text-ink">
            Clinician Copilot
          </span>
        </NavLink>
        <nav className="hidden items-center gap-6 text-sm font-medium text-body md:flex">
          <NavLink className="cursor-pointer" to="/">
            AI Chat
          </NavLink>
          <NavLink className="cursor-pointer" to="/profile">
            Profile
          </NavLink>
          <NavLink className="cursor-pointer" to="/follow-up">
            Follow-Up
          </NavLink>
          <NavLink className="cursor-pointer" to="/notes">
            Notes & Tasks
          </NavLink>
          <NavLink className="cursor-pointer" to="/clinic">
            Clinic
          </NavLink>
        </nav>
        <div className="flex items-center gap-3">
          <button className="text-sm font-medium text-body">Sign in</button>
          <button className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-on-primary transition hover:bg-primary-active">
            Try Copilot
          </button>
        </div>
      </div>
    </header>
  )
}
