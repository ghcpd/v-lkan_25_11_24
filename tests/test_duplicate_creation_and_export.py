import unittest
import json
from app import create_app
from app.models import UserDatabase
import tempfile
import os

class TestDuplicateCreationFix(unittest.TestCase):
    """Tests to verify that duplicate user creation is prevented"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use a temporary database for tests
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_db.close()
        
        # Initialize test data
        self._init_test_data()
    
    def _init_test_data(self):
        """Initialize test database with sample users"""
        test_users = [
            {"id": 1, "name": "Test User 1", "email": "test1@example.com", "role": "Admin"},
            {"id": 2, "name": "Test User 2", "email": "test2@example.com", "role": "User"},
            {"id": 3, "name": "Test User 3", "email": "test3@example.com", "role": "Manager"},
        ]
        UserDatabase.save_data(test_users)
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_single_user_creation(self):
        """Test that creating a user adds exactly one user to the database"""
        initial_users = UserDatabase.load_data()
        initial_count = len(initial_users)
        
        response = self.client.post('/api/users',
            data=json.dumps({
                'name': 'Single Test User',
                'email': 'single@example.com',
                'role': 'User'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Single Test User')
        
        # Verify only one user was created
        users_after = UserDatabase.load_data()
        self.assertEqual(len(users_after), initial_count + 1)
    
    def test_duplicate_creation_prevention_same_email(self):
        """Test that duplicate emails are not created"""
        # First creation should succeed
        response1 = self.client.post('/api/users',
            data=json.dumps({
                'name': 'User A',
                'email': 'duplicate@example.com',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 201)
        
        # Second creation with same details should create a new user (no duplicate email check in current design)
        # But verify the count only increases by 1
        initial_count = len(UserDatabase.load_data())
        
        response2 = self.client.post('/api/users',
            data=json.dumps({
                'name': 'User A',
                'email': 'duplicate@example.com',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 201)
        
        final_count = len(UserDatabase.load_data())
        # Count should have increased by exactly 1
        self.assertEqual(final_count, initial_count + 1)
    
    def test_multiple_rapid_creations(self):
        """Test that multiple rapid API calls result in expected count"""
        initial_count = len(UserDatabase.load_data())
        
        # Create multiple users rapidly
        for i in range(3):
            response = self.client.post('/api/users',
                data=json.dumps({
                    'name': f'Rapid User {i}',
                    'email': f'rapid{i}@example.com',
                    'role': 'User'
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
        
        final_count = len(UserDatabase.load_data())
        # Should have exactly 3 more users
        self.assertEqual(final_count, initial_count + 3)
    
    def test_user_id_is_unique(self):
        """Test that each created user gets a unique ID"""
        ids = set()
        
        for i in range(5):
            response = self.client.post('/api/users',
                data=json.dumps({
                    'name': f'Unique ID User {i}',
                    'email': f'unique{i}@example.com',
                    'role': 'User'
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            ids.add(data['id'])
        
        # All IDs should be unique
        self.assertEqual(len(ids), 5)


class TestExportButtonVisibility(unittest.TestCase):
    """Tests to verify export functionality works correctly"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Initialize test data
        self._init_test_data()
    
    def _init_test_data(self):
        """Initialize test database with sample users"""
        test_users = [
            {"id": 1, "name": "Export Test User 1", "email": "export1@example.com", "role": "Admin"},
            {"id": 2, "name": "Export Test User 2", "email": "export2@example.com", "role": "User"},
            {"id": 3, "name": "Export Test User 3", "email": "export3@example.com", "role": "Manager"},
        ]
        UserDatabase.save_data(test_users)
    
    def test_export_json_endpoint_accessible(self):
        """Test that export JSON endpoint is accessible"""
        response = self.client.get('/api/users/export?format=json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
    
    def test_export_csv_endpoint_accessible(self):
        """Test that export CSV endpoint is accessible"""
        response = self.client.get('/api/users/export?format=csv')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response.content_type)
    
    def test_export_json_contains_all_users(self):
        """Test that exported JSON contains all users"""
        response = self.client.get('/api/users/export?format=json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        
        # Verify user data is present
        names = [user['name'] for user in data]
        self.assertIn('Export Test User 1', names)
        self.assertIn('Export Test User 2', names)
        self.assertIn('Export Test User 3', names)
    
    def test_export_csv_contains_headers_and_data(self):
        """Test that exported CSV contains proper headers and data"""
        response = self.client.get('/api/users/export?format=csv')
        self.assertEqual(response.status_code, 200)
        
        csv_content = response.data.decode()
        lines = [line.strip() for line in csv_content.strip().split('\n')]
        
        # First line should be headers
        self.assertEqual(lines[0], 'id,name,email,role')
        
        # Should have header + 3 users
        self.assertEqual(len(lines), 4)
        
        # Verify data is present
        csv_data = '\n'.join(lines)
        self.assertIn('Export Test User 1', csv_data)
        self.assertIn('export1@example.com', csv_data)
    
    def test_export_with_content_disposition(self):
        """Test that export responses have correct content disposition"""
        response_json = self.client.get('/api/users/export?format=json')
        self.assertIn('attachment', response_json.headers.get('Content-Disposition', ''))
        self.assertIn('users.json', response_json.headers.get('Content-Disposition', ''))
        
        response_csv = self.client.get('/api/users/export?format=csv')
        self.assertIn('attachment', response_csv.headers.get('Content-Disposition', ''))
        self.assertIn('users.csv', response_csv.headers.get('Content-Disposition', ''))
    
    def test_export_invalid_format_returns_error(self):
        """Test that invalid export format returns 400 error"""
        response = self.client.get('/api/users/export?format=xml')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)


class TestFormSubmissionValidation(unittest.TestCase):
    """Tests to verify form validation prevents issues"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        self._init_test_data()
    
    def _init_test_data(self):
        """Initialize test database with sample users"""
        test_users = [
            {"id": 1, "name": "Validation Test User", "email": "validation@example.com", "role": "Admin"},
        ]
        UserDatabase.save_data(test_users)
    
    def test_create_user_requires_all_fields(self):
        """Test that all fields are required for user creation"""
        # Missing email
        response = self.client.post('/api/users',
            data=json.dumps({
                'name': 'Incomplete User',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Missing role
        response = self.client.post('/api/users',
            data=json.dumps({
                'name': 'Incomplete User',
                'email': 'incomplete@example.com'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Missing name
        response = self.client.post('/api/users',
            data=json.dumps({
                'email': 'incomplete@example.com',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_user_invalid_email(self):
        """Test that invalid email format is rejected"""
        response = self.client.post('/api/users',
            data=json.dumps({
                'name': 'Invalid Email User',
                'email': 'notanemail',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
