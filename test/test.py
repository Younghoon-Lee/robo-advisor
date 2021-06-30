import pandas as pd
from pypfopt import objective_functions, risk_models
from pypfopt import expected_returns
from pypfopt.efficient_frontier import EfficientFrontier
import os
import sys

if __name__ == '__main__':
    sys.path.append(os.path.dirname(
        os.path.abspath(os.path.dirname(__file__))))
    from src.stock_data_collector import StockDataCollector

# Test Pypfopt module with your stock data
