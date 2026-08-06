# -*- coding: utf-8 -*-
from odoo import models, fields, tools


class Legos18CrmStageMov(models.Model):
    _name = 'legos18.crm.stage.mov'
    _description = 'Movimientos de etapa en leads CRM'
    _auto = False
    _order = 'fecha desc'

    lead_id = fields.Many2one('crm.lead', string='Lead', readonly=True)
    user_id = fields.Many2one('res.users', string='Usuario', readonly=True)
    stage_to_id = fields.Integer(string='ID Etapa Destino', readonly=True)
    stage_to_name = fields.Char(string='Etapa Destino', readonly=True)
    fecha = fields.Datetime(string='Fecha', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'legos18_crm_stage_mov')
        self._cr.execute("""
            CREATE OR REPLACE VIEW legos18_crm_stage_mov AS (
                SELECT
                    tv.id                AS id,
                    msg.res_id           AS lead_id,
                    msg.create_uid       AS user_id,
                    tv.new_value_integer AS stage_to_id,
                    tv.new_value_char    AS stage_to_name,
                    msg.date             AS fecha
                FROM mail_tracking_value tv
                JOIN mail_message msg ON msg.id = tv.mail_message_id
                WHERE msg.model = 'crm.lead'
                  AND tv.field_id = (
                      SELECT id FROM ir_model_fields
                      WHERE model = 'crm.lead' AND name = 'stage_id'
                      LIMIT 1
                  )
            )
        """)
