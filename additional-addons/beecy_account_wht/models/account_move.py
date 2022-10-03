from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_wht = fields.Float(
        string='Amount WHT',
        store=True,
        compute='_compute_wht_amount',
    )

    amount_wht_signed = fields.Float(
        string='Amount WHT Signed',
        store=True,
        compute='_compute_wht_amount',
    )

    @api.depends('invoice_line_ids.amount_wht',
                 'amount_total_signed', 'amount_wht')
    def _compute_wht_amount(self):
        for rec in self:
            total_wht = 0 if hasattr(
                rec, 'beecy_payment_id') and rec.beecy_payment_id.state == "paid" else sum(
                rec.invoice_line_ids.mapped(
                    lambda v: rec.currency_id.round(
                        v.amount_wht)))
            rec.write({
                'amount_wht': total_wht,
                'amount_wht_signed': -total_wht if rec.amount_total_signed < 0
                else total_wht,
            })

    @api.model_create_multi
    def create(self, vals_list):
        # force set invoice line values
        vals_list = [self.map_invoice_line(rec) for rec in vals_list]
        res = super(AccountMove, self).create(vals_list)
        return res

    def write(self, vals):
        vals = self.map_invoice_line(vals)
        res = super(AccountMove, self).write(vals)
        return res

    def map_invoice_line(self, vals_list):
        BUSINESS_FIELDS = ['wht_type_id']
        for line in vals_list.get('line_ids') or []:
            for invoice_line in vals_list.get('invoice_line_ids') or []:
                for field in BUSINESS_FIELDS:
                    if(line[1] in invoice_line and invoice_line[2]
                            and field in invoice_line[2]):
                        line[2][field] = invoice_line[2][field]
        return vals_list

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            section_5_list = []
            section_6_list = []
            for line in rec.invoice_line_ids:
                if (line.wht_type_id.sequence in [
                        5, 500] and line.wht_type_id.id not in section_5_list):
                    section_5_list.append(line.wht_type_id.id)
                if (line.wht_type_id.sequence in [
                        6, 600] and line.wht_type_id.id not in section_6_list):
                    section_6_list.append(line.wht_type_id.id)
            if 1 < len(section_5_list) or 1 < len(section_6_list):
                raise ValidationError(
                    _("You can not select different WHT under the same category."
                      " Right now your section 5 or section 6"
                      " are under the same category."))
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    wht_type_id = fields.Many2one(
        string='WHT',
        comodel_name='account.wht.type',
        ondelete='cascade'
    )

    amount_wht = fields.Float(
        string='Amount WHT',
        store=True,
        compute='_compute_wht_amount',
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        super()._onchange_product_id()
        for move in self:
            if move.move_id.move_type == 'in_invoice':
                move.wht_type_id = move.product_id.wht_type_id.id
            if (move.move_id.move_type == 'out_invoice'
                    and move.move_id.partner_id.company_type == 'company'):
                move.wht_type_id = move.product_id.wht_type_id.id

    @api.depends('price_subtotal', 'wht_type_id')
    def _compute_wht_amount(self):
        for rec in self:
            rec.amount_wht = rec.wht_type_id.wht_calculator(rec.price_subtotal)
