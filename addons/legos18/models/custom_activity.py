from odoo import models, fields, api

class MailActivity(models.Model):
    _inherit = "mail.activity"

    telefono_cliente = fields.Char(
        string="Celular Cliente",
        compute="_compute_telefono_cliente",
        store=False
    )

    @api.depends("res_id", "res_model")
    def _compute_telefono_cliente(self):
        for rec in self:
            rec.telefono_cliente = False

            if rec.res_model == "crm.lead" and rec.res_id:
                lead = self.env["crm.lead"].browse(rec.res_id)
                rec.telefono_cliente = lead.celular or False