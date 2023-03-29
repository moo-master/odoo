from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(
        selection_add=[
            ('reject', 'Rejected'),
        ]
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
        string='Cancel Reason',
    )
    reject_reason = fields.Char(
        string='Reject Reason',
    )
    approval_ids = fields.One2many(
        'user.approval.line',
        'purchase_id',
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
            _, res = employee.level_id.approval_validation(
                'purchase.order', rec.amount_total, False, employee, [])
            rec.write({
                'is_over_limit': not res
            })

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
            approve = []
            approve, res = employee.level_id.approval_validation(
                'purchase.order', self.amount_total, False, employee, approve)
            if not approve or res:
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
                            {'approval_ids': [(0, 0, {'manager_id': line}) for line in approve]}
                        )
                    self.write(val)
                    self.approval_ids.confirm_approval_line(employee)
                    self.env.cr.commit()  # pylint: disable=invalid-commit

                if manager.is_send_email:
                    # Email Function
                    self.env['approval.email.wizard'].with_context(
                        id=self.id,
                        model=self._name,
                        cids=1,
                        menu_id='purchase.menu_purchase_root',
                        action='purchase.purchase_rfq',
                    ).create({
                        'employee_id': employee.id,
                        'manager_id': manager.id,
                        'name': 'Purchase Order',
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

    def button_confirm(self):
        for rec in self:
            rec._user_validation()
            rec = super().button_approve()
            self.env['mail.activity'].sudo().search(
                [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
            ).unlink()
            return rec

    def action_cancel_reject_reason_wizard(self):
        view = self.env.ref('beecy_reason.view_cancel_reject_reason_form')
        context = dict(
            self.env.context,
            active_model='purchase.order',
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
