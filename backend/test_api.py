import unittest
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, init_db

class TestAuthenticationAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()

    def test_login_success(self):
        """Test successful login with admin credentials"""
        response = self.app.post('/api/auth/login',
                                data=json.dumps({
                                    'username': 'admin',
                                    'password': 'admin123'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'admin')

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.app.post('/api/auth/login',
                                data=json.dumps({
                                    'username': 'admin',
                                    'password': 'wrongpassword'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid credentials')

    def test_register_new_user(self):
        """Test user registration"""
        response = self.app.post('/api/auth/register',
                                data=json.dumps({
                                    'username': 'newuser',
                                    'email': 'newuser@example.com',
                                    'password': 'testpass123'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User created successfully')

    def test_register_duplicate_user(self):
        """Test registration with existing username"""
        # First registration
        self.app.post('/api/auth/register',
                     data=json.dumps({
                         'username': 'testuser',
                         'email': 'test@example.com',
                         'password': 'testpass123'
                     }),
                     content_type='application/json')
        
        # Duplicate registration
        response = self.app.post('/api/auth/register',
                                data=json.dumps({
                                    'username': 'testuser',
                                    'email': 'test2@example.com',
                                    'password': 'testpass123'
                                }),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User already exists')

    def test_protected_route_without_token(self):
        """Test accessing protected route without token"""
        response = self.app.get('/api/auth/profile')
        self.assertEqual(response.status_code, 401)

    def test_protected_route_with_token(self):
        """Test accessing protected route with valid token"""
        # Login first
        login_response = self.app.post('/api/auth/login',
                                      data=json.dumps({
                                          'username': 'admin',
                                          'password': 'admin123'
                                      }),
                                      content_type='application/json')
        
        login_data = json.loads(login_response.data)
        token = login_data['token']
        
        # Access protected route
        response = self.app.get('/api/auth/profile',
                               headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('user', data)

class TestConfigurationAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()
        
        # Login and get token
        login_response = self.app.post('/api/auth/login',
                                      data=json.dumps({
                                          'username': 'admin',
                                          'password': 'admin123'
                                      }),
                                      content_type='application/json')
        
        login_data = json.loads(login_response.data)
        self.token = login_data['token']
        self.headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

    def test_create_configuration(self):
        """Test creating a new configuration"""
        config_data = {
            'config_name': 'Test Config',
            'config_data': {
                'jira': {'url': 'https://test.atlassian.net', 'username': 'test', 'token': 'token123'},
                'github': {'username': 'testuser', 'token': 'ghp_test123'}
            },
            'is_active': True
        }
        
        response = self.app.post('/api/configurations',
                                data=json.dumps(config_data),
                                headers=self.headers)
        
        self.assertEqual(response.status_code, 201)

    def test_get_configurations(self):
        """Test retrieving configurations"""
        response = self.app.get('/api/configurations', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('configurations', data)

class TestAgentAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()
        
        # Login and get token
        login_response = self.app.post('/api/auth/login',
                                      data=json.dumps({
                                          'username': 'admin',
                                          'password': 'admin123'
                                      }),
                                      content_type='application/json')
        
        login_data = json.loads(login_response.data)
        self.token = login_data['token']
        self.headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

    def test_create_agent(self):
        """Test creating a new agent"""
        agent_data = {
            'name': 'Test Agent',
            'description': 'A test agent for meetings',
            'status': 'active',
            'config_data': {
                'jira_username': 'test.user',
                'github_username': 'testuser',
                'capabilities': ['Meeting Transcription', 'Action Item Extraction']
            }
        }
        
        response = self.app.post('/api/agents',
                                data=json.dumps(agent_data),
                                headers=self.headers)
        
        self.assertEqual(response.status_code, 201)

    def test_get_agents(self):
        """Test retrieving agents"""
        response = self.app.get('/api/agents', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('agents', data)

class TestMeetingAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()
        
        # Login and get token
        login_response = self.app.post('/api/auth/login',
                                      data=json.dumps({
                                          'username': 'admin',
                                          'password': 'admin123'
                                      }),
                                      content_type='application/json')
        
        login_data = json.loads(login_response.data)
        self.token = login_data['token']
        self.headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

    def test_create_meeting(self):
        """Test creating a new meeting"""
        meeting_data = {
            'title': 'Test Meeting',
            'description': 'A test meeting',
            'platform': 'Microsoft Teams',
            'meeting_url': 'https://teams.microsoft.com/test',
            'scheduled_start': '2024-01-01T10:00:00',
            'duration': 60,
            'status': 'scheduled'
        }
        
        response = self.app.post('/api/meetings',
                                data=json.dumps(meeting_data),
                                headers=self.headers)
        
        self.assertEqual(response.status_code, 201)

    def test_get_meetings(self):
        """Test retrieving meetings"""
        response = self.app.get('/api/meetings', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('meetings', data)

if __name__ == '__main__':
    unittest.main()

