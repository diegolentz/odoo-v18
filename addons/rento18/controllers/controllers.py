# -*- coding: utf-8 -*-
# from odoo import http


# class Rento18(http.Controller):
#     @http.route('/rento18/rento18', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rento18/rento18/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rento18.listing', {
#             'root': '/rento18/rento18',
#             'objects': http.request.env['rento18.rento18'].search([]),
#         })

#     @http.route('/rento18/rento18/objects/<model("rento18.rento18"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rento18.object', {
#             'object': obj
#         })

