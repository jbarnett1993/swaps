import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Load the data
df = pd.read_csv('master_txs.csv')
df.sort_values(by='close_date', inplace=True)

# Filter out rows with NaN in 'pnl'
df = df.dropna(subset=['pnl'])

# Convert PnL to basis points
fund_size = 50000000  # 50 million
bps_conversion_factor = fund_size / 10000  # Basis point value
df['pnl_bps'] = df['pnl'] / bps_conversion_factor

# Calculate cumulative PnL in basis points for each currency separately and combined
df['cumulative_pnl_bps'] = df['pnl_bps'].cumsum()
df['close_date'] = pd.to_datetime(df['close_date'])

# Separate dataframes for each currency
df_eur = df[df['ccy'] == 'eur'].copy()
df_gbp = df[df['ccy'] == 'gbp'].copy()
df_usd = df[df['ccy'] == 'usd'].copy()

# Calculate monthly returns
monthly_rets_eur = df_eur.groupby('close_date').sum('pnl_bps')['pnl_bps'] / 100
monthly_rets_gbp = df_gbp.groupby('close_date').sum('pnl_bps')['pnl_bps'] / 100 
monthly_rets_usd = df_usd.groupby('close_date').sum('pnl_bps')['pnl_bps'] / 100

print(monthly_rets_eur)
print(monthly_rets_gbp)
print(monthly_rets_usd)

# Assume risk-free rate is 0 for simplicity
risk_free_rate = 0.05
risk_free_rate = (1+risk_free_rate) ** (1/12) -1 

# Calculate Sharpe Ratio for monthly data
def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    excess_returns = returns - risk_free_rate
    return np.mean(excess_returns) / np.std(excess_returns)

sharpe_eur = calculate_sharpe_ratio(monthly_rets_eur)
sharpe_gbp = calculate_sharpe_ratio(monthly_rets_gbp)
sharpe_usd = calculate_sharpe_ratio(monthly_rets_usd)

print(sharpe_eur)
print(sharpe_gbp)
print(sharpe_gbp)

exit()

# Calculate Information Ratio for monthly data
def calculate_information_ratio(returns, benchmark_returns):
    excess_returns = returns - benchmark_returns
    return np.mean(excess_returns) / np.std(excess_returns)

# For simplicity, assume benchmark is 0 return
benchmark_return = 0.0
info_ratio_eur = calculate_information_ratio(monthly_rets_eur / 100, benchmark_return)
info_ratio_gbp = calculate_information_ratio(monthly_rets_gbp / 100, benchmark_return)
info_ratio_usd = calculate_information_ratio(monthly_rets_usd / 100, benchmark_return)

# Print Sharpe and Information Ratios
print(f'Sharpe Ratio (EUR): {sharpe_eur}')
print(f'Sharpe Ratio (GBP): {sharpe_gbp}')
print(f'Sharpe Ratio (USD): {sharpe_usd}')
print(f'Information Ratio (EUR): {info_ratio_eur}')
print(f'Information Ratio (GBP): {info_ratio_gbp}')
print(f'Information Ratio (USD): {info_ratio_usd}')

# Plotting
with PdfPages('master_pnl_stats.pdf') as pdf:
    # EUR cumulative PnL in basis points
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_rets_eur.index, monthly_rets_eur.cumsum(), label='EUR', color='blue')
    plt.title(f'Cumulative PnL in Basis Points - EUR\nSharpe Ratio: {sharpe_eur:.2f}, Information Ratio: {info_ratio_eur:.2f}')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL (bps)')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # GBP cumulative PnL in basis points
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_rets_gbp.index, monthly_rets_gbp.cumsum(), label='GBP', color='green')
    plt.title(f'Cumulative PnL in Basis Points - GBP\nSharpe Ratio: {sharpe_gbp:.2f}, Information Ratio: {info_ratio_gbp:.2f}')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL (bps)')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # USD cumulative PnL in basis points
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_rets_usd.index, monthly_rets_usd.cumsum(), label='USD', color='red')
    plt.title(f'Cumulative PnL in Basis Points - USD\nSharpe Ratio: {sharpe_usd:.2f}, Information Ratio: {info_ratio_usd:.2f}')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL (bps)')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close() 

df_eur.to_csv('df_eur.csv')