from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class Customers(models.Model):
    _inherit = 'res.partner'

    related_patient_id = fields.Many2one('hms.patient', string='Related Patient')

    @api.constrains('email', 'related_patient_id')
    def _check_email_patient(self):
        for record in self:
            if record.email and record.related_patient_id:
                patient = self.env['hms.patient'].search([
                    ('email', '=', record.email),
                    ('id', '!=', record.related_patient_id.id)
                ], limit=1)
                if patient:
                    raise ValidationError('This email already exists in patient records')

    def unlink(self):
        for record in self:
            if record.related_patient_id:
                raise UserError('Cannot delete a customer linked to a patient')
        return super(Customers, self).unlink()
