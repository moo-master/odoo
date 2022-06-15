from odoo import models
# import re


class ApiService(models.Model):
    _inherit = 'api.service'

    # def _get_log_status_incoming_kbt(self, route, response):
    #     status = 'fail'
    #     code = 1
    #     headers = re.match(r'application/json',
    #                        response.headers.get('Content-Type'))
    #     if headers:
    #         code = response.json().get('code')
    #     cancel_order = (route.key == 'cancel.order'
    #                     and code == 1032)
    #     if (200 <= response.status_code < 300 and code == 1 or cancel_order):
    #         status = 'success'
    #     print("\n RESSSS", response)
    #     return status
