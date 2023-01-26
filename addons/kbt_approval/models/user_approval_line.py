from odoo import models, fields


class UserApprovalLine(models.Model):
    _name = 'user.approval.line'
    _description = 'Approval Line'

    move_id = fields.Many2one(
        string='Account Move',
        comodel_name='account.move',
    )
    sale_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
    )
    purchase_id = fields.Many2one(
        string='Purchase Order',
        comodel_name='purchase.order',
    )
    is_approve = fields.Boolean(
        string='Approve',
        default=False,
    )
    approve_date = fields.Date(
        string='Approve Date',
    )
    manager_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Manager',
    )
    sequence = fields.Integer('Sequence')

    def confirm_approval_line(self, manager):
        approval = self.filtered(lambda x: x.manager_id.id == manager.id)
        if approval:
            approval.write({
                'is_approve': True,
                'approve_date': fields.Date.today()
            })
        return True
