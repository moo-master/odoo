from odoo import fields, models, _


class AccountDebitNoteReason(models.TransientModel):
    _name = 'account.debit.note.reason'
    _description = 'Debit Note Reason'

    def _domain_reason_id(self):
        move_type = self._context.get('default_move_type', False)
        domain = self.env['res.reason']._get_domain_reason(
            self._context.get('model_name'),
            move_type
        )
        return domain

    reason_id = fields.Many2one(
        'res.reason',
        string='Reason',
        domain=lambda self: self._domain_reason_id(),
    )
    reason_description = fields.Char('Reason Description')
    is_reason_description = fields.Boolean(
        related='reason_id.is_description'
    )

    def action_debit_note_moves(self):
        acc_move = self.env['account.move'].search([
            ('id', '=', self.env.context.get('active_id')),
        ])
        move_type = self._context.get('default_move_type', False)
        acc_move_dn = acc_move.copy({
            'invoice_date': fields.Date.today(),
            'invoice_ref_id': acc_move.id,
            'cn_dn_reason': self.reason_description or self.reason_id.name,
            'reason_id': self.reason_id.id, })
        acc_move_dn.write({
            'journal_id': acc_move.journal_id.id,
        })
        if move_type in ('out_invoice', 'out_refund', 'out_debit'):
            type_debit = 'out_debit'
            acc_move_dn.write({
                'move_type': self._context.get('move_type', 'out_debit'),
            })
        else:
            type_debit = 'in_debit'
            acc_move_dn.write({
                'move_type': self._context.get('move_type', 'in_debit')
            })
        context = dict(self.env.context, default_move_type=type_debit)
        return {
            'name': _('Debit Note'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': acc_move_dn.id,
            'domain': [('move_type', '=', type_debit)],
            'view_id': self.env.ref('beecy_account.view_move_form_inherit_beecy_accont').id,
            'context': context,
        }
