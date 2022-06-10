from odoo import models

MONTH_THAI = 'x มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม' \
             ' กันยายน ตุลาคม พฤศจิกายน ธันวาคม'


class BaseDocumentLayout(models.TransientModel):
    """
    Customise the company document layout and display a live preview
    """

    _inherit = 'base.document.layout'

    def action_update_company_detail(self):
        company = self.env.company
        company.company_details = (
            f'<b>{company.name}<br/></b>'
            f'{company.street}<br/>'
            f'{company.street2}<br/>'
            f'เขต {company.state_id.name} {company.zip_id.name}<br/>'
            f'<span class="fa fa-phone" contenteditable="false"></span>'
            f'{company.phone}'
            f'  Tax ID:'
            f'{company.vat}')
        action_ref = 'web.action_base_document_layout_configurator'
        res = self.env["ir.actions.actions"]._for_xml_id(action_ref)
        return res
