"""
Configuration model for storing agent framework settings.
"""

from src.models.user import db
from datetime import datetime
import json


class Configuration(db.Model):
    """Model for storing configuration settings."""
    
    __tablename__ = 'configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    config_data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)
    
    def __init__(self, name, config_data, description=None):
        self.name = name
        self.description = description
        self.config_data = json.dumps(config_data) if isinstance(config_data, dict) else config_data
    
    def get_config_dict(self):
        """Return configuration as dictionary."""
        return json.loads(self.config_data)
    
    def set_config_dict(self, config_dict):
        """Set configuration from dictionary."""
        self.config_data = json.dumps(config_dict)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'config_data': self.get_config_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }


class Agent(db.Model):
    """Model for storing agent information."""
    
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(100))
    teams = db.Column(db.Text)  # JSON array of team names
    projects = db.Column(db.Text)  # JSON array of project names
    jira_username = db.Column(db.String(100))
    github_username = db.Column(db.String(100))
    confluence_username = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, employee_id, name, email, **kwargs):
        self.employee_id = employee_id
        self.name = name
        self.email = email
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key in ['teams', 'projects'] and isinstance(value, list):
                    setattr(self, key, json.dumps(value))
                else:
                    setattr(self, key, value)
    
    def get_teams(self):
        """Return teams as list."""
        return json.loads(self.teams) if self.teams else []
    
    def get_projects(self):
        """Return projects as list."""
        return json.loads(self.projects) if self.projects else []
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'teams': self.get_teams(),
            'projects': self.get_projects(),
            'jira_username': self.jira_username,
            'github_username': self.github_username,
            'confluence_username': self.confluence_username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Meeting(db.Model):
    """Model for storing meeting information."""
    
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.String(100), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    platform = db.Column(db.String(50), nullable=False)  # teams, google_meet
    meeting_url = db.Column(db.String(500))
    participants = db.Column(db.Text)  # JSON array of employee IDs
    scheduled_start = db.Column(db.DateTime, nullable=False)
    actual_start = db.Column(db.DateTime)
    actual_end = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, active, completed, cancelled
    speech_provider = db.Column(db.String(50))  # azure, google_cloud, whisper
    enable_transcription = db.Column(db.Boolean, default=True)
    transcript_data = db.Column(db.Text)  # JSON transcript
    summary = db.Column(db.Text)
    action_items = db.Column(db.Text)  # JSON array of action items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, meeting_id, title, platform, scheduled_start, **kwargs):
        self.meeting_id = meeting_id
        self.title = title
        self.platform = platform
        self.scheduled_start = scheduled_start
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key in ['participants', 'action_items'] and isinstance(value, list):
                    setattr(self, key, json.dumps(value))
                elif key == 'transcript_data' and isinstance(value, list):
                    setattr(self, key, json.dumps(value))
                else:
                    setattr(self, key, value)
    
    def get_participants(self):
        """Return participants as list."""
        return json.loads(self.participants) if self.participants else []
    
    def get_transcript(self):
        """Return transcript as list."""
        return json.loads(self.transcript_data) if self.transcript_data else []
    
    def get_action_items(self):
        """Return action items as list."""
        return json.loads(self.action_items) if self.action_items else []
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'meeting_id': self.meeting_id,
            'title': self.title,
            'description': self.description,
            'platform': self.platform,
            'meeting_url': self.meeting_url,
            'participants': self.get_participants(),
            'scheduled_start': self.scheduled_start.isoformat(),
            'actual_start': self.actual_start.isoformat() if self.actual_start else None,
            'actual_end': self.actual_end.isoformat() if self.actual_end else None,
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'speech_provider': self.speech_provider,
            'enable_transcription': self.enable_transcription,
            'transcript': self.get_transcript(),
            'summary': self.summary,
            'action_items': self.get_action_items(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

