from odoo import models, fields


class TempJournalItem(models.Model):
    _name = 'temp.journal.item'
    _description = 'Temp Journal Item'

    account_id = fields.Many2one(
        comodel_name='account.account',
        string='account',
    )

    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoices'
    )

    is_wht = fields.Boolean(
        'is_wht'
    )

    name = fields.Char(
        string='Name'
    )

    debit = fields.Float(
        string='Debit'
    )

    credit = fields.Float(
        string='Credit'
    )

    payment_id = fields.Many2one(
        comodel_name='beecy.account.payment',
        string='Payment',
    )
