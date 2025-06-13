# Autonomous Agent Framework

A modular, scalable framework for creating autonomous agents that minimize time wasted in meetings by enabling user-specific agents to attend, communicate, and summarize meetings on behalf of employees.

## 🎯 Core Problem

Finance and enterprise companies spend excessive time in meetings, often repeating project updates and status reports. This framework solves this by:

- **Analyzing** Jira tickets, GitHub commits, and Confluence pages to understand each employee's work context
- **Attending** virtual meetings via voice, chat, or text-based platforms on behalf of employees
- **Communicating** status, blockers, and technical details automatically
- **Creating** Jira tickets, Confluence docs, or meeting summaries after meetings

## ✨ Key Features

### 🤖 Intelligent Agent System
- **Employee-specific agents** that understand individual work contexts
- **Multi-source context extraction** from Jira, GitHub, and Confluence
- **Intelligent response generation** based on current work status
- **Configurable behavior** per employee and team

### 🎪 Meeting Participation Engine
- **Text-based meeting simulation** with multiple agents
- **Smart conversation flow** with turn-taking management
- **Context-aware responses** to questions and discussions
- **Multiple meeting types** (standup, planning, review, etc.)

### 📊 Post-Meeting Actions
- **Automatic summary generation** with key points and decisions
- **Action item extraction** with assignees and due dates
- **Jira ticket creation** for follow-up tasks
- **Confluence documentation** updates with meeting notes

### 🔧 API Integrations
- **Jira API** for work item tracking and ticket management
- **GitHub API** for code activity and pull request monitoring
- **Confluence API** for documentation and knowledge base access
- **Extensible connector architecture** for additional integrations

## 🎙️ Audio-Aware Meeting Features (NEW)

### 🎭 Meeting Platform Integration
- **Microsoft Teams**: Native bot framework integration for Teams meetings
- **Google Meet**: Headless browser automation for Google Meet participation
- **Multi-Platform Support**: Seamless switching between different meeting platforms
- **Automatic Platform Detection**: Smart URL parsing and platform identification

### 🎤 Real-Time Speech Processing
- **Multi-Provider Speech-to-Text**: Support for Azure Speech, Google Cloud Speech, and OpenAI Whisper
- **Real-Time Transcription**: Live meeting transcription with high accuracy
- **Speaker Diarization**: Automatic speaker identification and separation
- **Fallback Support**: Automatic provider switching for maximum reliability

### 🎬 Audio-Aware Meeting Orchestration
- **Complete Meeting Lifecycle**: Automated scheduling, joining, participation, and cleanup
- **Concurrent Meeting Support**: Handle multiple simultaneous meetings
- **Intelligent Agent Responses**: Context-driven participation in live audio meetings
- **Real-Time Audio Processing**: Live audio streaming and transcription integration

### 🔊 Enhanced Meeting Participation
- **Voice-Enabled Meetings**: Agents can participate in actual Teams/Google Meet calls
- **Audio Transcription**: Real-time conversion of speech to text for processing
- **Smart Response Triggers**: Agents respond when mentioned or when relevant topics arise
- **Meeting State Management**: Track meeting progress and participant status

## 🏗️ Architecture

