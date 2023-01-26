from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(
        selection_add=[
            ('to approve', 'To Approve'),
            ('reject', 'Rejected'),
        ],
        ondelete={
            'to approve': 'set default',
            'reject': 'set default',
        }
    )
    approve_level = fields.Integer(
        'approve level',
        default=0
    )
    is_approve = fields.Boolean(
        compute='_compute_approve',
        default=True
    )
    cancel_reason = fields.Char(
        string='Cancel Reason Note',
    )
    reject_reason = fields.Char(
        string='Reject Reason Note',
    )
    approval_ids = fields.One2many(
        'user.approval.line',
        'move_id',
        string='Approval'
    )

    @api.depends('restrict_mode_hash_table', 'state')
    def _compute_show_reset_to_draft_button(self):
        for move in self:
            move.show_reset_to_draft_button = not move.restrict_mode_hash_table and move.state in (
                'posted', 'cancel', 'reject')

    def _compute_approve(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1).sudo()
        self.is_approve = (
            employee.level_id.level <= self.approve_level) \
            or (self.state != 'to approve') \
            or (employee.level_id.level > self.approve_level + 1)

    def _user_validation(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1).sudo()
        if not self.x_is_interface:
            if employee.level_id.approval_validation(
                    'account.move', self.amount_total, False):
                self.approval_ids.confirm_approval_line(employee)
                return True
            else:
                manager = employee.parent_id
                employee_manager = manager.name or 'Administrator'
                if manager:
                    self.activity_schedule(
                        'kbt_approval.mail_activity_data_to_approve',
                        user_id=manager.user_id.id
                    )
                    self.write({
                        'approval_ids': [(0, 0, {'manager_id': manager.id})],
                        'state': 'to approve',
                        'approve_level': employee.level_id.level,
                    })
                    self.approval_ids.confirm_approval_line(employee)
                    self.env.cr.commit()  # pylint: disable=invalid-commit

                if manager.is_send_email:
                    # Email Function
                    self.env['approval.email.wizard'].with_context(
                        id=self.id,
                        model=self._name,
                        cids=1,
                        menu_id='account_accountant.menu_accounting',
                        action='account.action_move_out_invoice_type',
                    ).create({
                        'employee_id': employee.id,
                        'manager_id': manager.id,
                        'name': dict(self._fields['move_type'].selection).get(self.move_type),
                        'order_name': self.name,
                        'order_amount': self.amount_total,
                    }).send_approval_email()

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
