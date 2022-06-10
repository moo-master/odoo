from odoo import fields, models
from dateutil.relativedelta import relativedelta
import datetime


class PurchaseTaxReportWizard(models.Model):
    _name = "purchase.tax.report.wizard"
    _description = "Purchase Tax Report Wizard"

    start_date = fields.Date(
        string='Tax Month',
        default=fields.Date.today,
    )

    company_ids = fields.Many2many(
        comodel_name='res.company',
        string="Company",
    )

    account_move_ids = fields.Many2many('account.move', string='')

    def button_export_xlsx(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "beecy_account_purchase_ext.purchase_tax_report_xlsx")
        start_date = self.start_date.strftime('%Y-%m-01')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = (start_date + relativedelta(months=+1, days=-1))
        domain = [
            ('invoice_date', '!=', False),
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
            ('move_type', 'not in', ['out_invoice', 'out_refund', 'out_debit']),
            ('state', '=', 'posted'),
        ]
        if self.company_ids:
            val = ('company_id', 'in', self.company_ids.ids)
            domain.append(val)
        account = self.env['account.move'].search(domain)
        self.account_move_ids = account.ids
        action.update({'close_on_report_download': True})
        return action
