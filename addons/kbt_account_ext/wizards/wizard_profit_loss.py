from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class WizardProfitLoss(models.TransientModel):
    _name = 'wizard.profit.loss'
    _description = 'Profit and Loss'

    from_date = fields.Date(
        string='From Month',
        default=fields.Date.today().replace(day=1),
    )
    to_date = fields.Date(
        string='To Month',
        compute='_compute_to_date'
    )

    def print_report_xls(self):
        return self.env.ref(
            'kbt_account_ext.profit_loss_report_xlsx'
        ).report_action(self)

    @api.depends('from_date')
    def _compute_to_date(self):
        self.to_date = self.from_date.replace(day=1) + relativedelta(months=1)\
            - timedelta(days=1)
