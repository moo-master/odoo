import math
from datetime import datetime

from odoo import fields, models, api


class AccountWhtPnd(models.Model):
    _name = 'account.wht.pnd'
    _description = 'WHT PND'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_selection(self):
        if self.pnd_type == 'pnd3' or self.env.context.get(
                'default_pnd_type') == 'pnd3':
            return [
                ('section3', 'Section 3'),
                ('section48', 'Section 48'),
                ('section50', 'Section 50')
            ]
        else:
            return [
                ('section3', 'Section 3'),
                ('section65', 'Section 65'),
                ('section69', 'Section 69'),
            ]

    name = fields.Char(string='Description', size=128, default='/')
    pnd_date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    type_no = fields.Integer(string='Type No.')
    is_attach_pnd = fields.Boolean(string='Attach PND', default=True)
    attach_count = fields.Integer(
        compute='_compute_line',
        string='Attach Count'
    )
    attach_no = fields.Integer(compute='_compute_line', string='Attach No')
    total_amount = fields.Float(
        compute='_compute_tax',
        digits='Account',
        string='Total Amount',
        tracking=True,
        store=True,
    )
    total_tax = fields.Float(
        compute='_compute_tax',
        digits='Account',
        string='Total Tax',
        tracking=True,
        store=True
    )
    add_amount = fields.Float(
        string='Add Amount',
        digits='Account',
        tracking=True
    )
    total_tax_send = fields.Float(
        compute='_compute_tax',
        digits='Account',
        string='Total Tax Send',
        tracking=True,
        store=True
    )
    wht_ids = fields.Many2many(
        comodel_name='account.wht',
        relation='account_wht_pnds',
        column1='pnd_id',
        column2='wht_id',
        string='Withholding Tax'
    )
    note = fields.Text(string='Note')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company.id
    )
    pnd_type = fields.Selection(
        selection=[
            ('pnd3', '(4) PND3'),
            ('pnd53', '(7) PND53')
        ],
        string='PND Type',
        required=True
    )
    period_pnd_date = fields.Date(
        string='Month PND',
        default=fields.Date.today,
        required=True
    )
    select_month = fields.Char(
        string='Month',
        required=False,
        compute='_compute_pickup_time_formatted',
        store=True,
        tracking=True
    )
    select_month_date = fields.Date(
        string='Select Month',
        required=False
    )
    section = fields.Selection(
        selection=lambda r: r._get_selection(),
        default='section3',
        string='Filing According to'
    )
    attachment_type = fields.Selection([
        ('paper', 'Paper Attachment'),
        ('electronic', 'Electronic Attachment')
    ],
        default='paper',
        string='Attachment Type'
    )
    fill_type = fields.Selection(
        selection=[
            ('ordinary', 'Ordinary Filing'),
            ('additional', 'Additional Filing')
        ],
        string='Filing Type',
        tracking=True
    )
    additional_fill = fields.Char(
        string='Additional Filing',
        tracking=True
    )
    wht_ids_count_str = fields.Char(
        compute='_compute_wht_line_partner'
    )
    year_select = fields.Selection(
        selection=[
            (str(num), str(num)) for num in range(
                2021, (datetime.now().year) + 2)
        ],
        string='Year',
        default=str(datetime.now().year),
    )
    month_select = fields.Selection(
        string='Month',
        selection=[
            ('01', '01'),
            ('02', '02'),
            ('03', '03'),
            ('04', '04'),
            ('05', '05'),
            ('06', '06'),
            ('07', '07'),
            ('08', '08'),
            ('09', '09'),
            ('10', '10'),
            ('11', '11'),
            ('12', '12'),
        ],
        default='{:02d}'.format(datetime.now().month),
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirm', 'Confirm')
        ],
        string='Status',
        default='draft',
    )

    @api.depends('wht_ids')
    def _compute_wht_line_partner(self):
        for rec in self:
            rec.wht_ids_count_str = False
            if rec.wht_ids:
                partner_count = len(rec.wht_ids.mapped('partner_id')) or 0
                rec.wht_ids_count_str = f'''
                    {len(rec.wht_ids) or 0}
                    Records From {partner_count} Partner'''

    @api.depends('wht_ids', 'add_amount')
    def _compute_tax(self):
        for rec in self:
            val = val1 = 0.0
            for line in rec.wht_ids:
                val1 += line.base_amount
                val += line.tax

            rec.total_tax = val
            rec.total_amount = val1
            rec.total_tax_send = val + rec.add_amount or 0.0

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

    def split_id_card(self):
        if self.company_id.vat and len(self.company_id.vat) == 13:
            card_1 = self.company_id.vat[0]
            card_2 = self.company_id.vat[1:5]
            card_3 = self.company_id.vat[5:10]
            card_4 = self.company_id.vat[10:12]
            card_5 = self.company_id.vat[12]
            return [card_1, card_2, card_3, card_4, card_5]
        return False

    def split_amount(self, amount):
        return math.modf(round(amount, 2))

    def get_decimal_amount(self, amount):
        rd_amount = round(amount, 2)
        decimal_1 = str(rd_amount)[2]
        decimal_2 = str(rd_amount)[3] if len(str(rd_amount)) > 3 else '0'
        return decimal_1 + decimal_2

    def get_attach_count(self):
        model_name = 'report.beecy_account_wht.report_pnd3_attach_pdf'
        report_id = self.env[model_name]._get_report_values(self.ids)
        return [report_id['total_page'], len(report_id['data_list'])]

    @api.depends('year_select', 'month_select')
    def _compute_pickup_time_formatted(self):
        for rec in self:
            date_obj = datetime.strptime(
                f'{rec.year_select}-{rec.month_select}', '%Y-%m')
            rec.select_month_date = date_obj
            rec.select_month = datetime.strftime(date_obj, '%m/%Y')
            rec.name = datetime.strftime(date_obj, '%m/%Y')

    def action_confirm(self):
        self.update({'state': 'confirm'})
