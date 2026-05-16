/**
 * TypeScript types for Symptom Analyzer feature
 */

export type SeverityLevel = 'mild' | 'moderate' | 'severe'

export interface AlternativeDiagnosis {
  condition: string
  confidence: number
}

export interface SymptomAnalysis {
  condition: string
  condition_code: string
  confidence: number
  severity: SeverityLevel
  severity_score: number
  recommended_action: string
  additional_notes: string
  timestamp: string
  alternative_diagnoses?: AlternativeDiagnosis[]
}

export interface AnalysisResponse {
  success: boolean
  analysis?: SymptomAnalysis
  error?: string
  message?: string
}

export interface SymptomAnalyzerStatus {
  available: boolean
  message: string
}

// Made with Bob
