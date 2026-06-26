import csv
import os


CSV_FILE = "signals.csv"


def initialize_csv():

    if os.path.exists(CSV_FILE):
        return

    with open(
        CSV_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "timestamp",
            "symbol",
            "direction",
            "entry_price",
            "score",
            "price_move",
            "volume_spike",
            "result_15m",
            "result_30m",
            "result_60m"
        ])


def log_signal(
    timestamp,
    symbol,
    direction,
    entry_price,
    score,
    price_move,
    volume_spike
):

    with open(
        CSV_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            timestamp,
            symbol,
            direction,
            entry_price,
            score,
            price_move,
            volume_spike,
            "",
            "",
            ""
        ])