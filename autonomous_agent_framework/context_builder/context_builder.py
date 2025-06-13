"""
Context builder module that aggregates information from multiple sources
to create comprehensive employee work context.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from ..agents.base_agent import WorkItem, ContextSummary, Priority
from ..api_connectors.jira_connector import JiraConnector
from ..api_connectors.github_connector import GitHubConnector
from ..api_connectors.confluence_connector import ConfluenceConnector


class ContextBuilder:
    """Builds comprehensive work context by aggregating data from multiple sources."""
    
    def __init__(self, jira_connector: Optional[JiraConnector] = None,
                 github_connector: Optional[GitHubConnector] = None,
                 confluence_connector: Optional[ConfluenceConnector] = None):
        self.jira_connector = jira_connector
        self.github_connector = github_connector
        self.confluence_connector = confluence_connector
        self.logger = logging.getLogger("context_builder")
        
    async def build_context(self, employee_id: str, days_back: int = 7) -> ContextSummary:
        """Build comprehensive context for an employee."""
        self.logger.info(f"Building context for {employee_id} (last {days_back} days)")
        
        # Collect work items from all sources
        all_work_items = []
        recent_commits = []
        
        # Jira context
        if self.jira_connector:
            try:
                jira_items = await self.jira_connector.extract_context(employee_id, days_back)
                all_work_items.extend(jira_items)
                self.logger.info(f"Added {len(jira_items)} items from Jira")
            except Exception as e:
                self.logger.error(f"Failed to get Jira context: {e}")
        
        # GitHub context
        if self.github_connector:
            try:
                github_items = await self.github_connector.extract_context(employee_id, days_back)
                all_work_items.extend(github_items)
                
                # Get recent commits separately
                github_activity = await self.github_connector.get_recent_activity(employee_id, days_back)
                recent_commits = [activity for activity in github_activity if activity['type'] == 'commit']
                
                self.logger.info(f"Added {len(github_items)} items and {len(recent_commits)} commits from GitHub")
            except Exception as e:
                self.logger.error(f"Failed to get GitHub context: {e}")
        
        # Confluence context
        if self.confluence_connector:
            try:
                confluence_items = await self.confluence_connector.extract_context(employee_id, days_back)
                all_work_items.extend(confluence_items)
                self.logger.info(f"Added {len(confluence_items)} items from Confluence")
            except Exception as e:
                self.logger.error(f"Failed to get Confluence context: {e}")
        
        # Analyze and categorize work items
        active_tasks = self._filter_active_tasks(all_work_items)
        blockers = self._filter_blockers(all_work_items)
        upcoming_deadlines = self._filter_upcoming_deadlines(all_work_items)
        key_achievements = await self._extract_key_achievements(employee_id, days_back)
        current_focus = self._determine_current_focus(active_tasks, recent_commits)
        availability_status = self._assess_availability(active_tasks, blockers)
        
        context_summary = ContextSummary(
            employee_id=employee_id,
            generated_at=datetime.now(),
            active_tasks=active_tasks,
            recent_commits=recent_commits,
            blockers=blockers,
            upcoming_deadlines=upcoming_deadlines,
            key_achievements=key_achievements,
            current_focus=current_focus,
            availability_status=availability_status
        )
        
        self.logger.info(f"Built context summary with {len(active_tasks)} active tasks, "
                        f"{len(blockers)} blockers, {len(upcoming_deadlines)} upcoming deadlines")
        
        return context_summary
    
    def _filter_active_tasks(self, work_items: List[WorkItem]) -> List[WorkItem]:
        """Filter work items to get currently active tasks."""
        active_statuses = {
            'In Progress', 'In Review', 'To Do', 'open', 'in_progress', 
            'review', 'todo', 'current', 'active'
        }
        
        active_tasks = []
        for item in work_items:
            if item.status.lower().replace(' ', '_') in {s.lower().replace(' ', '_') for s in active_statuses}:
                active_tasks.append(item)
        
        # Sort by priority and updated date
        active_tasks.sort(key=lambda x: (x.priority.value, x.updated_date), reverse=True)
        return active_tasks[:10]  # Limit to top 10 active tasks
    
    def _filter_blockers(self, work_items: List[WorkItem]) -> List[WorkItem]:
        """Filter work items to get blockers."""
        blocked_statuses = {'Blocked', 'blocked', 'impediment'}
        
        blockers = []
        for item in work_items:
            if (item.status.lower() in {s.lower() for s in blocked_statuses} or
                'blocked' in item.title.lower() or
                'blocker' in item.labels):
                blockers.append(item)
        
        return blockers
    
    def _filter_upcoming_deadlines(self, work_items: List[WorkItem], days_ahead: int = 14) -> List[WorkItem]:
        """Filter work items to get those with upcoming deadlines."""
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        upcoming = []
        for item in work_items:
            if (item.due_date and 
                item.due_date <= cutoff_date and 
                item.status.lower() not in {'done', 'closed', 'resolved', 'merged'}):
                upcoming.append(item)
        
        # Sort by due date
        upcoming.sort(key=lambda x: x.due_date or datetime.max)
        return upcoming
    
    async def _extract_key_achievements(self, employee_id: str, days_back: int) -> List[str]:
        """Extract key achievements from recent activity."""
        achievements = []
        
        # GitHub achievements
        if self.github_connector:
            try:
                github_activity = await self.github_connector.get_recent_activity(employee_id, days_back)
                
                # Count merged PRs
                merged_prs = [a for a in github_activity if a['type'] == 'pull_request' and a.get('merged')]
                if merged_prs:
                    achievements.append(f"Merged {len(merged_prs)} pull requests")
                
                # Count commits
                commits = [a for a in github_activity if a['type'] == 'commit']
                if commits:
                    achievements.append(f"Made {len(commits)} code commits")
                
                # Code reviews
                reviews = await self.github_connector.get_code_review_activity(employee_id, days_back)
                if reviews:
                    achievements.append(f"Completed {len(reviews)} code reviews")
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract GitHub achievements: {e}")
        
        # Jira achievements
        if self.jira_connector:
            try:
                jira_activity = await self.jira_connector.get_recent_activity(employee_id, days_back)
                
                # Count completed tasks
                completed = [a for a in jira_activity if a['type'] == 'status_change' and 
                           a.get('to_status', '').lower() in {'done', 'closed', 'resolved'}]
                if completed:
                    achievements.append(f"Completed {len(completed)} Jira tickets")
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract Jira achievements: {e}")
        
        # Confluence achievements
        if self.confluence_connector:
            try:
                confluence_activity = await self.confluence_connector.get_recent_activity(employee_id, days_back)
                
                # Count page updates
                page_updates = [a for a in confluence_activity if a['type'] == 'page_update']
                if page_updates:
                    achievements.append(f"Updated {len(page_updates)} documentation pages")
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract Confluence achievements: {e}")
        
        return achievements[:5]  # Limit to top 5 achievements
    
    def _determine_current_focus(self, active_tasks: List[WorkItem], recent_commits: List[Dict[str, Any]]) -> str:
        """Determine the employee's current focus based on active work."""
        if not active_tasks and not recent_commits:
            return "No active work detected"
        
        # Analyze active tasks
        if active_tasks:
            # Get the highest priority active task
            highest_priority_task = active_tasks[0]  # Already sorted by priority
            
            # Look for patterns in task titles/descriptions
            focus_keywords = {
                'bug': 'Bug fixing',
                'feature': 'Feature development',
                'refactor': 'Code refactoring',
                'test': 'Testing',
                'deploy': 'Deployment',
                'review': 'Code review',
                'documentation': 'Documentation',
                'security': 'Security improvements',
                'performance': 'Performance optimization'
            }
            
            task_text = (highest_priority_task.title + " " + highest_priority_task.description).lower()
            for keyword, focus in focus_keywords.items():
                if keyword in task_text:
                    return f"{focus} - {highest_priority_task.title[:50]}..."
            
            return f"Working on: {highest_priority_task.title[:50]}..."
        
        # Analyze recent commits if no active tasks
        if recent_commits:
            latest_commit = recent_commits[0]
            return f"Recent development: {latest_commit['message'][:50]}..."
        
        return "General development work"
    
    def _assess_availability(self, active_tasks: List[WorkItem], blockers: List[WorkItem]) -> str:
        """Assess the employee's availability based on workload and blockers."""
        if blockers:
            return f"Partially blocked ({len(blockers)} blockers)"
        
        if not active_tasks:
            return "Available for new work"
        
        high_priority_tasks = [task for task in active_tasks if task.priority in [Priority.HIGH, Priority.CRITICAL]]
        
        if len(active_tasks) > 8:
            return "Heavily loaded"
        elif len(active_tasks) > 5 or high_priority_tasks:
            return "Moderately busy"
        else:
            return "Available with some ongoing work"
    
    async def get_context_for_meeting(self, employee_id: str, meeting_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific context relevant for a meeting."""
        # Build general context
        context_summary = await self.build_context(employee_id)
        
        # Extract meeting-specific information
        meeting_type = meeting_context.get('meeting_type', 'general')
        agenda = meeting_context.get('agenda', '')
        
        relevant_context = {
            'employee_id': employee_id,
            'current_focus': context_summary.current_focus,
            'availability': context_summary.availability_status,
            'key_updates': []
        }
        
        # Add relevant updates based on meeting type
        if meeting_type == 'standup':
            relevant_context['key_updates'] = [
                f"Working on: {context_summary.current_focus}",
                f"Status: {context_summary.availability_status}"
            ]
            
            if context_summary.blockers:
                relevant_context['key_updates'].append(
                    f"Blockers: {len(context_summary.blockers)} items need attention"
                )
            
            if context_summary.key_achievements:
                relevant_context['key_updates'].extend(context_summary.key_achievements[:2])
        
        elif meeting_type == 'planning':
            relevant_context['upcoming_work'] = [task.title for task in context_summary.upcoming_deadlines[:3]]
            relevant_context['capacity'] = context_summary.availability_status
        
        elif meeting_type == 'review':
            relevant_context['achievements'] = context_summary.key_achievements
            relevant_context['completed_tasks'] = [
                task.title for task in context_summary.active_tasks 
                if task.status.lower() in {'done', 'closed', 'resolved'}
            ][:3]
        
        return relevant_context
    
    async def update_context_cache(self, employee_id: str, context: ContextSummary) -> None:
        """Update cached context for an employee (placeholder for future caching implementation)."""
        # This could be implemented with Redis, database, or file-based caching
        self.logger.info(f"Context cache updated for {employee_id}")
    
    async def get_cached_context(self, employee_id: str) -> Optional[ContextSummary]:
        """Get cached context for an employee (placeholder for future caching implementation)."""
        # This could be implemented with Redis, database, or file-based caching
        return None

