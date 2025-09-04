"""
Mock MediaPipe module for development when MediaPipe is not available
This allows the project to run and be tested without MediaPipe installation
"""

import numpy as np
from typing import List, Tuple, Optional

class MockPoseLandmark:
    """Mock pose landmarks for testing"""
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32

class MockLandmark:
    """Mock landmark class"""
    def __init__(self, x: float, y: float, z: float = 0.0, visibility: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

class MockPoseLandmarks:
    """Mock pose landmarks container"""
    def __init__(self):
        # Create 33 mock landmarks with reasonable positions
        self.landmark = []
        for i in range(33):
            # Generate realistic pose positions
            if i < 11:  # Head landmarks
                x = 0.5 + np.random.normal(0, 0.05)
                y = 0.2 + np.random.normal(0, 0.05)
            elif i < 23:  # Upper body
                x = 0.5 + np.random.normal(0, 0.1)
                y = 0.4 + np.random.normal(0, 0.1)
            else:  # Lower body
                x = 0.5 + np.random.normal(0, 0.1)
                y = 0.7 + np.random.normal(0, 0.1)
            
            self.landmark.append(MockLandmark(x, y, visibility=0.8 + np.random.normal(0, 0.1)))

class MockPoseResults:
    """Mock pose detection results"""
    def __init__(self):
        self.pose_landmarks = MockPoseLandmarks()

class MockPose:
    """Mock MediaPipe Pose class"""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    
    def process(self, image):
        """Mock pose processing"""
        return MockPoseResults()

class MockDrawing:
    """Mock drawing utilities"""
    @staticmethod
    def draw_landmarks(image, landmarks, connections=None, **kwargs):
        """Mock landmark drawing"""
        return image

# Create mock solutions module
class MockSolutions:
    class pose:
        Pose = MockPose
        PoseLandmark = MockPoseLandmark
        drawing_utils = MockDrawing

# Create mock mediapipe module
class MockMediaPipe:
    solutions = MockSolutions()

# Global flag to check if real mediapipe is available
MEDIAPIPE_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    print("⚠️  MediaPipe not available. Using mock implementation for development.")
    mp = MockMediaPipe() 