import json
import requests
import validators
import logging
from datetime import datetime
from typing import Any, Callable, List
from requests.models import Response
from odoo import models, fields, api, http, _
from odoo.exceptions import ValidationError

from .api_logs import APILogs

_logger: logging.Logger = logging.getLogger(__name__)
requests_wrapper: dict = {
    'get': requests.get,
    'post': requests.post,
    'put': requests.put,
    'patch': requests.patch,
    'delete': requests.delete,
}


class APIServiceRoute(models.Model):
    _name: str = 'api.service.route'
    _description: str = 'API Service Route'
    _rec_name: str = 'reference'
    _sql_constraints: List[tuple] = [
        ('key', 'unique(service_id, key)', _('Key must be unique per service'))
    ]

    reference = fields.Char(
        compute='_compute_reference',
        store=True,
    )

    name = fields.Char(
        required=True
    )

    key = fields.Char(
        required=True
    )

    service_id = fields.Many2one(
        comodel_name='api.service',
        ondelete='cascade',
    )

    service_key = fields.Char(
        related='service_id.key',
    )

    route_type = fields.Selection(
        string='Type',
        selection=[
            ('incoming', 'Incoming'),
            ('outgoing', 'Outgoing'),
        ],
        default='outgoing',
        required=True,
    )

    method = fields.Selection(
        string='method',
        selection=[(key, key.upper()) for key in requests_wrapper.keys()],
        required=True
    )

    path = fields.Char()

    url = fields.Char(
        compute='_compute_url',
        store=True
    )

    is_required_auth_token = fields.Boolean(
        string='Required Auth Token',
        default=False
    )

    active = fields.Boolean(
        default=True,
    )

    @api.depends('service_id.key', 'key')
    def _compute_reference(self) -> None:
        for record in self:
            record.reference = False
            if record.service_id.key and record.key:
                record.reference = f'{record.service_id.key}.{record.key}'

    @api.depends('route_type', 'service_id.base_url', 'path')
    def _compute_url(self) -> None:
        for record in self:
            record.url = False
            if record.route_type == 'incoming':
                record.url = record.path
            if record.route_type == 'outgoing' and record.service_id.base_url:
                path: str = ['', f'/{record.path}'][bool(record.path)]
                url: str = f'{record.service_id.base_url}{path}'
                record.url = url


