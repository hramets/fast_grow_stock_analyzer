from classes import(
    DataFilter,
    Yfinance,
    MetricsCalculator
)
from functions import get_page_tables
import config
import pandas as pd
from pandas import DataFrame
from datetime import datetime, timedelta
import logging


error_logger = logging.getLogger()
error_logger.setLevel(
    level=logging.WARNING
)
handler = logging.FileHandler(
    filename="errors.logs",
    mode="a"
)
formatter = logging.Formatter(
    fmt="%(name)s %(asctime)s %(message)s\nLine: %(lineno)s"
)
handler.setFormatter(
    fmt=formatter
)
error_logger.addHandler(hdlr=handler)


def main() -> None:
    ### Getting period and checking format

    # right_date_format: bool = False
    # while not right_date_format:
    #     start_period: str = input("Start period (yyyy-mm-dd): ").strip()
    #     try:
    #         datetime.strptime(start_period, "%Y-%m-%d")
    #     except:
    #         print("Wrong data format for start period. Try again.")
    #         continue
    #     end_period: str = input("End period (yyyy-mm-dd): ").strip()
    #     try:
    #         datetime.strptime(end_period, "%Y-%m-%d")
    #     except:
    #         print("Wrong data format for end period. Try again.")
    #         continue
    #     right_date_format = True
    end_period: str = "2024-06-01" # Testing
    start_period: str = "2024-05-01" # Testing
    start_period_dt = datetime.strptime(start_period, "%Y-%m-%d")
    end_period_dt = datetime.strptime(end_period, "%Y-%m-%d")
    
    

    ### Getting an index's stocks data.
    
    # The robot maintains several indexes: S&P 500, NASDAQ 100, NASDAQ COMPOSITE.
    
    # {index: (wiki web page, table nr on the page)}
    # On wiki an index's page has several tables.
    # A position of the table with tickers list always differs.
    indexes_info = config.INDEXES_INFO
    indexes: list = list(indexes_info.keys())
    
    ## User chooses index.

    index_nr_is_digit: bool = False
    while not index_nr_is_digit:
        index_nr: str = input(
            "\n".join(
                [
                    f"{n} - {index}" for n, index in enumerate(indexes_info.keys())
                ]
            ) + "\nPut one of the nr: "
        )
        index_nr_is_digit = True if (
            index_nr.isdigit() and int(index_nr) in range(len(indexes_info.keys()))
        ) else print("Invalid input.")
    
    chosen_index: str = indexes[int(index_nr)]
    chosen_index_url: str = indexes_info[chosen_index]["url"]
    chosen_index_table_nr: int = indexes_info[chosen_index]["table_nr"]
    chosen_index_ticker_name: str = indexes_info[chosen_index]["ticker_name"]
    
    ## Extracting the chosen index tickers from wiki.
    
    try:
        wiki_page_tables = get_page_tables(url=chosen_index_url)
    except Exception as e:
        error_msg = f"Error in extracting tables from {chosen_index_url}."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return
    
    try:
        tickers_table = wiki_page_tables[chosen_index_table_nr]
    except Exception as e:
        error_msg = f"Error in extracting table nr {chosen_index_table_nr} from \
            {chosen_index_url}."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return
    
    tickers: list[str] = tickers_table[tickers_table.columns[0]] \
        .to_list()
    tickers.append(chosen_index_ticker_name) # For rs calculating.

    ### Extracting tickers' stock data and index_data.
    
    yahoo_fin = Yfinance()

    # For moving average date requires a longer period.
    # Redudant 21 days data will be deleted.
    try:
        stocks_data_for_ma = yahoo_fin.get_price_data(
            tickers=tickers,
            period=(
                start_period_dt - timedelta(days=21),
                end_period_dt
            )
        )
    except Exception as e:
        error_msg = "Error in extracting the index stocks data."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return
    
    ## Calculating metrics.
    
    metrics = MetricsCalculator()
    
    try:
        stocks_data_for_ma = metrics.rs_on_data(
            stocks_data=stocks_data_for_ma,
            market_ticker=chosen_index_ticker_name
        )
    except Exception as e:
        error_msg = "Error in calculating rs."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return
    
    ma_window = config.MA_WINDOW
        
    try: 
        stocks_data_for_ma = metrics.rs_ma_on_data(
            stocks_data=stocks_data_for_ma,
            ma_window=ma_window
        )
    except Exception as e:
        error_msg = "Error in calculating moving average."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return

    # Cutting the tail with 21 days for ma calculating.

    stocks_data = stocks_data_for_ma[stocks_data_for_ma.index >= start_period]
    
    ## Filterting stocks
    
    stock_filter = DataFilter()

    try:
        rs_filtered_stocks_data = stock_filter.has_rs_grown(
            stocks_data=stocks_data
        )
    except Exception as e:
        error_msg = "Error in filtering stocks by rs."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return
    
    max_days_rs_holds_above_ma = len(stocks_data)
    days_val_is_digit: bool = False
    while not days_val_is_digit:
        days_rs_holds_above_ma = input("Moving average window: ")
        if not days_rs_holds_above_ma.isdigit() or int(days_rs_holds_above_ma) > max_days_rs_holds_above_ma:
            print("Invalid input.")
            days_val_is_digit = False
        else:
            days_rs_holds_above_ma = int(days_rs_holds_above_ma)
            days_val_is_digit = True
    
    try:
        full_filtered_stocks_data = stock_filter.has_rs_crossed_ma(
            stocks_data=rs_filtered_stocks_data,
            days_rs_holds_above_ma=days_rs_holds_above_ma
        )
    except Exception as e:
        error_msg = "Error in filtering stocks by rs that crossed ma."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return
    
    ## Result
    print(
        ", ".join(
            list(
                full_filtered_stocks_data.columns.get_level_values(1).unique()
            )
        )
    )


if __name__ == "__main__":
    main()
    