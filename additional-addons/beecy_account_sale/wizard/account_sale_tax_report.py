from odoo import models, fields
from dateutil.relativedelta import relativedelta
import datetime
import pytz
import html2text
from odoo.addons.beecy_web_report.models.base_document_layout import MONTH_THAI

tz = pytz.timezone('Asia/Bangkok')


class SaleTaxReportWizard(models.Model):
    _name = 'sale.tax.report.wizard'
    _description = 'Sale Tax Report Wizard'

    sales_person_id = fields.Many2one(
        comodel_name='res.users',
        string="Sales Person",
    )
    company_ids = fields.Many2many(
        comodel_name='res.company',
        string="Company",
    )
    start_date = fields.Date(
        string='Tax Month',
        default=fields.Date.today,
    )
    end_date = fields.Date(
        string='End Date',
        default=fields.Date.today,
    )
    account_move_ids = fields.Many2many('account.move', string='')

    def print_xls_report(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "beecy_account_sale.sale_tax_xlsx"
        )
        start_date = self.start_date.strftime('%Y-%m-01')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = (start_date + relativedelta(months=+1, days=-1))
        domain = [
            ('state', 'in', ['posted', 'cancel']),
            ('move_type', 'in', ['out_invoice', 'out_refund', 'out_debit']),
            ('state_customer', '!=', 'cancel'),
            ('amount_tax', '>', 0),
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date)

        ]
        if self.company_ids:
            val = ('company_id', 'in', self.company_ids.ids)
            domain.append(val)
        account_move = self.env['account.move'].search(domain)
        self.account_move_ids = account_move.ids
        action.update({'close_on_report_download': True})
        return action


