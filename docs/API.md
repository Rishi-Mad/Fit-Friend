# AI Fitness Coach API Documentation

## Overview

The AI Fitness Coach API provides endpoints for analyzing workout videos using computer vision and machine learning. The API can detect exercises, analyze form quality, and provide personalized recommendations.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication. In production, consider implementing API keys or OAuth.

## Endpoints

### 1. Upload and Analyze Video

**POST** `/upload`

Upload a workout video for analysis.

#### Request

- **Content-Type**: `multipart/form-data`
- **Body**: 
  - `video` (file): Video file (MP4, AVI, MOV, MKV, WEBM)
  - Max file size: 100MB

#### Response

```json
{
  "success": true,
  "results_id": "uuid-results-id",
  "analysis": {
    "exercise_detected": "squat",
    "confidence": 0.95,
    "overall_score": 85,
    "rep_count": 12,
    "issues_detected": [
      "knee_angle too shallow",
      "torso_lean excessive"
    ],
    "recommendations": [
      "Go deeper in your squat",
      "Keep your chest up"
    ],
    "key_frames": [
      {
        "frame": 150,
        "score": 65,
        "issues": ["knee_angle too shallow"],
        "image_path": "static/results/key_frame_150.jpg"
      }
    ],
    "video_duration": 45.2,
    "fps": 30,
    "frames_analyzed": 1500,
    "upload_time": "2024-01-15T10:30:00"
  }
}
```

#### Error Response

```json
{
  "error": "Invalid file type. Please upload MP4, AVI, MOV, MKV, or WEBM"
}
```

### 2. Get Analysis Results

**GET** `/results/{results_id}`

Retrieve previously generated analysis results.

#### Parameters

- `results_id` (string): The ID returned from the upload endpoint

#### Response

Returns the same analysis object as the upload endpoint.

#### Error Response

```json
{
  "error": "Results not found"
}
```

### 3. Health Check

**GET** `/health`

Check the health status of the API.

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "mediapipe_available": true,
  "version": "1.0.0"
}
```

### 4. API Documentation

**GET** `/api/docs`

Get detailed API documentation.

#### Response

```json
{
  "title": "AI Fitness Coach API",
  "version": "1.0.0",
  "description": "RESTful API for AI-powered fitness form analysis",
  "endpoints": {
    "POST /upload": {
      "description": "Upload and analyze workout video",
      "parameters": {
        "video": "Video file (MP4, AVI, MOV, MKV, WEBM)"
      },
      "response": "Analysis results with form scores and recommendations"
    }
  }
}
```

## Supported Exercise Types

The API can detect and analyze the following exercises:

1. **Squats**
   - Analyzes knee angles, hip hinge, torso lean, stance width
   - Detects issues like insufficient depth, knee cave, forward lean

2. **Push-ups**
   - Analyzes elbow angles, body alignment, range of motion
   - Detects issues like incomplete depth, hip sagging, poor alignment

3. **Bicep Curls**
   - Analyzes elbow angles, torso stability, movement control
   - Detects issues like momentum usage, elbow movement, incomplete range

4. **Planks**
   - Analyzes spine alignment, body stability, hold duration
   - Detects issues like hip sagging, poor alignment, instability

## Form Scoring

The API provides form scores on a scale of 0-100:

- **90-100**: Excellent form
- **75-89**: Good form with minor issues
- **60-74**: Needs improvement
- **Below 60**: Poor form requiring attention

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid file or parameters |
| 404 | Not Found - Results not found |
| 500 | Internal Server Error - Processing failed |

## Rate Limits

- 100 requests per minute per IP address
- File size limit: 100MB
- Processing time limit: 5 minutes

## Example Usage

### Python

```python
import requests

# Upload video
with open('workout.mp4', 'rb') as video_file:
    response = requests.post(
        'http://localhost:5000/upload',
        files={'video': video_file}
    )

if response.status_code == 200:
    data = response.json()
    print(f"Exercise: {data['analysis']['exercise_detected']}")
    print(f"Score: {data['analysis']['overall_score']}")
    print(f"Reps: {data['analysis']['rep_count']}")
```

### JavaScript

```javascript
const formData = new FormData();
formData.append('video', videoFile);

fetch('http://localhost:5000/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Exercise:', data.analysis.exercise_detected);
    console.log('Score:', data.analysis.overall_score);
    console.log('Reps:', data.analysis.rep_count);
});
```

### cURL

```bash
curl -X POST \
  http://localhost:5000/upload \
  -F "video=@workout.mp4"
```

## Web Interface

The API also provides a web interface at the root URL (`/`) for easy testing and demonstration.

## Support

For questions or issues, please create an issue on the GitHub repository.
