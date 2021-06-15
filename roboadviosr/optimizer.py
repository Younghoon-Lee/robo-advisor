import numpy as np
import pandas as pd
import time
from itertools import combinations
from operator import itemgetter
import pandas_datareader
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.efficient_frontier import EfficientFrontier
from datetime import datetime, timedelta


class PortfolioOptimizer:

    def __init__(self, assets, risk_tolerance=5.0, portfolio_size=10, max_iters=None, print_init=True, max_pos=1.0, min_pos=0.0):

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
