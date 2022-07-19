from odoo import models, fields


class CreateReason(models.TransientModel):
    _name = 'create.reason'
    _description = 'Create Reason'

    reason = fields.Char(
        string="Reason",
        required=True,
    )

    def create_reason(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        account_type = False
        ir_model = self.env['ir.model'].search([
            ('model', '=', active_model)
        ])
        account_type = (
            active_model == 'account.move'
            and self.env[active_model].browse(active_id).move_type
        )
        reason = self._search_reason()
        if reason:
            reason.update_model_in_reason(
                ir_model.id,
                account_type,
            )
        else:
            self.env['res.reason'].create(
                self._prepare_data_reason(
                    ir_model.ids,
                    account_type,
                )
            )
        return True

    def _search_reason(self):
        reason = self.env['res.reason'].search([
            ('name', '=', self.reason)
        ])
        return reason

    def _prepare_data_reason(self, model_ids, account_type):
        return {
            'name': self.reason,
            'model_ids': [(6, 0, model_ids)],
            'account_type': account_type,
        }
