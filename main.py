from result_evaluator import (
    evaluate_after_delay
)

from datetime import datetime, UTC
import asyncio
import json

import aiohttp
import websockets

from telegram_router import send_telegram

from signal_logger import (
    initialize_csv,
    log_signal
)

from metrics import (
    update_trade,
    total_score,
    price_history
)

from config import (
    ALERT_SCORE,
    WEBSOCKET_BATCH_SIZE,
    MIN_PRICE_MOVE
)

# ==========================================
# MEMORY
# ==========================================

last_alert = {}

# ==========================================
# SYMBOLS
# ==========================================

async def get_symbols():

    url = (
        "https://api.bybit.com/v5/market/"
        "instruments-info?category=linear"
    )

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            text = await response.text()

            print("BYBIT RESPONSE:")
            print(text)

            data = await response.json()

            symbols = []

            for item in data["result"]["list"]:

                symbol = item["symbol"]

                if symbol.endswith("USDT"):
                    symbols.append(symbol)

            return symbols

# ==========================================
# BATCHING
# ==========================================

def chunk_list(items, size):

    return [
        items[i:i + size]
        for i in range(
            0,
            len(items),
            size
        )
    ]

# ==========================================
# ALERTS
# ==========================================

async def evaluate(symbol):

    from time import time

    from metrics import (
        get_price_move,
        get_volume_spike,
        get_trade_speed
    )

    score = total_score(symbol)

    print(
        f"{symbol} | Score={score:.1f}"
    )

    if score < ALERT_SCORE:
        return

    now = time()

    if symbol in last_alert:

        seconds_passed = (
            now - last_alert[symbol]
        )

        if seconds_passed < 900:
            return

    price_move = get_price_move(symbol)

    entry_price = (
        price_history[symbol][-1]
    )

    volume_spike = get_volume_spike(symbol)

    trade_speed = get_trade_speed(symbol)

    if abs(price_move) < MIN_PRICE_MOVE:
        return

    if price_move <= 0:
        return

    direction = "🟢 LONG MOMENTUM"

    if score >= 95:
        confidence = "🔥 ELITE"

    elif score >= 90:
        confidence = "⭐⭐⭐⭐⭐"

    elif score >= 80:
        confidence = "⭐⭐⭐⭐"

    else:
        confidence = "⭐⭐⭐"

    bybit_link = (
        f"https://www.bybit.com/trade/usdt/{symbol}"
    )

    utc_time = datetime.now(UTC).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    message = f"""
{direction}

📈 Asset: {symbol}

⭐ Score: {score:.0f}/100

🎯 Confidence: {confidence}

📊 Price Move: {price_move:+.2f}%

🔥 Volume Spike: {volume_spike:.2f}x

⚡ Trade Speed: {trade_speed}

⏰ {utc_time} UTC

🔗 Bybit:

{bybit_link}
"""

    await send_telegram(message)

    log_signal(
    utc_time,
    symbol,
    direction,
    entry_price,
    score,
    price_move,
    volume_spike
)

    asyncio.create_task(
        evaluate_after_delay(
            utc_time,
            symbol,
            direction,
            entry_price,
        900,
        "result_15m"
    )
)

    asyncio.create_task(
    evaluate_after_delay(
        utc_time,
        symbol,
        direction,
        entry_price,
        1800,
        "result_30m"
    )
)

    asyncio.create_task(
    evaluate_after_delay(
        utc_time,
        symbol,
        direction,
        entry_price,
        3600,
        "result_60m"
    )
)

    last_alert[symbol] = now

# ==========================================
# PROCESS TRADE
# ==========================================

async def process_trade(symbol, trade):

    try:

        price = float(trade["p"])
        volume = float(trade["v"])

        update_trade(
            symbol,
            price,
            volume
        )

        await evaluate(symbol)

    except Exception as e:

        print(
            f"Trade Error {symbol}: {e}"
        )

# ==========================================
# WEBSOCKET BATCH
# ==========================================

async def websocket_batch(symbols):

    url = (
        "wss://stream.bybit.com/"
        "v5/public/linear"
    )

    while True:

        try:

            async with websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=20
            ) as ws:

                args = []

                for symbol in symbols:

                    args.append(
                        f"publicTrade.{symbol}"
                    )

                subscribe = {
                    "op": "subscribe",
                    "args": args
                }

                await ws.send(
                    json.dumps(subscribe)
                )

                print(
                    f"Batch Connected: "
                    f"{len(symbols)} symbols"
                )

                while True:

                    raw = await ws.recv()

                    data = json.loads(raw)

                    if "topic" not in data:
                        continue

                    topic = data["topic"]

                    if not topic.startswith(
                        "publicTrade."
                    ):
                        continue

                    symbol = topic.split(".")[1]

                    trades = data.get(
                        "data",
                        []
                    )

                    for trade in trades:

                        await process_trade(
                            symbol,
                            trade
                        )

        except Exception as e:

            print(
                f"Batch Error: {e}"
            )

            await asyncio.sleep(5)

# ==========================================
# MAIN
# ==========================================

async def main():

    initialize_csv()

    print(
        "Loading Bybit Symbols..."
    )

    await send_telegram(
        "✅ Momentum Scanner V2 Online"
    )

    symbols = await get_symbols()

    print(
        f"Found {len(symbols)} symbols"
    )

    batches = chunk_list(
        symbols,
        WEBSOCKET_BATCH_SIZE
    )

    print(
        f"Created {len(batches)} batches"
    )

    tasks = []

    for batch in batches:

        tasks.append(
            asyncio.create_task(
                websocket_batch(batch)
            )
        )

    await asyncio.gather(*tasks)

if __name__ == "__main__":

    asyncio.run(main())
