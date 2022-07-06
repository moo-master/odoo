from odoo import models


class ApiService(models.Model):
    _inherit = 'api.service'

    def _get_log_status_incoming_kbt(self, route, response):
        status = 'fail'

        if 200 <= response['code'] < 300:
            status = 'success'
        return status
