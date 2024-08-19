import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

df = pd.read_csv('rec3pay3_txs.csv')
df.sort_values(by='close_date', inplace=True)
input(df)

df = df.dropna(subset=['pnl'])


fund_size = 50000000  # 50 million
bps_conversion_factor = fund_size / 10000  
df['pnl_bps'] = df['pnl'] / bps_conversion_factor


df['cumulative_pnl_bps'] = df['pnl_bps'].cumsum()
df['close_date'] = pd.to_datetime(df['close_date'])


df_eur = df[df['ccy'] == 'eur'].copy()
df_gbp = df[df['ccy'] == 'gbp'].copy()
df_usd = df[df['ccy'] == 'usd'].copy()


monthly_rets_eur = df_eur.groupby('close_date').sum('pnl_bps')['pnl_bps'] / 100
monthly_rets_gbp = df_gbp.groupby('close_date').sum('pnl_bps')['pnl_bps'] / 100 
monthly_rets_usd = df_usd.groupby('close_date').sum('pnl_bps')['pnl_bps'] / 100

# print(monthly_rets_eur)
# print(monthly_rets_gbp)
# print(monthly_rets_usd)




def calculate_information_ratio(returns, benchmark_returns):
    excess_returns = returns - benchmark_returns
    return np.mean(excess_returns) / np.std(excess_returns)


benchmark_return = 0.0
info_ratio_eur = calculate_information_ratio(monthly_rets_eur / 100, benchmark_return)
info_ratio_gbp = calculate_information_ratio(monthly_rets_gbp / 100, benchmark_return)
info_ratio_usd = calculate_information_ratio(monthly_rets_usd / 100, benchmark_return)


print(f'Information Ratio (EUR): {info_ratio_eur}')
print(f'Information Ratio (GBP): {info_ratio_gbp}')
print(f'Information Ratio (USD): {info_ratio_usd}')

with PdfPages('test.pdf') as pdf:

    plt.figure(figsize=(10, 6))
    plt.plot(monthly_rets_eur.index, monthly_rets_eur.cumsum(), label='EUR', color='blue')
    plt.title(f'Cumulative PnL - EUR\n Information Ratio: {info_ratio_eur:.3f}')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL (%)')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(monthly_rets_gbp.index, monthly_rets_gbp.cumsum(), label='GBP', color='green')
    plt.title(f'Cumulative PnL GBP\n Information Ratio: {info_ratio_gbp:.3f}')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL (%)')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()


    plt.figure(figsize=(10, 6))
    plt.plot(monthly_rets_usd.index, monthly_rets_usd.cumsum(), label='USD', color='red')
    plt.title(f'Cumulative PnL USD\n Information Ratio: {info_ratio_usd:.3f}')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL (bps)')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close() 
