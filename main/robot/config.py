from typing import Any

INDEXES_INFO: dict[str, dict[str, Any]] = {
        "S&P 500": {
            "url": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
            "table_nr": 0,
            "ticker_name": "^SPX"
        },
        "NASDAQ 100": {
            "url": "https://en.wikipedia.org/wiki/Nasdaq-100",
            "table_nr": 3,
            "ticker_name": "^NDX"
        }
    }
MA_WINDOW: int = 21
