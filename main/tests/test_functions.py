import unittest
from robot.functions import get_page_tables
import pandas as pd

class TestGetPageTablesFunction(unittest.TestCase):
    
    def test_get_page_tables(self):
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = get_page_tables(url=url)
        
        self.assertIs(
            expr1=type(tables),
            expr2=list,
            msg="The result should be a list of DataFrames."
        )
        self.assertGreater(
            a=len(tables),
            b=0,
            msg="No tables were extracted from the page."
        )
        self.assertIs(
            expr1=type(tables[0]),
            expr2=pd.DataFrame,
            msg="The items in the list should be DataFrames."
        )
        
if __name__ == "__main__":
    unittest.main()