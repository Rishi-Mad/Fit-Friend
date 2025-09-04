import time
import random
import numpy as np
from collections import deque
import threading
import queue
try:
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("[WARNING] pyttsx3 not available. Voice coaching disabled.")

class EnhancedSmartCoach:
    def __init__(self, voice_enabled=True):
        self.voice_enabled = voice_enabled and VOICE_AVAILABLE
        
        # Performance tracking
        self.session_start_time = time.time()
        self.form_history = deque(maxlen=100)  # Last 100 form scores
        self.rep_history = deque(maxlen=50)    # Last 50 reps with timestamps
        self.exercise_history = deque(maxlen=20)  # Exercise type history
        
        # Coaching state
        self.current_exercise = "unknown"
        self.coaching_mode = "encouragement"  # encouragement, correction, rest
        self.last_coaching_time = 0
        self.coaching_interval = 5  # Minimum seconds between coaching
        
        # Fatigue and rest management
        self.fatigue_detected = False
        self.rest_recommended = False
        self.rest_start_time = None
        self.recommended_rest_duration = 60  # Default 60 seconds
        
        # Voice system
        if self.voice_enabled:
            self.voice_engine = pyttsx3.init()
            self.setup_voice()
            
        # Message queue for non-blocking voice
        self.voice_queue = queue.Queue()
        self.voice_thread = None
        if self.voice_enabled:
            self.start_voice_thread()
        
        # Exercise-specific coaching knowledge
        self.exercise_tips = {
            "squat": {
                "form_tips": [
                    "Keep your chest up and core engaged",
                    "Push through your heels",
                    "Don't let knees cave inward",
                    "Sit back like you're sitting in a chair",
                    "Keep your weight centered"
                ],
                "common_issues": {
                    "knee_angle": "Focus on proper depth - thighs parallel to ground",
                    "torso_lean": "Keep chest up, don't lean forward",
                    "knee_symmetry": "Keep knees aligned with toes",
                    "foot_distance": "Adjust stance to shoulder width"
                },
                "encouragement": [
                    "Strong squats! Keep it up!",
                    "Great depth on that one!",
                    "Perfect form - you're crushing it!",
                    "Feel those glutes working!"
                ]
            },
            "bicep_curl": {
                "form_tips": [
                    "Keep elbows at your sides",
                    "Control the negative portion",
                    "Don't swing the weights",
                    "Focus on the bicep contraction",
                    "Keep your core tight"
                ],
                "common_issues": {
                    "elbow_angle": "Control the range of motion",
                    "torso_lean": "Stand straight, no leaning",
                    "velocity": "Slow down - control the weight"
                },
                "encouragement": [
                    "Nice controlled movement!",
                    "Feel that bicep burn!",
                    "Excellent form on those curls!",
                    "Keep that control!"
                ]
            },
            "push_up": {
                "form_tips": [
                    "Keep body in straight line",
                    "Lower chest to ground",
                    "Push through your palms",
                    "Keep core engaged",
                    "Don't let hips sag"
                ],
                "common_issues": {
                    "spine_angle": "Keep that plank position strong",
                    "elbow_angle": "Go deeper - chest to ground",
                    "symmetry": "Keep body aligned"
                },
                "encouragement": [
                    "Strong push-ups!",
                    "Perfect plank position!",
                    "You're getting stronger!",
                    "Great upper body work!"
                ]
            }
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            "excellent": 90,
            "good": 75,
            "needs_improvement": 60,
            "poor": 40
        }
        
        print("[INFO] Enhanced Smart Coach initialized")
    
    def setup_voice(self):
        """Configure voice engine settings"""
        if not self.voice_enabled:
            return
            
        voices = self.voice_engine.getProperty('voices')
        if voices:
            # Try to find a clear voice
            for voice in voices:
                if 'english' in voice.name.lower():
                    self.voice_engine.setProperty('voice', voice.id)
                    break
        
        # Set speech rate and volume
        self.voice_engine.setProperty('rate', 180)  # Words per minute
        self.voice_engine.setProperty('volume', 0.9)
    
    def start_voice_thread(self):
        """Start background thread for voice coaching"""
        if not self.voice_enabled:
            return
            
        def voice_worker():
            while True:
                try:
                    message = self.voice_queue.get(timeout=1)
                    if message == "STOP":
                        break
                    self.voice_engine.say(message)
                    self.voice_engine.runAndWait()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[ERROR] Voice system error: {e}")
        
        self.voice_thread = threading.Thread(target=voice_worker, daemon=True)
        self.voice_thread.start()
    
    def update(self, form_score, rep_count, exercise_type="unknown", features=None, issues=None, recommendations=None):
        """Main update method called from pose tracker"""
        current_time = time.time()
        
        # Update tracking data
        self.form_history.append((current_time, form_score))
        self.current_exercise = exercise_type
        self.exercise_history.append(exercise_type)
        
        # Track reps
        if hasattr(self, 'last_rep_count'):
            if rep_count > self.last_rep_count:
                self.rep_history.append(current_time)
        self.last_rep_count = rep_count
        
        # Analyze performance and provide coaching
        self.analyze_performance(form_score, rep_count, features, issues, recommendations)
        
        # Check if coaching is needed
        if current_time - self.last_coaching_time > self.coaching_interval:
            self.provide_coaching(form_score, rep_count, issues, recommendations)
            self.last_coaching_time = current_time
    
    def analyze_performance(self, form_score, rep_count, features, issues, recommendations):
        """Analyze current performance and detect patterns"""
        current_time = time.time()
        
        # Analyze form trend
        if len(self.form_history) >= 10:
            recent_scores = [score for _, score in list(self.form_history)[-10:]]
            avg_recent_form = np.mean(recent_scores)
            form_trend = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
            
            # Detect fatigue
            if avg_recent_form < 60 and form_trend < -2:
                self.fatigue_detected = True
            elif avg_recent_form > 75 and form_trend > 1:
                self.fatigue_detected = False
        
        # Analyze rep rate
        if len(self.rep_history) >= 5:
            recent_reps = [t for t in self.rep_history if current_time - t < 60]
            rep_rate = len(recent_reps)  # Reps per minute
            
            # Detect if going too fast
            if rep_rate > 20:  # More than 20 reps per minute
                self.coaching_mode = "slow_down"
            elif rep_rate < 5 and rep_count > 5:  # Less than 5 reps per minute after 5 reps
                self.coaching_mode = "encouragement"
        
        # Detect rest needs
        session_duration = current_time - self.session_start_time
        if (self.fatigue_detected or rep_count >= 15) and not self.rest_recommended:
            self.rest_recommended = True
            self.rest_start_time = current_time
    
    def provide_coaching(self, form_score, rep_count, issues, recommendations):
        """Provide intelligent coaching based on current state"""
        
        # Rest coaching
        if self.rest_recommended and self.rest_start_time:
            rest_duration = time.time() - self.rest_start_time
            if rest_duration < self.recommended_rest_duration:
                if rest_duration < 5:  # Just started rest
                    self.say_coaching("Take a breather. You've earned it!")
                return
            else:
                self.rest_recommended = False
                self.rest_start_time = None
                self.say_coaching("Rest complete! Ready for more?")
                return
        
        # Form-based coaching
        if form_score < self.performance_thresholds["poor"]:
            self.provide_correction_coaching(issues, recommendations)
        elif form_score < self.performance_thresholds["needs_improvement"]:
            self.provide_improvement_coaching(issues, recommendations)
        elif form_score > self.performance_thresholds["excellent"]:
            self.provide_encouragement_coaching()
        else:
            # Good form - occasional encouragement
            if random.random() < 0.1:  # 10% chance
                self.provide_encouragement_coaching()
    
    def provide_correction_coaching(self, issues, recommendations):
        """Provide specific form corrections"""
        if not issues or not recommendations:
            self.say_coaching("Focus on your form. Slow down if needed.")
            return
        
        # Prioritize the most important issue
        primary_issue = issues[0] if issues else "form"
        primary_recommendation = recommendations[0] if recommendations else "focus on proper technique"
        
        # Get exercise-specific advice
        if self.current_exercise in self.exercise_tips:
            exercise_tips = self.exercise_tips[self.current_exercise]
            
            # Find specific advice for the issue
            specific_advice = None
            for issue_key, advice in exercise_tips["common_issues"].items():
                if issue_key in primary_issue.lower():
                    specific_advice = advice
                    break
            
            if specific_advice:
                self.say_coaching(specific_advice)
            else:
                self.say_coaching(primary_recommendation)
        else:
            self.say_coaching(primary_recommendation)
    
    def provide_improvement_coaching(self, issues, recommendations):
        """Provide coaching for moderate form issues"""
        messages = [
            "Good effort! Let's fine-tune that form.",
            "You're on the right track. Small adjustments needed.",
            "Almost there! Focus on the details."
        ]
        
        if recommendations:
            # Combine encouragement with specific advice
            encouragement = random.choice(messages)
            advice = recommendations[0]
            full_message = f"{encouragement} {advice}"
            self.say_coaching(full_message)
        else:
            self.say_coaching(random.choice(messages))
    
    def provide_encouragement_coaching(self):
        """Provide positive reinforcement for good form"""
        if self.current_exercise in self.exercise_tips:
            encouragements = self.exercise_tips[self.current_exercise]["encouragement"]
            message = random.choice(encouragements)
        else:
            general_encouragements = [
                "Excellent form! Keep it up!",
                "You're crushing it!",
                "Perfect technique!",
                "That's how it's done!",
                "Strong work!"
            ]
            message = random.choice(general_encouragements)
        
        self.say_coaching(message)
    
    def get_performance_summary(self):
        """Get a summary of the current workout session"""
        if not self.form_history:
            return "No data available yet."
        
        # Calculate statistics
        all_scores = [score for _, score in self.form_history]
        avg_form = np.mean(all_scores)
        total_reps = len(self.rep_history)
        session_duration = time.time() - self.session_start_time
        
        # Rep rate
        rep_rate = (total_reps / session_duration) * 60 if session_duration > 0 else 0
        
        # Form trend
        if len(all_scores) >= 5:
            recent_scores = all_scores[-5:]
            form_trend = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
            trend_description = "improving" if form_trend > 0 else "declining" if form_trend < -1 else "stable"
        else:
            trend_description = "stable"
        
        # Performance level
        if avg_form >= self.performance_thresholds["excellent"]:
            performance_level = "excellent"
        elif avg_form >= self.performance_thresholds["good"]:
            performance_level = "good"
        elif avg_form >= self.performance_thresholds["needs_improvement"]:
            performance_level = "needs improvement"
        else:
            performance_level = "poor"
        
        summary = {
            "session_duration": session_duration / 60,  # in minutes
            "total_reps": total_reps,
            "average_form_score": avg_form,
            "rep_rate": rep_rate,
            "form_trend": trend_description,
            "performance_level": performance_level,
            "primary_exercise": max(set(self.exercise_history), key=self.exercise_history.count) if self.exercise_history else "unknown"
        }
        
        return summary
    
    def give_workout_summary(self):
        """Provide end-of-workout summary and advice"""
        summary = self.get_performance_summary()
        
        message = f"Great workout! You completed {summary['total_reps']} reps "
        message += f"with {summary['performance_level']} form. "
        
        if summary['form_trend'] == "improving":
            message += "Your form improved during the session - excellent progress!"
        elif summary['form_trend'] == "declining":
            message += "Form declined toward the end - consider shorter sets or more rest."
        else:
            message += "You maintained consistent form throughout."
        
        self.say_coaching(message)
        
        # Provide specific advice based on performance
        if summary['performance_level'] == "excellent":
            self.say_coaching("Outstanding work! You're ready for more challenging variations.")
        elif summary['performance_level'] == "good":
            self.say_coaching("Solid session! Focus on consistency for continued improvement.")
        elif summary['performance_level'] == "needs improvement":
            self.say_coaching("Good effort! Practice with lighter weights or fewer reps to master the form.")
        else:
            self.say_coaching("Remember, quality over quantity. Focus on perfect form first.")
    
    def say_coaching(self, message):
        """Send coaching message to voice system"""
        print(f"[COACH] {message}")
        
        if self.voice_enabled:
            try:
                self.voice_queue.put(message, timeout=1)
            except queue.Full:
                print("[WARNING] Voice queue full, skipping message")
    
    def give_specific_tip(self, exercise_type=None):
        """Give a specific tip for the current or specified exercise"""
        target_exercise = exercise_type or self.current_exercise
        
        if target_exercise in self.exercise_tips:
            tips = self.exercise_tips[target_exercise]["form_tips"]
            tip = random.choice(tips)
            self.say_coaching(f"Pro tip: {tip}")
        else:
            general_tips = [
                "Focus on controlled movements",
                "Quality over quantity always",
                "Breathe properly during each rep",
                "Engage your core throughout",
                "Listen to your body"
            ]
            tip = random.choice(general_tips)
            self.say_coaching(f"Remember: {tip}")
    
    def reset_session(self):
        """Reset for a new workout session"""
        self.session_start_time = time.time()
        self.form_history.clear()
        self.rep_history.clear()
        self.exercise_history.clear()
        self.fatigue_detected = False
        self.rest_recommended = False
        self.rest_start_time = None
        self.coaching_mode = "encouragement"
        self.last_rep_count = 0
        
        self.say_coaching("New session started! Let's make it count!")
    
    def cleanup(self):
        """Clean up resources"""
        if self.voice_enabled and self.voice_thread:
            self.voice_queue.put("STOP")
            self.voice_thread.join(timeout=2)
        
        print("[INFO] Smart Coach cleanup completed")

