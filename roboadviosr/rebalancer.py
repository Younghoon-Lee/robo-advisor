import numpy as np
import matplotlib.pyplot as plt
import time
import statistics
import pandas as pd
from pandas_datareader import data as web
from datetime import datetime, timedelta
import math
from pykrx import stock


class RebalancingSimulator:

    def __init__(self, p, frac_units=False, starting_cash=700000, trade_cost=0.001, max_thresh=1.1, min_thresh=0.9, back_test=False):

        self.thresh_high = max_thresh
        self.thresh_low = min_thresh
        self.trade_cost = trade_cost
        self.optimal_portfolio = p
        self.frac_units = frac_units
        self.starting_portfolio_value = starting_cash
        self.back_test = back_test
        self.data_prep()
        self.initialize_portfolio()

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
                datetime.today()-timedelta(weeks=52)).strftime("%Y%m%d")
            stock_end_date = datetime.today().strftime("%Y%m%d")
            count = 0
            for asset in asset_list:
                if (count == 0):
                    df = stock.get_etf_ohlcv_by_date(stock_start_date, stock_end_date, asset)[
                        '종가']
                    df = df.to_frame()
                    count += 1
                else:
                    temp = stock.get_etf_ohlcv_by_date(stock_start_date, stock_end_date, asset)[
                        '종가']
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
                cash_used = num_units*start_price*(1+trade_cost)
                self.starting_residual_cash = self.starting_residual_cash-cash_used
                self.starting_residual_cash = math.floor(
                    self.starting_residual_cash*1000)/1000

            portfolio_init.append((starting_vals[i][0], num_units))

        self.starting_unit_holdings = [x[1] for x in portfolio_init]
        self.initialize_portfolio_ = portfolio_init
        return

    def run_simulation(self, plot=False):

        if self.back_test == False:
            print('')
            print("please set back_test = True")
            return
        start = time.time()
        self.total_trades = 0
        portfolio_values = []
        weight_history = []
        unit_history = []
        cash_history = []
        trade_history = []

        price_simulation = None
        self.current_unit_holdings = self.starting_unit_holdings
        self.sim_cash_balance = self.starting_residual_cash
        df = self.back_test_stock_data

        for i in range(1, len(df)):

            self.current_unit_prices = df.iloc[i].tolist()
            self.current_trade_day = df.iloc[i].name
            port_val, new_weights, weight_diffs, new_target_vals, unit_holdings, trade_count = self.get_portfolio_values()

            print("{} 포트폴리오 평가 금액: {}".format(
                self.current_trade_day, port_val))
            print("{} 포트폴리오 자산 비중 현황: {}".format(
                self.current_trade_day, list(zip(self.asset_list, new_weights))))

            portfolio_values.append(port_val)
            weight_history.append(new_weights)
            unit_history.append(unit_holdings)
            cash_history.append(self.sim_cash_balance)
            trade_history.append(trade_count)

        self.sim_port_vals = portfolio_values
        self.sim_weight_vals = weight_history
        self.sim_holding_history = unit_history
        self.sim_cash_history = cash_history
        self.sim_trade_history = trade_history

        if plot == True:
            plt.figure(figsize=(12, 4))
            plt.title('Simulated Portfolio Value')
            plt.plt(self.sim_port_vals)
            plt.show()

            plt.figure(figsize=(12, 4))
            plt.title('Simulation Cash Level')
            plt.plot(self.sim_cash_history)
            plt.sho()

            plt.figure(figsize=(12, 4))
            plt.title('Asset Weight History')
            for i in range(len(self.asset_list)):
                trace = [x[i] for x in self.sim_weight_vals]
                plt.plot(trace, labe=self.asset_list[i])
            plt.legend()
            plt.sho()

        self.total_trades = sum(self.sim_trade_history)

        print('')
        print('')
        print('SIMULATION REPORT')
        print('-----------------')
        print('Rebalancing simulation finished in: %.2f seconds' %
              (time.time()-start))
        print('Total number of trades executed: ', self.total_trades)
        print('Maximum cash balance: ', round(max(self.sim_cash_history), 2))
        print('Minimum cash balance: ', round(min(self.sim_cash_history), 2))
        print('Average cash balance: ', round(
            sum(self.sim_cash_history)/len(self.sim_cash_history), 2))
        print("Fractional Units allowed? {}".format(str(self.frac_units)))
        print('')

        for i in range(len(self.asset_list)):
            weight_history = [x[i] for x in self.sim_weight_vals]
            asset = self.asset_list[i]
            print('Weight mtrics for: {}'.format(asset))
            print('-------------------------')
            print('  Target portfolio weight: {}'.format(
                self.target_weights[i]))
            print('  Standarad deviation of {} portfolio weight: {}'.format(
                asset, round(statistics.stdev(weight_history), 4)))
            print('  Maximum weight reached for {}: {}'.format(
                asset, round(max(weight_history), 4)))
            print('  Minimum weight reached for {}: {}'.format(
                asset, round(min(weight_history), 4)))
            print('  Average of {} portforlio weight: {}'.format(
                asset, round(statistics.mean(weight_history), 4)))
            print('')

        return

    def get_portfolio_values(self):

        unit_holdings = self.current_unit_holdings
        unit_prices = self.current_unit_prices
        frac_units = self.frac_units
        target_weights = self.target_weights
        trade_cost = self.trade_cost
        regular_rebalancing_day = ['2021-05-13']

        port_val = sum(x * y for x, y in zip(unit_holdings,
                       unit_prices)) + self.sim_cash_balance
        new_weights = [(x*y)/port_val for x,
                       y in zip(unit_holdings, unit_prices)]
        weight_diffs = [(x/y) for x, y in zip(new_weights, target_weights)]
        new_target_vals = [x*port_val for x in target_weights]

        thresh_high = self.thresh_high
        thresh_low = self.thresh_low
        trade_count = 0

        if self.current_trade_day in regular_rebalancing_day:

            self.before_weights = new_weights
            print("{} 정기 리밸런싱".format(self.current_trade_day))

            # selling
            for i in range(len(new_weights)):

                if target_weights[i] != new_weights[i] and new_weights[i] > target_weights[i]:

                    target_sell = (
                        unit_prices[i]*unit_holdings[i]) - new_target_vals

                    if frac_units == False:

                        if ((target_sell)//unit_prices[i]) >= 1:
                            allowable_units = (target_sell//unit_prices[i])
                            unit_holdings[i] = unit_holdings[i] - \
                                allowable_units
                            self.sim_cash_balance = self.sim_cash_balance + \
                                (allowable_units*unit_prices[i]*(1-trade_cost))
                            trade_count += 1
                    else:
                        pass

            # buying
            for i in range(len(new_weights)):

                if target_weights[i] != new_weights[i] and new_weights < target_weights[i]:

                    target_buy = new_target_vals[i] - \
                        (unit_prices * unit_holdings[i])

                    if frac_units == False:

                        if self.sim_cash_balance >= (target_buy * (1 + trade_cost)):
                            allowable_units = target_buy//(
                                unit_prices[i] * (1 + trade_cost))
                            unit_holdings[i] = unit_holdings[i] + \
                                allowable_units
                            self.sim_cash_balance = self.sim_cash_balance - \
                                allowable_units*unit_prices[i]*(1+trade_cost)
                            trade_count += 1
                    else:
                        pass

        self.current_unit_holdings = unit_holdings

        return port_val, new_weights, weight_diffs, new_target_vals, unit_holdings, trade_count


if __name__ == "__main__":
    from optimizer import PortfolioOptimizer
    assets = ['252670.KS', '091220.KS', '114800.KS', '122630.KS', '251340.KS',
              '233740.KS', '252710.KS', '214980.KS']
    test = PortfolioOptimizer(assets)
    test.fetch_data()
    test.get_optimal_portfolio()
    rebalancer = RebalancingSimulator(test, back_test=True)
    rebalancer.data_prep()
    rebalancer.initialize_portfolio()
    rebalancer.run_simulation()
