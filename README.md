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
   ```bash
   docker-compose up -d
   ```

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

1. Fork the repository
2. Create a feature branch
3. Make your changes
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

