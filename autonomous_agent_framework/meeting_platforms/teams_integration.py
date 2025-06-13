"""
Microsoft Teams Bot Framework integration for autonomous agent framework.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    from botbuilder.core import (
        ActivityHandler, TurnContext, MessageFactory, 
        CardFactory, ConversationState, UserState
    )
    from botbuilder.core.conversation_state import ConversationState
    from botbuilder.core.user_state import UserState
    from botbuilder.schema import (
        Activity, ActivityTypes, ChannelAccount, 
        ConversationReference, Attachment
    )
    from botbuilder.adapter.teams import TeamsAdapter
    from botbuilder.schema.teams import (
        TeamsChannelAccount, TeamInfo, TeamsChannelData,
        TeamsMeetingInfo, TeamsMeetingParticipant
    )
    from microsoft.graph import GraphServiceClient
    from microsoft.graph.generated.models.online_meeting import OnlineMeeting
    from microsoft.graph.generated.models.meeting_participants import MeetingParticipants
    from microsoft.graph.generated.models.meeting_participant_info import MeetingParticipantInfo
except ImportError:
    # Mock classes for development without actual dependencies
    class ActivityHandler:
        pass
    class TurnContext:
        pass
    class MessageFactory:
        pass
    class Activity:
        pass
    class ActivityTypes:
        pass
    class TeamsAdapter:
        pass

from ..agents.base_agent import BaseAgent, MeetingMessage, MessageType, MeetingContext
from ..config.config_manager import ConfigManager


class TeamsAgentBot(ActivityHandler):
    """
    Microsoft Teams bot that represents an autonomous agent in meetings.
    """
    
    def __init__(self, agent: BaseAgent, conversation_state: ConversationState, 
                 user_state: UserState):
        self.agent = agent
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.logger = logging.getLogger(f"teams_bot_{agent.employee_id}")
        
        # Meeting context tracking
        self.current_meeting_context: Optional[MeetingContext] = None
        self.meeting_participants: List[str] = []
        self.meeting_transcript: List[MeetingMessage] = []
        
    async def on_message_activity(self, turn_context: TurnContext) -> None:
        """
        Handle incoming messages in Teams meetings.
        """
        try:
            # Extract message content and sender
            message_text = turn_context.activity.text or ""
            sender_name = turn_context.activity.from_property.name or "Unknown"
            
            self.logger.info(f"Received message from {sender_name}: {message_text[:100]}...")
            
            # Add to transcript
            incoming_message = MeetingMessage(
                speaker=sender_name,
                content=message_text,
                message_type=MessageType.GENERAL,
                timestamp=datetime.now(),
                context_used=[],
                confidence=1.0
            )
            self.meeting_transcript.append(incoming_message)
            
            # Check if the agent should respond
            should_respond = await self._should_respond_to_message(message_text, sender_name)
            
            if should_respond:
                # Generate response using the agent
                response = await self.agent.generate_response(
                    message_text, 
                    self.current_meeting_context
                )
                
                # Send response to Teams
                await self._send_response(turn_context, response)
                
                # Add agent response to transcript
                self.meeting_transcript.append(response)
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            await turn_context.send_activity(
                MessageFactory.text("I'm experiencing technical difficulties. Please try again.")
            )
    
    async def on_teams_meeting_start(self, meeting_details: Dict[str, Any], 
                                   turn_context: TurnContext) -> None:
        """
        Handle when a Teams meeting starts.
        """
        try:
            self.logger.info(f"Meeting started: {meeting_details}")
            
            # Create meeting context
            self.current_meeting_context = MeetingContext(
                meeting_id=meeting_details.get('id', 'unknown'),
                title=meeting_details.get('subject', 'Teams Meeting'),
                participants=self._extract_participants(meeting_details),
                start_time=datetime.now(),
                agenda=meeting_details.get('agenda', ''),
                meeting_type='teams_meeting'
            )
            
            # Update agent context
            await self.agent.update_context()
            
            # Send greeting message
            greeting = await self._generate_meeting_greeting()
            await turn_context.send_activity(MessageFactory.text(greeting))
            
        except Exception as e:
            self.logger.error(f"Error handling meeting start: {e}")
    
    async def on_teams_meeting_end(self, meeting_details: Dict[str, Any], 
                                 turn_context: TurnContext) -> None:
        """
        Handle when a Teams meeting ends.
        """
        try:
            self.logger.info(f"Meeting ended: {meeting_details}")
            
            if self.current_meeting_context:
                # Process meeting completion
                from ..post_meeting.action_handler import PostMeetingActionHandler
                
                action_handler = PostMeetingActionHandler()
                results = await action_handler.process_meeting_completion(
                    self.meeting_transcript,
                    self.current_meeting_context
                )
                
                # Send summary to meeting participants (if configured)
                summary_text = self._format_meeting_summary(results['summary'])
                await turn_context.send_activity(MessageFactory.text(summary_text))
                
                # Reset meeting state
                self.current_meeting_context = None
                self.meeting_transcript = []
                self.meeting_participants = []
            
        except Exception as e:
            self.logger.error(f"Error handling meeting end: {e}")
    
    async def _should_respond_to_message(self, message: str, sender: str) -> bool:
        """
        Determine if the agent should respond to a message.
        """
        # Don't respond to own messages
        if sender == self.agent.employee_config.name:
            return False
        
        # Respond if directly mentioned
        agent_name = self.agent.employee_config.name.lower()
        if agent_name in message.lower():
            return True
        
        # Respond to questions about status, blockers, or work
        response_triggers = [
            'status', 'update', 'progress', 'working on', 'blocker', 
            'blocked', 'impediment', 'help', 'question'
        ]
        
        message_lower = message.lower()
        if any(trigger in message_lower for trigger in response_triggers):
            return True
        
        # Respond to direct questions
        if message.strip().endswith('?'):
            return True
        
        return False
    
    async def _send_response(self, turn_context: TurnContext, response: MeetingMessage) -> None:
        """
        Send agent response to Teams meeting.
        """
        try:
            # Format response based on message type
            if response.message_type == MessageType.STATUS_UPDATE:
                formatted_message = f"📊 **Status Update**: {response.content}"
            elif response.message_type == MessageType.BLOCKER:
                formatted_message = f"🚫 **Blocker**: {response.content}"
            elif response.message_type == MessageType.QUESTION:
                formatted_message = f"❓ **Question**: {response.content}"
            else:
                formatted_message = response.content
            
            await turn_context.send_activity(MessageFactory.text(formatted_message))
            
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")
    
    def _extract_participants(self, meeting_details: Dict[str, Any]) -> List[str]:
        """
        Extract participant names from meeting details.
        """
        participants = []
        
        # Extract from various possible fields
        if 'participants' in meeting_details:
            for participant in meeting_details['participants']:
                name = participant.get('displayName') or participant.get('name')
                if name:
                    participants.append(name)
        
        if 'attendees' in meeting_details:
            for attendee in meeting_details['attendees']:
                name = attendee.get('displayName') or attendee.get('name')
                if name:
                    participants.append(name)
        
        return participants
    
    async def _generate_meeting_greeting(self) -> str:
        """
        Generate a greeting message for the meeting.
        """
        agent_name = self.agent.employee_config.name
        
        # Get current status from agent context
        context = self.agent.context
        if context and context.current_focus:
            return (f"Hello everyone! {agent_name} here. "
                   f"I'm currently {context.current_focus.lower()}. "
                   f"Happy to share updates and answer questions!")
        else:
            return (f"Hello everyone! {agent_name} here. "
                   f"Ready to share updates and answer questions!")
    
    def _format_meeting_summary(self, summary) -> str:
        """
        Format meeting summary for Teams message.
        """
        if not summary:
            return "Meeting completed. Summary will be available shortly."
        
        formatted = f"📝 **Meeting Summary**\n\n"
        
        if summary.key_points:
            formatted += "**Key Points:**\n"
            for point in summary.key_points[:3]:  # Limit for Teams message
                formatted += f"• {point}\n"
            formatted += "\n"
        
        if summary.action_items:
            formatted += "**Action Items:**\n"
            for item in summary.action_items[:3]:  # Limit for Teams message
                formatted += f"• {item.description} (Assigned: {item.assignee})\n"
            formatted += "\n"
        
        formatted += "Full summary and action items will be available in Confluence."
        
        return formatted


class TeamsIntegrationManager:
    """
    Manages Teams integration for autonomous agents.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.logger = logging.getLogger("teams_integration")
        
        # Teams-specific configuration
        self.app_id = self.config.api_credentials.get('teams_app_id')
        self.app_password = self.config.api_credentials.get('teams_app_password')
        self.tenant_id = self.config.api_credentials.get('teams_tenant_id')
        
        # Bot instances for each agent
        self.agent_bots: Dict[str, TeamsAgentBot] = {}
        
        # Graph client for meeting management
        self.graph_client: Optional[GraphServiceClient] = None
    
    async def initialize(self, agents: Dict[str, BaseAgent]) -> None:
        """
        Initialize Teams integration for all agents.
        """
        try:
            self.logger.info("Initializing Teams integration...")
            
            # Initialize Graph client
            await self._initialize_graph_client()
            
            # Create bot instances for each agent
            for agent_id, agent in agents.items():
                await self._create_agent_bot(agent_id, agent)
            
            self.logger.info(f"Teams integration initialized for {len(agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Teams integration: {e}")
            raise
    
    async def _initialize_graph_client(self) -> None:
        """
        Initialize Microsoft Graph client for meeting management.
        """
        try:
            # This would require proper authentication setup
            # For now, we'll create a placeholder
            self.logger.info("Graph client initialization placeholder")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Graph client: {e}")
    
    async def _create_agent_bot(self, agent_id: str, agent: BaseAgent) -> None:
        """
        Create a Teams bot instance for an agent.
        """
        try:
            # Create conversation and user state
            conversation_state = ConversationState(None)  # Would need proper storage
            user_state = UserState(None)  # Would need proper storage
            
            # Create bot instance
            bot = TeamsAgentBot(agent, conversation_state, user_state)
            self.agent_bots[agent_id] = bot
            
            self.logger.info(f"Created Teams bot for agent: {agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to create bot for agent {agent_id}: {e}")
    
    async def join_meeting(self, meeting_url: str, agent_id: str) -> bool:
        """
        Join a Teams meeting with the specified agent.
        """
        try:
            self.logger.info(f"Attempting to join meeting {meeting_url} with agent {agent_id}")
            
            if agent_id not in self.agent_bots:
                self.logger.error(f"No bot found for agent: {agent_id}")
                return False
            
            # This would involve the actual Teams SDK integration
            # For now, we'll simulate the joining process
            
            bot = self.agent_bots[agent_id]
            
            # Extract meeting details from URL
            meeting_details = await self._extract_meeting_details(meeting_url)
            
            # Simulate joining the meeting
            await bot.on_teams_meeting_start(meeting_details, None)
            
            self.logger.info(f"Successfully joined meeting with agent {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to join meeting: {e}")
            return False
    
    async def _extract_meeting_details(self, meeting_url: str) -> Dict[str, Any]:
        """
        Extract meeting details from Teams meeting URL.
        """
        # This would parse the actual Teams meeting URL
        # For now, return mock details
        return {
            'id': 'mock_meeting_id',
            'subject': 'Teams Meeting',
            'participants': [],
            'agenda': 'Meeting agenda'
        }
    
    async def create_meeting(self, title: str, participants: List[str], 
                           start_time: datetime, duration_minutes: int = 60) -> str:
        """
        Create a new Teams meeting.
        """
        try:
            self.logger.info(f"Creating Teams meeting: {title}")
            
            # This would use the Graph API to create an actual meeting
            # For now, return a mock meeting URL
            
            meeting_url = f"https://teams.microsoft.com/l/meetup-join/mock_meeting_id"
            
            self.logger.info(f"Created Teams meeting: {meeting_url}")
            return meeting_url
            
        except Exception as e:
            self.logger.error(f"Failed to create Teams meeting: {e}")
            return ""
    
    async def get_agent_bot(self, agent_id: str) -> Optional[TeamsAgentBot]:
        """
        Get the Teams bot instance for an agent.
        """
        return self.agent_bots.get(agent_id)
    
    async def cleanup(self) -> None:
        """
        Cleanup Teams integration resources.
        """
        try:
            self.logger.info("Cleaning up Teams integration...")
            
            # Cleanup bot instances
            for bot in self.agent_bots.values():
                # Perform any necessary cleanup
                pass
            
            self.agent_bots.clear()
            
            self.logger.info("Teams integration cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during Teams integration cleanup: {e}")


# Example usage and testing
async def test_teams_integration():
    """
    Test function for Teams integration.
    """
    from ..config.config_manager import ConfigManager
    from ..agents.agent_manager import AgentManager
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize agents
    agent_manager = AgentManager(config_manager)
    await agent_manager.initialize()
    
    # Initialize Teams integration
    teams_manager = TeamsIntegrationManager(config_manager)
    await teams_manager.initialize(agent_manager.agents)
    
    # Test joining a meeting
    meeting_url = "https://teams.microsoft.com/l/meetup-join/test_meeting"
    success = await teams_manager.join_meeting(meeting_url, "vivek")
    
    print(f"Meeting join test: {'Success' if success else 'Failed'}")
    
    # Cleanup
    await teams_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(test_teams_integration())

