from odoo import models, fields, api
from datetime import datetime


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _domain_reason_id(self):
        context = dict(self.env.context or {})
        domain = self.env['res.reason']._get_domain_reason(
            context.get('model_name'),
            context.get('move_type')
        )
        return domain

    vendor_ref = fields.Char(
        string='Vendor Reference',
    )

    accounting_date = fields.Date(
        string='Accounting Date',
    )

    reason_id = fields.Many2one(
        string='Select Reason',
        comodel_name='res.reason',
        ondelete='cascade',
        domain=lambda self: self._domain_reason_id(),
    )
    reason_description = fields.Char(
        'Reason Description',)
    is_reason_description = fields.Boolean(
        related='reason_id.is_description'
    )

    def reverse_moves(self):
        res = super(AccountMoveReversal, self).reverse_moves()
        move_type = self._context.get('default_move_type', False)
        for move in self.new_move_ids:
            move.write({
                'ref': self.vendor_ref,
                'date': self.accounting_date or datetime.utcnow().date(),
                'reason_id': self.reason_id.id,
                'cn_dn_reason': self.reason_description or self.reason_id.name,
                'invoice_ref_id': self._context.get('active_id', False),
            })
            if move_type == 'out_invoice':
                move.write({
                    'move_type': 'out_refund'
                })
            elif move_type == 'in_invoice':
                move.write({
                    'move_type': 'in_refund'
                })
        return res

    @api.onchange('reason_id')
    def _onchange_reason_id(self):
        for rec in self:
            rec.reason_description = False
