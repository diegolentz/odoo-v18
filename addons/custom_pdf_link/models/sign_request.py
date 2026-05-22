# -*- coding: utf-8 -*-
import secrets
from odoo import models, fields


class SignRequest(models.Model):
    _name = 'custom_pdf_link.sign_request'
    _description = 'Sign Request'

    attachment_id = fields.Many2one('ir.attachment', string='Adjunto', required=True, ondelete='cascade')
    token = fields.Char(default=lambda self: secrets.token_urlsafe(32), readonly=True, copy=False)
    signature = fields.Binary('Imagen de Firma')
    signed_date = fields.Datetime('Fecha de Firma', readonly=True)
    state = fields.Selection([('pending', 'Pendiente'), ('signed', 'Firmado')], default='pending', readonly=True)
    res_model = fields.Char('Modelo relacionado')
    res_id = fields.Integer('ID de registro')