```
autonomous_agent_framework/
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Base agent architecture
│   ├── employee_agent.py  # Employee-specific agent
│   └── agent_manager.py   # Multi-agent management
├── api_connectors/        # External API integrations
│   ├── jira_connector.py
│   ├── github_connector.py
│   └── confluence_connector.py
├── meeting_platforms/     # Meeting platform integrations (NEW)
│   ├── platform_manager.py      # Multi-platform management
│   ├── teams_integration.py     # Microsoft Teams integration
│   └── google_meet_integration.py # Google Meet integration
├── speech_processing/     # Speech-to-text integrations (NEW)
│   ├── speech_manager.py        # Multi-provider speech management
│   ├── azure_speech.py          # Azure Speech Services
│   ├── google_speech.py         # Google Cloud Speech
│   └── whisper_integration.py   # OpenAI Whisper
├── context_builder/       # Context aggregation
│   └── context_builder.py
├── meeting_engine/        # Meeting simulation and orchestration
│   ├── meeting_simulator.py           # Text-based meeting simulation
│   ├── conversation_manager.py        # Conversation flow management
│   └── audio_meeting_orchestrator.py  # Audio-aware meeting orchestration (NEW)
├── post_meeting/          # Post-meeting processing
│   └── action_handler.py
├── config/               # Configuration management
│   ├── config_manager.py
│   └── agent_config.yaml
├── examples/             # Example implementations
│   ├── demo_vivek.py           # Basic framework demo
│   └── audio_aware_demo.py     # Audio-aware features demo (NEW)
└── tests/               # Testing utilities
    ├── verify_framework.py
    ├── verify_enhanced_framework.py  # Enhanced verification (NEW)
    └── test_integrations.py          # Integration tests (NEW)
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the framework
cd autonomous_agent_framework

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy and customize the configuration file:

```bash
cp config/agent_config.yaml config/my_config.yaml
```

Edit `config/my_config.yaml` with your API credentials and employee information:

```yaml
api_credentials:
  jira_url: "https://your-company.atlassian.net"
  jira_username: "your-email@company.com"
  jira_token: "your-jira-api-token"
  github_token: "your-github-token"
  confluence_url: "https://your-company.atlassian.net/wiki"
  confluence_username: "your-email@company.com"
  confluence_token: "your-confluence-token"
  
  # Meeting platform credentials (NEW)
  teams_app_id: "your-teams-app-id"
  teams_app_password: "your-teams-app-password"
  teams_tenant_id: "your-azure-tenant-id"
  
  # Speech-to-text service credentials (NEW)
  azure_speech_key: "your-azure-speech-key"
  azure_speech_region: "eastus"
  google_speech_credentials_path: "path/to/google_credentials.json"
  google_cloud_project_id: "your-google-project-id"
  openai_api_key: "your-openai-api-key"

# Meeting platform configuration (NEW)
meeting_platforms:
  preferred_platform: "teams"
  enabled_platforms: ["teams", "google_meet"]
  
  teams:
    auto_join_scheduled_meetings: true
    enable_chat_responses: true
    enable_meeting_summaries: true
  
  google_meet:
    use_headless_browser: true
    auto_disable_camera: true
    auto_disable_microphone: true

# Speech processing configuration (NEW)
speech_processing:
  preferred_provider: "azure"
  enabled_providers: ["azure", "google_cloud", "whisper"]
  enable_fallback: true
  
  real_time:
    chunk_duration_seconds: 30
    enable_partial_results: true
    enable_speaker_diarization: true
    max_speakers: 8

employees:
  vivek:
    name: "Vivek Kumar"
    employee_id: "vivek"
    email: "vivek@company.com"
    jira_username: "vivek.kumar"
    github_username: "vivek-dev"
    projects: ["PROJECT-A", "PROJECT-B"]
    teams: ["backend-team"]
    role: "Senior Software Engineer"
```

### 3. Run the Demo

**Basic Framework Demo:**
```bash
python examples/demo_vivek.py
```

**Audio-Aware Meeting Demo (NEW):**
```bash
python examples/audio_aware_demo.py
```

The basic demo demonstrates:
- Agent initialization with sample data
- Multi-agent meeting simulation
- Post-meeting summary generation
- Action item extraction

The audio-aware demo demonstrates:
- Meeting platform integration (Teams/Google Meet)
- Real-time speech-to-text processing
- Audio-aware meeting orchestration
- Multi-provider speech processing
- Live meeting participation

## 📖 Usage Guide

### Creating Agents

```python
from autonomous_agent_framework.config.config_manager import ConfigManager
from autonomous_agent_framework.agents.agent_manager import AgentManager

# Initialize configuration
config_manager = ConfigManager("config/my_config.yaml")
agent_manager = AgentManager(config_manager)

# Initialize all agents
await agent_manager.initialize()

# Get a specific agent
vivek_agent = await agent_manager.get_agent('vivek')
```

### Running Meetings

```python
from autonomous_agent_framework.meeting_engine.meeting_simulator import MeetingSimulator

