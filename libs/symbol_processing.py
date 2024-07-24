


def symbol_processing(symbol_input, processer=None) -> str:
    if any(substring in symbol_input for substring in ['AAPL', 'apple', 'Apple']):
        return 'AAPL.US'
    if any(substring in symbol_input for substring in ['tencent', '700', 'Tencent']):
        if processer == 'longport_openapi':
            return '700.HK'
        else:
            return '00700.HK'
    if any(substring in symbol_input for substring in ['9988', 'alibaba', 'Alibaba']):
        if processer == 'longport_openapi':
            return '9988.HK'
        else:
            return '09988.HK'
    return symbol_input

if __name__ == "__main__":
    symbol = symbol_processing('09988')
    print(symbol)