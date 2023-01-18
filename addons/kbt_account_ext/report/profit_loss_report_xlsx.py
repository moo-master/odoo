from odoo import models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    # XLS_HEADERS,
)


class ProfitLossReportXlsx(models.AbstractModel):
    _name = 'report.kbt_account_ext.profit_loss_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Profit and Loss Report xlsx'

    def add_format_work_book(self, workbook):
        FORMATS['head_format'] = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'font_size': 11,
        })
        FORMATS['format_center'] = workbook.add_format({
            'bold': 0,
            'align': 'center',
            'font_size': 10,
        })
        FORMATS['format_center_l'] = workbook.add_format({
            'bold': 0,
            'align': 'left',
            'font_size': 10,
        })
        FORMATS['format_center_bold'] = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'font_size': 10,
        })
        FORMATS['format_r_bold_num'] = workbook.add_format({
            'bold': 0,
            'align': 'right',
            'font_size': 10,
            'num_format': '#,##0.00',
        })
        FORMATS['format_left'] = workbook.add_format({
            'bold': 0,
            'align': 'left',
            'font_size': 10,
            'num_format': '#,##0.00',
        })
        FORMATS['format_b_left'] = workbook.add_format({
            'bold': 1,
            'align': 'left',
            'font_size': 10,
            'num_format': '#,##0.00',
        })
        FORMATS['head_format_yellow'] = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'font_size': 10,
            'pattern': 1,
            'bg_color': 'FFFF8E',
        })

    def set_header_xlsx(self, worksheet, to_date_str, from_year, last_year):
        # Top Head
        worksheet.merge_range(
            'A1:M1', 'Kaset Inno  Co., Ltd.', FORMATS['head_format'])
        worksheet.merge_range(
            'A2:M2', 'PROGRAM STATEMENT', FORMATS['head_format'])
        worksheet.merge_range(
            'A3:M3', f'FOR THE MONTH OF {to_date_str}', FORMATS['head_format'])

        # Head Table Line Data Yellow zone
        worksheet.merge_range(
            'C6:F6', 'CURRENT MONTH', FORMATS['head_format_yellow'])
        worksheet.merge_range(
            'G6:J6', 'YEAR-TO-DATE', FORMATS['head_format_yellow'])
        worksheet.merge_range(
            'K6:L6', f'YEAR {from_year}', FORMATS['head_format_yellow'])
        worksheet.write('M6', 'YEAR', FORMATS['head_format_yellow'])
        worksheet.set_column('C7:M7', None, FORMATS['head_format_yellow'])

        worksheet.write(7, 2, 'ACTUAL', FORMATS['head_format_yellow'])
        worksheet.write(7, 3, 'PLAN', FORMATS['head_format_yellow'])
        worksheet.write(7, 4, 'VAR', FORMATS['head_format_yellow'])
        worksheet.write(7, 5, last_year, FORMATS['head_format_yellow'])
        worksheet.write(7, 6, 'ACTUAL', FORMATS['head_format_yellow'])
        worksheet.write(7, 7, 'PLAN', FORMATS['head_format_yellow'])
        worksheet.write(7, 8, 'VAR', FORMATS['head_format_yellow'])
        worksheet.write(7, 9, last_year, FORMATS['head_format_yellow'])
        worksheet.write(7, 10, 'ESTIMATED', FORMATS['head_format_yellow'])
        worksheet.write(7, 11, 'PLAN', FORMATS['head_format_yellow'])
        worksheet.write(7, 12, last_year, FORMATS['head_format_yellow'])

    def set_account_group_xlsx(self, worksheet):
        internal_group = self.env['account.account.group']._fields['internal_group'].selection
        row = 8
        for group in internal_group:
            acc_group = self.env['account.account.group'].search([
                ('internal_group', '=', group[0])
            ], order='sequence')
            for acc in acc_group:
                worksheet.write(row, 0, acc.name, FORMATS['format_left'])
                row += 1
            worksheet.write(row, 0, f'  {group[1]}', FORMATS['format_b_left'])
            row += 1

    def generate_xlsx_report(self, workbook, data, lines):
        from_date = lines.from_date
        to_date = lines.to_date
        # from_date_str = from_date.strftime('%B 1, %Y').upper()
        to_date_str = to_date.strftime('%B %d, %Y').upper()
        from_year = from_date.year
        last_year = to_date.year - 1

        self.add_format_work_book(workbook)
        worksheet = workbook.add_worksheet('PGST_KIN')

        # Freeze row 1-8 culumn A-B actual in xlsx
        worksheet.freeze_panes(8, 2)
        # Set Column
        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 45)
        worksheet.set_column('C:M', 20)

        # Set Header
        self.set_header_xlsx(worksheet, to_date_str, from_year, last_year)
        # Set show account group
        self.set_account_group_xlsx(worksheet)
