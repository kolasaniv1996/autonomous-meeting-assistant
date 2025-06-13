<<<<<<< HEAD
# Autonomous Agent Framework - Web Interface

A comprehensive web interface for managing the autonomous agent framework, providing user-friendly configuration, agent management, and meeting control capabilities.

## 🎯 Overview

This web interface provides a complete dashboard for managing autonomous agents that can attend meetings, extract context from Jira/GitHub/Confluence, and automate meeting participation with real-time speech processing.

## 🏗️ Architecture

The web interface consists of two main components:

### Backend (Flask API)
- **RESTful API** for all data operations
- **SQLite Database** for persistent storage
- **CORS Support** for cross-origin requests
- **Comprehensive Error Handling**

### Frontend (React Dashboard)
- **Modern React 18** with hooks
- **Responsive Design** with Tailwind CSS
- **Professional UI Components** with shadcn/ui
- **Real-time Updates** and state management

## 📁 Project Structure

```
autonomous-agent-web-interface/
├── agent_web_interface/          # Flask Backend
│   ├── src/
│   │   ├── main.py              # Main Flask application
│   │   ├── models/              # Database models
│   │   └── routes/              # API route handlers
│   ├── requirements.txt         # Python dependencies
│   └── venv/                    # Virtual environment
├── agent-dashboard/             # React Frontend
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Main application pages
│   │   └── utils/               # Utility functions
│   ├── package.json             # Node.js dependencies
│   └── dist/                    # Production build
├── autonomous_agent_framework/  # Core Agent Framework
│   ├── agents/                  # Agent implementations
│   ├── api_connectors/          # External API integrations
│   ├── meeting_platforms/       # Teams/Google Meet integration
│   ├── speech_processing/       # Speech-to-text services
│   └── examples/                # Demo implementations
└── docs/                        # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- pnpm (recommended) or npm

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd agent_web_interface
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask server:**
   ```bash
   python src/main.py
   ```
   The API will be available at `http://localhost:5001`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd agent-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pnpm install  # or npm install
   ```

3. **Start the development server:**
   ```bash
   pnpm run dev  # or npm run dev
   ```
   The dashboard will be available at `http://localhost:5173`

## 🎨 Features

### Configuration Management
- **Multi-tab Configuration Forms** for API credentials, meeting platforms, and speech processing
- **Template System** for quick configuration setup
- **Validation** with real-time feedback
- **Import/Export** functionality for configuration backup

### Agent Management
- **Complete CRUD Operations** for agent lifecycle management
- **Search and Filter** capabilities across multiple fields
- **Bulk Operations** for managing multiple agents
- **Integration Mapping** for Jira, GitHub, and Confluence usernames

### Meeting Management
- **Meeting Scheduling** with platform selection (Teams/Google Meet)
- **Real-time Meeting Control** (start, stop, pause)
- **Participant Management** with agent assignment
- **Transcript Viewing** and meeting analytics
- **Speech Processing Configuration** (Azure, Google Cloud, Whisper)

### Dashboard Analytics
- **Real-time Statistics** for agents and meetings
- **Status Monitoring** with color-coded indicators
- **Activity Tracking** and performance metrics

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///agent_framework.db

# API Credentials
JIRA_URL=your_jira_instance_url
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_api_token

GITHUB_TOKEN=your_github_token

CONFLUENCE_URL=your_confluence_url
CONFLUENCE_USERNAME=your_username
CONFLUENCE_API_TOKEN=your_api_token

# Meeting Platform Credentials
TEAMS_APP_ID=your_teams_app_id
TEAMS_APP_SECRET=your_teams_app_secret
TEAMS_TENANT_ID=your_tenant_id

# Speech Processing
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region

GOOGLE_CLOUD_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path_to_service_account.json

OPENAI_API_KEY=your_openai_api_key
```

### Frontend Configuration

Update `src/utils/api.js` for production:

```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-api-domain.com/api'
  : 'http://localhost:5001/api'
