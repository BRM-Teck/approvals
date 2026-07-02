from odoo.tests.common import TransactionCase

class TestApprovalRequest(TransactionCase):

    def setUp(self):
        super(TestApprovalRequest, self).setUp()
        self.ApprovalCategory = self.env['approval.category']
        self.ApprovalRequest = self.env['approval.request']
        self.category = self.ApprovalCategory.create({
            'name': 'Test Category',
            'approval_minimum': 1,
        })

    def test_create_approval_request(self):
        """Test creating an approval request."""
        request = self.ApprovalRequest.create({
            'name': 'Test Request',
            'category_id': self.category.id,
        })
        self.assertEqual(request.request_status, 'new')
        self.assertEqual(request.category_id, self.category)

    def test_approver_hierarchy(self):
        """Test the approver sequence/hierarchy."""
        category_seq = self.ApprovalCategory.create({
            'name': 'Sequence Category',
            'approval_minimum': 2,
            'approver_sequence': True,
        })
        user1 = self.env['res.users'].create({'name': 'Approver 1', 'login': 'app1'})
        user2 = self.env['res.users'].create({'name': 'Approver 2', 'login': 'app2'})
        
        request = self.ApprovalRequest.create({
            'name': 'Test Sequence Request',
            'category_id': category_seq.id,
            'approver_ids': [
                (0, 0, {'user_id': user1.id, 'sequence': 10, 'required': True}),
                (0, 0, {'user_id': user2.id, 'sequence': 20, 'required': True}),
            ]
        })
        
        # Confirm request
        request.action_confirm()
        
        app1 = request.approver_ids.filtered(lambda a: a.user_id == user1)
        app2 = request.approver_ids.filtered(lambda a: a.user_id == user2)
        
        # Only the first approver should be pending
        self.assertEqual(app1.status, 'pending')
        self.assertEqual(app2.status, 'new')
        
        # Approver 1 approves
        request.with_user(user1).sudo().action_approve()
        
        # Approver 2 should now be pending
        self.assertEqual(app1.status, 'approved')
        self.assertEqual(app2.status, 'pending')
        self.assertEqual(request.request_status, 'pending')
        
        # Approver 2 approves
        request.with_user(user2).sudo().action_approve()
        
        self.assertEqual(app2.status, 'approved')
        self.assertEqual(request.request_status, 'approved')
