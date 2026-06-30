from odoo import models, fields, api, _

class ApprovalRequest(models.Model):
    _name = 'approval.request'
    _description = 'Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True, default='New')
    request_owner_id = fields.Many2one('res.users', string='Request Owner', default=lambda self: self.env.user, required=True, tracking=True)
    category_id = fields.Many2one('approval.category', string='Category', required=True, tracking=True)
    category_image = fields.Binary(related='category_id.image')
    approval_type = fields.Selection(related='category_id.approval_type')
    approval_minimum = fields.Integer(related='category_id.approval_minimum')
    approver_sequence = fields.Boolean(related='category_id.approver_sequence')
    automated_sequence = fields.Boolean(related='category_id.automated_sequence')
    
    # Category related fields for view toggling
    has_date = fields.Selection(related='category_id.has_date')
    has_period = fields.Selection(related='category_id.has_period')
    has_quantity = fields.Selection(related='category_id.has_quantity')
    has_amount = fields.Selection(related='category_id.has_amount')
    has_reference = fields.Selection(related='category_id.has_reference')
    has_partner = fields.Selection(related='category_id.has_partner')
    has_payment_method = fields.Selection(related='category_id.has_payment_method')
    has_location = fields.Selection(related='category_id.has_location')
    has_product = fields.Selection(related='category_id.has_product')
    requirer_document = fields.Selection(related='category_id.requirer_document')

    # Data fields
    date = fields.Datetime(string='Date')
    date_start = fields.Datetime(string='Date start')
    date_end = fields.Datetime(string='Date end')
    date_confirmed = fields.Datetime(string='Date confirmed')
    location = fields.Char(string='Location')
    partner_id = fields.Many2one('res.partner', string='Contact')
    quantity = fields.Float(string='Quantity')
    amount = fields.Float(string='Amount')
    reference = fields.Char(string='Reference')
    reason = fields.Html(string='Description')
    
    company_id = fields.Many2one('res.company', string='Company', related='category_id.company_id', store=True)
    
    # Status
    request_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='Status', default='new', tracking=True)
    
    user_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='User Status', compute='_compute_user_status')
    
    # Relational
    approver_ids = fields.One2many('approval.approver', 'request_id', string='Approvers')
    product_line_ids = fields.One2many('approval.product.line', 'approval_request_id', string='Products')
    
    attachment_number = fields.Integer(string='Number of Attachments', compute='_compute_attachment_number')
    approval_properties = fields.Properties(
        'Properties',
        definition='category_id.approval_properties_definition',
        copy=True)

    change_request_owner = fields.Boolean(string='Can Change Request Owner', compute='_compute_change_request_owner')
    has_access_to_request = fields.Boolean(string='Has Access To Request', compute='_compute_has_access_to_request')

    def _compute_attachment_number(self):
        for request in self:
            request.attachment_number = self.env['ir.attachment'].search_count([
                ('res_model', '=', self._name), ('res_id', '=', request.id)
            ])

    def _compute_user_status(self):
        for request in self:
            approver = request.approver_ids.filtered(lambda a: a.user_id == self.env.user)
            request.user_status = approver.status if approver else False

    def _compute_change_request_owner(self):
        for request in self:
            request.change_request_owner = True # To refine based on rules

    def _compute_has_access_to_request(self):
        for request in self:
            request.has_access_to_request = True

    def action_confirm(self):
        self.ensure_one()
        self.request_status = 'pending'
        
        # Notification and activities for approvers
        approver_users = self.approver_ids.mapped('user_id')
        approver_partners = approver_users.mapped('partner_id')
        if approver_partners:
            self.message_subscribe(partner_ids=approver_partners.ids)
            
        self.message_post(
            body=_("The request has been submitted and is pending for your approval."),
            partner_ids=approver_partners.ids,
        )
        
        for user in approver_users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=user.id,
                note=_("Please review this approval request.")
            )

    def action_approve(self):
        self.ensure_one()
        self.request_status = 'approved'
        self.message_post(
            body=_("The request has been approved."),
            partner_ids=self.request_owner_id.partner_id.ids,
        )
        # Clear activities
        self.activity_unlink(['mail.mail_activity_data_todo'])

    def action_refuse(self):
        self.ensure_one()
        self.request_status = 'refused'
        self.message_post(
            body=_("The request has been refused."),
            partner_ids=self.request_owner_id.partner_id.ids,
        )
        # Clear activities
        self.activity_unlink(['mail.mail_activity_data_todo'])

    def action_withdraw(self):
        self.ensure_one()
        self.request_status = 'pending'

    def action_draft(self):
        self.ensure_one()
        self.request_status = 'new'

    def action_cancel(self):
        self.ensure_one()
        self.request_status = 'cancel'
        
    def action_get_attachment_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'view_mode': 'list,form',
        }
