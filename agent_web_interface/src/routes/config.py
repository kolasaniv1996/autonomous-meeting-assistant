"""
Configuration management API routes.
"""

from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.agent_models import Configuration
import json

config_bp = Blueprint('config', __name__)


@config_bp.route('/configurations', methods=['GET'])
def get_configurations():
    """Get all configurations."""
    try:
        configurations = Configuration.query.all()
        return jsonify({
            'success': True,
            'data': [config.to_dict() for config in configurations]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/configurations', methods=['POST'])
def create_configuration():
    """Create a new configuration."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Configuration name is required'
            }), 400
        
        if not data.get('config_data'):
            return jsonify({
                'success': False,
                'error': 'Configuration data is required'
            }), 400
        
        # Check if configuration name already exists
        existing = Configuration.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Configuration with this name already exists'
            }), 400
        
        # Create new configuration
        config = Configuration(
            name=data['name'],
            description=data.get('description'),
            config_data=data['config_data']
        )
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': config.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/configurations/<int:config_id>', methods=['GET'])
def get_configuration(config_id):
    """Get a specific configuration."""
    try:
        config = Configuration.query.get_or_404(config_id)
        return jsonify({
            'success': True,
            'data': config.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/configurations/<int:config_id>', methods=['PUT'])
def update_configuration(config_id):
    """Update a configuration."""
    try:
        config = Configuration.query.get_or_404(config_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            # Check if new name conflicts with existing
            existing = Configuration.query.filter(
                Configuration.name == data['name'],
                Configuration.id != config_id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Configuration with this name already exists'
                }), 400
            config.name = data['name']
        
        if 'description' in data:
            config.description = data['description']
        
        if 'config_data' in data:
            config.set_config_dict(data['config_data'])
        
        if 'is_active' in data:
            config.is_active = data['is_active']
            
            # If setting this config as active, deactivate others
            if data['is_active']:
                Configuration.query.filter(Configuration.id != config_id).update({'is_active': False})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': config.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/configurations/<int:config_id>', methods=['DELETE'])
def delete_configuration(config_id):
    """Delete a configuration."""
    try:
        config = Configuration.query.get_or_404(config_id)
        
        # Don't allow deletion of active configuration
        if config.is_active:
            return jsonify({
                'success': False,
                'error': 'Cannot delete active configuration'
            }), 400
        
        db.session.delete(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Configuration deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/configurations/active', methods=['GET'])
def get_active_configuration():
    """Get the currently active configuration."""
    try:
        config = Configuration.query.filter_by(is_active=True).first()
        if not config:
            return jsonify({
                'success': False,
                'error': 'No active configuration found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': config.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/configurations/validate', methods=['POST'])
def validate_configuration():
    """Validate a configuration structure."""
    try:
        data = request.get_json()
        config_data = data.get('config_data', {})
        
        # Validation rules
        errors = []
        warnings = []
        
        # Check required sections
        required_sections = ['api_credentials', 'employees']
        for section in required_sections:
            if section not in config_data:
                errors.append(f"Missing required section: {section}")
        
        # Validate API credentials
        if 'api_credentials' in config_data:
            api_creds = config_data['api_credentials']
            required_api_fields = ['jira_url', 'github_token']
            for field in required_api_fields:
                if not api_creds.get(field):
                    errors.append(f"Missing required API credential: {field}")
        
        # Validate employees
        if 'employees' in config_data:
            employees = config_data['employees']
            if not isinstance(employees, dict) or len(employees) == 0:
                errors.append("At least one employee must be configured")
            else:
                for emp_id, emp_data in employees.items():
                    if not emp_data.get('name'):
                        errors.append(f"Employee {emp_id} missing name")
                    if not emp_data.get('email'):
                        errors.append(f"Employee {emp_id} missing email")
        
        # Check optional sections and provide warnings
        optional_sections = ['meeting_platforms', 'speech_processing']
        for section in optional_sections:
            if section not in config_data:
                warnings.append(f"Optional section not configured: {section}")
        
        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/configurations/template', methods=['GET'])
def get_configuration_template():
    """Get a configuration template."""
    try:
        template = {
            "api_credentials": {
                "jira_url": "https://your-company.atlassian.net",
                "jira_username": "your-email@company.com",
                "jira_token": "your-jira-api-token",
                "github_token": "your-github-token",
                "confluence_url": "https://your-company.atlassian.net/wiki",
                "confluence_username": "your-email@company.com",
                "confluence_token": "your-confluence-token",
                "teams_app_id": "your-teams-app-id",
                "teams_app_password": "your-teams-app-password",
                "teams_tenant_id": "your-azure-tenant-id",
                "azure_speech_key": "your-azure-speech-key",
                "azure_speech_region": "eastus",
                "google_speech_credentials_path": "path/to/google_credentials.json",
                "google_cloud_project_id": "your-google-project-id",
                "openai_api_key": "your-openai-api-key"
            },
            "meeting_platforms": {
                "preferred_platform": "teams",
                "enabled_platforms": ["teams", "google_meet"],
                "teams": {
                    "auto_join_scheduled_meetings": True,
                    "enable_chat_responses": True,
                    "enable_meeting_summaries": True
                },
                "google_meet": {
                    "use_headless_browser": True,
                    "auto_disable_camera": True,
                    "auto_disable_microphone": True
                }
            },
            "speech_processing": {
                "preferred_provider": "azure",
                "enabled_providers": ["azure", "google_cloud", "whisper"],
                "enable_fallback": True,
                "real_time": {
                    "chunk_duration_seconds": 30,
                    "enable_partial_results": True,
                    "enable_speaker_diarization": True,
                    "max_speakers": 8
                }
            },
            "employees": {
                "example_user": {
                    "name": "Example User",
                    "employee_id": "example_user",
                    "email": "example@company.com",
                    "jira_username": "example.user",
                    "github_username": "example-user",
                    "projects": ["PROJECT-A", "PROJECT-B"],
                    "teams": ["backend-team"],
                    "role": "Software Engineer"
                }
            }
        }
        
        return jsonify({
            'success': True,
            'data': template
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

