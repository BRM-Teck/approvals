from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestApprovalAccountMove(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_model = cls.env['approval.category']
        cls.move_model = cls.env['account.move']
        
        cls.category = cls.category_model.create({
            'name': 'Test Invoice Approval',
            'approval_type': 'invoice',
        })
        
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.journal = cls.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        
    def test_01_invoice_approval_required(self):
        """Test that posting an invoice requires approval if category exists."""
        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'journal_id': self.journal.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Test line',
                'price_unit': 100.0,
            })]
        })
        
        with self.assertRaises(UserError):
            invoice.action_post()
            
    def test_02_invoice_request_approval(self):
        """Test requesting approval for an invoice."""
        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'journal_id': self.journal.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Test line',
                'price_unit': 100.0,
            })]
        })
        
        invoice.action_request_approval()
        self.assertTrue(invoice.approval_request_id)
        self.assertEqual(invoice.approval_request_status, 'pending')
