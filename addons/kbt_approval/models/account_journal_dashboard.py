

from odoo import models
from odoo.tools.misc import formatLang


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _get_ar_staff_to_approve_query(self, res):
        query = """SELECT am.amount_total as amount_total, am.currency_id AS currency
                    FROM account_move am
                    inner join account_journal aj on am.journal_id = aj.id
                    WHERE am.state IN ('to approve')
                    and is_officer_approved = true
                    and (is_ae_approver_approved = false or is_ae_approver_approved is null)
                    and aj.account_entry = 'ar'"""
        self.env.cr.execute(query)
        query_results = self.env.cr.dictfetchall()
        (number_to_pay, sum_to_pay) = self._count_results_and_sum_amounts(
            query_results, self.company_id.currency_id)
        res['number_ar_staff_to_approve'] = number_to_pay
        res['sum_ar_staff_to_approve'] = formatLang(
            self.env,
            sum_to_pay or 0.0,
            currency_obj=self.currency_id or self.company_id.currency_id)
        return res

    def _get_ar_manager_to_approve_query(self, res):
        query = """SELECT am.amount_total as amount_total, am.currency_id AS currency
                    FROM account_move am
                    inner join account_journal aj on am.journal_id = aj.id
                    WHERE am.state IN ('to approve')
                    and is_ae_approver_approved = true
                    and (is_ae_manager_approved = false or is_ae_manager_approved is null)
                    and aj.account_entry = 'ar'"""
        self.env.cr.execute(query)
        query_results = self.env.cr.dictfetchall()
        (number_to_pay, sum_to_pay) = self._count_results_and_sum_amounts(
            query_results, self.company_id.currency_id)
        res['number_ar_manager_to_approve'] = number_to_pay
        res['sum_ar_manager_to_approve'] = formatLang(
            self.env,
            sum_to_pay or 0.0,
            currency_obj=self.currency_id or self.company_id.currency_id)
        return res

    def _get_ap_staff_to_approve_query(self, res):
        query = """SELECT am.amount_total as amount_total, am.currency_id AS currency
                    FROM account_move am
                    inner join account_journal aj on am.journal_id = aj.id
                    WHERE am.state IN ('to approve')
                    and is_officer_approved = true
                    and (is_ae_approver_approved = false or is_ae_approver_approved is null)
                    and aj.account_entry = 'ap'"""
        self.env.cr.execute(query)
        query_results = self.env.cr.dictfetchall()
        (number_to_pay, sum_to_pay) = self._count_results_and_sum_amounts(
            query_results, self.company_id.currency_id)
        res['number_ap_staff_to_approve'] = number_to_pay
        res['sum_ap_staff_to_approve'] = formatLang(
            self.env,
            sum_to_pay or 0.0,
            currency_obj=self.currency_id or self.company_id.currency_id)
        return res

    def _get_ap_manager_to_approve_query(self, res):
        query = """SELECT am.amount_total as amount_total, am.currency_id AS currency
                    FROM account_move am
                    inner join account_journal aj on am.journal_id = aj.id
                    WHERE am.state IN ('to approve')
                    and is_ae_approver_approved = true
                    and (is_ae_manager_approved = false or is_ae_manager_approved is null)
                    and aj.account_entry = 'ap'"""
        self.env.cr.execute(query)
        query_results = self.env.cr.dictfetchall()
        (number_to_pay, sum_to_pay) = self._count_results_and_sum_amounts(
            query_results, self.company_id.currency_id)
        res['number_ap_manager_to_approve'] = number_to_pay
        res['sum_ap_manager_to_approve'] = formatLang(
            self.env,
            sum_to_pay or 0.0,
            currency_obj=self.currency_id or self.company_id.currency_id)
        return res

    def get_journal_dashboard_datas(self):
        res = super(AccountJournal, self).get_journal_dashboard_datas()
        # add the number and sum of expenses to pay to the json defining the
        # accounting dashboard data
        res = self._get_ar_staff_to_approve_query(res)
        res = self._get_ar_manager_to_approve_query(res)
        res = self._get_ap_staff_to_approve_query(res)
        res = self._get_ap_manager_to_approve_query(res)
        return res

    def open_ar_staff_move_action(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'account.action_move_line_form')
        action['domain'] = [
            ('state', '=', 'to approve'),
            ('is_officer_approved', '=', True),
            ('is_ae_approver_approved', '=', False),
            ('journal_id.account_entry', '=', 'ar')
        ]
        return action

    def open_ar_manager_move_action(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'account.action_move_line_form')
        action['domain'] = [
            ('state', '=', 'to approve'),
            ('is_ae_approver_approved', '=', True),
            ('is_ae_manager_approved', '=', False),
            ('journal_id.account_entry', '=', 'ar')
        ]
        return action

    def open_ap_staff_move_action(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'account.action_move_line_form')
        action['domain'] = [
            ('state', '=', 'to approve'),
            ('is_officer_approved', '=', True),
            ('is_ae_approver_approved', '=', False),
            ('journal_id.account_entry', '=', 'ap')
        ]
        return action

    def open_ap_manager_move_action(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'account.action_move_line_form')
        action['domain'] = [
            ('state', '=', 'to approve'),
            ('is_ae_approver_approved', '=', True),
            ('is_ae_manager_approved', '=', False),
            ('journal_id.account_entry', '=', 'ap')
        ]
        return action
