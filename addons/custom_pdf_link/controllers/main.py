# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import base64


class SignPdfController(http.Controller):

    @http.route('/sign_pdf/generate_link', type='json', auth='user', methods=['POST'])
    def generate_sign_link(self, attachment_id, **kwargs):
        attachment = request.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            return {'error': 'Attachment not found'}

        # Crear o reutilizar sign request existente
        sign_req = request.env['custom_pdf_link.sign_request'].search([
            ('attachment_id', '=', attachment.id),
            ('state', '=', 'pending'),
        ], limit=1)
        if not sign_req:
            sign_req = request.env['custom_pdf_link.sign_request'].create({
                'attachment_id': attachment.id,
            })

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f"{base_url}/sign/document/{sign_req.token}"
        return {'url': url}

    @http.route('/sign/document/<string:token>', type='http', auth='public', website=False)
    def sign_page(self, token, **kwargs):
        sign_req = request.env['custom_pdf_link.sign_request'].sudo().search([
            ('token', '=', token),
        ], limit=1)
        if not sign_req:
            return request.not_found()

        attachment = sign_req.attachment_id
        access_tokens = attachment.sudo().generate_access_token()
        pdf_url = f"/web/content/{attachment.id}?access_token={access_tokens[0]}"

        return request.render('custom_pdf_link.sign_page_template', {
            'sign_req': sign_req,
            'pdf_url': pdf_url,
            'token': token,
        })

    @http.route('/sign/document/<string:token>/submit', type='json', auth='public', methods=['POST'])
    def sign_submit(self, token, signature=None, **kwargs):
        sign_req = request.env['custom_pdf_link.sign_request'].sudo().search([
            ('token', '=', token),
            ('state', '=', 'pending'),
        ], limit=1)
        if not sign_req:
            return {'error': 'No encontrado o ya firmado'}
        if not signature:
            return {'error': 'Firma vacía'}

        # Quitar prefijo data URL si existe
        if ',' in signature:
            signature = signature.split(',')[1]

        sign_req.write({
            'signature': signature,
            'signed_date': fields.Datetime.now(),
            'state': 'signed',
        })

        # Publicar mensaje en el chatter del registro relacionado
        attachment = sign_req.attachment_id
        if attachment.res_model and attachment.res_id:
            try:
                record = request.env[attachment.res_model].sudo().browse(attachment.res_id)
                if record.exists() and hasattr(record, 'message_post'):
                    # Adjuntar imagen de firma como attachment del mensaje
                    sign_attachment = request.env['ir.attachment'].sudo().create({
                        'name': 'firma.png',
                        'type': 'binary',
                        'datas': signature,
                        'mimetype': 'image/png',
                    })
                    record.message_post(
                        body=f'✅ <b>Documento firmado:</b> {attachment.name}<br/>'
                             f'<img src="/web/image/{sign_attachment.id}" style="max-width:300px;border:1px solid #ccc;border-radius:4px;margin-top:8px"/>',
                        subject='Documento firmado electrónicamente',
                        attachment_ids=[sign_attachment.id],
                    )
            except Exception:
                pass  # No interrumpir el flujo si el chatter falla

        return {'success': True}