import unittest
import json
from app import create_app
from app.models import UserDatabase
import tempfile
import os

class TestDuplicateUserPrevention(unittest.TestCase):
    """Test cases to verify duplicate user prevention"""
    
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
            {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "Admin"},
            {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "User"},
        ]
        UserDatabase.save_data(test_users)
    
    def test_create_user_with_duplicate_email(self):
        """Test that creating a user with duplicate email fails"""
        response = self.client.post('/api/users',
            data=json.dumps({
                'name': 'Another Alice',
                'email': 'alice@example.com',  # Duplicate email
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('already exists', data['error'].lower())
    
    def test_create_user_with_duplicate_email_case_insensitive(self):
        """Test that duplicate check is case-insensitive"""
        response = self.client.post('/api/users',
            data=json.dumps({
                'name': 'Another Alice',
                'email': 'ALICE@EXAMPLE.COM',  # Same email, different case
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('already exists', data['error'].lower())
    
    def test_create_user_with_unique_email(self):
        """Test that creating a user with unique email succeeds"""
        response = self.client.post('/api/users',
            data=json.dumps({
                'name': 'Charlie Davis',
                'email': 'charlie@example.com',  # Unique email
                'role': 'Manager'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['email'], 'charlie@example.com')
        self.assertEqual(data['name'], 'Charlie Davis')
    
    def test_update_user_with_duplicate_email(self):
        """Test that updating a user to have a duplicate email fails"""
        response = self.client.put('/api/users/2',
            data=json.dumps({
                'email': 'alice@example.com'  # Bob trying to use Alice's email
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('already exists', data['error'].lower())
    
    def test_update_user_with_same_email(self):
        """Test that updating a user with their own email succeeds"""
        response = self.client.put('/api/users/1',
            data=json.dumps({
                'name': 'Alice Updated',
                'email': 'alice@example.com',  # Same email
                'role': 'Admin'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Alice Updated')
        self.assertEqual(data['email'], 'alice@example.com')
    
    def test_update_user_with_unique_email(self):
        """Test that updating a user with a unique email succeeds"""
        response = self.client.put('/api/users/2',
            data=json.dumps({
                'email': 'bob.updated@example.com'  # New unique email
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['email'], 'bob.updated@example.com')
    
    def test_multiple_users_different_emails(self):
        """Test creating multiple users with different emails"""
        # Create first user
        response1 = self.client.post('/api/users',
            data=json.dumps({
                'name': 'User One',
                'email': 'user1@test.com',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 201)
        
        # Create second user with different email
        response2 = self.client.post('/api/users',
            data=json.dumps({
                'name': 'User Two',
                'email': 'user2@test.com',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 201)
        
        # Verify both users exist
        response = self.client.get('/api/users')
        data = json.loads(response.data)
        self.assertGreaterEqual(len(data['data']), 4)  # At least 4 users now
    
    def test_duplicate_prevention_after_delete(self):
        """Test that email can be reused after user is deleted"""
        # Delete user with email
        delete_response = self.client.delete('/api/users/1')
        self.assertEqual(delete_response.status_code, 200)
        
        # Create new user with same email
        response = self.client.post('/api/users',
            data=json.dumps({
                'name': 'New Alice',
                'email': 'alice@example.com',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['email'], 'alice@example.com')

if __name__ == '__main__':
    unittest.main()
