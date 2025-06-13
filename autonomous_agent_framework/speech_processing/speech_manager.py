"""
Speech processing manager for autonomous agent framework.
Coordinates between different speech-to-text services.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

from ..config.config_manager import ConfigManager


class SpeechProvider(Enum):
    """Supported speech-to-text providers."""
    AZURE = "azure"
    GOOGLE_CLOUD = "google_cloud"
    OPENAI_WHISPER = "whisper"


class SpeechProcessingManager:
    """
    Manages speech-to-text processing across multiple providers.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.logger = logging.getLogger("speech_processing_manager")
        
        # Provider integrations
        self.azure_integration = None
        self.google_integration = None
        self.whisper_integration = None
        
        # Configuration
        self.preferred_provider = self._get_preferred_provider()
        self.enabled_providers = self._get_enabled_providers()
        self.fallback_enabled = self.config.speech_config.get('enable_fallback', True)
        
        # Active transcriptions
        self.active_transcriptions: Dict[str, Dict[str, Any]] = {}
        
        # Global transcription callback
        self.global_callback: Optional[Callable] = None
    
    def _get_preferred_provider(self) -> SpeechProvider:
        """Get the preferred speech provider from configuration."""
        provider_name = self.config.speech_config.get('preferred_provider', 'azure')
        try:
            return SpeechProvider(provider_name.lower())
        except ValueError:
            self.logger.warning(f"Unknown provider '{provider_name}', defaulting to Azure")
            return SpeechProvider.AZURE
    
    def _get_enabled_providers(self) -> List[SpeechProvider]:
        """Get list of enabled speech providers."""
        enabled = self.config.speech_config.get('enabled_providers', ['azure', 'google_cloud', 'whisper'])
        providers = []
        
        for provider_name in enabled:
            try:
                providers.append(SpeechProvider(provider_name.lower()))
            except ValueError:
                self.logger.warning(f"Unknown provider '{provider_name}', skipping")
        
        return providers
    
    async def initialize(self) -> None:
        """
        Initialize all enabled speech processing integrations.
        """
        try:
            self.logger.info("Initializing speech processing integrations...")
            
            # Initialize Azure Speech if enabled
            if SpeechProvider.AZURE in self.enabled_providers:
                await self._initialize_azure_integration()
            
            # Initialize Google Cloud Speech if enabled
            if SpeechProvider.GOOGLE_CLOUD in self.enabled_providers:
                await self._initialize_google_integration()
            
            # Initialize OpenAI Whisper if enabled
            if SpeechProvider.OPENAI_WHISPER in self.enabled_providers:
                await self._initialize_whisper_integration()
            
            self.logger.info(f"Initialized {len(self.get_available_providers())} speech providers")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize speech processing: {e}")
            raise
    
    async def _initialize_azure_integration(self) -> None:
        """Initialize Azure Speech integration."""
        try:
            from .azure_speech import AzureSpeechIntegrationManager
            
            self.azure_integration = AzureSpeechIntegrationManager(self.config_manager)
            
            if await self.azure_integration.initialize():
                self.logger.info("Azure Speech integration initialized")
            else:
                self.logger.warning("Failed to initialize Azure Speech integration")
                self.azure_integration = None
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure Speech integration: {e}")
            self.azure_integration = None
    
    async def _initialize_google_integration(self) -> None:
        """Initialize Google Cloud Speech integration."""
        try:
            from .google_speech import GoogleSpeechIntegrationManager
            
            self.google_integration = GoogleSpeechIntegrationManager(self.config_manager)
            
            if await self.google_integration.initialize():
                self.logger.info("Google Cloud Speech integration initialized")
            else:
                self.logger.warning("Failed to initialize Google Cloud Speech integration")
                self.google_integration = None
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Cloud Speech integration: {e}")
            self.google_integration = None
    
    async def _initialize_whisper_integration(self) -> None:
        """Initialize OpenAI Whisper integration."""
        try:
            from .whisper_integration import WhisperIntegrationManager
            
            self.whisper_integration = WhisperIntegrationManager(self.config_manager)
            
            if await self.whisper_integration.initialize():
                self.logger.info("OpenAI Whisper integration initialized")
            else:
                self.logger.warning("Failed to initialize OpenAI Whisper integration")
                self.whisper_integration = None
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI Whisper integration: {e}")
            self.whisper_integration = None
    
    async def start_meeting_transcription(self, meeting_id: str, 
                                        provider: Optional[SpeechProvider] = None,
                                        callback: Optional[Callable] = None) -> bool:
        """
        Start transcription for a meeting.
        
        Args:
            meeting_id: Unique identifier for the meeting
            provider: Specific provider to use (auto-select if None)
            callback: Callback function for transcription results
        
        Returns:
            True if transcription started successfully, False otherwise
        """
        try:
            if meeting_id in self.active_transcriptions:
                self.logger.warning(f"Transcription already active for meeting: {meeting_id}")
                return True
            
            # Select provider
            if provider is None:
                provider = self._select_best_provider()
            
            if not self.is_provider_available(provider):
                if self.fallback_enabled:
                    provider = self._select_fallback_provider()
                    if not provider:
                        self.logger.error("No available speech providers")
                        return False
                else:
                    self.logger.error(f"Provider {provider.value} not available")
                    return False
            
            self.logger.info(f"Starting transcription for meeting {meeting_id} using {provider.value}")
            
            # Set up callback wrapper
            async def transcription_callback(result):
                result['provider'] = provider.value
                
                # Call global callback if set
                if self.global_callback:
                    await self.global_callback(result)
                
                # Call specific callback if provided
                if callback:
                    await callback(result)
            
            # Start transcription with selected provider
            success = False
            if provider == SpeechProvider.AZURE and self.azure_integration:
                success = await self.azure_integration.start_meeting_transcription(
                    meeting_id, transcription_callback
                )
            elif provider == SpeechProvider.GOOGLE_CLOUD and self.google_integration:
                success = await self.google_integration.start_meeting_transcription(
                    meeting_id, transcription_callback
                )
            elif provider == SpeechProvider.OPENAI_WHISPER and self.whisper_integration:
                success = await self.whisper_integration.start_meeting_transcription(
                    meeting_id, transcription_callback
                )
            
            if success:
                self.active_transcriptions[meeting_id] = {
                    'provider': provider,
                    'start_time': datetime.now(),
                    'callback': callback
                }
                self.logger.info(f"Started transcription for meeting: {meeting_id}")
                return True
            else:
                self.logger.error(f"Failed to start transcription for meeting: {meeting_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error starting meeting transcription: {e}")
            return False
    
    def _select_best_provider(self) -> SpeechProvider:
        """
        Select the best available provider based on preferences and availability.
        """
        # First try preferred provider
        if self.is_provider_available(self.preferred_provider):
            return self.preferred_provider
        
        # Try other providers in order of preference
        provider_priority = [
            SpeechProvider.AZURE,
            SpeechProvider.GOOGLE_CLOUD,
            SpeechProvider.OPENAI_WHISPER
        ]
        
        for provider in provider_priority:
            if self.is_provider_available(provider):
                return provider
        
        # Fallback to first available
        available = self.get_available_providers()
        if available:
            return available[0]
        
        return self.preferred_provider  # Will fail later if not available
    
    def _select_fallback_provider(self) -> Optional[SpeechProvider]:
        """
        Select a fallback provider when the primary fails.
        """
        available = self.get_available_providers()
        
        # Remove preferred provider from fallback options
        fallback_options = [p for p in available if p != self.preferred_provider]
        
        return fallback_options[0] if fallback_options else None
    
    async def stop_meeting_transcription(self, meeting_id: str) -> None:
        """
        Stop transcription for a meeting.
        """
        try:
            if meeting_id not in self.active_transcriptions:
                self.logger.warning(f"No active transcription for meeting: {meeting_id}")
                return
            
            transcription_info = self.active_transcriptions[meeting_id]
            provider = transcription_info['provider']
            
            self.logger.info(f"Stopping transcription for meeting {meeting_id} (provider: {provider.value})")
            
            # Stop transcription with the appropriate provider
            if provider == SpeechProvider.AZURE and self.azure_integration:
                await self.azure_integration.stop_meeting_transcription(meeting_id)
            elif provider == SpeechProvider.GOOGLE_CLOUD and self.google_integration:
                await self.google_integration.stop_meeting_transcription(meeting_id)
            elif provider == SpeechProvider.OPENAI_WHISPER and self.whisper_integration:
                await self.whisper_integration.stop_meeting_transcription(meeting_id)
            
            # Remove from active transcriptions
            del self.active_transcriptions[meeting_id]
            
            self.logger.info(f"Stopped transcription for meeting: {meeting_id}")
            
        except Exception as e:
            self.logger.error(f"Error stopping meeting transcription: {e}")
    
    async def process_meeting_audio(self, meeting_id: str, audio_data: bytes) -> None:
        """
        Process audio data for a specific meeting.
        """
        try:
            if meeting_id not in self.active_transcriptions:
                return
            
            transcription_info = self.active_transcriptions[meeting_id]
            provider = transcription_info['provider']
            
            # Route audio to the appropriate provider
            if provider == SpeechProvider.AZURE and self.azure_integration:
                await self.azure_integration.process_meeting_audio(meeting_id, audio_data)
            elif provider == SpeechProvider.GOOGLE_CLOUD and self.google_integration:
                await self.google_integration.process_meeting_audio(meeting_id, audio_data)
            elif provider == SpeechProvider.OPENAI_WHISPER and self.whisper_integration:
                await self.whisper_integration.process_meeting_audio(meeting_id, audio_data)
            
        except Exception as e:
            self.logger.error(f"Error processing audio for meeting {meeting_id}: {e}")
    
    def set_meeting_speaker(self, meeting_id: str, speaker: str) -> None:
        """
        Set the current speaker for a meeting.
        """
        try:
            if meeting_id not in self.active_transcriptions:
                return
            
            transcription_info = self.active_transcriptions[meeting_id]
            provider = transcription_info['provider']
            
            # Set speaker for the appropriate provider
            if provider == SpeechProvider.AZURE and self.azure_integration:
                self.azure_integration.set_meeting_speaker(meeting_id, speaker)
            elif provider == SpeechProvider.GOOGLE_CLOUD and self.google_integration:
                self.google_integration.set_meeting_speaker(meeting_id, speaker)
            elif provider == SpeechProvider.OPENAI_WHISPER and self.whisper_integration:
                self.whisper_integration.set_meeting_speaker(meeting_id, speaker)
            
        except Exception as e:
            self.logger.error(f"Error setting speaker for meeting {meeting_id}: {e}")
    
    def get_meeting_transcript(self, meeting_id: str) -> List[Dict[str, Any]]:
        """
        Get transcript for a specific meeting.
        """
        try:
            if meeting_id not in self.active_transcriptions:
                return []
            
            transcription_info = self.active_transcriptions[meeting_id]
            provider = transcription_info['provider']
            
            # Get transcript from the appropriate provider
            if provider == SpeechProvider.AZURE and self.azure_integration:
                return self.azure_integration.get_meeting_transcript(meeting_id)
            elif provider == SpeechProvider.GOOGLE_CLOUD and self.google_integration:
                return self.google_integration.get_meeting_transcript(meeting_id)
            elif provider == SpeechProvider.OPENAI_WHISPER and self.whisper_integration:
                return self.whisper_integration.get_meeting_transcript(meeting_id)
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting transcript for meeting {meeting_id}: {e}")
            return []
    
    async def transcribe_audio_file(self, file_path: str, 
                                  provider: Optional[SpeechProvider] = None) -> List[Dict[str, Any]]:
        """
        Transcribe an audio file using the specified provider.
        """
        try:
            if provider is None:
                provider = self._select_best_provider()
            
            if not self.is_provider_available(provider):
                self.logger.error(f"Provider {provider.value} not available")
                return []
            
            self.logger.info(f"Transcribing audio file using {provider.value}")
            
            # Transcribe with selected provider
            if provider == SpeechProvider.AZURE and self.azure_integration:
                return await self.azure_integration.transcribe_audio_file(file_path)
            elif provider == SpeechProvider.GOOGLE_CLOUD and self.google_integration:
                return await self.google_integration.transcribe_audio_file(file_path)
            elif provider == SpeechProvider.OPENAI_WHISPER and self.whisper_integration:
                return await self.whisper_integration.transcribe_audio_file(file_path)
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error transcribing audio file: {e}")
            return []
    
    def get_available_providers(self) -> List[SpeechProvider]:
        """Get list of available (initialized) providers."""
        available = []
        
        if self.azure_integration:
            available.append(SpeechProvider.AZURE)
        
        if self.google_integration:
            available.append(SpeechProvider.GOOGLE_CLOUD)
        
        if self.whisper_integration:
            available.append(SpeechProvider.OPENAI_WHISPER)
        
        return available
    
    def is_provider_available(self, provider: SpeechProvider) -> bool:
        """Check if a specific provider is available."""
        return provider in self.get_available_providers()
    
    def get_active_transcriptions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active transcriptions."""
        return self.active_transcriptions.copy()
    
    def set_global_callback(self, callback: Callable) -> None:
        """Set a global callback for all transcription results."""
        self.global_callback = callback
    
    async def cleanup(self) -> None:
        """
        Cleanup all speech processing integrations.
        """
        try:
            self.logger.info("Cleaning up speech processing integrations...")
            
            # Stop all active transcriptions
            for meeting_id in list(self.active_transcriptions.keys()):
                await self.stop_meeting_transcription(meeting_id)
            
            # Cleanup individual integrations
            if self.azure_integration:
                await self.azure_integration.cleanup()
            
            if self.google_integration:
                await self.google_integration.cleanup()
            
            if self.whisper_integration:
                await self.whisper_integration.cleanup()
            
            self.logger.info("Speech processing cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during speech processing cleanup: {e}")


# Configuration helper functions
def add_speech_processing_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add speech processing configuration to the main config.
    """
    if 'speech_processing' not in config:
        config['speech_processing'] = {}
    
    # Default configuration
    config['speech_processing'].update({
        'preferred_provider': 'azure',
        'enabled_providers': ['azure', 'google_cloud', 'whisper'],
        'enable_fallback': True,
        
        # Real-time processing settings
        'real_time': {
            'chunk_duration_seconds': 30,
            'enable_partial_results': True,
            'enable_speaker_diarization': True,
            'max_speakers': 8
        },
        
        # Quality settings
        'quality': {
            'sample_rate': 16000,
            'audio_format': 'wav',
            'enable_noise_reduction': True,
            'confidence_threshold': 0.7
        },
        
        # Provider-specific settings
        'azure': {
            'language': 'en-US',
            'enable_dictation': True,
            'enable_profanity_filter': False
        },
        
        'google_cloud': {
            'language': 'en-US',
            'model': 'latest_long',
            'use_enhanced': True,
            'enable_automatic_punctuation': True
        },
        
        'whisper': {
            'model': 'whisper-1',
            'response_format': 'verbose_json',
            'enable_translation': False,
            'chunk_duration_seconds': 30
        }
    })
    
    return config


