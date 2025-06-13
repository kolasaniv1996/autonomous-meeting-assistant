import unittest
import json
import tempfile
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, init_db

class TestAuthenticationAPI(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for each test
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        with app.app_context():
            init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

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

if __name__ == '__main__':
    # Run a simple test
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAuthenticationAPI)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✅ All authentication tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed")
        for test, error in result.failures:
            print(f"Failed: {test}")
            print(f"Error: {error}")
    
    # Test basic API endpoints manually
    print("\n🔧 Testing API endpoints manually...")
    
    # Test health endpoint (if exists)
    try:
        response = app.test_client().get('/api/health')
        if response.status_code == 404:
            print("⚠️  Health endpoint not implemented")
        else:
            print(f"✅ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    print("\n📊 Test Summary:")
    print(f"- Tests run: {result.testsRun}")
    print(f"- Failures: {len(result.failures)}")
    print(f"- Errors: {len(result.errors)}")
    print(f"- Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

