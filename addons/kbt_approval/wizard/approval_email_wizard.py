from odoo import fields, models


class ApprovalEmailWizard(models.TransientModel):
    """
    Core Wizard for Sending Email Approval
    in sale.order purchase.order, account.move
    """
    _name = 'approval.email.wizard'
    _description = 'Approval Email Wizard'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee'
    )
    manager_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Manager'
    )
    name = fields.Char('Document Name')
    order_amount = fields.Float('Total Amount')
    order_name = fields.Char('Order Name')
    url = fields.Char('URL')

    def send_approval_email(self):
        # self.write({'url': request.httprequest.url})
        template = self.env.ref('kbt_approval.approval_email_template')
        template.send_mail(self.id, force_send=True)
