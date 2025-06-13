"""
Enhanced meeting orchestrator that integrates meeting platforms with speech processing.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

from ..agents.base_agent import BaseAgent, MeetingMessage, MessageType, MeetingContext
from ..config.config_manager import ConfigManager
from ..meeting_platforms.platform_manager import MeetingPlatformManager, MeetingPlatform
from ..speech_processing.speech_manager import SpeechProcessingManager, SpeechProvider


class MeetingState(Enum):
    """Meeting states."""
    SCHEDULED = "scheduled"
    STARTING = "starting"
    ACTIVE = "active"
    ENDING = "ending"
    COMPLETED = "completed"
    FAILED = "failed"


class AudioAwareMeetingOrchestrator:
    """
    Orchestrates meetings with integrated audio processing and platform management.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.logger = logging.getLogger("meeting_orchestrator")
        
        # Component managers
        self.platform_manager: Optional[MeetingPlatformManager] = None
        self.speech_manager: Optional[SpeechProcessingManager] = None
        
        # Active meetings
        self.active_meetings: Dict[str, Dict[str, Any]] = {}
        
        # Agent registry
        self.agents: Dict[str, BaseAgent] = {}
        
        # Meeting callbacks
        self.meeting_callbacks: Dict[str, List[Callable]] = {}
        
        # Configuration
        self.max_concurrent_meetings = self.config.meeting_config.get('max_concurrent_meetings', 3)
        self.meeting_timeout_minutes = self.config.meeting_config.get('meeting_timeout_minutes', 120)
        self.auto_transcription = self.config.meeting_config.get('enable_auto_transcription', True)
    
    async def initialize(self, agents: Dict[str, BaseAgent]) -> None:
        """
        Initialize the meeting orchestrator with agents and component managers.
        """
        try:
            self.logger.info("Initializing audio-aware meeting orchestrator...")
            
            # Store agent registry
            self.agents = agents
            
            # Initialize meeting platform manager
            self.platform_manager = MeetingPlatformManager(self.config_manager)
            await self.platform_manager.initialize(agents)
            
            # Initialize speech processing manager
            self.speech_manager = SpeechProcessingManager(self.config_manager)
            await self.speech_manager.initialize()
            
            # Set up global speech callback
            self.speech_manager.set_global_callback(self._handle_transcription_result)
            
            self.logger.info("Meeting orchestrator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize meeting orchestrator: {e}")
            raise
    
    async def schedule_meeting(self, meeting_config: Dict[str, Any]) -> str:
        """
        Schedule a new meeting with specified configuration.
        
        Args:
            meeting_config: Meeting configuration including:
                - title: Meeting title
                - participants: List of participant agent IDs
                - start_time: Scheduled start time
                - duration_minutes: Meeting duration
                - platform: Preferred meeting platform
                - enable_transcription: Whether to enable speech-to-text
                - meeting_url: Optional existing meeting URL
        
        Returns:
            Meeting ID if successful, empty string otherwise
        """
        try:
            meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Validate configuration
            if not self._validate_meeting_config(meeting_config):
                return ""
            
            # Check concurrent meeting limit
            if len(self.active_meetings) >= self.max_concurrent_meetings:
                self.logger.error("Maximum concurrent meetings reached")
                return ""
            
            # Create meeting URL if not provided
            meeting_url = meeting_config.get('meeting_url')
            if not meeting_url:
                meeting_url = await self._create_meeting_url(meeting_config)
                if not meeting_url:
                    self.logger.error("Failed to create meeting URL")
                    return ""
            
            # Create meeting record
            meeting_record = {
                'id': meeting_id,
                'title': meeting_config['title'],
                'participants': meeting_config['participants'],
                'start_time': meeting_config['start_time'],
                'duration_minutes': meeting_config.get('duration_minutes', 60),
                'platform': meeting_config.get('platform'),
                'meeting_url': meeting_url,
                'enable_transcription': meeting_config.get('enable_transcription', self.auto_transcription),
                'speech_provider': meeting_config.get('speech_provider'),
                'state': MeetingState.SCHEDULED,
                'created_time': datetime.now(),
                'transcript': [],
                'participants_joined': [],
                'audio_streams': {}
            }
            
            self.active_meetings[meeting_id] = meeting_record
            
            # Schedule meeting start
            start_delay = (meeting_config['start_time'] - datetime.now()).total_seconds()
            if start_delay > 0:
                asyncio.create_task(self._schedule_meeting_start(meeting_id, start_delay))
            else:
                # Start immediately if scheduled time has passed
                asyncio.create_task(self.start_meeting(meeting_id))
            
            self.logger.info(f"Scheduled meeting: {meeting_id} at {meeting_config['start_time']}")
            return meeting_id
            
        except Exception as e:
            self.logger.error(f"Error scheduling meeting: {e}")
            return ""
    
    def _validate_meeting_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate meeting configuration.
        """
        required_fields = ['title', 'participants', 'start_time']
        
        for field in required_fields:
            if field not in config:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Validate participants
        for participant in config['participants']:
            if participant not in self.agents:
                self.logger.error(f"Unknown participant agent: {participant}")
                return False
        
        return True
    
    async def _create_meeting_url(self, meeting_config: Dict[str, Any]) -> str:
        """
        Create a meeting URL using the platform manager.
        """
        try:
            if not self.platform_manager:
                return ""
            
            platform = meeting_config.get('platform')
            if platform:
                platform_enum = MeetingPlatform(platform)
            else:
                platform_enum = None
            
            return await self.platform_manager.create_meeting(
                title=meeting_config['title'],
                participants=meeting_config['participants'],
                start_time=meeting_config['start_time'],
                duration_minutes=meeting_config.get('duration_minutes', 60),
                platform=platform_enum
            )
            
        except Exception as e:
            self.logger.error(f"Error creating meeting URL: {e}")
            return ""
    
    async def _schedule_meeting_start(self, meeting_id: str, delay_seconds: float) -> None:
        """
        Schedule meeting start after delay.
        """
        try:
            await asyncio.sleep(delay_seconds)
            await self.start_meeting(meeting_id)
        except Exception as e:
            self.logger.error(f"Error in scheduled meeting start: {e}")
    
    async def start_meeting(self, meeting_id: str) -> bool:
        """
        Start a scheduled meeting.
        """
        try:
            if meeting_id not in self.active_meetings:
                self.logger.error(f"Meeting not found: {meeting_id}")
                return False
            
            meeting = self.active_meetings[meeting_id]
            
            if meeting['state'] != MeetingState.SCHEDULED:
                self.logger.warning(f"Meeting {meeting_id} not in scheduled state")
                return False
            
            self.logger.info(f"Starting meeting: {meeting_id}")
            meeting['state'] = MeetingState.STARTING
            
            # Start transcription if enabled
            if meeting['enable_transcription'] and self.speech_manager:
                speech_provider = meeting.get('speech_provider')
                if speech_provider:
                    provider_enum = SpeechProvider(speech_provider)
                else:
                    provider_enum = None
                
                transcription_started = await self.speech_manager.start_meeting_transcription(
                    meeting_id, 
                    provider_enum,
                    self._create_meeting_transcription_callback(meeting_id)
                )
                
                if not transcription_started:
                    self.logger.warning(f"Failed to start transcription for meeting: {meeting_id}")
            
            # Join agents to meeting
            join_tasks = []
            for participant_id in meeting['participants']:
                if participant_id in self.agents:
                    task = asyncio.create_task(
                        self._join_agent_to_meeting(meeting_id, participant_id)
                    )
                    join_tasks.append(task)
            
            # Wait for all agents to join
            join_results = await asyncio.gather(*join_tasks, return_exceptions=True)
            
            # Check if at least one agent joined successfully
            successful_joins = sum(1 for result in join_results if result is True)
            
            if successful_joins > 0:
                meeting['state'] = MeetingState.ACTIVE
                meeting['actual_start_time'] = datetime.now()
                
                # Set up meeting timeout
                asyncio.create_task(self._setup_meeting_timeout(meeting_id))
                
                # Notify callbacks
                await self._notify_meeting_callbacks(meeting_id, 'meeting_started', meeting)
                
                self.logger.info(f"Meeting started successfully: {meeting_id} ({successful_joins} agents joined)")
                return True
            else:
                meeting['state'] = MeetingState.FAILED
                self.logger.error(f"No agents could join meeting: {meeting_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error starting meeting {meeting_id}: {e}")
            if meeting_id in self.active_meetings:
                self.active_meetings[meeting_id]['state'] = MeetingState.FAILED
            return False
    
    async def _join_agent_to_meeting(self, meeting_id: str, agent_id: str) -> bool:
        """
        Join a specific agent to a meeting.
        """
        try:
            if not self.platform_manager:
                return False
            
            meeting = self.active_meetings[meeting_id]
            meeting_url = meeting['meeting_url']
            
            # Detect platform from URL if not specified
            platform = meeting.get('platform')
            if platform:
                platform_enum = MeetingPlatform(platform)
            else:
                platform_enum = None
            
            # Join meeting via platform manager
            success = await self.platform_manager.join_meeting(
                meeting_url, 
                agent_id, 
                platform_enum
            )
            
            if success:
                meeting['participants_joined'].append(agent_id)
                self.logger.info(f"Agent {agent_id} joined meeting {meeting_id}")
                return True
            else:
                self.logger.error(f"Agent {agent_id} failed to join meeting {meeting_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error joining agent {agent_id} to meeting {meeting_id}: {e}")
            return False
    
    def _create_meeting_transcription_callback(self, meeting_id: str) -> Callable:
        """
        Create a transcription callback for a specific meeting.
        """
        async def transcription_callback(result):
            try:
                if meeting_id in self.active_meetings:
                    meeting = self.active_meetings[meeting_id]
                    
                    # Add to meeting transcript
                    transcript_entry = {
                        'timestamp': result['timestamp'],
                        'speaker': result['speaker'],
                        'text': result['text'],
                        'confidence': result['confidence'],
                        'type': result['type'],
                        'provider': result.get('provider', 'unknown')
                    }
                    
                    meeting['transcript'].append(transcript_entry)
                    
                    # Process final transcriptions for agent responses
                    if result['type'] == 'final':
                        await self._process_transcription_for_agents(meeting_id, result)
            
            except Exception as e:
                self.logger.error(f"Error in transcription callback for meeting {meeting_id}: {e}")
        
        return transcription_callback
    
    async def _process_transcription_for_agents(self, meeting_id: str, transcription: Dict[str, Any]) -> None:
        """
        Process transcription result and potentially trigger agent responses.
        """
        try:
            meeting = self.active_meetings[meeting_id]
            
            # Create meeting message from transcription
            message = MeetingMessage(
                speaker=transcription['speaker'],
                content=transcription['text'],
                message_type=MessageType.GENERAL,
                timestamp=transcription['timestamp'],
                context_used=[],
                confidence=transcription['confidence']
            )
            
            # Create meeting context
            context = MeetingContext(
                meeting_id=meeting_id,
                title=meeting['title'],
                participants=meeting['participants_joined'],
                start_time=meeting.get('actual_start_time', meeting['start_time']),
                agenda="",
                meeting_type='audio_meeting'
            )
            
            # Check if any agents should respond
            for agent_id in meeting['participants_joined']:
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    
                    # Check if agent should respond (avoid responding to own speech)
                    if transcription['speaker'] != agent.employee_config.name:
                        should_respond = await self._should_agent_respond(
                            agent, message, context
                        )
                        
                        if should_respond:
                            # Generate and send response
                            asyncio.create_task(
                                self._generate_and_send_agent_response(
                                    meeting_id, agent_id, message, context
                                )
                            )
        
        except Exception as e:
            self.logger.error(f"Error processing transcription for agents: {e}")
    
    async def _should_agent_respond(self, agent: BaseAgent, message: MeetingMessage, 
                                  context: MeetingContext) -> bool:
        """
        Determine if an agent should respond to a transcribed message.
        """
        try:
            # Check if agent is mentioned
            agent_name = agent.employee_config.name.lower()
            message_lower = message.content.lower()
            
            if agent_name in message_lower:
                return True
            
            # Check for status/update requests
            response_triggers = [
                'status', 'update', 'progress', 'working on', 'blocker', 
                'blocked', 'impediment', 'help', 'question'
            ]
            
            if any(trigger in message_lower for trigger in response_triggers):
                return True
            
            # Check for direct questions
            if message.content.strip().endswith('?'):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if agent should respond: {e}")
            return False
    
    async def _generate_and_send_agent_response(self, meeting_id: str, agent_id: str, 
                                              message: MeetingMessage, context: MeetingContext) -> None:
        """
        Generate and send agent response to a meeting.
        """
        try:
            if agent_id not in self.agents:
                return
            
            agent = self.agents[agent_id]
            
            # Generate response
            response = await agent.generate_response(message.content, context)
            
            if response and response.content:
                # Send response via platform manager
                # Note: This would need platform-specific implementation
                # For now, we'll add it to the meeting transcript
                
                meeting = self.active_meetings[meeting_id]
                meeting['transcript'].append({
                    'timestamp': datetime.now(),
                    'speaker': agent.employee_config.name,
                    'text': response.content,
                    'confidence': response.confidence,
                    'type': 'agent_response',
                    'provider': 'agent'
                })
                
                self.logger.info(f"Agent {agent_id} responded in meeting {meeting_id}: {response.content[:100]}...")
        
        except Exception as e:
            self.logger.error(f"Error generating agent response: {e}")
    
    async def _handle_transcription_result(self, result: Dict[str, Any]) -> None:
        """
        Global handler for transcription results.
        """
        try:
            meeting_id = result.get('meeting_id')
            if meeting_id and meeting_id in self.active_meetings:
                # Meeting-specific handling is done in the meeting callback
                pass
            
            # Log transcription for debugging
            self.logger.debug(f"Transcription: [{result.get('speaker', 'Unknown')}] {result.get('text', '')[:100]}...")
        
        except Exception as e:
            self.logger.error(f"Error handling transcription result: {e}")
    
    async def _setup_meeting_timeout(self, meeting_id: str) -> None:
        """
        Set up automatic meeting timeout.
        """
        try:
            timeout_seconds = self.meeting_timeout_minutes * 60
            await asyncio.sleep(timeout_seconds)
            
            # Check if meeting is still active
            if (meeting_id in self.active_meetings and 
                self.active_meetings[meeting_id]['state'] == MeetingState.ACTIVE):
                
                self.logger.info(f"Meeting timeout reached for {meeting_id}")
                await self.end_meeting(meeting_id, reason="timeout")
        
        except Exception as e:
            self.logger.error(f"Error in meeting timeout for {meeting_id}: {e}")
    
    async def end_meeting(self, meeting_id: str, reason: str = "manual") -> bool:
        """
        End an active meeting.
        """
        try:
            if meeting_id not in self.active_meetings:
                self.logger.error(f"Meeting not found: {meeting_id}")
                return False
            
            meeting = self.active_meetings[meeting_id]
            
            if meeting['state'] not in [MeetingState.ACTIVE, MeetingState.STARTING]:
                self.logger.warning(f"Meeting {meeting_id} not in active state")
                return False
            
            self.logger.info(f"Ending meeting: {meeting_id} (reason: {reason})")
            meeting['state'] = MeetingState.ENDING
            
            # Stop transcription
            if meeting['enable_transcription'] and self.speech_manager:
                await self.speech_manager.stop_meeting_transcription(meeting_id)
            
            # Remove agents from meeting
            for agent_id in meeting['participants_joined']:
                if self.platform_manager:
                    await self.platform_manager.leave_meeting(agent_id)
            
            # Process meeting completion
            await self._process_meeting_completion(meeting_id)
            
            meeting['state'] = MeetingState.COMPLETED
            meeting['end_time'] = datetime.now()
            meeting['end_reason'] = reason
            
            # Notify callbacks
            await self._notify_meeting_callbacks(meeting_id, 'meeting_ended', meeting)
            
            self.logger.info(f"Meeting ended successfully: {meeting_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error ending meeting {meeting_id}: {e}")
            return False
    
    async def _process_meeting_completion(self, meeting_id: str) -> None:
        """
        Process meeting completion (summaries, action items, etc.).
        """
        try:
            meeting = self.active_meetings[meeting_id]
            
            # Convert transcript to meeting messages
            transcript_messages = []
            for entry in meeting['transcript']:
                if entry['type'] in ['final', 'agent_response']:
                    message = MeetingMessage(
                        speaker=entry['speaker'],
                        content=entry['text'],
                        message_type=MessageType.GENERAL,
                        timestamp=entry['timestamp'],
                        context_used=[],
                        confidence=entry['confidence']
                    )
                    transcript_messages.append(message)
            
            # Create meeting context
            context = MeetingContext(
                meeting_id=meeting_id,
                title=meeting['title'],
                participants=meeting['participants_joined'],
                start_time=meeting.get('actual_start_time', meeting['start_time']),
                agenda="",
                meeting_type='audio_meeting'
            )
            
            # Process with post-meeting handler
            from ..post_meeting.action_handler import PostMeetingActionHandler
            
            action_handler = PostMeetingActionHandler()
            results = await action_handler.process_meeting_completion(
                transcript_messages, context
            )
            
            # Store results in meeting record
            meeting['summary'] = results.get('summary')
            meeting['action_items'] = results.get('action_items', [])
            meeting['jira_tickets'] = results.get('jira_tickets', [])
            meeting['confluence_docs'] = results.get('confluence_docs', [])
            
            self.logger.info(f"Meeting completion processed for {meeting_id}: "
                           f"{len(results.get('action_items', []))} action items created")
        
        except Exception as e:
            self.logger.error(f"Error processing meeting completion: {e}")
    
    def add_meeting_callback(self, meeting_id: str, callback: Callable) -> None:
        """
        Add a callback for meeting events.
        """
        if meeting_id not in self.meeting_callbacks:
            self.meeting_callbacks[meeting_id] = []
        self.meeting_callbacks[meeting_id].append(callback)
    
    async def _notify_meeting_callbacks(self, meeting_id: str, event: str, data: Any) -> None:
        """
        Notify meeting callbacks of events.
        """
        try:
            if meeting_id in self.meeting_callbacks:
                for callback in self.meeting_callbacks[meeting_id]:
                    try:
                        await callback(event, data)
                    except Exception as e:
                        self.logger.error(f"Error in meeting callback: {e}")
        
        except Exception as e:
            self.logger.error(f"Error notifying meeting callbacks: {e}")
    
    def get_meeting_status(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific meeting.
        """
        if meeting_id in self.active_meetings:
            meeting = self.active_meetings[meeting_id].copy()
            
            # Add real-time status information
            meeting['transcript_length'] = len(meeting.get('transcript', []))
            meeting['participants_count'] = len(meeting.get('participants_joined', []))
            
            if meeting['state'] == MeetingState.ACTIVE:
                start_time = meeting.get('actual_start_time', meeting['start_time'])
                meeting['duration_minutes'] = (datetime.now() - start_time).total_seconds() / 60
            
            return meeting
        
        return None
    
    def get_active_meetings(self) -> List[Dict[str, Any]]:
        """
        Get list of all active meetings.
        """
        active = []
        for meeting_id, meeting in self.active_meetings.items():
            if meeting['state'] in [MeetingState.SCHEDULED, MeetingState.STARTING, MeetingState.ACTIVE]:
                status = self.get_meeting_status(meeting_id)
                if status:
                    active.append(status)
        
        return active
    
    async def cleanup(self) -> None:
        """
        Cleanup the meeting orchestrator.
        """
        try:
            self.logger.info("Cleaning up meeting orchestrator...")
            
            # End all active meetings
            for meeting_id in list(self.active_meetings.keys()):
                meeting = self.active_meetings[meeting_id]
                if meeting['state'] in [MeetingState.ACTIVE, MeetingState.STARTING]:
                    await self.end_meeting(meeting_id, reason="cleanup")
            
            # Cleanup component managers
            if self.platform_manager:
                await self.platform_manager.cleanup()
            
            if self.speech_manager:
                await self.speech_manager.cleanup()
            
            self.active_meetings.clear()
            self.meeting_callbacks.clear()
            
            self.logger.info("Meeting orchestrator cleanup completed")
        
        except Exception as e:
            self.logger.error(f"Error during meeting orchestrator cleanup: {e}")


