from odoo.tests.common import TransactionCase

class TestApprovalCategory(TransactionCase):

    def setUp(self):
        super(TestApprovalCategory, self).setUp()
        self.ApprovalCategory = self.env['approval.category']

    def test_create_approval_category(self):
        """Test the creation of an approval category with basic fields."""
        category = self.ApprovalCategory.create({
            'name': 'Test Category',
            'description': 'Test Description',
            'active': True,
        })
        self.assertEqual(category.name, 'Test Category')
        self.assertEqual(category.description, 'Test Description')
        self.assertTrue(category.active)
