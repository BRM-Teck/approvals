from odoo import models, api

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    def _message_post_after_hook(self, message, msg_vals):
        res = super()._message_post_after_hook(message, msg_vals)
        if self.category_id.document_folder_id and message.attachment_ids:
            # Pour chaque pièce jointe, créer un document dans le dossier défini
            for attachment in message.attachment_ids:
                # Vérifier s'il n'y a pas déjà un document pour cette pièce jointe
                existing_doc = self.env['documents.document'].sudo().search([
                    ('attachment_id', '=', attachment.id)
                ], limit=1)
                
                if not existing_doc:
                    self.env['documents.document'].sudo().create({
                        'attachment_id': attachment.id,
                        'folder_id': self.category_id.document_folder_id.id,
                        'tag_ids': [(6, 0, self.category_id.document_tag_ids.ids)],
                        'res_model': self._name,
                        'res_id': self.id,
                    })
        return res
