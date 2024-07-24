import traceback
from typing import List
from urllib.parse import urlencode
import json
from longport.openapi import TradeContext, Config, HttpClient

from libs.symbol_processing import symbol_processing
from commons.cfg_loader import project_cfg
from .longport_openapi import *
from commons.logger import logger

# get config fields from config file or env or some secret management system


# create config object
# conf = Config(app_key = key, app_secret = secret, access_token = token, http_url = url)
http_cli = HttpClient(app_key= project_cfg.lp_key, app_secret=project_cfg.lp_secret, access_token=project_cfg.lp_token, http_url=project_cfg.lp_url)


def get_account_status(account_no, *args, **kwargs):

    method = "POST"

    uri = "/v1/whaleapi/account/get"
    params = f"account_no={account_no}"
    resp = http_cli.request(method, uri + '?' + params)
    # resp = json.dumps(resp, indent=4)
    resp_description = 'state: 1 means account deleted. disable: true means frozen'
    return {'resp': resp, 'resp_description': resp_description}


# function to "GET" account_info
def get_account_info():

    method = "GET"

    for account in account_list:
        uri = "/v1/whaleapi/account/open_info"
        params = f"account_no={account}"
        resp = http_cli.request(method, uri + '?' + params)
        resp = json.dumps(resp, indent=4)
        print(resp)


# function to "GET" stock_info
def get_stock_info(account_no, **kwargs):
    uri = "/v1/whaleapi/asset/stock_info"
    params = f"account_no={account_no}" # TODO for testing
    resp = http_cli.request("GET", uri + '?' + params)
    total_stock_value_by_market = {} # {'HK': 123, 'US':321}
    description = ''
    for stock in resp['stock_list']:
        last_done = float(stock['last_done'])
        total_quantity = float(stock['total_quantity'])
        stock_value = last_done * total_quantity
        market = stock['market']
        total_stock_value_by_market[market] = total_stock_value_by_market.get(market, 0) + stock_value
        stock['value'] = stock_value

    for stock in resp['stock_list']:
        share = round(stock['value']/total_stock_value_by_market[stock['market']], 2) * 100
        stock['share'] = share
        market = stock['market']
        symbol = stock['symbol']
        description += f'stock: {symbol}, market: {market}, percentage in own portfolio: {share}'
    # print(json.dumps(resp, indent=4))
    print('total value market: ', total_stock_value_by_market)
    description = description if description else 'you do not have any stock assets'
    print('stock info: ', description)
    # add intermediates
    resp['total_stock_value_by_market'] = total_stock_value_by_market
    return {'resp': resp,
            'resp_description': f'your total stock value by market: {total_stock_value_by_market}. Details: '+description}


def get_stock_symbols(account_no, *args, **kwargs)->List:
    uri = "/v1/whaleapi/asset/stock_info"
    params = f"account_no={account_no}" # TODO for testing
    resp = http_cli.request("GET", uri + '?' + params)
    result = []
    for stock in resp['stock_list']:
        stock_symbol = stock['symbol']
        result.append(stock_symbol)
    print('symbols: ', result)
    return result

# function to "GET" asset overview - uri = "/v1/whaleapi/asset/overview"
def get_asset_overview(account_no):
    uri = "/v1/whaleapi/asset/overview"
    params = f"account_no={account_no}"
    resp = http_cli.request("GET", uri + '?' + params)
    # resp = json.dumps(resp, indent=4)
    print(resp)
    resp_description = ''
    return {'resp': resp, 'resp_description': resp_description}


# function to "POST" asset detail info - uri = "/v1/whaleapi/asset/detail_info"
def get_asset_detail_info():
    method = "POST"

    for account in account_list:
        uri = "/v1/whaleapi/asset/detail_info"
        params = f"account_no={account}"
        resp = http_cli.request(method, uri + '?' + params)
        resp = json.dumps(resp, indent=4)
        print(resp)



# function to "POST" frozen_cash
def post_frozen_cash():

    method = "POST"

    currency = input("Enter currency (HKD/USD): ")
    frozen_amount = input("Enter amount to be frozen: ")
    biz_code = input("Enter biz code (default: CMTF): ")
    remark = input("Enter remark: ")

    for account in account_list:
        uri = "/v1/whaleapi/asset/frozen_cash"
        #params = f"account_no={account}&currency={currency}&frozen_amount={frozen_amount}&biz_code={biz_code}&remark=测试新股数据#1234"
        params = f"account_no={account}&currency={currency}&frozen_amount={frozen_amount}&biz_code={biz_code}&remark={remark}"
        resp = http_cli.request(method, uri + '?' + params)
        resp = json.dumps(resp, indent=4)
        print(resp)


# function to "GET" frozen history - uri = "/v1/whaleapi/asset/financial_frozen_flows"
def get_frozen_history():
    method = "GET"

    for account in account_list:
        uri = "/v1/whaleapi/asset/financial_frozen_flows"
        params = f"account_no={account}"
        resp = http_cli.request(method, uri + '?' + params)
        resp = json.dumps(resp, indent=4)
        print(resp)


# Historical Order Inquiry - /v1/whaleapi/trade/order/history
def get_order_history(account_no, **kwargs):
    uri = "/v1/whaleapi/trade/order/history"
    params = f"account_no={account_no}"
    resp = http_cli.request("GET", uri + '?' + params)
    # resp = json.dumps(resp, indent=4)
    resp_description = ""
    return {'resp': resp, 'resp_description': resp_description}


