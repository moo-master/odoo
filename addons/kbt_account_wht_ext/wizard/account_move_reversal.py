from odoo import models, fields


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    reason_id = fields.Many2one(
        comodel_name='res.reason',
        string='Reason',
    )

    def reverse_moves(self):
        res = super().reverse_moves()
        ac_move_ids = self._context.get('active_ids', [False])
        credit_note = self.env['account.move'].browse([res.get('res_id')])
        credit_note.write({
            'x_invoice_id': ac_move_ids[0],
            'reason_id': self.reason_id,
        })
        return res
