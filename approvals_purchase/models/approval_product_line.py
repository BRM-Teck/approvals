from odoo import models, fields

class ApprovalProductLine(models.Model):
    _inherit = 'approval.product.line'

    seller_id = fields.Many2one(
        'res.partner',
        string="Fournisseur",
        domain="[('is_company', '=', True)]"
    )
