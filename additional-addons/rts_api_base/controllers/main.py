
import json
import logging
from functools import wraps
from datetime import datetime
from typing import Any
from odoo import http
from odoo.http import request

from ..models.api_logs import APILogs
from ..models.api_service import APIServiceRoute

_logger: logging.Logger = logging.getLogger(__name__)


class APIBase(http.Controller):

    @classmethod
    def api_wrapper(self, route_references: list, request_type: str = 'json'):
        '''
        API wrapper validate route and create log
        @params route_reference list of api.service.route reference
        @params request_type route type http or json
        '''
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                request_type_error: dict = {
                    'http': http.Response('{"error": true}', status=400),
                    'json': {'error': True},
                }
                route: APIServiceRoute = request.env['api.service.route']\
                    .sudo().search([
                        ('reference', 'in', route_references),
                        ('route_type', '=', 'incoming'),
                        ('method', '=', request.httprequest.method.lower()),
                        ('active', '=', True),
                    ], limit=1)

                if route:
                    log: APILogs = self._log_request(route)
                    response: Any = None
                    error: str = None
                    try:
                        with request.env.cr.savepoint():
                            response: Any = func(*args, **kwargs)
                    except Exception as e:
                        error = str(e)
                    self._log_response(log, response, error)
                    return response
                return request_type_error[request_type]
            return wrapper
        return decorator

    @classmethod
    def _log_request(self, route: APIServiceRoute) -> APILogs:
        return request.env['api.logs'].sudo().create(
            self._prepare_log_request(route)
        )

    @classmethod
    def _prepare_log_request(self, route: APIServiceRoute) -> dict:
        params: dict = dict(request.params)
        for key in dict(request.params):
            params[key] = str(params[key])
        return {
            'service_id': route.service_id.id,
            'route_id': route.id,
            'request_url': request.httprequest.url,
            'request_header': json.dumps(dict(request.httprequest.headers)),
            'request_query_string': json.dumps(params),
            'request_body': (
                getattr(request, 'jsonrequest', False)
                and json.dumps(request.jsonrequest)
            ),
        }

    @classmethod
    def _log_response(
        self,
        log: APILogs,
        response: Any,
        error: str = None
    ) -> None:
        log.sudo().write(
            self._prepare_log_response(log.route_id, response, error)
        )
        log_detail: list = log._get_log_detail()
        _logger.debug(f'\n>>> API Logs:\n{json.dumps(log_detail, indent=2)}')

    @classmethod
    def _prepare_log_response(
        self,
        route: APIServiceRoute,
        response: Any,
        error: str = None
    ) -> dict:
        value: dict = {
            'response_status_code': -1,
            'response_datetime': datetime.utcnow(),
            'response_body': error,
            'status': 'fail'
        }
        if response is not None:
            if isinstance(response, http.Response):
                body = (
                    response.response
                    and response.response[0].decode()
                ) or False
                value.update({
                    'response_status_code': response.status_code,
                    'response_header': json.dumps(dict(response.headers)),
                    'response_body': body and body.replace('\x00', '\uFFFD'),
                })
            elif isinstance(response, dict):
                value.update({
                    'response_status_code': 200,
                    'response_body': json.dumps(dict(response))
                })
            value['status'] = request.env['api.service'].sudo()\
                ._get_log_status_incoming(route, response)
        return value
