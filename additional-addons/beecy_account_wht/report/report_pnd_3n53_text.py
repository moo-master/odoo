from dateutil.relativedelta import relativedelta

from odoo import models, api, _
from odoo.exceptions import ValidationError


class ReportPND3n53Text(models.TransientModel):
    _name = 'report.beecy_account_wht.report_pnd_3n53_text'
    _description = 'Report PND3 Attachment Report'

    def _prepare_text_data(self, text, i, wht_id, line_id):
        partner_id = wht_id.partner_id
        code = partner_id.branch_code if partner_id.branch != 'hq' else '00000' if partner_id.company_type == 'company' else ''
        document_date = (
            wht_id.document_date + relativedelta(years=543)
        ).strftime('%d/%m/%Y')
        pnd_type = wht_id.wht_kind
        if pnd_type == 'pnd3':
            wht_payment = 1 if wht_id.wht_payment == 'wht' else 2
        else:
            wht_payment = 1 if wht_id.wht_payment == 'wht' else 2

        if partner_id.company_type == 'person':
            name = (partner_id.prefix or '') + '|' + \
                (partner_id.firstname or '') + '||' + (partner_id.lastname or '')
        else:
            name = (partner_id.prefix or '') + '|' + (partner_id.name or '') + ((' ' + partner_id.suffix)
                                                                                if partner_id.suffix and partner_id.name else partner_id.suffix or '')

        text += "{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}\n".\
            format(
                i,
                partner_id.vat or '',
                code,
                name,
                partner_id.building or '',
                partner_id.room_number or '',
                partner_id.floor or '',
                partner_id.village or '',
                partner_id.house_number or '',
                partner_id.village_number or '',
                partner_id.alley or '',
                partner_id.sub_alley or '',
                partner_id.street or '',
                partner_id.street2 or '',
                partner_id.city or '',
                partner_id.state_id.name or '',
                partner_id.zip or '',
                document_date or '',
                line_id.wht_type_id.printed or line_id.note or '',
                '%.2f' % line_id.percent,
                '%.2f' % round(line_id.base_amount, 2),
                '%.2f' % round(line_id.wht_amount, 2),
                wht_payment
            )
        return text

    @api.model
    def _get_report_values(self, docids, data=None):
        pnd_ids = self.env['account.wht.pnd'].sudo().browse(docids)
        if pnd_ids.wht_ids.filtered(lambda w: not w.document_date):
            raise ValidationError(
                _("Some documents do not contain 'Document Date'"))
        wht_ids = pnd_ids.wht_ids.sorted(
            key=lambda w: (
                w.document_date,
                w.line_ids.wht_type_id.mapped('sequence')))
        partner_ids = wht_ids.partner_id
        i = 1
        text = ""
        for partner in partner_ids:
            line_count = 0
            data_count = 0
            line_ids = wht_ids.filtered(
                lambda w: w.partner_id == partner).line_ids
            for rec in line_ids:
                line_count += 1
                data_count += 1
                text = self._prepare_text_data(text, i, rec.wht_id, rec)
                if line_count == 3 or len(line_ids) == data_count:
                    i += 1
                    line_count = 0
        return {
            'doc_ids': docids,
            'doc_model': pnd_ids._name,
            'docs': pnd_ids,
            'text': text,
        }
