from odoo import models, api, _
from odoo.exceptions import ValidationError


class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'

    @api.constrains('date_from', 'date_to')
    def _check_date_from_and_to(self):
        for rec in self:
            sequence = rec.sequence_id
            date_from, date_to = sequence._get_date_from_range(
                sequence.range, rec.date_from
            )
            rec.check_date_range_duplicate(
                date_from, date_to
            )
            if rec.date_from != date_from or rec.date_to != date_to:
                raise ValidationError(
                    _('Please set date from equal %s and date to %s') %
                    (str(date_from), str(date_to))
                )

    def check_date_range_duplicate(self, date_from, date_to):
        date_range_duplicate = self.search([
            ('date_from', '=', date_from),
            ('date_to', '=', date_to),
            ('id', '!=', self.id),
            ('sequence_id', '=', self.sequence_id.id),
        ])
        if date_range_duplicate:
            raise ValidationError(
                _('Please Check Date Range Duplicate')
            )
