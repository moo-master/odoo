from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _convert_entities_char(self, text):
        """Hook Convert HTML Entities to characters
        Example : text.replace(b"&quot;", b'"')
        """
        return text

    @api.model
    def _render_qweb_text(self, docids, data=None):
        """Delete space"""
        res = super()._render_qweb_text(docids, data=data)
        lst = list(res)
        lst[0] = lst[0].strip()
        lst[0] = self._convert_entities_char(lst[0])
        res = tuple(lst)
        return res
