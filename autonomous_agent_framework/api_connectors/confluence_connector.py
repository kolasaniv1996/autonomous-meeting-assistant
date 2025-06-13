"""
Confluence API connector for extracting documentation and knowledge context.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import logging
from ..agents.base_agent import WorkItem, Priority, ContextExtractor


class ConfluenceConnector(ContextExtractor):
    """Connector for Confluence API to extract documentation context."""
    
    def __init__(self, confluence_url: str, username: str, token: str):
        self.confluence_url = confluence_url.rstrip('/')
        self.username = username
        self.token = token
        self.session = requests.Session()
        self.session.auth = (username, token)
        self.logger = logging.getLogger("confluence_connector")
        
    async def connect(self) -> None:
        """Test connection to Confluence."""
        try:
            response = self.session.get(f"{self.confluence_url}/rest/api/user/current")
            response.raise_for_status()
            user_data = response.json()
            self.logger.info(f"Successfully connected to Confluence as {user_data.get('displayName', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Confluence: {e}")
            raise
    
    def _clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and extract text."""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:500] + "..." if len(text) > 500 else text
    
    def _parse_confluence_page(self, page_data: Dict[str, Any]) -> WorkItem:
        """Parse a Confluence page into a WorkItem."""
        content = self._clean_html_content(page_data.get('body', {}).get('storage', {}).get('value', ''))
        
        return WorkItem(
            id=page_data['id'],
            title=page_data['title'],
            description=content,
            status=page_data.get('status', 'current'),
            priority=Priority.MEDIUM,  # Confluence pages don't have priority
            assignee=page_data.get('version', {}).get('by', {}).get('username'),
            created_date=datetime.fromisoformat(page_data['version']['when'].replace('Z', '+00:00')),
            updated_date=datetime.fromisoformat(page_data['version']['when'].replace('Z', '+00:00')),
            due_date=None,
            source="confluence",
            url=f"{self.confluence_url}{page_data['_links']['webui']}",
            labels=page_data.get('metadata', {}).get('labels', {}).get('results', []),
            comments=[]
        )
    
    async def extract_context(self, employee_id: str, days_back: int = 7) -> List[WorkItem]:
        """Extract work items for an employee from Confluence."""
        work_items = []
        
        try:
            # Get pages created or modified by the employee
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Search for pages by author
            search_url = f"{self.confluence_url}/rest/api/content/search"
            params = {
                'cql': f'creator = "{employee_id}" OR contributor = "{employee_id}"',
                'limit': 50,
                'expand': 'body.storage,version,metadata.labels'
            }
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            search_results = response.json()
            
            for page in search_results.get('results', []):
                try:
                    # Check if page was updated within the time window
                    page_updated = datetime.fromisoformat(page['version']['when'].replace('Z', '+00:00'))
                    if page_updated >= start_date:
                        work_item = self._parse_confluence_page(page)
                        work_items.append(work_item)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to parse Confluence page {page.get('id', 'unknown')}: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(work_items)} work items from Confluence for {employee_id}")
            return work_items
            
        except Exception as e:
            self.logger.error(f"Failed to extract Confluence context for {employee_id}: {e}")
            return []
    
    async def get_recent_activity(self, employee_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get recent activity for an employee from Confluence."""
        activities = []
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get recent content updates
            search_url = f"{self.confluence_url}/rest/api/content/search"
            params = {
                'cql': f'(creator = "{employee_id}" OR contributor = "{employee_id}") AND lastModified >= "{start_date.strftime("%Y-%m-%d")}"',
                'limit': 20,
                'expand': 'version,space'
            }
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            search_results = response.json()
            
            for page in search_results.get('results', []):
                try:
                    activities.append({
                        'type': 'page_update',
                        'page_id': page['id'],
                        'title': page['title'],
                        'space': page.get('space', {}).get('name', 'Unknown'),
                        'timestamp': datetime.fromisoformat(page['version']['when'].replace('Z', '+00:00')),
                        'url': f"{self.confluence_url}{page['_links']['webui']}",
                        'version': page['version']['number']
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse activity for page {page.get('id', 'unknown')}: {e}")
                    continue
            
            # Get comments by the user
            comment_search_url = f"{self.confluence_url}/rest/api/content/search"
            comment_params = {
                'cql': f'type = comment AND creator = "{employee_id}" AND created >= "{start_date.strftime("%Y-%m-%d")}"',
                'limit': 10,
                'expand': 'container,version'
            }
            
            comment_response = self.session.get(comment_search_url, params=comment_params)
            if comment_response.status_code == 200:
                comment_results = comment_response.json()
                
                for comment in comment_results.get('results', []):
                    try:
                        activities.append({
                            'type': 'comment',
                            'comment_id': comment['id'],
                            'page_title': comment.get('container', {}).get('title', 'Unknown'),
                            'timestamp': datetime.fromisoformat(comment['version']['when'].replace('Z', '+00:00')),
                            'url': f"{self.confluence_url}{comment['_links']['webui']}"
                        })
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to parse comment {comment.get('id', 'unknown')}: {e}")
                        continue
            
            # Sort by timestamp
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            return activities[:15]
            
        except Exception as e:
            self.logger.error(f"Failed to get recent Confluence activity for {employee_id}: {e}")
            return []
    
    async def get_spaces_for_user(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get Confluence spaces where the user is active."""
        try:
            # Get spaces where user has contributed
            search_url = f"{self.confluence_url}/rest/api/content/search"
            params = {
                'cql': f'contributor = "{employee_id}"',
                'limit': 100,
                'expand': 'space'
            }
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            search_results = response.json()
            
            spaces = {}
            for page in search_results.get('results', []):
                space_data = page.get('space', {})
                if space_data:
                    space_key = space_data.get('key')
                    if space_key not in spaces:
                        spaces[space_key] = {
                            'key': space_key,
                            'name': space_data.get('name'),
                            'type': space_data.get('type'),
                            'pages_contributed': 0
                        }
                    spaces[space_key]['pages_contributed'] += 1
            
            return list(spaces.values())
            
        except Exception as e:
            self.logger.error(f"Failed to get spaces for {employee_id}: {e}")
            return []
    
    async def create_page(self, space_key: str, title: str, content: str, 
                         parent_id: Optional[str] = None) -> Optional[str]:
        """Create a new Confluence page."""
        try:
            page_data = {
                'type': 'page',
                'title': title,
                'space': {'key': space_key},
                'body': {
                    'storage': {
                        'value': content,
                        'representation': 'storage'
                    }
                }
            }
            
            if parent_id:
                page_data['ancestors'] = [{'id': parent_id}]
            
            response = self.session.post(
                f"{self.confluence_url}/rest/api/content",
                json=page_data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            created_page = response.json()
            page_id = created_page['id']
            self.logger.info(f"Created Confluence page: {page_id}")
            return page_id
            
        except Exception as e:
            self.logger.error(f"Failed to create Confluence page: {e}")
            return None
    
    async def update_page(self, page_id: str, title: str, content: str, version: int) -> bool:
        """Update an existing Confluence page."""
        try:
            page_data = {
                'version': {'number': version + 1},
                'title': title,
                'type': 'page',
                'body': {
                    'storage': {
                        'value': content,
                        'representation': 'storage'
                    }
                }
            }
            
            response = self.session.put(
                f"{self.confluence_url}/rest/api/content/{page_id}",
                json=page_data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            self.logger.info(f"Updated Confluence page: {page_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update Confluence page {page_id}: {e}")
            return False
    
    async def search_content(self, query: str, space_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for content in Confluence."""
        try:
            cql = f'text ~ "{query}"'
            if space_key:
                cql += f' AND space = "{space_key}"'
            
            search_url = f"{self.confluence_url}/rest/api/content/search"
            params = {
                'cql': cql,
                'limit': 20,
                'expand': 'body.view,version,space'
            }
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            search_results = response.json()
            
            results = []
            for page in search_results.get('results', []):
                results.append({
                    'id': page['id'],
                    'title': page['title'],
                    'space': page.get('space', {}).get('name', 'Unknown'),
                    'url': f"{self.confluence_url}{page['_links']['webui']}",
                    'excerpt': self._clean_html_content(page.get('body', {}).get('view', {}).get('value', ''))[:200]
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search Confluence content: {e}")
            return []

