import attr
import pytest
from unittest.mock import MagicMock, Mock
from requests.models import Response
from pytest_tr_odoo.fixtures import env
from odoo import http
from odoo.exceptions import ValidationError
from .fixtures import *
from ..models.api_service import requests_wrapper


@pytest.fixture
def model_as(env):
    return env['api.service']


@pytest.fixture
def model_asr(env):
    return env['api.service.route']


def test_asr__compute_reference(route, service):
    assert route.reference == f'{route.service_id.key}.{route.key}'


@pytest.mark.parametrize('test_input', [
    {'route_type': 'incoming', 'path': False},
    {'route_type': 'incoming', 'path': '/as.c'},
    {'route_type': 'outgoing', 'path': False},
    {'route_type': 'outgoing', 'path': '/as.c'},
])
def test_asr__compute_url(model_asr, service, test_input):
    record = model_asr.create({
        'service_id': service.id,
        'name': 'Georgia',
        'key': 'geo',
        'method': 'get',
        **test_input
    })
    url: str = None
    if test_input['route_type'] == 'incoming':
        url = record.path
    elif test_input['route_type'] == 'outgoing':
        path: str = ['', f'/{record.path}'][bool(record.path)]
        url = f'{record.service_id.base_url}{path}'
    assert record.url == url


def test_as_compute_reference(service):
    assert service.reference == f'[{service.key}] {service.name}'


def test_as_compute_route_count(service):
    assert service.route_count == len(service.route_ids)


@pytest.mark.parametrize('test_input,expected', [
    ('jamal', False),
    ('jamal.info', False),
    ('https://jamal.info', True),
])
def test_as_check_base_url(model_as, test_input, expected):
    value = {
        'name': 'Custom',
        'key': 'cust',
        'base_url': test_input
    }
    import inspect
    if not expected:
        with pytest.raises(ValidationError) as excinfo:
            model_as.create(value)
        assert str(excinfo.value) == 'Base url is invalid url.'
    else:
        record = model_as.create(value)
        assert record.base_url == test_input


@pytest.mark.parametrize('test_input,expected', [
    (False, False),
    (True, True),
])
def test_get_route(model_as, service, route, test_input, expected):
    route.active = test_input
    if not expected:
        with pytest.raises(ValidationError) as excinfo:
            model_as._get_route(route.reference)
        assert str(excinfo.value) == 'API service route is invalid.'
    else:
        assert model_as._get_route(route.reference) == route


@pytest.mark.parametrize('test_input,expected', [
    (None, 100.0),
    (10, 10.0),
    (20, 20.0),
])
def test_get_timeout(env, model_as, test_input, expected):
    env['ir.config_parameter'].sudo().set_param(
        'api.request.timeout',
        '100'
    )
    assert model_as._get_timeout(test_input) == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'prefix': '_get_me'}, None),
    ({'prefix': '_get_me', 'service': True}, True),
    ({'prefix': '_get_me', 'route': True}, True),
])
def test_get_service_method(model_as, service, route,
                            test_input, expected):
    if test_input.get('route'):
        def _route():
            pass
        func_name = '_route'
        setattr(
            type(model_as),
            f'{test_input["prefix"]}_{route.service_id.key}_{route.key}',
            _route
        )
    elif test_input.get('service'):
        def _service():
            pass
        func_name = '_service'
        setattr(
            type(model_as),
            f'{test_input["prefix"]}_{route.service_id.key}',
            _service
        )
    method = model_as._get_service_method(route, test_input['prefix'])
    if expected:
        assert method.__name__ == func_name
    else:
        assert not method


@pytest.mark.parametrize('test_input,expected', [
    ({'method': None}, {}),
    ({'method': True}, {'f': 1}),
    ({'is_required_auth_token': True, 'method': None}, {}),
    ({'is_required_auth_token': True, 'method': True}, {'f': 1}),
])
def test_prepare_header(monkeypatch, mocker, model_as, route,
                        test_input, expected):
    route.is_required_auth_token = test_input.get('is_required_auth_token',
                                                  False)
    if test_input['method']:
        test_input['method'] = lambda a: expected
    monkeypatch.setattr(type(model_as), '_get_auth_token',
                        lambda a, b: 'token')
    spy_gat = mocker.spy(type(model_as), '_get_auth_token')
    monkeypatch.setattr(type(model_as), '_get_service_method',
                        lambda a, b, c: test_input['method'])
    spy_gsm = mocker.spy(type(model_as), '_get_service_method')
    data = model_as._prepare_header(route)
    if test_input.get('is_required_auth_token'):
        spy_gat.assert_called_once_with(model_as, route)
        expected.update({'Authorization': 'token'})
    spy_gsm.assert_called_once_with(model_as, route, '_prepare_header')
    assert data == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'method': None}, 'token'),
    ({'method': True}, 'e97e27b8-999d-42b4-8803-660318116b41'),
])
def test_get_auth_token(monkeypatch, mocker, model_as, route,
                        test_input, expected):
    if test_input['method']:
        test_input['method'] = lambda a: expected
    monkeypatch.setattr(type(model_as), '_get_service_method',
                        lambda a, b, c: test_input['method'])
    spy_gsm = mocker.spy(type(model_as), '_get_service_method')
    data = model_as._get_auth_token(route)
    spy_gsm.assert_called_once_with(model_as, route, '_get_auth_token')
    assert data == expected


