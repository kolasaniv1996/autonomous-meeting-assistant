"""
Example implementation demonstrating the autonomous agent framework
with sample data for employee "Vivek".
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os

# Add the framework to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autonomous_agent_framework.config.config_manager import ConfigManager
from autonomous_agent_framework.agents.agent_manager import AgentManager
from autonomous_agent_framework.meeting_engine.meeting_simulator import MeetingSimulator
from autonomous_agent_framework.post_meeting.action_handler import PostMeetingActionHandler
from autonomous_agent_framework.agents.base_agent import MeetingContext, WorkItem, Priority


class MockJiraConnector:
    """Mock Jira connector for testing without real API credentials."""
    
    def __init__(self):
        self.logger = logging.getLogger("mock_jira")
        
    async def connect(self):
        self.logger.info("Mock Jira connector connected")
        
    async def extract_context(self, employee_id: str, days_back: int = 7) -> List[WorkItem]:
        """Return sample Jira work items for testing."""
        sample_items = [
            WorkItem(
                id="PROJ-123",
                title="Implement user authentication API",
                description="Create REST API endpoints for user login and registration",
                status="In Progress",
                priority=Priority.HIGH,
                assignee=employee_id,
                created_date=datetime.now() - timedelta(days=5),
                updated_date=datetime.now() - timedelta(days=1),
                due_date=datetime.now() + timedelta(days=3),
                source="jira",
                url="https://company.atlassian.net/browse/PROJ-123",
                labels=["backend", "api", "authentication"],
                comments=["Started implementation", "Need to review security requirements"]
            ),
            WorkItem(
                id="PROJ-124",
                title="Fix database connection pooling issue",
                description="Resolve connection timeout issues in production",
                status="To Do",
                priority=Priority.MEDIUM,
                assignee=employee_id,
                created_date=datetime.now() - timedelta(days=3),
                updated_date=datetime.now() - timedelta(days=2),
                due_date=datetime.now() + timedelta(days=7),
                source="jira",
                url="https://company.atlassian.net/browse/PROJ-124",
                labels=["backend", "database", "bug"],
                comments=["Investigating root cause"]
            )
        ]
        return sample_items
    
    async def get_recent_activity(self, employee_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Return sample recent activity."""
        return [
            {
                'type': 'status_change',
                'issue_key': 'PROJ-123',
                'issue_title': 'Implement user authentication API',
                'from_status': 'To Do',
                'to_status': 'In Progress',
                'timestamp': datetime.now() - timedelta(days=1),
                'author': 'Vivek Kumar'
            },
            {
                'type': 'comment',
                'issue_key': 'PROJ-123',
                'issue_title': 'Implement user authentication API',
                'comment': 'Started working on the JWT token implementation',
                'timestamp': datetime.now() - timedelta(hours=6),
                'author': 'Vivek Kumar'
            }
        ]


