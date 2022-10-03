from pytest_tr_odoo.fixtures import env


def test__render_qweb_text(env):
    pnd = env['account.wht.pnd'].create({'pnd_type': 'pnd3'})
    report_x = env.ref('beecy_account_wht.action_pnd_3n53_report_txt')
    report_x._render_qweb_text(pnd.ids)