# Create meeting simulator
meeting_simulator = MeetingSimulator()

# Create a meeting
meeting_id = await meeting_simulator.create_meeting(
    title="Daily Standup - Backend Team",
    participants=['vivek', 'sarah', 'alex'],
    meeting_type="standup"
)

# Start the meeting
await meeting_simulator.start_meeting(meeting_id, agent_manager.agents)

# End the meeting
completed_meeting = await meeting_simulator.end_meeting(meeting_id)
```

### Processing Meeting Results

```python
from autonomous_agent_framework.post_meeting.action_handler import PostMeetingActionHandler

# Create action handler
action_handler = PostMeetingActionHandler(
    jira_connector=jira_connector,
    confluence_connector=confluence_connector
)

# Process meeting completion
results = await action_handler.process_meeting_completion(
    completed_meeting.messages,
    completed_meeting.context
)

print(f"Created {len(results['jira_tickets'])} Jira tickets")
print(f"Generated summary with {len(results['summary'].action_items)} action items")
```

### Audio-Aware Meeting Usage (NEW)

```python
from autonomous_agent_framework.meeting_engine.audio_meeting_orchestrator import AudioAwareMeetingOrchestrator
from datetime import datetime, timedelta

# Initialize audio-aware orchestrator
orchestrator = AudioAwareMeetingOrchestrator(config_manager)
await orchestrator.initialize(agent_manager.agents)

# Schedule an audio meeting
meeting_config = {
    'title': 'Sprint Planning - Q1 2025',
    'participants': ['vivek', 'sarah'],
    'start_time': datetime.now() + timedelta(minutes=5),
    'duration_minutes': 30,
    'platform': 'teams',  # or 'google_meet'
    'speech_provider': 'azure',  # or 'google_cloud', 'whisper'
    'enable_transcription': True
}

meeting_id = await orchestrator.schedule_meeting(meeting_config)

# Monitor meeting status
status = orchestrator.get_meeting_status(meeting_id)
print(f"Meeting state: {status['state'].value}")
print(f"Transcript entries: {status['transcript_length']}")

# End meeting when done
await orchestrator.end_meeting(meeting_id, "meeting_complete")
```

### Speech Processing Usage (NEW)

```python
from autonomous_agent_framework.speech_processing.speech_manager import SpeechProcessingManager

# Initialize speech manager
speech_manager = SpeechProcessingManager(config_manager)
await speech_manager.initialize()

# Set up transcription callback
async def transcription_callback(result):
    print(f"[{result['speaker']}] {result['text']}")

speech_manager.set_global_callback(transcription_callback)

# Start meeting transcription
await speech_manager.start_meeting_transcription("meeting_001")

# Process audio data (from meeting platform)
await speech_manager.process_meeting_audio("meeting_001", audio_data)

# Get transcript
transcript = speech_manager.get_meeting_transcript("meeting_001")

