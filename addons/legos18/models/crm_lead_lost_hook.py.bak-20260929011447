# -*- coding: utf-8 -*-
import logging

import requests

from odoo import models

_logger = logging.getLogger(__name__)

# URL del webhook de n8n que escucha los leads marcados como perdidos.
# TODO: reemplazar por la URL real cuando esté disponible.
N8N_LEAD_LOST_WEBHOOK_URL = "https://www.ejemplo.com"


class CrmLeadLostHook(models.TransientModel):
    """Hereda el wizard de 'Marcar como perdido' para notificar a n8n."""
    _inherit = 'crm.lead.lost'

    def action_lost_reason_apply(self):
        # Ejecuta primero la lógica original de Odoo (marca los leads como
        # perdidos, aplica el lost_reason_id y registra la nota en el chatter).
        res = super().action_lost_reason_apply()
        self._notify_n8n_lead_lost()
        return res

    def _notify_n8n_lead_lost(self):
        """Envía a n8n el/los lead(s) perdidos, quién los marcó y el motivo."""
        payload = []
        for lead in self.lead_ids:
            payload.append({
                "lead_id": lead.id,
                "lead_name": lead.name,
                "lost_by_user_id": self.env.user.id,
                "lost_by_user_name": self.env.user.name,
                "lost_reason_id": self.lost_reason_id.id if self.lost_reason_id else None,
                "lost_reason_name": self.lost_reason_id.name if self.lost_reason_id else None,
                "closing_note": self.lost_feedback or "",
            })

        if not payload:
            return

        try:
            requests.post(N8N_LEAD_LOST_WEBHOOK_URL, json=payload, timeout=5)
        except Exception as e:
            _logger.error("Error al enviar datos de lead perdido a n8n: %s", e)
