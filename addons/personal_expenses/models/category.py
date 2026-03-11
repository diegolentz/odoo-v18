from odoo import models, fields

class PersonalExpenseCategory(models.Model):
    _name = "personal.expense.category"
    _description = "Personal Expense Category"

    name = fields.Char(required=True)
    expense_ids = fields.One2many("personal.expense", "category_id", string="Expenses")