from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestApprovalRequestAccount(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_model = cls.env['approval.category']
        cls.move_model = cls.env['account.move']
        cls.request_model = cls.env['approval.request']
        
        cls.category = cls.category_model.create({
            'name': 'Test Invoice Approval',
            'approval_type': 'invoice',
        })
        
        cls.approver = cls.env['res.users'].create({
            'name': 'Approver',
            'login': 'approver',
            'group_ids': [(4, cls.env.ref('approvals.group_approval_user').id)],
        })
        
        cls.env['approval.category.approver'].create({
            'category_id': cls.category.id,
            'user_id': cls.approver.id,
            'required': True,
        })
        
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.journal = cls.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        
    def test_01_approval_request_approves_invoice(self):
        """Test that approving a request updates the invoice and allows posting."""
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
        request = invoice.approval_request_id
        
        self.assertEqual(request.request_status, 'pending')
        
        # Approver approves
        request.with_user(self.approver).action_approve()
        
        self.assertEqual(request.request_status, 'approved')
        self.assertEqual(invoice.approval_request_status, 'approved')
        
        # Now we can post it
        invoice.action_post()
        self.assertEqual(invoice.state, 'posted')
        
    def test_02_approval_request_chatter(self):
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.env.user.partner_id.id,
        })
        invoice.action_request_approval()
        
        request = self.env['approval.request'].search([('account_move_id', '=', invoice.id)])
        
        # Messages count before approval
        msg_count_before = len(invoice.message_ids)
        
        request.with_user(self.approver).action_approve()
        
        # Messages count should increase
        msg_count_after = len(invoice.message_ids)
        self.assertTrue(msg_count_after > msg_count_before)
        
        # Ensure the last message contains approval info
        last_message = invoice.message_ids[0]
        self.assertIn("Approval Request", last_message.body)
        self.assertIn("Approved", last_message.body)
