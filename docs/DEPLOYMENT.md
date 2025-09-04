# Deployment Guide

This guide covers various deployment options for the AI Fitness Coach application.

## Prerequisites

- Python 3.8 or higher
- Docker (for containerized deployment)
- Git

## Local Development

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-Fitness
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`.

## Docker Deployment

### 1. Build the Docker Image

```bash
docker build -t ai-fitness-coach .
```

### 2. Run the Container

```bash
docker run -p 5000:5000 ai-fitness-coach
```

### 3. Docker Compose (Recommended)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  ai-fitness-coach:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key-here
    volumes:
      - ./uploads:/app/uploads
      - ./static/results:/app/static/results
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:

```bash
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment

#### Using AWS App Runner

1. **Prepare the application**:
   ```bash
   # Ensure Dockerfile is present
   # Push to GitHub repository
   ```

2. **Create App Runner service**:
   - Go to AWS App Runner console
   - Create new service
   - Connect to GitHub repository
   - Configure build settings:
     - Build command: `docker build -t ai-fitness-coach .`
     - Start command: `gunicorn --bind 0.0.0.0:8000 --workers 4 app:app`
   - Set port to 8000

#### Using AWS EC2

1. **Launch EC2 instance**:
   ```bash
   # Launch Ubuntu 20.04 LTS instance
   # Configure security group to allow HTTP/HTTPS traffic
   ```

2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip docker.io nginx
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Deploy application**:
   ```bash
   git clone <repository-url>
   cd AI-Fitness
   docker build -t ai-fitness-coach .
   docker run -d -p 5000:5000 --name ai-fitness ai-fitness-coach
   ```

4. **Configure Nginx**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and push to Container Registry**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/ai-fitness-coach
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy ai-fitness-coach \
     --image gcr.io/PROJECT-ID/ai-fitness-coach \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Azure Deployment

#### Using Azure Container Instances

1. **Build and push to Azure Container Registry**:
   ```bash
   az acr build --registry myregistry --image ai-fitness-coach .
   ```

2. **Deploy to Container Instances**:
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name ai-fitness-coach \
     --image myregistry.azurecr.io/ai-fitness-coach \
     --ports 5000 \
     --dns-name-label ai-fitness-coach
   ```

## Production Configuration

### Environment Variables

Create a `.env` file for production:

```bash
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=postgresql://user:password@localhost/fitness_coach
REDIS_URL=redis://localhost:6379/0
MAX_CONTENT_LENGTH=104857600
UPLOAD_FOLDER=uploads
LOG_LEVEL=INFO
```

### Security Considerations

1. **Use HTTPS**: Always use SSL/TLS in production
2. **Secure Secret Key**: Use a strong, random secret key
3. **File Upload Limits**: Configure appropriate file size limits
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Input Validation**: Validate all user inputs
6. **Error Handling**: Don't expose sensitive information in errors

### Performance Optimization

1. **Use Gunicorn**: For production WSGI server
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
   ```

2. **Enable Caching**: Use Redis for session storage and caching
3. **CDN**: Use a CDN for static assets
4. **Load Balancing**: Use multiple application instances behind a load balancer

### Monitoring and Logging

1. **Application Logs**: Configure structured logging
2. **Health Checks**: Implement health check endpoints
3. **Metrics**: Monitor CPU, memory, and response times
4. **Error Tracking**: Use services like Sentry for error tracking

## Scaling Considerations

### Horizontal Scaling

- Use multiple application instances
- Implement load balancing
- Use shared storage for uploaded files
- Implement session storage (Redis)

### Vertical Scaling

- Increase CPU and memory resources
- Optimize MediaPipe configuration
- Use GPU acceleration if available

## Backup and Recovery

1. **Database Backups**: Regular database backups
2. **File Backups**: Backup uploaded files and results
3. **Configuration Backups**: Version control for configuration files
4. **Disaster Recovery**: Plan for disaster recovery scenarios

## Maintenance

### Regular Tasks

1. **Update Dependencies**: Keep dependencies updated
2. **Security Patches**: Apply security patches promptly
3. **Monitor Performance**: Regular performance monitoring
4. **Clean Up**: Regular cleanup of temporary files

### Updates

1. **Blue-Green Deployment**: Use blue-green deployment for zero-downtime updates
2. **Rolling Updates**: For containerized deployments
3. **Database Migrations**: Plan for database schema changes

## Troubleshooting

### Common Issues

1. **MediaPipe Installation**: Ensure proper system dependencies
2. **Memory Issues**: Monitor memory usage during video processing
3. **File Upload Issues**: Check file size limits and permissions
4. **Performance Issues**: Monitor CPU usage and optimize accordingly

### Logs

Check application logs for errors:

```bash
# Docker logs
docker logs ai-fitness-coach

# Application logs
tail -f logs/fitness_coach.log
```

## Support

For deployment issues, please check the troubleshooting section or create an issue on GitHub.
