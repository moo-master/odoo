from datetime import timedelta
from odoo import models, fields, api


class IrSequence(models.Model):
    '''
    Sequence
    '''
    _inherit = 'ir.sequence'

    range = fields.Selection(
        [
            ('week', 'Week'),
            ('month', 'Month'),
            ('year', 'Year'),
        ],
        string='Range',
    )

    @api.onchange('use_date_range')
    def _onchange_use_date_range(self):
        _range = False
        if self.use_date_range:
            _range = 'year'
        self.range = _range

    # overwrite std odoo
    def _create_date_range_seq(self, date):
        current_date = fields.Date.from_string(date)
        date_from, date_to = self._get_date_from_range(
            self.range, current_date
        )
        seq_date_range = self.env['ir.sequence.date_range'].sudo().create({
            'date_from': date_from,
            'date_to': date_to,
            'sequence_id': self.id,
        })
        return seq_date_range

    def _get_date_to_and_date_from_week(
            self, current_date
    ):
        day_weekday = current_date.weekday()
        date_from = current_date - timedelta(days=day_weekday)
        date_to = date_from + timedelta(days=6)
        return date_from, date_to

    def _get_date_to_and_date_from_month(
            self, current_date
    ):
        date_from = current_date.replace(day=1)
        month = 1
        if current_date.month == 12:
            date_to = date_from.replace(
                year=current_date.year + 1,
                month=month,
            )
        else:
            date_to = date_from.replace(
                month=current_date.month + month,
            )
        date_to -= timedelta(days=1)
        return date_from, date_to

    def _get_date_to_and_date_from_year(
            self, current_date
    ):
        date_from = current_date.replace(
            month=1, day=1
        )
        date_to = date_from.replace(
            year=current_date.year + 1
        )
        date_to -= timedelta(days=1)
        return date_from, date_to

    def _get_date_from_range(self, t_range, current_date):
        if t_range == 'year':
            date_from, date_to = self._get_date_to_and_date_from_year(
                current_date
            )
        elif t_range == 'month':
            date_from, date_to = self._get_date_to_and_date_from_month(
                current_date
            )
        else:
            date_from, date_to = self._get_date_to_and_date_from_week(
                current_date
            )
        return date_from, date_to
