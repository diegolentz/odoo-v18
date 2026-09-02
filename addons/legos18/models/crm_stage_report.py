from odoo import models, fields, tools

CONFIRMADO_STAGE_ID = 6


class Legos18CrmConfirmaReport(models.Model):
    _name = 'legos18.crm.confirma.report'
    _description = 'Leads que pasaron por la etapa Confirmado'
    _auto = False
    _order = 'fecha_entrada desc'

    lead_id = fields.Many2one('crm.lead', string='Oportunidad', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Contacto', readonly=True)
    user_id = fields.Many2one('res.users', string='Comercial', readonly=True)
    referido = fields.Char(string='Referido', readonly=True)
    source_id = fields.Many2one('utm.source', string='Origen', readonly=True)
    fecha_entrada = fields.Datetime(string='Fecha de entrada a Confirmado', readonly=True)
    active = fields.Boolean(string='Activo', readonly=True)
    priority = fields.Selection([
        ('0', 'Ninguna'),
        ('1', 'Leve'),
        ('2', 'Medio'),
        ('3', 'Grave'),
    ], string='Prioridad', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'legos18_crm_confirma_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW legos18_crm_confirma_report AS (
                SELECT DISTINCT ON (msg.res_id)
                    msg.res_id          AS id,
                    msg.res_id          AS lead_id,
                    lead.partner_id     AS partner_id,
                    msg.create_uid      AS user_id,
                    lead.referred       AS referido,
                    lead.source_id      AS source_id,
                    msg.date            AS fecha_entrada,
                    lead.active         AS active,
                    lead.priority_custom AS priority
                FROM mail_tracking_value tv
                JOIN mail_message msg ON msg.id = tv.mail_message_id
                JOIN crm_lead lead    ON lead.id = msg.res_id
                WHERE msg.model = 'crm.lead'
                  AND tv.field_id = (
                      SELECT id FROM ir_model_fields
                      WHERE model = 'crm.lead' AND name = 'stage_id'
                  )
                  AND tv.new_value_integer = %s
                ORDER BY msg.res_id, msg.date ASC
            )
        """, (CONFIRMADO_STAGE_ID,))