"""
Configuration settings for AI Fitness Coach
Centralized configuration management
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'mpg', 'mpeg'}
    
    # MediaPipe Configuration
    MEDIAPIPE_CONFIG = {
        'static_image_mode': False,
        'model_complexity': 1,
        'enable_segmentation': False,
        'min_detection_confidence': 0.7,
        'min_tracking_confidence': 0.5
    }
    
    # Analysis Configuration
    FRAME_SKIP = 3  # Process every 3rd frame for efficiency
    MIN_FRAMES_FOR_ANALYSIS = 30
    MAX_ANALYSIS_DURATION = 300  # 5 minutes max
    
    # Exercise Detection Configuration
    EXERCISE_CONFIDENCE_THRESHOLD = 0.6
    MIN_REPS_FOR_VALID_SET = 3
    
    # Form Analysis Configuration
    FORM_SCORE_WEIGHTS = {
        'squat': {
            'knee_angle': 0.3,
            'hip_angle': 0.25,
            'spine_alignment': 0.2,
            'depth': 0.15,
            'symmetry': 0.1
        },
        'pushup': {
            'elbow_angle': 0.3,
            'body_alignment': 0.25,
            'depth': 0.2,
            'stability': 0.15,
            'symmetry': 0.1
        },
        'bicep_curl': {
            'elbow_angle': 0.4,
            'torso_stability': 0.25,
            'range_of_motion': 0.2,
            'control': 0.15
        },
        'plank': {
            'spine_alignment': 0.4,
            'stability': 0.3,
            'hip_position': 0.2,
            'duration': 0.1
        }
    }
    
    # Voice Configuration
    VOICE_ENABLED = os.environ.get('VOICE_ENABLED', 'False').lower() == 'true'
    VOICE_RATE = int(os.environ.get('VOICE_RATE', '180'))
    
    # Database Configuration (for future use)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///fitness_coach.db')
    
    # API Configuration
    API_RATE_LIMIT = '100 per minute'
    
    # Security Configuration
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000']
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'fitness_coach.log'
    
    @classmethod
    def get_exercise_config(cls, exercise_type: str) -> Dict[str, Any]:
        """Get configuration for specific exercise type"""
        return cls.FORM_SCORE_WEIGHTS.get(exercise_type, {})
    
    @classmethod
    def is_allowed_file(cls, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in cls.ALLOWED_EXTENSIONS

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Stricter settings for production
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    MIN_DETECTION_CONFIDENCE = 0.8

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 