# Example usage and testing
async def test_audio_aware_meeting_orchestrator():
    """
    Test function for the audio-aware meeting orchestrator.
    """
    from ..config.config_manager import ConfigManager
    from ..agents.agent_manager import AgentManager
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize agents
    agent_manager = AgentManager(config_manager)
    await agent_manager.initialize()
    
    # Initialize meeting orchestrator
    orchestrator = AudioAwareMeetingOrchestrator(config_manager)
    await orchestrator.initialize(agent_manager.agents)
    
    # Schedule a test meeting
    meeting_config = {
        'title': 'Test Audio Meeting',
        'participants': ['vivek'],
        'start_time': datetime.now() + timedelta(seconds=5),
        'duration_minutes': 30,
        'enable_transcription': True
    }
    
    meeting_id = await orchestrator.schedule_meeting(meeting_config)
    
    if meeting_id:
        print(f"Scheduled meeting: {meeting_id}")
        
        # Wait for meeting to start and run
        await asyncio.sleep(10)
        
        # Check meeting status
        status = orchestrator.get_meeting_status(meeting_id)
        if status:
            print(f"Meeting status: {status['state'].value}")
            print(f"Transcript entries: {status['transcript_length']}")
        
        # End meeting
        await orchestrator.end_meeting(meeting_id, "test_complete")
    
    # Cleanup
    await orchestrator.cleanup()


if __name__ == "__main__":
    asyncio.run(test_audio_aware_meeting_orchestrator())

