import cv2
import mediapipe as mp
import numpy as np
import time
import os
import csv
from collections import deque
import threading
import queue
import sys
import traceback

# Import your modules with error handling
try:
    from features import extract_comprehensive_features, detect_exercise_type, analyze_form_quality
    print("[INFO] Successfully imported features module")
except ImportError as e:
    print(f"[ERROR] Failed to import features module: {e}")
    sys.exit(1)

try:
    from smart_coach import SmartCoach  # Use the backward compatible wrapper
    print("[INFO] Successfully imported SmartCoach")
except ImportError as e:
    print(f"[ERROR] Failed to import SmartCoach: {e}")
    sys.exit(1)

class IntegratedPoseCoach:
    """
    Main class that integrates all components for seamless operation
    """
    def __init__(self, voice_enabled=True, camera_id=0):
        print("[INFO] Initializing Integrated Pose Coach...")
        
        # Core components
        self.voice_enabled = voice_enabled
        self.camera_id = camera_id
        
        # MediaPipe setup
        try:
            self.pose = mp.solutions.pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.drawing = mp.solutions.drawing_utils
            print("[INFO] MediaPipe initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize MediaPipe: {e}")
            raise
        
        # Smart Coach - Initialize with proper error handling
        try:
            self.coach = SmartCoach()
            print("[INFO] SmartCoach initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize SmartCoach: {e}")
            print("[WARNING] Continuing without voice coaching")
            self.coach = None
        
        # Session tracking
        self.session_start_time = time.time()
        self.frame_count = 0
        self.fps_counter = deque(maxlen=30)
        
        # Exercise tracking
        self.current_exercise = "unknown"
        self.exercise_confidence = 0
        self.exercise_history = deque(maxlen=10)  # For smoothing exercise detection
        
        # Rep counting
        self.rep_count = 0
        self.rep_states = {
            "squat": {"threshold_low": 120, "threshold_high": 160, "current_phase": "up", "last_angle": None},
            "bicep_curl": {"threshold_low": 90, "threshold_high": 150, "current_phase": "down", "last_angle": None},
            "push_up": {"threshold_low": 110, "threshold_high": 160, "current_phase": "up", "last_angle": None}
        }
        
        # Data logging
        self.data_file = "workout_session.csv"
        self.ensure_data_file()
        
        # UI settings
        self.show_landmarks = True
        self.show_detailed_info = True
        self.recording_mode = False
        
        # Performance tracking
        self.last_form_score = 100
        self.form_scores = deque(maxlen=50)
        self.last_coaching_time = 0
        self.coaching_interval = 8  # seconds
        
        # Error tracking
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        
        print("[INFO] Integrated Pose Coach initialized successfully!")
        self.print_controls()
    
    def print_controls(self):
        """Display available controls"""
        print("\n=== CONTROLS ===")
        print("Q - Quit application")
        print("S - Save current frame and data")
        print("R - Reset session")
        print("I - Toggle detailed info display")
        print("L - Toggle landmark display")
        print("C - Get coaching tip")
        print("W - Get workout summary")
        print("SPACE - Toggle recording mode")
        print("===============\n")
    
    def ensure_data_file(self):
        """Create CSV file for session data if it doesn't exist"""
        try:
            if not os.path.exists(self.data_file):
                with open(self.data_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'timestamp', 'exercise', 'rep_count', 'form_score', 
                        'issues', 'recommendations', 'session_duration'
                    ])
                print(f"[INFO] Created data file: {self.data_file}")
        except Exception as e:
            print(f"[ERROR] Failed to create data file: {e}")
    
    def smooth_exercise_detection(self, detected_exercise):
        """Smooth exercise detection to avoid rapid switching"""
        if detected_exercise is None:
            detected_exercise = "unknown"
            
        self.exercise_history.append(detected_exercise)
        
        if len(self.exercise_history) >= 5:
            # Count occurrences of each exercise in recent history
            exercise_counts = {}
            for ex in self.exercise_history:
                exercise_counts[ex] = exercise_counts.get(ex, 0) + 1
            
            # Get most common exercise
            most_common = max(exercise_counts, key=exercise_counts.get)
            confidence = exercise_counts[most_common] / len(self.exercise_history)
            
            # Only update if confidence is high enough
            if confidence >= 0.6:  # 60% confidence threshold
                self.current_exercise = most_common
                self.exercise_confidence = confidence
        
        return self.current_exercise
    
    def update_rep_count(self, features):
        """Enhanced rep counting with proper state management"""
        if self.current_exercise not in self.rep_states:
            return
        
        state = self.rep_states[self.current_exercise]
        
        try:
            if self.current_exercise == "squat":
                if 'right_knee_angle' in features and 'left_knee_angle' in features:
                    avg_knee = (features['right_knee_angle'] + features['left_knee_angle']) / 2
                    self._count_reps_squat(avg_knee, state)
            
            elif self.current_exercise == "bicep_curl":
                if 'right_elbow_angle' in features and 'left_elbow_angle' in features:
                    avg_elbow = (features['right_elbow_angle'] + features['left_elbow_angle']) / 2
                    self._count_reps_bicep(avg_elbow, state)
            
            elif self.current_exercise == "push_up":
                if 'right_elbow_angle' in features and 'left_elbow_angle' in features:
                    avg_elbow = (features['right_elbow_angle'] + features['left_elbow_angle']) / 2
                    self._count_reps_pushup(avg_elbow, state)
        
        except (KeyError, TypeError) as e:
            print(f"[DEBUG] Rep counting error: {e}")
    
    def _count_reps_squat(self, knee_angle, state):
        """Count squats based on knee angle"""
        if state["current_phase"] == "up" and knee_angle < state["threshold_low"]:
            state["current_phase"] = "down"
            print(f"[DEBUG] Squat down phase - knee angle: {knee_angle:.1f}")
        
        elif state["current_phase"] == "down" and knee_angle > state["threshold_high"]:
            state["current_phase"] = "up"
            self.rep_count += 1
            print(f"[INFO] Squat completed! Rep #{self.rep_count}")
            if self.coach:
                self.coach.say_coaching(f"Great squat! Rep {self.rep_count}")
    
    def _count_reps_bicep(self, elbow_angle, state):
        """Count bicep curls based on elbow angle"""
        if state["current_phase"] == "down" and elbow_angle < state["threshold_low"]:
            state["current_phase"] = "up"
            print(f"[DEBUG] Bicep curl up phase - elbow angle: {elbow_angle:.1f}")
        
        elif state["current_phase"] == "up" and elbow_angle > state["threshold_high"]:
            state["current_phase"] = "down"
            self.rep_count += 1
            print(f"[INFO] Bicep curl completed! Rep #{self.rep_count}")
            if self.coach:
                self.coach.say_coaching(f"Nice curl! Rep {self.rep_count}")
    
    def _count_reps_pushup(self, elbow_angle, state):
        """Count push-ups based on elbow angle"""
        if state["current_phase"] == "up" and elbow_angle < state["threshold_low"]:
            state["current_phase"] = "down"
            print(f"[DEBUG] Push-up down phase - elbow angle: {elbow_angle:.1f}")
        
        elif state["current_phase"] == "down" and elbow_angle > state["threshold_high"]:
            state["current_phase"] = "up"
            self.rep_count += 1
            print(f"[INFO] Push-up completed! Rep #{self.rep_count}")
            if self.coach:
                self.coach.say_coaching(f"Strong push-up! Rep {self.rep_count}")
    
    def calculate_fps(self):
        """Calculate current FPS"""
        current_time = time.time()
        self.fps_counter.append(current_time)
        
        if len(self.fps_counter) > 1:
            fps = len(self.fps_counter) / (self.fps_counter[-1] - self.fps_counter[0])
            return fps
        return 0
    
    def draw_interface(self, frame, features, analysis):
        """Draw the main user interface"""
        h, w = frame.shape[:2]
        
        # Performance color coding
        score = analysis.get('overall_score', 0) if analysis else 0
        if score >= 80:
            color = (0, 255, 0)  # Green
            level = "EXCELLENT"
        elif score >= 60:
            color = (0, 255, 255)  # Yellow
            level = "GOOD"
        elif score >= 40:
            color = (0, 165, 255)  # Orange
            level = "NEEDS WORK"
        else:
            color = (0, 0, 255)  # Red
            level = "POOR"
        
        # Main info panel
        panel_height = 220 if self.show_detailed_info else 140
        cv2.rectangle(frame, (10, 10), (420, panel_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (420, panel_height), color, 2)
        
        y = 35
        # Exercise info
        cv2.putText(frame, f"Exercise: {self.current_exercise.replace('_', ' ').title()}", 
                   (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y += 25
        
        # Rep count
        cv2.putText(frame, f"Reps: {self.rep_count}", 
                   (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        y += 25
        
        # Form score
        cv2.putText(frame, f"Form: {int(score)}/100 ({level})", 
                   (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        y += 25
        
        # Session info
        duration = time.time() - self.session_start_time
        fps = self.calculate_fps()
        cv2.putText(frame, f"Time: {duration/60:.1f}m | FPS: {fps:.1f}", 
                   (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 20
        
        # Confidence indicator
        cv2.putText(frame, f"Detection: {self.exercise_confidence:.1%}", 
                   (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        y += 25
        
        # Detailed info
        if self.show_detailed_info and analysis:
            # Issues
            issues = analysis.get('issues', [])
            if issues:
                cv2.putText(frame, "Issues:", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                y += 20
                for issue in issues[:2]:  # Show top 2 issues
                    text = f"• {issue[:35]}..." if len(issue) > 35 else f"• {issue}"
                    cv2.putText(frame, text, (25, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                    y += 15
            
            # Recommendations
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                cv2.putText(frame, "Tips:", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                y += 20
                for rec in recommendations[:2]:  # Show top 2 recommendations
                    text = f"• {rec[:35]}..." if len(rec) > 35 else f"• {rec}"
                    cv2.putText(frame, text, (25, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                    y += 15
        
        # Recording indicator
        if self.recording_mode:
            cv2.circle(frame, (w - 30, 30), 8, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (w - 55, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Error indicator
        if self.consecutive_errors > 3:
            cv2.putText(frame, f"Errors: {self.consecutive_errors}", 
                       (w - 120, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Controls
        cv2.putText(frame, "Q-Quit | S-Save | R-Reset | I-Info | L-Landmarks | C-Tip | W-Summary", 
                   (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
    
    def save_session_data(self, analysis):
        """Save current session data to CSV"""
        try:
            timestamp = time.time()
            duration = timestamp - self.session_start_time
            
            with open(self.data_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    self.current_exercise,
                    self.rep_count,
                    analysis.get('overall_score', 0) if analysis else 0,
                    '; '.join(analysis.get('issues', [])) if analysis else '',
                    '; '.join(analysis.get('recommendations', [])) if analysis else '',
                    duration
                ])
            
            print(f"[INFO] Session data saved to {self.data_file}")
            if self.coach:
                self.coach.say_coaching("Data saved!")
            
        except Exception as e:
            print(f"[ERROR] Failed to save data: {e}")
    
    def reset_session(self):
        """Reset the current session"""
        self.session_start_time = time.time()
        self.rep_count = 0
        self.current_exercise = "unknown"
        self.exercise_confidence = 0
        self.exercise_history.clear()
        self.form_scores.clear()
        self.fps_counter.clear()
        self.consecutive_errors = 0
        
        # Reset rep states
        for exercise in self.rep_states:
            self.rep_states[exercise]["current_phase"] = "up" if exercise in ["squat", "push_up"] else "down"
            self.rep_states[exercise]["last_angle"] = None
        
        # Reset coach
        if self.coach:
            self.coach.reset_session()
        
        print("[INFO] Session reset successfully")
    
    def update_coach(self, form_score, features, issues, recommendations):
        """Update the coach with current workout data"""
        if not self.coach:
            return
            
        try:
            # Use the enhanced update method if available
            if hasattr(self.coach, 'update') and len(self.coach.update.__code__.co_varnames) > 3:
                self.coach.update(
                    form_score=form_score,
                    rep_count=self.rep_count,
                    exercise_type=self.current_exercise,
                    features=features,
                    issues=issues,
                    recommendations=recommendations
                )
            else:
                # Fall back to basic update method
                self.coach.update(form_score, self.rep_count)
                
        except Exception as e:
            print(f"[ERROR] Coach update failed: {e}")
    
    def run(self):
        """Main execution loop"""
        # Initialize camera
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print(f"[ERROR] Could not open camera {self.camera_id}")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("[INFO] Starting pose tracking...")
        if self.coach:
            self.coach.say_coaching("Pose tracking started! Let's get fit!")
        
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    print("[ERROR] Failed to capture frame")
                    self.consecutive_errors += 1
                    if self.consecutive_errors > self.max_consecutive_errors:
                        print("[ERROR] Too many consecutive errors, stopping")
                        break
                    continue
                
                # Reset error counter on successful frame
                self.consecutive_errors = 0
                
                # Process frame
                frame = cv2.flip(frame, 1)  # Mirror effect
                h, w, _ = frame.shape
                
                # Convert to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_frame)
                
                # Initialize default values
                features = None
                coords = None
                analysis = None
                
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    
                    try:
                        # Extract features
                        features, coords = extract_comprehensive_features(landmarks, (h, w, 3))
                        
                        if features and coords:
                            # Detect and smooth exercise type
                            detected_exercise = detect_exercise_type(features, coords)
                            self.smooth_exercise_detection(detected_exercise)
                            
                            # Analyze form
                            analysis = analyze_form_quality(self.current_exercise, features, coords)
                            
                            # Update rep counting
                            self.update_rep_count(features)
                            
                            # Update coach
                            current_time = time.time()
                            if current_time - self.last_coaching_time > self.coaching_interval:
                                self.update_coach(
                                    form_score=analysis.get('overall_score', 0),
                                    features=features,
                                    issues=analysis.get('issues', []),
                                    recommendations=analysis.get('recommendations', [])
                                )
                                self.last_coaching_time = current_time
                            
                            # Track form scores
                            form_score = analysis.get('overall_score', 0)
                            self.form_scores.append(form_score)
                            self.last_form_score = form_score
                            
                            # Draw landmarks
                            if self.show_landmarks:
                                self.drawing.draw_landmarks(
                                    frame, 
                                    results.pose_landmarks, 
                                    mp.solutions.pose.POSE_CONNECTIONS,
                                    mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                    mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2)
                                )
                        
                        else:
                            cv2.putText(frame, "Feature extraction failed", (50, 50), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    except Exception as e:
                        print(f"[ERROR] Processing error: {e}")
                        cv2.putText(frame, f"Processing error: {str(e)[:30]}", (50, 50), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                else:
                    cv2.putText(frame, "No pose detected", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Draw interface (always draw, even without data)
                self.draw_interface(frame, features, analysis)
                
                # Display frame
                cv2.imshow("Integrated Pose Coach", frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('s') and analysis:
                    self.save_session_data(analysis)
                elif key == ord('r'):
                    self.reset_session()
                elif key == ord('i'):
                    self.show_detailed_info = not self.show_detailed_info
                    print(f"[INFO] Detailed info: {'ON' if self.show_detailed_info else 'OFF'}")
                elif key == ord('l'):
                    self.show_landmarks = not self.show_landmarks
                    print(f"[INFO] Landmarks: {'ON' if self.show_landmarks else 'OFF'}")
                elif key == ord('c'):
                    if self.coach:
                        self.coach.give_specific_tip(self.current_exercise)
                elif key == ord('w'):
                    if self.coach:
                        self.coach.give_workout_summary()
                elif key == ord(' '):
                    self.recording_mode = not self.recording_mode
                    print(f"[INFO] Recording mode: {'ON' if self.recording_mode else 'OFF'}")
                
                self.frame_count += 1
                
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user")
        
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            traceback.print_exc()
        
        finally:
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()
            
            # Final workout summary
            if self.coach and len(self.form_scores) > 0:
                try:
                    self.coach.give_workout_summary()
                except Exception as e:
                    print(f"[ERROR] Failed to give workout summary: {e}")
            
            if self.coach:
                self.coach.cleanup()
            
            print("[INFO] Pose tracking stopped")


def main():
    """Main function to run the integrated pose coach"""
    print("=== Integrated Pose Tracking Fitness Coach ===")
    print("Initializing system...")
    
    try:
        # Create and run the integrated coach
        coach = IntegratedPoseCoach(voice_enabled=True, camera_id=0)
        coach.run()
    
    except KeyboardInterrupt:
        print("\n[INFO] Application interrupted by user")
    
    except Exception as e:
        print(f"[ERROR] Failed to start application: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()