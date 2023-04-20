from odoo import models, fields


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    payment_term_code = fields.Char('Payment Term Code')
