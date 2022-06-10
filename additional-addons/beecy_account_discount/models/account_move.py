from functools import reduce

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    formula_discount = fields.Char(
        string='Disc. %',
    )

    direct_discount = fields.Float(
        string='Disc. Amount',
        digits='Discount',
        default=0
    )
    amount_before_global_discount = fields.Monetary(
        string='Amount Before Global Disc.',
        currency_field='company_currency_id',
        compute='_compute_amount',
        store=True,
    )

    @api.depends('line_ids')
    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        for move in self:
            move.amount_before_global_discount = sum(
                line_id.price_subtotal_wo_prorated
                for line_id in move.invoice_line_ids
            )
        return res

    @api.model
    def _get_price_discount_model(self, price_unit=0.0, formula=''):
        return reduce(
            lambda x, y: x * y,
            [price_unit] + self._get_ordered_factor(formula=formula)
        )

    @api.model
    def _get_price_wo_discount_model(self, price_unit=0.0, formula=''):
        return reduce(
            lambda x, y: x / y,
            [price_unit] + self._get_ordered_factor(formula=formula)
        )

    @staticmethod
    def _get_ordered_factor(formula):
        def _isfloat(num_str):
            try:
                float(num_str)
                return True
            except ValueError:
                return False

        formula = str(formula) if formula else ''

        return [
            1 - (j * 0.01)
            for j in map(
                float, filter(
                    _isfloat, ",".join(
                        formula.replace('%', ' ').split('+')
                    ).split(',')
                )
            )
            if j < 100
        ]

    @api.onchange('formula_discount', 'direct_discount', 'amount_untaxed')
    def _onchange_discount(self):
        self.line_ids._compute_prorated_discount()
        self.invoice_line_ids._onchange_price_subtotal()
        for line in self.line_ids:
            line._onchange_mark_recompute_taxes()
        self._recompute_dynamic_lines()

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        super(AccountMove, self)._onchange_invoice_line_ids()
        self._onchange_invoice_discount()

    def _onchange_invoice_discount(self):
        for rec in self:
            formula_discount = rec.formula_discount
            direct_discount = rec.direct_discount

            rec.update({
                'formula_discount': '',
                'direct_discount': 0.0
            })
            rec._onchange_discount()

            rec.update({
                'formula_discount': formula_discount,
                'direct_discount': direct_discount
            })
            rec._onchange_discount()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    formula_discount = fields.Char(
        string='Disc. %',
    )

    direct_discount = fields.Float(
        string='Disc. Amount',
        digits='Discount',
        default=0
    )

    price_unit_discount = fields.Float(
        compute="_compute_price_unit_discount",
        digits='Price Unit Discount',
    )

    prorated_discount = fields.Float(
        digits='Price Unit Discount',
        default=0.0
    )

    price_subtotal_wo_prorated = fields.Monetary(
        string='Subtotal before prorated discount',
        compute="_compute_price_subtotal_wo_prorated",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    @api.onchange(
        'quantity', 'price_unit', 'tax_ids',
        'formula_discount', 'direct_discount'
    )
    def _onchange_price_subtotal(self):
        super(AccountMoveLine, self)._onchange_price_subtotal()

    @api.depends('price_unit', 'formula_discount')
    def _compute_price_unit_discount(self):
        for rec in self:
            rec.price_unit_discount = rec.move_id._get_price_discount_model(
                price_unit=rec.price_unit,
                formula=rec.formula_discount
            )

    @api.depends('price_subtotal', 'prorated_discount')
    def _compute_price_subtotal_wo_prorated(self):
        for rec in self:
            taxes = rec.tax_ids
            if taxes and any(tax.price_include for tax in taxes):
                total = rec.price_total + rec.prorated_discount
            else:
                total = rec.price_subtotal + rec.prorated_discount
            rec.price_subtotal_wo_prorated = total

    def _compute_prorated_discount(self):
        for rec in self:
            move = rec.move_id
            if rec.exclude_from_invoice_tab or not rec.price_unit:
                prorate = 0.0
            else:
                amount_untaxed = [
                    sum([
                        line.price_unit_discount * line.quantity,
                        -line.direct_discount
                    ])
                    for line in move.invoice_line_ids
                ]

                amount_untaxed = sum(amount_untaxed)

                price_subtotal = sum([
                    rec.price_unit_discount * rec.quantity,
                    -rec.direct_discount
                ])

                prorate = price_subtotal - move._get_price_discount_model(
                    price_unit=price_subtotal,
                    formula=move.formula_discount,
                )

                if amount_untaxed:
                    ratio = price_subtotal / amount_untaxed
                    prorate += ratio * move.direct_discount

                if rec.currency_id:
                    prorate = rec.currency_id.round(prorate)

            rec.prorated_discount = prorate

    def _get_price_total_and_subtotal(
        self, price_unit=None, quantity=None, discount=None, currency=None,
        product=None, partner=None, taxes=None, move_type=None,
        formula_discount='', prorated_discount=0.0
    ):
        self.ensure_one()
        return self._get_price_total_and_subtotal_model(
            price_unit=price_unit or self.price_unit,
            quantity=quantity or self.quantity,
            discount=self.direct_discount,
            currency=currency or self.currency_id,
            product=product or self.product_id,
            partner=partner or self.partner_id,
            taxes=taxes or self.tax_ids,
            move_type=move_type or self.move_id.move_type,
            formula_discount=formula_discount or self.formula_discount,
            prorated_discount=prorated_discount or self.prorated_discount
        )

    @api.model
    def _get_price_total_and_subtotal_model(
        self, price_unit, quantity, discount, currency,
        product, partner, taxes, move_type, formula_discount, prorated_discount
    ):
        if formula_discount:
            price_unit = self.move_id._get_price_discount_model(
                price_unit=price_unit,
                formula=formula_discount
            )

        discount += prorated_discount
        res = {}
        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(
                price_unit,
                quantity=quantity, currency=currency, product=product,
                partner=partner,
                is_refund=move_type in ('out_refund', 'in_refund'),
                discount=discount,
            )
            res['price_subtotal'] = taxes_res.get('total_excluded')
            res['price_total'] = taxes_res.get('total_included')
        else:
            subtotal = (price_unit * quantity) - discount
            if subtotal < 0:
                subtotal = 0

            res['price_total'] = res['price_subtotal'] = subtotal

        # In case of multi currency,
        # round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res

    def _get_fields_onchange_balance(
        self, quantity=None, discount=None, amount_currency=None,
        move_type=None, currency=None, taxes=None, price_subtotal=None,
        force_computation=False,
        formula_discount=None, prorated_discount=None
    ):
        self.ensure_one()
        return self._get_fields_onchange_balance_model(
            quantity=quantity or self.quantity,
            discount=discount or self.direct_discount,
            amount_currency=amount_currency or self.amount_currency,
            move_type=move_type or self.move_id.move_type,
            currency=currency or self.currency_id or self.move_id.currency_id,
            taxes=taxes or self.tax_ids,
            price_subtotal=price_subtotal or self.price_subtotal,
            force_computation=force_computation,
            formula_discount=formula_discount or self.formula_discount,
            prorated_discount=prorated_discount or self.prorated_discount
        )

    @api.model
    def _get_fields_onchange_balance_model(
        self, quantity, discount, amount_currency, move_type, currency,
        taxes, price_subtotal, force_computation=False,
        formula_discount='', prorated_discount=0.0
    ):
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        amount_currency *= sign

        if not force_computation and currency.is_zero(
            amount_currency - price_subtotal
        ):
            return {}

        taxes = taxes.flatten_taxes_hierarchy()
        if taxes and any(tax.price_include for tax in taxes):
            force_sign = -1 if move_type in (
                'out_invoice', 'in_refund', 'out_receipt'
            ) else 1
            taxes_res = taxes._origin.with_context(
                force_sign=force_sign
            ).compute_all(
                amount_currency,
                currency=currency,
                handle_price_include=False
            )
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                if tax.price_include:
                    amount_currency += tax_res['amount']

        if amount_currency:
            amount_currency += discount + prorated_discount
            amount_currency = self.move_id._get_price_wo_discount_model(
                price_unit=amount_currency,
                formula=formula_discount,
            )
            price_unit = amount_currency / (quantity or 1.0)
            if currency:
                price_unit = currency.round(price_unit)
            vals = {
                'quantity': quantity or 1.0,
                'discount': 0.0,
                'price_unit': price_unit,
                'prorated_discount': prorated_discount
            }
        else:
            vals = {'price_unit': 0.0, 'prorated_discount': 0.0}
        return vals

    def _compute_base_line_taxes(self):
        """
            This is Overide Inner Function
            for support discount in Beecy Project
        """
        move = self.move_id

        sign = -1 if move.is_inbound() else 1
        discount = sign * (
            self.direct_discount + self.prorated_discount
        )

        if move.is_invoice(include_receipts=True):
            handle_price_include = True
            quantity = self.quantity
            is_refund = move.move_type in ('out_refund', 'in_refund')
            price_unit_wo_discount = sign * self.price_unit_discount
        else:
            handle_price_include = False
            quantity = 1.0
            tax_type = self.tax_ids[0].type_tax_use if self.tax_ids else None
            is_refund = any([
                tax_type == 'sale' and self.debit,
                tax_type == 'purchase' and self.credit
            ])
            price_unit_wo_discount = self.amount_currency

        return self.tax_ids._origin.with_context(
            force_sign=move._get_tax_force_sign()).compute_all(
            price_unit_wo_discount,
            currency=self.currency_id,
            quantity=quantity,
            product=self.product_id,
            partner=self.partner_id,
            is_refund=is_refund,
            handle_price_include=handle_price_include,
            include_caba_tags=move.always_tax_exigible,
            discount=discount,
        )

    def recompute_create_line(self, vals_list):
        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')

        for vals in vals_list:
            move = self.env['account.move'].browse(vals['move_id'])
            vals.setdefault(
                'company_currency_id',
                move.company_id.currency_id.id
            )
            currency_id = vals.get(
                'currency_id') or move.company_id.currency_id.id
            if currency_id == move.company_id.currency_id.id:
                balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
                vals.update({
                    'currency_id': currency_id,
                    'amount_currency': balance,
                })
            else:
                vals['amount_currency'] = vals.get('amount_currency', 0.0)

            if move.is_invoice(include_receipts=True):
                currency = move.currency_id
                partner = self.env['res.partner'].browse(
                    vals.get('partner_id'))
                taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
                tax_ids = set(taxes.ids)
                taxes = self.env['account.tax'].browse(tax_ids)

                if any(vals.get(field) for field in ACCOUNTING_FIELDS):
                    price_subtotal = self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(
                            vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        vals.get('formula_discount', 0.0),
                        vals.get('prorated_discount', 0.0)
                    ).get('price_subtotal', 0.0)
                    vals.update(self._get_fields_onchange_balance_model(
                        vals.get('quantity', 0.0),
                        vals.get('direct_discount', 0.0),
                        vals['amount_currency'],
                        move.move_type,
                        currency,
                        taxes,
                        price_subtotal,
                        False,
                        vals.get('formula_discount', ''),
                        vals.get('prorated_discount', 0.0)
                    ))
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('direct_discount', 0.0),
                        currency,
                        self.env['product.product'].browse(
                            vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        vals.get('formula_discount', ''),
                        vals.get('prorated_discount', 0.0)
                    ))
                elif any(vals.get(field) for field in BUSINESS_FIELDS):
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('direct_discount', 0.0),
                        currency,
                        self.env['product.product'].browse(
                            vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        vals.get('formula_discount', ''),
                        vals.get('prorated_discount', 0.0)
                    ))
                    vals.update(self._get_fields_onchange_subtotal_model(
                        vals['price_subtotal'],
                        move.move_type,
                        currency,
                        move.company_id,
                        move.date,
                    ))
        return vals_list

    # override function for support discount in Beecy Account WHT
    @api.depends('price_subtotal', 'wht_type_id', 'prorated_discount')
    def _compute_wht_amount(self):
        for rec in self:
            rec.amount_wht = rec.wht_type_id.wht_calculator(
                rec.price_subtotal - rec.prorated_discount)