# Example usage and testing
async def test_speech_processing_manager():
    """
    Test function for speech processing manager.
    """
    from ..config.config_manager import ConfigManager
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize speech processing manager
    speech_manager = SpeechProcessingManager(config_manager)
    await speech_manager.initialize()
    
    # Set up transcription callback
    async def transcription_callback(result):
        print(f"[{result['provider']}] [{result['speaker']}] {result['text']} (confidence: {result['confidence']:.2f})")
    
    speech_manager.set_global_callback(transcription_callback)
    
    # Test provider selection
    print(f"Available providers: {[p.value for p in speech_manager.get_available_providers()]}")
    print(f"Preferred provider: {speech_manager.preferred_provider.value}")
    
    # Start meeting transcription
    meeting_id = "test_meeting_001"
    success = await speech_manager.start_meeting_transcription(meeting_id)
    
    if success:
        print(f"Started transcription for meeting: {meeting_id}")
        
        # Simulate some processing time
        await asyncio.sleep(10)
        
        # Get transcript
        transcript = speech_manager.get_meeting_transcript(meeting_id)
        print(f"Transcript has {len(transcript)} entries")
        
        # Stop transcription
        await speech_manager.stop_meeting_transcription(meeting_id)
    
    # Cleanup
    await speech_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(test_speech_processing_manager())

