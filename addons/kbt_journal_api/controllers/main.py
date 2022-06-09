import requests

from odoo import http
from odoo.http import request


class SaleOrderDataController(http.Controller):

    @http.route('/journal/create', type='json', auth='user')
    def journal_create_api(self, **params):
        try:
            self._create_journal_entry(**params)
        except requests.HTTPError as http_err:
            return {
                'HTTP error': http_err,
            }
        except Exception as error:
            return {
                'error': error,
            }

    def _create_journal_entry(self, **params):
        AccountMove = request.env['account.move']
        return AccountMove
