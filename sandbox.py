import pandas as pd
import numpy as np

# Assuming your data is in a CSV or you have it in a DataFrame named `df`
data = {
    'close_date': ['2009-09-01', '2009-10-01', '2009-11-02', '2009-12-01', '2010-01-04', 
                   '2024-03-01', '2024-04-02', '2024-05-01', '2024-06-03', '2024-07-01'],
    'pnl': [76.042377, 53.616778, 23.193911, 112.948106, 26.140612, 
            141.734303, -41.933632, 81.131266, -1.410652, -49.101956]
}
df = pd.DataFrame(data)
df['close_date'] = pd.to_datetime(df['close_date'])
df.set_index('close_date', inplace=True)

# Convert PnL from basis points to decimal form
returns = df['pnl'] / 10000

# Parameters
risk_free_rate = 0.01 / 100  # Example risk-free rate in decimal form (e.g., 1% annualized)
benchmark_return = returns.mean()  # Example benchmark return

# Sharpe Ratio
excess_return = returns - risk_free_rate
sharpe_ratio = excess_return.mean() / excess_return.std()

# Information Ratio
active_return = returns - benchmark_return
information_ratio = active_return.mean() / active_return.std()

print(f"Sharpe Ratio: {sharpe_ratio}")
print(f"Information Ratio: {information_ratio}")