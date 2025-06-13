# Deployment Guide

## Overview

This guide covers different deployment options for the Autonomous Agent Framework Web Interface, from local development to production deployment.

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)
- Git

## Local Development

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd autonomous-agent-web-interface
   ```

2. **Set up environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your credentials
   ```

3. **Run with Docker Compose:**
   ```bash
   ./deploy.sh
   ```

### Manual Setup

#### Backend Setup

1. **Navigate to backend:**
   ```bash
   cd agent_web_interface
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   python src/main.py
   ```

#### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd agent-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pnpm install  # or npm install
   ```

3. **Start development server:**
   ```bash
   pnpm run dev  # or npm run dev
   ```

## Docker Deployment

### Development Environment

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Environment

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS

1. **Create ECR repositories:**
   ```bash
   aws ecr create-repository --repository-name agent-backend
   aws ecr create-repository --repository-name agent-frontend
   ```

2. **Build and push images:**
   ```bash
   # Get login token
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Build and tag images
   docker build -t agent-backend ./agent_web_interface
   docker tag agent-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/agent-backend:latest

   docker build -t agent-frontend ./agent-dashboard
   docker tag agent-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/agent-frontend:latest

   # Push images
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/agent-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/agent-frontend:latest
   ```

3. **Create ECS task definition:**
   ```json
   {
     "family": "agent-framework",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/agent-backend:latest",
         "portMappings": [
           {
             "containerPort": 5001,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "FLASK_ENV",
             "value": "production"
           }
         ]
       },
       {
         "name": "frontend",
         "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/agent-frontend:latest",
         "portMappings": [
           {
             "containerPort": 80,
             "protocol": "tcp"
           }
         ]
       }
     ]
   }
   ```

#### Using AWS App Runner

1. **Create apprunner.yaml:**
   ```yaml
   version: 1.0
   runtime: python3.11
   build:
     commands:
       build:
         - pip install -r requirements.txt
   run:
     runtime-version: 3.11
     command: python src/main.py
     network:
       port: 5001
       env: PORT
   ```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and deploy backend:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/agent-backend ./agent_web_interface
   gcloud run deploy agent-backend --image gcr.io/PROJECT-ID/agent-backend --platform managed
   ```

2. **Build and deploy frontend:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/agent-frontend ./agent-dashboard
   gcloud run deploy agent-frontend --image gcr.io/PROJECT-ID/agent-frontend --platform managed
   ```

### Azure Deployment

#### Using Azure Container Instances

1. **Create resource group:**
   ```bash
   az group create --name agent-framework --location eastus
   ```

2. **Deploy containers:**
   ```bash
   az container create \
     --resource-group agent-framework \
     --name agent-backend \
     --image your-registry/agent-backend:latest \
     --ports 5001 \
     --environment-variables FLASK_ENV=production
   ```

## Environment Configuration

### Production Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@db-host:5432/agent_framework

# Security
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production

# API Credentials
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=service-account@company.com
JIRA_API_TOKEN=your-production-token

# Meeting Platforms
TEAMS_APP_ID=production-app-id
TEAMS_APP_SECRET=production-app-secret
TEAMS_TENANT_ID=your-tenant-id

# Speech Processing
AZURE_SPEECH_KEY=production-speech-key
AZURE_SPEECH_REGION=eastus

# Frontend
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_ENVIRONMENT=production
```

### SSL/TLS Configuration

#### Using Let's Encrypt with Nginx

1. **Install Certbot:**
   ```bash
   sudo apt-get update
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. **Obtain certificate:**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Update nginx configuration:**
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       location / {
           proxy_pass http://frontend:3000;
       }
       
       location /api {
           proxy_pass http://backend:5001;
       }
   }
   ```

## Database Setup

### PostgreSQL (Recommended for Production)

1. **Install PostgreSQL:**
   ```bash
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **Create database and user:**
   ```sql
   CREATE DATABASE agent_framework;
   CREATE USER agent_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE agent_framework TO agent_user;
   ```

3. **Update connection string:**
   ```bash
   DATABASE_URL=postgresql://agent_user:secure_password@localhost:5432/agent_framework
   ```

### MySQL Alternative

```bash
# Install MySQL
sudo apt-get install mysql-server

# Create database
mysql -u root -p
CREATE DATABASE agent_framework;
CREATE USER 'agent_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON agent_framework.* TO 'agent_user'@'localhost';

# Connection string
DATABASE_URL=mysql://agent_user:secure_password@localhost:3306/agent_framework
```

## Monitoring and Logging

### Application Monitoring

1. **Health Check Endpoints:**
   ```python
   @app.route('/health')
   def health_check():
       return {'status': 'healthy', 'timestamp': datetime.utcnow()}
   ```

2. **Prometheus Metrics:**
   ```python
   from prometheus_client import Counter, Histogram, generate_latest
   
   REQUEST_COUNT = Counter('requests_total', 'Total requests')
   REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')
   ```

### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

if app.config['ENV'] == 'production':
    file_handler = RotatingFileHandler('logs/agent_framework.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

## Security Considerations

### Production Security Checklist

- [ ] Use HTTPS in production
- [ ] Set secure session cookies
- [ ] Implement rate limiting
- [ ] Use environment variables for secrets
- [ ] Enable CORS only for trusted domains
- [ ] Implement authentication and authorization
- [ ] Regular security updates
- [ ] Database connection encryption
- [ ] API key rotation policy
- [ ] Audit logging

### Example Security Configuration

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Secure headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump -h localhost -U agent_user agent_framework > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U agent_user agent_framework > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### Application Data Backup

```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

## Troubleshooting

### Common Deployment Issues

1. **Port conflicts:**
   ```bash
   # Check what's using the port
   sudo netstat -tlnp | grep :5001
   
   # Kill process if needed
   sudo kill -9 <PID>
   ```

2. **Permission issues:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER /path/to/app
   chmod +x deploy.sh
   ```

3. **Database connection issues:**
   ```bash
   # Test database connection
   psql -h localhost -U agent_user -d agent_framework -c "SELECT 1;"
   ```

4. **Memory issues:**
   ```bash
   # Check memory usage
   free -h
   
   # Increase swap if needed
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Performance Optimization

1. **Enable gzip compression:**
   ```nginx
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   ```

2. **Use Redis for caching:**
   ```python
   import redis
   from flask_caching import Cache
   
   cache = Cache(app, config={'CACHE_TYPE': 'redis'})
   ```

3. **Database optimization:**
   ```sql
   -- Add indexes for frequently queried fields
   CREATE INDEX idx_agents_status ON agents(status);
   CREATE INDEX idx_meetings_scheduled_time ON meetings(scheduled_time);
   ```

