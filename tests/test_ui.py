import unittest
from pathlib import Path


class TestUIDashboard(unittest.TestCase):
    def test_export_dropdown_overlay(self):
        """Ensure export dropdown has overflow visible and high z-index so it's not obscured"""
        template_path = Path(__file__).resolve().parents[1] / 'app' / 'templates' / 'dashboard.html'
        self.assertTrue(template_path.exists(), f"Template not found: {template_path}")

        content = template_path.read_text(encoding='utf-8')
        # Check that the header wrapper allows overflow and has high stacking so the dropdown is visible
        self.assertIn('glass-effect rounded-2xl shadow-2xl p-8 mb-8 overflow-visible z-50 relative', content)
        # Check dropdown uses higher z-index
        self.assertIn('shadow-xl z-[9999]', content)


if __name__ == '__main__':
    unittest.main()
