import unittest
from robot.classes import(
    Yfinance,
    MetricsCalculator,
    DataFilter
)
from pandas import(
    DataFrame,
    Series
)
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Callable


class TestYfinanceClass(unittest.TestCase):
    
    def test_get_price_data(self):
        yfin = Yfinance()

        tickers: list[str] = ["AAPL", "TSLA", "NVDA"]
        start_date = "2024-01-02"
        end_date = "2024-02-01"
        period: tuple[str] = (start_date, end_date)
        
        df: DataFrame = yfin.get_price_data(
            tickers=tickers,
            period=period
        )
        
        self.assertIs(
            expr1=type(df),
            expr2=DataFrame,
            msg=f"Wrong type result."
        )
        self.assertEqual(
            first=str(datetime.date(df.index[0])),
            second=start_date,
            msg="Period is extracted incorrectly."
        )
        self.assertCountEqual(
            first=tickers,
            second=set(df.columns.get_level_values(level=1)),
            msg="Stocks data is extracted incorrecly."
        )
        

class TestDataFilterClass(unittest.TestCase):
    
    def setUp(self):
        columns: list[tuple] = [
            ("NVDA", "close_price"),
            ("NVDA", "market_price"),
            ("TSLA", "close_price"),
            ("TSLA", "market_price")
        ]
        multi_cols = pd.MultiIndex.from_tuples(tuples=columns)
        df: DataFrame = DataFrame(
            data=[
                [22.7, 20.3, 20.3, 22.7],
                [18.4, 17.1, 17.1, 18.4],
                [29.1, 26.4, 26.4, 29.1],
                [11.6, 10.9, 10.9, 11.6],
                [26.3, 23.7, 23.7, 26.3],
                [13.2, 12.1, 12.1, 13.2],
                [17.8, 15.4, 15.4, 17.8],
                [25.5, 22.8, 22.8, 25.5],
                [19.9, 18.3, 18.3, 19.9],
                [27.4, 24.6, 24.6, 27.4],
                [10.8, 10.4, 10.4, 10.8],
                [23.3, 20.2, 20.2, 23.3],
                [15.6, 14.3, 14.3, 15.6],
                [28.9, 26.0, 26.0, 28.9],
                [21.2, 19.1, 19.1, 21.2],
                [12.5, 11.7, 11.7, 12.5],
                [24.0, 21.3, 21.3, 24.0],
                [16.7, 15.0, 15.0, 16.7],
                [14.1, 13.6, 13.6, 14.1],
                [20.6, 18.8, 18.8, 20.6],
                [29.8, 27.1, 27.1, 29.8],
                [10.1, 10.0, 10.0, 10.1],
                [30.0, 28.2, 28.2, 30.0],
                [11.3, 10.9, 10.9, 11.3],
                [13.9, 12.7, 12.7, 13.9],
                [17.2, 15.9, 15.9, 17.2]
            ],
            columns=multi_cols
        )
        calculate_rs: Callable[[float, float], float] = MetricsCalculator().rs
        calculate_rs_ma: Callable[[DataFrame], DataFrame] = MetricsCalculator().rs_ma_on_data
        for ticker, _ in multi_cols: 
            df[ticker, "rs"] = calculate_rs(
                stock_price=df[ticker, "close_price"],
                market_price=df[ticker, "market_price"]
            )
        df: DataFrame = calculate_rs_ma(
            stocks_data=df,
            ma_window=2
        )
        self.df = df
    
    def test_has_rs_grown(self):
        filter_has_rs_grown: Callable[[DataFrame], DataFrame] = \
            DataFilter().has_rs_grown
        df: DataFrame = filter_has_rs_grown(stocks_data=self.df)
        filtered_tickers_must_be: list = ["TSLA"]
        filtered_tickers_are: list = list(df.columns.get_level_values(0).unique())
        
        self.assertListEqual(
            list1=filtered_tickers_must_be,
            list2=filtered_tickers_are,
            msg=f"Tickers are filtered wrongly - {filtered_tickers_are}"
        )        
            
    def test_has_rs_crossed_ma(self):
        # According to the setUp dataframe, there must be left TSLA to the dataframe with a window of 1.
        # With the window of 2 there have to be no stocks.
        filter_has_rs_crossed_ma: Callable[[DataFrame, int], DataFrame] = \
            DataFilter().has_rs_crossed_ma
        df1: DataFrame = filter_has_rs_crossed_ma(
            stocks_data = self.df,
            days_rs_holds_above_ma=1
        )
        df2: DataFrame = filter_has_rs_crossed_ma(
            stocks_data = self.df,
            days_rs_holds_above_ma=2
        )
        
        df1_tickers_left: list = list(df1.columns.get_level_values(0).unique())
        df1_tickers_must_have_left: list = ["TSLA"]
        df2_tickers_left: list = list(df2.columns.get_level_values(0).unique())
        df2_tickers_must_have_left: list = []
        
        self.assertListEqual(
            list1=df1_tickers_left,
            list2=df1_tickers_must_have_left,
            msg=f"Must have left only TSLA with window of 1. Left - {df1_tickers_left}"
        )
        self.assertListEqual(
            list1=df2_tickers_left,
            list2=df2_tickers_must_have_left,
            msg=f"Must have left nothing with window of 2. Left - {df2_tickers_left}"
        )
    
class TestMetricsClass(unittest.TestCase):
    
    def setUp(self):
        df: DataFrame = DataFrame(
            data=[
                [22.7, 20.3],
                [18.4, 17.1],
                [29.1, 26.4],
                [11.6, 10.9],
                [26.3, 23.7],
                [13.2, 12.1],
                [17.8, 15.4],
                [25.5, 22.8],
                [19.9, 18.3],
                [27.4, 24.6],
                [10.8, 10.4],
                [23.3, 20.2],
                [15.6, 14.3],
                [28.9, 26.0],
                [21.2, 19.1],
                [12.5, 11.7],
                [24.0, 21.3],
                [16.7, 15.0],
                [14.1, 13.6],
                [20.6, 18.8],
                [29.8, 27.1],
                [10.1, 10.0],
                [30.0, 28.2],
                [11.3, 10.9],
                [13.9, 12.7],
                [17.2, 15.9]
            ],
                        columns=["close_price", "market_price"]
        )
        calculate_rs: Callable[[float, float], float] = MetricsCalculator().rs
        df["rs"] = calculate_rs(
            stock_price=df["close_price"],
            market_price=df["market_price"]
        )
        self.df = df
    
    def test_rs_ma(self):
        calculate_rs_ma: Callable[[DataFrame], DataFrame] = MetricsCalculator().rs_ma_on_data
        df: DataFrame = calculate_rs_ma(stock_data=self.df, ma_window=2)
        
        row_1_ma = df.loc[0, "rs_ma"]
        row_2_ma = df.loc[1, "rs_ma"]
        self.assertTrue(
            expr=pd.isna(row_1_ma),
            msg="The first row is not NaN value."
        )
        self.assertEqual(
            first=type(row_2_ma),
            second=np.float64,
            msg=f"Type of the second row is not float, but {type(row_2_ma)}"
        )
        
        
        
        
    
if __name__ == "__main__":
    unittest.main()