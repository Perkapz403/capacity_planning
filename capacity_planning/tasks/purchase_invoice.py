import logging
import random, string

from datetime import datetime
from tasks.utils.constants import TODAY
from tasks.utils.functions import *
from tasks.reports import *
from locust import SequentialTaskSet, task, constant_pacing

def get_rest_api_qparam(q_param = None, filters=None, name=None):
    if not q_param:
        q_param = {
            "ignore_user_permissions": "0",
            "reference_doctype": "Purchase Invoice"
        }
    if name:
        if not filters:
            filters = {}
        filters['name'] = name
        q_param['fields'] = ["*"]
    return get_qparam_urlencoded(q_param, filters)

def get_pi_supplier_qparam(name=None):
    return get_rest_api_qparam(q_param=None, filters=None, name=name)

def get_pi_item_qparam(name=None):
    filters = {
        "disabled": 0,
        "is_purchase_item": 1,
        "has_variants": 0
    }
    return get_rest_api_qparam(q_param=None, filters=filters, name=name)

def get_pi_credit_to_qparam(company, name=None):
    filters = {
        "account_type": "Payable",
        "is_group": 0,
        "company": company
    }
    return get_rest_api_qparam(q_param=None, filters=filters, name=name)

def get_pi_expense_account_qparam(company, name=None):
    # txt=&doctype=Account&ignore_user_permissions=0&reference_doctype=Purchase+Invoice+Item&query=stanch.api.get_expense_account&filters=[{"include":["Fixed+Assets"],"exclude":[]}]
    filters = {
        "company": company,
        "is_group": 0
    }
    return get_rest_api_qparam(q_param=None, filters=filters, name=name)

def get_filtered_dimensions_qparam(doctype: str, company:str, account:str = None):
    q_param = {
        "txt": "",
        "doctype": doctype.title(),
        "ignore_user_permissions": 0,
        "reference_doctype": "Purchase Invoice",
        "query": "erpnext.controllers.queries.get_filtered_dimensions"
    }

    filters={
        "dimension": doctype.lower(),
        "company": company
    }

    if account:
        filters["account"] = account
    
    return get_qparam_urlencoded(q_param, filters)

class PurchaseInvoice:
    """
    Item: Mandatory parameters
    ["income_account", "item_name", "description",  "uom", "conversion_factor", "rate", "amount", base_rate", "base_amount", "cost_center"]

    Link:
    ["income_account", "uom", "cost_center"]
    """
    branch: hash
    company: str
    cost_center: hash
    supplier: hash
    credit_to: hash
    expense_account: hash
    item: hash
    purchase_invoice: hash
    name: str
    buying_price_list: str = "Standard Buying"
    conversion_rate: float = 1.0
    currency: str = "INR"

    def gen_purchase_invoice_req_body(self):
        price = random.randint(1, 1000)
        return {
            # default
            "docstatus": 0,
            "idx": 0,
            "workflow_state": "In-Progress",
            # sales invoice
            "company": self.company,
            "posting_date": TODAY,
            "currency": self.currency,
            "conversion_rate": self.conversion_rate,
            "buying_price_list": self.buying_price_list,
            "price_list_currency": self.currency,
            "plc_conversion_rate": self.conversion_rate,
            "credit_to": self.credit_to['name'],
            "cost_center": self.cost_center['value'],
            "branch": self.branch['value'],
            "base_net_total": price,
            "base_grand_total": price,
            "grand_total": price,
            # customer
            "supplier": self.supplier['name'],
            "supplier_name": self.supplier['supplier_name'],
            # items
            "items": [
                {
                    "expense_account": self.expense_account['name'],
                    "item_name": self.item['name'],
                    "description": self.item['description'],
                    "uom": "Nos",
                    "qty": 1.0,
                    "conversion_factor": self.conversion_rate,
                    "rate": price,
                    "amount": price,
                    "base_rate": price,
                    "base_amount": price,
                }
            ]
        }