def test_log_request(monkeypatch, mocker, model_as, route, service):
    value = {
        'service_id': route.service_id.id,
        'route_id': route.id,
    }
    monkeypatch.setattr(type(model_as), '_prepare_log_request',
                        lambda a, b, c, d, e, f: value)
    spy = mocker.spy(type(model_as), '_prepare_log_request')
    log = model_as._log_request(route, route.url, {})
    spy.assert_called_once_with(model_as, route, route.url, {}, False, False)
    assert log.service_id == route.service_id
    assert log.route_id == route


@pytest.mark.parametrize('test_input,expected', [
    ({'method': None}, {}),
    ({'method': True}, {'f': 1}),
])
def test_prepare_log_request(monkeypatch, mocker, model_as, route,
                             test_input, expected):
    if test_input['method']:
        test_input['method'] = lambda a, b, c, d, e: expected
    monkeypatch.setattr(type(model_as), '_get_service_method',
                        lambda a, b, c: test_input['method'])
    spy_gsm = mocker.spy(type(model_as), '_get_service_method')
    data = model_as._prepare_log_request(route, route.url, {}, False, False)
    spy_gsm.assert_called_once_with(model_as, route, '_prepare_log_request')
    assert data == {
        'service_id': route.service_id.id,
        'route_id': route.id,
        'request_url': route.url,
        'request_header': {},
        'request_query_string': False,
        'request_body': False,
        **expected
    }


def test_log_response(monkeypatch, mocker, model_as, route, log):
    value = {
        'requested_by': 'Granite',
    }
    monkeypatch.setattr(type(model_as), '_prepare_log_response',
                        lambda a, b, c, d: value)
    spy = mocker.spy(type(model_as), '_prepare_log_response')
    model_as._log_response(log, route, None)
    spy.assert_called_once_with(model_as, route, None, None)
    assert log.requested_by == 'Granite'


@pytest.mark.parametrize('test_input,expected', [
    ({'method': None}, {'data': {}}),
    ({'response': True, 'method': None}, {'response': True, 'data': {}}),
    ({'method': True}, {'data': {'f': 1}}),
    ({'response': True, 'method': True}, {'response': True, 'data': {'f': 1}}),
])
def test_prepare_log_response(monkeypatch, mocker, model_as, route,
                              test_input, expected):
    res = None
    expected_status_code = -1
    error = 'error'
    expected_body = error
    expected_status = 'fail'
    if test_input.get('response'):
        expected_status_code = 200
        expected_body = '{"status": "OK"}'
        expected_status = 'success'
        res = Mock(
            status_code=expected_status_code,
            headers={},
            text=expected_body,
            spec=Response
        )
    if test_input['method']:
        test_input['method'] = lambda a, b, c: expected['data']
    monkeypatch.setattr(type(model_as), '_get_service_method',
                        lambda a, b, c: test_input['method'])
    spy_gsm = mocker.spy(type(model_as), '_get_service_method')
    monkeypatch.setattr(type(model_as), '_get_log_status',
                        lambda a, b, c: expected_status)
    spy_gls = mocker.spy(type(model_as), '_get_log_status')

    data = model_as._prepare_log_response(route, res, error)
    spy_gsm.assert_called_once_with(model_as, route, '_prepare_log_response')
    if expected.get('response'):
        spy_gls.assert_called_once_with(model_as, route, res)
    assert data['response_status_code'] == expected_status_code
    assert data['response_body'] == expected_body
    assert data['status'] == expected_status
    for key in expected['data']:
        assert data[key] == expected['data'][key]


@pytest.mark.parametrize('test_input,expected', [
    ({'status_code': 199, 'method': None}, {'status': 'fail'}),
    ({'status_code': 300, 'method': None}, {'status': 'fail'}),
    ({'status_code': 200, 'method': True},
     {'status': 'fail', 'method': 'fail'}),
    ({'status_code': 200, 'method': None}, {'status': 'success'}),
    ({'status_code': 201, 'method': None}, {'status': 'success'}),
    ({'status_code': 204, 'method': None}, {'status': 'success'}),
    ({'status_code': 300, 'method': True},
     {'status': 'success', 'method': 'success'}),
])
def test_get_log_status(monkeypatch, mocker, model_as, route,
                        test_input, expected):
    if test_input['method']:
        test_input['method'] = lambda a, b: expected['method']
    monkeypatch.setattr(type(model_as), '_get_service_method',
                        lambda a, b, c: test_input['method'])
    spy_gsm = mocker.spy(type(model_as), '_get_service_method')
    res = Mock(status_code=test_input['status_code'], spec=Response)

    data = model_as._get_log_status(route, res)
    spy_gsm.assert_called_once_with(model_as, route, '_get_log_status')
    assert data == expected['status']


