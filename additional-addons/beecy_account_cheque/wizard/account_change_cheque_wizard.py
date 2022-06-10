from odoo import fields, models


class AccountChequeWizard(models.TransientModel):
    _name = 'account.change.cheque.wizard'
    _description = 'Account Cheque Wizard'

    name = fields.Char(
        string='Cheque No',
        required=True,
    )

    cheque_date = fields.Date(
        string='Cheque Date',
        required=True
    )

    bank_id = fields.Many2one(
        string='Bank',
        comodel_name='res.bank',
        ondelete='cascade'
    )

    partner_bank_id = fields.Many2one(
        string='Partner Bank',
        comodel_name='res.partner.bank',
        ondelete='cascade'
    )

    reason = fields.Text(
        string='Reason',
        required=True
    )

    def action_confirm(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        cheque = self.env['account.cheque'].browse(active_ids)
        cheque_new = cheque.copy({
            'name': self.name,
            'cheque_date': self.cheque_date,
            'bank_id': self.bank_id.id,
            'from_bank_id': self.partner_bank_id.id,
            'reference': cheque.name
        })
        cheque.write({'state': 'cancel'})
        action = self.env["ir.actions.actions"]._for_xml_id(
            "beecy_account_cheque.customer_account_cheque_action")
        action['res_id'] = cheque_new.id
        action['context'] = self.env.context
        action['domain'] = [('id', 'in', cheque_new.ids)]
        action['views'] = [(False, 'form')]
        return action
