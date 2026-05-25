from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import re


class HmsPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Hospital Patient'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    email = fields.Char(string='Email')
    birth_date = fields.Date(string='Birth Date')
    history = fields.Html(string='History')
    cr_ratio = fields.Float(string='CR Ratio')
    blood_type = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
    ], string='Blood Type')
    pcr = fields.Boolean(string='PCR')
    image = fields.Binary(string='Image')
    address = fields.Text(string='Address')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    department_id = fields.Many2one('hms.department', string='Department')
    department_capacity = fields.Integer(string='Department Capacity', related='department_id.capacity')
    doctor_ids = fields.Many2many('hms.doctor', string='Doctors')
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious'),
    ], string='State', default='undetermined')
    log_history_ids = fields.One2many('hms.log.history', 'patient_id', string='Log History')

    _sql_constraints = [
        ('email_unique', 'unique(email)', 'Email must be unique')
    ]

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = date.today()
                birth = record.birth_date
                record.age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            else:
                record.age = 0

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, record.email):
                    raise ValidationError('Please enter a valid email address')

    @api.onchange('age')
    def _onchange_age(self):
        if self.age and self.age < 30:
            self.pcr = True
            return {
                'warning': {
                    'title': 'PCR Checked',
                    'message': 'PCR has been automatically checked because age is lower than 30'
                }
            }

    @api.onchange('department_id')
    def _onchange_department(self):
        if not self.department_id:
            self.doctor_ids = [(5, 0, 0)]

    @api.constrains('department_id')
    def _check_department_opened(self):
        for record in self:
            if record.department_id and not record.department_id.is_opened:
                raise ValidationError('You cannot select a closed department')

    @api.constrains('pcr', 'cr_ratio')
    def _check_cr_ratio(self):
        for record in self:
            if record.pcr and not record.cr_ratio:
                raise ValidationError('CR Ratio is mandatory when PCR is checked')

    def write(self, vals):
        if 'state' in vals:
            old_state = self.state
            result = super(HmsPatient, self).write(vals)
            if old_state != vals['state']:
                state_labels = dict(self._fields['state'].selection)
                new_state_label = state_labels.get(vals['state'])
                self.env['hms.log.history'].create({
                    'patient_id': self.id,
                    'description': f'State changed to {new_state_label}'
                })
            return result
        return super(HmsPatient, self).write(vals)
