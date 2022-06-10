from odoo import models, fields


class ResReason(models.Model):
    '''
    Reason
    '''
    _name = 'res.reason'
    _rec_name = 'name'
    _description = 'Reason'

    name = fields.Char(
        string='Name',
        required=True,
    )

    model_ids = fields.Many2many(
        comodel_name='ir.model',
        relation='model_reason_rel',
        column1='model_id',
        column2='reason_id',
        string='Models',
    )

    account_type = fields.Selection(
        string='Account Type',
        selection=[
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
        ],
        required=False,
    )

    is_description = fields.Boolean(
        string='Is Description',
        default=False,
    )

    # Force sudo() line 43 because ir.model about Access Rights in Account move
    def _get_domain_reason(self, model_name, move_type):
        model = self.env['ir.model'].sudo().search([
            ('model', '=', model_name)
        ])
        if move_type:
            domain = [
                '|', '&',
                ('model_ids', '=', model.id),
                ('account_type', '=', move_type),
                ('model_ids', '=', False),
            ]
        else:
            domain = [
                '|',
                ('model_ids', '=', model.id),
                ('model_ids', '=', False),
            ]
        return domain

    def update_model_in_reason(self, model_id, account_type):
        self.write({
            'model_ids': [(4, model_id)],
            'account_type': account_type,
        })
        return True