class SaleTaxXlsx(models.AbstractModel):
    _name = 'report.beecy_account_sale.sale_tax'
    _description = 'Sale Tax Xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        account_move = wizard.account_move_ids
        account_move = account_move.search(
            [('id', 'in', account_move.ids)], order='invoice_date ASC')
        today = datetime.datetime.now(datetime.timezone.utc)
        m_thai = MONTH_THAI.split(' ')
        month_report = ''
        year_report = ''
        if wizard.start_date:
            invoice_date = wizard.start_date
            month_report = m_thai[int(invoice_date.month)]
            year_report = invoice_date.year + 543
        company = self.env.company
        branch = \
            'สำนักงานใหญ่' if company.branch == 'hq' else company.branch_code
        street = company.street
        street2 = company.street2
        state_id = company.state_id
        zip_code = company.zip
        vat = self.env.company.vat
        address = ' {0} {1} {2} {3}'.format(
            street, street2, state_id.name, zip_code)
        sheet = workbook.add_worksheet("Report")

        normal_border = workbook.add_format({"border": 1})
        normal = workbook.add_format()
        normal.set_align('center')
        normal_right = workbook.add_format()
        normal_right.set_align('right')
        normal_left = workbook.add_format()
        normal_left.set_align('left')
        normal_center = workbook.add_format()
        normal_center.set_align('center')
        normal_border_center = workbook.add_format({"border": 1})
        normal_border_center.set_align('center')
        normal_float_right = workbook.add_format({'num_format': '0.00'})
        normal_float_right.set_align('right')
        normal_border_right = workbook.add_format(
            {'num_format': '0.00', "border": 1})
        normal_border_right.set_align('right')
        bold_center = workbook.add_format({"bold": True})
        bold_center.set_align('center')
        normal_float_right.set_align('right')
        bold_border_center = workbook.add_format({"bold": True, "border": 1})
        bold_border_center.set_align('center')

        bold_left = workbook.add_format({"bold": True})
        bold_left.set_align('left')
        bold_right = workbook.add_format({"bold": True})
        bold_right.set_align('right')
        bold_border_right = workbook.add_format({"bold": True, "border": 1})
        bold_border_right.set_align('right')

        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 9, 15)
        sheet.set_column(10, 10, 15)
        sheet.merge_range(0, 4, 0, 5, 'รายงานภาษีขาย', bold_center)
        sheet.write(1, 3, 'เดือนภาษี', bold_center)
        sheet.write(1, 4, month_report, normal)
        sheet.write(1, 5, 'ปี', bold_center)
        sheet.write(1, 6, year_report, normal)
        sheet.write(
            1, 10, 'วันที่พิมพ์: {0}'.format(
                today.strftime("%d/%m/%y")), bold_left
        )
        sheet.merge_range(2, 0, 2, 1, 'ชื่อผู้ประกอบการ : ', bold_left)
        sheet.merge_range(2, 2, 2, 3, company.name, normal_left)
        sheet.write(
            2, 6, 'เลขประจำตัวผู้เสียภาษี :', bold_left
        )
        sheet.write(2, 7, vat, bold_left)
        sheet.write(3, 0, 'ที่อยู่ : ', bold_left)
        sheet.merge_range(3, 1, 3, 5, address, normal_left)
        sheet.write(3, 6, 'สำนักงาน/สาขาที่ ', bold_left)
        sheet.write(3, 7, branch, bold_left)
        head_col = ['ลำดับ',
                    'วัน/เดือน/ปี',
                    'เลขที่เอกสาร',
                    'ชื่อลูกค้า',
                    'เลขประจำตัวผู้เสียภาษี',
                    'สำนักงาน/สาขาที่',
                    'มูลค่าสินค้า/บริการ',
                    'ภาษีมูลค่าเพิ่ม',
                    'จำนวนเงินรวม',
                    'สถานะ',
                    'หมายเหตุ']
        self._set_head_column(4, head_col, sheet, bold_border_center)
        n = 0
        amount_untaxed_total = 0
        amount_tax_total = 0
        for i, obj in enumerate(account_move):
            n += 1
            sheet.write(i + 5, 0, n, normal_center)
            sheet.write(
                i + 5,
                1,
                obj.invoice_date.strftime("%d/%m/%y"),
                normal_border_center)
            if obj.move_type == 'out_refund':
                amount_untaxed = abs(obj.amount_untaxed) * -1
                amount_tax = abs(obj.amount_tax) * -1
                amount_total_signed = abs(obj.amount_total_signed) * -1
            elif obj.move_type == 'out_debit':
                amount_untaxed = abs(obj.amount_untaxed)
                amount_tax = abs(obj.amount_tax)
                amount_total_signed = abs(obj.amount_total_signed)
            else:
                amount_untaxed = obj.amount_untaxed
                amount_tax = obj.amount_tax
                amount_total_signed = obj.amount_total_signed

            sheet.write(i + 5, 2, obj.name, normal_border_center)
            sheet.write(i + 5, 3, obj.partner_id.name, normal_border_center)
            sheet.write(
                i + 5,
                4,
                obj.partner_id.vat or '',
                normal_border_center)
            sheet.write(i + 5, 5, 'สำนักงานใหญ่', normal_border_center)
            sheet.write(i + 5, 6, amount_untaxed, normal_border_right)
            sheet.write(i + 5, 7, amount_tax or '', normal_border_right)
            sheet.write(i + 5, 8, amount_total_signed, normal_border_right)
            sheet.write(i + 5, 9, obj.state_customer, normal_border_center)
            remark = html2text.html2text(obj.cn_dn_reason or '')
            sheet.write(i + 5, 10, remark, normal_border_center)
            amount_untaxed_total += amount_untaxed
            amount_tax_total += amount_tax

        sheet.write(n + 5, 0, '', normal_border)
        sheet.write(n + 5, 1, '', normal_border)
        sheet.write(n + 5, 2, '', normal_border)
        sheet.write(n + 5, 3, '', normal_border)
        sheet.write(n + 5, 4, '', normal_border)
        sheet.write(n + 5, 5, 'รวม', bold_border_right)
        sheet.write(n + 5, 6, amount_untaxed_total or '', normal_border_right)
        sheet.write(n + 5, 7, amount_tax_total or '', normal_border_right)
        sheet.write(n + 5, 8,
                    sum(account_move.mapped('amount_total_signed')) or '',
                    normal_border_right)
        sheet.write(n + 5, 9, '', normal_border)
        sheet.write(n + 5, 10, '', normal_border)

    def _set_head_column(self, start_row, h_col, sheet, bold_center):
        for i, rec in enumerate(h_col):
            sheet.write(start_row, i, rec, bold_center)
            sheet.write(start_row, i, rec, bold_center)
            sheet.write(start_row, i, rec, bold_center)
            sheet.write(start_row, i, rec, bold_center)
            sheet.write(start_row, i, rec, bold_center)
            sheet.write(start_row, i, rec, bold_center)
            sheet.write(start_row, i, rec, bold_center)
            sheet.write(start_row, i, rec, bold_center)
            sheet.write(start_row, i, rec, bold_center)
            sheet.write(start_row, i, rec, bold_center)
