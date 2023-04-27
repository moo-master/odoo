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
                deferred = rec.order_line.filtered(lambda r:
                                                   r.tax_type == 'deferred')
                tax = rec.order_line.filtered(lambda r:
                                              r.tax_type == 'tax')
                if deferred:
                    rec.write({
                        'tax_type': 'deferred'
                    })
                elif tax:
                    rec.write({
                        'tax_type': 'tax'
                    })
                else:
                    rec.write({
                        'tax_type': 'no_tax'
                    })
            else:
                rec.write({
                    'tax_type': False
                })

    @api.model_create_multi
    def create(self, vals):
        result = super().create(vals)
        for res in result:
            deferred = res.order_line.filtered(lambda r:
                                               r.tax_type == 'deferred')
            tax = res.order_line.filtered(lambda r:
                                          r.tax_type == 'tax')
            if (tax and deferred):
                raise UserError(
                    _('Order line cannot contain with Tax and Deferred tax.'))
        return result

    def write(self, vals):
        res = super().write(vals)
        if 'order_line' in vals:
            deferred = self.order_line.filtered(lambda r:
                                                r.tax_type == 'deferred')
            tax = self.order_line.filtered(lambda r:
                                           r.tax_type == 'tax')
            if (tax and deferred):
                raise UserError(
                    _('Order line cannot contain with Tax and Deferred tax.'))
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tax_type = fields.Selection(
        string="Tax Type",
        selection=[
            ('no_tax', 'No Tax'),
            ('tax', 'Tax'),
            ('deferred', 'Deferred Tax')
        ],
        compute="_compute_tax_type"
    )

    @api.depends('tax_id')
    def _compute_tax_type(self):
        for rec in self:
            if rec.tax_id.tax_exigibility == 'on_payment':
                rec.write({
                    'tax_type': 'deferred'
                })
            elif rec.tax_id.is_exempt or not rec.tax_id:
                rec.write({
                    'tax_type': 'no_tax'
                })
            else:
                rec.write({
                    'tax_type': 'tax'
                })

    def _prepare_invoice_line(self, **optional_values):
        res = super(
            SaleOrderLine,
            self)._prepare_invoice_line(
            **optional_values)
        order = self.order_id
        if order.x_is_interface and order.invoice_count > 0 and order.so_type_id.is_unearn_revenue:
            res['account_id'] = order.so_type_id.x_revenue_account_id
        return res
