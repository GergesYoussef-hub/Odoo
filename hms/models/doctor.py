from odoo import models, fields


class HmsDoctor(models.Model):
    _name = 'hms.doctor'
    _description = 'Hospital Doctor'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    image = fields.Binary(string='Image')
    patient_ids = fields.Many2many('hms.patient', string='Patients')
