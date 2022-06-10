from odoo import fields, models, api
from datetime import datetime


class AccountWhtPnd(models.Model):
    _name = 'account.wht.pnd'
    _description = "WHT PND"

    @api.model
    def _compute_tax(self):
        result = {}
        for rec in self.ids:
            result[rec] = {
                'total_amount': 0.0,
                'total_tax': 0.0,
                'total_tax_send': 0.0,
            }
            data = self.browse([rec])[0]
            val = val1 = 0.0
            for line in data.wht_ids:
                val1 += line.base_amount
                val += line.tax

            data.total_tax = val
            data.total_amount = val1
            data.total_tax_send = val + data.add_amount or 0.0

    @api.model
    def _compute_line(self):
        result = {}
        for rec in self:
            if rec.id:
                result[rec.id] = {
                    'attach_count': 0,
                    'attach_no': 0,
                }
                data = rec.browse([rec.id])[0]

                count_line = len(data.wht_ids)
                count_page = (count_line / 6) == 0 and 1 or (count_line / 6)
                rec.attach_count = count_line
                rec.attach_no = count_page

            return result

    def _get_selection(self):
        if self.pnd_type == 'pnd3' or self.env.context.get(
                'default_pnd_type') == 'pnd3':
            return [
                ('section3', "Section 3"),
                ('section48', "Section 48"),
                ('section50', "Section 50")
            ]
        else:
            return [
                ('section53', "Section 53"),
                ('section65', "Section 65"),
                ('section69', "Section 69"),
            ]

    def _default_get_pnd(self):
        if self.pnd_type == 'pnd3' or self.env.context.get(
                'default_pnd_type') == 'pnd3':
            return 'section3'
        else:
            return 'section53'

    name = fields.Char('Description', size=128, default='/')
    pnd_date = fields.Date('Date', required=True, default=fields.Date.today)
    type_no = fields.Integer('Type No.')
    is_attach_pnd = fields.Boolean('Attach PND', default=True)
    attach_count = fields.Integer(
        compute="_compute_line", string='Attach Count')
    attach_no = fields.Integer(compute="_compute_line", string='Attach No')
    total_amount = fields.Float(
        compute="_compute_tax",
        digits='Account',
        string='Total Amount'
    )
    total_tax = fields.Float(
        compute="_compute_tax",
        digits='Account',
        string='Total Tax'
    )
    add_amount = fields.Float('Add Amount', digits='Account')
    total_tax_send = fields.Float(
        compute="_compute_tax",
        digits='Account',
        string='Total Tax Send'
    )
    wht_ids = fields.Many2many(
        'account.wht',
        'account_wht_pnds',
        'pnd_id',
        'wht_id',
        'With holding tax')
    note = fields.Text('Note')
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda self: self.env.company.id,
    )
    pnd_type = fields.Selection(
        selection=[
            ('pnd3', '(4) PND3'),
            ('pnd53', '(7) PND53')
        ],
        string='PND Type',
        required=True,
    )
    period_pnd_date = fields.Date(
        string='Month PND',
        default=fields.Date.today,
        required=True,
    )
    select_month = fields.Char(
        string="Month",
        required=False,
        compute='_compute_pickup_time_formated',
        store=True,
    )
    select_month_date = fields.Date(
        string='Select Month',
        required=False,
    )
    section = fields.Selection(
        selection=lambda r: r._get_selection(),
        default=lambda r: r._default_get_pnd(),
        string='Filing According to')
    attachment_type = fields.Selection([
        ('paper', 'Paper Attachment'),
        ('electronic', 'Electronic Attachment')
    ],
        default='paper',
        string='Attachment Type')
    fill_type = fields.Selection([
        ('ordinary', 'Ordinary Filing'),
        ('additional', 'Additional Filing')
    ],
        string='Filing Type')
    additional_fill = fields.Char(
        'Additional Filing',
    )

    @api.depends('wht_ids')
    def _compute_wht_line_partner(self):
        for rec in self:
            if not rec.wht_ids:
                rec.wht_ids_count_str = False
            else:
                partner_count = len(rec.wht_ids.mapped('partner_id')) or 0
                rec.wht_ids_count_str = f'{len(rec.wht_ids) or 0} Records From {partner_count} Partner'

    wht_ids_count_str = fields.Char(' ', compute='_compute_wht_line_partner')

    def action_print_pnd3(self):
        for rec in self:
            return rec.env.ref(
                'beecy_account_wht.action_pnd3_report').report_action(rec)

    def action_print_pnd53(self):
        for rec in self:
            return rec.env.ref(
                'beecy_account_wht.action_pnd53_report').report_action(rec)

    def action_files_docs(self):
        return True

    def action_file(self):
        return True

    @api.depends('select_month_date')
    def _compute_pickup_time_formated(self):
        for rec in self:
            if rec.select_month_date:
                date = rec.select_month_date
                date_obj = datetime.strptime(str(date), "%Y-%m-%d")
                rec.select_month = datetime.strftime(date_obj, '%m/%Y')
                rec.name = datetime.strftime(date_obj, '%m/%Y')
