# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CustomCrmLeads(models.Model):
    _inherit = 'crm.lead'

    name_contact_form = fields.Char(string='Nombre', tracking=True)
    celular = fields.Char(string='Celular', tracking=True)
    edad = fields.Integer(string='Edad', default=35, tracking=True)
    grado_lesion = fields.Float(string='Grado de Lesión', default=10, tracking=True)
    fractura = fields.Boolean(string='Fractura', tracking=True)
    ingreso_base = fields.Integer(string='Salario Base', tracking=True)
    coeficiente_actualizacion = fields.Float(default=1.2, tracking=True)
    salario_actualizado = fields.Float(compute="_compute_salario_actualizado", store=True, tracking=True)
    ingreso_bruto = fields.Float(compute="_compute_ingreso_bruto", store=True, tracking=True)
    tipo_accidente = fields.Selection([
        ('trabajo', 'Accidente de Trabajo'),
        ('itinere', 'In Itinere')
    ], string='Tipo de Accidente', default="trabajo", tracking=True)

    observaciones = fields.Text(string='Observaciones', tracking=True)
    fecha_accidente = fields.Date(string='Fecha Accidente', tracking=True)
    fecha_cobro = fields.Date(string='Fecha de Cobro Estimada', tracking=True)
    tipo_lesion = fields.Char(string='Tipo de Lesión', tracking=True)

    junta_medica = fields.Float(compute="_compute_junta_medica", store=True, tracking=True)
    audiencia_medica = fields.Float(compute="_compute_audiencia_medica", store=True, tracking=True)
    instancia_judicial = fields.Float(compute="_compute_instancia_judicial", store=True, tracking=True)

    prioridad_estimada = fields.Selection([
        ('0', 'Ninguna'),
        ('1', 'Leve'),
        ('2', 'Media'),
        ('3', 'Grave'),
    ], compute="_compute_prioridad", store=True, tracking=True)

    number_dots = fields.Text(compute='_compute_number_dots', tracking=True)

    fuero = fields.Selection([
        ('accidente_art', 'Accidente ART'),
        ('accidente_transito', 'Accidente Tránsito'),
        ('despido', 'Despido'),
        ('sucesion', 'Sucesión'),
        ('corporate', 'Corporativo'),
        ('otros', 'Otros')
    ], string='Fuero/Categoría', tracking=True)

    telefono_secundario = fields.Char(string='Teléfono Secundario', tracking=True)
    telefono_alternativo = fields.Char(string='Teléfono Alternativo', tracking=True)
    celular_secundario = fields.Char(string='Celular Secundario', tracking=True)
    celular_alternativo = fields.Char(string='Celular Alternativo', tracking=True)

    # redefino campos base para poder trackerarlos
    name = fields.Char(tracking=True)                                   # Nombre del lead/oportunidad
    partner_id = fields.Many2one('res.partner', tracking=True)          # Contacto
    contact_name = fields.Char(tracking=True)                           # Nombre contacto
    email_from = fields.Char(tracking=True)                             # Email
    phone = fields.Char(tracking=True)                                  # Teléfono
    mobile = fields.Char(tracking=True)                                 # Móvil
    stage_id = fields.Many2one('crm.stage', tracking=True)              # Etapa (statusbar)
    user_id = fields.Many2one('res.users', tracking=True)               # Responsable
    team_id = fields.Many2one('crm.team', tracking=True)                # Equipo de ventas
    tag_ids = fields.Many2many('crm.tag', tracking=True)                # Etiquetas
    expected_revenue = fields.Monetary(tracking=True)                   # Ingreso esperado
    probability = fields.Float(tracking=True)                           # Probabilidad
    date_deadline = fields.Date(tracking=True)                          # Fecha cierre esperada
    lost_reason_id = fields.Many2one('crm.lost.reason', tracking=True)  # Razón pérdida
    description = fields.Html(tracking=True)  
    priority_custom = fields.Selection( [ 
            ('0', 'Ninguna'), 
            ('1', 'Leve'), 
            ('2', 'Media'), 
            ('3', 'Grave'), 
        ], string='Prioridad', related='priority', store=True, readonly=False, tracking=True )

    _sql_constraints = [
        ('phone_unique', 'unique(phone)', 'El número ingresado ya existe, verifique el campo Teléfono')
    ]



    @api.depends('ingreso_base', 'coeficiente_actualizacion')
    def _compute_salario_actualizado(self):
        for record in self:
            record.salario_actualizado = record.ingreso_base * record.coeficiente_actualizacion

    @api.depends('salario_actualizado')
    def _compute_ingreso_bruto(self):
        for record in self:
            record.ingreso_bruto = record.salario_actualizado * 1.18

    @api.depends('edad', 'grado_lesion', 'salario_actualizado', 'tipo_accidente')
    def _compute_junta_medica(self):
        for record in self:
            factor = 0.012 if record.tipo_accidente == 'trabajo' else 0.01
            if record.edad > 0:
                record.junta_medica = (record.ingreso_bruto * 3445 / record.edad * record.grado_lesion * factor)
            else:
                record.junta_medica = 0.0

    @api.depends('junta_medica')
    def _compute_audiencia_medica(self):
        for record in self:
            record.audiencia_medica = record.junta_medica * 1.2

    @api.depends('edad', 'grado_lesion', 'salario_actualizado', 'tipo_accidente')
    def _compute_instancia_judicial(self):
        for record in self:
            factor = 0.012 if record.tipo_accidente == 'trabajo' else 0.01
            if record.edad > 0:
                record.instancia_judicial = (record.ingreso_bruto * 3445 / record.edad * (record.grado_lesion + 10) * factor)
            else:
                record.instancia_judicial = 0.0

    @api.depends('junta_medica')
    def _compute_number_dots(self):
        for record in self:
            record.number_dots = "{:,}".format(int(record.junta_medica)) if record.junta_medica else "0"

    @api.depends('junta_medica')
    def _compute_prioridad(self):
        for record in self:
            if record.junta_medica < 30000000:
                record.prioridad_estimada = '1'
            elif record.junta_medica < 80000000:
                record.prioridad_estimada = '2'
            else:
                record.prioridad_estimada = '3'

    def _generate_whatsapp_url(self, phone, message):
        return {
            'type': 'ir.actions.act_url',
            'url': f"https://wa.me/549{phone.replace(' ', '').replace('-', '')}?text={message}",
            'target': 'new',
            'res_id': self.id,
        }

    def mobile_whatsapp_calc(self):
        message = (
            f"Hola {self.contact_name.replace(' ', '%20')}, "
            f"me comunico de legasesor.com por una consulta que recibimos respecto a tu indemnización. "
            f"Según los datos ingresados daría ${self.number_dots} "
            f"¿Tuviste el alta ya?"
        )
        return self._generate_whatsapp_url(self.celular, message)

    def cel_wpp_calc(self):
        message = (
            f"Hola {self.contact_name.replace(' ', '%20')}, "
            f"me comunico de legasesor.com por tu consulta respecto a un accidente. "
            "¿Iniciaste el reclamo correspondiente?"
        )
        return self._generate_whatsapp_url(self.celular, message)

    def mobile_whatsapp_link(self):
        message = (
            f"Hola {self.contact_name.replace(' ', '%20')}, ¿Cómo estás? "
            "Me comunico de legasesor.com por tu consulta, "
            "¿Tenés alguna duda respecto al reclamo a realizar?"
        )
        return self._generate_whatsapp_url(self.celular, message)

    def mobile_whatsapp_consulta(self):
        message = (
            f"Hola {self.contact_name.replace(' ', '%20')}, ¿Cómo estás?"
        )
        return self._generate_whatsapp_url(self.celular, message)
