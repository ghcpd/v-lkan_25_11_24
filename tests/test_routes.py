import unittest
from app import create_app


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_dashboard_contains_export_button(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn('Export', html)
        # ensure our fixed classes are present
        self.assertIn('export-dropdown', html)
        self.assertIn('export-dropdown-menu', html)
        self.assertIn('toggleExportMenu', html)


if __name__ == '__main__':
    unittest.main()
