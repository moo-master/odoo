from odoo import models
import datetime
import pytz
from odoo.addons.beecy_web_report.models.base_document_layout import MONTH_THAI

tz = pytz.timezone('Asia/Bangkok')


class PartnerXlsx(models.AbstractModel):
    _name = "report.beecy_account_purchase_ext.purchase_tax_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Purchase Tax Report xlsx"

    def generate_xlsx_report(self, workbook, data, wizard):
        account_move = wizard.account_move_ids
        today = datetime.datetime.now(datetime.timezone.utc)
        m_thai = MONTH_THAI.split(' ')
        month_report = ''
        year_report = ''
        if wizard.start_date:
            invoice_date = wizard.start_date
            month_report = m_thai[int(invoice_date.month)]
            year_report = invoice_date.year + 543
        company = self.env.company
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
        normal_border_center = workbook.add_format({
            'align': 'center',
            'left': 1,
            'right': 1,
        })
        normal_float_right = workbook.add_format({'num_format': '0.00'})
        normal_float_right.set_align('right')
        normal_border_right = workbook.add_format(
            {'align': 'right',
             'num_format': '#,##0.00;-#,##0.00',
             'left': 1,
             'right': 1, })
        head = workbook.add_format({'align': 'center',
                                    'bold': True,
                                    'font_size': '11px',
                                    'border': 1,
                                    'border_color': 'ffffff'})
        head_company = workbook.add_format({'align': 'left',
                                            'font_size': '11px',
                                            'border': 1,
                                            'border_color': 'ffffff'})
        bold_left_head = workbook.add_format({'align': 'left',
                                              'bold': True,
                                              'font_size': '11px',
                                              'border': 1,
                                              'border_color': 'ffffff'})
        bold_right_num = workbook.add_format(
            {
                'num_format': '#,##0.00;-#,##0.00',
                'align': 'right',
                'bold': True,
                'font_size': '11px',
                'border': 1,
            })
        normal_left_head = workbook.add_format({'align': 'left',
                                                'font_size': '11px',
                                                'border': 1,
                                                'border_color': 'ffffff'})
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
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)
        sheet.merge_range('A1:J1', 'รายงานภาษีซื้อ', head)
        sheet.merge_range('A2:C2', '', head)
        sheet.write(1, 3, 'เดือนภาษี', head)
        sheet.write(1, 4, month_report, normal)
        sheet.write(1, 5, 'ปี', head)
        sheet.write(1, 7, '', head)
        sheet.write(1, 9, '', head)
        sheet.write(1, 6, year_report, normal)
        sheet.write(
            1, 8, 'วันที่พิมพ์: {0}'.format(
                today.strftime("%d/%m/%y")), head
        )
        sheet.merge_range(2, 0, 2, 1, 'ชื่อผู้ประกอบการ : ', bold_left)
        sheet.merge_range('C3:F3', company.name, head_company)
        sheet.write(2, 6, 'เลขประจำตัวผู้เสียภาษี : ', bold_left_head)
        sheet.merge_range('H3:J3', vat, normal_left_head)
        sheet.write(3, 6, 'สำนักงาน/สาขาที่', bold_left_head)
        sheet.merge_range('H4:J4', 'สำนักงานใหญ่', bold_left_head)
        sheet.merge_range(
            'A4:B4',
            'ที่อยู่สถานประกอบการ : ',
            bold_left_head)
        sheet.merge_range('C4:F4', address, normal_left)
        sheet.write(4, 2, '', normal_border)
        head_col = ['ลำดับ',
                    'วัน/เดือน/ปี',
                    'เลขที่เอกสาร',
                    'ชื่อผู้ขายสินค้า/ชื่อผู้ให้บริการ',
                    'เลขประจำตัวผู้เสียภาษีอากร',
                    'สำนักงาน/สาขาที่',
                    'มูลค่าสินค้า/บริการ',
                    'ภาษีมูลค่าเพิ่ม',
                    'จำนวนเงินรวมทั้งสิ้น',
                    'หมายเหตุ']
        self._set_head_column(4, head_col, sheet, bold_border_center)
        n = 0
        for i, obj in enumerate(account_move):
            n += 1
            sheet.write(i + 5, 0, n, normal_center)
            sheet.write(
                i + 5,
                1,
                obj.invoice_date.strftime("%d/%m/%y"),
                normal_border_center)
            if obj.move_type == 'in_refund':
                amount_total = abs(obj.amount_untaxed) * -1
                amount_tax = abs(obj.amount_tax) * -1
                amount_total_signed = abs(obj.amount_total_signed) * -1
            else:
                amount_total = obj.amount_untaxed
                amount_tax = obj.amount_tax
                amount_total_signed = obj.amount_total_signed
            sheet.write(
                i + 5, 2, obj.invoice_ref_id.name or '', normal_border_center
            )
            sheet.write(
                i + 5, 3, '{0} {1} {2} {3}'.format(
                    obj.partner_id.title.name or '',
                    obj.partner_id.title.prefix or '',
                    obj.partner_id.name,
                    obj.partner_id.title.suffix or ''
                ), normal_border_center
            )
            sheet.write(
                i + 5,
                4,
                obj.partner_id.vat or '',
                normal_border_center)
            sheet.write(i + 5, 5, 'สำนักงานใหญ่', normal_border_center)
            sheet.write(i + 5, 6, amount_total, normal_border_right)
            sheet.write(i + 5, 7, amount_tax or '', normal_border_right)
            sheet.write(i + 5, 8, amount_total_signed, normal_border_right)
            sheet.write(i + 5, 9, '', normal_border_center)

        sheet.write(n + 5, 0, '', normal_border)
        sheet.write(n + 5, 1, '', normal_border)
        sheet.write(n + 5, 2, '', normal_border)
        sheet.write(n + 5, 3, '', normal_border)
        sheet.write(n + 5, 4, '', normal_border)
        sheet.write(n + 5, 5, 'รวม', bold_right_num)
        sheet.write(
            n + 5, 6,
            sum(account_move.mapped('amount_total')) or '', bold_right_num)
        sheet.write(
            n + 5, 7,
            sum(account_move.mapped('amount_tax')) or '', bold_right_num)
        sheet.write(n + 5, 8,
                    sum(account_move.mapped('amount_total_signed')) or '',
                    bold_right_num)
        sheet.write(n + 5, 9, '', bold_right_num)

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
