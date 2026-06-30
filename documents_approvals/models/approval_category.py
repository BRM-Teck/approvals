from odoo import models, fields, api, _

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    document_folder_id = fields.Many2one(
        'documents.document', string="Workspace",
        domain=[('type', '=', 'folder')],
        help="Workspace where the attached documents will be stored."
    )
    document_tag_ids = fields.Many2many(
        'documents.tag', string="Tags",
        domain="[('folder_id', '=', document_folder_id)]",
        help="Tags to apply to the created documents."
    )
