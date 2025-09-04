import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, FileVideo, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAnalysisStore } from '../stores/analysisStore'

export default function VideoUpload() {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const { setAnalysisData, setCurrentFile } = useAnalysisStore()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file type
    const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm']
    if (!validTypes.includes(file.type)) {
      toast.error('Please upload a valid video file (MP4, AVI, MOV, MKV, WEBM)')
      return
    }

    // Validate file size (100MB limit)
    const maxSize = 100 * 1024 * 1024 // 100MB
    if (file.size > maxSize) {
      toast.error('File size must be less than 100MB')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)
    setCurrentFile(file)

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + Math.random() * 10
        })
      }, 200)

      // Create FormData for upload
      const formData = new FormData()
      formData.append('video', file)

      // Upload file
      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const uploadResult = await response.json()
      clearInterval(progressInterval)
      setUploadProgress(100)

      // Start analysis
      const analysisResponse = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename: uploadResult.filename }),
      })

      if (!analysisResponse.ok) {
        throw new Error('Analysis failed')
      }

      const analysisResult = await analysisResponse.json()
      setAnalysisData(analysisResult.results)

      toast.success('Analysis completed successfully!')
      
      // Navigate to results page
      setTimeout(() => {
        window.location.href = `/results/${analysisResult.session_id}`
      }, 1000)

    } catch (error) {
      console.error('Upload/Analysis error:', error)
      toast.error('Failed to upload or analyze video. Please try again.')
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }, [setAnalysisData, setCurrentFile])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    },
    multiple: false,
    disabled: isUploading
  })

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="w-full"
    >
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }
          ${isUploading ? 'pointer-events-none opacity-75' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {isUploading ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <div className="w-16 h-16 mx-auto bg-primary-100 rounded-full flex items-center justify-center">
              <Upload className="w-8 h-8 text-primary-600 animate-pulse" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Processing Video...
              </h3>
              <p className="text-gray-600 mb-4">
                Analyzing your workout form with AI
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <motion.div
                  className="bg-primary-600 h-2 rounded-full"
                  style={{ width: `${uploadProgress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">
                {Math.round(uploadProgress)}% complete
              </p>
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center">
              {isDragActive ? (
                <CheckCircle className="w-8 h-8 text-primary-600" />
              ) : (
                <FileVideo className="w-8 h-8 text-gray-600" />
              )}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {isDragActive ? 'Drop your video here' : 'Upload Workout Video'}
              </h3>
              <p className="text-gray-600 mb-4">
                Drag and drop your video file here, or click to browse
              </p>
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                <AlertCircle className="w-4 h-4" />
                <span>Supports MP4, AVI, MOV, MKV, WEBM (max 100MB)</span>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
