# Get Real-time Quotes Of Securities
# https://open.longportapp.com/docs/quote/pull/quote
# Before running, please visit the "Developers to ensure that the account has the correct quotes authority.
# If you do not have the quotes authority, you can enter "Me - My Quotes - Store" to purchase the authority through the "LongPort" mobile app.
from typing import List

from longport.openapi import QuoteContext, Config

config = Config.from_env()


def get_stock_price(symbol: str) -> float:
    print('openapi get stock price, symbol: ', symbol)
    ctx = QuoteContext(config)
    resp = ctx.quote([symbol])
    symbol, price = resp[0].symbol, resp[0].last_done
    return {"price": price, "symbol": symbol}


if __name__ == '__main__':
    result = get_stock_price('09899.HK')
    print(result['price'])