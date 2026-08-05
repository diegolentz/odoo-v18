# models/crm_lead_mass_convert_chunked.py
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

CHUNK_SIZE = 10


class CrmLead2opportunityPartnerMass(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner.mass'

    def action_mass_convert(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids', [])

        # Si son pocos, no hace falta trocear: comportamiento original.
        if len(active_ids) <= CHUNK_SIZE:
            return super().action_mass_convert()

        _logger.info(
            "Mass convert: %s leads, procesando en chunks de %s",
            len(active_ids), CHUNK_SIZE
        )

        result = None
        for i in range(0, len(active_ids), CHUNK_SIZE):
            chunk_ids = active_ids[i:i + CHUNK_SIZE]
            _logger.info("Procesando chunk %s-%s de %s", i, i + len(chunk_ids), len(active_ids))

            # Reconstruimos el wizard con el subconjunto de leads en el contexto
            # y sobre lead_tomerge_ids, que es lo que usa la lógica de dedupe.
            wizard_chunk = self.with_context(active_ids=chunk_ids)
            wizard_chunk.lead_tomerge_ids = [(6, 0, chunk_ids)]

            result = super(CrmLead2opportunityPartnerMass, wizard_chunk).action_mass_convert()

            # Commit intermedio: libera la transacción y evita que un
            # timeout tire abajo TODO el trabajo ya hecho.
            self.env.cr.commit()

        return result