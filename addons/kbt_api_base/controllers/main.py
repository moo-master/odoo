import requests

from odoo.http import request
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

    def _check_wht_sequence(self, order_lines, default_wht):
        section_5_list = []
        section_6_list = []
        for line in order_lines:
            product = request.env['product.product'].search(
                [('default_code', '=', line.get('product_id'))])
            if not product:
                raise ValueError(
                    "product_id not found."
                )

            seq = int(line.get('x_wht_id')) if line.get('x_wht_id') \
                else getattr(product, default_wht).sequence
            if (self.section_check(seq) == 5 and seq not in section_5_list):
                section_5_list.append(seq)
            if (self.section_check(seq) == 6 and seq not in section_6_list):
                section_6_list.append(seq)

        if len(section_5_list) > 1 or len(section_6_list) > 1:
            raise ValueError(
                "You can not select different WHT under the same category."
                " Right now your section 5 or section 6"
                " are under the same category.")

    def section_check(self, sequence):
        if(int(sequence / 500) == 1 and (sequence % 500) < 100):
            return 5
        if(int(sequence / 600) == 1 and (sequence % 600) < 100):
            return 6
