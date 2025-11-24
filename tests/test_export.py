import unittest
import json
import csv
from io import StringIO
from app import create_app
from app.models import UserDatabase

class TestExportFunctionality(unittest.TestCase):
    """Test cases for user export functionality"""
    
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
            {"id": 3, "name": "Carol Davis", "email": "carol@example.com", "role": "Manager"},
        ]
        UserDatabase.save_data(test_users)
    
    def test_export_json_format(self):
        """Test exporting users as JSON"""
        response = self.client.get('/api/users/export?format=json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        # Check content-disposition header
        self.assertIn('Content-Disposition', response.headers)
        self.assertIn('users.json', response.headers['Content-Disposition'])
        
        # Verify JSON content
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], 'Alice Johnson')
        self.assertEqual(data[1]['email'], 'bob@example.com')
        self.assertEqual(data[2]['role'], 'Manager')
    
    def test_export_csv_format(self):
        """Test exporting users as CSV"""
        response = self.client.get('/api/users/export?format=csv')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response.content_type)
        
        # Check content-disposition header
        self.assertIn('Content-Disposition', response.headers)
        self.assertIn('users.csv', response.headers['Content-Disposition'])
        
        # Verify CSV content
        csv_content = response.data.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_content))
        rows = list(csv_reader)
        
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]['name'], 'Alice Johnson')
        self.assertEqual(rows[1]['email'], 'bob@example.com')
        self.assertEqual(rows[2]['role'], 'Manager')
        
        # Check CSV headers
        self.assertIn('id', rows[0].keys())
        self.assertIn('name', rows[0].keys())
        self.assertIn('email', rows[0].keys())
        self.assertIn('role', rows[0].keys())
    
    def test_export_default_format(self):
        """Test that default export format is JSON"""
        response = self.client.get('/api/users/export')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        # Verify it's valid JSON
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_export_invalid_format(self):
        """Test export with invalid format returns error"""
        response = self.client.get('/api/users/export?format=xml')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Format must be csv or json', data['error'])
    
    def test_export_json_structure(self):
        """Test that exported JSON has correct structure"""
        response = self.client.get('/api/users/export?format=json')
        data = json.loads(response.data)
        
        # Check each user has required fields
        for user in data:
            self.assertIn('id', user)
            self.assertIn('name', user)
            self.assertIn('email', user)
            self.assertIn('role', user)
            
            # Verify data types
            self.assertIsInstance(user['id'], int)
            self.assertIsInstance(user['name'], str)
            self.assertIsInstance(user['email'], str)
            self.assertIsInstance(user['role'], str)
    
    def test_export_csv_encoding(self):
        """Test CSV export handles special characters properly"""
        # Add user with special characters
        UserDatabase.save_data([
            {"id": 1, "name": "José García", "email": "jose@example.com", "role": "Admin"},
            {"id": 2, "name": "François Müller", "email": "francois@example.com", "role": "User"},
        ])
        
        response = self.client.get('/api/users/export?format=csv')
        self.assertEqual(response.status_code, 200)
        
        csv_content = response.data.decode('utf-8')
        self.assertIn('José García', csv_content)
        self.assertIn('François Müller', csv_content)
    
    def test_export_empty_database(self):
        """Test export when database is empty"""
        UserDatabase.save_data([])
        
        # Test JSON export
        response_json = self.client.get('/api/users/export?format=json')
        self.assertEqual(response_json.status_code, 200)
        data = json.loads(response_json.data)
        self.assertEqual(len(data), 0)
        
        # Test CSV export
        response_csv = self.client.get('/api/users/export?format=csv')
        self.assertEqual(response_csv.status_code, 200)
        csv_content = response_csv.data.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_content))
        rows = list(csv_reader)
        self.assertEqual(len(rows), 0)
    
    def test_export_large_dataset(self):
        """Test export with large number of users"""
        # Create 100 users
        large_dataset = [
            {"id": i, "name": f"User {i}", "email": f"user{i}@example.com", "role": "User"}
            for i in range(1, 101)
        ]
        UserDatabase.save_data(large_dataset)
        
        # Test JSON export
        response_json = self.client.get('/api/users/export?format=json')
        self.assertEqual(response_json.status_code, 200)
        data = json.loads(response_json.data)
        self.assertEqual(len(data), 100)
        
        # Test CSV export
        response_csv = self.client.get('/api/users/export?format=csv')
        self.assertEqual(response_csv.status_code, 200)
        csv_content = response_csv.data.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_content))
        rows = list(csv_reader)
        self.assertEqual(len(rows), 100)
    
    def test_export_case_insensitive_format(self):
        """Test that format parameter is case-insensitive"""
        # Test uppercase
        response_json = self.client.get('/api/users/export?format=JSON')
        self.assertEqual(response_json.status_code, 200)
        self.assertEqual(response_json.content_type, 'application/json')
        
        response_csv = self.client.get('/api/users/export?format=CSV')
        self.assertEqual(response_csv.status_code, 200)
        self.assertIn('text/csv', response_csv.content_type)
        
        # Test mixed case
        response_json2 = self.client.get('/api/users/export?format=Json')
        self.assertEqual(response_json2.status_code, 200)
        self.assertEqual(response_json2.content_type, 'application/json')

if __name__ == '__main__':
    unittest.main()
