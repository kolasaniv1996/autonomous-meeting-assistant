"""
Configuration management for the Autonomous Agent Framework.
Handles employee mappings, API credentials, and system settings.
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pathlib import Path


class APICredentials(BaseModel):
    """API credentials for external services."""
    jira_url: Optional[str] = None
    jira_username: Optional[str] = None
    jira_token: Optional[str] = None
    github_token: Optional[str] = None
    confluence_url: Optional[str] = None
    confluence_username: Optional[str] = None
    confluence_token: Optional[str] = None
    slack_token: Optional[str] = None
    openai_api_key: Optional[str] = None


class EmployeeConfig(BaseModel):
    """Configuration for an individual employee."""
    name: str
    employee_id: str
    email: str
    jira_username: Optional[str] = None
    github_username: Optional[str] = None
    confluence_username: Optional[str] = None
    slack_user_id: Optional[str] = None
    projects: List[str] = Field(default_factory=list)
    teams: List[str] = Field(default_factory=list)
    role: Optional[str] = None
    manager: Optional[str] = None


class MeetingConfig(BaseModel):
    """Configuration for meeting behavior."""
    max_response_length: int = 200
    context_window_days: int = 7
    auto_join_meetings: bool = True
    create_summaries: bool = True
    create_action_items: bool = True
    update_jira_tickets: bool = True


class AgentConfig(BaseModel):
    """Main configuration for the agent framework."""
    api_credentials: APICredentials
    employees: Dict[str, EmployeeConfig]
    meeting_config: MeetingConfig
    llm_model: str = "gpt-3.5-turbo"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    log_level: str = "INFO"


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.config: Optional[AgentConfig] = None
        
    def _find_config_file(self) -> str:
        """Find configuration file in standard locations."""
        possible_paths = [
            "config/agent_config.yaml",
            "agent_config.yaml",
            os.path.expanduser("~/.agent_config.yaml"),
            "/etc/agent_config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # Return default path if none found
        return "config/agent_config.yaml"
    
    def load_config(self) -> AgentConfig:
        """Load configuration from file and environment variables."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Override with environment variables
        self._apply_env_overrides(config_data)
        
        self.config = AgentConfig(**config_data)
        return self.config
    
    def _apply_env_overrides(self, config_data: Dict[str, Any]) -> None:
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            'JIRA_URL': ['api_credentials', 'jira_url'],
            'JIRA_USERNAME': ['api_credentials', 'jira_username'],
            'JIRA_TOKEN': ['api_credentials', 'jira_token'],
            'GITHUB_TOKEN': ['api_credentials', 'github_token'],
            'CONFLUENCE_URL': ['api_credentials', 'confluence_url'],
            'CONFLUENCE_USERNAME': ['api_credentials', 'confluence_username'],
            'CONFLUENCE_TOKEN': ['api_credentials', 'confluence_token'],
            'SLACK_TOKEN': ['api_credentials', 'slack_token'],
            'OPENAI_API_KEY': ['api_credentials', 'openai_api_key'],
            'LLM_MODEL': ['llm_model'],
            'LOG_LEVEL': ['log_level']
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(config_data, config_path, value)
    
    def _set_nested_value(self, data: Dict, path: List[str], value: Any) -> None:
        """Set a nested value in a dictionary."""
        for key in path[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        data[path[-1]] = value
    
    def get_employee_config(self, employee_id: str) -> Optional[EmployeeConfig]:
        """Get configuration for a specific employee."""
        if not self.config:
            self.load_config()
        return self.config.employees.get(employee_id)
    
    def create_sample_config(self, output_path: str) -> None:
        """Create a sample configuration file."""
        sample_config = {
            'api_credentials': {
                'jira_url': 'https://your-company.atlassian.net',
                'jira_username': 'your-email@company.com',
                'jira_token': 'your-jira-api-token',
                'github_token': 'your-github-token',
                'confluence_url': 'https://your-company.atlassian.net/wiki',
                'confluence_username': 'your-email@company.com',
                'confluence_token': 'your-confluence-token',
                'slack_token': 'your-slack-bot-token',
                'openai_api_key': 'your-openai-api-key'
            },
            'employees': {
                'vivek': {
                    'name': 'Vivek Kumar',
                    'employee_id': 'vivek',
                    'email': 'vivek@company.com',
                    'jira_username': 'vivek.kumar',
                    'github_username': 'vivek-dev',
                    'confluence_username': 'vivek.kumar',
                    'slack_user_id': 'U1234567890',
                    'projects': ['PROJECT-A', 'PROJECT-B'],
                    'teams': ['backend-team', 'platform-team'],
                    'role': 'Senior Software Engineer',
                    'manager': 'sarah'
                },
                'sarah': {
                    'name': 'Sarah Johnson',
                    'employee_id': 'sarah',
                    'email': 'sarah@company.com',
                    'jira_username': 'sarah.johnson',
                    'github_username': 'sarah-manager',
                    'confluence_username': 'sarah.johnson',
                    'slack_user_id': 'U0987654321',
                    'projects': ['PROJECT-A', 'PROJECT-B', 'PROJECT-C'],
                    'teams': ['backend-team', 'platform-team', 'management'],
                    'role': 'Engineering Manager',
                    'manager': None
                }
            },
            'meeting_config': {
                'max_response_length': 200,
                'context_window_days': 7,
                'auto_join_meetings': True,
                'create_summaries': True,
                'create_action_items': True,
                'update_jira_tickets': True
            },
            'llm_model': 'gpt-3.5-turbo',
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'log_level': 'INFO'
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)


# Global config manager instance
config_manager = ConfigManager()

