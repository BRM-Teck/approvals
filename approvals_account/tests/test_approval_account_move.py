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

    def test_03_journal_entry_bypass_approval(self):
        """Test that regular journal entries bypass the invoice approval process."""
        account = self.env['account.account'].search([('company_id', '=', self.env.company.id)], limit=1)
        journal = self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', self.env.company.id)], limit=1)
        
        journal_entry = self.move_model.create({
            'move_type': 'entry',
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'name': 'Debit line',
                    'debit': 100.0,
                    'credit': 0.0,
                    'account_id': account.id
                }),
                (0, 0, {
                    'name': 'Credit line',
                    'debit': 0.0,
                    'credit': 100.0,
                    'account_id': account.id
                }),
            ]
        })
        
        # This should not raise any UserError
        journal_entry.action_post()
        self.assertEqual(journal_entry.state, 'posted')
