from odoo import models, fields


class AccountPaymentMethodLine(models.Model):
    _inherit = 'account.payment.method.line'

    payment_account_id = fields.Many2one(
        domain=lambda self: "[('deprecated', '=', False),"
        "('company_id', '=', company_id),"
        "('user_type_id.type', 'not in', ('receivable', 'payable'))]"
    )
