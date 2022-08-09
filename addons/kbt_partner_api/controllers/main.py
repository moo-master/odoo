import requests

from odoo import http
from odoo.http import request
from odoo.addons.kbt_api_base.controllers.main import KBTApiBase


class PartnerDataController(KBTApiBase):

    @KBTApiBase.api_wrapper(['kbt.partner'])
    @http.route('/partner/data', type='json', auth='user')
    def res_partner_api(self, **params):
        try:
            msg = self._check_partner_values(**params)
            if msg:
                return self._response_api(message=msg)
            self._create_update_partner(**params)
            return self._response_api(isSuccess=True)
        except requests.HTTPError as http_err:
            return self._response_api(message=str(http_err))
        except Exception as error:
            return self._response_api(message=str(error))

    def _check_partner_values(self, **params):
        msg_list = []
        if not params.get('data'):
            msg_list.append('Data: No Data')
        return msg_list

    def _create_update_partner(self, **params):
        Partner = request.env['res.partner']
        ResBank = request.env['res.bank']
        data_params = params
        User = request.env.user

        for data in data_params.get('data'):
            account_receivable_id = request.env['account.account'].search([
                ('code', '=', data.get('property_account_receivable_id')),
                ('reconcile', '=', True),
                ('company_id', '=', User.company_id.id),
            ])
            if not account_receivable_id:
                raise ValueError("account_receivable_id not found.")

            account_payable_id = request.env['account.account'].search([
                ('code', '=', data.get('property_account_payable_id')),
                ('reconcile', '=', True),
                ('company_id', '=', User.company_id.id),
            ])
            if not account_payable_id:
                raise ValueError("account_payable_id not found.")

            partner_id = Partner.search(
                [('x_interface_id', '=', data.get('x_external_code'))])

            if data.get('company_type') not in ['person', 'company']:
                raise ValueError("company_type must be 'person' or 'company'")

            vals_dict = {
                'x_interface_id': data.get('x_external_code'),
                'name': data.get('name'),
                'company_type': data.get('company_type'),
                'type': data.get('type'),
                'street': data.get('street'),
                'street2': data.get('street2'),
                'zip': data.get('zip'),
                'city': data.get('city'),
                'state_id': data.get('state_id'),
                'country_id': data.get('country_id'),
                'vat': data.get('vat'),
                'phone': data.get('phone'),
                'mobile': data.get('mobile'),
                'email': data.get('email'),
                'website': data.get('website'),
                'category_id': data.get('category_id'),
                'property_account_receivable_id': account_receivable_id.id,
                'property_account_payable_id': account_payable_id.id,
                'x_is_interface': True,
            }
            bank_id = ResBank.search([
                ('bic', '=', data.get('bank_id'))
            ], limit=1)
            if not bank_id:
                raise ValueError("bank_id not found.")

            if not partner_id:
                # Check acc_number is duplicate
                is_new_acc = self._get_res_partner_bank_data(
                    data.get('bank_acc_number'))
                if is_new_acc:
                    return self._raise_error_duplicate()

                vals_dict.update({
                    'bank_ids': [(0, 0, {
                        'acc_number': data.get('bank_acc_number'),
                        'bank_id': bank_id.id
                    })]
                })
                Partner.create(vals_dict)
                return

            # Check res.partner.bank from API is found
            partner_bank_id = self._get_res_partner_bank_data(
                data.get('bank_acc_number'), partner_id, bank_id)

            if not partner_bank_id:
                partner_bank_id = self._get_res_partner_bank_data(
                    data.get('bank_acc_number'), partner_id)
                if partner_bank_id:
                    # Same acc_number But New Bank
                    vals_dict.update({
                        'bank_ids': [(1, partner_bank_id.id, {
                            'bank_id': bank_id.id,
                        })]
                    })
                    partner_id.write(vals_dict)
                    return

                partner_bank_id = self._get_res_partner_bank_data(
                    partner_id=partner_id, bank_id=bank_id)
                if partner_bank_id:
                    # Same Bank But New acc_number
                    is_new_acc = self._get_res_partner_bank_data(
                        data.get('bank_acc_number'))
                    if is_new_acc:
                        return self._raise_error_duplicate()
                    vals_dict.update({
                        'bank_ids': [(1, partner_bank_id.id, {
                            'acc_number': data.get('bank_acc_number'),
                        })]
                    })
                else:
                    # Create New res.partner.bank
                    vals_dict.update({
                        'bank_ids': [(0, 0, {
                            'acc_number': data.get('bank_acc_number'),
                            'bank_id': bank_id.id,
                        })]
                    })

            partner_id.write(vals_dict)

    def _get_res_partner_bank_data(
            self,
            acc_number='',
            partner_id=False,
            bank_id=False):
        domain = []
        if acc_number:
            domain.append(('acc_number', '=', acc_number))
        if partner_id:
            domain.append(('partner_id', '=', partner_id.id))
        if bank_id:
            domain.append(('bank_id', '=', bank_id.id))
        partner_bank_id = request.env['res.partner.bank'].search(
            domain, limit=1)
        return partner_bank_id

    def _raise_error_duplicate(self):
        raise ValueError(
            "Bank Account number is duplicate with other contact."
        )
