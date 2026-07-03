from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestApprovalAccountPayment(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_model = cls.env['approval.category']
        cls.payment_model = cls.env['account.payment']
        
        cls.category = cls.category_model.create({
            'name': 'Test Payment Approval',
            'approval_type': 'payment',
        })
        
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.journal = cls.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        if not cls.journal:
            cls.journal = cls.env['account.journal'].create({
                'name': 'Bank Test',
                'type': 'bank',
                'code': 'BTST'
            })
        
    def test_01_payment_approval_required(self):
        """Test that posting a payment requires approval if category exists."""
        payment = self.payment_model.create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 500.0,
            'journal_id': self.journal.id,
        })
        
        with self.assertRaises(UserError):
            payment.action_post()
            
    def test_02_payment_request_approval(self):
        """Test requesting approval for a payment."""
        payment = self.payment_model.create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 500.0,
            'journal_id': self.journal.id,
        })
        
        payment.action_request_approval()
        self.assertTrue(payment.approval_request_id)
        self.assertEqual(payment.approval_request_status, 'pending')
