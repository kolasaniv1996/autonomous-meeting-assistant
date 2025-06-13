"""
GitHub API connector for extracting code-related context and activity.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from github import Github
import logging
from ..agents.base_agent import WorkItem, Priority, ContextExtractor


class GitHubConnector(ContextExtractor):
    """Connector for GitHub API to extract code-related context."""
    
    def __init__(self, token: str):
        self.token = token
        self.client: Optional[Github] = None
        self.logger = logging.getLogger("github_connector")
        
    async def connect(self) -> None:
        """Establish connection to GitHub."""
        try:
            self.client = Github(self.token)
            # Test the connection
            user = self.client.get_user()
            self.logger.info(f"Successfully connected to GitHub as {user.login}")
        except Exception as e:
            self.logger.error(f"Failed to connect to GitHub: {e}")
            raise
    
    def _map_priority_from_labels(self, labels: List[str]) -> Priority:
        """Map GitHub labels to internal Priority enum."""
        priority_labels = {
            'priority: critical': Priority.CRITICAL,
            'priority: high': Priority.HIGH,
            'priority: medium': Priority.MEDIUM,
            'priority: low': Priority.LOW,
            'critical': Priority.CRITICAL,
            'high': Priority.HIGH,
            'medium': Priority.MEDIUM,
            'low': Priority.LOW,
            'urgent': Priority.CRITICAL,
            'bug': Priority.HIGH
        }
        
        for label in labels:
            label_lower = label.lower()
            if label_lower in priority_labels:
                return priority_labels[label_lower]
        
        return Priority.MEDIUM
    
    def _parse_github_issue(self, issue, repo_name: str) -> WorkItem:
        """Parse a GitHub issue into a WorkItem."""
        labels = [label.name for label in issue.labels]
        
        return WorkItem(
            id=f"{repo_name}#{issue.number}",
            title=issue.title,
            description=issue.body or "",
            status=issue.state,
            priority=self._map_priority_from_labels(labels),
            assignee=issue.assignee.login if issue.assignee else None,
            created_date=issue.created_at,
            updated_date=issue.updated_at,
            due_date=None,  # GitHub issues don't have due dates by default
            source="github",
            url=issue.html_url,
            labels=labels,
            comments=[comment.body for comment in issue.get_comments()[-5:]]  # Last 5 comments
        )
    
    def _parse_github_pr(self, pr, repo_name: str) -> WorkItem:
        """Parse a GitHub pull request into a WorkItem."""
        labels = [label.name for label in pr.labels]
        
        return WorkItem(
            id=f"{repo_name}#PR{pr.number}",
            title=f"PR: {pr.title}",
            description=pr.body or "",
            status=pr.state,
            priority=self._map_priority_from_labels(labels),
            assignee=pr.assignee.login if pr.assignee else None,
            created_date=pr.created_at,
            updated_date=pr.updated_at,
            due_date=None,
            source="github",
            url=pr.html_url,
            labels=labels + ["pull-request"],
            comments=[comment.body for comment in pr.get_issue_comments()[-3:]]  # Last 3 comments
        )
    
    async def extract_context(self, employee_id: str, days_back: int = 7) -> List[WorkItem]:
        """Extract work items for an employee from GitHub."""
        if not self.client:
            await self.connect()
        
        work_items = []
        
        try:
            # Get user's repositories
            user = self.client.get_user(employee_id)
            repos = list(user.get_repos(type='all', sort='updated'))[:20]  # Limit to 20 most recent repos
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            for repo in repos:
                try:
                    # Get assigned issues
                    issues = repo.get_issues(
                        assignee=employee_id,
                        state='all',
                        since=start_date
                    )
                    
                    for issue in issues:
                        if not issue.pull_request:  # Regular issue
                            work_item = self._parse_github_issue(issue, repo.name)
                            work_items.append(work_item)
                    
                    # Get pull requests
                    prs = repo.get_pulls(
                        state='all',
                        sort='updated',
                        direction='desc'
                    )
                    
                    for pr in prs:
                        if pr.user.login == employee_id and pr.updated_at >= start_date:
                            work_item = self._parse_github_pr(pr, repo.name)
                            work_items.append(work_item)
                            
                except Exception as e:
                    self.logger.warning(f"Failed to process repo {repo.name}: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(work_items)} work items from GitHub for {employee_id}")
            return work_items
            
        except Exception as e:
            self.logger.error(f"Failed to extract GitHub context for {employee_id}: {e}")
            return []
    
    async def get_recent_activity(self, employee_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get recent activity for an employee from GitHub."""
        if not self.client:
            await self.connect()
        
        activities = []
        
        try:
            user = self.client.get_user(employee_id)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get recent commits
            repos = list(user.get_repos(type='all', sort='updated'))[:10]  # Limit to 10 repos
            
            for repo in repos:
                try:
                    commits = repo.get_commits(
                        author=employee_id,
                        since=start_date
                    )
                    
                    for commit in commits:
                        activities.append({
                            'type': 'commit',
                            'repo': repo.name,
                            'message': commit.commit.message.split('\n')[0][:100],  # First line, max 100 chars
                            'sha': commit.sha[:8],
                            'timestamp': commit.commit.author.date,
                            'url': commit.html_url,
                            'files_changed': len(commit.files) if commit.files else 0
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Failed to get commits for repo {repo.name}: {e}")
                    continue
            
            # Get recent issue/PR activities
            for repo in repos[:5]:  # Limit to 5 repos for issue activity
                try:
                    # Recent issues
                    issues = repo.get_issues(
                        creator=employee_id,
                        state='all',
                        since=start_date
                    )
                    
                    for issue in issues:
                        if not issue.pull_request:
                            activities.append({
                                'type': 'issue_created',
                                'repo': repo.name,
                                'title': issue.title[:100],
                                'number': issue.number,
                                'timestamp': issue.created_at,
                                'url': issue.html_url,
                                'state': issue.state
                            })
                    
                    # Recent PRs
                    prs = repo.get_pulls(
                        state='all',
                        sort='updated',
                        direction='desc'
                    )
                    
                    for pr in prs:
                        if pr.user.login == employee_id and pr.updated_at >= start_date:
                            activities.append({
                                'type': 'pull_request',
                                'repo': repo.name,
                                'title': pr.title[:100],
                                'number': pr.number,
                                'timestamp': pr.updated_at,
                                'url': pr.html_url,
                                'state': pr.state,
                                'merged': pr.merged
                            })
                            
                except Exception as e:
                    self.logger.warning(f"Failed to get issue/PR activity for repo {repo.name}: {e}")
                    continue
            
            # Sort by timestamp
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            return activities[:15]  # Return top 15 recent activities
            
        except Exception as e:
            self.logger.error(f"Failed to get recent GitHub activity for {employee_id}: {e}")
            return []
    
    async def get_repository_stats(self, employee_id: str, repo_names: List[str] = None) -> Dict[str, Any]:
        """Get repository statistics for an employee."""
        if not self.client:
            await self.connect()
        
        try:
            user = self.client.get_user(employee_id)
            
            if repo_names:
                repos = [self.client.get_repo(name) for name in repo_names]
            else:
                repos = list(user.get_repos(type='all', sort='updated'))[:10]
            
            stats = {
                'total_repos': len(repos),
                'languages': {},
                'total_commits_last_week': 0,
                'active_repos': []
            }
            
            week_ago = datetime.now() - timedelta(days=7)
            
            for repo in repos:
                try:
                    # Get language stats
                    languages = repo.get_languages()
                    for lang, bytes_count in languages.items():
                        stats['languages'][lang] = stats['languages'].get(lang, 0) + bytes_count
                    
                    # Get recent commits count
                    commits = list(repo.get_commits(author=employee_id, since=week_ago))
                    commit_count = len(commits)
                    stats['total_commits_last_week'] += commit_count
                    
                    if commit_count > 0:
                        stats['active_repos'].append({
                            'name': repo.name,
                            'commits': commit_count,
                            'last_commit': commits[0].commit.author.date if commits else None
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Failed to get stats for repo {repo.name}: {e}")
                    continue
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get repository stats for {employee_id}: {e}")
            return {}
    
    async def get_code_review_activity(self, employee_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get code review activity for an employee."""
        if not self.client:
            await self.connect()
        
        reviews = []
        
        try:
            user = self.client.get_user(employee_id)
            repos = list(user.get_repos(type='all', sort='updated'))[:10]
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            for repo in repos:
                try:
                    prs = repo.get_pulls(state='all', sort='updated', direction='desc')
                    
                    for pr in prs:
                        if pr.updated_at < start_date:
                            break
                            
                        pr_reviews = pr.get_reviews()
                        for review in pr_reviews:
                            if review.user.login == employee_id and review.submitted_at >= start_date:
                                reviews.append({
                                    'type': 'code_review',
                                    'repo': repo.name,
                                    'pr_title': pr.title[:100],
                                    'pr_number': pr.number,
                                    'review_state': review.state,
                                    'timestamp': review.submitted_at,
                                    'url': pr.html_url
                                })
                                
                except Exception as e:
                    self.logger.warning(f"Failed to get review activity for repo {repo.name}: {e}")
                    continue
            
            reviews.sort(key=lambda x: x['timestamp'], reverse=True)
            return reviews[:10]
            
        except Exception as e:
            self.logger.error(f"Failed to get code review activity for {employee_id}: {e}")
            return []

