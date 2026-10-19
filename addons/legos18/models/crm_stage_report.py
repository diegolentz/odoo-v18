from odoo import models, fields, tools

CONFIRMADO_STAGE_ID = 6


class Legos18CrmConfirmaReport(models.Model):
    _name = 'legos18.crm.confirma.report'
    _description = 'Leads que pasaron por la etapa Confirmado'
    _auto = False
    _order = 'fecha_entrada desc'

    lead_id = fields.Many2one('crm.lead', string='Oportunidad', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Contacto')
    user_id = fields.Many2one('res.users', string='Comercial')
    referido = fields.Char(string='Referido')
    source_id = fields.Many2one('utm.source', string='Origen')
    fecha_entrada = fields.Datetime(string='Fecha de entrada a Confirmado', readonly=True)
    active = fields.Boolean(string='Activo')
    priority = fields.Selection([
        ('0', 'Ninguna'),
        ('1', 'Leve'),
        ('2', 'Medio'),
        ('3', 'Grave'),
    ], string='Prioridad')

    def write(self, vals):
        """
        Este modelo es una SQL VIEW, por lo que no se escribe
        directamente sobre la vista.

        Los cambios se aplican sobre el crm.lead correspondiente.
        """

        lead_vals = {}

        # Campos que tienen el mismo nombre en crm.lead
        if 'partner_id' in vals:
            lead_vals['partner_id'] = vals['partner_id']

        if 'user_id' in vals:
            lead_vals['user_id'] = vals['user_id']

        if 'source_id' in vals:
            lead_vals['source_id'] = vals['source_id']

        if 'active' in vals:
            lead_vals['active'] = vals['active']

        if 'priority' in vals:
            lead_vals['priority'] = vals['priority']

        # En el informe se llama "referido",
        # pero en crm.lead se llama "referred"
        if 'referido' in vals:
            lead_vals['referred'] = vals['referido']

        if lead_vals:
            leads = self.env['crm.lead'].browse(self.ids)
            leads.write(lead_vals)

        return True

        return True

    def init(self):
        tools.drop_view_if_exists(
            self._cr,
            'legos18_crm_confirma_report'
        )

        self._cr.execute("""
            CREATE OR REPLACE VIEW legos18_crm_confirma_report AS (
                SELECT DISTINCT ON (msg.res_id)
                    msg.res_id          AS id,
                    msg.res_id          AS lead_id,
                    lead.partner_id     AS partner_id,
                    lead.user_id        AS user_id,
                    lead.referred       AS referido,
                    lead.source_id      AS source_id,
                    msg.date            AS fecha_entrada,
                    lead.active         AS active,
                    lead.priority       AS priority
                FROM mail_tracking_value tv
                JOIN mail_message msg ON msg.id = tv.mail_message_id
                JOIN crm_lead lead    ON lead.id = msg.res_id
                WHERE msg.model = 'crm.lead'
                  AND tv.field_id = (
                      SELECT id
                      FROM ir_model_fields
                      WHERE model = 'crm.lead'
                        AND name = 'stage_id'
                  )
                  AND tv.new_value_integer = %s
                ORDER BY msg.res_id, msg.date ASC
            )
        """, (CONFIRMADO_STAGE_ID,))