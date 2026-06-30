from odoo import models, fields, api, _

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    purchase_order_count = fields.Integer(string="Purchase Order Count", compute='_compute_purchase_order_count')

    def _compute_purchase_order_count(self):
        for request in self:
            request.purchase_order_count = self.env['purchase.order'].search_count([('approval_request_id', '=', request.id)])

    def action_create_purchase_orders(self):
        self.ensure_one()
        # Group lines by partner_id if product lines have partner? No, approval request has partner_id
        if not self.partner_id:
            return # Require a partner to create a PO
            
        po = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'approval_request_id': self.id,
            'origin': self.name,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.description or line.product_id.name,
                'product_qty': line.quantity,
                'product_uom': line.product_uom_id.id or line.product_id.uom_po_id.id,
            }) for line in self.product_line_ids]
        })
        
        return self.action_view_purchase_orders()

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('purchase.purchase_rfq')
        action['domain'] = [('approval_request_id', '=', self.id)]
        action['context'] = {'default_approval_request_id': self.id, 'default_partner_id': self.partner_id.id}
        return action
