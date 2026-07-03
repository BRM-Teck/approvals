from odoo import models, fields, api

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    account_move_id = fields.Many2one('account.move', string="Invoice")
    account_payment_id = fields.Many2one('account.payment', string="Payment")

    def action_approve(self):
        res = super().action_approve()
        
        # Chatter integration
        for request in self:
            if request.request_status == 'approved':
                if request.account_move_id:
                    request.account_move_id.message_post(body="Approval Request %s has been Approved." % request.name)
                elif request.account_payment_id:
                    request.account_payment_id.message_post(body="Approval Request %s has been Approved." % request.name)
                    
        return res

    def action_refuse(self):
        res = super().action_refuse()
        
        # Chatter integration
        for request in self:
            if request.request_status == 'refused':
                if request.account_move_id:
                    request.account_move_id.message_post(body="Approval Request %s has been Refused." % request.name)
                elif request.account_payment_id:
                    request.account_payment_id.message_post(body="Approval Request %s has been Refused." % request.name)
                    
        return res
