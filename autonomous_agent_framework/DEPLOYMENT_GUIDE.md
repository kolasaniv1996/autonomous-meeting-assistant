# Deployment Guide

This guide covers different deployment options for the Autonomous Agent Framework, from local development to production environments.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Configuration Management](#configuration-management)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

## Local Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Access to Jira, GitHub, and Confluence APIs

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd autonomous_agent_framework
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your API credentials
   ```

5. **Configure Agents**
   ```bash
   cp config/agent_config.yaml config/my_config.yaml
   # Edit my_config.yaml with your employee information
   ```

6. **Verify Installation**
   ```bash
   python tests/verify_framework.py
   ```

7. **Run Demo**
   ```bash
   python examples/demo_vivek.py
   ```

### Development Workflow

1. **Make Changes**: Edit framework code
2. **Test Changes**: Run verification script
3. **Test Integration**: Run demo with your changes
4. **Commit Changes**: Use git for version control

## Docker Deployment

### Quick Start with Docker

1. **Build the Image**
   ```bash
   docker build -t autonomous-agent-framework .
   ```

2. **Run with Docker Compose**
   ```bash
   # Copy environment template
   cp .env.template .env
   # Edit .env with your credentials
   
   # Start the services
   docker-compose up -d
   ```

3. **View Logs**
   ```bash
   docker-compose logs -f autonomous-agent
   ```

4. **Stop Services**
   ```bash
   docker-compose down
   ```

### Custom Docker Configuration

#### Dockerfile Customization

```dockerfile
# Custom Dockerfile for specific requirements
FROM python:3.11-slim

# Install additional system packages
RUN apt-get update && apt-get install -y \
    your-additional-packages \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set custom environment variables
ENV CUSTOM_VAR=value

# Custom startup command
CMD ["python", "your_custom_script.py"]
```

#### Docker Compose Override

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'

services:
  autonomous-agent:
    volumes:
      # Mount local code for development
      - .:/app
    environment:
      # Override environment variables
      - LOG_LEVEL=DEBUG
    ports:
      # Expose additional ports
      - "8001:8001"
```

### Multi-Stage Build for Production

```dockerfile
# Multi-stage build for smaller production image
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim as production

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . /app
WORKDIR /app

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

CMD ["python", "examples/demo_vivek.py"]
```

## Production Deployment

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB
- **Network**: Stable internet connection

#### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **Network**: High-speed internet with low latency

### Production Setup

1. **Server Preparation**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install required packages
   sudo apt install -y python3.11 python3.11-venv git nginx supervisor
   
   # Create application user
   sudo useradd -m -s /bin/bash agentuser
   sudo usermod -aG sudo agentuser
   ```

2. **Application Deployment**
   ```bash
   # Switch to application user
   sudo su - agentuser
   
   # Clone repository
   git clone <repository-url> /home/agentuser/autonomous_agent_framework
   cd /home/agentuser/autonomous_agent_framework
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration**
   ```bash
   # Copy and configure environment
   cp .env.template .env
   # Edit .env with production credentials
   
   # Copy and configure agents
   cp config/agent_config.yaml config/production_config.yaml
   # Edit production_config.yaml
   ```

4. **Process Management with Supervisor**

   Create `/etc/supervisor/conf.d/autonomous_agent.conf`:
   ```ini
   [program:autonomous_agent]
   command=/home/agentuser/autonomous_agent_framework/venv/bin/python examples/demo_vivek.py
   directory=/home/agentuser/autonomous_agent_framework
   user=agentuser
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/autonomous_agent.log
   environment=PATH="/home/agentuser/autonomous_agent_framework/venv/bin"
   ```

   Start the service:
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start autonomous_agent
   ```

### Load Balancing and High Availability

#### Nginx Configuration

Create `/etc/nginx/sites-available/autonomous_agent`:
```nginx
upstream autonomous_agent {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;  # Additional instances
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://autonomous_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/autonomous_agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Multiple Instance Setup

Run multiple instances on different ports:
```bash
# Instance 1 on port 8000
PORT=8000 python examples/demo_vivek.py &

# Instance 2 on port 8001
PORT=8001 python examples/demo_vivek.py &
```

## Cloud Deployment

### AWS Deployment

#### EC2 Instance Setup

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (minimum)
   - Security Group: Allow HTTP (80), HTTPS (443), SSH (22)

2. **Install Docker**
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo usermod -aG docker ubuntu
   ```

3. **Deploy Application**
   ```bash
   git clone <repository-url>
   cd autonomous_agent_framework
   
   # Configure environment
   cp .env.template .env
   # Edit .env with AWS-specific settings
   
   # Deploy with Docker Compose
   docker-compose up -d
   ```

#### ECS Deployment

Create `task-definition.json`:
```json
{
  "family": "autonomous-agent-framework",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "autonomous-agent",
      "image": "your-account.dkr.ecr.region.amazonaws.com/autonomous-agent-framework:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "JIRA_TOKEN",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:jira-token"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/autonomous-agent-framework",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### Cloud Run Deployment

1. **Build and Push Image**
   ```bash
   # Build image
   docker build -t gcr.io/your-project/autonomous-agent-framework .
   
   # Push to Container Registry
   docker push gcr.io/your-project/autonomous-agent-framework
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy autonomous-agent-framework \
     --image gcr.io/your-project/autonomous-agent-framework \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars LOG_LEVEL=INFO \
     --set-secrets JIRA_TOKEN=jira-token:latest
   ```

### Azure Deployment

#### Container Instances

```bash
# Create resource group
az group create --name autonomous-agent-rg --location eastus

# Deploy container
az container create \
  --resource-group autonomous-agent-rg \
  --name autonomous-agent-framework \
  --image your-registry/autonomous-agent-framework:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables LOG_LEVEL=INFO \
  --secure-environment-variables JIRA_TOKEN=your-token
```

## Configuration Management

### Environment-Specific Configurations

#### Development
```yaml
# config/development.yaml
api_credentials:
  jira_url: "https://dev-company.atlassian.net"
  # Use development/sandbox APIs

meeting_config:
  max_response_length: 500  # More verbose for debugging
  context_window_days: 3    # Shorter for faster testing

log_level: "DEBUG"
```

#### Staging
```yaml
# config/staging.yaml
api_credentials:
  jira_url: "https://staging-company.atlassian.net"
  # Use staging APIs

meeting_config:
  max_response_length: 200
  context_window_days: 7

log_level: "INFO"
```

#### Production
```yaml
# config/production.yaml
api_credentials:
  jira_url: "https://company.atlassian.net"
  # Use production APIs

meeting_config:
  max_response_length: 150  # Concise for production
  context_window_days: 7

log_level: "WARNING"
```

### Secret Management

#### Using Environment Variables
```bash
# Set secrets as environment variables
export JIRA_TOKEN="your-secret-token"
export GITHUB_TOKEN="your-github-token"
export CONFLUENCE_TOKEN="your-confluence-token"
```

#### Using Docker Secrets
```yaml
# docker-compose.yml
version: '3.8'

services:
  autonomous-agent:
    image: autonomous-agent-framework
    secrets:
      - jira_token
      - github_token
    environment:
      - JIRA_TOKEN_FILE=/run/secrets/jira_token

secrets:
  jira_token:
    file: ./secrets/jira_token.txt
  github_token:
    file: ./secrets/github_token.txt
```

#### Using Kubernetes Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-credentials
type: Opaque
data:
  jira-token: <base64-encoded-token>
  github-token: <base64-encoded-token>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autonomous-agent-framework
spec:
  template:
    spec:
      containers:
      - name: autonomous-agent
        image: autonomous-agent-framework:latest
        env:
        - name: JIRA_TOKEN
          valueFrom:
            secretKeyRef:
              name: api-credentials
              key: jira-token
```

## Monitoring and Logging

### Application Logging

#### Structured Logging Configuration
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'employee_id'):
            log_entry['employee_id'] = record.employee_id
            
        if hasattr(record, 'meeting_id'):
            log_entry['meeting_id'] = record.meeting_id
            
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/autonomous_agent.log')
    ]
)

# Set JSON formatter
for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

### Health Checks

#### Application Health Check
```python
# health_check.py
import asyncio
import sys
from autonomous_agent_framework.config.config_manager import ConfigManager

async def health_check():
    try:
        # Test configuration loading
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Test API connectivity (basic checks)
        # Add specific health checks here
        
        print("Health check passed")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(health_check())
    sys.exit(0 if result else 1)
```

#### Docker Health Check
```dockerfile
# Add to Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python health_check.py || exit 1
```

### Monitoring with Prometheus

#### Metrics Collection
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
MEETINGS_TOTAL = Counter('meetings_total', 'Total number of meetings processed')
MEETING_DURATION = Histogram('meeting_duration_seconds', 'Meeting duration in seconds')
ACTIVE_AGENTS = Gauge('active_agents', 'Number of active agents')
API_REQUESTS = Counter('api_requests_total', 'Total API requests', ['service', 'status'])

class MetricsCollector:
    def __init__(self):
        # Start metrics server
        start_http_server(8001)
    
    def record_meeting_start(self):
        MEETINGS_TOTAL.inc()
    
    def record_meeting_duration(self, duration):
        MEETING_DURATION.observe(duration)
    
    def update_active_agents(self, count):
        ACTIVE_AGENTS.set(count)
    
    def record_api_request(self, service, status):
        API_REQUESTS.labels(service=service, status=status).inc()
```

### Log Aggregation

#### ELK Stack Configuration

**Logstash Configuration** (`logstash.conf`):
```ruby
input {
  file {
    path => "/var/log/autonomous_agent.log"
    start_position => "beginning"
    codec => "json"
  }
}

filter {
  if [level] == "ERROR" {
    mutate {
      add_tag => ["error"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "autonomous-agent-%{+YYYY.MM.dd}"
  }
}
```

**Docker Compose for ELK**:
```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      - /var/log:/var/log:ro
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## Security Considerations

### API Security

1. **Token Management**
   - Use environment variables for API tokens
   - Rotate tokens regularly
   - Use least-privilege access

2. **Network Security**
   - Use HTTPS for all API communications
   - Implement rate limiting
   - Use VPN for internal communications

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use secure communication channels
   - Implement data retention policies

### Container Security

1. **Image Security**
   ```dockerfile
   # Use non-root user
   RUN useradd -m -u 1000 agent
   USER agent
   
   # Remove unnecessary packages
   RUN apt-get remove -y build-essential && apt-get autoremove -y
   
   # Set read-only filesystem
   VOLUME ["/tmp"]
   ```

2. **Runtime Security**
   ```yaml
   # docker-compose.yml
   services:
     autonomous-agent:
       security_opt:
         - no-new-privileges:true
       read_only: true
       tmpfs:
         - /tmp
   ```

### Access Control

#### Role-Based Access Control
```yaml
# rbac.yaml
roles:
  admin:
    permissions:
      - manage_agents
      - view_all_meetings
      - modify_configuration
  
  manager:
    permissions:
      - view_team_meetings
      - create_meetings
      - view_team_status
  
  employee:
    permissions:
      - view_own_meetings
      - update_own_status

users:
  - username: admin
    role: admin
  - username: sarah
    role: manager
    teams: ["backend-team"]
  - username: vivek
    role: employee
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Problem: ModuleNotFoundError
# Solution: Check Python path and virtual environment
export PYTHONPATH=/path/to/autonomous_agent_framework:$PYTHONPATH
source venv/bin/activate
```

#### 2. API Authentication Failures
```bash
# Problem: 401 Unauthorized
# Solution: Verify API tokens and permissions
curl -H "Authorization: Bearer $JIRA_TOKEN" https://your-domain.atlassian.net/rest/api/2/myself
```

#### 3. Memory Issues
```bash
# Problem: Out of memory errors
# Solution: Increase memory limits or optimize context window
docker run -m 4g autonomous-agent-framework
```

#### 4. Network Connectivity
```bash
# Problem: Connection timeouts
# Solution: Check network connectivity and firewall rules
telnet your-domain.atlassian.net 443
```

### Debug Mode

Enable comprehensive debugging:
```python
import logging
import os

# Set debug environment
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['PYTHONPATH'] = '/path/to/framework'

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug.log')
    ]
)
```

### Performance Monitoring

#### Resource Usage Monitoring
```bash
# Monitor container resources
docker stats autonomous-agent-framework

# Monitor system resources
htop
iotop
nethogs
```

#### Application Performance
```python
import time
import psutil
import logging

class PerformanceMonitor:
    def __init__(self):
        self.logger = logging.getLogger('performance')
    
    def monitor_function(self, func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss
            
            result = func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            self.logger.info(f"{func.__name__} took {end_time - start_time:.2f}s, "
                           f"memory delta: {(end_memory - start_memory) / 1024 / 1024:.2f}MB")
            
            return result
        return wrapper
```

### Backup and Recovery

#### Configuration Backup
```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/backup/autonomous_agent/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup configuration files
cp -r config/ $BACKUP_DIR/
cp .env $BACKUP_DIR/

# Backup logs
cp -r logs/ $BACKUP_DIR/

# Create archive
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup created: $BACKUP_DIR.tar.gz"
```

#### Disaster Recovery
```bash
#!/bin/bash
# restore_config.sh

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Extract backup
tar -xzf $BACKUP_FILE

# Restore configuration
BACKUP_DIR=$(basename $BACKUP_FILE .tar.gz)
cp -r $BACKUP_DIR/config/ ./
cp $BACKUP_DIR/.env ./

# Restart services
docker-compose restart

echo "Configuration restored from $BACKUP_FILE"
```

This deployment guide provides comprehensive instructions for deploying the Autonomous Agent Framework in various environments, from local development to production cloud deployments.

