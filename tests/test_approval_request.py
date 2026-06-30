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
