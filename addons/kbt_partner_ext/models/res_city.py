
from odoo import models, fields


class ResCity(models.Model):
    _inherit = "res.city"

    code = fields.Char(
        string="Code"
    )

    _sql_constraints = [
        (
            "code_uniq",
            "UNIQUE(code)",
            "You already have this City Code.",
        )
    ]