# Stop transcription
await speech_manager.stop_meeting_transcription("meeting_001")
```

## 🔧 Configuration Reference

### API Credentials

| Field | Description | Required |
|-------|-------------|----------|
| `jira_url` | Jira instance URL | Yes |
| `jira_username` | Jira username/email | Yes |
| `jira_token` | Jira API token | Yes |
| `github_token` | GitHub personal access token | Yes |
| `confluence_url` | Confluence instance URL | Yes |
| `confluence_username` | Confluence username/email | Yes |
| `confluence_token` | Confluence API token | Yes |
| **Meeting Platform Credentials (NEW)** | | |
| `teams_app_id` | Microsoft Teams app ID | For Teams |
| `teams_app_password` | Microsoft Teams app password | For Teams |
| `teams_tenant_id` | Azure tenant ID | For Teams |
| **Speech Processing Credentials (NEW)** | | |
| `azure_speech_key` | Azure Speech Services key | For Azure Speech |
| `azure_speech_region` | Azure Speech Services region | For Azure Speech |
| `google_speech_credentials_path` | Google Cloud credentials file path | For Google Speech |
| `google_cloud_project_id` | Google Cloud project ID | For Google Speech |
| `openai_api_key` | OpenAI API key | For Whisper |

### Employee Configuration

| Field | Description | Required |
|-------|-------------|----------|
| `name` | Full name of employee | Yes |
| `employee_id` | Unique identifier | Yes |
| `email` | Email address | Yes |
| `jira_username` | Jira username | No |
| `github_username` | GitHub username | No |
| `confluence_username` | Confluence username | No |
| `projects` | List of project keys | No |
| `teams` | List of team names | No |
| `role` | Job title/role | No |
| `manager` | Manager's employee_id | No |

### Meeting Configuration

| Field | Description | Default |
|-------|-------------|---------|
| `max_response_length` | Maximum response length | 200 |
| `context_window_days` | Days of context to load | 7 |
| `auto_join_meetings` | Auto-join scheduled meetings | true |
| `create_summaries` | Generate meeting summaries | true |
| `create_action_items` | Extract action items | true |
| `update_jira_tickets` | Create Jira tickets | true |

## 🎭 Meeting Types

The framework supports different meeting types with customized flows:

### Standup Meetings
- Opening and introductions
- Status updates from each team member
- Discussion of blockers and impediments
- Planning for upcoming work
- Action items and next steps

### Planning Meetings
- Review of previous sprint/period
- Planning upcoming work
- Task estimation and assignment
- Risk assessment and mitigation
- Summary and action items

### Review Meetings
- Demo of completed work
- Feedback and discussion
- Retrospective on process
- Lessons learned
- Next steps

## 🔌 API Integrations

### Jira Integration
- Extract assigned tickets and work items
- Track status changes and updates
- Get blocked items and impediments
- Create new tickets for action items
- Update existing tickets

### GitHub Integration
- Monitor commits and pull requests
- Track code review activity
- Extract repository statistics
- Analyze contribution patterns
- Get recent development activity

### Confluence Integration
- Access documentation pages
- Track page updates and edits
- Search for relevant content
- Create meeting summaries
- Update documentation

## 🧪 Testing

### Verify Framework Structure
```bash
# Basic framework verification
python tests/verify_framework.py

# Enhanced framework verification (NEW)
python tests/verify_enhanced_framework.py

# Integration tests (NEW)
python tests/test_integrations.py
```

### Run Demos
```bash
# Basic framework demo
python examples/demo_vivek.py

# Audio-aware meeting demo (NEW)
python examples/audio_aware_demo.py
```

### Custom Testing
Create your own test scripts using the mock connectors provided in the examples.

### Testing Audio Features (NEW)
The framework includes comprehensive testing for:
- Meeting platform integrations (Teams, Google Meet)
- Speech-to-text providers (Azure, Google Cloud, Whisper)
- Audio-aware meeting orchestration
- Real-time transcription and processing
- Error handling and fallback mechanisms

## 🚀 Deployment

### Docker Deployment (Coming Soon)
```bash
# Build the container
docker build -t autonomous-agent-framework .

# Run with configuration
docker run -v $(pwd)/config:/app/config autonomous-agent-framework
```

### Production Considerations
- **Security**: Store API tokens securely using environment variables
- **Scaling**: Use Redis for context caching in multi-instance deployments
- **Monitoring**: Implement logging and metrics collection
- **Backup**: Regular backup of configuration and meeting data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions, issues, or feature requests:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information
4. Contact the development team

## 🔮 Roadmap

### Phase 1 (Current)
- ✅ Core agent framework
- ✅ Text-based meeting simulation
- ✅ Basic API integrations
- ✅ Post-meeting processing

### Phase 2 (Planned)
- 🔄 Voice-based meeting integration
- 🔄 Slack/Teams bot integration
- 🔄 Advanced NLP for better context understanding
- 🔄 Machine learning for response optimization

### Phase 3 (Future)
- 🔄 Real-time meeting transcription
- 🔄 Video meeting integration
- 🔄 Advanced scheduling and calendar integration
- 🔄 Multi-language support

---

**Built with ❤️ for reducing meeting overhead and improving productivity**

