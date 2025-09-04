#!/usr/bin/env python3
"""
Simple version of AI Fitness Coach for testing
This version works without MediaPipe and other complex dependencies
"""

from flask import Flask, render_template, request, jsonify
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

# Ensure directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/results', exist_ok=True)

@app.route('/')
def index():
    """Main page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Fitness Coach - Demo</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }
            .upload-area {
                border: 3px dashed #667eea;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                background: #f8f9fa;
            }
            .upload-area:hover {
                border-color: #764ba2;
                background: #e9ecef;
            }
            input[type="file"] {
                margin: 20px 0;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                margin: 10px;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .results {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                display: none;
            }
            .progress {
                width: 100%;
                height: 20px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                margin: 20px 0;
                display: none;
            }
            .progress-bar {
                height: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                width: 0%;
                transition: width 0.3s ease;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏋️ AI Fitness Coach</h1>
            <p style="text-align: center; color: #666; margin-bottom: 30px;">
                Upload your workout video for AI-powered form analysis
            </p>
            
            <div class="upload-area">
                <h3>📹 Upload Workout Video</h3>
                <p>Drag and drop your video file here, or click to browse</p>
                <input type="file" id="videoFile" accept="video/*" style="display: none;">
                <button onclick="document.getElementById('videoFile').click()">Choose File</button>
                <div id="fileName" style="margin-top: 10px; font-weight: bold;"></div>
            </div>
            
            <div class="progress" id="progress">
                <div class="progress-bar" id="progressBar"></div>
                <div id="progressText" style="text-align: center; margin-top: 10px;">Processing...</div>
            </div>
            
            <div style="text-align: center;">
                <button onclick="analyzeVideo()" id="analyzeBtn" disabled>Analyze Video</button>
                <button onclick="showDemoResults()">Show Demo Results</button>
            </div>
            
            <div class="results" id="results">
                <h3>📊 Analysis Results</h3>
                <div id="resultsContent"></div>
            </div>
        </div>

        <script>
            let selectedFile = null;
            
            document.getElementById('videoFile').addEventListener('change', function(e) {
                selectedFile = e.target.files[0];
                if (selectedFile) {
                    document.getElementById('fileName').textContent = 'Selected: ' + selectedFile.name;
                    document.getElementById('analyzeBtn').disabled = false;
                }
            });
            
            function analyzeVideo() {
                if (!selectedFile) return;
                
                document.getElementById('progress').style.display = 'block';
                document.getElementById('results').style.display = 'none';
                
                // Simulate progress
                let progress = 0;
                const progressBar = document.getElementById('progressBar');
                const progressText = document.getElementById('progressText');
                
                const interval = setInterval(() => {
                    progress += Math.random() * 15;
                    if (progress > 100) progress = 100;
                    
                    progressBar.style.width = progress + '%';
                    progressText.textContent = Math.round(progress) + '% complete';
                    
                    if (progress >= 100) {
                        clearInterval(interval);
                        setTimeout(() => {
                            showResults();
                        }, 500);
                    }
                }, 200);
            }
            
            function showDemoResults() {
                document.getElementById('progress').style.display = 'none';
                document.getElementById('results').style.display = 'block';
                
                const demoResults = {
                    exercise: 'Squat',
                    score: 85,
                    reps: 12,
                    issues: [
                        'Knee angle slightly too shallow',
                        'Hip hinge could be deeper'
                    ],
                    recommendations: [
                        'Go deeper in your squat',
                        'Keep your chest up',
                        'Push through your heels'
                    ]
                };
                
                displayResults(demoResults);
            }
            
            function showResults() {
                document.getElementById('progress').style.display = 'none';
                document.getElementById('results').style.display = 'block';
                
                // Mock results for demo
                const mockResults = {
                    exercise: 'Push-up',
                    score: 78,
                    reps: 8,
                    issues: [
                        'Incomplete depth on some reps',
                        'Hip sagging detected'
                    ],
                    recommendations: [
                        'Go deeper on each rep',
                        'Keep your core tight',
                        'Maintain straight body alignment'
                    ]
                };
                
                displayResults(mockResults);
            }
            
            function displayResults(results) {
                const content = `
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
                        <div style="text-align: center; padding: 20px; background: white; border-radius: 10px;">
                            <h4>Overall Score</h4>
                            <div style="font-size: 3em; font-weight: bold; color: ${results.score >= 80 ? '#28a745' : results.score >= 60 ? '#ffc107' : '#dc3545'};">${results.score}</div>
                        </div>
                        <div style="text-align: center; padding: 20px; background: white; border-radius: 10px;">
                            <h4>Exercise</h4>
                            <div style="font-size: 2em; font-weight: bold; color: #667eea;">${results.exercise}</div>
                        </div>
                        <div style="text-align: center; padding: 20px; background: white; border-radius: 10px;">
                            <h4>Repetitions</h4>
                            <div style="font-size: 2em; font-weight: bold; color: #764ba2;">${results.reps}</div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                        <div>
                            <h4>⚠️ Issues Detected</h4>
                            <ul>
                                ${results.issues.map(issue => `<li>${issue}</li>`).join('')}
                            </ul>
                        </div>
                        <div>
                            <h4>💡 Recommendations</h4>
                            <ul>
                                ${results.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `;
                
                document.getElementById('resultsContent').innerHTML = content;
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Handle video upload (mock)"""
    return jsonify({
        'success': True,
        'message': 'Video uploaded successfully (demo mode)',
        'filename': 'demo_video.mp4'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    """Handle video analysis (mock)"""
    return jsonify({
        'success': True,
        'session_id': str(uuid.uuid4()),
        'results': {
            'exercise_detected': 'squat',
            'confidence': 0.95,
            'overall_score': 85,
            'rep_count': 12,
            'issues_detected': ['knee_angle too shallow', 'hip_hinge could be deeper'],
            'recommendations': ['Go deeper in your squat', 'Keep your chest up', 'Push through your heels'],
            'frames_analyzed': 1500,
            'video_duration': 45.2,
            'fps': 30
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-demo',
        'mode': 'demo'
    })

if __name__ == '__main__':
    print("🚀 Starting AI Fitness Coach Demo...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("💡 This is a demo version - no actual video processing")
    app.run(debug=True, host='0.0.0.0', port=5000)
