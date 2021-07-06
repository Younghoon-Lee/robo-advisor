import os
from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta


class StockDataCollector:

    def __init__(self):
        DATA_FOLDER = 'data'
        file_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(file_dir, DATA_FOLDER)
        self.data_folder = file_path

    def update_historical_data(self, start_date, end_date, tickers):

        for ticker in tickers:
            df = stock.get_etf_ohlcv_by_date(start_date, end_date, ticker)
            self._save_df_to_csv(df, ticker)
            print("{} successfully loaded".format(ticker))

    def get_historical_data(self, start_date, end_date, ticker):

        df = self._load_df_from_csv(ticker)
        df = df.loc[start_date:end_date]
        return df

    def _save_df_to_csv(self, dataframe, file_name):
        file_path = os.path.join(self.data_folder, file_name + '.csv')
        dataframe.to_csv(file_path, na_rep='NaN')

    def _load_df_from_csv(self, file_name):
        file_path = os.path.join(self.data_folder, file_name + '.csv')
        df = pd.read_csv(file_path, index_col=0)
        return df


if __name__ == '__main__':
    dirname = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    df = pd.read_csv(dirname+'/universe.csv')
    tickers = df["ISIN"].to_list()[:-1]
    start_date = (datetime.today()-timedelta(weeks=78)).strftime("%Y%m%d")
    end_date = datetime.today().strftime("%Y%m%d")
    StockDataCollector().update_historical_data(
        start_date, end_date, tickers)
