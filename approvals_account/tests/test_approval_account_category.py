from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestApprovalAccountCategory(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_model = cls.env['approval.category']
    
    def test_01_create_invoice_approval_category(self):
        """Test creating an approval category for invoices."""
        category = self.category_model.create({
            'name': 'Test Invoice Approval',
            'approval_type': 'invoice',
        })
        self.assertEqual(category.approval_type, 'invoice')

    def test_02_create_payment_approval_category(self):
        """Test creating an approval category for payments."""
        category = self.category_model.create({
            'name': 'Test Payment Approval',
            'approval_type': 'payment',
        })
        self.assertEqual(category.approval_type, 'payment')
