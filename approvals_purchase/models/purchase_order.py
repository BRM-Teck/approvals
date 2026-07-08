from odoo import models, fields, _, api
from odoo.exceptions import UserError
from markupsafe import Markup

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approval_request_id = fields.Many2one('approval.request', string='Approval Request', copy=False, tracking=True)
    approval_request_status = fields.Selection(related='approval_request_id.request_status', string="Approval Status")
    user_status = fields.Selection(related='approval_request_id.user_status', string="User Status")

    def action_request_approval(self):
        for order in self:
            if order.approval_request_id:
                raise UserError(_("An approval request is already linked to this order."))
            
            category = self.env['approval.category'].search([('approval_type', '=', 'purchase')], limit=1)
            if not category:
                raise UserError(_("Please define an Approval Category with type 'Purchase' first."))
                
            # Create the approval request
            request_vals = {
                'name': _("Approval for PO: %s", order.name),
                'category_id': category.id,
                'request_owner_id': order.user_id.id or self.env.user.id,
                'partner_id': order.partner_id.id,
                'amount': order.amount_total,
                'product_line_ids': [(0, 0, {
                    'product_id': line.product_id.id,
                    'description': line.name,
                    'quantity': line.product_qty,
                    'product_uom_id': getattr(line, 'product_uom', getattr(line, 'product_uom_id', line.product_id.uom_id)).id,
                }) for line in order.order_line]
            }
            approval_request = self.env['approval.request'].create(request_vals)
            order.approval_request_id = approval_request.id
            approval_request.action_confirm() # Automatically submit it
            
            # Traceability: post messages
            order.message_post(body=Markup(_("Approval request submitted: <a href='#' data-oe-model='approval.request' data-oe-id='%s'>%s</a>")) % (approval_request.id, approval_request.name))
            approval_request.message_post(body=Markup(_("Created from Purchase Order: <a href='#' data-oe-model='purchase.order' data-oe-id='%s'>%s</a>")) % (order.id, order.name))

    def action_approve(self):
        for order in self:
            if order.approval_request_id:
                order.approval_request_id.action_approve()

    def action_refuse(self):
        for order in self:
            if order.approval_request_id:
                order.approval_request_id.action_refuse()

    def button_confirm(self):
        for order in self:
            if order.approval_request_id and order.approval_request_id.request_status != 'approved':
                raise UserError(_("You cannot confirm this order because the associated approval request is not yet approved."))
            if not order.approval_request_id and self.env.user.has_group('purchase.group_purchase_user') and not self.env.user.has_group('purchase.group_purchase_manager'):
                # Optional: Force users to request approval if they are just users, not managers
                # Actually, standard flow can be driven by a setting, but for now we enforce it if they haven't requested and they click confirm
                pass # or raise an error if mandatory
        return super().button_confirm()

