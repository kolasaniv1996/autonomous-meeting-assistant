"""
Meeting simulation engine for text-based multi-agent conversations.
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
from enum import Enum
from ..agents.base_agent import (
    MeetingContext, MeetingMessage, MessageType, 
    BaseAgent, MeetingSummary, ActionItem
)


class MeetingState(Enum):
    """States of a meeting."""
    SCHEDULED = "scheduled"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    ENDING = "ending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MeetingSimulator:
    """Simulates text-based meetings with multiple agents."""
    
    def __init__(self):
        self.active_meetings: Dict[str, 'Meeting'] = {}
        self.meeting_history: List['Meeting'] = []
        self.logger = logging.getLogger("meeting_simulator")
    
    async def create_meeting(self, title: str, participants: List[str], 
                           agenda: Optional[str] = None, 
                           duration_minutes: int = 30,
                           meeting_type: str = "standup") -> str:
        """Create a new meeting."""
        meeting_id = str(uuid.uuid4())
        
        meeting_context = MeetingContext(
            meeting_id=meeting_id,
            title=title,
            participants=participants,
            agenda=agenda,
            start_time=datetime.now(),
            duration_minutes=duration_minutes,
            meeting_type=meeting_type
        )
        
        meeting = Meeting(meeting_context)
        self.active_meetings[meeting_id] = meeting
        
        self.logger.info(f"Created meeting: {meeting_id} - {title}")
        return meeting_id
    
    async def start_meeting(self, meeting_id: str, agents: Dict[str, BaseAgent]) -> None:
        """Start a meeting with the provided agents."""
        if meeting_id not in self.active_meetings:
            raise ValueError(f"Meeting {meeting_id} not found")
        
        meeting = self.active_meetings[meeting_id]
        await meeting.start(agents)
        
        self.logger.info(f"Started meeting: {meeting_id}")
    
    async def end_meeting(self, meeting_id: str) -> Optional['Meeting']:
        """End a meeting and move it to history."""
        if meeting_id not in self.active_meetings:
            return None
        
        meeting = self.active_meetings[meeting_id]
        await meeting.end()
        
        # Move to history
        self.meeting_history.append(meeting)
        del self.active_meetings[meeting_id]
        
        self.logger.info(f"Ended meeting: {meeting_id}")
        return meeting
    
    def get_meeting(self, meeting_id: str) -> Optional['Meeting']:
        """Get a meeting by ID."""
        return self.active_meetings.get(meeting_id)
    
    def get_active_meetings(self) -> List['Meeting']:
        """Get all active meetings."""
        return list(self.active_meetings.values())


class Meeting:
    """Represents a single meeting with multiple agents."""
    
    def __init__(self, context: MeetingContext):
        self.context = context
        self.state = MeetingState.SCHEDULED
        self.agents: Dict[str, BaseAgent] = {}
        self.messages: List[MeetingMessage] = []
        self.current_speaker: Optional[str] = None
        self.speaking_queue: List[str] = []
        self.facilitator: Optional[str] = None
        self.logger = logging.getLogger(f"meeting.{context.meeting_id}")
        
        # Meeting flow control
        self.agenda_items: List[str] = []
        self.current_agenda_item: int = 0
        self.meeting_phases: List[str] = []
        self.current_phase: int = 0
        
        self._setup_meeting_flow()
    
    def _setup_meeting_flow(self) -> None:
        """Setup meeting flow based on meeting type."""
        if self.context.meeting_type == "standup":
            self.meeting_phases = ["opening", "status_updates", "blockers", "planning", "closing"]
            self.agenda_items = [
                "Welcome and introductions",
                "Status updates from each team member",
                "Discussion of blockers and impediments",
                "Planning for upcoming work",
                "Action items and next steps"
            ]
        elif self.context.meeting_type == "planning":
            self.meeting_phases = ["opening", "review", "planning", "estimation", "closing"]
            self.agenda_items = [
                "Review of previous sprint/period",
                "Planning upcoming work",
                "Task estimation and assignment",
                "Risk assessment and mitigation",
                "Summary and action items"
            ]
        elif self.context.meeting_type == "review":
            self.meeting_phases = ["opening", "demo", "feedback", "retrospective", "closing"]
            self.agenda_items = [
                "Demo of completed work",
                "Feedback and discussion",
                "Retrospective on process",
                "Lessons learned",
                "Next steps"
            ]
        else:
            # Generic meeting
            self.meeting_phases = ["opening", "discussion", "decisions", "closing"]
            self.agenda_items = [
                "Opening and agenda review",
                "Main discussion topics",
                "Decision making",
                "Action items and next steps"
            ]
    
    async def start(self, agents: Dict[str, BaseAgent]) -> None:
        """Start the meeting with the provided agents."""
        self.state = MeetingState.STARTING
        
        # Add agents that are participants
        for participant in self.context.participants:
            if participant in agents:
                self.agents[participant] = agents[participant]
                await agents[participant].join_meeting(self.context)
        
        # Set facilitator (first participant or manager if available)
        self.facilitator = self._select_facilitator()
        
        self.state = MeetingState.IN_PROGRESS
        
        # Send opening message
        await self._send_system_message(
            f"Meeting '{self.context.title}' started. "
            f"Participants: {', '.join(self.context.participants)}. "
            f"Facilitator: {self.facilitator}"
        )
        
        # Start the meeting flow
        await self._advance_meeting_phase()
    
    def _select_facilitator(self) -> str:
        """Select a facilitator for the meeting."""
        # Try to find a manager or senior person
        for participant in self.context.participants:
            if participant in self.agents:
                agent = self.agents[participant]
                if (hasattr(agent, 'employee_config') and 
                    agent.employee_config and 
                    'manager' in agent.employee_config.role.lower()):
                    return participant
        
        # Default to first participant
        return self.context.participants[0] if self.context.participants else "system"
    
    async def _advance_meeting_phase(self) -> None:
        """Advance to the next phase of the meeting."""
        if self.current_phase >= len(self.meeting_phases):
            await self.end()
            return
        
        phase = self.meeting_phases[self.current_phase]
        
        if phase == "opening":
            await self._handle_opening_phase()
        elif phase == "status_updates":
            await self._handle_status_updates_phase()
        elif phase == "blockers":
            await self._handle_blockers_phase()
        elif phase == "planning":
            await self._handle_planning_phase()
        elif phase == "closing":
            await self._handle_closing_phase()
        else:
            await self._handle_generic_phase(phase)
        
        self.current_phase += 1
        
        # Continue to next phase after a brief pause
        if self.state == MeetingState.IN_PROGRESS:
            await asyncio.sleep(1)  # Brief pause between phases
            await self._advance_meeting_phase()
    
    async def _handle_opening_phase(self) -> None:
        """Handle the opening phase of the meeting."""
        await self._send_facilitator_message(
            f"Good morning everyone! Let's start our {self.context.meeting_type}. "
            f"Today's agenda: {self.context.agenda or 'Standard agenda items'}"
        )
    
    async def _handle_status_updates_phase(self) -> None:
        """Handle status updates from each participant."""
        await self._send_facilitator_message(
            "Let's go around and get status updates from everyone. "
            "Please share what you've been working on and your current progress."
        )
        
        # Get status updates from each agent
        for participant in self.context.participants:
            if participant in self.agents and participant != self.facilitator:
                agent = self.agents[participant]
                try:
                    response = await agent.generate_response(
                        "Please provide your status update", 
                        self.context
                    )
                    if response:
                        self.messages.append(response)
                        await asyncio.sleep(0.5)  # Brief pause between speakers
                except Exception as e:
                    self.logger.error(f"Failed to get status update from {participant}: {e}")
    
    async def _handle_blockers_phase(self) -> None:
        """Handle discussion of blockers and impediments."""
        await self._send_facilitator_message(
            "Now let's discuss any blockers or impediments. "
            "Does anyone have anything that's preventing them from making progress?"
        )
        
        # Check for blockers from each agent
        for participant in self.context.participants:
            if participant in self.agents and participant != self.facilitator:
                agent = self.agents[participant]
                try:
                    response = await agent.generate_response(
                        "Do you have any blockers or impediments?", 
                        self.context
                    )
                    if response and "no current blockers" not in response.content.lower():
                        self.messages.append(response)
                        await asyncio.sleep(0.5)
                except Exception as e:
                    self.logger.error(f"Failed to get blocker update from {participant}: {e}")
    
    async def _handle_planning_phase(self) -> None:
        """Handle planning for upcoming work."""
        await self._send_facilitator_message(
            "Let's talk about planning for the rest of the week/sprint. "
            "What are your priorities and upcoming deadlines?"
        )
        
        # Get planning input from each agent
        for participant in self.context.participants:
            if participant in self.agents and participant != self.facilitator:
                agent = self.agents[participant]
                try:
                    response = await agent.generate_response(
                        "What are your priorities and upcoming deadlines?", 
                        self.context
                    )
                    if response:
                        self.messages.append(response)
                        await asyncio.sleep(0.5)
                except Exception as e:
                    self.logger.error(f"Failed to get planning input from {participant}: {e}")
    
    async def _handle_closing_phase(self) -> None:
        """Handle the closing phase of the meeting."""
        await self._send_facilitator_message(
            "Thank you everyone for the updates. "
            "I'll send out a summary with any action items. "
            "Have a great rest of your day!"
        )
    
    async def _handle_generic_phase(self, phase: str) -> None:
        """Handle a generic meeting phase."""
        await self._send_facilitator_message(f"Moving to {phase} phase.")
    
    async def _send_facilitator_message(self, content: str) -> None:
        """Send a message from the facilitator."""
        message = MeetingMessage(
            speaker=self.facilitator,
            content=content,
            message_type=MessageType.GENERAL,
            timestamp=datetime.now(),
            confidence=1.0
        )
        self.messages.append(message)
    
    async def _send_system_message(self, content: str) -> None:
        """Send a system message."""
        message = MeetingMessage(
            speaker="system",
            content=content,
            message_type=MessageType.GENERAL,
            timestamp=datetime.now(),
            confidence=1.0
        )
        self.messages.append(message)
    
    async def send_message(self, speaker: str, content: str, 
                          message_type: MessageType = MessageType.GENERAL) -> None:
        """Send a message to the meeting."""
        if speaker not in self.context.participants:
            raise ValueError(f"Speaker {speaker} is not a participant")
        
        message = MeetingMessage(
            speaker=speaker,
            content=content,
            message_type=message_type,
            timestamp=datetime.now(),
            confidence=1.0
        )
        
        self.messages.append(message)
        
        # Generate responses from other agents if appropriate
        await self._handle_message_responses(message)
    
    async def _handle_message_responses(self, message: MeetingMessage) -> None:
        """Handle responses to a message from other agents."""
        # Skip responses for system messages or if meeting is ending
        if message.speaker == "system" or self.state != MeetingState.IN_PROGRESS:
            return
        
        # Check if any agent should respond
        for participant in self.context.participants:
            if (participant != message.speaker and 
                participant in self.agents):
                
                agent = self.agents[participant]
                try:
                    response = await agent.generate_response(message.content, self.context)
                    if response:
                        self.messages.append(response)
                        await asyncio.sleep(0.3)  # Brief pause between responses
                except Exception as e:
                    self.logger.error(f"Failed to get response from {participant}: {e}")
    
    async def end(self) -> None:
        """End the meeting."""
        self.state = MeetingState.ENDING
        
        # Have all agents leave the meeting
        for participant, agent in self.agents.items():
            try:
                await agent.leave_meeting(self.context.meeting_id)
            except Exception as e:
                self.logger.error(f"Error having {participant} leave meeting: {e}")
        
        self.state = MeetingState.COMPLETED
        
        await self._send_system_message(
            f"Meeting '{self.context.title}' ended. "
            f"Duration: {(datetime.now() - self.context.start_time).total_seconds() / 60:.1f} minutes"
        )
    
    def get_transcript(self) -> List[Dict[str, Any]]:
        """Get the meeting transcript."""
        transcript = []
        for message in self.messages:
            transcript.append({
                'timestamp': message.timestamp.isoformat(),
                'speaker': message.speaker,
                'content': message.content,
                'message_type': message.message_type.value,
                'confidence': message.confidence
            })
        return transcript
    
    def get_summary_data(self) -> Dict[str, Any]:
        """Get data for meeting summary generation."""
        return {
            'meeting_id': self.context.meeting_id,
            'title': self.context.title,
            'participants': self.context.participants,
            'start_time': self.context.start_time,
            'end_time': datetime.now() if self.state == MeetingState.COMPLETED else None,
            'meeting_type': self.context.meeting_type,
            'message_count': len(self.messages),
            'transcript': self.get_transcript()
        }

