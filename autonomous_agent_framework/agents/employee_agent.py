"""
Employee agent implementation that represents an individual employee
in meetings and handles their work context.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from ..agents.base_agent import (
    BaseAgent, ContextSummary, MeetingMessage, MeetingContext, 
    MessageType, WorkItem, Priority
)
from ..context_builder.context_builder import ContextBuilder
from ..api_connectors.jira_connector import JiraConnector
from ..api_connectors.github_connector import GitHubConnector
from ..api_connectors.confluence_connector import ConfluenceConnector
from ..config.config_manager import EmployeeConfig


class EmployeeAgent(BaseAgent):
    """Agent representing an individual employee."""
    
    def __init__(self, employee_id: str, config: Dict[str, Any]):
        super().__init__(employee_id, config)
        self.employee_config: Optional[EmployeeConfig] = None
        self.context_builder: Optional[ContextBuilder] = None
        self.jira_connector: Optional[JiraConnector] = None
        self.github_connector: Optional[GitHubConnector] = None
        self.confluence_connector: Optional[ConfluenceConnector] = None
        self.meeting_history: List[Dict[str, Any]] = []
        
    async def initialize(self) -> None:
        """Initialize the agent with necessary data and connections."""
        self.logger.info(f"Initializing agent for {self.employee_id}")
        
        # Load employee configuration
        self.employee_config = self.config.get('employee_config')
        if not self.employee_config:
            raise ValueError(f"No configuration found for employee {self.employee_id}")
        
        # Initialize API connectors based on available credentials
        api_creds = self.config.get('api_credentials', {})
        
        # Initialize Jira connector
        if (api_creds.get('jira_url') and 
            api_creds.get('jira_username') and 
            api_creds.get('jira_token')):
            self.jira_connector = JiraConnector(
                api_creds['jira_url'],
                api_creds['jira_username'],
                api_creds['jira_token']
            )
            await self.jira_connector.connect()
            self.logger.info("Jira connector initialized")
        
        # Initialize GitHub connector
        if api_creds.get('github_token'):
            self.github_connector = GitHubConnector(api_creds['github_token'])
            await self.github_connector.connect()
            self.logger.info("GitHub connector initialized")
        
        # Initialize Confluence connector
        if (api_creds.get('confluence_url') and 
            api_creds.get('confluence_username') and 
            api_creds.get('confluence_token')):
            self.confluence_connector = ConfluenceConnector(
                api_creds['confluence_url'],
                api_creds['confluence_username'],
                api_creds['confluence_token']
            )
            await self.confluence_connector.connect()
            self.logger.info("Confluence connector initialized")
        
        # Initialize context builder
        self.context_builder = ContextBuilder(
            self.jira_connector,
            self.github_connector,
            self.confluence_connector
        )
        
        # Load initial context
        await self.update_context()
        
        self.logger.info(f"Agent initialization complete for {self.employee_id}")
    
    async def update_context(self) -> ContextSummary:
        """Update and return the current work context."""
        if not self.context_builder:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        self.logger.info(f"Updating context for {self.employee_id}")
        
        # Use the appropriate username for each service
        jira_username = self.employee_config.jira_username or self.employee_id
        github_username = self.employee_config.github_username or self.employee_id
        confluence_username = self.employee_config.confluence_username or self.employee_id
        
        # Build context using the most appropriate username for each service
        # For now, we'll use the employee_id as fallback
        context_username = github_username if self.github_connector else jira_username
        
        self.context = await self.context_builder.build_context(context_username)
        self.last_context_update = datetime.now()
        
        self.logger.info(f"Context updated for {self.employee_id}: "
                        f"{len(self.context.active_tasks)} active tasks, "
                        f"{len(self.context.blockers)} blockers")
        
        return self.context
    
    async def generate_response(self, message: str, meeting_context: MeetingContext) -> MeetingMessage:
        """Generate a response to a message in a meeting."""
        if not self.context:
            await self.update_context()
        
        # Analyze the message to determine response type
        message_lower = message.lower()
        response_type = MessageType.GENERAL
        
        # Determine if this is a status update request
        if any(keyword in message_lower for keyword in ['status', 'update', 'progress', 'working on']):
            response_type = MessageType.STATUS_UPDATE
            response_content = self._generate_status_update()
        
        # Check if it's about blockers
        elif any(keyword in message_lower for keyword in ['blocker', 'blocked', 'impediment', 'stuck']):
            response_type = MessageType.BLOCKER
            response_content = self._generate_blocker_update()
        
        # Check if it's a question directed at this agent
        elif self.employee_config.name.lower() in message_lower or self.employee_id in message_lower:
            response_type = MessageType.ANSWER
            response_content = await self._generate_contextual_answer(message)
        
        else:
            # General response or no response needed
            return None
        
        return MeetingMessage(
            speaker=self.employee_id,
            content=response_content,
            message_type=response_type,
            timestamp=datetime.now(),
            context_used=self._get_context_summary(),
            confidence=0.8
        )
    
    async def handle_question(self, question: str, meeting_context: MeetingContext) -> MeetingMessage:
        """Handle a direct question in a meeting."""
        if not self.context:
            await self.update_context()
        
        response_content = await self._generate_contextual_answer(question)
        
        return MeetingMessage(
            speaker=self.employee_id,
            content=response_content,
            message_type=MessageType.ANSWER,
            timestamp=datetime.now(),
            context_used=self._get_context_summary(),
            confidence=0.9
        )
    
    def _generate_status_update(self) -> str:
        """Generate a status update based on current context."""
        if not self.context:
            return "I don't have current context available."
        
        update_parts = []
        
        # Current focus
        if self.context.current_focus:
            update_parts.append(f"Currently {self.context.current_focus.lower()}")
        
        # Key achievements
        if self.context.key_achievements:
            achievements = self.context.key_achievements[:2]  # Top 2 achievements
            update_parts.append(f"Recent progress: {', '.join(achievements)}")
        
        # Active tasks count
        if self.context.active_tasks:
            high_priority = len([task for task in self.context.active_tasks 
                               if task.priority in [Priority.HIGH, Priority.CRITICAL]])
            if high_priority > 0:
                update_parts.append(f"Working on {len(self.context.active_tasks)} tasks ({high_priority} high priority)")
            else:
                update_parts.append(f"Working on {len(self.context.active_tasks)} tasks")
        
        # Availability
        update_parts.append(f"Status: {self.context.availability_status}")
        
        return ". ".join(update_parts) + "."
    
    def _generate_blocker_update(self) -> str:
        """Generate an update about current blockers."""
        if not self.context or not self.context.blockers:
            return "No current blockers."
        
        blocker_count = len(self.context.blockers)
        if blocker_count == 1:
            blocker = self.context.blockers[0]
            return f"I have 1 blocker: {blocker.title} - need help to resolve this."
        else:
            return f"I have {blocker_count} blockers that need attention for resolution."
    
    async def _generate_contextual_answer(self, question: str) -> str:
        """Generate a contextual answer to a question."""
        if not self.context:
            return "I don't have current context to answer that question."
        
        question_lower = question.lower()
        
        # Handle specific question types
        if any(keyword in question_lower for keyword in ['deadline', 'due', 'when']):
            return self._answer_deadline_question()
        
        elif any(keyword in question_lower for keyword in ['priority', 'important', 'urgent']):
            return self._answer_priority_question()
        
        elif any(keyword in question_lower for keyword in ['capacity', 'available', 'bandwidth']):
            return self._answer_capacity_question()
        
        elif any(keyword in question_lower for keyword in ['project', 'working on']):
            return self._answer_project_question()
        
        else:
            # Generic response based on current focus
            return f"Based on my current work, {self.context.current_focus.lower()}. {self.context.availability_status}."
    
    def _answer_deadline_question(self) -> str:
        """Answer questions about deadlines."""
        if not self.context.upcoming_deadlines:
            return "I don't have any upcoming deadlines in the next two weeks."
        
        urgent_deadlines = [task for task in self.context.upcoming_deadlines 
                          if task.due_date and task.due_date <= datetime.now() + timedelta(days=3)]
        
        if urgent_deadlines:
            task = urgent_deadlines[0]
            days_left = (task.due_date - datetime.now()).days
            return f"I have an urgent deadline: {task.title} due in {days_left} days."
        else:
            task = self.context.upcoming_deadlines[0]
            days_left = (task.due_date - datetime.now()).days
            return f"Next deadline: {task.title} due in {days_left} days."
    
    def _answer_priority_question(self) -> str:
        """Answer questions about priorities."""
        high_priority_tasks = [task for task in self.context.active_tasks 
                             if task.priority in [Priority.HIGH, Priority.CRITICAL]]
        
        if not high_priority_tasks:
            return "No high-priority tasks at the moment."
        
        if len(high_priority_tasks) == 1:
            return f"My top priority is: {high_priority_tasks[0].title}"
        else:
            return f"I have {len(high_priority_tasks)} high-priority tasks to focus on."
    
    def _answer_capacity_question(self) -> str:
        """Answer questions about capacity and availability."""
        return f"Current status: {self.context.availability_status}. " \
               f"I have {len(self.context.active_tasks)} active tasks."
    
    def _answer_project_question(self) -> str:
        """Answer questions about current projects."""
        if not self.employee_config.projects:
            return f"Currently {self.context.current_focus.lower()}."
        
        projects = ", ".join(self.employee_config.projects[:3])  # Top 3 projects
        return f"Working on projects: {projects}. Currently {self.context.current_focus.lower()}."
    
    def _get_context_summary(self) -> List[str]:
        """Get a summary of context used for response generation."""
        if not self.context:
            return []
        
        summary = []
        if self.context.active_tasks:
            summary.append(f"{len(self.context.active_tasks)} active tasks")
        if self.context.blockers:
            summary.append(f"{len(self.context.blockers)} blockers")
        if self.context.upcoming_deadlines:
            summary.append(f"{len(self.context.upcoming_deadlines)} upcoming deadlines")
        if self.context.recent_commits:
            summary.append(f"{len(self.context.recent_commits)} recent commits")
        
        return summary
    
    async def join_meeting(self, meeting_context: MeetingContext) -> None:
        """Join a meeting."""
        self.logger.info(f"Agent {self.employee_id} joining meeting: {meeting_context.meeting_id}")
        
        # Update context before joining if needed
        if self.should_update_context():
            await self.update_context()
        
        # Record meeting participation
        self.meeting_history.append({
            'meeting_id': meeting_context.meeting_id,
            'title': meeting_context.title,
            'joined_at': datetime.now(),
            'participants': meeting_context.participants
        })
    
    async def leave_meeting(self, meeting_id: str) -> None:
        """Leave a meeting."""
        self.logger.info(f"Agent {self.employee_id} leaving meeting: {meeting_id}")
        
        # Update meeting history
        for meeting in self.meeting_history:
            if meeting['meeting_id'] == meeting_id:
                meeting['left_at'] = datetime.now()
                break
    
    def get_meeting_preparation_summary(self, meeting_context: MeetingContext) -> Dict[str, Any]:
        """Get a summary to prepare for a meeting."""
        if not self.context:
            return {}
        
        return {
            'employee_name': self.employee_config.name,
            'current_focus': self.context.current_focus,
            'availability': self.context.availability_status,
            'key_updates': self.context.key_achievements[:3],
            'blockers': [blocker.title for blocker in self.context.blockers],
            'upcoming_deadlines': [
                f"{task.title} (due {task.due_date.strftime('%Y-%m-%d')})" 
                for task in self.context.upcoming_deadlines[:3]
                if task.due_date
            ],
            'active_task_count': len(self.context.active_tasks),
            'last_context_update': self.last_context_update.isoformat() if self.last_context_update else None
        }

