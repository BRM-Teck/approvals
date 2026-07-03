from odoo import models, fields, _, api
from odoo.exceptions import UserError
from markupsafe import Markup

class AccountMove(models.Model):
    _inherit = 'account.move'

    approval_request_id = fields.Many2one('approval.request', string='Approval Request', copy=False, tracking=True)
    approval_request_status = fields.Selection(related='approval_request_id.request_status', string="Approval Status")

    def action_request_approval(self):
        for move in self:
            if move.approval_request_id:
                raise UserError(_("An approval request is already linked to this invoice."))
            
            category = self.env['approval.category'].search([('approval_type', '=', 'invoice')], limit=1)
            if not category:
                raise UserError(_("Please define an Approval Category with type 'Invoice' first."))
                
            request_vals = {
                'name': _("Approval for Invoice: %s", move.name or 'Draft'),
                'category_id': category.id,
                'request_owner_id': move.invoice_user_id.id or self.env.user.id,
                'partner_id': move.partner_id.id,
                'amount': move.amount_total,
                'reason': move.narration,
            }
            approval_request = self.env['approval.request'].create(request_vals)
            move.approval_request_id = approval_request.id
            approval_request.action_confirm()
            
            move.message_post(body=Markup(_("Approval request submitted: <a href='#' data-oe-model='approval.request' data-oe-id='%s'>%s</a>")) % (approval_request.id, approval_request.name))
            approval_request.message_post(body=Markup(_("Created from Invoice: <a href='#' data-oe-model='account.move' data-oe-id='%s'>%s</a>")) % (move.id, move.name or 'Draft'))

    def action_post(self):
        for move in self:
            if move.approval_request_id and move.approval_request_status != 'approved':
                raise UserError(_("You cannot confirm this invoice because the associated approval request is not yet approved."))
            
            category = self.env['approval.category'].search([('approval_type', '=', 'invoice')], limit=1)
            if category and not move.approval_request_id:
                # If a category exists and no approval request is linked, we enforce approval if the category is configured to require it.
                # For simplicity, if the category exists, we force approval.
                raise UserError(_("You must request approval before confirming this invoice."))
        return super().action_post()
