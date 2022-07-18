import requests

from odoo.addons.rts_api_base.controllers.main import APIBase


class KBTApiBase(APIBase):

    def _response_api(self, isSuccess=False, message='', **kwargs):
        response_api = {
            'isSuccess': True if isSuccess else False,
            'code': requests.codes.all_ok if isSuccess else
            requests.codes.bad_request,
        }
        if message:
            response_api.update({
                'message': message
            })
        response_api.update(kwargs)
        return response_api
