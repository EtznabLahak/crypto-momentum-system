import aiohttp
import csv
import asyncio

CSV_FILE = "signals.csv"


async def get_current_price(symbol):

    url = (
        "https://api.bybit.com/v5/market/tickers"
        f"?category=linear&symbol={symbol}"
    )

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            data = await response.json()

            return float(
                data["result"]["list"][0]["lastPrice"]
            )


def update_csv_result(
    timestamp,
    column_name,
    result
):

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        rows = list(csv.reader(f))

    header = rows[0]

    column_index = header.index(
        column_name
    )

    timestamp_index = header.index(
        "timestamp"
    )

    for row in rows[1:]:

        if row[timestamp_index] == timestamp:

            row[column_index] = str(result)

            break

    with open(
        CSV_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerows(rows)


async def evaluate_after_delay(
    timestamp,
    symbol,
    direction,
    entry_price,
    delay_seconds,
    column_name
):

    await asyncio.sleep(
        delay_seconds
    )

    try:

        current_price = (
            await get_current_price(
                symbol
            )
        )

        move = (
            (current_price - entry_price)
            / entry_price
        ) * 100

        if "SHORT" in direction:

            move = -move

        update_csv_result(
            timestamp,
            column_name,
            round(move, 2)
        )

        with open(
            "evaluator_log.txt",
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                f"{symbol} | {column_name} | {move:.2f}%\n"
            )

        print(
            f"{symbol} "
            f"{column_name} "
            f"{move:.2f}%"
        )

    except Exception as e:

        print(
            f"Evaluation Error: {e}"
        )