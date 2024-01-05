import json
import logging

from tasks.utils.constants import APP_DICT
from urllib.parse import urlencode

def get_payload_urlencoded(payload) -> str:
    encoded = urlencode(payload)
    # replace any single-quotes into double-quotes
    return encoded.replace ('%27', '%22')
    
def get_qparam_urlencoded(q_param, filters) -> str:
    if filters:
        q_param['filters'] = json.dumps(filters, separators=(",", ":"))

    logging.debug(q_param)
    return get_payload_urlencoded(q_param)

def get_auth_token(host: str) -> str:
    try:
        auth_token = APP_DICT[host]['auth']
        logging.debug(f"Auth Token retrieved: {auth_token}")
        return auth_token
    except KeyError as ex:
        raise(f"Host's auth token for {host} not found.")

def get_company(host: str) -> str:
    try:
        return APP_DICT[host]['company']
    except KeyError as ex:
        raise(f"Host's company name for {host} not found.")