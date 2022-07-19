import pytest
from pytest_tr_odoo.fixtures import env
from datetime import datetime, timedelta
from .fixtures import *


def test_get_log_detail(log):
    details = log._get_log_detail()
    assert details == [{
        'route_reference': log.route_reference,
        'status': log.status,
        'request_url': log.request_url,
        'request_header': log.request_header,
        'request_query_string': log.request_query_string,
        'request_body': log.request_body,
        'response_status_code': log.response_status_code,
        'response_body': log.response_body
    }]


@pytest.mark.parametrize('test_input,expected', [
    (0, 0),
    (1, 1),
    (10, 1),
])
def test_cron_clear_interface_history(env, log, test_input, expected):
    env.cr.execute('UPDATE api_logs SET create_date = %s', (
        (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
    ))
    env['ir.config_parameter'].sudo().set_param(
        'api.log.duration',
        test_input
    )
    assert log._cron_clear_interface_history()
    assert len(log.search([])) == expected
