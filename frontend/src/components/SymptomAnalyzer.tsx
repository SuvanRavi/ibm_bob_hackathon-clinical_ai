import { useState, useRef } from 'react'
import type { AnalysisResponse, SeverityLevel } from '../types/symptom'
import { analyzeSymptom } from '../services/symptomAnalyzerService'

export function SymptomAnalyzer() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setSelectedImage(file)
    setAnalysisResult(null)

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleAnalyze = async () => {
    if (!selectedImage) return

    setIsAnalyzing(true)
    setAnalysisResult(null)

    try {
      const result = await analyzeSymptom(selectedImage)
      setAnalysisResult(result)
    } catch (error) {
      setAnalysisResult({
        success: false,
        error: 'Analysis failed',
        message: error instanceof Error ? error.message : 'Unknown error occurred'
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReset = () => {
    setSelectedImage(null)
    setImagePreview(null)
    setAnalysisResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const getSeverityColor = (severity: SeverityLevel) => {
    switch (severity) {
      case 'severe':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'moderate':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'mild':
        return 'text-green-600 bg-green-50 border-green-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getSeverityIcon = (severity: SeverityLevel) => {
    switch (severity) {
      case 'severe':
        return '⚠️'
      case 'moderate':
        return '⚡'
      case 'mild':
        return '✓'
      default:
        return 'ℹ️'
    }
  }

  return (
    <section className="animate-fade-up rounded-xl border border-hairline bg-canvas p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-muted">
            AI-Powered Analysis
          </p>
          <h2 className="mt-2 text-2xl font-normal tracking-tight text-ink">
            Symptom Analyzer
          </h2>
          <p className="mt-2 text-sm text-muted">
            Upload an image of a skin condition for AI-powered analysis and recommendations
          </p>
        </div>
      </div>

      {/* Upload Section */}
      <div className="mt-6">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/jpg,image/png"
          onChange={handleImageSelect}
          className="hidden"
          id="symptom-image-upload"
        />
        
        {!imagePreview ? (
          <label
            htmlFor="symptom-image-upload"
            className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-hairline bg-surface-card p-12 transition-colors hover:border-ink/30 hover:bg-surface-card/80"
          >
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              className="mb-4 text-muted"
            >
              <path
                d="M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6Z"
                stroke="currentColor"
                strokeWidth="1.5"
              />
              <path
                d="M8 14l2.5-2.5 3 3L16 12l4 4"
                stroke="currentColor"
                strokeWidth="1.5"
              />
              <circle cx="9" cy="9" r="1.5" fill="currentColor" />
            </svg>
            <p className="text-sm font-medium text-ink">
              Click to upload an image
            </p>
            <p className="mt-1 text-xs text-muted">
              JPEG or PNG, max 10MB
            </p>
          </label>
        ) : (
          <div className="space-y-4">
            {/* Image Preview */}
            <div className="relative overflow-hidden rounded-lg border border-hairline bg-surface-card">
              <img
                src={imagePreview}
                alt="Selected symptom"
                className="h-64 w-full object-contain"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="flex-1 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-canvas transition-colors hover:bg-ink/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAnalyzing ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Analyzing...
                  </span>
                ) : (
                  'Analyze Symptom'
                )}
              </button>
              <button
                onClick={handleReset}
                disabled={isAnalyzing}
                className="rounded-md border border-hairline px-4 py-2 text-sm font-medium text-body transition-colors hover:bg-surface-card disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Reset
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="mt-6 animate-fade-up">
          {analysisResult.success && analysisResult.analysis ? (
            <div className="space-y-4">
              {/* Condition Card */}
              <div className="rounded-lg border border-hairline bg-surface-card p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-xs uppercase tracking-wider text-muted">
                      Detected Condition
                    </p>
                    <h3 className="mt-1 text-lg font-semibold text-ink">
                      {analysisResult.analysis.condition}
                    </h3>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted">Confidence</p>
                    <p className="text-2xl font-bold text-ink">
                      {(analysisResult.analysis.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>

                {/* Confidence Bar */}
                <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-canvas">
                  <div
                    className="h-full bg-ink transition-all duration-500"
                    style={{
                      width: `${analysisResult.analysis.confidence * 100}%`
                    }}
                  />
                </div>
              </div>

              {/* Severity Badge */}
              <div
                className={`rounded-lg border p-4 ${getSeverityColor(
                  analysisResult.analysis.severity
                )}`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-2xl">
                    {getSeverityIcon(analysisResult.analysis.severity)}
                  </span>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider">
                      Severity: {analysisResult.analysis.severity}
                    </p>
                    <p className="text-xs opacity-75">
                      Score: {analysisResult.analysis.severity_score}/10
                    </p>
                  </div>
                </div>
              </div>

              {/* Recommended Action */}
              <div className="rounded-lg border border-hairline bg-surface-card p-4">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted">
                  Recommended Action
                </p>
                <p className="mt-2 text-sm leading-relaxed text-ink">
                  {analysisResult.analysis.recommended_action}
                </p>
              </div>

              {/* Additional Notes */}
              <div className="rounded-lg border border-hairline bg-surface-card p-4">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted">
                  Additional Information
                </p>
                <p className="mt-2 text-sm leading-relaxed text-body">
                  {analysisResult.analysis.additional_notes}
                </p>
              </div>

              {/* Alternative Diagnoses */}
              {analysisResult.analysis.alternative_diagnoses &&
                analysisResult.analysis.alternative_diagnoses.length > 0 && (
                  <div className="rounded-lg border border-hairline bg-surface-card p-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-muted">
                      Alternative Diagnoses
                    </p>
                    <div className="mt-3 space-y-2">
                      {analysisResult.analysis.alternative_diagnoses.map(
                        (alt, idx) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between text-sm"
                          >
                            <span className="text-body">{alt.condition}</span>
                            <span className="font-medium text-ink">
                              {(alt.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

              {/* Disclaimer */}
              <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
                <p className="text-xs leading-relaxed text-yellow-800">
                  <strong>⚠️ Medical Disclaimer:</strong> This AI analysis is for
                  informational purposes only and should not replace professional
                  medical advice. Always consult with a qualified healthcare
                  provider for proper diagnosis and treatment.
                </p>
              </div>
            </div>
          ) : (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4">
              <p className="text-sm font-semibold text-red-800">
                {analysisResult.error || 'Analysis Failed'}
              </p>
              <p className="mt-1 text-xs text-red-700">
                {analysisResult.message || 'An error occurred during analysis'}
              </p>
            </div>
          )}
        </div>
      )}
    </section>
  )
}

// Made with Bob