# today's order inquiry - /v1/whaleapi/trade/order/today
def get_today_order_history(account_no, **kwargs):
    uri = "/v1/whaleapi/trade/order/today"
    params = f"account_no={account_no}"
    resp = http_cli.request("GET", uri + '?' + params)
    # resp = json.dumps(resp, indent=4)
    resp_description = ""
    return {'resp': resp, 'resp_description': resp_description}


# place order "POST" - /v1/whaleapi/trade/order
def place_order(**kwargs):
    symbol = symbol_processing(kwargs.get('symbol'))
    kwargs['symbol'] = symbol

    uri = "/v1/whaleapi/trade/order"
    order_type = kwargs.get('order_type')
    if order_type == "MO":
        try:
            result = get_stock_price(symbol)
            kwargs['submitted_price'] = result['price']
        except:
            return {'resp': {'api': uri, 'params': kwargs, 'symbol': symbol},
                    'resp_description': 'failed at price quote'}

    return {'resp': {'api': uri, 'params': kwargs, 'symbol': symbol}, 'resp_description': 'order placed per instruction'}

#  "order_id": "985446267550257152"


# function to withdraw order with order_id and account_no - /v1/whaleapi/trade/order
def withdraw_order():
    method = "DELETE"
    
    order_id = input("Enter order_id: ")
    account_no = input("Enter account_no: ")
    
    uri = "/v1/whaleapi/trade/order"
    params = f"order_id={order_id}&account_no={account_no}"
    resp = http_cli.request(method, uri + '?' + params)
    resp = json.dumps(resp, indent=4)
    print(resp)


# function to withdraw IPO order with order_id and account_no - /v1/whaleapi/ipo/withdraw
def withdraw_IPO_order():
    method = "POST"
    
    order_id = input("Enter order_id: ")
    account_no = input("Enter account_no: ")
    
    uri = "/v1/whaleapi/ipo/withdraw"
    params = f"order_id={order_id}&account_no={account_no}"
    resp = http_cli.request(method, uri + '?' + params)
    resp = json.dumps(resp, indent=4)
    print(resp)


# function to get IPO order history - /v1/whaleapi/ipo/order/list
def get_IPO_order_history():
    method = "GET"

    for account in account_list:
        uri = "/v1/whaleapi/ipo/order/list"
        params = f"account_no={account}"
        resp = http_cli.request(method, uri + '?' + params)
        resp = json.dumps(resp, indent=4)
        print(resp)


def query_account_cash_balance(account_no,  *args, **kwargs):
    currency = None
    uri = "/v1/whaleapi/asset/cash_info"
    params = f"account_no={account_no}"

    resp = http_cli.request("GET", uri + '?' + params)
    if currency:
        for n in resp['cash_list']:
            if n['currency'] == currency.upper():
                currency_cash_amount = n['cash_amount']
                currency_available_amount = n['available_amount']
                resp_description = f"total {currency} cash value {currency_cash_amount}, total available cash {currency_available_amount}"
                return {'resp': resp,
                    'resp_description': resp_description,
                    'total_cash': int(float(currency_cash_amount)),
                    'total_cash_available': int(float(currency_available_amount))}
    else:
        total_cash = resp['total_cash']
        total_available_cash = resp['total_available_cash']
        resp_description = f"total cash value {total_cash}, total available cash {total_available_cash}"
        return {'resp': resp,
                'resp_description': resp_description,
                'total_cash': int(float(total_cash)),
                'total_cash_available': int(float(total_available_cash))}


def calculate_affordable_shares(account_no, symbol, currency=None, **kwargs):
    # get currency balance if currency else total balance
    result = query_account_cash_balance(account_no, currency)
    resp, description, total, available = result['resp'], result['resp_description'], result['total_cash'], result['total_cash_available']
    if available <= 0:
        return {'resp':'0 share', 'resp_description': f'Your available balance is {available}, so you cannot make any purchase.'}
    # get current stock price
    symbol = symbol_processing(symbol, processer='longport_openapi')
    logger.info(f'getting price for stock: {symbol}')
    result = get_stock_price(symbol)
    price = int(result['price'])
    print('price: ', price)
    shares = available // price
    resp_description = f'you have available {currency}, {available}. the current price of {symbol} is {price}, so you can buy {shares} shares.'
    return {'resp': str(int(shares)), 'resp_description': resp_description}


if __name__ == "__main__":
    # account with IPO Stock
    account_list = [
        "PDU00000001",
        "PDC81030316UAT",
        "PDC80940316UAT",
        "PDC80950316UAT",
        "PDC80970316UAT",
        "PDC80960316UAT"
    ]
    #get_account_info()
    # get_stock_info(account_list[3])
    # get_asset_overview(account_no=account_list[5])
    #get_asset_detail_info()

    # get_order_history()
    # get_today_order_history()
    #withdraw_order()

    # place order
    # place_order(account_list[5], 'AAPL.US', 'Buy', '',10, time_in_force="Day", order_type = "LO",)

    result = query_account_cash_balance(account_list[0], 'HKD')
    print(result)
    #post_frozen_cash()
    # get_frozen_history()

    #withdraw_IPO_order()
    # get_IPO_order_history()

    # get_account_status()