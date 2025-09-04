"""
Test suite for AI Fitness Coach application
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from app import app, analyzer, allowed_file

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_video():
    """Create a sample video file for testing"""
    # Create a temporary video file
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    temp_file.write(b'fake video content')
    temp_file.close()
    yield temp_file.name
    os.unlink(temp_file.name)

class TestApp:
    """Test cases for the main application"""
    
    def test_index_route(self, client):
        """Test the main index route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'AI Fitness Coach' in response.data
    
    def test_demo_route(self, client):
        """Test the demo route"""
        response = client.get('/demo')
        assert response.status_code == 200
        assert b'Demo' in response.data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
    
    def test_api_docs(self, client):
        """Test API documentation endpoint"""
        response = client.get('/api/docs')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'AI Fitness Coach API'
        assert 'endpoints' in data
    
    def test_allowed_file_function(self):
        """Test file extension validation"""
        assert allowed_file('test.mp4') == True
        assert allowed_file('test.avi') == True
        assert allowed_file('test.mov') == True
        assert allowed_file('test.txt') == False
        assert allowed_file('test') == False
    
    @patch('app.analyzer.analyze_video')
    def test_upload_video_success(self, mock_analyze, client, sample_video):
        """Test successful video upload and analysis"""
        # Mock the analysis results
        mock_analyze.return_value = {
            'exercise_detected': 'squat',
            'confidence': 0.95,
            'overall_score': 85,
            'rep_count': 10,
            'issues_detected': ['knee_angle too shallow'],
            'recommendations': ['Go deeper in your squat'],
            'key_frames': [],
            'video_duration': 30.0,
            'fps': 30,
            'frames_analyzed': 100
        }
        
        with open(sample_video, 'rb') as video_file:
            response = client.post('/upload', 
                                 data={'video': (video_file, 'test.mp4')},
                                 content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'analysis' in data
        assert data['analysis']['exercise_detected'] == 'squat'
    
    def test_upload_no_file(self, client):
        """Test upload without file"""
        response = client.post('/upload')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_upload_invalid_file_type(self, client):
        """Test upload with invalid file type"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.write(b'not a video')
        temp_file.close()
        
        try:
            with open(temp_file.name, 'rb') as file:
                response = client.post('/upload',
                                     data={'video': (file, 'test.txt')},
                                     content_type='multipart/form-data')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
        finally:
            os.unlink(temp_file.name)
    
    def test_get_results_not_found(self, client):
        """Test getting results for non-existent ID"""
        response = client.get('/results/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

class TestVideoAnalyzer:
    """Test cases for the VideoAnalyzer class"""
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly"""
        assert analyzer is not None
        assert hasattr(analyzer, 'pose')
        assert hasattr(analyzer, 'drawing')
    
    def test_estimate_rep_count(self):
        """Test rep count estimation"""
        # Test with good form scores
        good_scores = [85, 87, 89, 86, 88, 90, 87, 89, 88, 90]
        reps = analyzer.estimate_rep_count(good_scores)
        assert reps >= 0
        
        # Test with poor form scores
        poor_scores = [30, 25, 35, 20, 40, 25, 30, 35, 20, 25]
        reps = analyzer.estimate_rep_count(poor_scores)
        assert reps >= 0
        
        # Test with empty scores
        reps = analyzer.estimate_rep_count([])
        assert reps == 0

if __name__ == '__main__':
    pytest.main([__file__])
