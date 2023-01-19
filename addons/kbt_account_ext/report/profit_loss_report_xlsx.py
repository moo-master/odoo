from odoo import models
from datetime import datetime

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
        FORMATS['format_right'] = workbook.add_format({
            'bold': 0,
            'align': 'right',
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

    def set_header_xlsx(
        self,
        worksheet,
        from_date: datetime,
        to_date: datetime
    ):
        to_date_str = to_date.strftime('%B %d, %Y').upper()
        last_year = from_date.year - 1
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
            'K6:L6', f'YEAR {from_date.year}', FORMATS['head_format_yellow'])
        worksheet.write('M6', 'YEAR', FORMATS['head_format_yellow'])
        # worksheet.set_column('C7:M7', None, FORMATS['head_format_yellow'])

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

    def check_value(
        self,
        group_id: int,
        data_dict: dict,
        head_column: str
    ):
        column_lst = ('actual', 'plan', 'var', 'last')
        result = []
        for column in column_lst:
            val = data_dict[column][group_id][head_column]\
                if group_id in data_dict[column] else 0
            result.append(val)
        return result

    def set_current_month_xlsx(
        self,
        worksheet,
        from_date: datetime,
        to_date: datetime
    ):
        internal_groups = \
            self.env['account.account.group']._fields['internal_group'].selection
        row = 8
        count_row = 1
        for group in internal_groups:
            acc_group = self.env['account.account.group'].search([
                ('internal_group', '=', group[0])
            ], order='sequence')

            sum_current_month = [0, 0, 0, 0]
            sum_year_to_date = [0, 0, 0, 0]
            sum_current_year = [0, 0, 0, 0]

            for a_group in acc_group:
                cur_month = self._get_lines_data(
                    a_group.id, from_date, to_date)
                year_to_date = self._get_lines_data(
                    a_group.id,
                    from_date.replace(day=1, month=1),
                    to_date)
                cur_year = self._get_lines_data(
                    a_group.id,
                    from_date.replace(day=1, month=1),
                    to_date.replace(day=31, month=12))

                worksheet.write(row, 0, a_group.name, FORMATS['format_left'])
                # Column Current Month
                worksheet.write(row, 2, cur_month[0] or '-',
                                FORMATS['format_right'])
                worksheet.write(row, 3, cur_month[1] or '-',
                                FORMATS['format_right'])
                worksheet.write(row, 4, cur_month[2] or '-',
                                FORMATS['format_right'])
                worksheet.write(row, 5, cur_month[3] or '-',
                                FORMATS['format_right'])
                # Column Year to Date
                worksheet.write(row, 6, year_to_date[0] or '-',
                                FORMATS['format_right'])
                worksheet.write(row, 7, year_to_date[1] or '-',
                                FORMATS['format_right'])
                worksheet.write(row, 8, year_to_date[2] or '-',
                                FORMATS['format_right'])
                worksheet.write(
                    row, 9, year_to_date[3] or '-', FORMATS['format_right'])
                # Column Current Year
                worksheet.write(row, 10, year_to_date[2] or '-',
                                FORMATS['format_right'])
                worksheet.write(
                    row, 11, year_to_date[3] or '-', FORMATS['format_right'])
                worksheet.write(
                    row, 12, cur_year[0] or '-', FORMATS['format_right'])
                # Row number
                worksheet.write(row, 13, count_row, FORMATS['format_center'])

                sum_current_month = \
                    [x + y for x, y in zip(sum_current_month, cur_month)]
                sum_year_to_date = \
                    [x + y for x, y in zip(sum_year_to_date, year_to_date)]
                sum_current_year = \
                    [x + y for x, y in zip(sum_current_year, cur_year)]

                row += 1
                count_row += 1

            worksheet.write(row, 0, f'  {group[1]}', FORMATS['format_b_left'])
            # Column Current Month
            worksheet.write(row, 2, sum_current_month[0],
                            FORMATS['format_right'])
            worksheet.write(row, 3, sum_current_month[1],
                            FORMATS['format_right'])
            worksheet.write(row, 4, sum_current_month[2],
                            FORMATS['format_right'])
            worksheet.write(row, 5, sum_current_month[3],
                            FORMATS['format_right'])
            # Column Year to Date
            worksheet.write(
                row, 6, sum_year_to_date[0], FORMATS['format_right'])
            worksheet.write(row, 7, sum_year_to_date[1],
                            FORMATS['format_right'])
            worksheet.write(row, 8, sum_year_to_date[2],
                            FORMATS['format_right'])
            worksheet.write(row, 9, sum_year_to_date[3],
                            FORMATS['format_right'])
            # Column Current Year

            worksheet.write(row, 13, count_row,
                            FORMATS['format_center'])
            count_row += 1
            row += 1

    def _get_lines_data_last(
        self,
        group_id: int,
        from_date: datetime,
        to_date: datetime
    ):
        move_lines = sum(self.env['account.move.line'].search([
            ('date', '>=', from_date),
            ('date', '<=', to_date),
            ('account_group_id', '=', group_id),
            ('parent_state', '=', 'posted'),
        ]).mapped(lambda x: -(x.credit - x.debit)))
        return move_lines

    def _get_lines_data(
        self,
        group_id: int,
        from_date: datetime,
        to_date: datetime
    ):
        move_lines = sum(self.env['account.move.line'].search([
            ('date', '>=', from_date),
            ('date', '<=', to_date),
            ('account_group_id', '=', group_id),
            ('parent_state', '=', 'posted'),
        ]).mapped(lambda x: -(x.credit - x.debit)))
        crossover_lines = sum(self.env['crossovered.budget.lines'].search([
            ('account_group_id', '=', group_id),
            ('crossovered_budget_state', '=', 'confirm'),
            ('date_from', '>=', from_date),
            ('date_to', '<=', to_date),
        ]).mapped('planned_amount'))
        last_move_lines = sum(self.env['account.move.line'].search([
            ('date', '>=', from_date.replace(year=from_date.year - 1)),
            ('date', '<=', to_date.replace(year=to_date.year - 1)),
            ('account_group_id', '=', group_id),
            ('parent_state', '=', 'posted'),
        ]).mapped(lambda x: -(x.credit - x.debit)))
        var = move_lines - crossover_lines
        return [move_lines, crossover_lines, var, last_move_lines]

    def _get_data_current_month(self):
        last_from_date = self.from_date.replace(year=self.from_date.year - 1)
        last_to_date = self.to_date.replace(year=self.to_date.year - 1)
        days_list = (
            (self.from_date, self.to_date, 'actual'),
            (last_from_date, last_to_date, 'plan'),
            (last_from_date, last_to_date, 'var'),
            (last_from_date, last_to_date, 'last')
        )
        query = """
        SELECT
            aag.id,
            aag."name" ,
            -(sum(aml.credit) - sum(aml.debit)) as total,
            aag.internal_group
        FROM account_account_group aag
        RIGHT JOIN account_move_line aml  on aml.account_group_id = aag.id
        WHERE
            aml.parent_state = 'posted'
            and aml."date" >= %(from_date)s
            and aml."date" <= %(to_date)s
        GROUP BY
            aag.internal_group,
            aag.name,
            aag.id,
            aag."sequence" ,
            aag.internal_group
        """
        result = {}
        for day_lst in days_list:
            self.env.cr.execute(query, {
                'from_date': day_lst[0],
                'to_date': day_lst[1],
            })
            records = self.env.cr.dictfetchall()
            result[day_lst[2]] = {
                rec.get('id'): rec.get('total') for rec in records
            }

        for act in result['actual']:
            result['var'][act] = result['actual'][act] - \
                result['plan'].get(act, 0)

        return result

    def generate_xlsx_report(self, workbook, data: dict, lines: object):
        from_date: datetime = lines.from_date
        to_date: datetime = lines.to_date

        self.add_format_work_book(workbook)
        worksheet = workbook.add_worksheet('PGST_KIN')

        # Freeze row 1-8 culumn A-B actual in xlsx
        worksheet.freeze_panes(8, 2)
        # Set Column
        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 35)
        worksheet.set_column('C:M', 15)
        # Prepare data on lines table
        # data_current_month = self._get_data_current_month()
        # Set Header
        self.set_header_xlsx(worksheet, from_date, to_date)
        # Set show account group
        self.set_current_month_xlsx(worksheet, from_date, to_date)
