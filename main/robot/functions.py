import pandas as pd
from pandas import DataFrame
import requests
from io import StringIO

def get_page_tables(url: str) -> list[DataFrame]:
    """
    Function extracts all tables from a web page.
    """
    # Headers are necessary for some pages, e.g. wiki to simulate a browser visit.
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    html = response.text

    tables = pd.read_html(StringIO(html))
    
    return tables