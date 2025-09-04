from flask import Flask, render_template, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import json
import time
from datetime import datetime
import uuid
from pose_tracker import IntegratedPoseCoach
from features import extract_comprehensive_features, detect_exercise_type, analyze_form_quality

# Import mediapipe with fallback to mock
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    from mediapipe_mock import mp, MEDIAPIPE_AVAILABLE

# Import configuration and utilities
from config import Config, config
from utils.logger import logger, log_function_call, performance_monitor

# Create Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_CONFIG', 'default')
app.config.from_object(config[config_name])

# Set MediaPipe availability
app.MEDIAPIPE_AVAILABLE = MEDIAPIPE_AVAILABLE

# Ensure directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/results', exist_ok=True)
os.makedirs('logs', exist_ok=True)

class VideoAnalyzer:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose(**Config.MEDIAPIPE_CONFIG)
        self.drawing = mp.solutions.drawing_utils
        logger.info("VideoAnalyzer initialized", mediapipe_available=MEDIAPIPE_AVAILABLE)
    
    @log_function_call
    def analyze_video(self, video_path):
        """Analyze uploaded video and return comprehensive results"""
        performance_monitor.start_timer('video_analysis')
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error("Could not open video file", video_path=video_path)
                return {"error": "Could not open video file"}
            
            # Video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Analysis results
            analysis_results = {
                "frames_analyzed": 0,
                "exercise_detected": "unknown",
                "confidence": 0.0,
                "form_scores": [],
                "issues_detected": [],
                "recommendations": [],
                "rep_count": 0,
                "key_frames": [],
                "overall_score": 0,
                "video_duration": duration,
                "fps": fps
            }
            
            exercise_votes = {}
            frame_count = 0
            
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Process every 3rd frame for efficiency (10 FPS analysis)
                    if frame_count % Config.FRAME_SKIP != 0:
                        frame_count += 1
                        continue
                    
                    # Convert to RGB for MediaPipe
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.pose.process(rgb_frame)
                    
                    if results.pose_landmarks:
                        landmarks = results.pose_landmarks.landmark
                        h, w, _ = frame.shape
                        
                        # Extract features
                        features, coords = extract_comprehensive_features(landmarks, (h, w, 3))
                        
                        if features and coords:
                            # Detect exercise
                            detected_exercise = detect_exercise_type(features, coords)
                            exercise_votes[detected_exercise] = exercise_votes.get(detected_exercise, 0) + 1
                            
                            # Analyze form
                            analysis = analyze_form_quality(detected_exercise, features, coords)
                            
                            if analysis:
                                analysis_results["form_scores"].append(analysis["overall_score"])
                                analysis_results["issues_detected"].extend(analysis["issues"])
                                analysis_results["recommendations"].extend(analysis["recommendations"])
                                
                                # Store key frames with poor form
                                if analysis["overall_score"] < 70:
                                    key_frame_path = f"static/results/key_frame_{frame_count}.jpg"
                                    cv2.imwrite(key_frame_path, frame)
                                    analysis_results["key_frames"].append({
                                        "frame": frame_count,
                                        "score": analysis["overall_score"],
                                        "issues": analysis["issues"][:2],  # Top 2 issues
                                        "image_path": key_frame_path
                                    })
                            
                            analysis_results["frames_analyzed"] += 1
                    
                    frame_count += 1
                    
                    # Progress update every 100 frames
                    if frame_count % 100 == 0:
                        logger.info(f"Processed {frame_count} frames...")
            
            finally:
                cap.release()
            
            # Determine most likely exercise
            if exercise_votes:
                most_likely_exercise = max(exercise_votes, key=exercise_votes.get)
                total_votes = sum(exercise_votes.values())
                confidence = exercise_votes[most_likely_exercise] / total_votes
                
                analysis_results["exercise_detected"] = most_likely_exercise
                analysis_results["confidence"] = confidence
                
                # Calculate overall score
                if analysis_results["form_scores"]:
                    analysis_results["overall_score"] = int(sum(analysis_results["form_scores"]) / len(analysis_results["form_scores"]))
                
                # Estimate rep count
                analysis_results["rep_count"] = self.estimate_rep_count(analysis_results["form_scores"])
                
                # Remove duplicates from issues and recommendations
                analysis_results["issues_detected"] = list(set(analysis_results["issues_detected"]))
                analysis_results["recommendations"] = list(set(analysis_results["recommendations"]))
                
                # Log analysis completion
                duration = performance_monitor.end_timer('video_analysis')
                logger.info("Video analysis completed", 
                           exercise=most_likely_exercise, 
                           score=analysis_results["overall_score"],
                           duration=duration)
                
                return analysis_results
            else:
                logger.warning("No pose landmarks detected in video")
                return {"error": "No pose landmarks detected in video"}
                
        except Exception as e:
            logger.error(f"Error during video analysis: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def estimate_rep_count(self, form_scores):
        """Estimate rep count based on form score patterns"""
        if len(form_scores) < 10:
            return 0
        
        # Look for patterns of form degradation and recovery
        threshold = np.mean(form_scores) - np.std(form_scores)
        low_form_periods = 0
        in_low_period = False
        
        for score in form_scores:
            if score < threshold and not in_low_period:
                low_form_periods += 1
                in_low_period = True
            elif score >= threshold:
                in_low_period = False
        
        return max(0, low_form_periods - 1)  # Subtract 1 for initial setup

# Global analyzer instance
analyzer = VideoAnalyzer()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload MP4, AVI, MOV, MKV, or WEBM'}), 400
    
    try:
        # Generate unique filename
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save uploaded file
        file.save(filepath)
        
        # Analyze video
        print(f"Starting analysis of {filename}...")
        analysis_results = analyzer.analyze_video(filepath)
        
        # Add metadata
        analysis_results['upload_time'] = datetime.now().isoformat()
        analysis_results['filename'] = filename
        
        # Save results
        results_filename = f"{uuid.uuid4()}_results.json"
        results_path = os.path.join('static/results', results_filename)
        
        with open(results_path, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        # Clean up uploaded video
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'results_id': results_filename,
            'analysis': analysis_results
        })
    
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return jsonify({'error': f'Error processing video: {str(e)}'}), 500

@app.route('/results/<results_id>')
def get_results(results_id):
    try:
        results_path = os.path.join('static/results', results_id)
        with open(results_path, 'r') as f:
            results = json.load(f)
        return jsonify(results)
    except FileNotFoundError:
        return jsonify({'error': 'Results not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error loading results: {str(e)}'}), 500

@app.route('/demo')
def demo():
    """Demo page with sample analysis"""
    return render_template('demo.html')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'mediapipe_available': MEDIAPIPE_AVAILABLE,
        'version': '1.0.0'
    })

@app.route('/api/docs')
def api_docs():
    """API documentation endpoint"""
    docs = {
        'title': 'AI Fitness Coach API',
        'version': '1.0.0',
        'description': 'RESTful API for AI-powered fitness form analysis',
        'endpoints': {
            'POST /upload': {
                'description': 'Upload and analyze workout video',
                'parameters': {
                    'video': 'Video file (MP4, AVI, MOV, MKV, WEBM)'
                },
                'response': 'Analysis results with form scores and recommendations'
            },
            'GET /results/<id>': {
                'description': 'Retrieve analysis results by ID',
                'response': 'Stored analysis results'
            },
            'GET /health': {
                'description': 'Health check endpoint',
                'response': 'System status and availability'
            }
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 