from roboadviosr.optimizer import PortfolioOptimizer
from roboadviosr.rebalancer import RebalancingSimulator
import pandas as pd

df = pd.read_csv("universe.csv")
assets = df["ISIN"].to_list()[:-1]

optimizer = PortfolioOptimizer(assets)
rebalancer = RebalancingSimulator(optimizer, back_test=True)
rebalancer.run_simulation()