class PurchaseAccountant(SequentialTaskSet):
    def on_start(self):
        logging.info(f'{datetime.now()} [TaskSet] [PurchaseAccountant] [on_start]')
        self.invoice = PurchaseInvoice()
        self.company = self.invoice.company = self.user.company

    @task(1)
    def create_purchase_invoice(self):
        logging.info(f'{datetime.now()} [TaskSet] [PurchaseAccountant] [create_purchase_invoice]')

        supplier_name = None

        # Get customer
        qparam = get_pi_supplier_qparam()
        with self.user.rest("GET", f"/api/resource/Supplier?{qparam}") as resp:
            res_data  = random.choice(resp.js['data'])
            supplier_name = res_data['name']
            assert supplier_name is not None

        qparam = get_pi_supplier_qparam(supplier_name)
        with self.user.rest("GET", f"/api/resource/Supplier?{qparam}") as resp:
            supplier = resp.js['data'][0]
            assert supplier is not None
            self.invoice.supplier = supplier
        # Get Account
        qparam = get_pi_credit_to_qparam(self.company)
        with self.user.rest("GET", f"/api/resource/Account?{qparam}") as resp:
            res_data  = random.choice(resp.js['data'])
            acc_name = res_data['name']
            assert acc_name is not None
        
        qparam = get_pi_credit_to_qparam(self.company, acc_name)
        with self.user.rest("GET", f"/api/resource/Account?{qparam}") as resp:
            account = resp.js['data'][0]
            assert account is not None
            self.invoice.credit_to = account

        # Get Item
        qparam = get_pi_item_qparam()
        with self.user.rest("GET", f"/api/resource/Item?{qparam}") as resp:
            res_data  = random.choice(resp.js['data'])
            item_name = res_data['name']
            assert item_name is not None

        qparam = get_pi_item_qparam(item_name)
        with self.user.rest("GET", f"/api/resource/Item?{qparam}") as resp:
            item = resp.js['data'][0]
            assert item is not None
            self.invoice.item = item

        # Get Expense account
        qparam = get_pi_expense_account_qparam(company=self.company)
        with self.user.rest("GET", f"/api/resource/Account?{qparam}") as resp:
            res_data  = random.choice(resp.js['data'])
            expense_acc_name = res_data['name']
            assert expense_acc_name is not None

        qparam = get_pi_expense_account_qparam(company=self.company, name=expense_acc_name)
        with self.user.rest("GET", f"/api/resource/Account?{qparam}") as resp:
            expense_account = resp.js['data'][0]
            assert expense_account is not None
            self.invoice.expense_account = expense_account

        # Cost center
        qparam = get_filtered_dimensions_qparam(
            doctype='Cost Center',
            company=self.company,
            account=self.invoice.credit_to['name']
        )
        with self.user.rest("POST", f"/api/method/frappe.desk.search.search_link?{qparam}") as resp:
            res_data = random.choice(resp.js['results'])
            assert res_data is not None
            self.invoice.cost_center = res_data

        # Branch
        qparam = get_filtered_dimensions_qparam(
            doctype='Branch',
            company=self.company,
            account=self.invoice.credit_to['name']
        )
        with self.user.rest("POST", f"/api/method/frappe.desk.search.search_link?{qparam}") as resp:
            res_data = random.choice(resp.js['results'])
            assert res_data is not None
            self.invoice.branch = res_data

        # Create Purchase invoice
        with self.user.rest("POST", '/api/resource/Purchase Invoice', json={'data': self.invoice.gen_purchase_invoice_req_body()}) as resp:
            purchase_invoice = resp.js['data']
            assert purchase_invoice is not None
            self.invoice.purchase_invoice = purchase_invoice
            self.invoice.name = purchase_invoice['name']
        # Purchase Invoice - Accounted
        accounted = {"data": { "workflow_state": "Accounted", "docstatus":1 }}
        with self.user.rest("PUT", f'/api/resource/Purchase Invoice/{self.invoice.name}', json=accounted) as resp:
            assert resp.js['data'] is not None

    @task(1)
    def create_payment_entry(self):
        # Get party details
        # txt=&doctype=Account&ignore_user_permissions=0&reference_doctype=Payment+Entry&filters=%7B%22is_group%22%3A0%2C%22company%22%3A%22MN%22%2C%22account_type%22%3A%5B%22in%22%2C%5B%22Payable%22%5D%5D%7D
        logging.info(f'{datetime.now()} [TaskSet] [PurchaseAccountant] [create_payment_entry]')
        payload = {
            'dt': 'Purchase Invoice',
            'dn': self.invoice.name
        }
        payment_entry = None
        logging.info("========> Creating Payment Entry")
        with self.user.rest("POST", "/api/method/erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry", json=payload) as resp:
            payment_entry = resp.js['message']
            assert payment_entry is not None
            del payment_entry["taxes"]
            del payment_entry["deductions"]
            del payment_entry["__islocal"]
            del payment_entry["__unsaved"]
            for res in payment_entry['references']:
                res['docstatus'] = 1
                del res["__islocal"]
            
            # ref number & reference date
            payment_entry['docstatus'] = 1
            payment_entry['reference_no'] = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            payment_entry['reference_date'] = TODAY

        with self.user.rest("POST", '/api/resource/Payment Entry', json={'data': payment_entry}) as resp:
            assert resp.js['data'] is not None
    
    tasks = [get_balance_sheet, get_trial_balance, get_profit_loss, get_general_ledger]

    @task(1)
    def stop(self):
        logging.info(f'{datetime.now()} [TaskSet] [PurchaseAccountant] [stop]')
        self.interrupt(reschedule=True)