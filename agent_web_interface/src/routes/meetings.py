"""
Meeting management API routes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.user import db
from src.models.agent_models import Meeting, Agent
from datetime import datetime, timedelta
import json
import uuid

meeting_bp = Blueprint('meeting', __name__)


@meeting_bp.route('/meetings', methods=['GET'])
@jwt_required()
def get_meetings():
    """Get all meetings with optional filtering."""
    try:
        # Query parameters
        status = request.args.get('status')
        platform = request.args.get('platform')
        participant = request.args.get('participant')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', type=int)
        
        meetings_query = Meeting.query
        
        # Apply filters
        if status:
            meetings_query = meetings_query.filter(Meeting.status == status)
        
        if platform:
            meetings_query = meetings_query.filter(Meeting.platform == platform)
        
        if participant:
            meetings_query = meetings_query.filter(Meeting.participants.like(f'%{participant}%'))
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            meetings_query = meetings_query.filter(Meeting.scheduled_start >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            meetings_query = meetings_query.filter(Meeting.scheduled_start <= end_dt)
        
        # Order by scheduled start time (most recent first)
        meetings_query = meetings_query.order_by(Meeting.scheduled_start.desc())
        
        if limit:
            meetings_query = meetings_query.limit(limit)
        
        meetings = meetings_query.all()
        
        return jsonify({
            'success': True,
            'data': [meeting.to_dict() for meeting in meetings],
            'count': len(meetings)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meeting_bp.route('/meetings', methods=['POST'])
@jwt_required()
def create_meeting():
    """Create a new meeting."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'platform', 'scheduled_start', 'participants']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Validate participants exist
        participants = data['participants']
        for participant_id in participants:
            agent = Agent.query.filter_by(employee_id=participant_id).first()
            if not agent:
                return jsonify({
                    'success': False,
                    'error': f'Agent with employee_id {participant_id} not found'
                }), 400
        
        # Parse scheduled start time
        try:
            scheduled_start = datetime.fromisoformat(data['scheduled_start'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid scheduled_start format. Use ISO format.'
            }), 400
        
        # Generate unique meeting ID
        meeting_id = f"meeting_{uuid.uuid4().hex[:8]}"
        
        # Create meeting
        meeting = Meeting(
            meeting_id=meeting_id,
            title=data['title'],
            description=data.get('description'),
            platform=data['platform'],
            meeting_url=data.get('meeting_url'),
            participants=participants,
            scheduled_start=scheduled_start,
            duration_minutes=data.get('duration_minutes', 60),
            speech_provider=data.get('speech_provider', 'azure'),
            enable_transcription=data.get('enable_transcription', True)
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': meeting.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meeting_bp.route('/meetings/<int:meeting_id>', methods=['GET'])
@jwt_required()
def get_meeting(meeting_id):
    """Get a specific meeting."""
    try:
        meeting = Meeting.query.get_or_404(meeting_id)
        return jsonify({
            'success': True,
            'data': meeting.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meeting_bp.route('/meetings/<int:meeting_id>', methods=['PUT'])
@jwt_required()
def update_meeting(meeting_id):
    """Update a meeting."""
    try:
        meeting = Meeting.query.get_or_404(meeting_id)
        data = request.get_json()
        
        # Don't allow updates to active meetings
        if meeting.status == 'active':
            return jsonify({
                'success': False,
                'error': 'Cannot update active meeting'
            }), 400
        
        # Update fields
        updatable_fields = [
            'title', 'description', 'platform', 'meeting_url',
            'duration_minutes', 'speech_provider', 'enable_transcription'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(meeting, field, data[field])
        
        # Handle special fields
        if 'participants' in data:
            # Validate participants exist
            for participant_id in data['participants']:
                agent = Agent.query.filter_by(employee_id=participant_id).first()
                if not agent:
                    return jsonify({
                        'success': False,
                        'error': f'Agent with employee_id {participant_id} not found'
                    }), 400
            meeting.participants = json.dumps(data['participants'])
        
        if 'scheduled_start' in data:
            try:
                meeting.scheduled_start = datetime.fromisoformat(data['scheduled_start'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid scheduled_start format. Use ISO format.'
                }), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': meeting.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meeting_bp.route('/meetings/<int:meeting_id>', methods=['DELETE'])
@jwt_required()
def delete_meeting(meeting_id):
    """Delete a meeting."""
    try:
        meeting = Meeting.query.get_or_404(meeting_id)
        
        # Don't allow deletion of active meetings
        if meeting.status == 'active':
            return jsonify({
                'success': False,
                'error': 'Cannot delete active meeting'
            }), 400
        
        db.session.delete(meeting)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Meeting deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meeting_bp.route('/meetings/<int:meeting_id>/start', methods=['POST'])
@jwt_required()
def start_meeting(meeting_id):
    """Start a meeting."""
    try:
        meeting = Meeting.query.get_or_404(meeting_id)
        
        if meeting.status != 'scheduled':
            return jsonify({
                'success': False,
                'error': f'Cannot start meeting with status: {meeting.status}'
            }), 400
        
        meeting.status = 'active'
        meeting.actual_start = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': meeting.to_dict(),
            'message': 'Meeting started successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meeting_bp.route('/meetings/<int:meeting_id>/end', methods=['POST'])
@jwt_required()
def end_meeting(meeting_id):
    """End a meeting."""
    try:
        meeting = Meeting.query.get_or_404(meeting_id)
        data = request.get_json() or {}
        
        if meeting.status != 'active':
            return jsonify({
                'success': False,
                'error': f'Cannot end meeting with status: {meeting.status}'
            }), 400
        
        meeting.status = 'completed'
        meeting.actual_end = datetime.utcnow()
        
        # Calculate actual duration
        if meeting.actual_start:
            duration = meeting.actual_end - meeting.actual_start
            meeting.duration_minutes = int(duration.total_seconds() / 60)
        
        # Update summary and action items if provided
        if 'summary' in data:
            meeting.summary = data['summary']
        
        if 'action_items' in data:
            meeting.action_items = json.dumps(data['action_items'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': meeting.to_dict(),
            'message': 'Meeting ended successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meeting_bp.route('/meetings/<int:meeting_id>/transcript', methods=['GET'])
@jwt_required()
def get_meeting_transcript(meeting_id):
    """Get meeting transcript."""
    try:
        meeting = Meeting.query.get_or_404(meeting_id)
        
        return jsonify({
            'success': True,
            'data': {
                'meeting_id': meeting.meeting_id,
                'title': meeting.title,
                'transcript': meeting.get_transcript(),
                'transcript_length': len(meeting.get_transcript())
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meeting_bp.route('/meetings/<int:meeting_id>/transcript', methods=['POST'])
@jwt_required()
def update_meeting_transcript(meeting_id):
    """Update meeting transcript."""
    try:
        meeting = Meeting.query.get_or_404(meeting_id)
        data = request.get_json()
        
        if 'transcript_entry' in data:
            # Add single transcript entry
            current_transcript = meeting.get_transcript()
            current_transcript.append(data['transcript_entry'])
            meeting.transcript_data = json.dumps(current_transcript)
        elif 'transcript' in data:
            # Replace entire transcript
            meeting.transcript_data = json.dumps(data['transcript'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'transcript_length': len(meeting.get_transcript())
            },
            'message': 'Transcript updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meeting_bp.route('/meetings/stats', methods=['GET'])
@jwt_required()
def get_meeting_stats():
    """Get meeting statistics."""
    try:
        total_meetings = Meeting.query.count()
        active_meetings = Meeting.query.filter_by(status='active').count()
        completed_meetings = Meeting.query.filter_by(status='completed').count()
        scheduled_meetings = Meeting.query.filter_by(status='scheduled').count()
        
        # Platform distribution
        platform_stats = db.session.query(
            Meeting.platform,
            db.func.count(Meeting.id)
        ).group_by(Meeting.platform).all()
        
        platform_distribution = {platform: count for platform, count in platform_stats}
        
        # Recent meetings (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_meetings = Meeting.query.filter(
            Meeting.scheduled_start >= week_ago
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_meetings': total_meetings,
                'active_meetings': active_meetings,
                'completed_meetings': completed_meetings,
                'scheduled_meetings': scheduled_meetings,
                'platform_distribution': platform_distribution,
                'recent_meetings_7_days': recent_meetings
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meeting_bp.route('/meetings/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_meetings():
    """Get upcoming meetings."""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        upcoming_meetings = Meeting.query.filter(
            Meeting.status == 'scheduled',
            Meeting.scheduled_start > datetime.utcnow()
        ).order_by(Meeting.scheduled_start.asc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [meeting.to_dict() for meeting in upcoming_meetings],
            'count': len(upcoming_meetings)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

