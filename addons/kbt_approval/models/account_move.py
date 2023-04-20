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
        'move_id',
        string='Approval'
    )
    is_officer_approved = fields.Boolean(
        string='Officer Approved',
        copy=False,
    )
    is_ae_approver_approved = fields.Boolean(
        string='Approver Approved',
        copy=False,
    )
    is_ae_manager_approved = fields.Boolean(
        string='Manager Approved',
        copy=False,
    )
    is_hide_approver_button = fields.Boolean(
        string='Hide button',
        compute='_compute_is_hide_approver_button',
    )
    is_hide_manager_button = fields.Boolean(
        string='Hide button',
        compute='_compute_is_hide_manager_button',
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
    is_can_user_reject = fields.Boolean(
        string='User can reject',
        compute='_compute_is_can_user_reject'
    )

    def _compute_is_can_user_approve(self):
        for rec in self:
            employee = self.env['hr.employee'].search(
                [('user_id', '=', rec.env.uid)], limit=1).sudo()
            rec.write({'is_can_user_approve': (rec.is_skip_level and (
                employee.level_id.level == rec.approve_skip_level)) or (
                employee.level_id == rec.approve_level_id)
            })

    def _compute_is_can_user_reject(self):
        for rec in self:
            employee = self.env['hr.employee'].search(
                [('user_id', '=', rec.env.uid)], limit=1).sudo()
            rec.write({'is_can_user_reject': (rec.is_skip_level and (
                employee.level_id.level >= rec.approve_skip_level)) or (
                employee.level_id.level >= rec.approve_level_id.level)
            })

    def skip_level(self, employee):
        level = employee.parent_id.level_id.get_authorize(
            'account.move', self.move_type, self.amount_total)
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

    @api.depends('amount_total')
    def _compute_is_hide_approver_button(self):
        for rec in self:
            is_hide_approver_button = False
            if rec.journal_id.account_entry == 'ar':
                is_hide_approver_button = (rec.state != 'to approve') or \
                    not (self.env.user == rec.company_id.ar_approver_uid) or \
                    not rec.is_officer_approved or \
                    rec.is_ae_approver_approved
            else:
                is_hide_approver_button = (rec.state != 'to approve') or \
                    not (self.env.user == rec.company_id.ap_approver_uid) or \
                    not rec.is_officer_approved or \
                    rec.is_ae_approver_approved
            rec.write({
                'is_hide_approver_button': is_hide_approver_button
            })

    @api.depends('amount_total')
    def _compute_is_hide_manager_button(self):
        for rec in self:
            is_hide_manager_button = False
            if rec.journal_id.account_entry == 'ar':
                is_hide_manager_button = (rec.state != 'to approve') or \
                    not (rec.env.user == rec.company_id.ar_manager_uid) or \
                    not rec.is_officer_approved or \
                    not rec.is_ae_approver_approved
            else:
                is_hide_manager_button = (rec.state != 'to approve') or \
                    not (rec.env.user == rec.company_id.ap_manager_uid) or \
                    not rec.is_officer_approved or \
                    not rec.is_ae_approver_approved
            rec.write({
                'is_hide_manager_button': is_hide_manager_button
            })

    @api.depends('restrict_mode_hash_table', 'state')
    def _compute_show_reset_to_draft_button(self):
        for move in self:
            move.show_reset_to_draft_button = not move.restrict_mode_hash_table and move.state in (
                'posted', 'cancel', 'reject')

    def user_validation(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1).sudo()
        if not self.x_is_interface:
            if not employee.parent_id.level_id:
                raise ValidationError(_('Your manager do not have level.'))
            if (employee.parent_id.level_id.level - employee.level_id.level
                    > 1) and (not self.is_skip_level) and (not employee.parent_id):
                self.is_skip_level = True
                self.skip_level(employee)
            approve = []
            approve, res = employee.level_id.approval_validation(
                'account.move', self.amount_total, self.move_type, employee, approve)

            if self.journal_id.account_entry == 'ap':
                ae_employee_id = self.env['hr.employee'].search(
                    [('user_id', '=', self.env.company.ap_approver_uid.id)], limit=1).sudo()
                ae_manager_employee_id = self.env['hr.employee'].search(
                    [('user_id', '=', self.env.company.ap_manager_uid.id)], limit=1).sudo()
                approve.append(ae_employee_id.id)
                approve.append(ae_manager_employee_id.id)
            else:
                ae_employee_id = self.env['hr.employee'].search(
                    [('user_id', '=', self.env.company.ar_approver_uid.id)], limit=1).sudo()
                ae_manager_employee_id = self.env['hr.employee'].search(
                    [('user_id', '=', self.env.company.ar_manager_uid.id)], limit=1).sudo()
                approve.append(ae_employee_id.id)
                approve.append(ae_manager_employee_id.id)

            if not approve or res:
                self.approval_ids.confirm_approval_line(employee)
                self.is_officer_approved = True
                self.action_post()
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
            rec.action_send_ae_approve()
            rec.action_send_ae_manager_approve()
            rec = super().action_post()
            self.env['mail.activity'].sudo().search(
                [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
            ).unlink()
            return rec

    def action_approver_approve(self):
        self.is_ae_approver_approved = True
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1).sudo()
        self.approval_ids.confirm_approval_line(employee)
        self.action_post()

    def action_manager_approve(self):
        self.is_ae_manager_approved = True
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1).sudo()
        self.approval_ids.confirm_approval_line(employee)
        self.action_post()

    def action_send_ae_manager_approve(self):
        if not self.is_ae_manager_approved:
            # notice to manager to approve
            approver = self.env['res.users']
            if not self.journal_id.account_entry:
                raise ValidationError(
                    _('Please set Account Entries of journal'))
            if self.journal_id.account_entry == 'ap':
                approver = self.company_id.ap_manager_uid
            else:
                approver = self.company_id.ar_manager_uid
            if approver:
                self.activity_schedule(
                    'kbt_approval.mail_activity_data_to_approve',
                    user_id=approver.id
                )
            self.env.cr.commit()  # pylint: disable=invalid-commit
            massage = 'Please contact (%s) for approving this document'
            massage += '\nโปรดติดต่อ (%s) สำหรับการอนุมัติเอกสาร'
            raise ValidationError(
                _(
                    massage,
                    approver.name,
                    approver.name))

    def action_send_ae_approve(self):
        if not self.is_ae_approver_approved:
            # notice to approver to approve
            approver = self.env['res.users']
            if not self.journal_id.account_entry:
                raise ValidationError(
                    _('Please set Account Entries of journal'))
            if self.journal_id.account_entry == 'ap':
                approver = self.company_id.ap_approver_uid
            else:
                approver = self.company_id.ar_approver_uid
            if approver:
                self.activity_schedule(
                    'kbt_approval.mail_activity_data_to_approve',
                    user_id=approver.id
                )
            self.env.cr.commit()  # pylint: disable=invalid-commit
            massage = 'Please contact (%s) for approving this document'
            massage += '\nโปรดติดต่อ (%s) สำหรับการอนุมัติเอกสาร'
            raise ValidationError(
                _(
                    massage,
                    approver.name,
                    approver.name))

    def action_cancel_reject_reason_wizard(self):
        view = self.env.ref('beecy_reason.view_cancel_reject_reason_form')
        context = dict(
            self.env.context,
            active_model='account.move',
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
