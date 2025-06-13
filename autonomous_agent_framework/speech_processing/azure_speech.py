"""
Azure Speech-to-Text integration for autonomous agent framework.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import json
import io
import wave

try:
    import azure.cognitiveservices.speech as speechsdk
    from azure.cognitiveservices.speech import SpeechConfig, AudioConfig
    from azure.cognitiveservices.speech.audio import AudioStreamFormat, PushAudioInputStream
except ImportError:
    # Mock for development without Azure SDK
    speechsdk = None
    SpeechConfig = None
    AudioConfig = None

from ..agents.base_agent import MeetingMessage, MessageType
from ..config.config_manager import ConfigManager


class AzureSpeechProcessor:
    """
    Azure Speech-to-Text processor for real-time meeting transcription.
    """
    
    def __init__(self, subscription_key: str, region: str):
        self.subscription_key = subscription_key
        self.region = region
        self.logger = logging.getLogger("azure_speech")
        
        # Speech configuration
        self.speech_config: Optional[SpeechConfig] = None
        self.audio_config: Optional[AudioConfig] = None
        self.speech_recognizer = None
        
        # Transcription state
        self.is_listening = False
        self.transcription_callback: Optional[Callable] = None
        self.current_speaker = "Unknown"
        
        # Audio stream
        self.audio_stream: Optional[PushAudioInputStream] = None
        
        # Transcription results
        self.partial_results: List[str] = []
        self.final_results: List[Dict[str, Any]] = []
    
    async def initialize(self) -> bool:
        """
        Initialize Azure Speech service.
        """
        try:
            if not speechsdk:
                self.logger.error("Azure Speech SDK not available. Install with: pip install azure-cognitiveservices-speech")
                return False
            
            # Create speech configuration
            self.speech_config = SpeechConfig(
                subscription=self.subscription_key,
                region=self.region
            )
            
            # Configure recognition settings
            self.speech_config.speech_recognition_language = "en-US"
            self.speech_config.enable_dictation()
            
            # Enable speaker diarization
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_EnableAudioLogging, 
                "true"
            )
            
            # Create audio stream
            audio_format = AudioStreamFormat(
                samples_per_second=16000,
                bits_per_sample=16,
                channels=1
            )
            self.audio_stream = PushAudioInputStream(audio_format)
            
            # Create audio configuration
            self.audio_config = AudioConfig(stream=self.audio_stream)
            
            # Create speech recognizer
            self.speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=self.audio_config
            )
            
            # Set up event handlers
            self._setup_event_handlers()
            
            self.logger.info("Azure Speech service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure Speech service: {e}")
            return False
    
    def _setup_event_handlers(self) -> None:
        """
        Set up event handlers for speech recognition.
        """
        if not self.speech_recognizer:
            return
        
        # Handle partial results (real-time)
        self.speech_recognizer.recognizing.connect(self._on_recognizing)
        
        # Handle final results
        self.speech_recognizer.recognized.connect(self._on_recognized)
        
        # Handle session events
        self.speech_recognizer.session_started.connect(self._on_session_started)
        self.speech_recognizer.session_stopped.connect(self._on_session_stopped)
        
        # Handle errors
        self.speech_recognizer.canceled.connect(self._on_canceled)
    
    def _on_recognizing(self, evt) -> None:
        """
        Handle partial recognition results.
        """
        try:
            if evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
                partial_text = evt.result.text
                if partial_text:
                    self.partial_results.append(partial_text)
                    self.logger.debug(f"Partial: {partial_text}")
                    
                    # Call callback if set
                    if self.transcription_callback:
                        asyncio.create_task(self.transcription_callback({
                            'type': 'partial',
                            'text': partial_text,
                            'speaker': self.current_speaker,
                            'timestamp': datetime.now(),
                            'confidence': 0.5  # Partial results have lower confidence
                        }))
        
        except Exception as e:
            self.logger.error(f"Error in recognizing handler: {e}")
    
    def _on_recognized(self, evt) -> None:
        """
        Handle final recognition results.
        """
        try:
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                final_text = evt.result.text
                if final_text:
                    result = {
                        'type': 'final',
                        'text': final_text,
                        'speaker': self.current_speaker,
                        'timestamp': datetime.now(),
                        'confidence': self._extract_confidence(evt.result),
                        'duration': evt.result.duration.total_seconds() if evt.result.duration else 0
                    }
                    
                    self.final_results.append(result)
                    self.logger.info(f"Final: {final_text}")
                    
                    # Call callback if set
                    if self.transcription_callback:
                        asyncio.create_task(self.transcription_callback(result))
            
            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                self.logger.debug("No speech could be recognized")
        
        except Exception as e:
            self.logger.error(f"Error in recognized handler: {e}")
    
    def _on_session_started(self, evt) -> None:
        """
        Handle session started event.
        """
        self.logger.info("Speech recognition session started")
    
    def _on_session_stopped(self, evt) -> None:
        """
        Handle session stopped event.
        """
        self.logger.info("Speech recognition session stopped")
        self.is_listening = False
    
    def _on_canceled(self, evt) -> None:
        """
        Handle recognition canceled event.
        """
        self.logger.error(f"Speech recognition canceled: {evt.result.cancellation_details.reason}")
        if evt.result.cancellation_details.error_details:
            self.logger.error(f"Error details: {evt.result.cancellation_details.error_details}")
        self.is_listening = False
    
    def _extract_confidence(self, result) -> float:
        """
        Extract confidence score from recognition result.
        """
        try:
            # Azure Speech SDK provides confidence in the result properties
            # This is a simplified extraction
            return 0.9  # Default high confidence for final results
        except:
            return 0.8
    
    async def start_continuous_recognition(self, callback: Optional[Callable] = None) -> bool:
        """
        Start continuous speech recognition.
        """
        try:
            if not self.speech_recognizer:
                self.logger.error("Speech recognizer not initialized")
                return False
            
            if self.is_listening:
                self.logger.warning("Already listening")
                return True
            
            self.transcription_callback = callback
            
            # Start continuous recognition
            self.speech_recognizer.start_continuous_recognition()
            self.is_listening = True
            
            self.logger.info("Started continuous speech recognition")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start continuous recognition: {e}")
            return False
    
    async def stop_continuous_recognition(self) -> None:
        """
        Stop continuous speech recognition.
        """
        try:
            if self.speech_recognizer and self.is_listening:
                self.speech_recognizer.stop_continuous_recognition()
                self.is_listening = False
                self.logger.info("Stopped continuous speech recognition")
        
        except Exception as e:
            self.logger.error(f"Error stopping recognition: {e}")
    
    async def process_audio_chunk(self, audio_data: bytes) -> None:
        """
        Process a chunk of audio data.
        """
        try:
            if self.audio_stream and self.is_listening:
                self.audio_stream.write(audio_data)
        
        except Exception as e:
            self.logger.error(f"Error processing audio chunk: {e}")
    
    async def transcribe_audio_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Transcribe an audio file (batch processing).
        """
        try:
            if not speechsdk:
                self.logger.error("Azure Speech SDK not available")
                return []
            
            # Create audio configuration for file
            audio_config = AudioConfig(filename=file_path)
            
            # Create recognizer for file
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Perform recognition
            result = recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return [{
                    'type': 'final',
                    'text': result.text,
                    'speaker': 'Unknown',
                    'timestamp': datetime.now(),
                    'confidence': self._extract_confidence(result),
                    'duration': result.duration.total_seconds() if result.duration else 0
                }]
            else:
                self.logger.warning(f"Recognition failed: {result.reason}")
                return []
        
        except Exception as e:
            self.logger.error(f"Error transcribing audio file: {e}")
            return []
    
    def set_current_speaker(self, speaker: str) -> None:
        """
        Set the current speaker for attribution.
        """
        self.current_speaker = speaker
    
    def get_transcription_results(self, final_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get transcription results.
        """
        if final_only:
            return self.final_results.copy()
        else:
            # Combine partial and final results
            all_results = []
            for partial in self.partial_results:
                all_results.append({
                    'type': 'partial',
                    'text': partial,
                    'speaker': self.current_speaker,
                    'timestamp': datetime.now(),
                    'confidence': 0.5
                })
            all_results.extend(self.final_results)
            return all_results
    
    def clear_results(self) -> None:
        """
        Clear transcription results.
        """
        self.partial_results.clear()
        self.final_results.clear()
    
    async def cleanup(self) -> None:
        """
        Cleanup resources.
        """
        try:
            await self.stop_continuous_recognition()
            
            if self.audio_stream:
                self.audio_stream.close()
                self.audio_stream = None
            
            self.speech_recognizer = None
            self.speech_config = None
            self.audio_config = None
            
            self.logger.info("Azure Speech processor cleanup completed")
        
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class AzureSpeechIntegrationManager:
    """
    Manages Azure Speech-to-Text integration for the autonomous agent framework.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.logger = logging.getLogger("azure_speech_manager")
        
        # Azure configuration
        self.subscription_key = self.config.api_credentials.get('azure_speech_key')
        self.region = self.config.api_credentials.get('azure_speech_region', 'eastus')
        
        # Speech processors for different meetings/contexts
        self.processors: Dict[str, AzureSpeechProcessor] = {}
        
        # Global transcription callback
        self.global_transcription_callback: Optional[Callable] = None
    
    async def initialize(self) -> bool:
        """
        Initialize Azure Speech integration.
        """
        try:
            if not self.subscription_key:
                self.logger.error("Azure Speech subscription key not configured")
                return False
            
            self.logger.info("Azure Speech integration initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure Speech integration: {e}")
            return False
    
    async def create_processor(self, processor_id: str) -> Optional[AzureSpeechProcessor]:
        """
        Create a new speech processor instance.
        """
        try:
            if processor_id in self.processors:
                self.logger.warning(f"Processor {processor_id} already exists")
                return self.processors[processor_id]
            
            processor = AzureSpeechProcessor(self.subscription_key, self.region)
            
            if await processor.initialize():
                self.processors[processor_id] = processor
                self.logger.info(f"Created speech processor: {processor_id}")
                return processor
            else:
                self.logger.error(f"Failed to initialize processor: {processor_id}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error creating processor {processor_id}: {e}")
            return None
    
    async def start_meeting_transcription(self, meeting_id: str, 
                                        callback: Optional[Callable] = None) -> bool:
        """
        Start transcription for a meeting.
        """
        try:
            processor = await self.create_processor(meeting_id)
            if not processor:
                return False
            
            # Set up callback that includes meeting context
            async def meeting_callback(result):
                result['meeting_id'] = meeting_id
                
                # Call global callback if set
                if self.global_transcription_callback:
                    await self.global_transcription_callback(result)
                
                # Call specific callback if provided
                if callback:
                    await callback(result)
            
            return await processor.start_continuous_recognition(meeting_callback)
        
        except Exception as e:
            self.logger.error(f"Error starting meeting transcription: {e}")
            return False
    
    async def stop_meeting_transcription(self, meeting_id: str) -> None:
        """
        Stop transcription for a meeting.
        """
        try:
            if meeting_id in self.processors:
                processor = self.processors[meeting_id]
                await processor.stop_continuous_recognition()
                await processor.cleanup()
                del self.processors[meeting_id]
                self.logger.info(f"Stopped transcription for meeting: {meeting_id}")
        
        except Exception as e:
            self.logger.error(f"Error stopping meeting transcription: {e}")
    
    async def process_meeting_audio(self, meeting_id: str, audio_data: bytes) -> None:
        """
        Process audio data for a specific meeting.
        """
        try:
            if meeting_id in self.processors:
                await self.processors[meeting_id].process_audio_chunk(audio_data)
        
        except Exception as e:
            self.logger.error(f"Error processing audio for meeting {meeting_id}: {e}")
    
    def set_meeting_speaker(self, meeting_id: str, speaker: str) -> None:
        """
        Set the current speaker for a meeting.
        """
        if meeting_id in self.processors:
            self.processors[meeting_id].set_current_speaker(speaker)
    
    def get_meeting_transcript(self, meeting_id: str) -> List[Dict[str, Any]]:
        """
        Get transcript for a specific meeting.
        """
        if meeting_id in self.processors:
            return self.processors[meeting_id].get_transcription_results()
        return []
    
    def set_global_transcription_callback(self, callback: Callable) -> None:
        """
        Set a global callback for all transcription results.
        """
        self.global_transcription_callback = callback
    
    async def transcribe_audio_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Transcribe an audio file using a temporary processor.
        """
        try:
            temp_processor = AzureSpeechProcessor(self.subscription_key, self.region)
            
            if await temp_processor.initialize():
                results = await temp_processor.transcribe_audio_file(file_path)
                await temp_processor.cleanup()
                return results
            else:
                return []
        
        except Exception as e:
            self.logger.error(f"Error transcribing audio file: {e}")
            return []
    
    async def cleanup(self) -> None:
        """
        Cleanup all speech processors.
        """
        try:
            self.logger.info("Cleaning up Azure Speech integration...")
            
            for meeting_id in list(self.processors.keys()):
                await self.stop_meeting_transcription(meeting_id)
            
            self.processors.clear()
            
            self.logger.info("Azure Speech integration cleanup completed")
        
        except Exception as e:
            self.logger.error(f"Error during Azure Speech cleanup: {e}")


# Example usage and testing
async def test_azure_speech_integration():
    """
    Test function for Azure Speech integration.
    """
    from ..config.config_manager import ConfigManager
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize Azure Speech integration
    azure_manager = AzureSpeechIntegrationManager(config_manager)
    
    if not await azure_manager.initialize():
        print("Failed to initialize Azure Speech integration")
        return
    
    # Set up transcription callback
    async def transcription_callback(result):
        print(f"Transcription: [{result['speaker']}] {result['text']} (confidence: {result['confidence']:.2f})")
    
    azure_manager.set_global_transcription_callback(transcription_callback)
    
    # Start meeting transcription
    meeting_id = "test_meeting_001"
    success = await azure_manager.start_meeting_transcription(meeting_id)
    
    if success:
        print("Started meeting transcription")
        
        # Simulate some processing time
        await asyncio.sleep(10)
        
        # Get transcript
        transcript = azure_manager.get_meeting_transcript(meeting_id)
        print(f"Transcript has {len(transcript)} entries")
        
        # Stop transcription
        await azure_manager.stop_meeting_transcription(meeting_id)
    
    # Cleanup
    await azure_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(test_azure_speech_integration())

