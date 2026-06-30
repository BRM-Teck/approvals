from odoo import models, fields

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(
        selection_add=[('purchase', 'Create RFQ\'s')],
        ondelete={'purchase': 'set default'}
    )
