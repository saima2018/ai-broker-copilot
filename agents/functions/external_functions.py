import requests


url = "https://currency-conversion-and-exchange-rates.p.rapidapi.com/convert"


def currency_exchange(from_, to, amount, url=url, **kwargs):

    querystring = {"from": from_,"to": to, "amount": amount}

    headers = {
        "x-rapidapi-key": "ba9ebce432msh54dd85c134d09ffp1abedcjsndddcd8e42184",
        "x-rapidapi-host": "currency-conversion-and-exchange-rates.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    print(response.json())
    response = response.json()
    result = response['result']
    date = response['date']
    rate = response['info']['rate']
    resp_description = f'converted result: {result}, exchange rate: {rate} as of date {date}'
    return {'resp': result, 'resp_description': resp_description}




if __name__ == '__main__':

    currency_exchange('USD', 'CNY', 88)