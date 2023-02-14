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
        ctx = dict(self.env.context)
        order_id = ctx.get('id')
        model = ctx.get('model')
        cids = ctx.get('cids')
        menu_id = self.env.ref(ctx.get('menu_id')).id
        action = self.env.ref(ctx.get('action')).id

        domain = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')

        # url Sample
        # http://localhost:8069/web#id=565&cids=1&menu_id=176&action=292&model=sale.order&view_type=form
        url = f'{domain}/web#id={order_id}&cids={cids}&menu_id={menu_id}&action={action}&model={model}&view_type=form'

        self.write({'url': url})
        template = self.env.ref('kbt_approval.approval_email_template')
        template.send_mail(self.id, force_send=True)
