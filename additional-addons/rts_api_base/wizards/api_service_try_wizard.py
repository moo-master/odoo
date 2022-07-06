import json
from odoo import models, fields


class APIServiceTryWizard(models.TransientModel):
    _name: str = 'api.service.try.wizard'
    _description: str = 'API Service Try Wizard'

    service_id = fields.Many2one(
        comodel_name='api.service',
        required=True,
    )

    route_id = fields.Many2one(
        comodel_name='api.service.route',
        domain='''[
            ('service_id', '=', service_id),
        ]''',
        required=True,
    )

    path_params = fields.Text()

    headers = fields.Text(
        default='{}',
        required=True,
    )

    params = fields.Text(
        default='{}',
        required=True,
    )

    data = fields.Text(
        default='{}',
        required=True,
    )

    def action_confirm(self) -> None:
        self.env['api.service'].requests(
            self.route_id.reference,
            path_params=self.path_params and json.loads(self.path_params),
            headers=json.loads(self.headers),
            params=json.loads(self.params),
            data=json.loads(self.data)
        )
