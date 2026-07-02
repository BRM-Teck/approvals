from odoo import models, fields, api

class ApprovalApprover(models.Model):
    _name = 'approval.approver'
    _description = 'Approver'

    user_id = fields.Many2one('res.users', string='User', required=True)
    request_id = fields.Many2one('approval.request', string='Request', ondelete='cascade')
    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='Status', default='new', required=True, copy=False)
    
    required = fields.Boolean(string='Is Required', default=True)
    sequence = fields.Integer(string='Sequence', default=10)
    company_id = fields.Many2one(related='request_id.company_id', store=True)
    
    existing_request_user_ids = fields.Many2many('res.users', compute='_compute_existing_request_user_ids')
    can_edit = fields.Boolean(compute='_compute_can_edit')
    can_edit_user_id = fields.Boolean(compute='_compute_can_edit_user_id')

    def _compute_existing_request_user_ids(self):
        for approver in self:
            approver.existing_request_user_ids = approver.request_id.approver_ids.user_id

    def _compute_can_edit(self):
        for approver in self:
            approver.can_edit = True

    def _compute_can_edit_user_id(self):
        for approver in self:
            approver.can_edit_user_id = True
