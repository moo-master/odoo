from odoo import models, fields, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_approve_send = fields.Boolean(
        string='is_approve_send',
        invisible=True,
    )

    reject_reason = fields.Char(
        string='Reject Reason Note',
    )

    def action_post(self):
        employee = self.env['hr.employee'].search(
            [('id', '=', self.partner_id.employee_ids.id)])
        if not self.x_is_interface:
            if employee.level_id.approval_validation('account.move', sum(
                    self.line_ids.mapped('debit')), self.move_type):
                super().action_post()
            else:
                self.is_approve_send = True
                em_level = employee.level_id._rec_name if employee.level_id else "no level_id"
                raise ValidationError(
                    _(
                        'You cannot validate this document due limitation policy. Please contact employee {%s}\n ไม่สามารถดำเนินการได้เนื่องจากเกินวงเงินที่กำหนด กรุณาติดต่อพนักงาน {%s}',
                        em_level,
                        em_level))
        else:
            super().action_post()

    def action_cancel_reject_reason_wizard(self):
        view = self.env.ref('beecy_reason.view_cancel_reject_reason_form')
        context = dict(
            self.env.context,
            model_name='account.move',
            state='reject'
        )
        return {
            'name': _('Reject Quotations'),
            'view_mode': 'form',
            'res_model': 'cancel.reject.reason',
            'view_id': view.id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
