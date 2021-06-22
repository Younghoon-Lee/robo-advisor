import numpy as np
import pandas as pd
import time
from itertools import combinations
from operator import itemgetter
from pykrx import stock
from pandas_datareader import data as web
from pypfopt import objective_functions, risk_models
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
        self.fetch_data()
        self.get_optimal_portfolio()

    def fetch_data(self):

        start = time.time()
        count = 0

        self.assets_errors = []
        self.cov_matrix_results = []
        self.return_matrix_results = []
        self.asset_combo_list = []

        stock_start_date = (
            datetime.today()-timedelta(weeks=52)).strftime("%Y%m%d")
        stock_end_date = datetime.today().strftime("%Y%m%d")
        df = pd.DataFrame()
        column_names = []

        for asset in self.asset_basket:
            if (count == 0):
                try:
                    df = stock.get_etf_ohlcv_by_date(stock_start_date, stock_end_date, asset)[
                        'NAV']
                    df = df.to_frame()
                    column_names.append(asset)
                    count += 1
                except Exception as e:
                    print('fetching data error : {}'.format(asset), e)
                    self.assets_errors.append(asset)
            else:
                try:
                    temp = stock.get_etf_ohlcv_by_date(stock_start_date, stock_end_date, asset)[
                        'NAV']
                    column_names.append(asset)
                    df = pd.merge(df, temp, how='outer',
                                  left_index=True, right_index=True)
                except Exception as e:
                    print('fetching data error : {}'.format(asset), e)
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
            cov_matrix = risk_models.CovarianceShrinkage(
                filtered_df).ledoit_wolf()
            self.num_assets = len(assets)
            self.sim_packages.append([assets, cov_matrix, return_matrix])

        print('Omitted assets: {}'.format(self.assets_errors))
        print("---")
        print("Time to fetch data: %.2f seconds" % (time.time() - start))

    def get_optimal_portfolio(self):

        start = time.time()
        self.portfolio_list = []
        sim_packages = self.sim_packages.copy()
        self.combos_error = []

        # create sector mapper
        universe = pd.read_csv(
            "/Users/tickle/tickle/robo-advisor/universe.csv")
        sector_mapper = {}
        for asset in self.asset_basket:
            sector_mapper[asset] = universe[universe["ISIN"]
                                            == asset]["위험자산여부"].values[0]
        sector_lower = {"Y": 0.0, "N": 0.0}
        sector_upper = {"Y": 0.6, "N": 0.4}

        for _ in range(len(sim_packages)):

            sim = sim_packages.pop()
            return_model = sim[2]
            risk_model = sim[1]
            assets = sim[0]
            ef = EfficientFrontier(
                return_model, risk_model, weight_bounds=(0, 1))
            ef.add_objective(objective_functions.L2_reg, gamma=1)
            ef.add_sector_constraints(
                sector_mapper=sector_mapper, sector_lower=sector_lower, sector_upper=sector_upper)
            try:
                port = ef.efficient_return(0.2)
                port = ef.clean_weights()
                weights = []
                for i in range(len(port)):
                    weights.append(round(port[assets[i]], 4))
                markowitz_portfolio = list(zip(assets, weights))
                portfolio_stats = ef.portfolio_performance()
                self.portfolio_list.append([weights, markowitz_portfolio, round(
                    portfolio_stats[0]*100, 4), round(portfolio_stats[1]*100, 4), round(portfolio_stats[2], 4)])
            except:
                self.combos_error.append(sim)
            self.portfolio_list = sorted(
                self.portfolio_list, key=itemgetter(4), reverse=True)

        self.best_sharpe_portfolio = self.portfolio_list[0]
        temp = self.best_sharpe_portfolio
        print('---')
        print('Time to optimize portfolio: %.2f seconds' %
              (time.time() - start))

        print('-----------------------------------------------')
        print('----- Portfolio Optimized for Sharpe Ratio ----')
        print('-----------------------------------------------')
        print('')
        print(*temp[1], sep='\n')
        print('')
        print('Optimal Portfolio Return: {}%'.format(temp[2]))
        print('Optimal Portfolio Volatility: {}%'.format(temp[3]))
        print('Optimal Portfolio Sharpe Ratio: {}'.format(temp[4]))
        print('')
        print('')


if __name__ == "__main__":
    assets = ['069500', '091170', '130730', '229200', '139270', '305720', '228800', '144600', '102110', '139220', '117700',
              '214980', '130680', '305540', '261220', '139230', '219390', '278540', '292150', '272560', '091180', '228790']
    test = PortfolioOptimizer(assets)
    test.fetch_data()
    test.get_optimal_portfolio()
