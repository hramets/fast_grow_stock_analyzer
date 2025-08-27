from classes import(
    DataFilter,
    Yfinance,
    Metrics
)
import pandas as pd
from pandas import DataFrame
from datetime import datetime
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


def main():

    ## Getting period and checking format

    right_date_format: bool = False
    while not right_date_format:
        right_date_format = True
        start_period: str = input("Start period (yyyy-mm-dd): ").strip()
        end_period: str = input("End period (yyyy-mm-dd): ").strip()
        for date in [start_period, end_period]:
            try:
                datetime.strptime(date)
            except:
                print("Wrong data format. Try again.")
                right_date_format = False
    
    

    ### Getting an index's stocks data.
    # The robot maintains several indexes: S&P 500, NASDAQ 100, NASDAQ COMPOSITE.
    
    # {index: (wiki web page, table nr on the page)}
    # On wiki an index's page has several tables.
    # A position of the table with tickers list always differs.
    indexes_data: dict[str, tuple[str, int]] = {
        "S&P 500": ("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", 0),
        "NASDAQ 100": ("https://en.wikipedia.org/wiki/Nasdaq-100", 3)
    }
    indexes: list = list(indexes_data.keys())
    
    ## User chooses index.

    while not index_nr_is_digit:
        index_nr: str = input(
            "\n".join(
                [
                    f"{n} - {indexes}" for n, index in enumerate(indexes_data.keys())
                ]
            ) + "\nPut one of the nr: "
        )
        index_nr_is_digit = True if (
            index_nr.isdigit() and int(index_nr) in range(len(indexes_data.keys()))
        ) else print("Invalid input.")
    
    chosen_index: str = indexes[int(index_nr)]
    chosen_index_params: tuple[str, int] = indexes_data[chosen_index]
    
    ## Extracting the chosen index tickers from wiki.
    
    try:
        index_tickers_data: DataFrame = pd.read_html(
            io=indexes_data[chosen_index_params][0] # web page
        )[indexes_data[chosen_index_params][1]] # table nr
    except Exception as e:
        error_msg = f"Error in extracting the index tickers data from wiki."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return
    
    index_tickers: list[str] = index_tickers_data[index_tickers_data.columns[0]]\
        .to_list()

    ## Extracting tickers' stock data and index_data.
    
    yahoo_fin = Yfinance()

    # For moving average date requires a longer period.
    # Redudant 21 days data will be deleted.
    try:
        stocks_data = yahoo_fin.get_price_data(
            tickers=index_tickers,
            period=(
                datetime.strptime(start_period) - 21, datetime.strptime(end_period)
            )
        )
    except Exception as e:
        error_msg = "Error in extracting the index stocks data."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return
    
    try:
        index_data = yahoo_fin.get_price_data(tickers=chosen_index)
    except Exception as e:
        error_msg = "Error in extracting the index data."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return
    
    ## Calculating metrics.
    
    metrics = Metrics()
    
    # In the initial data the first col lvl is prices, the second - tickers.
    # Should be changed according to methods, that will be used.
    multi_lvl_cols: pd.MultiIndex = stocks_data.columns
    new_multi_lvl_cols = multi_lvl_cols.reorder_levels(order=[1, 0])
    stocks_data.columns = new_multi_lvl_cols
    
    try:
        for stock in index_tickers:
            stocks_data[stock, "rs"] = metrics.rs(
                stock_price=stocks_data[stock, "Close"],
                market_price=index_data["Close"]
            )
    except Exception as e:
        error_msg = "Error in calculating rs."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return
    
    while not ma_win_is_digit:
        ma_window = input("Moving average window (1-21): ")
        if not ma_window.isdigit() or not 0 < int(ma_window) < 22:
            print("Invalid input.")
            ma_win_is_digit = False
        else:
            ma_window = int(ma_window)
            ma_win_is_digit = True
        
        
    try: 
        stocks_data = metrics.rs_ma(
            stocks_data=stocks_data,
            ma_window=ma_window
        )
    except:
        error_msg = "Error in calculating moving average."
        error_logger.critical(
            msg=error_msg + f"\nDescription: {e}"
        )
        print(error_msg + "See logs.")
        return

    # Cutting the tail with 21 days for ma calculating.
    
    stocks_data = stocks_data[stocks_data["Date"] > start_period]
    
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
    print(", ".join(list(full_filtered_stocks_data.columns)))
    