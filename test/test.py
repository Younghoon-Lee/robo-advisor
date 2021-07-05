import pandas as pd
from pandas.tseries.offsets import LastWeekOfMonth
from pypfopt import objective_functions, risk_models
from pypfopt import expected_returns
from pypfopt.efficient_frontier import EfficientFrontier
import os
import sys
from datetime import datetime, timedelta

if __name__ == '__main__':
    dirname = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.dirname(
        dirname))

    from src.stock_data_collector import StockDataCollector
    universe = pd.read_csv(os.path.dirname(dirname)+"/universe.csv")
    assets = universe['ISIN'].to_list()[:-1]
    stockCollector, df, column_names = StockDataCollector(), pd.DataFrame(), []
    stock_start_date = (
        datetime.today()-timedelta(weeks=52)).strftime("%Y-%m-%d")
    stock_end_date = datetime.today().strftime("%Y-%m-%d")
    count = 0
    for asset in assets:
        if count == 0:
            df = stockCollector.get_historical_data(
                stock_start_date, stock_end_date, asset)['NAV']
            df = df.to_frame()
            column_names.append(asset)
            count += 1
        else:
            temp = stockCollector.get_historical_data(
                stock_start_date, stock_end_date, asset)['NAV']
            column_names.append(asset)
            df = pd.merge(df, temp, how='outer',
                          left_index=True, right_index=True)
    df.columns = column_names
    return_matrix = expected_returns.mean_historical_return(df)
    print(return_matrix)
    cov_matrix = risk_models.CovarianceShrinkage(df).ledoit_wolf()
    ef = EfficientFrontier(return_matrix, cov_matrix, weight_bounds=(0, 0.5))
    ef.add_objective(objective_functions.L2_reg, gamma=1)
    weights = ef.efficient_return(0.1)
    weights = ef.clean_weights()
    print(weights)


# Test Pypfopt module with your stock data
