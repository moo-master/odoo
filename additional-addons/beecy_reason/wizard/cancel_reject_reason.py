from odoo import models, fields


class CancelRejectReason(models.TransientModel):
    '''
    Cancel / Reject Reason
    '''
    _name = 'cancel.reject.reason'
    _description = 'Cancel Reject Reason'

    def _domain_reason_id(self):
        domain = self.env['res.reason']._get_domain_reason(
            self._context.get('active_model', self._name),
            False,
        )
        return domain

    reason_id = fields.Many2one(
        comodel_name='res.reason',
        string='Reason',
        required=False,
        domain=lambda self: self._domain_reason_id(),
    )

    description = fields.Text(
        string='Description',
        required=False,
    )

    is_description = fields.Boolean(
        string='Is Description',
        related='reason_id.is_description',
    )

    def button_confirm(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        state = self._context.get('state', 'reject')
        model = self.env[active_model].browse(active_id)
        reason_text = self._get_reason_text()
        getattr(
            model,
            f'action_{state}_reason',
            lambda *args, **kwargs: True
        )()
        model.write({
            f'{state}_reason': reason_text,
            'state': state,
        })

    def _get_reason_text(self):
        reason_text = self.reason_id.name
        if self.reason_id.is_description:
            reason_text = self.description
        return reason_text
