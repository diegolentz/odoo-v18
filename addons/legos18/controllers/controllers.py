# -*- coding: utf-8 -*-
# from odoo import http


# class Odoo18(http.Controller):
#     @http.route('/odoo18/odoo18', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo18/odoo18/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo18.listing', {
#             'root': '/odoo18/odoo18',
#             'objects': http.request.env['odoo18.odoo18'].search([]),
#         })

#     @http.route('/odoo18/odoo18/objects/<model("odoo18.odoo18"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo18.object', {
#             'object': obj
#         })

