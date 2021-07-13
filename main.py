from roboadvisor.optimizer import PortfolioOptimizer
from roboadvisor.rebalancer import RebalancingSimulator
import pandas as pd


# 투자 유니버스에서 자산 목록 가져오기
df = pd.read_csv("universe.csv")
assets = df["ISIN"].to_list()[:-1]


# risk tolerance option
# 4: 적극투자형, 3: 위험중립형, 2: 안전추구형

optimizer = PortfolioOptimizer(assets, risk_tolerance=4)
rebalancer = RebalancingSimulator(
    optimizer, back_test=False, starting_cash=500000)

# rebalancer.run_simulation()
