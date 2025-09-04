import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Brain, BarChart3, Zap, Shield, Upload, Play, TrendingUp, Users } from 'lucide-react'
import VideoUpload from '../components/VideoUpload'
import FeatureCard from '../components/FeatureCard'
import StatsCard from '../components/StatsCard'

export default function Home() {
  const navigate = useNavigate()

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Advanced pose detection and form assessment using cutting-edge computer vision technology.',
      color: 'from-blue-500 to-purple-600'
    },
    {
      icon: BarChart3,
      title: 'Real-time Feedback',
      description: 'Instant form correction and improvement tips with detailed biomechanical analysis.',
      color: 'from-green-500 to-teal-600'
    },
    {
      icon: Zap,
      title: 'Multiple Exercises',
      description: 'Support for squats, push-ups, curls, planks, and more with exercise-specific analysis.',
      color: 'from-orange-500 to-red-600'
    },
    {
      icon: Shield,
      title: 'Privacy First',
      description: 'Your videos are processed locally and never stored on our servers.',
      color: 'from-purple-500 to-pink-600'
    }
  ]

  const stats = [
    { icon: Upload, label: 'Videos Analyzed', value: '10,000+', color: 'text-blue-600' },
    { icon: TrendingUp, label: 'Accuracy Rate', value: '95%', color: 'text-green-600' },
    { icon: Users, label: 'Active Users', value: '5,000+', color: 'text-purple-600' },
    { icon: Play, label: 'Exercises Supported', value: '4+', color: 'text-orange-600' }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-500 via-primary-600 to-secondary-600">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center text-white"
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              AI Fitness Coach
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-white/90 max-w-3xl mx-auto">
              Advanced form analysis powered by artificial intelligence. 
              Get personalized feedback and improve your workout technique.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/analysis')}
                className="btn-primary text-lg px-8 py-4"
              >
                Start Analysis
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/dashboard')}
                className="btn-secondary text-lg px-8 py-4"
              >
                View Dashboard
              </motion.button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Video Upload Section */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Upload Your Workout Video
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Get instant AI-powered analysis of your exercise form. 
              Upload a video and receive detailed feedback in seconds.
            </p>
          </motion.div>
          <VideoUpload />
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Everything you need to improve your fitness form and technique.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <FeatureCard {...feature} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Trusted by Thousands
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Join the community of fitness enthusiasts improving their form with AI.
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <StatsCard {...stat} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
