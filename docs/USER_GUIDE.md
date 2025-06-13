# User Guide - Autonomous Agent Framework Web Interface

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Configuration Management](#configuration-management)
4. [Agent Management](#agent-management)
5. [Meeting Management](#meeting-management)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Setup

1. **Access the Application**
   - Open your web browser
   - Navigate to `http://localhost:3000` (or your deployed URL)
   - You should see the Autonomous Agent Dashboard

2. **Initial Configuration**
   - Click on "Configurations" in the sidebar
   - Click "Create New Configuration"
   - Fill in your API credentials and settings
   - Save and activate the configuration

### Navigation

The dashboard uses a sidebar navigation with the following sections:
- **Dashboard** - Overview and statistics
- **Configurations** - API credentials and settings
- **Agents** - Employee agent management
- **Meetings** - Meeting scheduling and control
- **Settings** - Application preferences

## Dashboard Overview

The dashboard provides a real-time overview of your autonomous agent system:

### Key Metrics
- **Total Agents** - Number of configured employee agents
- **Active Agents** - Agents currently available for meetings
- **Total Meetings** - All scheduled and completed meetings
- **Active Meetings** - Currently running meetings

### Quick Actions
- Create new agents
- Schedule meetings
- View recent activity
- Access configuration settings

## Configuration Management

### Creating a Configuration

1. **Navigate to Configurations**
   - Click "Configurations" in the sidebar
   - Click "Create New Configuration"

2. **Basic Information**
   - **Name**: Give your configuration a descriptive name
   - **Description**: Add details about this configuration's purpose

3. **API Credentials Tab**
   - **Jira Settings**:
     - URL: Your Jira instance URL (e.g., `https://company.atlassian.net`)
     - Username: Your Jira email address
     - API Token: Generate from Jira Account Settings > Security > API tokens
   
   - **GitHub Settings**:
     - Token: Personal Access Token from GitHub Settings > Developer settings
   
   - **Confluence Settings**:
     - URL: Your Confluence URL (e.g., `https://company.atlassian.net/wiki`)
     - Username: Your Confluence email address
     - API Token: Same as Jira token if using Atlassian Cloud

4. **Meeting Platforms Tab**
   - **Microsoft Teams**:
     - App ID: From Azure App Registration
     - App Secret: Client secret from Azure
     - Tenant ID: Your Azure AD tenant ID
   
   - **Google Meet**:
     - Client ID: From Google Cloud Console
     - Client Secret: OAuth 2.0 client secret

5. **Speech Processing Tab**
   - **Azure Speech Services**:
     - Speech Key: From Azure Cognitive Services
     - Region: Azure region (e.g., `eastus`)
   
   - **Google Cloud Speech**:
     - Project ID: Your Google Cloud project ID
     - Credentials: Path to service account JSON file
   
   - **OpenAI Whisper**:
     - API Key: Your OpenAI API key

6. **Employee Configuration Tab**
   - Add employee mappings in JSON format:
   ```json
   {
     "john_doe": {
       "name": "John Doe",
       "email": "john@company.com",
       "jira_username": "john.doe",
       "github_username": "johndoe",
       "teams": ["engineering", "backend"],
       "projects": ["project-alpha"]
     }
   }
   ```

### Managing Configurations

- **Edit**: Click the edit icon to modify a configuration
- **Delete**: Click the trash icon to remove a configuration
- **Activate**: Click "Activate" to make a configuration active
- **Duplicate**: Create a copy of an existing configuration

## Agent Management

### Creating Agents

1. **Navigate to Agents**
   - Click "Agents" in the sidebar
   - Click "Create New Agent"

2. **Fill Agent Details**
   - **Employee ID**: Unique identifier (e.g., `EMP001`)
   - **Name**: Full name of the employee
   - **Email**: Work email address
   - **Title**: Job title or role
   - **Teams**: Comma-separated team names
   - **Projects**: Comma-separated project names

3. **Integration Mappings**
   - **Jira Username**: Username in Jira
   - **GitHub Username**: GitHub handle
   - **Confluence Username**: Confluence username

### Agent Operations

- **Search**: Use the search bar to find agents by name, email, or ID
- **Filter**: Filter by status, team, or project
- **Edit**: Click the edit icon to modify agent details
- **Toggle Status**: Activate or deactivate agents
- **Delete**: Remove agents from the system

### Agent Status

- **Active** (Green): Agent is available for meetings
- **Inactive** (Gray): Agent is disabled

## Meeting Management

### Scheduling Meetings

1. **Navigate to Meetings**
   - Click "Meetings" in the sidebar
   - Click "Schedule Meeting"

2. **Meeting Details**
   - **Title**: Meeting name
   - **Description**: Meeting purpose and agenda
   - **Platform**: Choose Teams or Google Meet
   - **Date & Time**: When the meeting should occur
   - **Duration**: Meeting length in minutes

3. **Participants**
   - Select agents from the dropdown
   - Add multiple participants as needed

4. **Speech Processing**
   - **Enable Transcription**: Toggle on/off
   - **Provider**: Choose Azure, Google Cloud, or Whisper
   - **Language**: Select the meeting language

### Meeting Control

- **Start Meeting**: Begin the meeting and start recording
- **End Meeting**: Stop the meeting and process transcript
- **Edit**: Modify meeting details before it starts
- **Delete**: Cancel and remove the meeting

### Meeting Status

- **Scheduled** (Blue): Meeting is planned for the future
- **Active** (Green): Meeting is currently in progress
- **Completed** (Gray): Meeting has ended
- **Cancelled** (Red): Meeting was cancelled

### Viewing Transcripts

1. **Find Completed Meeting**
   - Look for meetings with "Completed" status
   - Click "View Transcript" button

2. **Transcript Features**
   - **Full Transcript**: Complete meeting conversation
   - **Speaker Identification**: Who said what
   - **Timestamps**: When each part was spoken
   - **Action Items**: Extracted tasks and assignments

## Troubleshooting

### Common Issues

#### "API Connection Failed"
- Check your internet connection
- Verify API credentials in configuration
- Ensure the backend server is running

#### "Agent Not Responding"
- Check agent status (should be Active)
- Verify integration mappings are correct
- Check if the agent has necessary permissions

#### "Meeting Won't Start"
- Verify meeting platform credentials
- Check if the meeting time has arrived
- Ensure participants are available

#### "Transcription Not Working"
- Check speech processing configuration
- Verify API keys for speech services
- Ensure microphone permissions are granted

### Getting Help

1. **Check Logs**
   - Backend logs: Check Flask server console
   - Frontend logs: Open browser developer tools

2. **Verify Configuration**
   - Ensure all required fields are filled
   - Test API connections individually
   - Check credential validity

3. **Contact Support**
   - Create an issue on GitHub
   - Include error messages and logs
   - Describe steps to reproduce the problem

### Performance Tips

1. **Optimize Agent Count**
   - Don't create more agents than necessary
   - Deactivate unused agents

2. **Meeting Management**
   - End meetings promptly to free resources
   - Clean up old meeting data regularly

3. **Configuration**
   - Use only required integrations
   - Keep API credentials up to date

### Security Best Practices

1. **Credential Management**
   - Store API keys securely
   - Rotate credentials regularly
   - Use environment variables for sensitive data

2. **Access Control**
   - Limit who can create/modify configurations
   - Monitor agent activity
   - Review meeting participants

3. **Data Protection**
   - Regularly backup configuration data
   - Secure meeting transcripts
   - Follow company data policies

