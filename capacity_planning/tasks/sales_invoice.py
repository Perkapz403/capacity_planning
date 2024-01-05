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
            "reference_doctype": "Sales Invoice Item"
        }
    if name:
        if not filters:
            filters = {}
        filters['name'] = name
        q_param['fields'] = ["*"]
    return get_qparam_urlencoded(q_param, filters)

def get_si_customer_qparam(name=None):
    return get_rest_api_qparam(q_param=None, filters=None, name=name)

def get_si_item_qparam(name=None):
    filters = {
        "disabled": 0,
        "is_sales_item": 1,
        "has_variants": 0
    }
    return get_rest_api_qparam(q_param=None, filters=filters, name=name)

def get_si_debit_to_qparam(company, name=None):
    filters = {
        "account_type": "Receivable",
        "is_group": 0,
        "company": company
    }
    return get_rest_api_qparam(q_param=None, filters=filters, name=name)

def get_si_income_account_qparam(company, name=None):
    filters = {
        "company": company,
        "root_type": "Income",
        "is_group": 0
    }
    return get_rest_api_qparam(q_param=None, filters=filters, name=name)

def get_filtered_dimensions_qparam(doctype: str, company:str, account:str = None):
    q_param = {
        "txt": "",
        "doctype": doctype.title(),
        "ignore_user_permissions": 0,
        "reference_doctype": "Sales Invoice",
        "query": "erpnext.controllers.queries.get_filtered_dimensions"
    }

    filters={
        "dimension": doctype.lower(),
        "company": company
    }

    if account:
        filters["account"] = account
    
    return get_qparam_urlencoded(q_param, filters)

class SalesInvoice:
    """
    Item: Mandatory parameters
    ["income_account", "item_name", "description",  "uom", "conversion_factor", "rate", "amount", base_rate", "base_amount", "cost_center"]

    Link:
    ["income_account", "uom", "cost_center"]
    """
    branch: hash
    company: str
    cost_center: hash
    customer: hash
    debit_to: hash
    income_account: hash
    item: hash
    sales_invoice: hash
    name: str
    selling_price_list: str = "Standard Selling"
    conversion_rate: float = 1.0
    currency: str = "INR"

    def gen_sales_invoice_req_body(self):
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
            "selling_price_list": self.selling_price_list,
            "price_list_currency": self.currency,
            "plc_conversion_rate": self.conversion_rate,
            "debit_to": self.debit_to['name'],
            "cost_center": self.cost_center['value'],
            "branch": self.branch['value'],
            "base_net_total": price,
            "base_grand_total": price,
            "grand_total": price,
            # customer
            "customer": self.customer['name'],
            "customer_name": self.customer['customer_name'],
            "territory": self.customer['territory'],
            "customer_group": self.customer['customer_group'],
            # items
            "items": [
                {
                    "income_account": self.income_account['name'],
                    "item_name": self.item['name'],
                    "description": self.item['description'],
                    "uom": "Nos",
                    "qty": 1.0,
                    "conversion_factor": self.conversion_rate,
                    "rate": price,
                    "amount": price,
                    "base_rate": price,
                    "base_amount": price,
                    #"cost_center": self.cost_center['value']
                }
            ]
        }

