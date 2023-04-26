from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tax_type = fields.Selection(
        string="Tax Type",
        selection=[
            ('no_tax', 'No Tax'),
            ('tax', 'Tax'),
            ('deferred', 'Deferred Tax')
        ],
        compute="_compute_tax_type"
    )

    @api.depends('order_line.tax_id')
    def _compute_tax_type(self):
        for rec in self:
            if rec.order_line:
                if not rec.order_line[0].tax_id:
                    rec.write({
                        'tax_type': 'no_tax'
                    })
                elif rec.order_line[0].tax_id.is_exempt:
                    rec.write({
                        'tax_type': 'deferred'
                    })
                else:
                    rec.write({
                        'tax_type': 'tax'
                    })
            else:
                rec.write({
                    'tax_type': False
                })

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        taxs = res.order_line.mapped('tax_id')
        null_taxs = self.env['sale.order.line']
        for line in res.order_line:
            if not line.tax_id and not line.display_type:
                null_taxs = line
                break
        if (taxs and null_taxs) or (len(taxs) > 1):
            raise UserError(_('Tax must be one and only one.'))
        return res

    def write(self, vals):
        res = super().write(vals)
        if 'order_line' in vals:
            taxs = self.order_line.mapped('tax_id')
            null_taxs = self.env['sale.order.line']
            for line in self.order_line:
                if not line.tax_id and not line.display_type:
                    null_taxs = line
                    break
            if (taxs and null_taxs) or (len(taxs) > 1):
                raise UserError(_('Tax must be one and only one.'))
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        res = super(
            SaleOrderLine,
            self)._prepare_invoice_line(
            **optional_values)
        order = self.order_id
        if order.x_is_interface and order.invoice_count > 0 and order.so_type_id.is_unearn_revenue:
            res['account_id'] = order.so_type_id.x_revenue_account_id
        return res
