import requests
import json
from datetime import datetime, timedelta

cache_expired_time = 20
cache = {}


def caching_decorator(func):
    def cache_data(*args):
        arg = ':'.join(args) if args else 'default'
        cached = cache.get(func.__name__, None)
        if cached:
            cached_data = cached.get(arg, None)
            if cached_data and cached_data.get('time') > datetime.utcnow() - timedelta(
                    seconds=cache_expired_time):
                # print(f"{GREEN}•{RESET}", end=RESET) #{GREEN}cached {func.__name__}{RESET}", end=' ')
                return cached_data.get('data')
        data = func(*args)
        cache.setdefault(func.__name__, {})
        cache[func.__name__].update({arg: {'time': datetime.utcnow(), 'data': data}})
        # print(f"{RED}•{RESET}", end=RESET)  #{RED}{func.__name__}{RESET}
        return data
    return cache_data


headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Length": "123",
    "content-type": "application/json",
    "Host": "p2p.binance.com",
    "Origin": "https://p2p.binance.com",
    "Pragma": "no-cache",
    "TE": "Trailers",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
}

data = {
    "asset": "USDT",
    "fiat": "EUR",
    "merchantCheck": False,
    "page": 1,
    "payTypes": [],
    "publisherType": None,
    "rows": 1,
    "tradeType": "BUY"
}


@caching_decorator
def get_price(asset: str, fiat: str, side: str = "BUY", p_type: str = None) -> float:
    data['asset'] = asset
    data['fiat'] = fiat
    data['tradeType'] = side
    if p_type:
        data['payTypes'] = [p_type]
    r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search',
            headers=headers,
            json=data)
    try:
        d = json.loads(r.text)
        return d['data'][0]['adv']['price']
    except:
        return 0


# print(get_price('USDT', 'RUB', 'BUY'))
# print(get_price('USDT', 'RUB', 'BUY', 'Tinkoff'))
# print(get_price("USDT", "TRY", "BUY"))
# print(get_price("USDT", "TRY", "SELL"))
# print(get_price(asset="USDT", fiat="TRY", side="BUY"))
