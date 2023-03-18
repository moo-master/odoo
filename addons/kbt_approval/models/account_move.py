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
    is_over_limit = fields.Boolean(
        compute='_compute_is_over_limit',
        string='Over Limit',
    )

    @api.depends('amount_total')
    def _compute_is_over_limit(self):
        for rec in self:
            employee = self.env['hr.employee'].sudo().search(
                [('user_id', '=', self.env.uid)], limit=1)
            rec.write({
                'is_over_limit': not employee.level_id.check_over_limit(
                    'account.move', rec.amount_total, False
                )
            })

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
            approve = employee.level_id.approval_validation(
                'account.move', self.amount_total, self.move_type, employee)
            if not approve:
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
                    val = {
                        'state': 'to approve',
                        'approve_level': employee.level_id.level,
                    }
                    if not self.approval_ids:
                        val.update(
                            {'approval_ids': [(0, 0, {'manager_id': line})
                                              for line in approve]}
                        )
                    self.write(val)
                    self.approval_ids.confirm_approval_line(employee)
                    self.env.cr.commit()  # pylint: disable=invalid-commit
                    max_level = [rec.level_id.level for rec in
                                 self.approval_ids.filtered(
                                     lambda r: r
                                 ).mapped('manager_id').sudo()]
                    is_approve_level = [rec.level_id.level
                                        for rec in self.approval_ids.filtered(
                                            lambda r: r.is_approve
                                        ).mapped('manager_id').sudo()]

                    if is_approve_level:
                        if max(list(set(is_approve_level))) >= \
                                max(list(set(max_level))):
                            return True

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

                massage = 'Please contact (%s) for approving this document'
                massage += '\nโปรดติดต่อ (%s) สำหรับการอนุมัติเอกสาร'
                raise ValidationError(
                    _(
                        massage,
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
