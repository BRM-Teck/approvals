from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestPurchaseApproval(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_buyer = cls.env['res.users'].create({
            'name': 'Buyer User',
            'login': 'buyer',
            'email': 'buyer@example.com',
            'group_ids': [(6, 0, [
                cls.env.ref('purchase.group_purchase_user').id,
                cls.env.ref('base.group_user').id,
                cls.env.ref('approvals.group_approval_user').id
            ])]
        })
        
        cls.user_approver = cls.env['res.users'].create({
            'name': 'Approver User',
            'login': 'approver',
            'email': 'approver@example.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('approvals.group_approval_manager').id
            ])]
        })
        
        cls.category = cls.env['approval.category'].create({
            'name': 'Purchase Approval',
            'approval_type': 'purchase',
            'approver_ids': [(0, 0, {
                'user_id': cls.user_approver.id,
                'required': True,
                'sequence': 10,
            })]
        })
        
        cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu',
            'standard_price': 100.0,
        })

    def test_purchase_approval_flow(self):
        # 1. Buyer creates PO
        po = self.env['purchase.order'].with_user(self.user_buyer).create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_qty': 5,
                'price_unit': 100.0,
            })]
        })
        
        # 2. Buyer requests approval
        po.with_user(self.user_buyer).action_request_approval()
        
        # 3. Check if approval request is created
        self.assertTrue(po.approval_request_id, "Approval request should be created and linked to PO")
        self.assertEqual(po.approval_request_id.category_id.approval_type, 'purchase', "Category should be purchase")
        self.assertEqual(po.approval_request_id.request_status, 'pending', "Approval request should be pending")
        
        # 4. Buyer cannot confirm PO
        with self.assertRaises(UserError):
            po.with_user(self.user_buyer).button_confirm()
            
        # 5. Approver approves
        # Before approving, we must confirm the request (it's already confirmed in action_request_approval though)
        if po.approval_request_id.request_status == 'new':
            po.approval_request_id.with_user(self.user_buyer).action_confirm()
            
        # Approver approves
        po.approval_request_id.with_user(self.user_approver).action_approve()
        
        # 6. Now buyer can confirm PO
        self.assertEqual(po.approval_request_id.request_status, 'approved', "Approval request should be approved")
        po.with_user(self.user_buyer).button_confirm()
        self.assertEqual(po.state, 'purchase', "PO should be confirmed")
