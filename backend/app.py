from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET', 'your-super-secret-jwt-key')

# Database initialization
def init_db():
    conn = sqlite3.connect('meeting_assistant.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # User sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            token VARCHAR(255) UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User configurations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            config_name VARCHAR(100) NOT NULL,
            config_data TEXT,
            is_active BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Agents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            name VARCHAR(100) NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'inactive',
            config_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Meetings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            title VARCHAR(200) NOT NULL,
            description TEXT,
            platform VARCHAR(50),
            meeting_url TEXT,
            scheduled_start TIMESTAMP,
            duration INTEGER DEFAULT 60,
            status VARCHAR(20) DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            setting_key VARCHAR(100) NOT NULL,
            setting_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', admin_password, 'admin'))
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('meeting_assistant.db')
    conn.row_factory = sqlite3.Row
    return conn

def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', 
                   (data['username'], data['email']))
    if cursor.fetchone():
        conn.close()
        return jsonify({'message': 'User already exists'}), 409
    
    # Create new user
    password_hash = generate_password_hash(data['password'])
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', (data['username'], data['email'], password_hash, data.get('role', 'user')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing credentials'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', 
                   (data['username'],))
    user = cursor.fetchone()
    
    if not user or not check_password_hash(user['password_hash'], data['password']):
        conn.close()
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Update last login
    cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', 
                   (user['id'],))
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200

@app.route('/api/auth/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, role, created_at, last_login FROM users WHERE id = ?', 
                   (current_user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'user': dict(user)
    }), 200

# Configuration routes
@app.route('/api/configurations', methods=['GET'])
@token_required
def get_configurations(current_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, config_name, config_data, is_active, created_at 
        FROM user_configurations 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (current_user_id,))
    
    configurations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'configurations': configurations}), 200

@app.route('/api/configurations', methods=['POST'])
@token_required
def create_configuration(current_user_id):
    data = request.get_json()
    
    if not data or not data.get('config_name') or not data.get('config_data'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Deactivate other configurations if this one is set as active
    if data.get('is_active'):
        cursor.execute('UPDATE user_configurations SET is_active = 0 WHERE user_id = ?', 
                       (current_user_id,))
    
    cursor.execute('''
        INSERT INTO user_configurations (user_id, config_name, config_data, is_active)
        VALUES (?, ?, ?, ?)
    ''', (current_user_id, data['config_name'], str(data['config_data']), 
          data.get('is_active', False)))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Configuration created successfully'}), 201

@app.route('/api/configurations/<int:config_id>', methods=['PUT'])
@token_required
def update_configuration(current_user_id, config_id):
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if configuration belongs to user
    cursor.execute('SELECT id FROM user_configurations WHERE id = ? AND user_id = ?', 
                   (config_id, current_user_id))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Configuration not found'}), 404
    
    # Deactivate other configurations if this one is set as active
    if data.get('is_active'):
        cursor.execute('UPDATE user_configurations SET is_active = 0 WHERE user_id = ? AND id != ?', 
                       (current_user_id, config_id))
    
    cursor.execute('''
        UPDATE user_configurations 
        SET config_name = ?, config_data = ?, is_active = ?
        WHERE id = ? AND user_id = ?
    ''', (data.get('config_name'), str(data.get('config_data')), 
          data.get('is_active', False), config_id, current_user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Configuration updated successfully'}), 200

@app.route('/api/configurations/<int:config_id>', methods=['DELETE'])
@token_required
def delete_configuration(current_user_id, config_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM user_configurations WHERE id = ? AND user_id = ?', 
                   (config_id, current_user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'message': 'Configuration not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Configuration deleted successfully'}), 200

# Agent routes
@app.route('/api/agents', methods=['GET'])
@token_required
def get_agents(current_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, description, status, config_data, created_at, updated_at
        FROM agents 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (current_user_id,))
    
    agents = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'agents': agents}), 200

@app.route('/api/agents', methods=['POST'])
@token_required
def create_agent(current_user_id):
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Agent name is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO agents (user_id, name, description, status, config_data)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_user_id, data['name'], data.get('description', ''), 
          data.get('status', 'inactive'), str(data.get('config_data', {}))))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Agent created successfully'}), 201

