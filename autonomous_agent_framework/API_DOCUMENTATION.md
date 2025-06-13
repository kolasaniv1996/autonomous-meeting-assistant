# API Documentation

This document provides detailed information about the Autonomous Agent Framework's API and how to use it programmatically.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Configuration Management](#configuration-management)
3. [Agent Management](#agent-management)
4. [Meeting Engine](#meeting-engine)
5. [Context Building](#context-building)
6. [Post-Meeting Processing](#post-meeting-processing)
7. [API Connectors](#api-connectors)
8. [Examples](#examples)

## Core Classes

### BaseAgent

The foundation class for all agents in the framework.

```python
from autonomous_agent_framework.agents.base_agent import BaseAgent

class BaseAgent(ABC):
    def __init__(self, employee_id: str, config: Dict[str, Any])
    
    @abstractmethod
    async def initialize(self) -> None
    
    @abstractmethod
    async def update_context(self) -> ContextSummary
    
    @abstractmethod
    async def generate_response(self, message: str, meeting_context: MeetingContext) -> MeetingMessage
    
    @abstractmethod
    async def handle_question(self, question: str, meeting_context: MeetingContext) -> MeetingMessage
```

### EmployeeAgent

Concrete implementation of BaseAgent for individual employees.

```python
from autonomous_agent_framework.agents.employee_agent import EmployeeAgent

# Create an employee agent
agent = EmployeeAgent("vivek", config)
await agent.initialize()

# Update context
context = await agent.update_context()

# Generate response to a message
response = await agent.generate_response("What's your status?", meeting_context)
```

### Data Models

#### WorkItem

Represents a work item from any source (Jira, GitHub, Confluence).

```python
from autonomous_agent_framework.agents.base_agent import WorkItem, Priority

work_item = WorkItem(
    id="PROJ-123",
    title="Implement user authentication",
    description="Create REST API endpoints for user login",
    status="In Progress",
    priority=Priority.HIGH,
    assignee="vivek",
    created_date=datetime.now(),
    updated_date=datetime.now(),
    source="jira",
    url="https://company.atlassian.net/browse/PROJ-123",
    labels=["backend", "api"],
    comments=["Started implementation"]
)
```

#### ContextSummary

Aggregated work context for an employee.

```python
from autonomous_agent_framework.agents.base_agent import ContextSummary

context = ContextSummary(
    employee_id="vivek",
    generated_at=datetime.now(),
    active_tasks=[work_item1, work_item2],
    recent_commits=[commit1, commit2],
    blockers=[blocked_item],
    upcoming_deadlines=[deadline_item],
    key_achievements=["Completed feature X", "Fixed critical bug"],
    current_focus="Working on authentication API",
    availability_status="Moderately busy"
)
```

#### MeetingMessage

Represents a message in a meeting.

```python
from autonomous_agent_framework.agents.base_agent import MeetingMessage, MessageType

message = MeetingMessage(
    speaker="vivek",
    content="I'm currently working on the authentication API",
    message_type=MessageType.STATUS_UPDATE,
    timestamp=datetime.now(),
    context_used=["active_tasks", "recent_commits"],
    confidence=0.9
)
```

## Configuration Management

### ConfigManager

Handles loading and managing configuration.

```python
from autonomous_agent_framework.config.config_manager import ConfigManager

# Initialize with config file
config_manager = ConfigManager("config/agent_config.yaml")

# Load configuration
config = config_manager.load_config()

# Get employee configuration
employee_config = config_manager.get_employee_config("vivek")

# Create sample configuration
config_manager.create_sample_config("config/sample_config.yaml")
```

### Configuration Structure

```python
from autonomous_agent_framework.config.config_manager import AgentConfig, EmployeeConfig, APICredentials

# API Credentials
api_creds = APICredentials(
    jira_url="https://company.atlassian.net",
    jira_username="user@company.com",
    jira_token="token",
    github_token="github_token",
    confluence_url="https://company.atlassian.net/wiki",
    confluence_username="user@company.com",
    confluence_token="confluence_token"
)

# Employee Configuration
employee = EmployeeConfig(
    name="Vivek Kumar",
    employee_id="vivek",
    email="vivek@company.com",
    jira_username="vivek.kumar",
    github_username="vivek-dev",
    projects=["PROJECT-A"],
    teams=["backend-team"],
    role="Senior Software Engineer"
)
```

## Agent Management

### AgentManager

Manages multiple employee agents.

```python
from autonomous_agent_framework.agents.agent_manager import AgentManager

# Initialize agent manager
agent_manager = AgentManager(config_manager)
await agent_manager.initialize()

# Get an agent
agent = await agent_manager.get_agent("vivek")

# Update context for all agents
results = await agent_manager.update_all_contexts()

# Get agent status
status = await agent_manager.get_agent_status("vivek")

# Get team summary
team_summary = await agent_manager.get_team_summary("backend-team")

# Prepare agents for meeting
preparation = await agent_manager.prepare_agents_for_meeting(["vivek", "sarah"])
```

### AgentOrchestrator

Coordinates multiple agents in meetings.

```python
from autonomous_agent_framework.agents.base_agent import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Register agents
orchestrator.register_agent(agent1)
orchestrator.register_agent(agent2)

# Start a meeting
await orchestrator.start_meeting(meeting_context)

# End a meeting
summary = await orchestrator.end_meeting(meeting_id)
```

## Meeting Engine

### MeetingSimulator

Simulates text-based meetings with multiple agents.

```python
from autonomous_agent_framework.meeting_engine.meeting_simulator import MeetingSimulator

simulator = MeetingSimulator()

# Create a meeting
meeting_id = await simulator.create_meeting(
    title="Daily Standup",
    participants=["vivek", "sarah", "alex"],
    agenda="Status updates and blockers",
    duration_minutes=15,
    meeting_type="standup"
)

# Start the meeting
await simulator.start_meeting(meeting_id, agents_dict)

# Get meeting status
meeting = simulator.get_meeting(meeting_id)
transcript = meeting.get_transcript()

# End the meeting
completed_meeting = await simulator.end_meeting(meeting_id)
```

### ConversationManager

Manages conversation flow and turn-taking.

```python
from autonomous_agent_framework.meeting_engine.conversation_manager import ConversationManager, TurnTakingStrategy

# Initialize conversation manager
conv_manager = ConversationManager(strategy=TurnTakingStrategy.NATURAL_FLOW)

# Initialize conversation
conv_manager.initialize_conversation(
    participants=["vivek", "sarah", "alex"],
    facilitator="sarah"
)

# Start conversation
await conv_manager.start_conversation("Good morning everyone!")

# Add messages
await conv_manager.add_message("vivek", "Good morning! I'm working on the API.", MessageType.STATUS_UPDATE)

# Get next speaker
next_speaker = conv_manager.get_next_speaker()

# Get conversation statistics
stats = conv_manager.get_conversation_stats()
summary = conv_manager.get_conversation_summary()
```

## Context Building

### ContextBuilder

Aggregates context from multiple sources.

```python
from autonomous_agent_framework.context_builder.context_builder import ContextBuilder

# Initialize with connectors
context_builder = ContextBuilder(
    jira_connector=jira_connector,
    github_connector=github_connector,
    confluence_connector=confluence_connector
)

# Build context for an employee
context = await context_builder.build_context("vivek", days_back=7)

# Get meeting-specific context
meeting_context_data = await context_builder.get_context_for_meeting(
    "vivek", 
    {"meeting_type": "standup", "agenda": "Daily updates"}
)
```

## Post-Meeting Processing

### PostMeetingActionHandler

Processes meeting outcomes and creates follow-up actions.

```python
from autonomous_agent_framework.post_meeting.action_handler import PostMeetingActionHandler

# Initialize action handler
action_handler = PostMeetingActionHandler(
    jira_connector=jira_connector,
    confluence_connector=confluence_connector
)

# Create meeting summary
summary = await action_handler.create_summary(messages, meeting_context)

# Extract action items
action_items = await action_handler.extract_action_items(messages, meeting_context)

# Create Jira tickets
ticket_keys = await action_handler.create_jira_tickets(action_items)

# Update Confluence
page_id = await action_handler.update_confluence(summary)

# Process complete meeting
results = await action_handler.process_meeting_completion(messages, meeting_context)
```

## API Connectors

### JiraConnector

Interfaces with Jira API for work item management.

```python
from autonomous_agent_framework.api_connectors.jira_connector import JiraConnector

# Initialize connector
jira = JiraConnector(
    jira_url="https://company.atlassian.net",
    username="user@company.com",
    token="api_token"
)

# Connect to Jira
await jira.connect()

# Extract context
work_items = await jira.extract_context("vivek", days_back=7)

# Get recent activity
activity = await jira.get_recent_activity("vivek", days_back=7)

# Get blockers
blockers = await jira.get_blockers("vivek")

# Get upcoming deadlines
deadlines = await jira.get_upcoming_deadlines("vivek", days_ahead=14)

# Create ticket
ticket_key = await jira.create_ticket(
    project_key="PROJ",
    summary="Action item from meeting",
    description="Follow up on authentication API",
    assignee="vivek"
)
```

### GitHubConnector

Interfaces with GitHub API for code activity monitoring.

```python
from autonomous_agent_framework.api_connectors.github_connector import GitHubConnector

# Initialize connector
github = GitHubConnector(token="github_token")

# Connect to GitHub
await github.connect()

# Extract context
work_items = await github.extract_context("vivek-dev", days_back=7)

# Get recent activity
activity = await github.get_recent_activity("vivek-dev", days_back=7)

# Get repository stats
stats = await github.get_repository_stats("vivek-dev", ["repo1", "repo2"])

# Get code review activity
reviews = await github.get_code_review_activity("vivek-dev", days_back=7)
```

### ConfluenceConnector

Interfaces with Confluence API for documentation management.

```python
from autonomous_agent_framework.api_connectors.confluence_connector import ConfluenceConnector

# Initialize connector
confluence = ConfluenceConnector(
    confluence_url="https://company.atlassian.net/wiki",
    username="user@company.com",
    token="api_token"
)

# Connect to Confluence
await confluence.connect()

# Extract context
work_items = await confluence.extract_context("vivek.kumar", days_back=7)

# Get recent activity
activity = await confluence.get_recent_activity("vivek.kumar", days_back=7)

# Create page
page_id = await confluence.create_page(
    space_key="MEETINGS",
    title="Meeting Summary - 2024-01-15",
    content="<h1>Meeting Summary</h1><p>Key points...</p>"
)

# Search content
results = await confluence.search_content("authentication API", space_key="TECH")
```

## Examples

### Complete Workflow Example

```python
import asyncio
from autonomous_agent_framework.config.config_manager import ConfigManager
from autonomous_agent_framework.agents.agent_manager import AgentManager
from autonomous_agent_framework.meeting_engine.meeting_simulator import MeetingSimulator
from autonomous_agent_framework.post_meeting.action_handler import PostMeetingActionHandler

async def run_complete_workflow():
    # 1. Initialize configuration
    config_manager = ConfigManager("config/agent_config.yaml")
    
    # 2. Initialize agents
    agent_manager = AgentManager(config_manager)
    await agent_manager.initialize()
    
    # 3. Create and run meeting
    meeting_simulator = MeetingSimulator()
    meeting_id = await meeting_simulator.create_meeting(
        title="Daily Standup",
        participants=["vivek", "sarah", "alex"],
        meeting_type="standup"
    )
    
    await meeting_simulator.start_meeting(meeting_id, agent_manager.agents)
    completed_meeting = await meeting_simulator.end_meeting(meeting_id)
    
    # 4. Process meeting results
    action_handler = PostMeetingActionHandler()
    results = await action_handler.process_meeting_completion(
        completed_meeting.messages,
        completed_meeting.context
    )
    
    print(f"Meeting completed with {len(results['summary'].action_items)} action items")
    return results

# Run the workflow
results = asyncio.run(run_complete_workflow())
```

### Custom Agent Example

```python
from autonomous_agent_framework.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    async def initialize(self):
        # Custom initialization logic
        pass
    
    async def update_context(self):
        # Custom context loading
        pass
    
    async def generate_response(self, message, meeting_context):
        # Custom response generation
        return MeetingMessage(
            speaker=self.employee_id,
            content="Custom response",
            message_type=MessageType.GENERAL,
            timestamp=datetime.now()
        )
    
    async def handle_question(self, question, meeting_context):
        # Custom question handling
        pass
```

### Error Handling

```python
try:
    # Initialize agent
    agent = EmployeeAgent("vivek", config)
    await agent.initialize()
    
    # Update context with error handling
    try:
        context = await agent.update_context()
    except Exception as e:
        logger.error(f"Failed to update context: {e}")
        # Handle gracefully or use cached context
        
except Exception as e:
    logger.error(f"Agent initialization failed: {e}")
    # Handle initialization failure
```

## Best Practices

1. **Error Handling**: Always wrap API calls in try-catch blocks
2. **Context Caching**: Cache context to avoid excessive API calls
3. **Rate Limiting**: Respect API rate limits for external services
4. **Logging**: Use structured logging for debugging and monitoring
5. **Configuration**: Use environment variables for sensitive data
6. **Testing**: Use mock connectors for testing without real API calls

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the framework is properly installed and in Python path
2. **API Authentication**: Verify API tokens and credentials are correct
3. **Rate Limiting**: Implement backoff strategies for API calls
4. **Memory Usage**: Monitor memory usage with large context windows
5. **Network Issues**: Handle network timeouts and connection errors

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

1. Use async/await for concurrent operations
2. Implement context caching for frequently accessed data
3. Limit context window size for better performance
4. Use connection pooling for database operations

