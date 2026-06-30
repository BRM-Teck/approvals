from odoo import models, fields, api

class ApprovalProductLine(models.Model):
    _name = 'approval.product.line'
    _description = 'Approval Product Line'

    approval_request_id = fields.Many2one('approval.request', string='Approval Request', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='approval_request_id.company_id', store=True)
    
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
