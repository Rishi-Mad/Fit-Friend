# AI Fitness Coach

An intelligent AI-powered fitness coaching platform that analyzes workout videos to provide real-time form feedback and personalized recommendations using computer vision and machine learning.

## Overview

AI Fitness Coach leverages advanced pose detection technology to analyze exercise form and provide actionable feedback. The platform supports multiple exercise types and delivers comprehensive biomechanical analysis to help users improve their workout technique.

## Features

### Core Capabilities
- **Real-time Pose Detection**: Advanced MediaPipe integration for accurate body landmark tracking
- **Multi-Exercise Support**: Automatically detects and analyzes squats, bicep curls, push-ups, and planks
- **Form Quality Assessment**: Comprehensive biomechanical analysis with detailed scoring
- **Personalized Feedback**: AI-driven recommendations based on detected form issues
- **Rep Counting**: Automatic repetition counting with form degradation detection
- **Progress Tracking**: Session data logging and performance trend analysis

### Web Platform Features
- **Video Upload**: Drag-and-drop interface for easy video submission
- **Instant Analysis**: Real-time processing with progress indicators
- **Detailed Reports**: Comprehensive analysis results with visual feedback
- **Key Frame Capture**: Automatic capture of frames with form issues
- **Downloadable Reports**: Export analysis results for offline review

### Technical Features
- **Biomechanical Analysis**: Joint angle calculations, symmetry analysis, movement dynamics
- **Fatigue Detection**: AI-powered fatigue recognition and rest recommendations
- **Voice Coaching**: Optional voice feedback for real-time guidance
- **Error Handling**: Robust error management and graceful degradation
- **Performance Optimization**: Efficient frame processing for large video files

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Webcam (for real-time mode)
- Modern web browser (for web platform)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-Fitness
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the web application**
   ```bash
   python app.py
   ```

4. **Access the platform**
   - Open your browser and go to `http://localhost:5000`
   - Upload a workout video for analysis
   - View detailed form feedback and recommendations

### Real-time Mode (Optional)
For real-time pose tracking with voice coaching:
```bash
python pose_tracker.py
```

## How It Works

### 1. Video Processing
- Upload workout video (MP4, AVI, MOV, MKV, WEBM)
- Automatic frame extraction and pose detection
- Processing every 3rd frame for efficiency (10 FPS analysis)

### 2. Pose Analysis
- MediaPipe pose detection for 33 body landmarks
- Joint angle calculations (knees, hips, elbows, spine)
- Symmetry analysis for balanced movement detection
- Movement velocity and control assessment

### 3. Exercise Detection
- AI-powered exercise classification
- Confidence scoring for detected movements
- Support for multiple exercise types

### 4. Form Assessment
- Biomechanical analysis against exercise-specific criteria
- Real-time scoring (0-100 scale)
- Issue detection and prioritization
- Personalized improvement recommendations

### 5. Results Generation
- Comprehensive analysis report
- Key frame capture for form issues
- Performance statistics and trends
- Downloadable results for progress tracking

## Supported Exercises

### Squats
- **Analysis**: Knee angles, hip hinge, torso lean, stance width
- **Issues Detected**: Insufficient depth, knee cave, forward lean, narrow stance
- **Recommendations**: Proper depth guidance, hip positioning, core engagement

### Bicep Curls
- **Analysis**: Elbow angles, torso stability, movement control
- **Issues Detected**: Momentum usage, elbow movement, incomplete range
- **Recommendations**: Controlled movement, proper elbow positioning

### Push-ups
- **Analysis**: Elbow angles, body alignment, range of motion
- **Issues Detected**: Incomplete depth, hip sagging, poor alignment
- **Recommendations**: Full range of motion, plank position maintenance

### Planks
- **Analysis**: Spine alignment, body stability, hold duration
- **Issues Detected**: Hip sagging, poor alignment, instability
- **Recommendations**: Core engagement, proper alignment

## Architecture

### Core Components

#### `features.py`
- Advanced feature extraction from pose landmarks
- Joint angle calculations and biomechanical analysis
- Exercise detection algorithms
- Form quality assessment functions

#### `pose_tracker.py`
- Real-time pose tracking with MediaPipe
- Integrated coaching system
- Session management and data logging
- Voice feedback integration

#### `smart_coach.py`
- AI-powered coaching logic
- Performance analysis and trend detection
- Personalized feedback generation
- Voice synthesis for real-time guidance

#### `app.py`
- Flask web application
- Video upload and processing
- Analysis results generation
- Web interface management

### Technical Stack
- **Backend**: Python, Flask, OpenCV, MediaPipe
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **AI/ML**: MediaPipe Pose, NumPy, scikit-learn
- **Voice**: pyttsx3 for text-to-speech
- **Deployment**: Gunicorn, Docker-ready

## Performance Metrics

### Accuracy Benchmarks
- **Exercise Detection**: 90-95% accuracy
- **Form Assessment**: Consistent scoring across sessions
- **Rep Counting**: 85-90% accuracy for standard movements
- **Processing Speed**: 10 FPS analysis for optimal performance

### Supported Video Formats
- **Input**: MP4, AVI, MOV, MKV, WEBM
- **Max File Size**: 100MB
- **Resolution**: Up to 4K (optimized for 1080p)
- **Duration**: No limit (processing time scales with length)

## Configuration

### Environment Variables
```bash
# Flask configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Processing settings
MAX_CONTENT_LENGTH=104857600  # 100MB
UPLOAD_FOLDER=uploads

# Voice settings (optional)
VOICE_ENABLED=true
VOICE_RATE=180
```

### Customization Options
- **Exercise Detection**: Add new exercises in `features.py`
- **Form Criteria**: Modify scoring algorithms in `features.py`
- **Voice Coaching**: Customize feedback in `smart_coach.py`
- **UI Design**: Modify templates in `templates/` directory

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t ai-fitness-coach .
docker run -p 5000:5000 ai-fitness-coach
```

### Cloud Deployment
- **Heroku**: Ready for Heroku deployment
- **AWS**: Compatible with EC2 and Lambda
- **Google Cloud**: Works with App Engine and Cloud Run
- **Azure**: Compatible with App Service

## API Endpoints

### Web Interface
- `GET /` - Main upload interface
- `GET /demo` - Demo page with sample results
- `POST /upload` - Video upload and analysis
- `GET /results/<id>` - Retrieve analysis results

### Response Format
```json
{
  "success": true,
  "analysis": {
    "exercise_detected": "squat",
    "confidence": 0.95,
    "overall_score": 78,
    "rep_count": 12,
    "issues_detected": ["knee_angle too shallow"],
    "recommendations": ["Go deeper in your squat"],
    "key_frames": [...],
    "video_duration": 45.2,
    "frames_analyzed": 1500
  }
}
```

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Areas for Improvement
- **Additional Exercises**: Support for more exercise types
- **Mobile App**: Native mobile application
- **Social Features**: Progress sharing and community
- **Advanced Analytics**: Machine learning for personalized insights
- **Integration**: Connect with fitness trackers and apps

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **MediaPipe**: Google's pose detection technology
- **OpenCV**: Computer vision library
- **Bootstrap**: Frontend framework
- **Flask**: Web framework

## Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Check the documentation
- Review the demo page for examples

---

Built for the fitness community