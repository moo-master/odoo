from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _check_credentials(self, password, env):
        self.env.cr.execute(
            '''select COALESCE(key, '')
            from res_users_apikeys
            where user_id =%s''', [self.env.user.id])
        hashed_lst = self.env.cr.fetchall()

        for hashed in hashed_lst:
            [hashed] = hashed
            valid, _ = self._crypt_context().verify_and_update(password, hashed)
            if valid:
                return

        return super()._check_credentials(password, env)
