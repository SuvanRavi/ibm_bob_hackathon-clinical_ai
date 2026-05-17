import { Route, Routes } from 'react-router-dom'
import { ChatPanel } from './components/ChatPanel'
import { ClinicAccessCard } from './components/ClinicAccessCard'
import { PatientProfile } from './components/PatientProfile'
import { PostAppointmentHub } from './components/PostAppointmentHub'
import { SymptomAnalyzer } from './components/SymptomAnalyzer'
import { TopNav } from './components/TopNav'
import { ClinicalNotesTasks } from './pages/ClinicalNotesTasks'
import { FollowUpUploads } from './pages/FollowUpUploads'

function App() {
  return (
    <div className="min-h-screen bg-canvas bg-canvas-glow font-body text-body">
      <TopNav />
      <main className="mx-auto grid max-w-6xl gap-6 px-6 py-12">
        <Routes>
          <Route
            path="/"
            element={
              <div className="max-w-3xl">
                <ChatPanel />
              </div>
            }
          />
          <Route
            path="/profile"
            element={
              <div className="max-w-3xl">
                <PatientProfile />
              </div>
            }
          />
          <Route
            path="/follow-up"
            element={
              <div className="max-w-3xl">
                <FollowUpUploads />
              </div>
            }
          />
          <Route
            path="/notes"
            element={
              <div className="max-w-3xl">
                <ClinicalNotesTasks />
              </div>
            }
          />
          <Route
            path="/clinic"
            element={
              <div className="max-w-3xl">
                <ClinicAccessCard />
              </div>
            }
          />
          <Route
            path="/symptom-analyzer"
            element={
              <div className="max-w-3xl">
                <SymptomAnalyzer />
              </div>
            }
          />
        </Routes>
      </main>
    </div>
  )
}

export default App
