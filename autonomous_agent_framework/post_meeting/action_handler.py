"""
Post-meeting action handler for processing meeting outcomes and creating follow-up actions.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import re
from ..agents.base_agent import (
    MeetingMessage, MeetingContext, MeetingSummary, 
    ActionItem, Priority, PostMeetingHandler
)
from ..api_connectors.jira_connector import JiraConnector
from ..api_connectors.confluence_connector import ConfluenceConnector


class PostMeetingActionHandler(PostMeetingHandler):
    """Handles post-meeting actions like creating summaries and action items."""
    
    def __init__(self, jira_connector: Optional[JiraConnector] = None,
                 confluence_connector: Optional[ConfluenceConnector] = None):
        self.jira_connector = jira_connector
        self.confluence_connector = confluence_connector
        self.logger = logging.getLogger("post_meeting_handler")
        
    async def create_summary(self, meeting_messages: List[MeetingMessage], 
                           meeting_context: MeetingContext) -> MeetingSummary:
        """Create a comprehensive meeting summary."""
        self.logger.info(f"Creating summary for meeting: {meeting_context.meeting_id}")
        
        # Extract key information from messages
        key_points = self._extract_key_points(meeting_messages)
        decisions_made = self._extract_decisions(meeting_messages)
        blockers_discussed = self._extract_blockers(meeting_messages)
        action_items = await self.extract_action_items(meeting_messages, meeting_context)
        
        # Determine next meeting if mentioned
        next_meeting = self._extract_next_meeting_date(meeting_messages)
        
        summary = MeetingSummary(
            meeting_id=meeting_context.meeting_id,
            title=meeting_context.title,
            participants=meeting_context.participants,
            start_time=meeting_context.start_time,
            end_time=datetime.now(),
            key_points=key_points,
            decisions_made=decisions_made,
            action_items=action_items,
            blockers_discussed=blockers_discussed,
            next_meeting=next_meeting
        )
        
        self.logger.info(f"Summary created with {len(key_points)} key points, "
                        f"{len(decisions_made)} decisions, {len(action_items)} action items")
        
        return summary
    
    def _extract_key_points(self, messages: List[MeetingMessage]) -> List[str]:
        """Extract key points from meeting messages."""
        key_points = []
        
        # Keywords that indicate important information
        importance_indicators = [
            'important', 'critical', 'key', 'main', 'primary', 'focus',
            'priority', 'urgent', 'deadline', 'milestone', 'goal',
            'completed', 'finished', 'delivered', 'released'
        ]
        
        for message in messages:
            if message.speaker == "system":
                continue
                
            content_lower = message.content.lower()
            
            # Check for importance indicators
            if any(indicator in content_lower for indicator in importance_indicators):
                # Clean and add the message
                clean_content = self._clean_message_content(message.content)
                if len(clean_content) > 20:  # Filter out very short messages
                    key_points.append(f"{message.speaker}: {clean_content}")
            
            # Add status updates
            if message.message_type.value == "status_update":
                clean_content = self._clean_message_content(message.content)
                key_points.append(f"Status - {message.speaker}: {clean_content}")
        
        return key_points[:10]  # Limit to top 10 key points
    
    def _extract_decisions(self, messages: List[MeetingMessage]) -> List[str]:
        """Extract decisions made during the meeting."""
        decisions = []
        
        decision_indicators = [
            'decided', 'decision', 'agree', 'agreed', 'consensus',
            'will do', 'going to', 'plan to', 'choose', 'selected'
        ]
        
        for message in messages:
            if message.speaker == "system":
                continue
                
            content_lower = message.content.lower()
            
            if any(indicator in content_lower for indicator in decision_indicators):
                clean_content = self._clean_message_content(message.content)
                decisions.append(f"Decision: {clean_content}")
        
        return decisions[:5]  # Limit to top 5 decisions
    
    def _extract_blockers(self, messages: List[MeetingMessage]) -> List[str]:
        """Extract blockers discussed in the meeting."""
        blockers = []
        
        blocker_indicators = [
            'blocker', 'blocked', 'impediment', 'stuck', 'waiting for',
            'dependency', 'issue', 'problem', 'challenge'
        ]
        
        for message in messages:
            if (message.speaker == "system" or 
                message.message_type.value != "blocker"):
                continue
                
            content_lower = message.content.lower()
            
            if any(indicator in content_lower for indicator in blocker_indicators):
                clean_content = self._clean_message_content(message.content)
                blockers.append(f"{message.speaker}: {clean_content}")
        
        return blockers
    
    async def extract_action_items(self, meeting_messages: List[MeetingMessage],
                                 meeting_context: MeetingContext) -> List[ActionItem]:
        """Extract action items from meeting messages."""
        action_items = []
        
        action_indicators = [
            'will do', 'going to', 'need to', 'should', 'must',
            'action item', 'todo', 'follow up', 'next step',
            'assign', 'responsible', 'owner', 'by when', 'deadline'
        ]
        
        for message in messages:
            if message.speaker == "system":
                continue
                
            content_lower = message.content.lower()
            
            if any(indicator in content_lower for indicator in action_indicators):
                action_item = self._parse_action_item(message, meeting_context)
                if action_item:
                    action_items.append(action_item)
        
        return action_items
    
    def _parse_action_item(self, message: MeetingMessage, 
                          meeting_context: MeetingContext) -> Optional[ActionItem]:
        """Parse a single action item from a message."""
        content = message.content
        
        # Extract assignee (default to speaker)
        assignee = message.speaker
        
        # Look for explicit assignment patterns
        assignment_patterns = [
            r'(\w+) will (\w+)',
            r'assign to (\w+)',
            r'(\w+) should (\w+)',
            r'(\w+) needs to (\w+)'
        ]
        
        for pattern in assignment_patterns:
            match = re.search(pattern, content.lower())
            if match:
                potential_assignee = match.group(1)
                if potential_assignee in meeting_context.participants:
                    assignee = potential_assignee
                break
        
        # Extract due date
        due_date = self._extract_due_date(content)
        
        # Determine priority
        priority = self._determine_action_priority(content)
        
        # Clean description
        description = self._clean_message_content(content)
        
        if len(description) < 10:  # Skip very short descriptions
            return None
        
        action_item = ActionItem(
            id=f"{meeting_context.meeting_id}_{len(meeting_context.participants)}_{message.timestamp.timestamp()}",
            description=description,
            assignee=assignee,
            due_date=due_date,
            priority=priority,
            meeting_id=meeting_context.meeting_id,
            created_at=message.timestamp,
            status="open"
        )
        
        return action_item
    
    def _extract_due_date(self, content: str) -> Optional[datetime]:
        """Extract due date from content."""
        content_lower = content.lower()
        
        # Look for explicit date patterns
        date_patterns = [
            r'by (\w+day)',  # by friday, by monday
            r'by (\d{1,2}/\d{1,2})',  # by 12/25
            r'by (\w+ \d{1,2})',  # by december 25
            r'in (\d+) days?',  # in 3 days
            r'next (\w+)',  # next week
            r'end of (\w+)'  # end of week
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content_lower)
            if match:
                date_str = match.group(1)
                return self._parse_relative_date(date_str)
        
        # Default to one week from now if no specific date found
        if any(word in content_lower for word in ['urgent', 'asap', 'immediately']):
            return datetime.now() + timedelta(days=1)
        elif any(word in content_lower for word in ['soon', 'quickly']):
            return datetime.now() + timedelta(days=3)
        else:
            return datetime.now() + timedelta(days=7)
    
    def _parse_relative_date(self, date_str: str) -> datetime:
        """Parse relative date strings."""
        now = datetime.now()
        
        if 'monday' in date_str:
            days_ahead = 0 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return now + timedelta(days=days_ahead)
        elif 'friday' in date_str:
            days_ahead = 4 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return now + timedelta(days=days_ahead)
        elif 'week' in date_str:
            return now + timedelta(days=7)
        elif 'days' in date_str:
            # Extract number of days
            match = re.search(r'(\d+)', date_str)
            if match:
                days = int(match.group(1))
                return now + timedelta(days=days)
        
        return now + timedelta(days=7)  # Default to one week
    
    def _determine_action_priority(self, content: str) -> Priority:
        """Determine priority of an action item."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['urgent', 'critical', 'asap', 'immediately']):
            return Priority.CRITICAL
        elif any(word in content_lower for word in ['important', 'high', 'priority']):
            return Priority.HIGH
        elif any(word in content_lower for word in ['low', 'nice to have', 'when possible']):
            return Priority.LOW
        else:
            return Priority.MEDIUM
    
    def _extract_next_meeting_date(self, messages: List[MeetingMessage]) -> Optional[datetime]:
        """Extract next meeting date if mentioned."""
        for message in messages:
            content_lower = message.content.lower()
            
            if 'next meeting' in content_lower or 'follow up' in content_lower:
                # Look for date patterns
                date_match = re.search(r'next (\w+)', content_lower)
                if date_match:
                    return self._parse_relative_date(date_match.group(1))
        
        return None
    
    def _clean_message_content(self, content: str) -> str:
        """Clean and normalize message content."""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove common filler words at the beginning
        filler_patterns = [
            r'^(um|uh|so|well|okay|alright),?\s*',
            r'^(i think|i believe|i guess),?\s*'
        ]
        
        for pattern in filler_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    async def create_jira_tickets(self, action_items: List[ActionItem]) -> List[str]:
        """Create Jira tickets for action items."""
        if not self.jira_connector:
            self.logger.warning("No Jira connector available for ticket creation")
            return []
        
        created_tickets = []
        
        for action_item in action_items:
            try:
                # Determine project key (this would need to be configured)
                project_key = "MEET"  # Default project for meeting action items
                
                # Create ticket
                ticket_key = await self.jira_connector.create_ticket(
                    project_key=project_key,
                    summary=f"Action Item: {action_item.description[:100]}",
                    description=f"Action item from meeting {action_item.meeting_id}\n\n"
                               f"Description: {action_item.description}\n"
                               f"Created: {action_item.created_at}\n"
                               f"Due Date: {action_item.due_date}",
                    issue_type="Task",
                    assignee=action_item.assignee,
                    priority=action_item.priority.value.title()
                )
                
                if ticket_key:
                    created_tickets.append(ticket_key)
                    self.logger.info(f"Created Jira ticket {ticket_key} for action item")
                
            except Exception as e:
                self.logger.error(f"Failed to create Jira ticket for action item: {e}")
        
        return created_tickets
    
    async def update_confluence(self, summary: MeetingSummary) -> str:
        """Update Confluence with meeting summary."""
        if not self.confluence_connector:
            self.logger.warning("No Confluence connector available for documentation")
            return ""
        
        try:
            # Generate Confluence content
            content = self._generate_confluence_content(summary)
            
            # Create page title
            page_title = f"Meeting Summary - {summary.title} - {summary.start_time.strftime('%Y-%m-%d')}"
            
            # Create the page (assuming a default space)
            space_key = "MEETINGS"  # This would need to be configured
            
            page_id = await self.confluence_connector.create_page(
                space_key=space_key,
                title=page_title,
                content=content
            )
            
            if page_id:
                self.logger.info(f"Created Confluence page {page_id} for meeting summary")
                return page_id
            
        except Exception as e:
            self.logger.error(f"Failed to create Confluence page: {e}")
        
        return ""
    
    def _generate_confluence_content(self, summary: MeetingSummary) -> str:
        """Generate Confluence-formatted content for meeting summary."""
        content = f"""
<h1>Meeting Summary: {summary.title}</h1>

<h2>Meeting Details</h2>
<ul>
<li><strong>Date:</strong> {summary.start_time.strftime('%Y-%m-%d %H:%M')}</li>
<li><strong>Duration:</strong> {(summary.end_time - summary.start_time).total_seconds() / 60:.0f} minutes</li>
<li><strong>Participants:</strong> {', '.join(summary.participants)}</li>
</ul>

<h2>Key Points</h2>
<ul>
"""
        
        for point in summary.key_points:
            content += f"<li>{point}</li>\n"
        
        content += "</ul>\n"
        
        if summary.decisions_made:
            content += "\n<h2>Decisions Made</h2>\n<ul>\n"
            for decision in summary.decisions_made:
                content += f"<li>{decision}</li>\n"
            content += "</ul>\n"
        
        if summary.action_items:
            content += "\n<h2>Action Items</h2>\n<table>\n"
            content += "<tr><th>Description</th><th>Assignee</th><th>Due Date</th><th>Priority</th></tr>\n"
            
            for item in summary.action_items:
                due_date_str = item.due_date.strftime('%Y-%m-%d') if item.due_date else 'TBD'
                content += f"<tr><td>{item.description}</td><td>{item.assignee}</td><td>{due_date_str}</td><td>{item.priority.value}</td></tr>\n"
            
            content += "</table>\n"
        
        if summary.blockers_discussed:
            content += "\n<h2>Blockers Discussed</h2>\n<ul>\n"
            for blocker in summary.blockers_discussed:
                content += f"<li>{blocker}</li>\n"
            content += "</ul>\n"
        
        if summary.next_meeting:
            content += f"\n<h2>Next Meeting</h2>\n<p>Scheduled for: {summary.next_meeting.strftime('%Y-%m-%d %H:%M')}</p>\n"
        
        return content
    
    async def process_meeting_completion(self, meeting_messages: List[MeetingMessage],
                                       meeting_context: MeetingContext) -> Dict[str, Any]:
        """Process complete meeting and perform all post-meeting actions."""
        self.logger.info(f"Processing completion of meeting: {meeting_context.meeting_id}")
        
        results = {
            'meeting_id': meeting_context.meeting_id,
            'summary': None,
            'jira_tickets': [],
            'confluence_page': '',
            'errors': []
        }
        
        try:
            # Create meeting summary
            summary = await self.create_summary(meeting_messages, meeting_context)
            results['summary'] = summary
            
            # Create Jira tickets for action items
            if summary.action_items:
                try:
                    jira_tickets = await self.create_jira_tickets(summary.action_items)
                    results['jira_tickets'] = jira_tickets
                except Exception as e:
                    results['errors'].append(f"Jira ticket creation failed: {e}")
            
            # Update Confluence
            try:
                confluence_page = await self.update_confluence(summary)
                results['confluence_page'] = confluence_page
            except Exception as e:
                results['errors'].append(f"Confluence update failed: {e}")
            
            self.logger.info(f"Meeting processing completed. Created {len(results['jira_tickets'])} tickets, "
                           f"Confluence page: {results['confluence_page']}")
            
        except Exception as e:
            self.logger.error(f"Failed to process meeting completion: {e}")
            results['errors'].append(f"Summary creation failed: {e}")
        
        return results

