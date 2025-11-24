import unittest
from app import create_app

class TestUIDashboard(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_export_dropdown_visible_classes(self):
        """Ensure export dropdown has classes that enable it to appear above other elements"""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        html = resp.data.decode('utf-8')
        self.assertIn('overflow-visible', html)
        self.assertIn('z-60', html)
        self.assertIn('aria-label="export-dropdown"', html)
        self.assertIn('id="exportBtn"', html)
        self.assertIn('id="exportDropdown"', html)

if __name__ == '__main__':
    unittest.main()
