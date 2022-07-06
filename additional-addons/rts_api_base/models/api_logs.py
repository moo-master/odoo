from datetime import datetime, timedelta
from odoo import api, fields, models


class APILogs(models.Model):
    _name = 'api.logs'
    _description = 'API Logs'
    _order = 'create_date desc'

    service_id = fields.Many2one(
        string='Service',
        comodel_name='api.service',
        required=True,
        readonly=True,
    )

    route_id = fields.Many2one(
        string='Route',
        comodel_name='api.service.route',
        required=True,
        readonly=True,
    )

    route_reference = fields.Char(
        related='route_id.reference'
    )

    route_type = fields.Selection(
        related='route_id.route_type'
    )

    route_method = fields.Selection(
        related='route_id.method'
    )

    status = fields.Selection(
        selection=[
            ('process', 'Processing'),
            ('success', 'Success'),
            ('fail', 'Fail')
        ],
        default='process',
        readonly=True,
        required=True,
    )

    requested_by_uid = fields.Many2one(
        string='Requested by User',
        comodel_name='res.users',
        readonly=True,
        default=lambda self: self.env.user,
    )

    requested_by = fields.Char(
        string='Requested by',
        readonly=True,
        default=lambda self: self.env.user.name,
    )

    '''
    Request
    '''
    request_datetime = fields.Datetime(
        default=lambda self: self._default_request_datetime(),
        readonly=True
    )
    request_url = fields.Char(
        readonly=True
    )
    request_header = fields.Text(
        readonly=True
    )
    request_query_string = fields.Text(
        readonly=True
    )
    request_body = fields.Text(
        readonly=True
    )

    '''
    Response
    '''
    response_status_code = fields.Char(
        readonly=True
    )
    response_datetime = fields.Datetime(
        readonly=True
    )
    response_header = fields.Text(
        readonly=True
    )
    response_body = fields.Text(
        readonly=True
    )

    def _default_request_datetime(self) -> datetime:
        return datetime.utcnow()

    def _get_log_detail(self) -> list:
        return list(self.mapped(lambda v: {
            'route_reference': v['route_reference'],
            'status': v['status'],
            'request_url': v['request_url'],
            'request_header': v['request_header'],
            'request_query_string': v['request_query_string'],
            'request_body': v['request_body'],
            'response_status_code': v['response_status_code'],
            'response_body': v['response_body'],
        }))

    @api.model
    def _cron_clear_interface_history(self) -> bool:
        duration_days: int = int(
            self.env['ir.config_parameter'].sudo().get_param(
                'api.log.duration',
                90
            )
        )

        expired_date: datetime = datetime.today() - timedelta(
            days=duration_days
        )
        sql: str = '''
            DELETE FROM api_logs WHERE DATE(create_date) < %s;
        '''
        self._cr.execute(sql, (expired_date.strftime('%Y-%m-%d'),))
        return True
