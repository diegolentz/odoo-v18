# -*- coding: utf-8 -*-
# from odoo import http


# class PersonalExpenses(http.Controller):
#     @http.route('/personal_expenses/personal_expenses', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/personal_expenses/personal_expenses/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('personal_expenses.listing', {
#             'root': '/personal_expenses/personal_expenses',
#             'objects': http.request.env['personal_expenses.personal_expenses'].search([]),
#         })

#     @http.route('/personal_expenses/personal_expenses/objects/<model("personal_expenses.personal_expenses"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('personal_expenses.object', {
#             'object': obj
#         })

