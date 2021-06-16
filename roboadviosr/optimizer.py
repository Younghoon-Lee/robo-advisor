import numpy as np
import pandas as pd
import time
from itertools import combinations
from operator import itemgetter
from pandas_datareader import data as web
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.efficient_frontier import EfficientFrontier
from datetime import datetime, timedelta


class PortfolioOptimizer:

    def __init__(self, assets, risk_tolerance=5.0, portfolio_size=5, max_iters=None, print_init=True, max_pos=1.0, min_pos=0.0):

        self.max_pos = max_pos
        self.min_pos = min_pos
        self.print_init = print_init
        self.asset_basket = assets
        self.max_iters = max_iters
        self.portfolio_size = portfolio_size
        self.assets = assets
        self.num_assets = portfolio_size
        self.risk_tolerance = risk_tolerance
        self.sim_iterations = 2500

    def fetch_data(self):

        start = time.time()
        count = 0

        self.assets_errors = []
        self.cov_matrix_results = []
        self.return_matrix_results = []
        self.asset_combo_list = []

        stock_start_date = (
            datetime.today()-timedelta(weeks=78)).strftime("%Y-%m-%d")
        df = pd.DataFrame()
        column_names = []

        for asset in self.asset_basket:
            if (count == 0):
                try:
                    df = web.DataReader(asset, data_source='yahoo', start=stock_start_date)[
                        'Adj Close']
                    df = df.to_frame()
                    column_names.append(asset)
                    count += 1
                except Exception as e:
                    print('fetching data error : ', e)
                    self.assets_errors.append(asset)
            else:
                try:
                    temp = web.DataReader(asset, data_source='yahoo', start=stock_start_date)[
                        'Adj Close']
                    column_names.append(asset)
                    df = pd.merge(df, temp, how='outer',
                                  left_index=True, right_index=True)
                except Exception as e:
                    print('fetching data error : ', e)
                    self.assets_errors.append(asset)

        # df = df.dropna(axis=0)
        df.columns = column_names
        print(df)
        self.raw_assets_data = df.copy()
        self.assets_combos = list(
            [combo for combo in combinations(column_names, self.portfolio_size)])
        print('Number of unique asset combinations: {}'.format(
            len(self.assets_combos)))

        if (self.max_iters == None):
            self.max_iters = len(self.assets_combos)

        elif (len(self.assets_combos) < self.max_iters):
            self.max_iters = len(self.assets_combos)

        print('Analyzing {} of {} asset combinations...'.format(
            self.max_iters, len(self.assets_combos)))

        self.sim_packages = []
        for i in range(self.max_iters):
            assets = list(self.assets_combos[i])
            filtered_df = df[assets].copy()
            return_matrix = expected_returns.mean_historical_return(
                filtered_df)
            cov_matrix = risk_models.CovarianceShrinkage(df).ledoit_wolf()
            self.num_assets = len(assets)
            self.sim_packages.append([assets, cov_matrix, return_matrix])

        print('Omitted assets: {}'.format(self.assets_errors))
        print("---")
        print("Time to fetch data: %.2f seconds" % (time.time() - start))


if __name__ == "__main__":
    assets = ['252670.KS', '091220.KS', '114800.KS', '122630.KS', '251340.KS',
              '233740.KS', '252710.KS', '214980.KS']
    test = PortfolioOptimizer(assets)
    test.fetch_data()
