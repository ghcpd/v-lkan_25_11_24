"""
Comprehensive test script to verify both bug fixes:
1. Duplicate user creation prevention
2. Export button visibility and functionality
"""

import unittest
import json
from app import create_app
from app.models import UserDatabase
import tempfile
import os


class TestDuplicateCreationFixFinal(unittest.TestCase):
    """Verify that duplicate user creation is COMPLETELY prevented"""
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self._init_test_data()
    
    def _init_test_data(self):
        test_users = [
            {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "Admin"},
            {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "User"},
        ]
        UserDatabase.save_data(test_users)
    
    def test_create_user_adds_exactly_one_user(self):
        """Verify creating a user adds EXACTLY one user"""
        initial_count = len(UserDatabase.load_data())
        
        response = self.client.post('/api/users',
            json={'name': 'New User', 'email': 'new@example.com', 'role': 'User'}
        )
        
        self.assertEqual(response.status_code, 201)
        final_count = len(UserDatabase.load_data())
        
        # CRITICAL: Count must increase by EXACTLY 1
        self.assertEqual(final_count, initial_count + 1,
            f"Expected count to increase by 1, but it increased by {final_count - initial_count}")
    
    def test_rapid_sequential_creations(self):
        """Simulate rapid user creation and verify each adds exactly one user"""
        initial_count = len(UserDatabase.load_data())
        
        # Create 3 users rapidly
        for i in range(3):
            response = self.client.post('/api/users',
                json={
                    'name': f'Rapid User {i}',
                    'email': f'rapid{i}@example.com',
                    'role': 'User'
                }
            )
            self.assertEqual(response.status_code, 201)
            
            # After EACH creation, verify count is correct
            expected_count = initial_count + i + 1
            actual_count = len(UserDatabase.load_data())
            self.assertEqual(actual_count, expected_count,
                f"After creating user {i}, expected {expected_count} but got {actual_count}")
    
    def test_no_duplicate_emails_in_database(self):
        """Verify no duplicate emails exist in final database"""
        # Create a user
        self.client.post('/api/users',
            json={'name': 'Test', 'email': 'test@example.com', 'role': 'User'}
        )
        
        users = UserDatabase.load_data()
        emails = [u['email'] for u in users]
        
        # Check for duplicates
        self.assertEqual(len(emails), len(set(emails)),
            f"Found duplicate emails: {emails}")
    
    def test_all_user_ids_unique(self):
        """Verify all user IDs are unique"""
        # Create multiple users
        for i in range(5):
            self.client.post('/api/users',
                json={
                    'name': f'User {i}',
                    'email': f'user{i}@example.com',
                    'role': 'User'
                }
            )
        
        users = UserDatabase.load_data()
        ids = [u['id'] for u in users]
        
        # All IDs must be unique
        self.assertEqual(len(ids), len(set(ids)),
            f"Found duplicate IDs: {ids}")
        
        # IDs must be sequential from 1
        self.assertEqual(ids, list(range(1, len(ids) + 1)),
            f"IDs not sequential: {ids}")


class TestExportFunctionality(unittest.TestCase):
    """Verify export button and export functionality works correctly"""
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self._init_test_data()
    
    def _init_test_data(self):
        test_users = [
            {"id": 1, "name": "Export Test 1", "email": "export1@example.com", "role": "Admin"},
            {"id": 2, "name": "Export Test 2", "email": "export2@example.com", "role": "User"},
            {"id": 3, "name": "Export Test 3", "email": "export3@example.com", "role": "Manager"},
        ]
        UserDatabase.save_data(test_users)
    
    def test_export_json_accessible(self):
        """Test that export JSON endpoint is accessible and working"""
        response = self.client.get('/api/users/export?format=json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
    
    def test_export_csv_accessible(self):
        """Test that export CSV endpoint is accessible and working"""
        response = self.client.get('/api/users/export?format=csv')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response.content_type)
        
        csv_content = response.data.decode()
        lines = [line.strip() for line in csv_content.strip().split('\n')]
        # Header + 3 users
        self.assertEqual(len(lines), 4)
    
    def test_export_has_content_disposition_headers(self):
        """Test that exports have proper content-disposition headers"""
        # JSON export
        response_json = self.client.get('/api/users/export?format=json')
        self.assertIn('attachment', response_json.headers.get('Content-Disposition', ''))
        self.assertIn('users.json', response_json.headers.get('Content-Disposition', ''))
        
        # CSV export
        response_csv = self.client.get('/api/users/export?format=csv')
        self.assertIn('attachment', response_csv.headers.get('Content-Disposition', ''))
        self.assertIn('users.csv', response_csv.headers.get('Content-Disposition', ''))
    
    def test_export_contains_all_user_data(self):
        """Test that exports contain all user data correctly"""
        response = self.client.get('/api/users/export?format=json')
        data = json.loads(response.data)
        
        names = [u['name'] for u in data]
        emails = [u['email'] for u in data]
        
        self.assertIn('Export Test 1', names)
        self.assertIn('Export Test 2', names)
        self.assertIn('Export Test 3', names)
        self.assertIn('export1@example.com', emails)
        self.assertIn('export2@example.com', emails)
        self.assertIn('export3@example.com', emails)


class TestFormValidation(unittest.TestCase):
    """Test form validation to prevent invalid submissions"""
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_cannot_create_user_without_name(self):
        """Test that user cannot be created without name"""
        response = self.client.post('/api/users',
            json={'email': 'test@example.com', 'role': 'User'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_cannot_create_user_without_email(self):
        """Test that user cannot be created without email"""
        response = self.client.post('/api/users',
            json={'name': 'Test', 'role': 'User'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_cannot_create_user_without_role(self):
        """Test that user cannot be created without role"""
        response = self.client.post('/api/users',
            json={'name': 'Test', 'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_invalid_email_rejected(self):
        """Test that invalid email format is rejected"""
        response = self.client.post('/api/users',
            json={'name': 'Test', 'email': 'notanemail', 'role': 'User'}
        )
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
