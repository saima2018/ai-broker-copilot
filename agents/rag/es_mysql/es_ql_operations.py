import json
from typing import List

import requests

from commons.mysql_connector import mysql_conn
from agents.trading.trading_apis import get_stock_symbols
from commons.cfg_loader import project_cfg


def query_stock_info(symbol, table="dwd_stock_hk_trade_history_day", **kwargs):
    """
    query movement of a stock
    """
    # TODO 暂时写定两个表
    symbol = symbol.split('.')[0]
    if table == 'dwd_stock_hk_trade_history_day':
        sql = f"SELECT date, stock_name, open, close, high, low, volume, close_price_dod_per FROM {table} WHERE stock_code='{symbol}' ORDER BY date DESC LIMIT 7"
    # elif table == 'scm_track':
    #     sql = f"SELECT logistics_number, shipping_time, channels, logistics_status FROM scm_track WHERE id = '{id_}'"
    print('sqllllllllll ', sql)

    headers = {'Content-Type': 'application/json'}  # headers
    data = {
        "query": sql
    }
    response = requests.post(url=project_cfg.es_endpoint, headers=headers, json=data)
    resp = response.json()
    print('response:', resp)

    description = ''
    for stock in resp[::-1]:
        symbol = stock['stock_name']
        dod_change = stock['close_price_dod_per'] * 100
        description += f'stock {symbol}, percentage change last 1 day {dod_change}'
    return {'resp': resp, 'resp_description': description}


def query_stock_movement(account_no, **kwargs):
    """
    query account portfolio movements
    """
    stocks = get_stock_symbols(account_no)
    stocks = '(' + ','.join("'"+stock[:-3]+"'" for stock in stocks) + ')'
    print('stocks: ', stocks)
    table = 'dwd_stock_hk_trade_history_day'
    query = f"SELECT date, stock_code, stock_name, close, volume, close_price_dod_per, close_price_dod_gap FROM {table} WHERE stock_code in {stocks} ORDER BY date DESC LIMIT 1"  # sql query
    print('sqllllllllll ', query)
    headers = {'Content-Type': 'application/json'}  # headers
    data = {
        "query": query
    }
    response = requests.post(url=project_cfg.es_endpoint, headers=headers, json=data)
    resp = json.loads(response.text)
    print('response:', resp)

    description = ''
    for stock in resp:
        symbol = stock['stock_code']
        close_price_dod_per = stock['close_price_dod_per']*100
        date = stock['date']
        description += f'stock {symbol}.HK, day on day percentage change {close_price_dod_per}, as of date {date}'

    return {'resp': resp, 'resp_description': description}


def query_stock_code(qtext: str, market: str, topk: int, **kwargs):
    """
    query stock code from db endpoint
    """
    data = {
        "qtext": qtext,
        "market": 'hk'
    }
    response = requests.post(url=project_cfg.es_endpoint_stock_code, json=data)
    print('response:', response)
    resp = response.json()

    description = ''

    return {'resp': resp, 'resp_description': description}
