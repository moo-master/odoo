# Copyright 2016 LasLabs Inc.
# Copyright 2017 Kaushal Prajapati <kbprajapati@live.com>.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    password_expiration = fields.Integer(
        "Days",
        default=90,
        help="How many days until passwords expire",
    )
    password_length = fields.Integer(
        "Characters",
        default=8,
        help="Minimum number of characters",
    )
    password_lower = fields.Integer(
        "Lowercase",
        default=1,
        help="Require number of lowercase letters",
    )
    password_upper = fields.Integer(
        "Uppercase",
        default=1,
        help="Require number of uppercase letters",
    )
    password_numeric = fields.Integer(
        "Numeric",
        default=1,
        help="Require number of numeric digits",
    )
    password_special = fields.Integer(
        "Special",
        default=0,
        help="Require number of unique special characters",
    )
    password_estimate = fields.Integer(
        "Estimation",
        default=0,
        help="Required score for the strength estimation. Between 0 and 4",
    )
    password_history = fields.Integer(
        "History",
        default=0,
        help="Disallow reuse of this many previous passwords - use negative "
        "number for infinite, or 0 to disable",
    )
    password_minimum = fields.Integer(
        "Minimum Hours",
        default=1,
        help="Amount of hours until a user may change password again",
    )

    @api.constrains("password_estimate")
    def _check_password_estimate(self):
        if 0 > self.password_estimate > 4:
            raise ValidationError(_("The estimation must be between 0 and 4."))
