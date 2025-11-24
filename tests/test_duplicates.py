import unittest
import json
from app import create_app
from app.models import UserDatabase


class TestDuplicateUserHandling(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        # initialize test data
        self._init_test_data()

    def _init_test_data(self):
        test_users = [
            {"id": 1, "name": "Test User 1", "email": "test1@example.com", "role": "Admin"},
            {"id": 2, "name": "Test User 2", "email": "test2@example.com", "role": "User"},
        ]
        UserDatabase.save_data(test_users)

    def test_create_user_duplicate_email(self):
        response = self.client.post(
            '/api/users',
            data=json.dumps({
                'name': 'Another User',
                'email': 'test1@example.com',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('already exists', data['error'])

    def test_update_user_duplicate_email(self):
        # Attempt to change user 1's email to user 2's email
        response = self.client.put(
            '/api/users/1',
            data=json.dumps({'email': 'test2@example.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('already exists', data['error'])


if __name__ == '__main__':
    unittest.main()
