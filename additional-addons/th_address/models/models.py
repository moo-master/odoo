import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class GEONamesTH(models.Model):
    _name = "geonames_th.geonames_th"
    _description = 'GEO Names TH'

    @api.model
    def import_data(self):
        th = self.env.ref("base.th")
        geoname_import = self.env["city.zip.geonames.import"]
        parse_csv = geoname_import.get_and_parse_csv(th)
        geoname_import._process_csv(parse_csv, th)
