"""
API Routes for AI Fitness Coach
RESTful API endpoints with comprehensive error handling and validation
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional

from utils.logger import logger, log_function_call
from config import Config

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

def validate_file_upload(file) -> Dict[str, Any]:
    """Validate uploaded file"""
    if not file:
        return {'valid': False, 'error': 'No file provided'}
    
    if file.filename == '':
        return {'valid': False, 'error': 'No file selected'}
    
    if not Config.is_allowed_file(file.filename):
        return {'valid': False, 'error': 'File type not allowed'}
    
    return {'valid': True, 'filename': secure_filename(file.filename)}

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'mediapipe_available': getattr(current_app, 'MEDIAPIPE_AVAILABLE', False)
    })

@api.route('/upload', methods=['POST'])
@log_function_call
def upload_video():
    """Upload video for analysis"""
    try:
        # Validate request
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        validation = validate_file_upload(file)
        
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 400
        
        # Generate unique filename
        filename = validation['filename']
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file.save(filepath)
        
        logger.info(f"Video uploaded successfully", filename=unique_filename)
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'message': 'Video uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

@api.route('/analyze', methods=['POST'])
@log_function_call
def analyze_video():
    """Analyze uploaded video"""
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data:
            return jsonify({'error': 'Filename required'}), 400
        
        filename = data['filename']
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Import here to avoid circular imports
        from app import VideoAnalyzer
        
        analyzer = VideoAnalyzer()
        results = analyzer.analyze_video(filepath)
        
        if 'error' in results:
            return jsonify({'error': results['error']}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save results
        results_file = f"static/results/{session_id}.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Analysis completed", session_id=session_id, exercise=results.get('exercise_detected'))
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return jsonify({'error': 'Analysis failed'}), 500

@api.route('/results/<session_id>', methods=['GET'])
@log_function_call
def get_results(session_id: str):
    """Get analysis results by session ID"""
    try:
        results_file = f"static/results/{session_id}.json"
        
        if not os.path.exists(results_file):
            return jsonify({'error': 'Results not found'}), 404
        
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Failed to retrieve results: {str(e)}")
        return jsonify({'error': 'Failed to retrieve results'}), 500

@api.route('/exercises', methods=['GET'])
def get_supported_exercises():
    """Get list of supported exercises"""
    exercises = [
        {
            'name': 'squat',
            'display_name': 'Squat',
            'description': 'Lower body compound exercise',
            'muscle_groups': ['quadriceps', 'glutes', 'hamstrings'],
            'difficulty': 'beginner'
        },
        {
            'name': 'pushup',
            'display_name': 'Push-up',
            'description': 'Upper body pushing exercise',
            'muscle_groups': ['chest', 'triceps', 'shoulders'],
            'difficulty': 'beginner'
        },
        {
            'name': 'bicep_curl',
            'display_name': 'Bicep Curl',
            'description': 'Isolation exercise for biceps',
            'muscle_groups': ['biceps'],
            'difficulty': 'beginner'
        },
        {
            'name': 'plank',
            'display_name': 'Plank',
            'description': 'Core stability exercise',
            'muscle_groups': ['core', 'shoulders'],
            'difficulty': 'beginner'
        }
    ]
    
    return jsonify({
        'success': True,
        'exercises': exercises
    })

@api.route('/stats', methods=['GET'])
def get_analytics_stats():
    """Get analytics statistics"""
    try:
        # Count analysis sessions
        results_dir = "static/results"
        if os.path.exists(results_dir):
            session_count = len([f for f in os.listdir(results_dir) if f.endswith('.json')])
        else:
            session_count = 0
        
        # Count uploaded videos
        upload_dir = Config.UPLOAD_FOLDER
        if os.path.exists(upload_dir):
            video_count = len([f for f in os.listdir(upload_dir) 
                             if Config.is_allowed_file(f)])
        else:
            video_count = 0
        
        stats = {
            'total_sessions': session_count,
            'total_videos': video_count,
            'mediapipe_available': getattr(current_app, 'MEDIAPIPE_AVAILABLE', False),
            'uptime': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@api.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@api.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@api.errorhandler(413)
def too_large(error):
    """Handle file too large errors"""
    return jsonify({'error': 'File too large'}), 413 