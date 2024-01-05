import random, string

from datetime import datetime
from tasks.utils.constants import TODAY
from tasks.utils.functions import *

def get_account_reporting(user, qparam: dict, filters: dict):
    qparam = get_qparam_urlencoded(qparam, filters)
    with user.rest("GET", f"/api/method/frappe.desk.query_report.run?{qparam}") as resp:
        assert resp.js['message'] is not None

"""
General Ledger:
 Accounting --> Reports --> General Ledge
 https://mn.staging.stanch.io/api/method/frappe.desk.query_report.run?
    report_name=General Ledger
    filters={
        "company":"MN",
        "from_date":"2023-12-02",
        "to_date":"2024-01-02",
        "group_by":"Group by Voucher (Consolidated)",
        "include_dimensions":1
    }
"""
def get_general_ledger(taskset):
    qparam = { 'report_name': 'General Ledger' }
    filters = {
        "company": taskset.user.company,
        "from_date":"2023-12-02",
        "to_date":"2024-01-02",
        "group_by":"Group by Voucher (Consolidated)",
        "include_dimensions":1
    }
    get_account_reporting(taskset.user, qparam, filters)

"""
Trial Balance:
 Accounting --> Reports --> Trial Balance
 https://mn.staging.stanch.io/api/method/frappe.desk.query_report.run?
    report_name=Trial Balance
    filters={
        "company":"MN",
        "fiscal_year":"2023-2024",
        "from_date":"2023-04-01",
        "to_date":"2024-03-31",
        "with_period_closing_entry":1,
        "show_unclosed_fy_pl_balances":1,
        "include_default_book_entries":1
    }
    is_tree=true
    parent_field=parent_account
"""
def get_trial_balance(taskset):
    qparam = {
        'report_name': 'Trial Balance',
        'is_tree': True,
        'parent_field': 'parent_account'
    }
    filters={
        "company": taskset.user.company,
        "fiscal_year": "2023-2024",
        "from_date": "2023-04-01",
        "to_date": "2024-03-31",
        "with_period_closing_entry": 1,
        "show_unclosed_fy_pl_balances": 1,
        "include_default_book_entries": 1
    }
    get_account_reporting(taskset.user, qparam, filters)

"""
Balance Sheet
 Accounting --> Reports --> Balance Sheet
 https://mn.staging.stanch.io/api/method/frappe.desk.query_report.run?
    report_name=Profit and Loss Statement
    filters={
        "company":"MN",
        "filter_based_on":"Fiscal Year",
        "period_start_date":"2023-04-01",
        "period_end_date":"2024-03-31",
        "from_fiscal_year":"2023-2024",
        "to_fiscal_year":"2023-2024",
        "periodicity":"Yearly",
        "include_default_book_entries":1
    }
    is_tree=true
    arent_field=parent_account
"""
def get_balance_sheet(taskset):
    qparam = {
        'report_name': 'Profit and Loss Statement',
        'is_tree': True,
        'parent_field': 'parent_account'
    }
    filters={
        "company": taskset.company,
        "filter_based_on": "Fiscal Year",
        "period_start_date": "2023-04-01",
        "period_end_date": "2024-03-31",
        "from_fiscal_year": "2023-2024",
        "to_fiscal_year": "2023-2024",
        "periodicity": "Yearly",
        "include_default_book_entries": 1
    }
    get_account_reporting(taskset.user, qparam, filters)
"""
Profit & Loss
 Accounting --> Reports --> Profit amd Loss
 https://mn.staging.stanch.io/api/method/frappe.desk.query_report.run?
    report_name=Profit and Loss Statement
    filters={
        "company":"MN",
        "filter_based_on":"Fiscal Year",
        "period_start_date":"2023-04-01",
        "period_end_date":"2024-03-31",
        "from_fiscal_year":"2023-2024",
        "to_fiscal_year":"2023-2024",
        "periodicity":"Yearly",
        "include_default_book_entries":1
    }
    is_tree=true
    parent_field=parent_account
"""
def get_profit_loss(taskset):
    qparam = {
        'report_name': 'Profit and Loss Statement',
        'is_tree': True,
        'parent_field': 'parent_account'
    }
    filters = {
        "company": taskset.company,
        "filter_based_on": "Fiscal Year",
        "period_start_date": "2023-04-01",
        "period_end_date": "2024-03-31",
        "from_fiscal_year": "2023-2024",
        "to_fiscal_year": "2023-2024",
        "periodicity": "Yearly",
        "include_default_book_entries": 1
    }
    get_account_reporting(taskset.user, qparam, filters)