```

## 📚 API Documentation

### Configuration Endpoints

- `GET /api/configurations` - List all configurations
- `POST /api/configurations` - Create new configuration
- `PUT /api/configurations/{id}` - Update configuration
- `DELETE /api/configurations/{id}` - Delete configuration
- `PUT /api/configurations/{id}/activate` - Activate configuration

### Agent Endpoints

- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `GET /api/agents/stats` - Get agent statistics

### Meeting Endpoints

- `GET /api/meetings` - List all meetings
- `POST /api/meetings` - Schedule new meeting
- `PUT /api/meetings/{id}` - Update meeting
- `DELETE /api/meetings/{id}` - Delete meeting
- `POST /api/meetings/{id}/start` - Start meeting
- `POST /api/meetings/{id}/end` - End meeting
- `GET /api/meetings/stats` - Get meeting statistics

## 🐳 Docker Deployment

### Build and Run with Docker

1. **Build the application:**
   ```bash
   docker-compose build
   ```

2. **Start the services:**
=======
# Autonomous Meeting Assistant

A comprehensive autonomous meeting assistant with Flask backend and React frontend that provides multi-platform meeting integration, agent management, and automated meeting participation.

## Features

- **Multi-platform Meeting Integration**: Support for Microsoft Teams, Google Meet, Zoom, and Webex
- **Agent Management**: Create and manage autonomous agents for automated meeting participation
- **Speech Processing**: Real-time transcription and speech-to-text capabilities
- **Integration Support**: Jira, GitHub, and Confluence integration for action item management
- **User Authentication**: JWT-based authentication with role-based access control
- **Configuration Management**: Comprehensive API credential and settings management
- **Meeting Scheduling**: Advanced meeting scheduling with calendar integration
- **Real-time Analytics**: Dashboard with meeting statistics and agent performance metrics

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional)
- Kubernetes cluster (for Helm deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/kolasaniv1996/autonomous-meeting-assistant.git
   cd autonomous-meeting-assistant
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp ../.env.example .env
   # Edit .env with your configuration
   python app.py
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - Default login: admin / admin123

### Docker Deployment

1. **Build and run with Docker Compose**
>>>>>>> develop
   ```bash
   docker-compose up -d
   ```

<<<<<<< HEAD
3. **Access the application:**
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:5001`

### Production Deployment

For production deployment, update the `docker-compose.prod.yml`:

```yaml
version: '3.8'
services:
  backend:
    build: ./agent_web_interface
    environment:
      - FLASK_ENV=production
    ports:
      - "5001:5001"
  
  frontend:
    build: ./agent-dashboard
    ports:
      - "80:80"
    depends_on:
      - backend
```

## 🧪 Testing

### Backend Testing
```bash
cd agent_web_interface
python -m pytest tests/
```

### Frontend Testing
```bash
cd agent-dashboard
pnpm test  # or npm test
```

### End-to-End Testing
```bash
# Start both backend and frontend
# Then run integration tests
python tests/test_integration.py
```

## 📖 User Guide

### Getting Started

1. **Configure API Credentials:**
   - Navigate to the Configurations page
   - Fill in your Jira, GitHub, and Confluence credentials
   - Configure meeting platform settings (Teams/Google Meet)
   - Set up speech processing preferences

2. **Create Agents:**
   - Go to the Agents page
   - Click "Create New Agent"
   - Fill in employee details and integration mappings
   - Assign teams and projects

3. **Schedule Meetings:**
   - Visit the Meetings page
   - Click "Schedule Meeting"
   - Select participants and platform
   - Configure speech processing options

4. **Monitor Activity:**
   - Use the Dashboard for real-time statistics
   - View meeting transcripts and summaries
   - Track agent performance and activity

## 🔒 Security Considerations

- **API Keys:** Store sensitive credentials in environment variables
- **CORS:** Configure appropriate origins for production
- **Authentication:** Implement user authentication for production use
- **HTTPS:** Use SSL/TLS certificates for production deployment
- **Database:** Use PostgreSQL or MySQL for production instead of SQLite

## 🤝 Contributing
=======
### Kubernetes Deployment with Helm

1. **Install the Helm chart**
   ```bash
   cd helm-chart
   helm install meeting-assistant . \
     --set auth.jwtSecret="your-secure-jwt-secret" \
     --set auth.adminPassword="your-admin-password"
   ```

2. **Access the application**
   ```bash
   kubectl port-forward svc/meeting-assistant-frontend 3000:80
   ```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

#### Authentication
- `JWT_SECRET`: Secret key for JWT token generation
- `ADMIN_PASSWORD`: Default admin user password
- `SESSION_TIMEOUT`: Session timeout in seconds

#### Email Configuration
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password

#### API Configuration
- `RATE_LIMIT_REQUESTS`: API rate limit requests per window
- `RATE_LIMIT_WINDOW`: Rate limit window in seconds
- `LOG_LEVEL`: Application log level (DEBUG, INFO, WARNING, ERROR)

### Integration Setup

Configure integrations through the web interface:

1. **Jira Integration**
   - Jira URL: `https://your-domain.atlassian.net`
   - Username: Your Jira email
   - API Token: Generate from Jira settings

