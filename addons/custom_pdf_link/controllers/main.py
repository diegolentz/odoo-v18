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
            'state': 'aclaracion_pending',
        })

        return {'next_step': 'aclaracion'}

    @http.route('/sign/document/<string:token>/aclaracion', type='json', auth='public', methods=['POST'])
    def sign_aclaracion(self, token, aclaracion=None, **kwargs):
        sign_req = request.env['custom_pdf_link.sign_request'].sudo().search([
            ('token', '=', token),
            ('state', '=', 'aclaracion_pending'),
        ], limit=1)
        if not sign_req:
            return {'error': 'No encontrado o estado inválido'}
        if not aclaracion:
            return {'error': 'La aclaración no puede estar vacía'}

        # Quitar prefijo data URL si existe
        if ',' in aclaracion:
            aclaracion = aclaracion.split(',')[1]

        sign_req.write({
            'aclaracion': aclaracion,
            'state': 'signed',
        })

        # Publicar mensaje en el chatter con firma y aclaración
        attachment = sign_req.attachment_id
        if attachment.res_model and attachment.res_id:
            try:
                record = request.env[attachment.res_model].sudo().browse(attachment.res_id)
                if record.exists() and hasattr(record, 'message_post'):
                    firma_att = request.env['ir.attachment'].sudo().create({
                        'name': 'firma.png',
                        'type': 'binary',
                        'datas': sign_req.signature,
                        'mimetype': 'image/png',
                    })
                    aclaracion_att = request.env['ir.attachment'].sudo().create({
                        'name': 'aclaracion.png',
                        'type': 'binary',
                        'datas': aclaracion,
                        'mimetype': 'image/png',
                    })
                    record.message_post(
                        body=f'✅ Documento firmado: {attachment.name}',
                        subject='Documento firmado electrónicamente',
                        attachment_ids=[firma_att.id, aclaracion_att.id],
                    )
            except Exception:
                pass

        return {'success': True}