"""
Google Cloud Speech-to-Text integration for autonomous agent framework.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import json
import io

try:
    from google.cloud import speech
    from google.cloud.speech import RecognitionConfig, StreamingRecognitionConfig
    from google.cloud.speech import StreamingRecognizeRequest, StreamingRecognizeResponse
    from google.oauth2 import service_account
except ImportError:
    # Mock for development without Google Cloud SDK
    speech = None
    RecognitionConfig = None
    StreamingRecognitionConfig = None

from ..agents.base_agent import MeetingMessage, MessageType
from ..config.config_manager import ConfigManager


class GoogleSpeechProcessor:
    """
    Google Cloud Speech-to-Text processor for real-time meeting transcription.
    """
    
    def __init__(self, credentials_path: str, project_id: str):
        self.credentials_path = credentials_path
        self.project_id = project_id
        self.logger = logging.getLogger("google_speech")
        
        # Speech client
        self.client: Optional[speech.SpeechClient] = None
        
        # Configuration
        self.config: Optional[RecognitionConfig] = None
        self.streaming_config: Optional[StreamingRecognitionConfig] = None
        
        # Transcription state
        self.is_listening = False
        self.transcription_callback: Optional[Callable] = None
        self.current_speaker = "Unknown"
        
        # Audio streaming
        self.audio_generator = None
        self.requests_generator = None
        
        # Transcription results
        self.partial_results: List[str] = []
        self.final_results: List[Dict[str, Any]] = []
    
    async def initialize(self) -> bool:
        """
        Initialize Google Cloud Speech service.
        """
        try:
            if not speech:
                self.logger.error("Google Cloud Speech SDK not available. Install with: pip install google-cloud-speech")
                return False
            
            # Initialize credentials
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = speech.SpeechClient(credentials=credentials)
            else:
                # Use default credentials
                self.client = speech.SpeechClient()
            
            # Configure recognition settings
            self.config = RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
                enable_automatic_punctuation=True,
                enable_speaker_diarization=True,
                diarization_speaker_count=8,  # Max speakers in meeting
                model="latest_long",  # Best for meetings
                use_enhanced=True
            )
            
            # Configure streaming settings
            self.streaming_config = StreamingRecognitionConfig(
                config=self.config,
                interim_results=True,  # Enable partial results
                single_utterance=False  # Continuous recognition
            )
            
            self.logger.info("Google Cloud Speech service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Cloud Speech service: {e}")
            return False
    
    async def start_continuous_recognition(self, callback: Optional[Callable] = None) -> bool:
        """
        Start continuous speech recognition.
        """
        try:
            if not self.client:
                self.logger.error("Speech client not initialized")
                return False
            
            if self.is_listening:
                self.logger.warning("Already listening")
                return True
            
            self.transcription_callback = callback
            self.is_listening = True
            
            # Start streaming recognition in background task
            asyncio.create_task(self._streaming_recognition_loop())
            
            self.logger.info("Started continuous speech recognition")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start continuous recognition: {e}")
            return False
    
    async def _streaming_recognition_loop(self) -> None:
        """
        Main streaming recognition loop.
        """
        try:
            # Create audio generator
            self.audio_generator = self._audio_generator()
            
            # Create requests generator
            self.requests_generator = self._request_generator()
            
            # Start streaming recognition
            responses = self.client.streaming_recognize(self.requests_generator)
            
            # Process responses
            await self._process_streaming_responses(responses)
            
        except Exception as e:
            self.logger.error(f"Error in streaming recognition loop: {e}")
            self.is_listening = False
    
    def _audio_generator(self):
        """
        Generator for audio chunks.
        """
        while self.is_listening:
            # This would be connected to actual audio input
            # For now, yield empty chunks to maintain the structure
            yield b''
            asyncio.sleep(0.1)
    
    def _request_generator(self):
        """
        Generator for streaming requests.
        """
        # First request with configuration
        yield StreamingRecognizeRequest(streaming_config=self.streaming_config)
        
        # Subsequent requests with audio data
        for chunk in self.audio_generator:
            if chunk:
                yield StreamingRecognizeRequest(audio_content=chunk)
    
    async def _process_streaming_responses(self, responses) -> None:
        """
        Process streaming recognition responses.
        """
        try:
            for response in responses:
                if not self.is_listening:
                    break
                
                for result in response.results:
                    if result.alternatives:
                        transcript = result.alternatives[0].transcript
                        confidence = result.alternatives[0].confidence
                        
                        # Extract speaker information if available
                        speaker = self._extract_speaker_info(result)
                        
                        if result.is_final:
                            # Final result
                            await self._handle_final_result(transcript, confidence, speaker)
                        else:
                            # Partial result
                            await self._handle_partial_result(transcript, speaker)
        
        except Exception as e:
            self.logger.error(f"Error processing streaming responses: {e}")
    
    def _extract_speaker_info(self, result) -> str:
        """
        Extract speaker information from recognition result.
        """
        try:
            # Google Cloud Speech provides speaker diarization
            if hasattr(result, 'alternatives') and result.alternatives:
                alternative = result.alternatives[0]
                if hasattr(alternative, 'words') and alternative.words:
                    # Get speaker tag from first word
                    first_word = alternative.words[0]
                    if hasattr(first_word, 'speaker_tag'):
                        return f"Speaker {first_word.speaker_tag}"
            
            return self.current_speaker
        
        except Exception as e:
            self.logger.debug(f"Could not extract speaker info: {e}")
            return self.current_speaker
    
    async def _handle_partial_result(self, transcript: str, speaker: str) -> None:
        """
        Handle partial recognition result.
        """
        try:
            if transcript:
                self.partial_results.append(transcript)
                self.logger.debug(f"Partial [{speaker}]: {transcript}")
                
                # Call callback if set
                if self.transcription_callback:
                    await self.transcription_callback({
                        'type': 'partial',
                        'text': transcript,
                        'speaker': speaker,
                        'timestamp': datetime.now(),
                        'confidence': 0.5  # Partial results have lower confidence
                    })
        
        except Exception as e:
            self.logger.error(f"Error handling partial result: {e}")
    
    async def _handle_final_result(self, transcript: str, confidence: float, speaker: str) -> None:
        """
        Handle final recognition result.
        """
        try:
            if transcript:
                result = {
                    'type': 'final',
                    'text': transcript,
                    'speaker': speaker,
                    'timestamp': datetime.now(),
                    'confidence': confidence,
                    'duration': 0  # Would need to calculate from timing info
                }
                
                self.final_results.append(result)
                self.logger.info(f"Final [{speaker}]: {transcript} (confidence: {confidence:.2f})")
                
                # Call callback if set
                if self.transcription_callback:
                    await self.transcription_callback(result)
        
        except Exception as e:
            self.logger.error(f"Error handling final result: {e}")
    
    async def stop_continuous_recognition(self) -> None:
        """
        Stop continuous speech recognition.
        """
        try:
            self.is_listening = False
            self.logger.info("Stopped continuous speech recognition")
        
        except Exception as e:
            self.logger.error(f"Error stopping recognition: {e}")
    
    async def process_audio_chunk(self, audio_data: bytes) -> None:
        """
        Process a chunk of audio data.
        """
        try:
            # This would feed audio data to the streaming recognizer
            # Implementation depends on how audio is captured from meetings
            pass
        
        except Exception as e:
            self.logger.error(f"Error processing audio chunk: {e}")
    
    async def transcribe_audio_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Transcribe an audio file (batch processing).
        """
        try:
            if not self.client:
                self.logger.error("Speech client not initialized")
                return []
            
            # Read audio file
            with io.open(file_path, "rb") as audio_file:
                content = audio_file.read()
            
            # Create audio object
            audio = speech.RecognitionAudio(content=content)
            
            # Perform recognition
            response = self.client.recognize(config=self.config, audio=audio)
            
            results = []
            for result in response.results:
                if result.alternatives:
                    alternative = result.alternatives[0]
                    
                    # Extract speaker information
                    speaker = "Unknown"
                    if hasattr(alternative, 'words') and alternative.words:
                        first_word = alternative.words[0]
                        if hasattr(first_word, 'speaker_tag'):
                            speaker = f"Speaker {first_word.speaker_tag}"
                    
                    results.append({
                        'type': 'final',
                        'text': alternative.transcript,
                        'speaker': speaker,
                        'timestamp': datetime.now(),
                        'confidence': alternative.confidence,
                        'duration': 0
                    })
            
            return results
        
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
            
            self.client = None
            self.config = None
            self.streaming_config = None
            
            self.logger.info("Google Speech processor cleanup completed")
        
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class GoogleSpeechIntegrationManager:
    """
    Manages Google Cloud Speech-to-Text integration for the autonomous agent framework.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.logger = logging.getLogger("google_speech_manager")
        
        # Google Cloud configuration
        self.credentials_path = self.config.api_credentials.get('google_speech_credentials_path')
        self.project_id = self.config.api_credentials.get('google_cloud_project_id')
        
        # Speech processors for different meetings/contexts
        self.processors: Dict[str, GoogleSpeechProcessor] = {}
        
        # Global transcription callback
        self.global_transcription_callback: Optional[Callable] = None
    
    async def initialize(self) -> bool:
        """
        Initialize Google Cloud Speech integration.
        """
        try:
            if not self.project_id:
                self.logger.error("Google Cloud project ID not configured")
                return False
            
            self.logger.info("Google Cloud Speech integration initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Cloud Speech integration: {e}")
            return False
    
    async def create_processor(self, processor_id: str) -> Optional[GoogleSpeechProcessor]:
        """
        Create a new speech processor instance.
        """
        try:
            if processor_id in self.processors:
                self.logger.warning(f"Processor {processor_id} already exists")
                return self.processors[processor_id]
            
            processor = GoogleSpeechProcessor(self.credentials_path, self.project_id)
            
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
            temp_processor = GoogleSpeechProcessor(self.credentials_path, self.project_id)
            
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
            self.logger.info("Cleaning up Google Cloud Speech integration...")
            
            for meeting_id in list(self.processors.keys()):
                await self.stop_meeting_transcription(meeting_id)
            
            self.processors.clear()
            
            self.logger.info("Google Cloud Speech integration cleanup completed")
        
        except Exception as e:
            self.logger.error(f"Error during Google Cloud Speech cleanup: {e}")


# Example usage and testing
async def test_google_speech_integration():
    """
    Test function for Google Cloud Speech integration.
    """
    from ..config.config_manager import ConfigManager
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize Google Cloud Speech integration
    google_manager = GoogleSpeechIntegrationManager(config_manager)
    
    if not await google_manager.initialize():
        print("Failed to initialize Google Cloud Speech integration")
        return
    
    # Set up transcription callback
    async def transcription_callback(result):
        print(f"Transcription: [{result['speaker']}] {result['text']} (confidence: {result['confidence']:.2f})")
    
    google_manager.set_global_transcription_callback(transcription_callback)
    
    # Start meeting transcription
    meeting_id = "test_meeting_001"
    success = await google_manager.start_meeting_transcription(meeting_id)
    
    if success:
        print("Started meeting transcription")
        
        # Simulate some processing time
        await asyncio.sleep(10)
        
        # Get transcript
        transcript = google_manager.get_meeting_transcript(meeting_id)
        print(f"Transcript has {len(transcript)} entries")
        
        # Stop transcription
        await google_manager.stop_meeting_transcription(meeting_id)
    
    # Cleanup
    await google_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(test_google_speech_integration())

