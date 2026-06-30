from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approval_request_id = fields.Many2one('approval.request', string='Approval Request', copy=False)
