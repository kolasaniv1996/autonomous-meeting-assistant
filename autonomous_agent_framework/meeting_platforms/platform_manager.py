"""
Meeting platform configuration and management for autonomous agent framework.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import logging

from ..config.config_manager import ConfigManager
from ..agents.base_agent import BaseAgent


class MeetingPlatform(Enum):
    """Supported meeting platforms."""
    TEAMS = "teams"
    GOOGLE_MEET = "google_meet"
    ZOOM = "zoom"  # Future support
    WEBEX = "webex"  # Future support


class MeetingPlatformManager:
    """
    Manages integration with different meeting platforms.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.logger = logging.getLogger("meeting_platform_manager")
        
        # Platform integrations
        self.teams_integration = None
        self.google_meet_integration = None
        
        # Configuration
        self.preferred_platform = self._get_preferred_platform()
        self.enabled_platforms = self._get_enabled_platforms()
    
    def _get_preferred_platform(self) -> MeetingPlatform:
        """Get the preferred meeting platform from configuration."""
        platform_name = self.config.meeting_config.get('preferred_platform', 'teams')
        try:
            return MeetingPlatform(platform_name.lower())
        except ValueError:
            self.logger.warning(f"Unknown platform '{platform_name}', defaulting to Teams")
            return MeetingPlatform.TEAMS
    
    def _get_enabled_platforms(self) -> List[MeetingPlatform]:
        """Get list of enabled meeting platforms."""
        enabled = self.config.meeting_config.get('enabled_platforms', ['teams', 'google_meet'])
        platforms = []
        
        for platform_name in enabled:
            try:
                platforms.append(MeetingPlatform(platform_name.lower()))
            except ValueError:
                self.logger.warning(f"Unknown platform '{platform_name}', skipping")
        
        return platforms
    
    async def initialize(self, agents: Dict[str, BaseAgent]) -> None:
        """
        Initialize all enabled meeting platform integrations.
        """
        try:
            self.logger.info("Initializing meeting platform integrations...")
            
            # Initialize Teams integration if enabled
            if MeetingPlatform.TEAMS in self.enabled_platforms:
                await self._initialize_teams_integration(agents)
            
            # Initialize Google Meet integration if enabled
            if MeetingPlatform.GOOGLE_MEET in self.enabled_platforms:
                await self._initialize_google_meet_integration(agents)
            
            self.logger.info(f"Initialized {len(self.enabled_platforms)} meeting platforms")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize meeting platforms: {e}")
            raise
    
    async def _initialize_teams_integration(self, agents: Dict[str, BaseAgent]) -> None:
        """Initialize Microsoft Teams integration."""
        try:
            from .teams_integration import TeamsIntegrationManager
            
            self.teams_integration = TeamsIntegrationManager(self.config_manager)
            await self.teams_integration.initialize(agents)
            
            self.logger.info("Teams integration initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Teams integration: {e}")
            # Don't raise - continue with other platforms
    
    async def _initialize_google_meet_integration(self, agents: Dict[str, BaseAgent]) -> None:
        """Initialize Google Meet integration."""
        try:
            from .google_meet_integration import GoogleMeetIntegrationManager
            
            self.google_meet_integration = GoogleMeetIntegrationManager(self.config_manager)
            await self.google_meet_integration.initialize(agents)
            
            self.logger.info("Google Meet integration initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Meet integration: {e}")
            # Don't raise - continue with other platforms
    
    async def join_meeting(self, meeting_url: str, agent_id: str, 
                          platform: Optional[MeetingPlatform] = None) -> bool:
        """
        Join a meeting with the specified agent.
        
        Args:
            meeting_url: URL of the meeting to join
            agent_id: ID of the agent to join with
            platform: Specific platform to use (auto-detect if None)
        
        Returns:
            True if successfully joined, False otherwise
        """
        try:
            # Auto-detect platform if not specified
            if platform is None:
                platform = self._detect_platform_from_url(meeting_url)
            
            self.logger.info(f"Joining {platform.value} meeting with agent {agent_id}")
            
            # Route to appropriate integration
            if platform == MeetingPlatform.TEAMS and self.teams_integration:
                return await self.teams_integration.join_meeting(meeting_url, agent_id)
            
            elif platform == MeetingPlatform.GOOGLE_MEET and self.google_meet_integration:
                return await self.google_meet_integration.join_meeting(meeting_url, agent_id)
            
            else:
                self.logger.error(f"Platform {platform.value} not available or not initialized")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to join meeting: {e}")
            return False
    
    def _detect_platform_from_url(self, meeting_url: str) -> MeetingPlatform:
        """
        Auto-detect meeting platform from URL.
        """
        url_lower = meeting_url.lower()
        
        if 'teams.microsoft.com' in url_lower:
            return MeetingPlatform.TEAMS
        elif 'meet.google.com' in url_lower:
            return MeetingPlatform.GOOGLE_MEET
        elif 'zoom.us' in url_lower:
            return MeetingPlatform.ZOOM
        elif 'webex.com' in url_lower:
            return MeetingPlatform.WEBEX
        else:
            # Default to preferred platform
            self.logger.warning(f"Could not detect platform from URL: {meeting_url}")
            return self.preferred_platform
    
    async def create_meeting(self, title: str, participants: List[str], 
                           start_time, duration_minutes: int = 60,
                           platform: Optional[MeetingPlatform] = None) -> str:
        """
        Create a new meeting on the specified platform.
        
        Returns:
            Meeting URL if successful, empty string otherwise
        """
        try:
            if platform is None:
                platform = self.preferred_platform
            
            self.logger.info(f"Creating {platform.value} meeting: {title}")
            
            # Route to appropriate integration
            if platform == MeetingPlatform.TEAMS and self.teams_integration:
                return await self.teams_integration.create_meeting(
                    title, participants, start_time, duration_minutes
                )
            
            elif platform == MeetingPlatform.GOOGLE_MEET:
                # Google Meet creation would require Calendar API integration
                self.logger.warning("Google Meet creation not yet implemented")
                return ""
            
            else:
                self.logger.error(f"Platform {platform.value} not available for meeting creation")
                return ""
            
        except Exception as e:
            self.logger.error(f"Failed to create meeting: {e}")
            return ""
    
    async def leave_meeting(self, agent_id: str, platform: Optional[MeetingPlatform] = None) -> None:
        """
        Leave meeting for the specified agent.
        """
        try:
            if platform is None:
                # Try all platforms
                if self.teams_integration:
                    # Teams bots handle leaving automatically
                    pass
                
                if self.google_meet_integration:
                    await self.google_meet_integration.leave_meeting(agent_id)
            
            elif platform == MeetingPlatform.TEAMS and self.teams_integration:
                # Teams bots handle leaving automatically
                pass
            
            elif platform == MeetingPlatform.GOOGLE_MEET and self.google_meet_integration:
                await self.google_meet_integration.leave_meeting(agent_id)
            
        except Exception as e:
            self.logger.error(f"Error leaving meeting for agent {agent_id}: {e}")
    
    def get_available_platforms(self) -> List[MeetingPlatform]:
        """Get list of available (initialized) platforms."""
        available = []
        
        if self.teams_integration:
            available.append(MeetingPlatform.TEAMS)
        
        if self.google_meet_integration:
            available.append(MeetingPlatform.GOOGLE_MEET)
        
        return available
    
    def is_platform_available(self, platform: MeetingPlatform) -> bool:
        """Check if a specific platform is available."""
        return platform in self.get_available_platforms()
    
    async def get_meeting_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get current meeting status for an agent across all platforms.
        """
        status = {
            'agent_id': agent_id,
            'in_meeting': False,
            'platform': None,
            'meeting_details': {}
        }
        
        try:
            # Check Teams
            if self.teams_integration:
                teams_bot = await self.teams_integration.get_agent_bot(agent_id)
                if teams_bot and teams_bot.current_meeting_context:
                    status['in_meeting'] = True
                    status['platform'] = MeetingPlatform.TEAMS.value
                    status['meeting_details'] = {
                        'meeting_id': teams_bot.current_meeting_context.meeting_id,
                        'title': teams_bot.current_meeting_context.title,
                        'participants': teams_bot.current_meeting_context.participants
                    }
                    return status
            
            # Check Google Meet
            if self.google_meet_integration and agent_id in self.google_meet_integration.agent_bots:
                meet_bot = self.google_meet_integration.agent_bots[agent_id]
                if meet_bot.is_in_meeting:
                    status['in_meeting'] = True
                    status['platform'] = MeetingPlatform.GOOGLE_MEET.value
                    if meet_bot.current_meeting_context:
                        status['meeting_details'] = {
                            'meeting_id': meet_bot.current_meeting_context.meeting_id,
                            'title': meet_bot.current_meeting_context.title,
                            'participants': meet_bot.current_meeting_context.participants
                        }
                    return status
            
        except Exception as e:
            self.logger.error(f"Error getting meeting status for agent {agent_id}: {e}")
        
        return status
    
    async def cleanup(self) -> None:
        """
        Cleanup all meeting platform integrations.
        """
        try:
            self.logger.info("Cleaning up meeting platform integrations...")
            
            if self.teams_integration:
                await self.teams_integration.cleanup()
            
            if self.google_meet_integration:
                await self.google_meet_integration.cleanup()
            
            self.logger.info("Meeting platform cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during meeting platform cleanup: {e}")


# Configuration helper functions
def add_meeting_platform_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add meeting platform configuration to the main config.
    """
    if 'meeting_platforms' not in config:
        config['meeting_platforms'] = {}
    
    # Default configuration
    config['meeting_platforms'].update({
        'preferred_platform': 'teams',
        'enabled_platforms': ['teams', 'google_meet'],
        
        # Teams configuration
        'teams': {
            'app_id': '',  # Microsoft Teams App ID
            'app_password': '',  # Microsoft Teams App Password
            'tenant_id': '',  # Azure AD Tenant ID
            'auto_join_scheduled_meetings': True,
            'enable_chat_responses': True,
            'enable_meeting_summaries': True
        },
        
        # Google Meet configuration
        'google_meet': {
            'use_headless_browser': True,
            'browser_timeout': 30,
            'auto_disable_camera': True,
            'auto_disable_microphone': True,
            'enable_chat_responses': True
        },
        
        # General meeting settings
        'general': {
            'max_concurrent_meetings': 3,
            'meeting_timeout_minutes': 120,
            'auto_leave_empty_meetings': True,
            'enable_meeting_recording': False
        }
    })
    
    return config


# Example usage
async def test_meeting_platform_manager():
    """
    Test function for meeting platform manager.
    """
    from ..config.config_manager import ConfigManager
    from ..agents.agent_manager import AgentManager
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize agents
    agent_manager = AgentManager(config_manager)
    await agent_manager.initialize()
    
    # Initialize meeting platform manager
    platform_manager = MeetingPlatformManager(config_manager)
    await platform_manager.initialize(agent_manager.agents)
    
    # Test platform detection
    teams_url = "https://teams.microsoft.com/l/meetup-join/test"
    meet_url = "https://meet.google.com/abc-defg-hij"
    
    teams_platform = platform_manager._detect_platform_from_url(teams_url)
    meet_platform = platform_manager._detect_platform_from_url(meet_url)
    
    print(f"Teams URL detected as: {teams_platform.value}")
    print(f"Meet URL detected as: {meet_platform.value}")
    
    # Test joining meetings
    print(f"Available platforms: {[p.value for p in platform_manager.get_available_platforms()]}")
    
    # Cleanup
    await platform_manager.cleanup()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_meeting_platform_manager())

