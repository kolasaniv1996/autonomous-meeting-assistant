"""
Agent management API routes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.user import db
from src.models.agent_models import Agent
import json

agent_bp = Blueprint('agent', __name__)


@agent_bp.route('/agents', methods=['GET'])
@jwt_required()
def get_agents():
    """Get all agents."""
    try:
        agents = Agent.query.all()
        return jsonify({
            'success': True,
            'data': [agent.to_dict() for agent in agents]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/agents', methods=['POST'])
@jwt_required()
def create_agent():
    """Create a new agent."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_id', 'name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Check if employee_id already exists
        existing = Agent.query.filter_by(employee_id=data['employee_id']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Agent with this employee ID already exists'
            }), 400
        
        # Create new agent
        agent = Agent(
            employee_id=data['employee_id'],
            name=data['name'],
            email=data['email'],
            role=data.get('role'),
            teams=data.get('teams', []),
            projects=data.get('projects', []),
            jira_username=data.get('jira_username'),
            github_username=data.get('github_username'),
            confluence_username=data.get('confluence_username'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(agent)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': agent.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/agents/<int:agent_id>', methods=['GET'])
@jwt_required()
def get_agent(agent_id):
    """Get a specific agent."""
    try:
        agent = Agent.query.get_or_404(agent_id)
        return jsonify({
            'success': True,
            'data': agent.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/agents/<int:agent_id>', methods=['PUT'])
@jwt_required()
def update_agent(agent_id):
    """Update an agent."""
    try:
        agent = Agent.query.get_or_404(agent_id)
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'name', 'email', 'role', 'jira_username', 
            'github_username', 'confluence_username', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(agent, field, data[field])
        
        # Handle list fields
        if 'teams' in data:
            agent.teams = json.dumps(data['teams'])
        
        if 'projects' in data:
            agent.projects = json.dumps(data['projects'])
        
        # Check for employee_id conflicts if updating
        if 'employee_id' in data and data['employee_id'] != agent.employee_id:
            existing = Agent.query.filter(
                Agent.employee_id == data['employee_id'],
                Agent.id != agent_id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Agent with this employee ID already exists'
                }), 400
            agent.employee_id = data['employee_id']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': agent.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/agents/<int:agent_id>', methods=['DELETE'])
@jwt_required()
def delete_agent(agent_id):
    """Delete an agent."""
    try:
        agent = Agent.query.get_or_404(agent_id)
        
        db.session.delete(agent)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Agent deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/agents/<int:agent_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_agent_status(agent_id):
    """Toggle agent active status."""
    try:
        agent = Agent.query.get_or_404(agent_id)
        agent.is_active = not agent.is_active
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': agent.to_dict(),
            'message': f'Agent {"activated" if agent.is_active else "deactivated"} successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/agents/search', methods=['GET'])
@jwt_required()
def search_agents():
    """Search agents by various criteria."""
    try:
        query = request.args.get('q', '')
        team = request.args.get('team')
        project = request.args.get('project')
        is_active = request.args.get('is_active')
        
        agents_query = Agent.query
        
        # Text search
        if query:
            agents_query = agents_query.filter(
                db.or_(
                    Agent.name.ilike(f'%{query}%'),
                    Agent.email.ilike(f'%{query}%'),
                    Agent.employee_id.ilike(f'%{query}%'),
                    Agent.role.ilike(f'%{query}%')
                )
            )
        
        # Filter by team
        if team:
            agents_query = agents_query.filter(Agent.teams.like(f'%{team}%'))
        
        # Filter by project
        if project:
            agents_query = agents_query.filter(Agent.projects.like(f'%{project}%'))
        
        # Filter by active status
        if is_active is not None:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            agents_query = agents_query.filter(Agent.is_active == is_active_bool)
        
        agents = agents_query.all()
        
        return jsonify({
            'success': True,
            'data': [agent.to_dict() for agent in agents],
            'count': len(agents)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/agents/stats', methods=['GET'])
@jwt_required()
def get_agent_stats():
    """Get agent statistics."""
    try:
        total_agents = Agent.query.count()
        active_agents = Agent.query.filter_by(is_active=True).count()
        inactive_agents = total_agents - active_agents
        
        # Get team distribution
        agents = Agent.query.all()
        team_counts = {}
        project_counts = {}
        
        for agent in agents:
            teams = agent.get_teams()
            projects = agent.get_projects()
            
            for team in teams:
                team_counts[team] = team_counts.get(team, 0) + 1
            
            for project in projects:
                project_counts[project] = project_counts.get(project, 0) + 1
        
        return jsonify({
            'success': True,
            'data': {
                'total_agents': total_agents,
                'active_agents': active_agents,
                'inactive_agents': inactive_agents,
                'team_distribution': team_counts,
                'project_distribution': project_counts
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/agents/bulk', methods=['POST'])
@jwt_required()
def bulk_create_agents():
    """Create multiple agents from a list."""
    try:
        data = request.get_json()
        agents_data = data.get('agents', [])
        
        if not agents_data:
            return jsonify({
                'success': False,
                'error': 'No agents data provided'
            }), 400
        
        created_agents = []
        errors = []
        
        for i, agent_data in enumerate(agents_data):
            try:
                # Validate required fields
                required_fields = ['employee_id', 'name', 'email']
                for field in required_fields:
                    if not agent_data.get(field):
                        errors.append(f'Agent {i+1}: {field} is required')
                        continue
                
                # Check if employee_id already exists
                existing = Agent.query.filter_by(employee_id=agent_data['employee_id']).first()
                if existing:
                    errors.append(f'Agent {i+1}: Employee ID {agent_data["employee_id"]} already exists')
                    continue
                
                # Create agent
                agent = Agent(
                    employee_id=agent_data['employee_id'],
                    name=agent_data['name'],
                    email=agent_data['email'],
                    role=agent_data.get('role'),
                    teams=agent_data.get('teams', []),
                    projects=agent_data.get('projects', []),
                    jira_username=agent_data.get('jira_username'),
                    github_username=agent_data.get('github_username'),
                    confluence_username=agent_data.get('confluence_username'),
                    is_active=agent_data.get('is_active', True)
                )
                
                db.session.add(agent)
                created_agents.append(agent)
                
            except Exception as e:
                errors.append(f'Agent {i+1}: {str(e)}')
        
        if created_agents:
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'created_count': len(created_agents),
                'created_agents': [agent.to_dict() for agent in created_agents],
                'errors': errors
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

