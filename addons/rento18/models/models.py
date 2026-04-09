from odoo import models, fields, api
from datetime import timedelta

class CustomCrmLeads(models.Model):
    _inherit = 'crm.lead'
    
    tipo_servicio = fields.Selection([
        ('volquete', 'Volquete'),
        ('volquetin', 'Volquetín'),
        ('instalacion_aa', 'Instalación AA'),
        ('hidrogrua', 'Hidrogrúa'),
        ('andamios', 'Andamios'),
        ('otros', 'Otros')
    ], string="Tipo de Servicio", required=True)
    
    celular = fields.Char(string="Celular")
    direccion = fields.Char(string="Dirección")
    entrecalle = fields.Char(string="Entre Calle")
    barrio = fields.Char(string="Barrio")
    
    metodo_pago = fields.Selection([
        ('transferencia', 'Transferencia'),
        ('efectivo', 'Efectivo'),
        ('otros', 'Otros')
    ], string="Método de Pago", required=True)
    
    pago_realizado = fields.Boolean(string="Pago Realizado")
    fecha_entrega = fields.Date(string="Fecha de Entrega")
    fecha_retiro = fields.Date(string="Fecha de Retiro")
    se_retiro = fields.Boolean(string="Se Retiró")
    detalles = fields.Text(string="Detalles")



    def _generate_whatsapp_url(self, celular, message):
            return {
                'type': 'ir.actions.act_url',
                'url': f"https://wa.me/549{celular.replace(' ', '').replace('-', '')}?text={message}",
                'target': 'new',
                'res_id': self.id,
            }

    def mobile_whatsapp_link(self):
        self.ensure_one()
        nombre = self.contact_name or "Cliente"
        message = (
            f"Hola {nombre.replace(' ', '%20')}, ¿Cómo estás? "
            "Me comunico de Rento por un servicio solicitado. "
        )
        return self._generate_whatsapp_url(self.celular, message)

    def cel_wpp_cobro(self):
        self.ensure_one()
        nombre = self.contact_name or "Cliente"
        message = (
            f"Hola {nombre.replace(' ', '%20')}, un gusto saludarte "
            "me comunico de Rento por un servicio pendiente de pago. "
        )
        return self._generate_whatsapp_url(self.celular, message)

    @api.onchange('fecha_entrega')
    def _onchange_fecha_entrega(self):
        print("escucho")
        if self.fecha_entrega:
            self.fecha_retiro = self.fecha_entrega + timedelta(days=2)
        else:
            self.fecha_retiro = False


