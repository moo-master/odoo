from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self):
        res = super().reverse_moves()
        ac_move_ids = self._context.get('active_ids', False)
        credit_note = self.env['account.move'].browse([res.get('res_id')])
        credit_note.write({
            'x_invoice_id': ac_move_ids[0]
        })
        return res
