from odoo import models, fields, api, _

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    purchase_order_count = fields.Integer(string="Purchase Order Count", compute='_compute_purchase_order_count')

    def _compute_purchase_order_count(self):
        for request in self:
            request.purchase_order_count = self.env['purchase.order'].search_count([('approval_request_id', '=', request.id)])

    def action_approve(self):
        super().action_approve()
        for request in self:
            if request.request_status == 'approved' and request.category_id.approval_type == 'purchase':
                if not request.purchase_order_count:
                    request.action_create_purchase_orders()

    def action_create_purchase_orders(self):
        self.ensure_one()
        # Group lines by seller_id, fallback to partner_id
        default_partner = self.partner_id
        lines_by_partner = {}
        for line in self.product_line_ids:
            partner = line.seller_id or default_partner
            if not partner:
                continue
            if partner not in lines_by_partner:
                lines_by_partner[partner] = []
            lines_by_partner[partner].append(line)
        
        for partner, lines in lines_by_partner.items():
            po = self.env['purchase.order'].sudo().create({
                'partner_id': partner.id,
                'approval_request_id': self.id,
                'origin': self.name,
                'order_line': [(0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.description or line.product_id.name,
                    'product_qty': line.quantity,
                    'product_uom': line.product_uom_id.id or line.product_id.uom_id.id,
                }) for line in lines]
            })
        
        return self.action_view_purchase_orders()

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('purchase.purchase_rfq')
        action['domain'] = [('approval_request_id', '=', self.id)]
        action['context'] = {'default_approval_request_id': self.id, 'default_partner_id': self.partner_id.id}
        return action