class MockGitHubConnector:
    """Mock GitHub connector for testing without real API credentials."""
    
    def __init__(self):
        self.logger = logging.getLogger("mock_github")
        
    async def connect(self):
        self.logger.info("Mock GitHub connector connected")
        
    async def extract_context(self, employee_id: str, days_back: int = 7) -> List[WorkItem]:
        """Return sample GitHub work items for testing."""
        sample_items = [
            WorkItem(
                id="auth-service#PR15",
                title="PR: Add JWT authentication middleware",
                description="Implements JWT token validation middleware for API routes",
                status="open",
                priority=Priority.HIGH,
                assignee=employee_id,
                created_date=datetime.now() - timedelta(days=2),
                updated_date=datetime.now() - timedelta(hours=4),
                due_date=None,
                source="github",
                url="https://github.com/company/auth-service/pull/15",
                labels=["pull-request", "authentication", "backend"],
                comments=["LGTM from security team", "Need to add more tests"]
            )
        ]
        return sample_items
    
    async def get_recent_activity(self, employee_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Return sample recent GitHub activity."""
        return [
            {
                'type': 'commit',
                'repo': 'auth-service',
                'message': 'Add JWT token validation middleware',
                'sha': 'abc12345',
                'timestamp': datetime.now() - timedelta(hours=4),
                'url': 'https://github.com/company/auth-service/commit/abc12345',
                'files_changed': 3
            },
            {
                'type': 'pull_request',
                'repo': 'auth-service',
                'title': 'Add JWT authentication middleware',
                'number': 15,
                'timestamp': datetime.now() - timedelta(days=2),
                'url': 'https://github.com/company/auth-service/pull/15',
                'state': 'open',
                'merged': False
            }
        ]


class MockConfluenceConnector:
    """Mock Confluence connector for testing without real API credentials."""
    
    def __init__(self):
        self.logger = logging.getLogger("mock_confluence")
        
    async def connect(self):
        self.logger.info("Mock Confluence connector connected")
        
    async def extract_context(self, employee_id: str, days_back: int = 7) -> List[WorkItem]:
        """Return sample Confluence work items for testing."""
        sample_items = [
            WorkItem(
                id="12345",
                title="Authentication Service Architecture",
                description="Documentation for the new authentication service design and implementation",
                status="current",
                priority=Priority.MEDIUM,
                assignee=employee_id,
                created_date=datetime.now() - timedelta(days=4),
                updated_date=datetime.now() - timedelta(days=1),
                due_date=None,
                source="confluence",
                url="https://company.atlassian.net/wiki/spaces/TECH/pages/12345",
                labels=["architecture", "authentication"],
                comments=[]
            )
        ]
        return sample_items
    
    async def get_recent_activity(self, employee_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Return sample recent Confluence activity."""
        return [
            {
                'type': 'page_update',
                'page_id': '12345',
                'title': 'Authentication Service Architecture',
                'space': 'Technical Documentation',
                'timestamp': datetime.now() - timedelta(days=1),
                'url': 'https://company.atlassian.net/wiki/spaces/TECH/pages/12345',
                'version': 3
            }
        ]


async def setup_mock_environment():
    """Set up the mock environment for testing."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a mock configuration
    mock_config = {
        'api_credentials': {
            'jira_url': 'https://mock-company.atlassian.net',
            'jira_username': 'test@company.com',
            'jira_token': 'mock-token',
            'github_token': 'mock-github-token',
            'confluence_url': 'https://mock-company.atlassian.net/wiki',
            'confluence_username': 'test@company.com',
            'confluence_token': 'mock-confluence-token',
            'openai_api_key': 'mock-openai-key'
        },
        'employees': {
            'vivek': {
                'name': 'Vivek Kumar',
                'employee_id': 'vivek',
                'email': 'vivek@company.com',
                'jira_username': 'vivek.kumar',
                'github_username': 'vivek-dev',
                'confluence_username': 'vivek.kumar',
                'projects': ['PROJECT-A', 'PROJECT-B'],
                'teams': ['backend-team', 'platform-team'],
                'role': 'Senior Software Engineer',
                'manager': 'sarah'
            },
            'sarah': {
                'name': 'Sarah Johnson',
                'employee_id': 'sarah',
                'email': 'sarah@company.com',
                'jira_username': 'sarah.johnson',
                'github_username': 'sarah-manager',
                'confluence_username': 'sarah.johnson',
                'projects': ['PROJECT-A', 'PROJECT-B', 'PROJECT-C'],
                'teams': ['backend-team', 'platform-team', 'management'],
                'role': 'Engineering Manager',
                'manager': None
            },
            'alex': {
                'name': 'Alex Chen',
                'employee_id': 'alex',
                'email': 'alex@company.com',
                'jira_username': 'alex.chen',
                'github_username': 'alex-frontend',
                'confluence_username': 'alex.chen',
                'projects': ['PROJECT-B', 'PROJECT-D'],
                'teams': ['frontend-team', 'ui-ux-team'],
                'role': 'Frontend Developer',
                'manager': 'sarah'
            }
        },
        'meeting_config': {
            'max_response_length': 200,
            'context_window_days': 7,
            'auto_join_meetings': True,
            'create_summaries': True,
            'create_action_items': True,
            'update_jira_tickets': True
        },
        'llm_model': 'gpt-3.5-turbo',
        'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
        'log_level': 'INFO'
    }
    
    return mock_config


async def test_agent_initialization(mock_config):
    """Test agent initialization with mock data."""
    print("\\n=== Testing Agent Initialization ===")
    
    # Create a mock config manager
    class MockConfigManager:
        def __init__(self, config):
            self.mock_config = config
            
        def load_config(self):
            from autonomous_agent_framework.config.config_manager import AgentConfig
            return AgentConfig(**self.mock_config)
    
    config_manager = MockConfigManager(mock_config)
    agent_manager = AgentManager(config_manager)
    
    # Override the connectors with mock versions
    await agent_manager.initialize()
    
    # Replace real connectors with mock ones for testing
    for agent in agent_manager.agents.values():
        agent.jira_connector = MockJiraConnector()
        agent.github_connector = MockGitHubConnector()
        agent.confluence_connector = MockConfluenceConnector()
        
        # Reinitialize context builder with mock connectors
        from autonomous_agent_framework.context_builder.context_builder import ContextBuilder
        agent.context_builder = ContextBuilder(
            agent.jira_connector,
            agent.github_connector,
            agent.confluence_connector
        )
    
    print(f"✓ Initialized {len(agent_manager.agents)} agents")
    
    # Test context loading for Vivek
    vivek_agent = await agent_manager.get_agent('vivek')
    if vivek_agent:
        await vivek_agent.update_context()
        print(f"✓ Loaded context for Vivek: {len(vivek_agent.context.active_tasks)} active tasks")
        print(f"  Current focus: {vivek_agent.context.current_focus}")
        print(f"  Availability: {vivek_agent.context.availability_status}")
    
    return agent_manager


async def test_meeting_simulation(agent_manager):
    """Test meeting simulation with multiple agents."""
    print("\\n=== Testing Meeting Simulation ===")
    
    # Create meeting simulator
    meeting_simulator = MeetingSimulator()
    
    # Create a standup meeting
    meeting_id = await meeting_simulator.create_meeting(
        title="Daily Standup - Backend Team",
        participants=['vivek', 'sarah', 'alex'],
        agenda="Daily standup: status updates, blockers, planning",
        duration_minutes=15,
        meeting_type="standup"
    )
    
    print(f"✓ Created meeting: {meeting_id}")
    
    # Start the meeting
    await meeting_simulator.start_meeting(meeting_id, agent_manager.agents)
    print("✓ Started meeting simulation")
    
    # Let the meeting run for a bit
    await asyncio.sleep(2)
    
    # Get meeting transcript
    meeting = meeting_simulator.get_meeting(meeting_id)
    if meeting:
        transcript = meeting.get_transcript()
        print(f"✓ Meeting generated {len(transcript)} messages")
        
        # Print sample messages
        for i, msg in enumerate(transcript[:5]):
            print(f"  {msg['speaker']}: {msg['content'][:80]}...")
    
    # End the meeting
    completed_meeting = await meeting_simulator.end_meeting(meeting_id)
    print("✓ Meeting completed")
    
    return completed_meeting


async def test_post_meeting_actions(completed_meeting):
    """Test post-meeting action processing."""
    print("\\n=== Testing Post-Meeting Actions ===")
    
    if not completed_meeting:
        print("✗ No completed meeting to process")
        return
    
    # Create post-meeting handler with mock connectors
    action_handler = PostMeetingActionHandler(
        jira_connector=MockJiraConnector(),
        confluence_connector=MockConfluenceConnector()
    )
    
    # Process the meeting
    results = await action_handler.process_meeting_completion(
        completed_meeting.messages,
        completed_meeting.context
    )
    
    print(f"✓ Generated meeting summary with:")
    if results['summary']:
        summary = results['summary']
        print(f"  - {len(summary.key_points)} key points")
        print(f"  - {len(summary.decisions_made)} decisions")
        print(f"  - {len(summary.action_items)} action items")
        print(f"  - {len(summary.blockers_discussed)} blockers")
        
        # Print sample key points
        if summary.key_points:
            print("  Sample key points:")
            for point in summary.key_points[:3]:
                print(f"    • {point[:80]}...")
    
    print(f"✓ Would create {len(results['jira_tickets'])} Jira tickets")
    print(f"✓ Would create Confluence page: {results['confluence_page']}")
    
    if results['errors']:
        print(f"⚠ Encountered {len(results['errors'])} errors:")
        for error in results['errors']:
            print(f"    - {error}")
    
    return results


async def test_team_status_summary(agent_manager):
    """Test team status summary functionality."""
    print("\\n=== Testing Team Status Summary ===")
    
    # Get team summary
    team_summary = await agent_manager.get_team_summary("backend-team")
    
    print(f"✓ Team summary for backend-team:")
    print(f"  - {team_summary['member_count']} members")
    print(f"  - {team_summary['total_active_tasks']} total active tasks")
    print(f"  - {team_summary['total_blockers']} total blockers")
    
    print("  Member status:")
    for member in team_summary['members']:
        print(f"    • {member['name']}: {member['availability']} "
              f"({member['active_tasks']} tasks, {member['blockers']} blockers)")
    
    return team_summary


async def main():
    """Main function to run all tests."""
    print("🚀 Starting Autonomous Agent Framework Demo")
    print("=" * 50)
    
    try:
        # Setup mock environment
        mock_config = await setup_mock_environment()
        print("✓ Mock environment configured")
        
        # Test agent initialization
        agent_manager = await test_agent_initialization(mock_config)
        
        # Test meeting simulation
        completed_meeting = await test_meeting_simulation(agent_manager)
        
        # Test post-meeting actions
        await test_post_meeting_actions(completed_meeting)
        
        # Test team status
        await test_team_status_summary(agent_manager)
        
        print("\\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("\\nThe autonomous agent framework demonstrated:")
        print("  ✓ Agent initialization and context loading")
        print("  ✓ Multi-agent meeting simulation")
        print("  ✓ Intelligent conversation flow")
        print("  ✓ Post-meeting summary generation")
        print("  ✓ Action item extraction")
        print("  ✓ Team status monitoring")
        
    except Exception as e:
        print(f"\\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