2. **GitHub Integration**
   - Username: Your GitHub username
   - Personal Access Token: Generate from GitHub settings

3. **Microsoft Teams Integration**
   - Tenant ID: Azure AD tenant ID
   - Client ID: Azure app registration client ID
   - Client Secret: Azure app registration secret

4. **Azure Speech Services**
   - Subscription Key: Azure Speech service key
   - Region: Azure region (e.g., eastus)

## Usage

### Creating Agents

1. Navigate to the **Agents** page
2. Click **New Agent**
3. Configure agent settings:
   - Name and description
   - Meeting platforms
   - Capabilities (transcription, action items, etc.)
   - Integration usernames
   - Maximum concurrent meetings

### Scheduling Meetings

1. Navigate to the **Meetings** page
2. Click **Schedule Meeting**
3. Fill in meeting details:
   - Title and description
   - Platform and meeting URL
   - Date and time
   - Duration
   - Assign agents

### Managing Configurations

1. Navigate to the **Configuration** page
2. Create configuration profiles with API credentials
3. Set one configuration as active
4. Export/import configurations for backup

### System Settings

1. Navigate to the **Settings** page
2. Configure system-wide preferences:
   - Timezone and language
   - Notification settings
   - Security settings
   - API limits
   - Backup settings

## API Documentation

### Authentication Endpoints

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/profile` - Get user profile

### Configuration Endpoints

- `GET /api/configurations` - List configurations
- `POST /api/configurations` - Create configuration
- `PUT /api/configurations/{id}` - Update configuration
- `DELETE /api/configurations/{id}` - Delete configuration

### Agent Endpoints

- `GET /api/agents` - List agents
- `POST /api/agents` - Create agent
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Meeting Endpoints

- `GET /api/meetings` - List meetings
- `POST /api/meetings` - Create meeting
- `PUT /api/meetings/{id}` - Update meeting
- `DELETE /api/meetings/{id}` - Delete meeting

### Settings Endpoints

- `GET /api/settings` - Get user settings
- `POST /api/settings` - Update settings

## Database Schema

The application uses SQLite by default with the following main tables:

- `users` - User accounts and authentication
- `user_sessions` - JWT session management
- `user_configurations` - API credentials and configurations
- `agents` - Autonomous meeting agents
- `meetings` - Scheduled meetings
- `settings` - User preferences and system settings
- `meeting_participants` - Agent-meeting assignments
- `meeting_transcripts` - Meeting transcriptions
- `action_items` - Extracted action items
- `integration_logs` - API integration logs
- `audit_logs` - System audit trail

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Rate limiting
- CORS protection
- Input validation and sanitization
- Audit logging
- Session encryption
- Optional 2FA support

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Ensure SQLite database file permissions
   - Check database path in environment variables

2. **Authentication failures**
   - Verify JWT secret configuration
   - Check token expiration settings

3. **Integration API errors**
   - Validate API credentials in configurations
   - Check network connectivity to external services
   - Review integration logs in the database

4. **Meeting scheduling issues**
   - Verify agent availability
   - Check meeting platform configurations
   - Ensure proper timezone settings

### Logs

Application logs are available at:
- Backend: Console output or configured log file
- Frontend: Browser console
- Database: `integration_logs` and `audit_logs` tables

## Contributing
>>>>>>> develop

1. Fork the repository
2. Create a feature branch
3. Make your changes
<<<<<<< HEAD
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `docs/` directory
- Review the API documentation for endpoint details

## 🔄 Updates and Roadmap

### Current Version: 1.0.0
- Complete web interface with CRUD operations
- Real-time meeting management
- Multi-platform integration support
- Comprehensive configuration management

### Planned Features:
- User authentication and authorization
- Advanced analytics and reporting
- Real-time notifications
- Mobile application
- Advanced meeting scheduling
- Integration with more platforms



## 🚀 Kubernetes Deployment

For detailed instructions on how to deploy this application to a Kubernetes cluster, including building Docker images, preparing Kubernetes manifests, and verifying the deployment, please refer to the [Kubernetes Deployment Guide](deployment_guide.md).

### Accessing the Application

Once deployed to Kubernetes, you can access the frontend dashboard through the Ingress. To find the URL, you can use `minikube service frontend-service --url` if you are using Minikube, or check your Ingress Controller's external IP/hostname for other Kubernetes clusters.

=======
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting section

## Changelog

### Version 1.0.0
- Initial release
- Complete authentication system
- Configuration management
- Agent management
- Meeting scheduling
- Settings management
- Helm chart deployment
- Comprehensive API endpoints
>>>>>>> develop

