from roboadvisor.optimizer import PortfolioOptimizer
from roboadvisor.rebalancer import RebalancingSimulator
import pandas as pd

df = pd.read_csv("universe.csv")
assets = df["ISIN"].to_list()[:-1]

# risk tolerance option
# 4: 적극투자형, 3: 위험중립형, 2: 안전추구형

optimizer = PortfolioOptimizer(assets, risk_tolerance=4)
rebalancer = RebalancingSimulator(
    optimizer, back_test=True, starting_cash=5000000)

rebalancer.run_simulation()
