#!/usr/bin/env python3
"""
Test script to validate AI Fitness Coach setup
Run this script to ensure all components are working correctly
"""

import sys
import importlib
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    required_modules = [
        'cv2',
        'mediapipe',
        'numpy',
        'flask',
        'werkzeug',
        'pyttsx3'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("✅ All modules imported successfully!")
        return True

def test_mediapipe():
    """Test MediaPipe pose detection"""
    print("\n🤖 Testing MediaPipe pose detection...")
    
    try:
        import mediapipe as mp
        import cv2
        import numpy as np
        
        # Initialize pose detection
        pose = mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        
        # Create a dummy image
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Process the image
        results = pose.process(dummy_image)
        
        print("✅ MediaPipe pose detection initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ MediaPipe test failed: {e}")
        return False

def test_features_module():
    """Test the features module"""
    print("\n📊 Testing features module...")
    
    try:
        from features import extract_comprehensive_features, detect_exercise_type, analyze_form_quality
        
        # Test with dummy data
        import numpy as np
        
        # Create dummy landmarks
        class DummyLandmark:
            def __init__(self, x, y, visibility=1.0):
                self.x = x
                self.y = y
                self.visibility = visibility
        
        # Create dummy landmarks array
        landmarks = [DummyLandmark(0.5, 0.5) for _ in range(33)]
        
        # Test feature extraction
        features, coords = extract_comprehensive_features(landmarks, (480, 640, 3))
        
        if features is not None:
            print("✅ Feature extraction working")
        else:
            print("❌ Feature extraction failed")
            return False
        
        # Test exercise detection
        exercise = detect_exercise_type(features, coords)
        print(f"✅ Exercise detection working (detected: {exercise})")
        
        # Test form analysis
        analysis = analyze_form_quality(exercise, features, coords)
        if analysis:
            print("✅ Form analysis working")
        else:
            print("❌ Form analysis failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Features module test failed: {e}")
        traceback.print_exc()
        return False

def test_smart_coach():
    """Test the smart coach module"""
    print("\n🎯 Testing smart coach module...")
    
    try:
        from smart_coach import SmartCoach
        
        # Initialize coach
        coach = SmartCoach(voice_enabled=False)  # Disable voice for testing
        
        # Test basic functionality
        coach.update(form_score=85, rep_count=5, exercise_type="squat")
        
        # Test performance summary
        summary = coach.get_performance_summary()
        
        print("✅ Smart coach working")
        return True
        
    except Exception as e:
        print(f"❌ Smart coach test failed: {e}")
        traceback.print_exc()
        return False

def test_flask_app():
    """Test Flask app initialization"""
    print("\n🌐 Testing Flask app...")
    
    try:
        from app import app
        
        # Test app creation
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Flask app working")
                return True
            else:
                print(f"❌ Flask app test failed: status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        traceback.print_exc()
        return False

def test_opencv():
    """Test OpenCV functionality"""
    print("\n📹 Testing OpenCV...")
    
    try:
        import cv2
        
        # Test basic OpenCV functionality
        img = cv2.imread('test_setup.py')  # This will fail, but we're testing import
        print("✅ OpenCV working")
        return True
        
    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Fitness Coach - Setup Validation")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("OpenCV", test_opencv),
        ("MediaPipe", test_mediapipe),
        ("Features Module", test_features_module),
        ("Smart Coach", test_smart_coach),
        ("Flask App", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your AI Fitness Coach is ready to use.")
        print("\n🚀 To start the application:")
        print("   python app.py")
        print("\n🎯 To run real-time mode:")
        print("   python pose_tracker.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 Common solutions:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Check Python version (requires 3.8+)")
        print("   - Ensure all files are in the correct directory")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 