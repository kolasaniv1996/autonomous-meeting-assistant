"""
Core agent architecture and base classes for the Autonomous Agent Framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import logging


class MessageType(Enum):
    """Types of messages in meetings."""
    STATUS_UPDATE = "status_update"
    QUESTION = "question"
    ANSWER = "answer"
    BLOCKER = "blocker"
    ACTION_ITEM = "action_item"
    GENERAL = "general"


class Priority(Enum):
    """Priority levels for tasks and issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkItem(BaseModel):
    """Represents a work item from any source (Jira, GitHub, etc.)."""
    id: str
    title: str
    description: str
    status: str
    priority: Priority
    assignee: Optional[str] = None
    created_date: datetime
    updated_date: datetime
    due_date: Optional[datetime] = None
    source: str  # 'jira', 'github', 'confluence'
    url: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    comments: List[str] = Field(default_factory=list)


class ContextSummary(BaseModel):
    """Summary of an employee's current work context."""
    employee_id: str
    generated_at: datetime
    active_tasks: List[WorkItem]
    recent_commits: List[Dict[str, Any]]
    blockers: List[WorkItem]
    upcoming_deadlines: List[WorkItem]
    key_achievements: List[str]
    current_focus: str
    availability_status: str


class MeetingMessage(BaseModel):
    """Represents a message in a meeting."""
    speaker: str
    content: str
    message_type: MessageType
    timestamp: datetime
    context_used: Optional[List[str]] = None
    confidence: float = 1.0


class MeetingContext(BaseModel):
    """Context for a meeting."""
    meeting_id: str
    title: str
    participants: List[str]
    agenda: Optional[str] = None
    start_time: datetime
    duration_minutes: int
    meeting_type: str = "standup"  # standup, planning, review, etc.


class ActionItem(BaseModel):
    """Represents an action item from a meeting."""
    id: str
    description: str
    assignee: str
    due_date: Optional[datetime] = None
    priority: Priority
    meeting_id: str
    created_at: datetime
    status: str = "open"


class MeetingSummary(BaseModel):
    """Summary of a meeting."""
    meeting_id: str
    title: str
    participants: List[str]
    start_time: datetime
    end_time: datetime
    key_points: List[str]
    decisions_made: List[str]
    action_items: List[ActionItem]
    blockers_discussed: List[str]
    next_meeting: Optional[datetime] = None


class BaseAgent(ABC):
    """Base class for all agents in the framework."""
    
    def __init__(self, employee_id: str, config: Dict[str, Any]):
        self.employee_id = employee_id
        self.config = config
        self.logger = logging.getLogger(f"agent.{employee_id}")
        self.context: Optional[ContextSummary] = None
        self.last_context_update: Optional[datetime] = None
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent with necessary data and connections."""
        pass
    
    @abstractmethod
    async def update_context(self) -> ContextSummary:
        """Update and return the current work context."""
        pass
    
    @abstractmethod
    async def generate_response(self, message: str, meeting_context: MeetingContext) -> MeetingMessage:
        """Generate a response to a message in a meeting."""
        pass
    
    @abstractmethod
    async def handle_question(self, question: str, meeting_context: MeetingContext) -> MeetingMessage:
        """Handle a direct question in a meeting."""
        pass
    
    def should_update_context(self) -> bool:
        """Check if context needs to be updated."""
        if not self.last_context_update:
            return True
        return datetime.now() - self.last_context_update > timedelta(hours=1)


class ContextExtractor(ABC):
    """Base class for context extractors."""
    
    @abstractmethod
    async def extract_context(self, employee_id: str, days_back: int = 7) -> List[WorkItem]:
        """Extract work items for an employee."""
        pass
    
    @abstractmethod
    async def get_recent_activity(self, employee_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get recent activity for an employee."""
        pass


class MeetingParticipant(ABC):
    """Base class for meeting participants."""
    
    @abstractmethod
    async def join_meeting(self, meeting_context: MeetingContext) -> None:
        """Join a meeting."""
        pass
    
    @abstractmethod
    async def leave_meeting(self, meeting_id: str) -> None:
        """Leave a meeting."""
        pass
    
    @abstractmethod
    async def send_message(self, message: MeetingMessage, meeting_id: str) -> None:
        """Send a message in a meeting."""
        pass


class PostMeetingHandler(ABC):
    """Base class for post-meeting action handlers."""
    
    @abstractmethod
    async def create_summary(self, meeting_messages: List[MeetingMessage], 
                           meeting_context: MeetingContext) -> MeetingSummary:
        """Create a meeting summary."""
        pass
    
    @abstractmethod
    async def extract_action_items(self, meeting_messages: List[MeetingMessage],
                                 meeting_context: MeetingContext) -> List[ActionItem]:
        """Extract action items from meeting."""
        pass
    
    @abstractmethod
    async def create_jira_tickets(self, action_items: List[ActionItem]) -> List[str]:
        """Create Jira tickets for action items."""
        pass
    
    @abstractmethod
    async def update_confluence(self, summary: MeetingSummary) -> str:
        """Update Confluence with meeting summary."""
        pass


class AgentOrchestrator:
    """Orchestrates multiple agents in meetings."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.active_meetings: Dict[str, MeetingContext] = {}
        self.logger = logging.getLogger("orchestrator")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent.employee_id] = agent
        self.logger.info(f"Registered agent for {agent.employee_id}")
    
    async def start_meeting(self, meeting_context: MeetingContext) -> None:
        """Start a meeting with relevant agents."""
        self.active_meetings[meeting_context.meeting_id] = meeting_context
        
        # Join relevant agents to the meeting
        for participant in meeting_context.participants:
            if participant in self.agents:
                agent = self.agents[participant]
                if agent.should_update_context():
                    await agent.update_context()
                await agent.join_meeting(meeting_context)
    
    async def end_meeting(self, meeting_id: str) -> MeetingSummary:
        """End a meeting and trigger post-meeting actions."""
        if meeting_id not in self.active_meetings:
            raise ValueError(f"Meeting {meeting_id} not found")
        
        meeting_context = self.active_meetings[meeting_id]
        
        # Have agents leave the meeting
        for participant in meeting_context.participants:
            if participant in self.agents:
                await self.agents[participant].leave_meeting(meeting_id)
        
        # Clean up
        del self.active_meetings[meeting_id]
        
        # Return a placeholder summary (will be implemented in post-meeting handler)
        return MeetingSummary(
            meeting_id=meeting_id,
            title=meeting_context.title,
            participants=meeting_context.participants,
            start_time=meeting_context.start_time,
            end_time=datetime.now(),
            key_points=[],
            decisions_made=[],
            action_items=[],
            blockers_discussed=[]
        )


class AgentFactory:
    """Factory for creating agents."""
    
    @staticmethod
    def create_agent(employee_id: str, config: Dict[str, Any]) -> BaseAgent:
        """Create an agent for an employee."""
        # Import here to avoid circular imports
        from .employee_agent import EmployeeAgent
        return EmployeeAgent(employee_id, config)

