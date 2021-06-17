import numpy as np
import matplotlib.pyplot as plt
import time
import statistics
import pandas as pd
from pandas_datareader import data as web
from datetime import datetime, timedelta
import math


class RebalancingSimulator:

    def __init__(self, p, frac_units=False, starting_cash=700000, trade_cost=0.001, max_thresh=1.1, min_thresh=0.9, back_test=False):

        self.thresh_high = max_thresh
        self.thresh_low = min_thresh
        self.trade_cost = trade_cost
        self.optimal_portfolio = p
        self.frac_units = frac_units
        self.starting_portfolio_value = starting_cash
        self.back_test = back_test

    def data_prep(self):

        sharpe_port = self.optimal_portfolio.best_sharpe_portfolio
        back_test = self.back_test

        optimal_port = sharpe_port[1]
        optimal_port = list(filter(lambda a: a[1] > 0.001, optimal_port))
        asset_list = [x[0] for x in optimal_port]
        weights = [x[1] for x in optimal_port]

        if back_test == False:
            df = self.optimal_portfolio.raw_assets_data.copy()
            df = df[asset_list]
            latest = df.tail(1)
            starting_vals = []
            count = 0

            for asset in asset_list:
                asset_ret = np.log(df[asset]/df[asset].shift(1)).mean()
                asset_vol = np.log(df[asset]/df[asset].shift(1)).std()
                starting_vals.append([
                    asset,
                    latest[asset].values[0],
                    round(asset_ret, 5),
                    round(asset_vol, 5),
                    weights[count]
                ])
                count += 1

            self.starting_vals = starting_vals
            self.target_weights = weights
            self.asset_list = asset_list
            print('Target weights: ', list(
                zip(self.asset_list, self.target_weights)))
        else:
            df = pd.DataFrame()
            stock_start_date = (
                datetime.today()-timedelta(weeks=52)).strftime("%Y-%m-%d")
            count = 0
            for asset in asset_list:
                if (count == 0):
                    df = web.DataReader(asset, data_source='yahoo', start=stock_start_date)[
                        'Adj Close']
                    df = df.to_frame()
                    count += 1
                else:
                    temp = web.DataReader(asset, data_source='yahoo', start=stock_start_date)[
                        'Adj Close']
                    df = pd.merge(df, temp, how='outer',
                                  left_index=True, right_index=True)

            df.columns = asset_list
            self.back_test_stock_data = df.copy()
            latest = df.head(1)
            starting_vals = []
            count = 0

            for asset in asset_list:
                starting_vals.append([
                    asset,
                    latest[asset].values[0],
                    'return_mean',
                    'std',
                    weights[count]
                ])
                count += 1

            self.starting_vals = starting_vals
            self.target_weights = weights
            self.asset_list = asset_list
            print("Target weights: ", list(
                zip(self.asset_list, self.target_weights)))

        return

    def initialize_portfolio(self):

        starting_vals = self.starting_vals
        trade_cost = self.trade_cost
        portfolio_init = []
        self.starting_residual_cash = self.starting_portfolio_value

        for i in range(len(starting_vals)):

            allocated_capital = round(
                starting_vals[i][4]*self.starting_portfolio_value, 4)
            start_price = starting_vals[i][1]

            if (self.frac_units == True):
                pass
            else:
                num_units = allocated_capital//(start_price*(1+trade_cost))
                cash_used = num_units*start_price*trade_cost
                self.starting_residual_cash = self.starting_residual_cash-cash_used
                self.starting_residual_cash = round(
                    self.starting_residual_cash, 4)

            portfolio_init.append((starting_vals[i][0], num_units))

        self.starting_unit_holdings = [x[1] for x in portfolio_init]
        self.initialize_portfolio_ = portfolio_init
        return


if __name__ == "__main__":
    from optimizer import PortfolioOptimizer
    assets = ['252670.KS', '091220.KS', '114800.KS', '122630.KS', '251340.KS',
              '233740.KS', '252710.KS', '214980.KS']
    test = PortfolioOptimizer(assets)
    test.fetch_data()
    test.get_optimal_portfolio()
    rebalancer = RebalancingSimulator(test, back_test=False)
    rebalancer.data_prep()
    rebalancer.initialize_portfolio()
