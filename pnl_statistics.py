import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Load the data
df = pd.read_csv('eur_gbp_usd_swaps_strat.csv')
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

df_eur['cumulative_pnl_bps'] = df_eur['pnl_bps'].cumsum()
df_gbp['cumulative_pnl_bps'] = df_gbp['pnl_bps'].cumsum()
df_usd['cumulative_pnl_bps'] = df_usd['pnl_bps'].cumsum()

# Plotting
with PdfPages('cumulative_pnl_bps.pdf') as pdf:
    # Combined cumulative PnL in basis points
    plt.figure(figsize=(10, 6))
    plt.plot(df['close_date'], df['cumulative_pnl_bps'], label='Combined')
    plt.title('Cumulative PnL in Basis Points - Combined')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL (bps)')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # EUR cumulative PnL in basis points
    plt.figure(figsize=(10, 6))
    plt.plot(df_eur['close_date'], df_eur['cumulative_pnl_bps'], label='EUR', color='blue')
    plt.title('Cumulative PnL in Basis Points - EUR')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL (bps)')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # GBP cumulative PnL in basis points
    plt.figure(figsize=(10, 6))
    plt.plot(df_gbp['close_date'], df_gbp['cumulative_pnl_bps'], label='GBP', color='green')
    plt.title('Cumulative PnL in Basis Points - GBP')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL (bps)')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # USD cumulative PnL in basis points
    plt.figure(figsize=(10, 6))
    plt.plot(df_usd['close_date'], df_usd['cumulative_pnl_bps'], label='USD', color='red')
    plt.title('Cumulative PnL in Basis Points - USD')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL (bps)')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()