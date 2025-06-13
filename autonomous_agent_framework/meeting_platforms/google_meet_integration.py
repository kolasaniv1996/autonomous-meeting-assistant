"""
Google Meet integration for autonomous agent framework.
This provides a fallback option for meeting participation when Teams is not available.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
except ImportError:
    # Mock for development without selenium
    webdriver = None
    WebDriverWait = None
    EC = None
    Options = None

from ..agents.base_agent import BaseAgent, MeetingMessage, MessageType, MeetingContext
from ..config.config_manager import ConfigManager


class GoogleMeetBot:
    """
    Google Meet bot that uses headless browser automation to join meetings.
    """
    
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.logger = logging.getLogger(f"meet_bot_{agent.employee_id}")
        
        # Browser and meeting state
        self.driver: Optional[webdriver.Chrome] = None
        self.current_meeting_context: Optional[MeetingContext] = None
        self.meeting_transcript: List[MeetingMessage] = []
        self.is_in_meeting = False
        
    async def initialize_browser(self) -> bool:
        """
        Initialize headless Chrome browser for Meet automation.
        """
        try:
            if not webdriver:
                self.logger.error("Selenium not available. Install with: pip install selenium")
                return False
            
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Allow microphone and camera access
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            chrome_options.add_argument("--use-fake-device-for-media-stream")
            
            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            self.logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def join_meeting(self, meeting_url: str) -> bool:
        """
        Join a Google Meet meeting using browser automation.
        """
        try:
            if not self.driver:
                if not await self.initialize_browser():
                    return False
            
            self.logger.info(f"Joining Google Meet: {meeting_url}")
            
            # Navigate to meeting URL
            self.driver.get(meeting_url)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Handle Google sign-in if required
            await self._handle_authentication()
            
            # Join the meeting
            success = await self._join_meeting_flow()
            
            if success:
                self.is_in_meeting = True
                
                # Create meeting context
                self.current_meeting_context = MeetingContext(
                    meeting_id=self._extract_meeting_id(meeting_url),
                    title="Google Meet",
                    participants=await self._get_participants(),
                    start_time=datetime.now(),
                    agenda="",
                    meeting_type='google_meet'
                )
                
                # Start monitoring meeting
                asyncio.create_task(self._monitor_meeting())
                
                self.logger.info("Successfully joined Google Meet")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to join meeting: {e}")
            return False
    
    async def _handle_authentication(self) -> None:
        """
        Handle Google authentication if required.
        """
        try:
            # Check if we need to sign in
            if "accounts.google.com" in self.driver.current_url:
                self.logger.info("Google authentication required")
                
                # This would require actual Google credentials
                # For demo purposes, we'll assume authentication is handled
                # In production, you'd need to implement OAuth flow or use service account
                
                await asyncio.sleep(2)
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
    
    async def _join_meeting_flow(self) -> bool:
        """
        Execute the meeting join flow.
        """
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Look for join button
            join_selectors = [
                "button[data-testid='join-button']",
                "button:contains('Join now')",
                "button:contains('Ask to join')",
                "[data-meeting-title] button",
                ".google-material-icons:contains('videocam') + span"
            ]
            
            for selector in join_selectors:
                try:
                    join_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    join_button.click()
                    self.logger.info(f"Clicked join button: {selector}")
                    break
                except TimeoutException:
                    continue
            else:
                self.logger.warning("Could not find join button")
                return False
            
            # Wait for meeting to load
            await asyncio.sleep(5)
            
            # Disable camera and microphone initially
            await self._toggle_camera(False)
            await self._toggle_microphone(False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in join flow: {e}")
            return False
    
    async def _toggle_camera(self, enable: bool) -> None:
        """
        Toggle camera on/off.
        """
        try:
            camera_selectors = [
                "button[data-testid='camera-button']",
                "button[aria-label*='camera']",
                "button[aria-label*='Camera']"
            ]
            
            for selector in camera_selectors:
                try:
                    camera_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    # Check current state and toggle if needed
                    is_enabled = "disabled" not in camera_button.get_attribute("class")
                    if is_enabled != enable:
                        camera_button.click()
                        self.logger.info(f"Camera {'enabled' if enable else 'disabled'}")
                    break
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error toggling camera: {e}")
    
    async def _toggle_microphone(self, enable: bool) -> None:
        """
        Toggle microphone on/off.
        """
        try:
            mic_selectors = [
                "button[data-testid='microphone-button']",
                "button[aria-label*='microphone']",
                "button[aria-label*='Microphone']"
            ]
            
            for selector in mic_selectors:
                try:
                    mic_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    # Check current state and toggle if needed
                    is_enabled = "disabled" not in mic_button.get_attribute("class")
                    if is_enabled != enable:
                        mic_button.click()
                        self.logger.info(f"Microphone {'enabled' if enable else 'disabled'}")
                    break
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error toggling microphone: {e}")
    
    async def _get_participants(self) -> List[str]:
        """
        Get list of meeting participants.
        """
        try:
            participants = []
            
            # Look for participant list
            participant_selectors = [
                "[data-participant-id]",
                ".participant-name",
                "[aria-label*='participant']"
            ]
            
            for selector in participant_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        name = element.text.strip()
                        if name and name not in participants:
                            participants.append(name)
                    if participants:
                        break
                except:
                    continue
            
            return participants
            
        except Exception as e:
            self.logger.error(f"Error getting participants: {e}")
            return []
    
    async def _monitor_meeting(self) -> None:
        """
        Monitor meeting for chat messages and other events.
        """
        try:
            while self.is_in_meeting:
                # Check for new chat messages
                await self._check_chat_messages()
                
                # Check if meeting is still active
                if not await self._is_meeting_active():
                    await self.leave_meeting()
                    break
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
        except Exception as e:
            self.logger.error(f"Error monitoring meeting: {e}")
    
    async def _check_chat_messages(self) -> None:
        """
        Check for new chat messages in the meeting.
        """
        try:
            # Look for chat messages
            chat_selectors = [
                ".chat-message",
                "[data-message-id]",
                ".message-content"
            ]
            
            for selector in chat_selectors:
                try:
                    messages = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for message_element in messages:
                        message_text = message_element.text.strip()
                        if message_text and not self._is_message_processed(message_text):
                            await self._process_chat_message(message_text)
                    break
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error checking chat messages: {e}")
    
    def _is_message_processed(self, message: str) -> bool:
        """
        Check if a message has already been processed.
        """
        return any(msg.content == message for msg in self.meeting_transcript)
    
    async def _process_chat_message(self, message: str) -> None:
        """
        Process a chat message and potentially respond.
        """
        try:
            # Create message object
            chat_message = MeetingMessage(
                speaker="Unknown",  # Would need to extract sender
                content=message,
                message_type=MessageType.GENERAL,
                timestamp=datetime.now(),
                context_used=[],
                confidence=1.0
            )
            
            self.meeting_transcript.append(chat_message)
            
            # Check if agent should respond
            if await self._should_respond_to_message(message):
                response = await self.agent.generate_response(
                    message, 
                    self.current_meeting_context
                )
                
                await self._send_chat_message(response.content)
                self.meeting_transcript.append(response)
            
        except Exception as e:
            self.logger.error(f"Error processing chat message: {e}")
    
    async def _should_respond_to_message(self, message: str) -> bool:
        """
        Determine if the agent should respond to a message.
        """
        # Similar logic to Teams bot
        agent_name = self.agent.employee_config.name.lower()
        message_lower = message.lower()
        
        # Respond if mentioned
        if agent_name in message_lower:
            return True
        
        # Respond to status requests
        response_triggers = ['status', 'update', 'progress', 'blocker']
        if any(trigger in message_lower for trigger in response_triggers):
            return True
        
        return False
    
    async def _send_chat_message(self, message: str) -> None:
        """
        Send a chat message to the meeting.
        """
        try:
            # Look for chat input
            chat_input_selectors = [
                "input[placeholder*='message']",
                "textarea[placeholder*='message']",
                "[data-testid='chat-input']"
            ]
            
            for selector in chat_input_selectors:
                try:
                    chat_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    chat_input.clear()
                    chat_input.send_keys(message)
                    
                    # Look for send button
                    send_button = self.driver.find_element(
                        By.CSS_SELECTOR, 
                        "button[aria-label*='Send'], button[data-testid='send-button']"
                    )
                    send_button.click()
                    
                    self.logger.info(f"Sent chat message: {message[:50]}...")
                    break
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error sending chat message: {e}")
    
    async def _is_meeting_active(self) -> bool:
        """
        Check if the meeting is still active.
        """
        try:
            # Look for indicators that meeting is active
            active_indicators = [
                "[data-meeting-state='active']",
                ".meeting-controls",
                "button[aria-label*='Leave']"
            ]
            
            for selector in active_indicators:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, selector)
                    return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking meeting status: {e}")
            return False
    
    def _extract_meeting_id(self, meeting_url: str) -> str:
        """
        Extract meeting ID from Google Meet URL.
        """
        # Extract meeting ID from URL pattern
        match = re.search(r'/([a-z0-9-]+)(?:\?|$)', meeting_url)
        return match.group(1) if match else "unknown"
    
    async def leave_meeting(self) -> None:
        """
        Leave the current meeting.
        """
        try:
            if not self.is_in_meeting:
                return
            
            self.logger.info("Leaving Google Meet")
            
            # Process meeting completion
            if self.current_meeting_context:
                from ..post_meeting.action_handler import PostMeetingActionHandler
                
                action_handler = PostMeetingActionHandler()
                results = await action_handler.process_meeting_completion(
                    self.meeting_transcript,
                    self.current_meeting_context
                )
                
                self.logger.info(f"Meeting processed: {len(results['summary'].action_items) if results['summary'] else 0} action items")
            
            # Leave meeting
            leave_selectors = [
                "button[aria-label*='Leave']",
                "button[data-testid='leave-button']",
                "button:contains('Leave call')"
            ]
            
            for selector in leave_selectors:
                try:
                    leave_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    leave_button.click()
                    break
                except:
                    continue
            
            # Reset state
            self.is_in_meeting = False
            self.current_meeting_context = None
            self.meeting_transcript = []
            
        except Exception as e:
            self.logger.error(f"Error leaving meeting: {e}")
    
    async def cleanup(self) -> None:
        """
        Cleanup browser resources.
        """
        try:
            if self.is_in_meeting:
                await self.leave_meeting()
            
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            self.logger.info("Browser cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class GoogleMeetIntegrationManager:
    """
    Manages Google Meet integration for autonomous agents.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.logger = logging.getLogger("meet_integration")
        
        # Bot instances for each agent
        self.agent_bots: Dict[str, GoogleMeetBot] = {}
    
    async def initialize(self, agents: Dict[str, BaseAgent]) -> None:
        """
        Initialize Google Meet integration for all agents.
        """
        try:
            self.logger.info("Initializing Google Meet integration...")
            
            # Create bot instances for each agent
            for agent_id, agent in agents.items():
                bot = GoogleMeetBot(agent)
                self.agent_bots[agent_id] = bot
            
            self.logger.info(f"Google Meet integration initialized for {len(agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Meet integration: {e}")
            raise
    
    async def join_meeting(self, meeting_url: str, agent_id: str) -> bool:
        """
        Join a Google Meet meeting with the specified agent.
        """
        try:
            if agent_id not in self.agent_bots:
                self.logger.error(f"No bot found for agent: {agent_id}")
                return False
            
            bot = self.agent_bots[agent_id]
            return await bot.join_meeting(meeting_url)
            
        except Exception as e:
            self.logger.error(f"Failed to join meeting: {e}")
            return False
    
    async def leave_meeting(self, agent_id: str) -> None:
        """
        Leave meeting for the specified agent.
        """
        try:
            if agent_id in self.agent_bots:
                await self.agent_bots[agent_id].leave_meeting()
            
        except Exception as e:
            self.logger.error(f"Error leaving meeting for agent {agent_id}: {e}")
    
    async def cleanup(self) -> None:
        """
        Cleanup all Google Meet integration resources.
        """
        try:
            self.logger.info("Cleaning up Google Meet integration...")
            
            for bot in self.agent_bots.values():
                await bot.cleanup()
            
            self.agent_bots.clear()
            
            self.logger.info("Google Meet integration cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during Google Meet integration cleanup: {e}")


# Example usage
async def test_google_meet_integration():
    """
    Test function for Google Meet integration.
    """
    from ..config.config_manager import ConfigManager
    from ..agents.agent_manager import AgentManager
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize agents
    agent_manager = AgentManager(config_manager)
    await agent_manager.initialize()
    
    # Initialize Google Meet integration
    meet_manager = GoogleMeetIntegrationManager(config_manager)
    await meet_manager.initialize(agent_manager.agents)
    
    # Test joining a meeting
    meeting_url = "https://meet.google.com/abc-defg-hij"
    success = await meet_manager.join_meeting(meeting_url, "vivek")
    
    print(f"Meeting join test: {'Success' if success else 'Failed'}")
    
    # Wait a bit, then leave
    await asyncio.sleep(10)
    await meet_manager.leave_meeting("vivek")
    
    # Cleanup
    await meet_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(test_google_meet_integration())