class SalesAccountant(SequentialTaskSet):
    def on_start(self):
        logging.info(f'{datetime.now()} [TaskSet] [SalesAccountant] [on_start]')
        self.invoice = SalesInvoice()
        self.company = self.invoice.company = self.user.company

    @task(1)
    def create_sales_invoice(self):
        logging.info(f'{datetime.now()} [TaskSet] [SalesAccountant] [create_sales_invoice]')

        cust_name = None

        # Get customer
        qparam = get_si_customer_qparam()
        with self.user.rest("GET", f"/api/resource/Customer?{qparam}") as resp:
            res_data  = random.choice(resp.js['data'])
            cust_name = res_data['name']
            assert cust_name is not None

        qparam = get_si_customer_qparam(cust_name)
        with self.user.rest("GET", f"/api/resource/Customer?{qparam}") as resp:
            customer = resp.js['data'][0]
            assert customer is not None
            self.invoice.customer = customer

        # Get Account
        qparam = get_si_debit_to_qparam(self.company)
        with self.user.rest("GET", f"/api/resource/Account?{qparam}") as resp:
            res_data  = random.choice(resp.js['data'])
            acc_name = res_data['name']
            assert acc_name is not None
        
        qparam = get_si_customer_qparam(acc_name)
        with self.user.rest("GET", f"/api/resource/Account?{qparam}") as resp:
            account = resp.js['data'][0]
            assert account is not None
            self.invoice.debit_to = account

        # Get Item
        qparam = get_si_item_qparam()
        with self.user.rest("GET", f"/api/resource/Item?{qparam}") as resp:
            res_data  = random.choice(resp.js['data'])
            item_name = res_data['name']
            assert item_name is not None

        qparam = get_si_item_qparam(item_name)
        with self.user.rest("GET", f"/api/resource/Item?{qparam}") as resp:
            item = resp.js['data'][0]
            assert item is not None
            self.invoice.item = item

        # Get Income account
        qparam = get_si_income_account_qparam(company=self.company)
        with self.user.rest("GET", f"/api/resource/Account?{qparam}") as resp:
            res_data  = random.choice(resp.js['data'])
            income_acc_name = res_data['name']
            assert income_acc_name is not None

        qparam = get_si_income_account_qparam(company=self.company, name=income_acc_name)
        with self.user.rest("GET", f"/api/resource/Account?{qparam}") as resp:
            income_acc = resp.js['data'][0]
            assert income_acc is not None
            self.invoice.income_account = income_acc

        # Cost center
        qparam = get_filtered_dimensions_qparam(
            doctype='Cost Center',
            company=self.company,
            account=self.invoice.debit_to['name']
        )
        with self.user.rest("POST", f"/api/method/frappe.desk.search.search_link?{qparam}") as resp:
            res_data = random.choice(resp.js['results'])
            assert res_data is not None
            self.invoice.cost_center = res_data

        # Branch
        qparam = get_filtered_dimensions_qparam(
            doctype='Branch',
            company=self.company,
            account=self.invoice.debit_to['name']
        )
        with self.user.rest("POST", f"/api/method/frappe.desk.search.search_link?{qparam}") as resp:
            res_data = random.choice(resp.js['results'])
            assert res_data is not None
            self.invoice.branch = res_data

        # Create Sales invoice
        logging.info(self.invoice.gen_sales_invoice_req_body())
        with self.user.rest("POST", '/api/resource/Sales Invoice', json={'data': self.invoice.gen_sales_invoice_req_body()}) as resp:
            sales_invoice = resp.js['data']
            assert sales_invoice is not None
            self.invoice.sales_invoice = sales_invoice
            self.invoice.name = sales_invoice['name']
        
        # Sales Invoice - Accounted
        accounted = {"data": { "workflow_state": "Accounted", "docstatus":1 }}
        with self.user.rest("PUT", f'/api/resource/Sales Invoice/{self.invoice.name}', json=accounted) as resp:
            assert resp.js['data'] is not None

    @task(1)
    def create_payment_entry(self):
        logging.info(f'{datetime.now()} [TaskSet] [SalesAccountant] [create_payment_entry]')
        payload = {
            'dt': 'Sales Invoice',
            'dn': self.invoice.sales_invoice['name']
        }
        payment_entry = None
        logging.info("========> Creating Payment Entry")
        logging.info(payload)
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

        logging.info(payment_entry)
        with self.user.rest("POST", '/api/resource/Payment Entry', json={'data': payment_entry}) as resp:
            assert resp.js['data'] is not None
    
    tasks = [get_balance_sheet, get_trial_balance, get_profit_loss, get_general_ledger]

    @task(1)
    def stop(self):
        logging.info(f'{datetime.now()} [TaskSet] [SalesAccountant] [stop]')
        self.interrupt(reschedule=True)