@pytest.mark.parametrize('test_input,expected', [
    ({}, False),
    ({'path_params': {'id': 1}}, False),
    ({'timeout': 50.0}, False),
    ({'headers': {'content-type': 'application/json'}}, False),
    ({'params': {'a': 1}}, False),
    ({'data': {'b': 1}}, False),
    ({'path_params': {'id': 1},
      'timeout': 50.0,
      'headers': {'content-type': 'application/json'},
      'params': {'a': 1},
      'data': {'b': 1}},
     False),
    ({}, True),
    ({'path_params': {'id': 1}}, True),
    ({'timeout': 50.0}, True),
    ({'headers': {'content-type': 'application/json'}}, True),
    ({'path_params': {'id': 1},
      'timeout': 50.0,
      'headers': {'content-type': 'application/json'},
      'params': {'a': 1},
      'data': {'b': 1}},
     True),
])
def test_requests(monkeypatch, mocker, model_as, route, log,
                  test_input, expected):
    response = None
    error = None
    if expected:
        response = True
        mock = MagicMock(return_value=response)
    else:
        error = 'error'
        mock = MagicMock(side_effect=Exception(error))

    monkeypatch.setattr(type(model_as), '_get_route', lambda a, b: route)
    spy_gr = mocker.spy(type(model_as), '_get_route')
    monkeypatch.setattr(type(model_as), '_get_timeout',
                        lambda a, b: test_input.get('timeout', 30.0))
    spy_gt = mocker.spy(type(model_as), '_get_timeout')
    monkeypatch.setattr(type(model_as), '_prepare_header', lambda a, b: {})
    spy_ph = mocker.spy(type(model_as), '_prepare_header')
    monkeypatch.setattr(type(model_as), '_log_request',
                        lambda a, b, c, d, e, f: log)
    spy_lreq = mocker.spy(type(model_as), '_log_request')
    monkeypatch.setitem(requests_wrapper, route.method, mock)
    monkeypatch.setattr(type(model_as), '_log_response',
                        lambda a, b, c, d, e: True)
    spy_lres = mocker.spy(type(model_as), '_log_response')
    expected_url = (
        (
            test_input.get('path_params')
            and route.url.format(**test_input.get('path_params'))
        )
        or route.url
    )

    data = model_as.requests(route.reference, **test_input)
    spy_gr.assert_called_once_with(model_as, route.reference)
    spy_gt.assert_called_once_with(model_as, test_input.get('timeout'))
    if not test_input.get('headers'):
        spy_ph.assert_called_once_with(model_as, route)
    spy_lreq.assert_called_once_with(
        model_as,
        route,
        expected_url,
        test_input.get('headers', {}),
        test_input.get('params'),
        test_input.get('data')
    )
    requests_wrapper[route.method].assert_called_once_with(
        expected_url,
        headers=test_input.get('headers', {}),
        timeout=test_input.get('timeout', 30.0),
        **(test_input.get('params', {})
           and {'params': test_input.get('params')}),
        **(test_input.get('data', {})
           and {'data': test_input.get('data')})
    )
    spy_lres.assert_called_once_with(
        model_as,
        log,
        route,
        response,
        error
    )
    assert data == response


@pytest.mark.parametrize('test_input,expected', [
    ({'dict': True, 'method': None}, {'status': 'success'}),
    ({'status_code': 199, 'method': None}, {'status': 'fail'}),
    ({'status_code': 300, 'method': None}, {'status': 'fail'}),
    ({'status_code': 200, 'method': True},
     {'status': 'fail', 'method': 'fail'}),
    ({'status_code': 200, 'method': None}, {'status': 'success'}),
    ({'status_code': 201, 'method': None}, {'status': 'success'}),
    ({'status_code': 204, 'method': None}, {'status': 'success'}),
    ({'status_code': 300, 'method': True},
     {'status': 'success', 'method': 'success'}),
])
def test_get_log_status_incoming(monkeypatch, mocker, model_as, route,
                                 test_input, expected):
    if test_input['method']:
        test_input['method'] = lambda a, b: expected['method']
    monkeypatch.setattr(type(model_as), '_get_service_method',
                        lambda a, b, c: test_input['method'])
    spy_gsm = mocker.spy(type(model_as), '_get_service_method')
    res = {}
    if not test_input.get('dict'):
        res = Mock(status_code=test_input['status_code'], spec=http.Response)

    data = model_as._get_log_status_incoming(route, res)
    spy_gsm.assert_called_once_with(model_as, route,
                                    '_get_log_status_incoming')
    assert data == expected['status']