class APIService(models.Model):
    _name: str = 'api.service'
    _description: str = 'API Service'
    _rec_name: str = 'reference'
    _sql_constraints: List[tuple] = [
        ('key', 'unique(key)', _('Key must be unique'))
    ]

    reference = fields.Char(
        compute='_compute_reference'
    )

    name = fields.Char(
        required=True,
    )

    key = fields.Char(
        required=True,
    )

    base_url = fields.Char(
        required=True,
    )

    route_ids = fields.One2many(
        string='Routes',
        comodel_name='api.service.route',
        inverse_name='service_id',
    )

    route_count = fields.Integer(
        compute='_compute_route_count'
    )

    active = fields.Boolean(
        default=True,
    )

    @api.depends('name', 'key')
    def _compute_reference(self) -> None:
        for record in self:
            record.reference = f'[{record.key}] {record.name}'

    @api.depends('route_ids')
    def _compute_route_count(self) -> None:
        for record in self:
            record.route_count = 0
            if record.route_ids:
                record.route_count = len(record.route_ids)

    @api.constrains('base_url')
    def _check_base_url(self) -> None:
        for record in self:
            valid: Any = validators.url(record.base_url)
            if isinstance(valid, validators.ValidationFailure):
                raise ValidationError(_('Base url is invalid url.'))

    @api.model
    def requests(
        self,
        key: str,
        *,
        path_params: dict = None,
        headers: dict = None,
        timeout: float = None,
        **kwargs
    ) -> Response:
        '''
        Requests API by key which is `service_key.route_key`
        '''
        route: APIServiceRoute = self._get_route(key)
        timeout: float = self._get_timeout(timeout)
        headers: dict = headers or self._prepare_header(route)
        url: str = (
            (path_params and route.url.format(**path_params))
            or route.url
        )

        response: Response = None
        error: str = None
        log: APILogs = self._log_request(
            route,
            url,
            headers,
            kwargs.get('params'),
            kwargs.get('data')
        )
        try:
            response = requests_wrapper[route.method](
                url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
        except Exception as e:
            error = str(e)
        self._log_response(log, route, response, error)
        return response

    def _get_route(self, key: str) -> APIServiceRoute:
        route: APIServiceRoute = self.env['api.service.route'].search([
            ('reference', '=', key),
            ('active', '=', True)
        ])
        if not route or not route.service_id.active:
            raise ValidationError(_('API service route is invalid.'))
        return route

    def _get_timeout(self, timeout: float) -> float:
        if not timeout:
            timeout: float = float(
                self.env['ir.config_parameter'].sudo().get_param(
                    'api.request.timeout',
                    '30'
                )
            )
        return timeout

    def _log_request(
        self,
        route: APIServiceRoute,
        url: str,
        header: dict,
        params: dict = False,
        data: dict = False
    ) -> APILogs:
        return self.env['api.logs'].sudo().create(
            self._prepare_log_request(route, url, header, params, data)
        )

    def _log_response(
        self,
        log: APILogs,
        route: APIServiceRoute,
        response: Response,
        error: str = None
    ) -> None:
        log.sudo().write(
            self._prepare_log_response(route, response, error)
        )
        log_detail: list = log._get_log_detail()
        _logger.debug(f'\n>>> API Logs:\n{json.dumps(log_detail, indent=2)}')

    def _get_service_method(
        self,
        route: APIServiceRoute,
        prefix: str
    ) -> Callable:
        return (
            getattr(self, f'{prefix}_{route.service_id.key}_{route.key}', None)
            or getattr(self, f'{prefix}_{route.service_id.key}', None)
        )

    def _prepare_header(self, route: APIServiceRoute) -> dict:
        header: dict = {}
        if route.is_required_auth_token:
            header['Authorization'] = self._get_auth_token(route)
        method: Callable = self._get_service_method(route, '_prepare_header')
        if method:
            header.update(method(route))
        return header

    def _get_auth_token(self, route: APIServiceRoute) -> dict:
        value: str = 'token'
        method: Callable = self._get_service_method(route, '_get_auth_token')
        if method:
            value = method(route)
        return value

    def _prepare_log_request(
        self,
        route: APIServiceRoute,
        url: str,
        header: dict,
        params: dict,
        data: dict
    ) -> dict:
        value: dict = {
            'service_id': route.service_id.id,
            'route_id': route.id,
            'request_url': url,
            'request_header': header and json.dumps(header),
            'request_query_string': params and json.dumps(params),
            'request_body': data and json.dumps(data),
        }
        method: Callable = self._get_service_method(route,
                                                    '_prepare_log_request')
        if method:
            value.update(method(route, url, header, params, data))
        return value

    def _prepare_log_response(
        self,
        route: APIServiceRoute,
        response: Response,
        error: str
    ) -> dict:
        value: dict = {
            'response_status_code': -1,
            'response_datetime': datetime.utcnow(),
            'response_body': error,
            'status': 'fail'
        }
        if response:
            value.update({
                'response_status_code': response.status_code,
                'response_header': json.dumps(dict(response.headers)),
                'response_body': response.text.replace('\x00', '\uFFFD'),
                'status': self._get_log_status(route, response)
            })
        method: Callable = self._get_service_method(route,
                                                    '_prepare_log_response')
        if method:
            value.update(method(route, response, error))
        return value

    def _get_log_status(
        self,
        route: APIServiceRoute,
        response: Response
    ) -> str:
        status: str = ['fail', 'success'][200 <= response.status_code < 300]
        method: Callable = self._get_service_method(route,
                                                    '_get_log_status')
        if method:
            status = method(route, response)
        return status

    def _get_log_status_incoming(
        self,
        route: APIServiceRoute,
        response: Any
    ) -> str:
        status: str = 'success'
        if isinstance(response, http.Response):
            status = ['fail', 'success'][200 <= response.status_code < 300]
        method: Callable = self._get_service_method(
            route,
            '_get_log_status_incoming'
        )
        if method:
            status = method(route, response)
        return status
