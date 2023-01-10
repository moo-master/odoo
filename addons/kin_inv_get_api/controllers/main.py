import requests

from odoo import http
from odoo.http import request
from datetime import datetime

class InvoicesDataController(http.Controller):
    @http.route('/get_invoices', type='json', auth='user')
    def get_invoices(self):
        print("Yes here entered")
        account_move = request.env['account.move'].search([])
        invoices = []
        for rec in account_move:
            
            vals = {
                'invoice_date' : rec.invoice_date,
                'amount_total' : rec.amount_total,
                'amount_paid'   : rec.amount_paid,

    
            }
            invoices.append(vals)
        print("Invoice List-->", invoices)    
        data = {'status':200, 'response': invoices, 'massage': 'Success'}    
        return data
