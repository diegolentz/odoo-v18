# -*- coding: utf-8 -*-
import logging
import threading
from datetime import datetime, timedelta

import pytz
import requests

from odoo import models

_logger = logging.getLogger(__name__)

# etapa (crm.stage.id) -> webhook de n8n que arma la actividad de esa etapa.
# Para sumar una etapa (Citado, Iniciado...) se agrega una línea acá.
# Las etapas que no están en el dict no generan ningún request.
STAGE_WEBHOOKS = {
    # 3 (Interesado): workflow LEGASESOR_NUEVOS INTERESADOS
    3: "https://n8n.apps.confortm.com/webhook/legasesor-lead-interesado",
    # 4 (Iniciado): workflow LEGASESOR_NUEVOS INICIADOS
    4: "https://n8n.apps.confortm.com/webhook/legasesor-lead-iniciado",
    # 5 (Citado): workflow LEGASESOR_NUEVOS CITADOS
    5: "https://n8n.apps.confortm.com/webhook/legasesor-lead-citado",
    # 6 (Confirmado): workflow LEGASESOR_NUEVOS CONFIRMADOS
    6: "https://n8n.apps.confortm.com/webhook/legasesor-lead-confirmado",
}

# Actividades automáticas por etapa (mail.activity.type.id). Al salir el lead de
# una etapa, o al perderse, se cancelan las abiertas de las demás etapas para
# que no se envíe un mensaje viejo ni se pisen entre sí.
STAGE_ACTIVITY_TYPES = {
    3: 15,  # Contactar Interesado
    4: 17,  # Contactar Iniciado
    5: 16,  # Contactar Citado
    6: 13,  # Contactar Confirmado
}

# Al pasar a Contactado se crea una actividad de Llamada para el comercial.
STAGE_CONTACTADO = 2
LLAMADA_RESUMEN = 'Llamar (pasó a Contactado)'
LLAMADA_DIAS = 2                 # vence a 2 días del cambio de etapa...
LLAMADA_DIAS_HABILES = (0, 1, 2, 3)  # ...corrido al próximo lunes-jueves (weekday 0=lunes)
LLAMADA_TZ = 'America/Argentina/Buenos_Aires'


def _post(url, payload):
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        _logger.error("Error al avisar a n8n del cambio de etapa (%s): %s", url, e)


