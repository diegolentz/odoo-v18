from odoo import models, fields

class PersonalExpense(models.Model):
    _name = "personal.expense"
    _description = "Personal Expense"

    name = fields.Char(required=True)
    amount = fields.Float(required=True)
    date = fields.Date(required=True)

    category_id = fields.Many2one("personal.expense.category", string="Category")