@app.route('/api/agents/<int:agent_id>', methods=['PUT'])
@token_required
def update_agent(current_user_id, agent_id):
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if agent belongs to user
    cursor.execute('SELECT id FROM agents WHERE id = ? AND user_id = ?', 
                   (agent_id, current_user_id))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Agent not found'}), 404
    
    cursor.execute('''
        UPDATE agents 
        SET name = ?, description = ?, status = ?, config_data = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    ''', (data.get('name'), data.get('description'), data.get('status'), 
          str(data.get('config_data', {})), agent_id, current_user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Agent updated successfully'}), 200

@app.route('/api/agents/<int:agent_id>', methods=['DELETE'])
@token_required
def delete_agent(current_user_id, agent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM agents WHERE id = ? AND user_id = ?', 
                   (agent_id, current_user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'message': 'Agent not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Agent deleted successfully'}), 200

# Meeting routes
@app.route('/api/meetings', methods=['GET'])
@token_required
def get_meetings(current_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, description, platform, meeting_url, scheduled_start, 
               duration, status, created_at
        FROM meetings 
        WHERE user_id = ? 
        ORDER BY scheduled_start DESC
    ''', (current_user_id,))
    
    meetings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'meetings': meetings}), 200

@app.route('/api/meetings', methods=['POST'])
@token_required
def create_meeting(current_user_id):
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('scheduled_start'):
        return jsonify({'message': 'Title and scheduled start time are required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO meetings (user_id, title, description, platform, meeting_url, 
                            scheduled_start, duration, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (current_user_id, data['title'], data.get('description', ''), 
          data.get('platform', ''), data.get('meeting_url', ''),
          data['scheduled_start'], data.get('duration', 60), 
          data.get('status', 'scheduled')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Meeting created successfully'}), 201

@app.route('/api/meetings/<int:meeting_id>', methods=['PUT'])
@token_required
def update_meeting(current_user_id, meeting_id):
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if meeting belongs to user
    cursor.execute('SELECT id FROM meetings WHERE id = ? AND user_id = ?', 
                   (meeting_id, current_user_id))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Meeting not found'}), 404
    
    cursor.execute('''
        UPDATE meetings 
        SET title = ?, description = ?, platform = ?, meeting_url = ?,
            scheduled_start = ?, duration = ?, status = ?
        WHERE id = ? AND user_id = ?
    ''', (data.get('title'), data.get('description'), data.get('platform'),
          data.get('meeting_url'), data.get('scheduled_start'), 
          data.get('duration'), data.get('status'), meeting_id, current_user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Meeting updated successfully'}), 200

@app.route('/api/meetings/<int:meeting_id>', methods=['DELETE'])
@token_required
def delete_meeting(current_user_id, meeting_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM meetings WHERE id = ? AND user_id = ?', 
                   (meeting_id, current_user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'message': 'Meeting not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Meeting deleted successfully'}), 200

# Settings routes
@app.route('/api/settings', methods=['GET'])
@token_required
def get_settings(current_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT setting_key, setting_value, created_at, updated_at
        FROM settings 
        WHERE user_id = ? 
        ORDER BY setting_key
    ''', (current_user_id,))
    
    settings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'settings': settings}), 200

@app.route('/api/settings', methods=['POST'])
@token_required
def update_settings(current_user_id):
    data = request.get_json()
    
    if not data or not isinstance(data, dict):
        return jsonify({'message': 'Invalid settings data'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for key, value in data.items():
        cursor.execute('''
            INSERT OR REPLACE INTO settings (user_id, setting_key, setting_value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (current_user_id, key, str(value)))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Settings updated successfully'}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True)

