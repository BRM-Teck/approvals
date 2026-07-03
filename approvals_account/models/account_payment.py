from odoo import models, fields, _, api
from odoo.exceptions import UserError
from markupsafe import Markup

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    approval_request_id = fields.Many2one('approval.request', string='Approval Request', copy=False, tracking=True)
    approval_request_status = fields.Selection(related='approval_request_id.request_status', string="Approval Status")

    def action_request_approval(self):
        for payment in self:
            if payment.approval_request_id:
                raise UserError(_("An approval request is already linked to this payment."))
            
            category = self.env['approval.category'].search([('approval_type', '=', 'payment')], limit=1)
            if not category:
                raise UserError(_("Please define an Approval Category with type 'Payment' first."))
                
            request_vals = {
                'name': _("Approval for Payment: %s", payment.name or 'Draft'),
                'category_id': category.id,
                'request_owner_id': self.env.user.id,
                'partner_id': payment.partner_id.id,
                'amount': payment.amount,
                'reason': getattr(payment, 'ref', getattr(payment, 'memo', '')),
                'account_payment_id': payment.id,
            }
            approval_request = self.env['approval.request'].create(request_vals)
            payment.approval_request_id = approval_request.id
            approval_request.action_confirm()
            
            payment.message_post(body=Markup(_("Approval request submitted: <a href='#' data-oe-model='approval.request' data-oe-id='%s'>%s</a>")) % (approval_request.id, approval_request.name))
            approval_request.message_post(body=Markup(_("Created from Payment: <a href='#' data-oe-model='account.payment' data-oe-id='%s'>%s</a>")) % (payment.id, payment.name or 'Draft'))

    def action_post(self):
        for payment in self:
            if payment.approval_request_id and payment.approval_request_status != 'approved':
                raise UserError(_("You cannot confirm this payment because the associated approval request is not yet approved."))
            
            category = self.env['approval.category'].search([('approval_type', '=', 'payment')], limit=1)
            if category and not payment.approval_request_id:
                raise UserError(_("You must request approval before confirming this payment."))
        return super().action_post()
