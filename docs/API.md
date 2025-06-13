# API Documentation

## Overview

The Autonomous Agent Framework Web Interface provides a comprehensive REST API for managing configurations, agents, and meetings. All endpoints return JSON responses with a consistent structure.

## Base URL

- Development: `http://localhost:5001/api`
- Production: `https://your-domain.com/api`

## Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": {...},
  "message": "Optional message",
  "error": "Error message if success is false"
}
```

## Authentication

Currently, the API does not require authentication. For production use, implement proper authentication mechanisms.

## Configuration Endpoints

### List Configurations

**GET** `/configurations`

Returns all configurations.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Production Config",
      "description": "Main production configuration",
      "is_active": true,
      "api_credentials": {...},
      "meeting_platforms": {...},
      "speech_processing": {...},
      "employees": {...},
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Configuration

**POST** `/configurations`

Creates a new configuration.

**Request Body:**
```json
{
  "name": "New Configuration",
  "description": "Description of the configuration",
  "api_credentials": {
    "jira_url": "https://company.atlassian.net",
    "jira_username": "user@company.com",
    "jira_api_token": "token",
    "github_token": "github_token",
    "confluence_url": "https://company.atlassian.net/wiki",
    "confluence_username": "user@company.com",
    "confluence_api_token": "token"
  },
  "meeting_platforms": {
    "teams": {
      "app_id": "teams_app_id",
      "app_secret": "teams_app_secret",
      "tenant_id": "tenant_id"
    },
    "google_meet": {
      "client_id": "google_client_id",
      "client_secret": "google_client_secret"
    }
  },
  "speech_processing": {
    "azure": {
      "speech_key": "azure_key",
      "region": "azure_region"
    },
    "google_cloud": {
      "project_id": "project_id",
      "credentials_path": "path_to_credentials"
    },
    "openai": {
      "api_key": "openai_key"
    }
  },
  "employees": {
    "vivek": {
      "name": "Vivek Kumar",
      "email": "vivek@company.com",
      "jira_username": "vivek.kumar",
      "github_username": "vivek-dev",
      "teams": ["engineering", "product"],
      "projects": ["project-alpha", "project-beta"]
    }
  }
}
```

### Update Configuration

**PUT** `/configurations/{id}`

Updates an existing configuration.

### Delete Configuration

**DELETE** `/configurations/{id}`

Deletes a configuration.

### Activate Configuration

**PUT** `/configurations/{id}/activate`

Activates a configuration and deactivates all others.

## Agent Endpoints

### List Agents

**GET** `/agents`

Returns all agents with optional filtering.

**Query Parameters:**
- `search` - Search by name, email, or employee_id
- `status` - Filter by status (active, inactive)
- `team` - Filter by team
- `project` - Filter by project

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "employee_id": "EMP001",
      "name": "John Doe",
      "email": "john@company.com",
      "title": "Software Engineer",
      "teams": ["engineering", "backend"],
      "projects": ["project-alpha"],
      "jira_username": "john.doe",
      "github_username": "johndoe",
      "confluence_username": "john.doe",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Agent

**POST** `/agents`

Creates a new agent.

**Request Body:**
```json
{
  "employee_id": "EMP002",
  "name": "Jane Smith",
  "email": "jane@company.com",
  "title": "Product Manager",
  "teams": ["product", "design"],
  "projects": ["project-beta"],
  "jira_username": "jane.smith",
  "github_username": "janesmith",
  "confluence_username": "jane.smith"
}
```

### Update Agent

**PUT** `/agents/{id}`

Updates an existing agent.

### Delete Agent

**DELETE** `/agents/{id}`

Deletes an agent.

### Toggle Agent Status

**PUT** `/agents/{id}/toggle-status`

Toggles the agent's active/inactive status.

### Get Agent Statistics

**GET** `/agents/stats`

Returns agent statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 25,
    "active": 20,
    "inactive": 5,
    "teams": {
      "engineering": 12,
      "product": 8,
      "design": 5
    }
  }
}
```

## Meeting Endpoints

### List Meetings

**GET** `/meetings`

Returns all meetings with optional filtering.

**Query Parameters:**
- `status` - Filter by status (scheduled, active, completed, cancelled)
- `platform` - Filter by platform (teams, google_meet)
- `date_from` - Filter meetings from date (YYYY-MM-DD)
- `date_to` - Filter meetings to date (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Daily Standup",
      "description": "Team daily standup meeting",
      "platform": "teams",
      "meeting_url": "https://teams.microsoft.com/...",
      "scheduled_time": "2024-01-01T09:00:00Z",
      "duration": 30,
      "participants": [1, 2, 3],
      "speech_processing": {
        "enabled": true,
        "provider": "azure",
        "language": "en-US"
      },
      "status": "scheduled",
      "transcript": null,
      "summary": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Schedule Meeting

**POST** `/meetings`

Schedules a new meeting.

**Request Body:**
```json
{
  "title": "Project Review",
  "description": "Weekly project review meeting",
  "platform": "teams",
  "scheduled_time": "2024-01-01T14:00:00Z",
  "duration": 60,
  "participants": [1, 2, 3, 4],
  "speech_processing": {
    "enabled": true,
    "provider": "azure",
    "language": "en-US"
  }
}
```

### Update Meeting

**PUT** `/meetings/{id}`

Updates an existing meeting.

### Delete Meeting

**DELETE** `/meetings/{id}`

Deletes a meeting.

### Start Meeting

**POST** `/meetings/{id}/start`

Starts a meeting and begins recording/transcription if enabled.

### End Meeting

**POST** `/meetings/{id}/end`

Ends a meeting and processes the transcript.

### Get Meeting Statistics

**GET** `/meetings/stats`

Returns meeting statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 150,
    "scheduled": 25,
    "active": 3,
    "completed": 120,
    "cancelled": 2,
    "platforms": {
      "teams": 90,
      "google_meet": 60
    },
    "avg_duration": 45
  }
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

Error responses include details:

```json
{
  "success": false,
  "error": "Validation error: Name is required",
  "details": {
    "field": "name",
    "code": "REQUIRED"
  }
}
```

## Rate Limiting

Currently, no rate limiting is implemented. For production use, implement appropriate rate limiting based on your requirements.

## Webhooks

The API supports webhooks for real-time updates:

### Meeting Events

- `meeting.started` - When a meeting starts
- `meeting.ended` - When a meeting ends
- `meeting.transcript.ready` - When transcript is processed

### Agent Events

- `agent.created` - When an agent is created
- `agent.updated` - When an agent is updated
- `agent.status.changed` - When agent status changes

Configure webhooks in your configuration:

```json
{
  "webhooks": {
    "url": "https://your-app.com/webhooks",
    "secret": "webhook_secret",
    "events": ["meeting.started", "meeting.ended"]
  }
}
```