class CrmLeadStageHook(models.Model):
    """Reacciona en el momento a los cambios de etapa de un lead.

    - Avisa a n8n cuando entra a una etapa con mensaje automático.
    - Crea la actividad de Llamada al entrar a Contactado.
    - Cancela las actividades automáticas pendientes de la etapa que deja, o
      todas si el lead se archiva (p. ej. al marcarlo como perdido).
    """
    _inherit = 'crm.lead'

    def write(self, vals):
        archivando = vals.get('active') is False
        if 'stage_id' not in vals and not archivando:
            return super().write(vals)

        if archivando:
            # Antes del super(): Odoo archiva las actividades del registro al
            # archivarlo, y ya no las encontraríamos abiertas para cancelarlas.
            self._cancelar_actividades_automaticas(self)

        anteriores = {lead.id: lead.stage_id.id for lead in self}
        res = super().write(vals)
        if 'stage_id' not in vals:
            return res

        cambiados = self.filtered(lambda l: l.stage_id.id != anteriores.get(l.id))
        if cambiados:
            self._cancelar_actividades_automaticas(cambiados, mantener_etapa=cambiados[0].stage_id.id)

        self._crear_llamada_contactado(
            self.filtered(lambda l: l.stage_id.id == STAGE_CONTACTADO
                          and anteriores.get(l.id) != STAGE_CONTACTADO))

        por_url = {}
        for lead in self:
            url = STAGE_WEBHOOKS.get(lead.stage_id.id)
            if url and lead.stage_id.id != anteriores.get(lead.id):
                por_url.setdefault(url, []).append({
                    "lead_id": lead.id,
                    "stage_id": lead.stage_id.id,
                    "stage_anterior_id": anteriores.get(lead.id),
                    "user_id": lead.user_id.id or None,
                })

        for url, payload in por_url.items():
            # Después del commit: un rollback no dispara mensajes, y n8n
            # encuentra el cambio ya guardado. En un hilo aparte para que un
            # n8n lento o caído nunca demore la respuesta al usuario. Un solo
            # request por lote aunque se muevan muchos leads a la vez.
            self.env.cr.postcommit.add(
                lambda url=url, payload=payload: threading.Thread(
                    target=_post, args=(url, payload), daemon=True).start()
            )
        return res

    def _cancelar_actividades_automaticas(self, leads, mantener_etapa=None):
        """Cierra (con nota) las actividades automáticas abiertas de `leads`.

        mantener_etapa: etapa a la que entra el lead; su actividad automática
        no se toca (la crea/gestiona el flujo de esa etapa). Sin ese argumento
        se cancelan todas (lead archivado o perdido).
        Un fallo acá nunca debe impedir el cambio: va al log.
        """
        try:
            with self.env.cr.savepoint():
                tipos = {t for etapa, t in STAGE_ACTIVITY_TYPES.items() if etapa != mantener_etapa}
                domain = ['&', ('res_model', '=', 'crm.lead'), ('res_id', 'in', leads.ids)]
                condiciones = [[('activity_type_id', 'in', list(tipos))]]
                llamada = self.env.ref('mail.mail_activity_data_call', raise_if_not_found=False)
                if llamada and mantener_etapa != STAGE_CONTACTADO:
                    # Solo las llamadas que creó este flujo, no las que agende un comercial a mano.
                    condiciones.append(['&', ('activity_type_id', '=', llamada.id),
                                        ('summary', '=', LLAMADA_RESUMEN)])
                filtro = condiciones[0] if len(condiciones) == 1 else ['|'] + condiciones[0] + condiciones[1]
                actividades = self.env['mail.activity'].sudo().search(domain + filtro)
                if actividades:
                    actividades.with_context(mail_activity_quick_update=True).action_feedback(
                        feedback='Cancelada: el lead cambió de etapa o se archivó')
        except Exception as e:
            _logger.error("No se pudieron cancelar las actividades automáticas: %s", e)

    def _crear_llamada_contactado(self, leads):
        """Actividad de Llamada para los leads que acaban de pasar a Contactado.

        Se crea en la misma transacción del cambio de etapa (si se revierte, se
        revierte también) y en un solo create para todo el lote. Sin comercial
        asignado queda a nombre de quien hizo el cambio (Odoo exige responsable).
        Un fallo acá nunca debe impedir el cambio de etapa: va al log.
        """
        if not leads:
            return
        tipo = self.env.ref('mail.mail_activity_data_call', raise_if_not_found=False)
        if not tipo:
            _logger.warning("No existe el tipo de actividad Llamada: no se crea la llamada de Contactado")
            return
        try:
            with self.env.cr.savepoint():
                # No duplicar si el lead ya tiene una llamada abierta (idas y vueltas de etapa).
                abiertas = set(self.env['mail.activity'].search([
                    ('res_model', '=', 'crm.lead'),
                    ('res_id', 'in', leads.ids),
                    ('activity_type_id', '=', tipo.id),
                ]).mapped('res_id'))
                hoy = datetime.now(pytz.timezone(LLAMADA_TZ)).date()
                vence = hoy + timedelta(days=LLAMADA_DIAS)
                while vence.weekday() not in LLAMADA_DIAS_HABILES:
                    vence += timedelta(days=1)
                modelo = self.env['ir.model']._get_id('crm.lead')
                vals = [{
                    'res_model_id': modelo,
                    'res_id': lead.id,
                    'activity_type_id': tipo.id,
                    'summary': LLAMADA_RESUMEN,
                    'date_deadline': vence,
                    'user_id': lead.user_id.id or self.env.user.id,
                } for lead in leads if lead.id not in abiertas]
                if vals:
                    # quick_update: sin mail de "te asignaron una actividad" por cada lead.
                    self.env['mail.activity'].with_context(mail_activity_quick_update=True).create(vals)
        except Exception as e:
            _logger.error("No se pudo crear la llamada de Contactado: %s", e)
