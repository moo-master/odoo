from odoo import models, fields, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('to approve', 'To Approve'),
            ('reject', 'Rejected'),
        ]
    )
    approve_level_id = fields.Many2one(
        string='Approve Level',
        comodel_name='org.level'
    )
    cancel_reason = fields.Char(
        string='Cancel Reason',
    )
    reject_reason = fields.Char(
        string='Reject Reason',
    )
    approval_ids = fields.One2many(
        'user.approval.line',
        'sale_id',
        string='Approval'
    )
    is_approve_done = fields.Boolean(
        string='Approve Done'
    )
    is_skip_level = fields.Boolean(
        string="Skip Level",
        copy=False,
    )
    approve_skip_level = fields.Integer(
        string='Approve skip level',
        copy=False,
    )
    level_to_approve_skip_level = fields.Integer(
        string='Level to Approve skip level',
        copy=False,
    )
    is_can_user_approve = fields.Boolean(
        string='User can approve',
        compute='_compute_is_can_user_approve',
    )

    def _compute_is_can_user_approve(self):
        for rec in self:
            employee = self.env['hr.employee'].search(
                [('user_id', '=', rec.env.uid)], limit=1).sudo()
            rec.write({'is_can_user_approve': (rec.is_skip_level and (
                employee.level_id.level == rec.approve_skip_level)) or (
                employee.level_id == rec.approve_level_id)
            })

    def action_force_approve(self):
        return self.action_confirm()

    def action_draft(self):
        orders = self.filtered(
            lambda s: s.state in [
                'cancel', 'sent', 'reject'])
        return orders.write({
            'state': 'draft',
            'signature': False,
            'signed_by': False,
            'signed_on': False,
        })

    def skip_level(self, employee):
        level = employee.parent_id.level_id.get_authorize(
            'sale.order', False, self.amount_total)
        if level:
            self.activity_schedule(
                'kbt_approval.mail_activity_data_to_approve',
                user_id=employee.parent_id.user_id.id
            )
            val = {
                'state': 'to approve',
                'approve_skip_level': employee.parent_id.level_id.level,
                'level_to_approve_skip_level': level.org_level_id.level
            }
            if not self.approval_ids:
                val.update(
                    {'approval_ids': [
                        (0, 0, {'manager_id': employee.parent_id.id})
                    ]}
                )
            self.write(val)
            self.env.cr.commit()  # pylint: disable=invalid-commit

    def user_validation(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1).sudo()
        if not self.x_is_interface:
            if not employee.parent_id.level_id:
                raise ValidationError(_('Your manager do not have level.'))
            if (employee.parent_id.level_id.level
                    - employee.level_id.level > 1) and (not self.is_skip_level):
                self.skip_level(employee)
                self.is_skip_level = True
            approve = []
            approve, res = employee.level_id.approval_validation(
                'sale.order', self.amount_total, False, employee, approve)
            if not approve or res:
                self.approval_ids.confirm_approval_line(employee)
                if not self.require_signature:
                    self.action_confirm()
                else:
                    self.is_approve_done = True
                    self.state = 'draft'
                self.env['mail.activity'].sudo().search(
                    [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
                ).unlink()
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
                        'approve_level_id': manager.level_id,
                    }
                    if not self.approval_ids:
                        val.update(
                            {'approval_ids': [(0, 0, {'manager_id': line}) for line in approve]}
                        )
                    self.write(val)
                    self.approval_ids.confirm_approval_line(employee)
                    self.env.cr.commit()  # pylint: disable=invalid-commit

                if manager.is_send_email:
                    self.env['approval.email.wizard'].with_context(
                        id=self.id,
                        model=self._name,
                        cids=1,
                        menu_id='sale.sale_menu_root',
                        action='sale.action_quotations_with_onboarding',
                    ).create({
                        'employee_id': employee.id,
                        'manager_id': manager.id,
                        'name': 'Sale Order',
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

    def action_confirm(self):
        for rec in self:
            rec = super().action_confirm()
            self.env['mail.activity'].sudo().search(
                [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
            ).unlink()
            return rec

    def action_cancel_reject_reason_wizard(self):
        view = self.env.ref('beecy_reason.view_cancel_reject_reason_form')
        context = dict(
            self.env.context,
            active_model='sale.order',
            active_id=self.id,
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
