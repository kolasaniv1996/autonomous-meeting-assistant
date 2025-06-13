"""
Conversation manager for coordinating multi-agent conversations in meetings.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
from enum import Enum
from ..agents.base_agent import MeetingMessage, MessageType, BaseAgent, MeetingContext


class ConversationState(Enum):
    """States of a conversation."""
    IDLE = "idle"
    ACTIVE = "active"
    WAITING_FOR_RESPONSE = "waiting_for_response"
    PAUSED = "paused"


class TurnTakingStrategy(Enum):
    """Strategies for managing turn-taking in conversations."""
    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    NATURAL_FLOW = "natural_flow"
    FACILITATOR_CONTROLLED = "facilitator_controlled"


class ConversationManager:
    """Manages conversation flow and turn-taking in meetings."""
    
    def __init__(self, strategy: TurnTakingStrategy = TurnTakingStrategy.NATURAL_FLOW):
        self.strategy = strategy
        self.state = ConversationState.IDLE
        self.current_speaker: Optional[str] = None
        self.speaking_queue: List[str] = []
        self.conversation_history: List[MeetingMessage] = []
        self.participants: List[str] = []
        self.facilitator: Optional[str] = None
        self.logger = logging.getLogger("conversation_manager")
        
        # Conversation flow control
        self.max_response_time = 30  # seconds
        self.max_consecutive_turns = 3
        self.turn_counts: Dict[str, int] = {}
        self.last_speaker_time: Dict[str, datetime] = {}
        
    def initialize_conversation(self, participants: List[str], 
                              facilitator: Optional[str] = None) -> None:
        """Initialize a new conversation."""
        self.participants = participants
        self.facilitator = facilitator or participants[0]
        self.speaking_queue = []
        self.turn_counts = {p: 0 for p in participants}
        self.last_speaker_time = {}
        self.state = ConversationState.IDLE
        
        self.logger.info(f"Initialized conversation with {len(participants)} participants")
    
    async def start_conversation(self, opening_message: Optional[str] = None) -> None:
        """Start the conversation."""
        self.state = ConversationState.ACTIVE
        
        if opening_message and self.facilitator:
            await self._add_message(self.facilitator, opening_message, MessageType.GENERAL)
        
        self.logger.info("Conversation started")
    
    async def add_message(self, speaker: str, content: str, 
                         message_type: MessageType = MessageType.GENERAL) -> None:
        """Add a message to the conversation."""
        if speaker not in self.participants:
            self.logger.warning(f"Speaker {speaker} is not a participant")
            return
        
        await self._add_message(speaker, content, message_type)
        await self._process_turn_taking(speaker)
    
    async def _add_message(self, speaker: str, content: str, 
                          message_type: MessageType) -> None:
        """Internal method to add a message."""
        message = MeetingMessage(
            speaker=speaker,
            content=content,
            message_type=message_type,
            timestamp=datetime.now(),
            confidence=1.0
        )
        
        self.conversation_history.append(message)
        self.current_speaker = speaker
        self.turn_counts[speaker] = self.turn_counts.get(speaker, 0) + 1
        self.last_speaker_time[speaker] = datetime.now()
        
        self.logger.debug(f"{speaker}: {content[:50]}...")
    
    async def _process_turn_taking(self, current_speaker: str) -> None:
        """Process turn-taking logic after a message."""
        if self.strategy == TurnTakingStrategy.ROUND_ROBIN:
            await self._handle_round_robin(current_speaker)
        elif self.strategy == TurnTakingStrategy.PRIORITY_BASED:
            await self._handle_priority_based(current_speaker)
        elif self.strategy == TurnTakingStrategy.NATURAL_FLOW:
            await self._handle_natural_flow(current_speaker)
        elif self.strategy == TurnTakingStrategy.FACILITATOR_CONTROLLED:
            await self._handle_facilitator_controlled(current_speaker)
    
    async def _handle_round_robin(self, current_speaker: str) -> None:
        """Handle round-robin turn-taking."""
        current_index = self.participants.index(current_speaker)
        next_index = (current_index + 1) % len(self.participants)
        next_speaker = self.participants[next_index]
        
        if next_speaker != current_speaker:
            self.speaking_queue.append(next_speaker)
    
    async def _handle_priority_based(self, current_speaker: str) -> None:
        """Handle priority-based turn-taking."""
        # Give priority to participants who haven't spoken much
        least_spoken = min(self.turn_counts.items(), key=lambda x: x[1])
        
        if least_spoken[0] != current_speaker and least_spoken[1] < self.turn_counts[current_speaker]:
            self.speaking_queue.append(least_spoken[0])
    
    async def _handle_natural_flow(self, current_speaker: str) -> None:
        """Handle natural conversation flow."""
        last_message = self.conversation_history[-1] if self.conversation_history else None
        
        if not last_message:
            return
        
        # Check if the message requires a response
        if self._message_requires_response(last_message):
            # Find the most appropriate responder
            responder = await self._find_appropriate_responder(last_message)
            if responder and responder != current_speaker:
                self.speaking_queue.append(responder)
        
        # Prevent one person from dominating the conversation
        if self.turn_counts[current_speaker] >= self.max_consecutive_turns:
            other_participants = [p for p in self.participants if p != current_speaker]
            if other_participants:
                # Give turn to someone who hasn't spoken recently
                least_recent = min(other_participants, 
                                 key=lambda p: self.last_speaker_time.get(p, datetime.min))
                self.speaking_queue.append(least_recent)
    
    async def _handle_facilitator_controlled(self, current_speaker: str) -> None:
        """Handle facilitator-controlled turn-taking."""
        # Only the facilitator can direct the conversation
        if current_speaker == self.facilitator:
            # Facilitator might direct a question to someone
            last_message = self.conversation_history[-1] if self.conversation_history else None
            if last_message and self._message_mentions_participant(last_message):
                mentioned = self._extract_mentioned_participant(last_message)
                if mentioned:
                    self.speaking_queue.append(mentioned)
    
    def _message_requires_response(self, message: MeetingMessage) -> bool:
        """Check if a message requires a response."""
        response_indicators = [
            '?', 'question', 'what do you think', 'thoughts', 'opinion',
            'agree', 'disagree', 'feedback', 'input', 'comment'
        ]
        
        content_lower = message.content.lower()
        return any(indicator in content_lower for indicator in response_indicators)
    
    async def _find_appropriate_responder(self, message: MeetingMessage) -> Optional[str]:
        """Find the most appropriate person to respond to a message."""
        content_lower = message.content.lower()
        
        # Check if a specific person is mentioned
        for participant in self.participants:
            if participant.lower() in content_lower:
                return participant
        
        # Check message type
        if message.message_type == MessageType.QUESTION:
            # Find someone who hasn't spoken recently
            recent_speakers = [p for p in self.participants 
                             if self.last_speaker_time.get(p, datetime.min) > 
                             datetime.now() - timedelta(minutes=2)]
            
            non_recent_speakers = [p for p in self.participants 
                                 if p not in recent_speakers and p != message.speaker]
            
            if non_recent_speakers:
                return non_recent_speakers[0]
        
        return None
    
    def _message_mentions_participant(self, message: MeetingMessage) -> bool:
        """Check if a message mentions a specific participant."""
        content_lower = message.content.lower()
        return any(participant.lower() in content_lower for participant in self.participants)
    
    def _extract_mentioned_participant(self, message: MeetingMessage) -> Optional[str]:
        """Extract the mentioned participant from a message."""
        content_lower = message.content.lower()
        for participant in self.participants:
            if participant.lower() in content_lower:
                return participant
        return None
    
    def get_next_speaker(self) -> Optional[str]:
        """Get the next speaker in the queue."""
        if self.speaking_queue:
            return self.speaking_queue.pop(0)
        return None
    
    def add_speaker_to_queue(self, speaker: str) -> None:
        """Add a speaker to the speaking queue."""
        if speaker in self.participants and speaker not in self.speaking_queue:
            self.speaking_queue.append(speaker)
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about the conversation."""
        total_messages = len(self.conversation_history)
        
        stats = {
            'total_messages': total_messages,
            'participants': len(self.participants),
            'turn_distribution': self.turn_counts.copy(),
            'message_types': {},
            'conversation_duration': None,
            'average_response_time': None
        }
        
        # Calculate message type distribution
        for message in self.conversation_history:
            msg_type = message.message_type.value
            stats['message_types'][msg_type] = stats['message_types'].get(msg_type, 0) + 1
        
        # Calculate conversation duration
        if self.conversation_history:
            start_time = self.conversation_history[0].timestamp
            end_time = self.conversation_history[-1].timestamp
            stats['conversation_duration'] = (end_time - start_time).total_seconds()
        
        # Calculate average response time
        response_times = []
        for i in range(1, len(self.conversation_history)):
            prev_msg = self.conversation_history[i-1]
            curr_msg = self.conversation_history[i]
            if prev_msg.speaker != curr_msg.speaker:
                response_time = (curr_msg.timestamp - prev_msg.timestamp).total_seconds()
                response_times.append(response_time)
        
        if response_times:
            stats['average_response_time'] = sum(response_times) / len(response_times)
        
        return stats
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation."""
        stats = self.get_conversation_stats()
        
        # Find most active participant
        most_active = max(self.turn_counts.items(), key=lambda x: x[1]) if self.turn_counts else None
        
        # Find key topics (simple keyword extraction)
        all_content = ' '.join([msg.content for msg in self.conversation_history])
        words = all_content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Only consider longer words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'statistics': stats,
            'most_active_participant': most_active[0] if most_active else None,
            'top_keywords': [kw[0] for kw in top_keywords],
            'conversation_flow': self._analyze_conversation_flow(),
            'engagement_level': self._calculate_engagement_level()
        }
    
    def _analyze_conversation_flow(self) -> Dict[str, Any]:
        """Analyze the flow of the conversation."""
        if len(self.conversation_history) < 2:
            return {'flow_type': 'insufficient_data'}
        
        # Analyze speaker transitions
        transitions = []
        for i in range(1, len(self.conversation_history)):
            prev_speaker = self.conversation_history[i-1].speaker
            curr_speaker = self.conversation_history[i].speaker
            if prev_speaker != curr_speaker:
                transitions.append((prev_speaker, curr_speaker))
        
        # Calculate flow metrics
        unique_transitions = len(set(transitions))
        total_transitions = len(transitions)
        
        flow_analysis = {
            'total_transitions': total_transitions,
            'unique_transitions': unique_transitions,
            'transition_diversity': unique_transitions / total_transitions if total_transitions > 0 else 0,
            'dominant_speakers': [p for p, count in self.turn_counts.items() 
                                if count > len(self.conversation_history) * 0.3]
        }
        
        return flow_analysis
    
    def _calculate_engagement_level(self) -> str:
        """Calculate the overall engagement level of the conversation."""
        if not self.conversation_history:
            return "no_activity"
        
        # Factors for engagement:
        # 1. Participation distribution
        # 2. Response times
        # 3. Message types diversity
        # 4. Conversation length
        
        participation_score = len([p for p in self.turn_counts.values() if p > 0]) / len(self.participants)
        
        message_types = set(msg.message_type for msg in self.conversation_history)
        type_diversity_score = len(message_types) / len(MessageType)
        
        avg_msg_length = sum(len(msg.content) for msg in self.conversation_history) / len(self.conversation_history)
        length_score = min(avg_msg_length / 100, 1.0)  # Normalize to 0-1
        
        overall_score = (participation_score + type_diversity_score + length_score) / 3
        
        if overall_score > 0.7:
            return "high"
        elif overall_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def pause_conversation(self) -> None:
        """Pause the conversation."""
        self.state = ConversationState.PAUSED
        self.logger.info("Conversation paused")
    
    def resume_conversation(self) -> None:
        """Resume the conversation."""
        self.state = ConversationState.ACTIVE
        self.logger.info("Conversation resumed")
    
    def end_conversation(self) -> Dict[str, Any]:
        """End the conversation and return summary."""
        self.state = ConversationState.IDLE
        summary = self.get_conversation_summary()
        self.logger.info("Conversation ended")
        return summary

