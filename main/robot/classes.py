import yfinance as yf
import pandas as pd
from pandas import DataFrame
from datetime import datetime


class Yfinance:
    """
    Class implements yahoo finance manipulation.
    """
    
    @staticmethod
    def get_price_data(
        tickers: str | list[str],
        period: tuple[datetime]
    ) -> DataFrame:
        """
        Method downloads price data from yahoo finance.
        """
        price_data: DataFrame = yf.download(
            tickers=tickers,
            start=period[0],
            end=period[1]
        )
        return price_data


class Metrics:
    """
    Class implements metrics that involved in analysis.
    """
    
    @staticmethod
    def rs(
        stock_price: float,
        market_price: float
    ) -> float:
        """
        Method calculates a relative strength.
        """
        rs: float = round(
            number=(stock_price / market_price),
            ndigits=2
        )
        return rs
    
    @staticmethod
    def rs_ma(
        stocks_data: DataFrame,
        ma_window: int
    ) -> DataFrame:
        """
        Method calculates a moving average of a relative strength.
        Moving average can be calculated for period not surpassing 21 days (one month).
        NB! Dataframe must contain a "rs" column
        """
        # Tickers are top lvl cols.
        tickers = stocks_data.columns.get_level_values(0).unique()
        for ticker in tickers:
            stocks_data[ticker, "rs_ma"] = stocks_data[ticker, "rs"].rolling(window=ma_window).mean()
        return stocks_data
        


class DataFilter:
    """
    Class contains filters for stocks price data. 
    """

    @staticmethod
    def has_rs_grown(stocks_data: DataFrame) -> DataFrame:
        """
        Methods checks whether a relative strength coefficient has grown and
        filters stocks.
        NB! Tickers must be top level columns.
        Data must contain the "rs" column.
        """
        tickers = stocks_data.columns.get_level_values(0).unique()
        for ticker in tickers:
            rs_period_start: float = stocks_data.loc[0, (ticker, "rs")]
            rs_period_end: float = stocks_data.loc[len(stocks_data) - 1, (ticker, "rs")]
                    

            stocks_data = stocks_data.drop(
                columns=[ticker],
                level=0
            ) if not rs_period_end > rs_period_start else stocks_data
        
        return stocks_data

    @staticmethod
    def has_rs_crossed_ma(
        stocks_data: DataFrame,
        days_rs_holds_above_ma: int
    ) -> DataFrame:
        """
        Method checks if a relative strenght has crossed a moving average while growing and filters data.
        The parameter days_rs_holds_above_ma means days, that stock has held its relative strength above ma.
        NB! Data must contain the columns "rs" and "ma".
        """
        # The main idea of the algorithm is it starts from the end checking if rs is higher than ma.
        # If a rs has been held above ma a defined amount of days a stock remains to a dataframe.
        
        stocks_tickers: list[str] = list(stocks_data.columns.get_level_values(0).unique())
        
        for ticker in stocks_tickers:
            row_nr: int = len(stocks_data) - 1
            count_days: int = 0
            
            postive_result: bool = False
            while row_nr != -1:
                rs: float = stocks_data.loc[row_nr, (ticker, "rs")]
                ma: float = stocks_data.loc[row_nr, (ticker, "rs_ma")]
                
                if rs < ma or pd.isna(ma):
                    break
                elif rs > ma:
                    count_days += 1

                row_nr -= 1
            
            if count_days >= days_rs_holds_above_ma:
                postive_result = True

            stocks_data = stocks_data.drop(
                columns=[ticker],
                level=0
            ) if not postive_result else stocks_data
 
        return stocks_data

    
class WikiTickersExtractor:
    
    """
    REDUDANT
    """
    
    def __init__(
        self,
        index_tickers_pages: dict[str, list[str, int]] # index: [wiki web page, table n]
    ):
        self.index_tickers_pages = index_tickers_pages
        
    def extract_table(
        self,
        index_name: str,
        table_nr: int
    ) -> DataFrame:
        """
        Method extracts index table from Wiki.
        """
        if index_name not in self.index_tickers_pages.keys:
            raise KeyError(f"Index {index_name} is not valid.")
        
        data: DataFrame = pd.read_html(
            self.index_tickers_pages[index_name][0]
        )[
            self.index_tickers_pages[index_name][1]
        ]
    