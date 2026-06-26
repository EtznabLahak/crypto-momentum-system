from collections import defaultdict
from time import time

price_history = defaultdict(list)
volume_history = defaultdict(list)

trade_timestamps = defaultdict(list)


def update_trade(symbol, price, volume):

    price_history[symbol].append(price)

    if len(price_history[symbol]) > 20:
        price_history[symbol].pop(0)

    volume_history[symbol].append(volume)

    if len(volume_history[symbol]) > 50:
        volume_history[symbol].pop(0)

    now = time()

    trade_timestamps[symbol].append(now)

    cutoff = now - 60

    trade_timestamps[symbol] = [
        t
        for t in trade_timestamps[symbol]
        if t > cutoff
    ]


def price_score(symbol):

    prices = price_history[symbol]

    if len(prices) < 20:
        return 0

    move = abs(
        (prices[-1] - prices[0]) / prices[0]
    ) * 100

    return min(move * 10, 30)


def volume_score(symbol):

    volumes = volume_history[symbol]

    if len(volumes) < 20:
        return 0

    avg = sum(volumes[:-1]) / len(volumes[:-1])

    if avg == 0:
        return 0

    ratio = volumes[-1] / avg

    return min(ratio * 10, 30)


def speed_score(symbol):

    speed = len(
        trade_timestamps[symbol]
    )

    return min(speed, 20)


def total_score(symbol):

    return (
        price_score(symbol)
        + volume_score(symbol)
        + speed_score(symbol)
    )


def get_price_move(symbol):

    prices = price_history[symbol]

    if len(prices) < 20:
        return 0

    return (
        (prices[-1] - prices[0])
        / prices[0]
    ) * 100


def get_volume_spike(symbol):

    volumes = volume_history[symbol]

    if len(volumes) < 20:
        return 1

    avg = sum(volumes[:-1]) / len(volumes[:-1])

    if avg == 0:
        return 1

    return volumes[-1] / avg


def get_trade_speed(symbol):

    return len(
        trade_timestamps[symbol]
    )
