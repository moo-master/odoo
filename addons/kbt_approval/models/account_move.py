from odoo import models, fields, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(
        selection_add=[
            ('to approve', 'To Approve'),
        ],
        ondelete={'to approve': 'set default'}
    )
    approve_level = fields.Integer(
        'approve level',
        default=0
    )
    is_approve = fields.Boolean(
        compute='_compute_approve',
        default=True
    )

    reject_reason = fields.Char(
        string='Reject Reason Note',
    )

    def _compute_approve(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1).sudo()
        self.is_approve = (
            employee.level_id.level <= self.approve_level) or (
            self.state != 'to approve')

    def _user_validation(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1).sudo()
        if not self.x_is_interface:
            if employee.level_id.approval_validation(
                    'account.move', self.amount_total, False):
                return True
            else:
                manager = employee.parent_id
                employee_manager = manager.name or 'Administrator'
                if manager:
                    self.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=manager.user_id.id
                    )
                    self.state = 'to approve'
                    self.approve_level = employee.level_id.level
                    self.env.cr.commit()  # pylint: disable=invalid-commit
                raise ValidationError(
                    _(
                        'You cannot validate this document due limitation policy. Please contact (%s)\n ไม่สามารถดำเนินการได้เนื่องจากเกินวงเงินที่กำหนด กรุณาติดต่อ (%s)',
                        employee_manager,
                        employee_manager))

    def action_post(self):
        for rec in self:
            rec._user_validation()
            rec = super().action_post()
            self.env['mail.activity'].sudo().search(
                [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
            ).unlink()
            return rec

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