# Backward compatibility - wrapper for original SmartCoach interface
class SmartCoach(EnhancedSmartCoach):
    """Backward compatible wrapper for the original SmartCoach interface"""
    
    def __init__(self):
        super().__init__()
        self.set_start_time = self.session_start_time
        self.last_form_score = 100
        self.resting = False
        self.rest_start = None
        
        # Original tips for compatibility
        self.tips = [
            "Keep your core tight!",
            "Don't rush the movement.",
            "Widen your stance a bit.",
            "Great job! Keep going!",
            "Focus on form, not speed."
        ]
    
    def update(self, form_score, reps):
        """Original update method signature for backward compatibility"""
        # Map to enhanced update method
        super().update(form_score, reps, self.current_exercise)
        
        # Update legacy attributes
        self.last_form_score = form_score
        
        # Legacy rest detection
        if self.rest_recommended and not self.resting:
            self.resting = True
            self.rest_start = time.time()
        elif not self.rest_recommended and self.resting:
            self.resting = False
            self.rest_start = None
    
    def give_tip(self):
        """Original give_tip method for backward compatibility"""
        tip = random.choice(self.tips)
        self.say_coaching(tip)
    
    def say(self, message):
        """Original say method for backward compatibility"""
        self.say_coaching(message)

# Usage example
if __name__ == "__main__":
    # Example usage with the enhanced coach
    coach = EnhancedSmartCoach(voice_enabled=True)
    
    # Simulate a workout session
    import time
    
    # Simulate form scores and reps over time
    for i in range(20):
        # Simulate declining form due to fatigue
        form_score = max(100 - i * 3 + random.randint(-10, 10), 30)
        rep_count = i
        
        # Simulate some common issues
        issues = []
        recommendations = []
        
        if form_score < 70:
            issues.append("knee_angle too shallow")
            recommendations.append("Go deeper in your squat")
        
        if form_score < 50:
            issues.append("torso_lean excessive")
            recommendations.append("Keep your chest up")
        
        # Update coach
        coach.update(
            form_score=form_score,
            rep_count=rep_count,
            exercise_type="squat",
            issues=issues,
            recommendations=recommendations
        )
        
        time.sleep(2)  # Simulate time between reps
    
    # Get workout summary
    summary = coach.get_performance_summary()
    print(f"\nWorkout Summary: {summary}")
    
    # Give final coaching
    coach.give_workout_summary()
    
    # Cleanup
    coach.cleanup()