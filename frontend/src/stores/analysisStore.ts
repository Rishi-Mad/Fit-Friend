import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface AnalysisData {
  frames_analyzed: number
  exercise_detected: string
  confidence: number
  form_scores: number[]
  issues_detected: string[]
  recommendations: string[]
  rep_count: number
  key_frames: Array<{
    frame: number
    score: number
    issues: string[]
    image_path: string
  }>
  overall_score: number
  video_duration: number
  fps: number
}

interface AnalysisState {
  currentFile: File | null
  analysisData: AnalysisData | null
  analysisHistory: AnalysisData[]
  isLoading: boolean
  error: string | null
  
  // Actions
  setCurrentFile: (file: File | null) => void
  setAnalysisData: (data: AnalysisData) => void
  addToHistory: (data: AnalysisData) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearAnalysis: () => void
}

export const useAnalysisStore = create<AnalysisState>()(
  persist(
    (set, get) => ({
      currentFile: null,
      analysisData: null,
      analysisHistory: [],
      isLoading: false,
      error: null,

      setCurrentFile: (file) => set({ currentFile: file }),
      
      setAnalysisData: (data) => {
        set({ analysisData: data })
        // Add to history
        const { analysisHistory } = get()
        set({ 
          analysisHistory: [data, ...analysisHistory.slice(0, 9)] // Keep last 10 analyses
        })
      },
      
      addToHistory: (data) => {
        const { analysisHistory } = get()
        set({ 
          analysisHistory: [data, ...analysisHistory.slice(0, 9)]
        })
      },
      
      setLoading: (loading) => set({ isLoading: loading }),
      
      setError: (error) => set({ error }),
      
      clearAnalysis: () => set({ 
        currentFile: null, 
        analysisData: null, 
        error: null 
      }),
    }),
    {
      name: 'analysis-storage',
      partialize: (state) => ({ 
        analysisHistory: state.analysisHistory 
      }),
    }
  )
)
