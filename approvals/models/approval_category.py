from odoo import models, fields, api, _

class ApprovalCategory(models.Model):
    _name = 'approval.category'
    _description = 'Approval Category'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, translate=True, help="Category name (e.g. Procurement, Time Off).")
    active = fields.Boolean(default=True, help="If unchecked, it will allow you to hide the category without removing it.")
    sequence = fields.Integer(string='Sequence', default=10, help="Determine the display order")
    description = fields.Char(string='Description', translate=True, help="Provide a detailed description or instructions for the users creating requests in this category.")
    image = fields.Binary(string='Image', help="Image for the kanban view")
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, help="Restrict this category to a specific company.")
    
    # Options
    approval_type = fields.Selection([('approval', 'Approval')], string='Approval Type', default='approval', help="Internal approval type.")
    requirer_document = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Document', default='optional', required=True, help="Require an attached document.")
    has_partner = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Contact', default='no', required=True, help="Require a contact (partner) on the request.")
    has_date = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Date', default='no', required=True, help="Require a date on the request.")
    has_period = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Period', default='no', required=True, help="Require a period (start and end date).")
    has_product = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Product', default='no', required=True, help="Require a specific product.")
    has_quantity = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Quantity', default='no', required=True, help="Require a quantity.")
    has_amount = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Amount', default='no', required=True, help="Require an amount.")
    has_reference = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Reference', default='no', required=True, help="Require a custom reference.")
    has_payment_method = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Payment Method', default='no', required=True, help="Require a payment method.")
    has_location = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Location', default='no', required=True, help="Require a location.")
    
    # Approvers
    manager_approval = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('no', 'None')], string='Manager Approval', default='no', required=True, help="How the employee's manager interacts with this category.\n"
                                                                                                                                                                        "- Required: The employee's manager must approve the request.\n"
                                                                                                                                                                        "- Optional: The employee's manager will be added as an approver but can be removed.\n"
                                                                                                                                                                        "- None: The employee's manager will not be added automatically.")
    approval_minimum = fields.Integer(string='Minimum Approval', default=1, help="Minimum number of approvals required to confirm a request.")
    invalid_minimum = fields.Boolean(string='Invalid Minimum', compute='_compute_invalid_minimum')
    invalid_minimum_warning = fields.Char(string='Invalid Minimum Warning', compute='_compute_invalid_minimum')
    
    approver_sequence = fields.Boolean(string='Approver Sequence', help="If checked, the approvers have to approve in a specific sequence.")
    
    # Sequence
    automated_sequence = fields.Boolean(string='Automated Sequence', help="If checked, the Approval Requests will have an automated generated name based on the given code.")
    sequence_code = fields.Char(string='Sequence Code', help="Code used to generate the sequence of requests. E.g. 'PROC' for Procurement.")
    sequence_id = fields.Many2one('ir.sequence', string='Sequence ID', help="The ir.sequence used to generate request names.", copy=False)

    # Counts
    request_to_validate_count = fields.Integer(string='Requests to Validate', compute='_compute_request_to_validate_count')

    # Relational
    user_ids = fields.Many2many('res.users', string='Approvers', compute='_compute_user_ids', help="Users who are configured to approve this category.")
    approver_ids = fields.One2many('approval.category.approver', 'category_id', string='Approvers', help="Specific approvers for this category.")
    approval_properties_definition = fields.PropertiesDefinition('Approval Properties', help="Custom properties to add dynamic fields to requests.")

    @api.depends('approver_ids.user_id')
    def _compute_user_ids(self):
        for category in self:
            category.user_ids = category.approver_ids.mapped('user_id')

    @api.depends('approval_minimum', 'approver_ids') 
    def _compute_invalid_minimum(self):
        for category in self:
            category.invalid_minimum = category.approval_minimum > len(category.approver_ids)
            if category.invalid_minimum:
                category.invalid_minimum_warning = _('The minimum number of approvals exceeds the number of approvers.')
            else:
                category.invalid_minimum_warning = False

    def _compute_request_to_validate_count(self):
        for category in self:
            category.request_to_validate_count = 0

    def create_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Request'),
            'res_model': 'approval.request',
            'view_mode': 'form',
            'context': {'default_category_id': self.id},
        }

    def action_view_requests_to_validate(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Requests to Validate'),
            'res_model': 'approval.request',
            'view_mode': 'list,form',
            'domain': [('category_id', '=', self.id)],
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('automated_sequence') and vals.get('sequence_code'):
                sequence = self.env['ir.sequence'].sudo().create({
                    'name': _('Approval Sequence %s', vals.get('name', '')),
                    'code': 'approval.request.%s' % vals.get('sequence_code'),
                    'prefix': vals.get('sequence_code') + '-',
                    'padding': 5,
                    'company_id': vals.get('company_id') or self.env.company.id,
                })
                vals['sequence_id'] = sequence.id
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        for category in self:
            if category.automated_sequence and category.sequence_code and not category.sequence_id:
                sequence = self.env['ir.sequence'].sudo().create({
                    'name': _('Approval Sequence %s', category.name),
                    'code': 'approval.request.%s' % category.sequence_code,
                    'prefix': category.sequence_code + '-',
                    'padding': 5,
                    'company_id': category.company_id.id or self.env.company.id,
                })
                category.sequence_id = sequence.id
            elif category.sequence_id and 'sequence_code' in vals and category.sequence_code:
                category.sequence_id.sudo().write({
                    'code': 'approval.request.%s' % category.sequence_code,
                    'prefix': category.sequence_code + '-',
                })
        return res

class ApprovalCategoryApprover(models.Model):
    _name = 'approval.category.approver'
    _description = 'Approval Category Approver'
    _order = 'sequence, id'

    category_id = fields.Many2one('approval.category', string='Category', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True)
    company_id = fields.Many2one(related='category_id.company_id', store=True)
    sequence = fields.Integer(string='Sequence', default=10)
    required = fields.Boolean(string='Is Required', default=False)
