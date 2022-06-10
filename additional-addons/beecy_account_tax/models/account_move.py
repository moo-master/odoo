from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Invoice/Payment Tax',
        states={'posted': [('readonly', True)]},
    )

    @api.onchange('tax_id')
    def _onchange_tax_id(self):
        for rec in self:
            for line in rec.invoice_line_ids:
                line.tax_ids = rec.tax_id
        self._onchange_invoice_discount()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_computed_taxes(self):
        self.ensure_one()

        return self.move_id.tax_id if self.move_id.tax_id else False

    @api.onchange('tax_ids')
    def _onchange_taxes(self):
        if len(self.tax_ids) > 1:
            raise ValidationError(
                _('Multiple taxes per line are resticted')
            )
