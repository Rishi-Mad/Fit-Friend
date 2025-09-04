import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Trophy, 
  Dumbbell, 
  Repeat, 
  AlertTriangle, 
  Lightbulb, 
  Download,
  ArrowLeft,
  TrendingUp,
  Clock,
  Target
} from 'lucide-react'
import { useAnalysisStore } from '../stores/analysisStore'
import toast from 'react-hot-toast'

export default function Results() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const { analysisData, setAnalysisData } = useAnalysisStore()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchResults = async () => {
      if (!sessionId) {
        toast.error('Invalid session ID')
        navigate('/')
        return
      }

      try {
        const response = await fetch(`/api/v1/results/${sessionId}`)
        if (!response.ok) {
          throw new Error('Failed to fetch results')
        }
        
        const data = await response.json()
        setAnalysisData(data.results)
      } catch (error) {
        console.error('Error fetching results:', error)
        toast.error('Failed to load analysis results')
        navigate('/')
      } finally {
        setLoading(false)
      }
    }

    if (!analysisData) {
      fetchResults()
    } else {
      setLoading(false)
    }
  }, [sessionId, analysisData, setAnalysisData, navigate])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-primary-100 rounded-full flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
      </div>
    )
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No analysis data found</p>
          <button 
            onClick={() => navigate('/')}
            className="btn-primary mt-4"
          >
            Start New Analysis
          </button>
        </div>
      </div>
    )
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    return 'Needs Improvement'
  }

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <button
            onClick={() => navigate('/')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Home</span>
          </button>
          
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Analysis Results
          </h1>
          <p className="text-lg text-gray-600">
            Your workout form analysis is complete
          </p>
        </motion.div>

        {/* Main Results Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Overall Score */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="lg:col-span-1"
          >
            <div className="card p-8 text-center">
              <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                <Trophy className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Overall Score</h3>
              <div className={`text-6xl font-bold mb-2 ${getScoreColor(analysisData.overall_score)}`}>
                {analysisData.overall_score}
              </div>
              <div className="text-lg text-gray-600 mb-4">
                {getScoreLabel(analysisData.overall_score)}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <motion.div
                  className="bg-gradient-to-r from-primary-500 to-secondary-500 h-3 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${analysisData.overall_score}%` }}
                  transition={{ duration: 1, delay: 0.5 }}
                />
              </div>
            </div>
          </motion.div>

          {/* Exercise & Reps */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="lg:col-span-2"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Exercise Detected */}
              <div className="card p-6">
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-teal-500 rounded-lg flex items-center justify-center">
                    <Dumbbell className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Exercise</h3>
                    <p className="text-sm text-gray-600">Detected with {Math.round(analysisData.confidence * 100)}% confidence</p>
                  </div>
                </div>
                <div className="text-2xl font-bold text-gray-900 capitalize">
                  {analysisData.exercise_detected}
                </div>
              </div>

              {/* Rep Count */}
              <div className="card p-6">
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                    <Repeat className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Repetitions</h3>
                    <p className="text-sm text-gray-600">Complete reps detected</p>
                  </div>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {analysisData.rep_count}
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Issues and Recommendations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Issues */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <div className="card p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900">Issues Detected</h3>
              </div>
              {analysisData.issues_detected.length > 0 ? (
                <ul className="space-y-3">
                  {analysisData.issues_detected.map((issue, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                      className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-400"
                    >
                      <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{issue}</span>
                    </motion.li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-500" />
                  <p>No major issues detected! Great form!</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Recommendations */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <div className="card p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
                  <Lightbulb className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900">Recommendations</h3>
              </div>
              {analysisData.recommendations.length > 0 ? (
                <ul className="space-y-3">
                  {analysisData.recommendations.map((recommendation, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                      className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg border-l-4 border-green-400"
                    >
                      <Lightbulb className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{recommendation}</span>
                    </motion.li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Trophy className="w-12 h-12 mx-auto mb-3 text-green-500" />
                  <p>Keep up the excellent work!</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Analysis Details */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="card p-6 mb-8"
        >
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Analysis Details</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-3 bg-blue-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{analysisData.frames_analyzed}</div>
              <div className="text-sm text-gray-600">Frames Analyzed</div>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-3 bg-green-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{analysisData.video_duration.toFixed(1)}s</div>
              <div className="text-sm text-gray-600">Video Duration</div>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-3 bg-purple-100 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{analysisData.fps.toFixed(1)}</div>
              <div className="text-sm text-gray-600">FPS</div>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-3 bg-orange-100 rounded-lg flex items-center justify-center">
                <Dumbbell className="w-6 h-6 text-orange-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{analysisData.key_frames.length}</div>
              <div className="text-sm text-gray-600">Key Frames</div>
            </div>
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <button className="btn-primary">
            <Download className="w-5 h-5 mr-2" />
            Download Report
          </button>
          <button 
            onClick={() => navigate('/analysis')}
            className="btn-secondary"
          >
            New Analysis
          </button>
        </motion.div>
      </div>
    </div>
  )
}
