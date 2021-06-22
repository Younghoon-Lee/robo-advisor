from pandas_datareader import data as web
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
from pykrx import stock

ticker_list = stock.get_etf_ticker_list("20200603")
dirpath = os.path.dirname(__file__)
test = pd.read_csv(
    "/Users/tickle/tickle/robo-advisor/test/etf.csv", encoding='CP949')
df = test[['종목코드', '종목명', '종가', '거래량']]
df = df.sort_values(by='거래량', ascending=False)
df2 = df[df['종목명'].str.contains('인버스') == False]
df3 = df2[df2['종목명'].str.contains('레버리지') == False]
df3 = df3[df3['거래량'] >= 50000]
print(df3)
df3 = df3['종목코드'].to_list()
df3 = list(map(str, df3))
print(len(df3))
target_etf = []
for i in range(len(df3)):
    if len(df3[i]) == 5:
        df3[i] = "0" + df3[i]
    if df3[i] in ticker_list:
        target_etf.append(df3[i])
print(len(target_etf))
temp = list(map(int, target_etf))
print(df[df['종목코드'].isin(temp)].tail(30))
'''
etf = df3.head(30)
etf = etf['종목코드'].tolist()
etf = list(map(str, etf))
target_etf = []
for i in range(len(etf)):
    if len(etf[i]) == 5:
        etf[i] = '0' + etf[i]
    if etf[i] in ticker_list:
        target_etf.append(etf[i])
print(target_etf)

stock_start_date = (datetime.today()-timedelta(weeks=52)).strftime("%Y%m%d")
stock_end_date = datetime.today().strftime("%Y%m%d")
df = pd.DataFrame()
column_names = []
count = 0


for asset in target_etf:
    if (count == 0):
        try:
            df = stock.get_etf_ohlcv_by_date(stock_start_date, stock_end_date, asset)[
                'NAV']
            df = df.to_frame()
            column_names.append(asset)
            count += 1
        except Exception as e:
            print('fetching data error : ', e)

    else:
        try:
            temp = stock.get_etf_ohlcv_by_date(stock_start_date, stock_end_date, asset)[
                'NAV']
            column_names.append(asset)
            df = pd.merge(df, temp, how='outer',
                          left_index=True, right_index=True)
        except Exception as e:
            print('fetching data error : ', e)


df.columns = column_names
print(df)
'''
