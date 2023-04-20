# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from builtins import Exception
from email.policy import default
from urllib import response
from odoo import api, fields, models, _
import datetime
from ast import literal_eval

import logging
_logger = logging.getLogger(__name__)



class TwoctwopTransaction(models.Model):
    _name = 'twoctwop.transaction'
    _description = '2C2P Transcations'
    _inherit = "mail.thread"


    name = fields.Datetime(string="Response Date", default=datetime.datetime.now(), copy=False);
    state = fields.Selection([
        ("draft", "Draft"),
        ("error", "Error"),
        ("cancel", "Cancel"),
        ("done", "Done"),], string="State", default="draft", tracking=True);
    invoice_no = fields.Char(string="Invoice No.", compute="_compute_invoice_no");
    response = fields.Text(string="Response Encrypted");
    resp_d = fields.Text(string="Response Decrypted");
    subscription_id = fields.Many2one("sale.subscription", string="Linked Subscription", copy=False);
    extra_comment = fields.Html(string="Extra Comment");

    @api.depends("resp_d")
    def _compute_invoice_no(self):
        for rec in self:
            resp = literal_eval(rec.resp_d or "{}");
            rec.invoice_no = resp.get("invoiceNo", "");


    def add_comment(self, comment):
        cmt = self.extra_comment or "";
        self.extra_comment = cmt + comment;



    def post_transcation(self, cron_call=False):
        pay_method = self.env["account.payment.method.line"].search([('name','=','2c2p')], limit=1)
        mes_subtype = self.env["mail.message.subtype"].search([('name','=','Discussions')]);
        for rec in self:
            try:
            
                _logger.info("@@@@@@@@@@@@@@@@@@@@%r",rec.resp_d)

                resp = literal_eval(rec.resp_d or "{}");

                _logger.info("@@@@@@@@@@@@@@@@@@@@%r",resp)

                if not resp.get('recurringUniqueID', False):
                    rec.state = "error";
                    text = self.env["ir.ui.view"]._render_template(
                        'wk_payment_2c2p.message_origin_link',
                        values={
                            'message': 'error1',
                            'origin': resp.get("invoiceNo"), 
                        });
                    rec.message_post(body=text, subtype_id=mes_subtype.id);
                    rec.add_comment(text);
                    continue;
                payment = self.env["account.payment"].search([
                    ("ref","=",resp.get("invoiceNo")),
                    ("payment_method_line_id", "=", pay_method.id),
                ]);
                if len(payment or ""):
                    rec.state = "cancel";
                    text = self.env["ir.ui.view"]._render_template(
                        'wk_payment_2c2p.message_origin_link',
                        values={
                            'message': 'cancel', 
                            'payment': payment,
                            'origin': resp.get("invoiceNo"),
                        });
                    _logger.info("@@@@@@@@@@texttext@@@@@@@@@@%r",text)
                    rec.message_post(body=text);
                    rec.add_comment(text);
                    if not cron_call:
                        return self.env['wk.wizard.message'].genrated_message(text)
                    continue;
                else:
                    sub = self.env["sale.subscription"].search([
                        ("twoctwop_recurring_unique_id","=", resp.get('recurringUniqueID'))], limit=1);
                    if len(sub or ""):
                        rec.subscription_id = sub.id;
                        pa = self.env['payment.acquirer'].sudo().search([('provider','=','2c2p')], limit=1);
                        vals = {
                            "journal_id" : pa.journal_id.id,
                            "ref" : resp.get("invoiceNo"),
                            "payment_type" : "inbound",
                            "payment_method_line_id" : pay_method.id,
                            "partner_id" : sub.partner_id.id,
                            "amount" : resp.get("fxAmount"),
                        }
                        payment = self.env["account.payment"].create(vals);
                        payment.action_post();
                        so = self.env['sale.order'].search([('twoctwop_recurring_unique_id', '=', sub.twoctwop_recurring_unique_id)], limit=1);
                        rec.state = "done";
                        text = self.env["ir.ui.view"]._render_template(
                            'wk_payment_2c2p.message_origin_link',
                            values={
                                'message': 'done', 
                                'self': rec, 
                                'origin': resp.get("invoiceNo"),
                                'payment': payment,
                                'so': so,
                                'sub': sub,
                                'cust': sub.partner_id,
                                'amount': payment.amount,});
                        _logger.info("@@@@@@@@@@texttext@@@@@@@@@@%r",text)
                        rec.message_post_with_view(
                            'wk_payment_2c2p.message_origin_link',
                            values={
                                'message': 'done',
                                'self': rec, 
                                'origin': resp.get("invoiceNo"),
                                'payment': payment,
                                'so': so,
                                'sub': sub,
                                'cust': sub.partner_id,
                                'amount': payment.amount,},
                            subtype_id=mes_subtype.id);
                        rec.add_comment(text);
                        if not cron_call:
                            return self.env['wk.wizard.message'].genrated_message(text);
                    else:
                        rec.state = "error";
                        text = self.env["ir.ui.view"]._render_template(
                            'wk_payment_2c2p.message_origin_link',
                            values={
                                'message': 'error',
                                'recurringID': resp.get("recurringUniqueID"), 
                            });
                        rec.message_post(body=text, subtype_id=mes_subtype.id);
                        rec.add_comment(text);
                        if not cron_call:
                            return self.env['wk.wizard.message'].genrated_message(text);

            except Exception:
                _logger.info("@@@@@@@@@@Exception@@@@@@@@@@%r",Exception)
                text = self.env["ir.ui.view"]._render_template(
                    'wk_payment_2c2p.message_origin_link',
                    values={
                        'message': 'error2',
                        'origin': rec.invoice_no,
                    });
                rec.message_post(body=text, subtype_id=mes_subtype.id);
                rec.add_comment(text);
                if not cron_call:
                    return self.env['wk.wizard.message'].genrated_message(text);


    def cron_post_2c2p_transcations(self):
        txs = self.search([('state', '=', 'draft')]);
        _logger.info("@@@@@@@@@@txs@@@@@@@@@@%r",txs)
        txs.post_transcation(cron_call=True);
