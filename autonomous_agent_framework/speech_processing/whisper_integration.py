"""
OpenAI Whisper integration for autonomous agent framework.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import json
import io
import tempfile
import os

try:
    import openai
    from openai import OpenAI
except ImportError:
    # Mock for development without OpenAI SDK
    openai = None
    OpenAI = None

from ..agents.base_agent import MeetingMessage, MessageType
from ..config.config_manager import ConfigManager


class WhisperProcessor:
    """
    OpenAI Whisper processor for meeting transcription.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger("whisper_processor")
        
        # OpenAI client
        self.client: Optional[OpenAI] = None
        
        # Transcription state
        self.is_listening = False
        self.transcription_callback: Optional[Callable] = None
        self.current_speaker = "Unknown"
        
        # Audio buffering for real-time processing
        self.audio_buffer = io.BytesIO()
        self.buffer_duration = 30  # seconds
        self.sample_rate = 16000
        self.chunk_size = 1024
        
        # Transcription results
        self.final_results: List[Dict[str, Any]] = []
        
        # Real-time processing task
        self.processing_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> bool:
        """
        Initialize OpenAI Whisper service.
        """
        try:
            if not openai:
                self.logger.error("OpenAI SDK not available. Install with: pip install openai")
                return False
            
            # Initialize OpenAI client
            self.client = OpenAI(api_key=self.api_key)
            
            # Test the connection
            try:
                # Make a small test request to verify credentials
                models = self.client.models.list()
                self.logger.info("OpenAI Whisper service initialized successfully")
                return True
            except Exception as e:
                self.logger.error(f"Failed to authenticate with OpenAI: {e}")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI Whisper service: {e}")
            return False
    
    async def start_continuous_recognition(self, callback: Optional[Callable] = None) -> bool:
        """
        Start continuous speech recognition using chunked processing.
        """
        try:
            if not self.client:
                self.logger.error("Whisper client not initialized")
                return False
            
            if self.is_listening:
                self.logger.warning("Already listening")
                return True
            
            self.transcription_callback = callback
            self.is_listening = True
            
            # Start processing task
            self.processing_task = asyncio.create_task(self._continuous_processing_loop())
            
            self.logger.info("Started continuous speech recognition")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start continuous recognition: {e}")
            return False
    
    async def _continuous_processing_loop(self) -> None:
        """
        Continuous processing loop for real-time transcription.
        """
        try:
            while self.is_listening:
                # Wait for buffer to accumulate enough audio
                await asyncio.sleep(self.buffer_duration)
                
                if not self.is_listening:
                    break
                
                # Process current buffer
                await self._process_audio_buffer()
                
        except Exception as e:
            self.logger.error(f"Error in continuous processing loop: {e}")
            self.is_listening = False
    
    async def _process_audio_buffer(self) -> None:
        """
        Process the current audio buffer.
        """
        try:
            # Get current buffer content
            self.audio_buffer.seek(0)
            audio_data = self.audio_buffer.read()
            
            if len(audio_data) < 1024:  # Skip if buffer too small
                return
            
            # Clear buffer for next chunk
            self.audio_buffer = io.BytesIO()
            
            # Create temporary file for Whisper API
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Write audio data as WAV file
                self._write_wav_file(temp_file.name, audio_data)
                
                # Transcribe using Whisper
                result = await self._transcribe_file(temp_file.name)
                
                # Clean up temporary file
                os.unlink(temp_file.name)
                
                if result:
                    await self._handle_transcription_result(result)
        
        except Exception as e:
            self.logger.error(f"Error processing audio buffer: {e}")
    
    def _write_wav_file(self, filename: str, audio_data: bytes) -> None:
        """
        Write audio data to WAV file.
        """
        try:
            import wave
            
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data)
        
        except Exception as e:
            self.logger.error(f"Error writing WAV file: {e}")
    
    async def _transcribe_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio file using Whisper API.
        """
        try:
            with open(file_path, "rb") as audio_file:
                # Use Whisper API for transcription
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
                
                return {
                    'text': transcript.text,
                    'language': getattr(transcript, 'language', 'en'),
                    'duration': getattr(transcript, 'duration', 0),
                    'words': getattr(transcript, 'words', [])
                }
        
        except Exception as e:
            self.logger.error(f"Error transcribing file: {e}")
            return None
    
    async def _handle_transcription_result(self, result: Dict[str, Any]) -> None:
        """
        Handle transcription result.
        """
        try:
            if result and result.get('text'):
                transcript_result = {
                    'type': 'final',
                    'text': result['text'].strip(),
                    'speaker': self.current_speaker,
                    'timestamp': datetime.now(),
                    'confidence': 0.9,  # Whisper generally has high confidence
                    'duration': result.get('duration', 0),
                    'language': result.get('language', 'en')
                }
                
                self.final_results.append(transcript_result)
                self.logger.info(f"Transcribed: [{self.current_speaker}] {result['text'][:100]}...")
                
                # Call callback if set
                if self.transcription_callback:
                    await self.transcription_callback(transcript_result)
        
        except Exception as e:
            self.logger.error(f"Error handling transcription result: {e}")
    
    async def stop_continuous_recognition(self) -> None:
        """
        Stop continuous speech recognition.
        """
        try:
            self.is_listening = False
            
            if self.processing_task:
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
                self.processing_task = None
            
            # Process any remaining audio in buffer
            if self.audio_buffer.tell() > 0:
                await self._process_audio_buffer()
            
            self.logger.info("Stopped continuous speech recognition")
        
        except Exception as e:
            self.logger.error(f"Error stopping recognition: {e}")
    
    async def process_audio_chunk(self, audio_data: bytes) -> None:
        """
        Process a chunk of audio data.
        """
        try:
            if self.is_listening:
                # Add to buffer
                self.audio_buffer.write(audio_data)
        
        except Exception as e:
            self.logger.error(f"Error processing audio chunk: {e}")
    
    async def transcribe_audio_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Transcribe an audio file (batch processing).
        """
        try:
            if not self.client:
                self.logger.error("Whisper client not initialized")
                return []
            
            result = await self._transcribe_file(file_path)
            
            if result:
                return [{
                    'type': 'final',
                    'text': result['text'],
                    'speaker': 'Unknown',
                    'timestamp': datetime.now(),
                    'confidence': 0.9,
                    'duration': result.get('duration', 0),
                    'language': result.get('language', 'en')
                }]
            else:
                return []
        
        except Exception as e:
            self.logger.error(f"Error transcribing audio file: {e}")
            return []
    
    async def translate_audio_file(self, file_path: str, target_language: str = "en") -> List[Dict[str, Any]]:
        """
        Translate audio file to target language using Whisper.
        """
        try:
            if not self.client:
                self.logger.error("Whisper client not initialized")
                return []
            
            with open(file_path, "rb") as audio_file:
                # Use Whisper API for translation
                transcript = self.client.audio.translations.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )
                
                return [{
                    'type': 'final',
                    'text': transcript.text,
                    'speaker': 'Unknown',
                    'timestamp': datetime.now(),
                    'confidence': 0.9,
                    'duration': getattr(transcript, 'duration', 0),
                    'language': target_language,
                    'original_language': getattr(transcript, 'language', 'unknown')
                }]
        
        except Exception as e:
            self.logger.error(f"Error translating audio file: {e}")
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
        return self.final_results.copy()
    
    def clear_results(self) -> None:
        """
        Clear transcription results.
        """
        self.final_results.clear()
    
    async def cleanup(self) -> None:
        """
        Cleanup resources.
        """
        try:
            await self.stop_continuous_recognition()
            
            self.client = None
            self.audio_buffer = io.BytesIO()
            
            self.logger.info("Whisper processor cleanup completed")
        
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class WhisperIntegrationManager:
    """
    Manages OpenAI Whisper integration for the autonomous agent framework.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.logger = logging.getLogger("whisper_manager")
        
        # OpenAI configuration
        self.api_key = self.config.api_credentials.get('openai_api_key')
        
        # Speech processors for different meetings/contexts
        self.processors: Dict[str, WhisperProcessor] = {}
        
        # Global transcription callback
        self.global_transcription_callback: Optional[Callable] = None
    
    async def initialize(self) -> bool:
        """
        Initialize OpenAI Whisper integration.
        """
        try:
            if not self.api_key:
                self.logger.error("OpenAI API key not configured")
                return False
            
            self.logger.info("OpenAI Whisper integration initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI Whisper integration: {e}")
            return False
    
    async def create_processor(self, processor_id: str) -> Optional[WhisperProcessor]:
        """
        Create a new speech processor instance.
        """
        try:
            if processor_id in self.processors:
                self.logger.warning(f"Processor {processor_id} already exists")
                return self.processors[processor_id]
            
            processor = WhisperProcessor(self.api_key)
            
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
            temp_processor = WhisperProcessor(self.api_key)
            
            if await temp_processor.initialize():
                results = await temp_processor.transcribe_audio_file(file_path)
                await temp_processor.cleanup()
                return results
            else:
                return []
        
        except Exception as e:
            self.logger.error(f"Error transcribing audio file: {e}")
            return []
    
    async def translate_audio_file(self, file_path: str, target_language: str = "en") -> List[Dict[str, Any]]:
        """
        Translate an audio file using a temporary processor.
        """
        try:
            temp_processor = WhisperProcessor(self.api_key)
            
            if await temp_processor.initialize():
                results = await temp_processor.translate_audio_file(file_path, target_language)
                await temp_processor.cleanup()
                return results
            else:
                return []
        
        except Exception as e:
            self.logger.error(f"Error translating audio file: {e}")
            return []
    
    async def cleanup(self) -> None:
        """
        Cleanup all speech processors.
        """
        try:
            self.logger.info("Cleaning up OpenAI Whisper integration...")
            
            for meeting_id in list(self.processors.keys()):
                await self.stop_meeting_transcription(meeting_id)
            
            self.processors.clear()
            
            self.logger.info("OpenAI Whisper integration cleanup completed")
        
        except Exception as e:
            self.logger.error(f"Error during OpenAI Whisper cleanup: {e}")


# Example usage and testing
async def test_whisper_integration():
    """
    Test function for OpenAI Whisper integration.
    """
    from ..config.config_manager import ConfigManager
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize Whisper integration
    whisper_manager = WhisperIntegrationManager(config_manager)
    
    if not await whisper_manager.initialize():
        print("Failed to initialize OpenAI Whisper integration")
        return
    
    # Set up transcription callback
    async def transcription_callback(result):
        print(f"Transcription: [{result['speaker']}] {result['text']} (confidence: {result['confidence']:.2f})")
    
    whisper_manager.set_global_transcription_callback(transcription_callback)
    
    # Start meeting transcription
    meeting_id = "test_meeting_001"
    success = await whisper_manager.start_meeting_transcription(meeting_id)
    
    if success:
        print("Started meeting transcription")
        
        # Simulate some processing time
        await asyncio.sleep(30)  # Whisper processes in chunks
        
        # Get transcript
        transcript = whisper_manager.get_meeting_transcript(meeting_id)
        print(f"Transcript has {len(transcript)} entries")
        
        # Stop transcription
        await whisper_manager.stop_meeting_transcription(meeting_id)
    
    # Cleanup
    await whisper_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(test_whisper_integration())

