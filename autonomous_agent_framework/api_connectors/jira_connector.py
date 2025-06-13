"""
Jira API connector for extracting work items and context.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from jira import JIRA
import logging
from ..agents.base_agent import WorkItem, Priority, ContextExtractor


class JiraConnector(ContextExtractor):
    """Connector for Jira API to extract work items and context."""
    
    def __init__(self, jira_url: str, username: str, token: str):
        self.jira_url = jira_url
        self.username = username
        self.token = token
        self.client: Optional[JIRA] = None
        self.logger = logging.getLogger("jira_connector")
        
    async def connect(self) -> None:
        """Establish connection to Jira."""
        try:
            self.client = JIRA(
                server=self.jira_url,
                basic_auth=(self.username, self.token)
            )
            self.logger.info("Successfully connected to Jira")
        except Exception as e:
            self.logger.error(f"Failed to connect to Jira: {e}")
            raise
    
    def _map_priority(self, jira_priority: str) -> Priority:
        """Map Jira priority to internal Priority enum."""
        priority_mapping = {
            'Lowest': Priority.LOW,
            'Low': Priority.LOW,
            'Medium': Priority.MEDIUM,
            'High': Priority.HIGH,
            'Highest': Priority.CRITICAL,
            'Critical': Priority.CRITICAL,
            'Blocker': Priority.CRITICAL
        }
        return priority_mapping.get(jira_priority, Priority.MEDIUM)
    
    def _parse_jira_issue(self, issue) -> WorkItem:
        """Parse a Jira issue into a WorkItem."""
        return WorkItem(
            id=issue.key,
            title=issue.fields.summary,
            description=issue.fields.description or "",
            status=issue.fields.status.name,
            priority=self._map_priority(issue.fields.priority.name if issue.fields.priority else "Medium"),
            assignee=issue.fields.assignee.name if issue.fields.assignee else None,
            created_date=datetime.strptime(issue.fields.created[:19], "%Y-%m-%dT%H:%M:%S"),
            updated_date=datetime.strptime(issue.fields.updated[:19], "%Y-%m-%dT%H:%M:%S"),
            due_date=datetime.strptime(issue.fields.duedate, "%Y-%m-%d") if issue.fields.duedate else None,
            source="jira",
            url=f"{self.jira_url}/browse/{issue.key}",
            labels=issue.fields.labels or [],
            comments=[comment.body for comment in issue.fields.comment.comments[-5:]]  # Last 5 comments
        )
    
    async def extract_context(self, employee_id: str, days_back: int = 7) -> List[WorkItem]:
        """Extract work items for an employee from Jira."""
        if not self.client:
            await self.connect()
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # JQL query to get issues assigned to the employee
            jql = f"""
                assignee = "{employee_id}" AND 
                (updated >= "{start_date.strftime('%Y-%m-%d')}" OR 
                 status in ("In Progress", "To Do", "In Review", "Blocked"))
                ORDER BY updated DESC
            """
            
            issues = self.client.search_issues(jql, maxResults=50, expand='changelog')
            work_items = []
            
            for issue in issues:
                try:
                    work_item = self._parse_jira_issue(issue)
                    work_items.append(work_item)
                except Exception as e:
                    self.logger.warning(f"Failed to parse issue {issue.key}: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(work_items)} work items for {employee_id}")
            return work_items
            
        except Exception as e:
            self.logger.error(f"Failed to extract context for {employee_id}: {e}")
            return []
    
    async def get_recent_activity(self, employee_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get recent activity for an employee from Jira."""
        if not self.client:
            await self.connect()
        
        try:
            # Get issues with recent activity
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            jql = f"""
                assignee = "{employee_id}" AND 
                updated >= "{start_date.strftime('%Y-%m-%d')}"
                ORDER BY updated DESC
            """
            
            issues = self.client.search_issues(jql, maxResults=20, expand='changelog')
            activities = []
            
            for issue in issues:
                try:
                    # Get recent status changes
                    for history in issue.changelog.histories[-3:]:  # Last 3 changes
                        for item in history.items:
                            if item.field == 'status':
                                activities.append({
                                    'type': 'status_change',
                                    'issue_key': issue.key,
                                    'issue_title': issue.fields.summary,
                                    'from_status': item.fromString,
                                    'to_status': item.toString,
                                    'timestamp': datetime.strptime(history.created[:19], "%Y-%m-%dT%H:%M:%S"),
                                    'author': history.author.displayName
                                })
                    
                    # Get recent comments
                    for comment in issue.fields.comment.comments[-2:]:  # Last 2 comments
                        if comment.author.name == employee_id:
                            activities.append({
                                'type': 'comment',
                                'issue_key': issue.key,
                                'issue_title': issue.fields.summary,
                                'comment': comment.body[:200] + "..." if len(comment.body) > 200 else comment.body,
                                'timestamp': datetime.strptime(comment.created[:19], "%Y-%m-%dT%H:%M:%S"),
                                'author': comment.author.displayName
                            })
                            
                except Exception as e:
                    self.logger.warning(f"Failed to get activity for issue {issue.key}: {e}")
                    continue
            
            # Sort by timestamp
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            return activities[:10]  # Return top 10 recent activities
            
        except Exception as e:
            self.logger.error(f"Failed to get recent activity for {employee_id}: {e}")
            return []
    
    async def get_blockers(self, employee_id: str) -> List[WorkItem]:
        """Get blocked issues for an employee."""
        if not self.client:
            await self.connect()
        
        try:
            jql = f"""
                assignee = "{employee_id}" AND 
                status = "Blocked"
                ORDER BY priority DESC, updated DESC
            """
            
            issues = self.client.search_issues(jql, maxResults=10)
            blockers = []
            
            for issue in issues:
                try:
                    work_item = self._parse_jira_issue(issue)
                    blockers.append(work_item)
                except Exception as e:
                    self.logger.warning(f"Failed to parse blocked issue {issue.key}: {e}")
                    continue
            
            return blockers
            
        except Exception as e:
            self.logger.error(f"Failed to get blockers for {employee_id}: {e}")
            return []
    
    async def get_upcoming_deadlines(self, employee_id: str, days_ahead: int = 14) -> List[WorkItem]:
        """Get issues with upcoming deadlines for an employee."""
        if not self.client:
            await self.connect()
        
        try:
            end_date = datetime.now() + timedelta(days=days_ahead)
            
            jql = f"""
                assignee = "{employee_id}" AND 
                duedate <= "{end_date.strftime('%Y-%m-%d')}" AND
                status not in ("Done", "Closed", "Resolved")
                ORDER BY duedate ASC
            """
            
            issues = self.client.search_issues(jql, maxResults=10)
            upcoming = []
            
            for issue in issues:
                try:
                    work_item = self._parse_jira_issue(issue)
                    upcoming.append(work_item)
                except Exception as e:
                    self.logger.warning(f"Failed to parse upcoming issue {issue.key}: {e}")
                    continue
            
            return upcoming
            
        except Exception as e:
            self.logger.error(f"Failed to get upcoming deadlines for {employee_id}: {e}")
            return []
    
    async def create_ticket(self, project_key: str, summary: str, description: str, 
                          issue_type: str = "Task", assignee: Optional[str] = None,
                          priority: str = "Medium") -> Optional[str]:
        """Create a new Jira ticket."""
        if not self.client:
            await self.connect()
        
        try:
            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
                'priority': {'name': priority}
            }
            
            if assignee:
                issue_dict['assignee'] = {'name': assignee}
            
            new_issue = self.client.create_issue(fields=issue_dict)
            self.logger.info(f"Created Jira ticket: {new_issue.key}")
            return new_issue.key
            
        except Exception as e:
            self.logger.error(f"Failed to create Jira ticket: {e}")
            return None
    
    async def update_ticket(self, issue_key: str, **kwargs) -> bool:
        """Update an existing Jira ticket."""
        if not self.client:
            await self.connect()
        
        try:
            issue = self.client.issue(issue_key)
            issue.update(fields=kwargs)
            self.logger.info(f"Updated Jira ticket: {issue_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update Jira ticket {issue_key}: {e}")
            return False

