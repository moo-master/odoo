from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_approve_send = fields.Boolean(
        string='is_approve_send',
        invisible=True,
    )

    def button_confirm(self):
        pass
