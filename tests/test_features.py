"""
Unit tests for features module
Comprehensive testing of feature extraction and analysis functions
"""

import unittest
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features import (
    extract_comprehensive_features,
    detect_exercise_type,
    analyze_form_quality,
    calculate_angle,
    AdvancedFeatureExtractor
)

class TestFeatureExtraction(unittest.TestCase):
    """Test feature extraction functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = AdvancedFeatureExtractor()
        
        # Create mock landmarks
        self.mock_landmarks = []
        for i in range(33):
            # Create realistic pose positions
            if i < 11:  # Head
                x, y = 0.5 + np.random.normal(0, 0.05), 0.2 + np.random.normal(0, 0.05)
            elif i < 23:  # Upper body
                x, y = 0.5 + np.random.normal(0, 0.1), 0.4 + np.random.normal(0, 0.1)
            else:  # Lower body
                x, y = 0.5 + np.random.normal(0, 0.1), 0.7 + np.random.normal(0, 0.1)
            
            landmark = type('Landmark', (), {
                'x': x, 'y': y, 'z': 0.0, 'visibility': 0.8 + np.random.normal(0, 0.1)
            })()
            self.mock_landmarks.append(landmark)
    
    def test_angle_calculation(self):
        """Test angle calculation function"""
        # Test basic angle calculation
        a, b, c = [0, 0], [1, 0], [1, 1]
        angle = calculate_angle(a, b, c)
        self.assertAlmostEqual(angle, 45.0, places=1)
        
        # Test zero vectors
        angle = calculate_angle([0, 0], [0, 0], [1, 1])
        self.assertEqual(angle, 0)
        
        # Test right angle
        a, b, c = [0, 0], [1, 0], [1, 0]
        angle = calculate_angle(a, b, c)
        self.assertAlmostEqual(angle, 0.0, places=1)
    
    def test_feature_extraction(self):
        """Test comprehensive feature extraction"""
        features, coords = extract_comprehensive_features(self.mock_landmarks, (480, 640, 3))
        
        self.assertIsNotNone(features)
        self.assertIsNotNone(coords)
        self.assertIsInstance(features, dict)
        self.assertIsInstance(coords, dict)
        
        # Check for required features
        required_features = ['right_knee_angle', 'left_knee_angle', 'right_hip_angle', 
                           'left_hip_angle', 'right_elbow_angle', 'left_elbow_angle']
        
        for feature in required_features:
            self.assertIn(feature, features)
            self.assertIsInstance(features[feature], (int, float))
    
    def test_exercise_detection(self):
        """Test exercise type detection"""
        # Test with squat-like features
        squat_features = {
            'right_knee_angle': 90,
            'left_knee_angle': 90,
            'right_hip_angle': 45,
            'left_hip_angle': 45,
            'right_elbow_angle': 180,
            'left_elbow_angle': 180
        }
        
        squat_coords = {
            'RIGHT_HIP': (320, 240, 1.0),
            'LEFT_HIP': (320, 240, 1.0),
            'RIGHT_KNEE': (320, 300, 1.0),
            'LEFT_KNEE': (320, 300, 1.0)
        }
        
        detected_exercise = detect_exercise_type(squat_features, squat_coords)
        self.assertIn(detected_exercise, ['squat', 'unknown'])
    
    def test_form_analysis(self):
        """Test form quality analysis"""
        features = {
            'right_knee_angle': 90,
            'left_knee_angle': 90,
            'right_hip_angle': 45,
            'left_hip_angle': 45,
            'right_elbow_angle': 180,
            'left_elbow_angle': 180
        }
        
        coords = {
            'RIGHT_HIP': (320, 240, 1.0),
            'LEFT_HIP': (320, 240, 1.0),
            'RIGHT_KNEE': (320, 300, 1.0),
            'LEFT_KNEE': (320, 300, 1.0)
        }
        
        analysis = analyze_form_quality('squat', features, coords)
        
        self.assertIsNotNone(analysis)
        self.assertIsInstance(analysis, dict)
        
        if analysis:
            self.assertIn('score', analysis)
            self.assertIn('issues', analysis)
            self.assertIn('recommendations', analysis)
            
            self.assertIsInstance(analysis['score'], (int, float))
            self.assertIsInstance(analysis['issues'], list)
            self.assertIsInstance(analysis['recommendations'], list)
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with None landmarks
        features, coords = extract_comprehensive_features(None, (480, 640, 3))
        self.assertIsNone(features)
        self.assertIsNone(coords)
        
        # Test with empty landmarks
        features, coords = extract_comprehensive_features([], (480, 640, 3))
        self.assertIsNone(features)
        self.assertIsNone(coords)
        
        # Test with invalid shape
        features, coords = extract_comprehensive_features(self.mock_landmarks, None)
        self.assertIsNone(features)
        self.assertIsNone(coords)

class TestAdvancedFeatureExtractor(unittest.TestCase):
    """Test AdvancedFeatureExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = AdvancedFeatureExtractor()
    
    def test_calculate_distance(self):
        """Test distance calculation"""
        p1, p2 = (0, 0), (3, 4)
        distance = self.extractor.calculate_distance(p1, p2)
        self.assertEqual(distance, 5.0)
        
        p1, p2 = (1, 1), (1, 1)
        distance = self.extractor.calculate_distance(p1, p2)
        self.assertEqual(distance, 0.0)
    
    def test_angle_history(self):
        """Test angle history tracking"""
        self.extractor.angle_history.append(90)
        self.extractor.angle_history.append(85)
        
        self.assertEqual(len(self.extractor.angle_history), 2)
        self.assertEqual(self.extractor.angle_history[0], 90)
        self.assertEqual(self.extractor.angle_history[1], 85)

if __name__ == '__main__':
    unittest.main() 