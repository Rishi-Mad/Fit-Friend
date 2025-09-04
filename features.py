import math
import numpy as np
from collections import deque
import warnings
warnings.filterwarnings('ignore')

# Import mediapipe with fallback to mock
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    from mediapipe_mock import mp, MEDIAPIPE_AVAILABLE

pose = mp.solutions.pose.PoseLandmark

class AdvancedFeatureExtractor:
    def __init__(self):
        self.angle_history = deque(maxlen=30)
        self.velocity_history = deque(maxlen=10)
        
    def calculate_angle(self, a, b, c):
        """Enhanced angle calculation with error handling"""
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba = a - b
        bc = c - b
        
        # Handle zero vectors
        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)
        
        if norm_ba == 0 or norm_bc == 0:
            return 0
            
        cosine = np.dot(ba, bc) / (norm_ba * norm_bc)
        angle = np.arccos(np.clip(cosine, -1.0, 1.0))
        return round(np.degrees(angle), 2)
    
    def calculate_distance(self, p1, p2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Create global instance for backward compatibility
feature_extractor = AdvancedFeatureExtractor()

# Keep your original function signature for compatibility
def calculate_angle(a, b, c):
    """Backward compatible angle calculation"""
    return feature_extractor.calculate_angle(a, b, c)

def extract_comprehensive_features(landmarks, shape):
    """Enhanced version of your original function"""
    h, w, _ = shape
    
    # Helper function with enhanced error handling
    def get_landmark_safe(name):
        try:
            landmark = landmarks[getattr(pose, name).value]
            return (
                int(landmark.x * w), 
                int(landmark.y * h),
                landmark.visibility if hasattr(landmark, 'visibility') else 1.0
            )
        except:
            return (0, 0, 0.0)
    
    try:
        # Extract all landmarks with visibility
        pts = {}
        landmark_names = [
            'RIGHT_HIP', 'RIGHT_KNEE', 'RIGHT_ANKLE',
            'LEFT_HIP', 'LEFT_KNEE', 'LEFT_ANKLE',
            'RIGHT_SHOULDER', 'RIGHT_ELBOW', 'RIGHT_WRIST',
            'LEFT_SHOULDER', 'LEFT_ELBOW', 'LEFT_WRIST',
            'RIGHT_EAR', 'LEFT_EAR', 'NOSE',
            'RIGHT_HEEL', 'LEFT_HEEL', 'RIGHT_FOOT_INDEX', 'LEFT_FOOT_INDEX'
        ]
        
        for name in landmark_names:
            pts[name] = get_landmark_safe(name)
        
        # Calculate your original angles
        angles = {
            'right_knee_angle': calculate_angle(pts['RIGHT_HIP'][:2], pts['RIGHT_KNEE'][:2], pts['RIGHT_ANKLE'][:2]),
            'left_knee_angle': calculate_angle(pts['LEFT_HIP'][:2], pts['LEFT_KNEE'][:2], pts['LEFT_ANKLE'][:2]),
            'right_hip_angle': calculate_angle(pts['RIGHT_SHOULDER'][:2], pts['RIGHT_HIP'][:2], pts['RIGHT_KNEE'][:2]),
            'left_hip_angle': calculate_angle(pts['LEFT_SHOULDER'][:2], pts['LEFT_HIP'][:2], pts['LEFT_KNEE'][:2]),
            'right_elbow_angle': calculate_angle(pts['RIGHT_SHOULDER'][:2], pts['RIGHT_ELBOW'][:2], pts['RIGHT_WRIST'][:2]),
            'left_elbow_angle': calculate_angle(pts['LEFT_SHOULDER'][:2], pts['LEFT_ELBOW'][:2], pts['LEFT_WRIST'][:2]),
        }
        
        # ADD NEW ENHANCED FEATURES
        # Body alignment and symmetry
        hip_center = [
            (pts['RIGHT_HIP'][0] + pts['LEFT_HIP'][0]) / 2,
            (pts['RIGHT_HIP'][1] + pts['LEFT_HIP'][1]) / 2
        ]
        
        shoulder_center = [
            (pts['RIGHT_SHOULDER'][0] + pts['LEFT_SHOULDER'][0]) / 2,
            (pts['RIGHT_SHOULDER'][1] + pts['LEFT_SHOULDER'][1]) / 2
        ]
        
        # Enhanced features that improve accuracy
        enhanced_features = {
            # Spine alignment
            'spine_angle': calculate_angle(
                pts['NOSE'][:2], 
                shoulder_center, 
                hip_center
            ),
            
            # Body symmetry
            'knee_symmetry': abs(pts['RIGHT_KNEE'][1] - pts['LEFT_KNEE'][1]),
            'hip_symmetry': abs(pts['RIGHT_HIP'][1] - pts['LEFT_HIP'][1]),
            'shoulder_symmetry': abs(pts['RIGHT_SHOULDER'][1] - pts['LEFT_SHOULDER'][1]),
            
            # Stance and positioning
            'foot_distance': feature_extractor.calculate_distance(
                pts['RIGHT_FOOT_INDEX'][:2], 
                pts['LEFT_FOOT_INDEX'][:2]
            ),
            'torso_lean': abs(hip_center[0] - shoulder_center[0]),
            
            # Body proportions
            'shoulder_hip_distance': feature_extractor.calculate_distance(shoulder_center, hip_center),
            
            # Confidence metrics
            'avg_visibility': np.mean([pts[name][2] for name in landmark_names if len(pts[name]) > 2]),
            'min_visibility': min([pts[name][2] for name in landmark_names if len(pts[name]) > 2]),
        }
        
        # Calculate temporal features (movement dynamics)
        temporal_features = calculate_temporal_features(angles)
        
        # Combine all features
        all_features = {**angles, **enhanced_features, **temporal_features}
        
        return all_features, pts
        
    except Exception as e:
        print(f"[ERROR] Enhanced feature extraction failed: {e}")
        return None, None

def calculate_temporal_features(current_angles):
    """Calculate movement velocity and smoothness"""
    temporal_features = {}
    
    # Store angle history for temporal analysis
    feature_extractor.angle_history.append(current_angles.copy())
    
    if len(feature_extractor.angle_history) >= 2:
        # Calculate angular velocities
        prev_angles = feature_extractor.angle_history[-2]
        dt = 1/30.0  # Assuming 30 FPS
        
        for joint in current_angles.keys():
            if joint in prev_angles:
                velocity = abs(current_angles[joint] - prev_angles[joint]) / dt
                temporal_features[f'{joint}_velocity'] = velocity
                
                # Movement smoothness indicator
                if velocity > 100:  # Fast movement threshold
                    temporal_features[f'{joint}_is_fast'] = 1
                else:
                    temporal_features[f'{joint}_is_fast'] = 0
    
    return temporal_features

def detect_exercise_type(features, coords):
    """Enhanced exercise detection with more criteria"""
    
    # Calculate averages
    avg_knee = (features['right_knee_angle'] + features['left_knee_angle']) / 2
    avg_hip = (features['right_hip_angle'] + features['left_hip_angle']) / 2
    avg_elbow = (features['right_elbow_angle'] + features['left_elbow_angle']) / 2
    
    # Enhanced squat detection
    if (avg_knee < 140 and avg_hip < 130 and 
        features.get('foot_distance', 0) > 40 and  # Proper stance
        features.get('spine_angle', 180) > 160):   # Upright torso
        return "squat"
    
    # Enhanced bicep curl detection
    elif (avg_elbow < 120 and 
          features.get('shoulder_hip_distance', 0) > 100 and  # Standing upright
          features.get('torso_lean', 0) < 20):  # Not leaning too much
        return "bicep_curl"
    
    # Push-up detection
    elif (avg_elbow < 130 and 
          features.get('spine_angle', 0) > 160 and  # Straight body line
          features.get('shoulder_hip_distance', 0) < 80):  # Horizontal position
        return "push_up"
    
    # Plank detection
    elif (features.get('spine_angle', 0) > 170 and 
          features.get('shoulder_hip_distance', 0) < 60):
        return "plank"
    
    return "unknown"

def analyze_form_quality(exercise, features, coords):
    """Enhanced form analysis with specific recommendations"""
    score = 100
    issues = []
    recommendations = []
    
    if exercise == "squat":
        # Knee angle analysis
        avg_knee = (features['right_knee_angle'] + features['left_knee_angle']) / 2
        if avg_knee < 60:
            issues.append("Squatting too deep - risk of knee injury")
            recommendations.append("Don't go below parallel (90 degrees)")
            score -= 20
        elif avg_knee > 140:
            issues.append("Not squatting deep enough")
            recommendations.append("Go deeper until thighs are parallel")
            score -= 15
        
        # Hip hinge analysis
        avg_hip = (features['right_hip_angle'] + features['left_hip_angle']) / 2
        if avg_hip < 60:
            issues.append("Hips not hinging properly")
            recommendations.append("Push hips back more, imagine sitting in a chair")
            score -= 20
        
        # Torso lean
        if features.get('torso_lean', 0) > 30:
            issues.append("Leaning forward too much")
            recommendations.append("Keep chest up and core engaged")
            score -= 15
        
        # Knee symmetry
        if features.get('knee_symmetry', 0) > 15:
            issues.append("Uneven knee positioning")
            recommendations.append("Focus on balanced movement")
            score -= 10
        
        # Stance width
        if features.get('foot_distance', 0) < 40:
            issues.append("Stance too narrow")
            recommendations.append("Widen stance to shoulder width")
            score -= 10
        
        # Movement speed
        knee_velocity = features.get('right_knee_angle_velocity', 0)
        if knee_velocity > 100:
            issues.append("Moving too quickly")
            recommendations.append("Slow down for better control")
            score -= 10
    
    elif exercise == "bicep_curl":
        # Elbow analysis
        if features['right_elbow_angle'] > 170 or features['left_elbow_angle'] > 170:
            issues.append("Elbow overextending")
            recommendations.append("Don't fully lock out elbows")
            score -= 10
        
        # Momentum check
        elbow_velocity = features.get('right_elbow_angle_velocity', 0)
        if elbow_velocity > 150:
            issues.append("Using momentum - swinging weights")
            recommendations.append("Use controlled movements")
            score -= 20
        
        # Posture check
        if features.get('torso_lean', 0) > 15:
            issues.append("Leaning too much")
            recommendations.append("Stand straight, engage core")
            score -= 10
    
    elif exercise == "push_up":
        # Elbow angle
        avg_elbow = (features['right_elbow_angle'] + features['left_elbow_angle']) / 2
        if avg_elbow > 160:
            issues.append("Not going down far enough")
            recommendations.append("Lower until chest nearly touches ground")
            score -= 15
        
        # Body alignment
        if features.get('spine_angle', 180) < 160:
            issues.append("Hips sagging or piking")
            recommendations.append("Maintain straight line from head to heels")
            score -= 20
    
    # Visibility check for all exercises
    if features.get('min_visibility', 1.0) < 0.7:
        issues.append("Poor camera angle or lighting")
        recommendations.append("Improve camera position and lighting")
        score -= 5
    
    return {
        "overall_score": max(score, 0), 
        "issues": issues,
        "recommendations": recommendations
    }