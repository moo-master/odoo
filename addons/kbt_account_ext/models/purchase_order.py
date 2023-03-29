from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tax_type = fields.Selection(
        string="Tax Type",
        selection=[
            ('no_tax', 'No Tax'),
            ('tax', 'Tax'),
            ('deferred', 'Deferred Tax')
        ],
        compute="_compute_tax_type"
    )

    @api.depends('order_line.taxes_id')
    def _compute_tax_type(self):
        for rec in self:
            if not rec.order_line[0].taxes_id:
                rec.write({
                    'tax_type': 'no_tax'
                })
            elif rec.order_line[0].taxes_id.tax_exigibility == 'on_payment':
                rec.write({
                    'tax_type': 'deferred'
                })
            else:
                rec.write({
                    'tax_type': 'tax'
                })

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        taxs = res.order_line.mapped('taxes_id')
        null_taxs = self.env['purchase.order.line']
        for line in res.order_line:
            if not line.taxes_id:
                null_taxs = line
                break
        if (taxs and null_taxs) or (len(taxs) > 1):
            raise UserError(_('Tax must be one and only one.'))
        return res

    def write(self, vals):
        res = super().write(vals)
        if 'order_line' in vals:
            taxs = self.order_line.mapped('taxes_id')
            null_taxs = self.env['purchase.order.line']
            for line in self.order_line:
                if not line.taxes_id:
                    null_taxs = line
                    break
            if (taxs and null_taxs) or (len(taxs) > 1):
                raise UserError(_('Tax must be one and only one.'))
        return res
