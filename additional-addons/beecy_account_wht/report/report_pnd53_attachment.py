import math
from dateutil.relativedelta import relativedelta

from odoo import models, api, _
from odoo.exceptions import ValidationError


class ReportPND53Attachment(models.TransientModel):
    _name = 'report.beecy_account_wht.report_pnd53_attach_pdf'
    _description = 'Report PND53 Attachment Report'

    def _get_report_data(self, data_list, page):
        return list(filter(lambda l: l['page'] == page, data_list))

    def _prepare_wht_data_val(self, wht_lines, line_no, wht_type_id, wht_id):
        wht_payment = 1 if wht_id.wht_payment == 'wht' else 2
        doc_date = (wht_id.document_date + relativedelta(years=543)).strftime(
            '%d/%m/%Y')
        why_type = wht_type_id.printed or '-'
        return {
            'line_no': line_no,
            'document_date': doc_date,
            'wht_type': why_type,
            'percent': wht_type_id.percent,
            'base_amount': round(sum(wht_lines.mapped('base_amount')), 2),
            'wht_amount': round(sum(wht_lines.mapped('wht_amount')), 2),
            'wht_payment': wht_payment,
        }

    def _prepare_report_data_val(self, sequence, partner, wht_id, wht_list):
        company_id = partner.parent_id if partner.parent_id else partner
        branch_code = partner.parent_id.x_branch_name if partner.parent_id \
            else partner.x_branch_name
        return {
            'page': math.ceil(sequence / 6),
            'sequence': sequence,
            'id_card_list': wht_id.split_id_card(pnd_type='53'),
            'branch_code': branch_code,
            # 'prefix': company_id.prefix,
            # 'suffix': company_id.suffix,
            'company_name': company_id.name,
            'address': self._get_partner_address(partner),
            'line_list': wht_list
        }

    def _get_partner_address(self, partner_id):
        address = str()
        if partner_id.street:
            address += partner_id.street + ' '
        if partner_id.street2:
            address += partner_id.street2 + ' '
        if partner_id.city:
            address += partner_id.city + ' '
        if partner_id.state_id:
            address += partner_id.state_id.name
        return address

    @api.model
    def _get_report_values(self, docids, data=None):
        Report = self.env['report.beecy_account_wht.report_pnd3_attach_pdf']
        pnd_ids = self.env['account.wht.pnd'].sudo().browse(docids)
        if pnd_ids.wht_ids.filtered(lambda w: not w.document_date):
            raise ValidationError(
                _("Some documents do not contain 'Document Date'"))
        wht_ids = pnd_ids.wht_ids.sorted(
            key=lambda w: (
                w.document_date,
                w.line_ids.wht_type_id.mapped('sequence')))
        partner_ids = wht_ids.partner_id
        data_list = list()
        i = 0
        for partner in partner_ids:
            wht_list = list()
            line_ids = wht_ids.filtered(
                lambda w: w.partner_id == partner).line_ids
            wht_type_ids = line_ids.mapped('wht_type_id')
            data_count = 0
            count_line = 1
            for wht_type_id in wht_type_ids:
                wht_lines = line_ids.filtered(
                    lambda x: x.wht_type_id == wht_type_id)
                wht_id = wht_lines.mapped('wht_id')
                wht_list.append(
                    self._prepare_wht_data_val(
                        wht_lines,
                        count_line,
                        wht_type_id,
                        wht_id))
                data_count += 1
                count_line += 1
                if len(wht_list) == 3 or len(wht_type_ids) == data_count:
                    i += 1
                    data_list.append(
                        self._prepare_report_data_val(
                            i, partner, wht_id, wht_list))
                    count_line = 1
                    wht_list = list()

        return {
            'report_model': Report,
            'doc_ids': docids,
            'doc_model': pnd_ids._name,
            'data_list': data_list,
            'docs': pnd_ids,
            'total_page': math.ceil(
                len(data_list) / 6)}
