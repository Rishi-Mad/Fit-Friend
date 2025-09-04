import { motion } from 'framer-motion'
import { useAnalysisStore } from '../stores/analysisStore'
import { 
  TrendingUp, 
  Activity, 
  Target, 
  Calendar,
  BarChart3,
  Trophy,
  Clock,
  Zap
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

export default function Dashboard() {
  const { analysisHistory } = useAnalysisStore()

  // Calculate statistics
  const totalAnalyses = analysisHistory.length
  const averageScore = analysisHistory.length > 0 
    ? Math.round(analysisHistory.reduce((sum, analysis) => sum + analysis.overall_score, 0) / analysisHistory.length)
    : 0
  const bestScore = analysisHistory.length > 0 
    ? Math.max(...analysisHistory.map(analysis => analysis.overall_score))
    : 0
  const totalReps = analysisHistory.reduce((sum, analysis) => sum + analysis.rep_count, 0)

  // Prepare chart data
  const scoreHistory = analysisHistory.slice(0, 10).reverse().map((analysis, index) => ({
    session: `Session ${index + 1}`,
    score: analysis.overall_score,
    reps: analysis.rep_count
  }))

  const exerciseDistribution = analysisHistory.reduce((acc, analysis) => {
    acc[analysis.exercise_detected] = (acc[analysis.exercise_detected] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const exerciseData = Object.entries(exerciseDistribution).map(([exercise, count]) => ({
    exercise: exercise.charAt(0).toUpperCase() + exercise.slice(1),
    count
  }))

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Fitness Dashboard
          </h1>
          <p className="text-lg text-gray-600">
            Track your progress and analyze your fitness journey
          </p>
        </motion.div>

        {analysisHistory.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center py-16"
          >
            <div className="w-24 h-24 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
              <BarChart3 className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-2xl font-semibold text-gray-900 mb-4">
              No Analysis Data Yet
            </h3>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Start analyzing your workout videos to see your progress and statistics here.
            </p>
            <button 
              onClick={() => window.location.href = '/analysis'}
              className="btn-primary"
            >
              Start Your First Analysis
            </button>
          </motion.div>
        ) : (
          <>
            {/* Stats Overview */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8"
            >
              <div className="card p-6 text-center">
                <div className="w-12 h-12 mx-auto mb-4 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Activity className="w-6 h-6 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{totalAnalyses}</div>
                <div className="text-sm text-gray-600">Total Analyses</div>
              </div>

              <div className="card p-6 text-center">
                <div className="w-12 h-12 mx-auto mb-4 bg-green-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{averageScore}</div>
                <div className="text-sm text-gray-600">Average Score</div>
              </div>

              <div className="card p-6 text-center">
                <div className="w-12 h-12 mx-auto mb-4 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Trophy className="w-6 h-6 text-purple-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{bestScore}</div>
                <div className="text-sm text-gray-600">Best Score</div>
              </div>

              <div className="card p-6 text-center">
                <div className="w-12 h-12 mx-auto mb-4 bg-orange-100 rounded-lg flex items-center justify-center">
                  <Target className="w-6 h-6 text-orange-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{totalReps}</div>
                <div className="text-sm text-gray-600">Total Reps</div>
              </div>
            </motion.div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Score Trend */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="card p-6"
              >
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Score Trend</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={scoreHistory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="session" />
                      <YAxis domain={[0, 100]} />
                      <Tooltip />
                      <Line 
                        type="monotone" 
                        dataKey="score" 
                        stroke="#667eea" 
                        strokeWidth={3}
                        dot={{ fill: '#667eea', strokeWidth: 2, r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </motion.div>

              {/* Exercise Distribution */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="card p-6"
              >
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Exercise Distribution</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={exerciseData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="exercise" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#764ba2" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </motion.div>
            </div>

            {/* Recent Analyses */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="card p-6"
            >
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Recent Analyses</h3>
              <div className="space-y-4">
                {analysisHistory.slice(0, 5).map((analysis, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
                        <Activity className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900 capitalize">
                          {analysis.exercise_detected}
                        </div>
                        <div className="text-sm text-gray-600">
                          {analysis.rep_count} reps • {analysis.frames_analyzed} frames
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${analysis.overall_score >= 80 ? 'text-green-600' : analysis.overall_score >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {analysis.overall_score}
                      </div>
                      <div className="text-sm text-gray-600">Score</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </>
        )}
      </div>
    </div>
  )
}
