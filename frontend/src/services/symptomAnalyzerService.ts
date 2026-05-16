/**
 * Symptom Analyzer API Service
 * Handles communication with the backend symptom analyzer endpoint
 */

import type { AnalysisResponse, SymptomAnalyzerStatus } from '../types/symptom'

const API_BASE_URL = 'http://localhost:5000/api'

/**
 * Convert image file to base64 string
 */
export async function convertImageToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = () => {
      const result = reader.result as string
      resolve(result)
    }
    
    reader.onerror = () => {
      reject(new Error('Failed to read image file'))
    }
    
    reader.readAsDataURL(file)
  })
}

/**
 * Validate image file
 */
export function validateImageFile(file: File): { valid: boolean; error?: string } {
  // Check file type
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png']
  if (!validTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Invalid file type. Please upload a JPEG or PNG image.'
    }
  }
  
  // Check file size (max 10MB)
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    return {
      valid: false,
      error: 'File too large. Maximum size is 10MB.'
    }
  }
  
  return { valid: true }
}

/**
 * Analyze symptom from image file
 */
export async function analyzeSymptom(imageFile: File): Promise<AnalysisResponse> {
  try {
    // Validate file
    const validation = validateImageFile(imageFile)
    if (!validation.valid) {
      return {
        success: false,
        error: 'Validation error',
        message: validation.error
      }
    }
    
    // Convert to base64
    const base64Image = await convertImageToBase64(imageFile)
    
    // Send to backend
    const response = await fetch(`${API_BASE_URL}/analyze-symptom`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image: base64Image
      })
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      return {
        success: false,
        error: data.error || 'Analysis failed',
        message: data.message || 'An error occurred during analysis'
      }
    }
    
    return data
    
  } catch (error) {
    console.error('Error analyzing symptom:', error)
    return {
      success: false,
      error: 'Network error',
      message: error instanceof Error ? error.message : 'Failed to connect to server'
    }
  }
}

/**
 * Check if symptom analyzer is available
 */
export async function checkSymptomAnalyzerStatus(): Promise<SymptomAnalyzerStatus> {
  try {
    const response = await fetch(`${API_BASE_URL}/symptom-analyzer/status`)
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error checking symptom analyzer status:', error)
    return {
      available: false,
      message: 'Failed to connect to server'
    }
  }
}

// Made with Bob
