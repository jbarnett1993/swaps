import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Load the data
df = pd.read_csv('eur_gbp_usd_swaps_strat.csv')
df.sort_values(by='close_date', inplace=True)

# Filter out rows with NaN in 'pnl'
df = df.dropna(subset=['pnl'])

# Calculate cumulative PnL for each currency separately and combined
df['cumulative_pnl'] = df['pnl'].cumsum()
df['close_date'] = pd.to_datetime(df['close_date'])

# Separate dataframes for each currency
df_eur = df[df['ccy'] == 'eur'].copy()
df_gbp = df[df['ccy'] == 'gbp'].copy()
df_usd = df[df['ccy'] == 'usd'].copy()

df_eur['cumulative_pnl'] = df_eur['pnl'].cumsum()
df_gbp['cumulative_pnl'] = df_gbp['pnl'].cumsum()
df_usd['cumulative_pnl'] = df_usd['pnl'].cumsum()

# Plotting
<<<<<<< HEAD
with PdfPages('pnl_stats.pdf') as pdf:
    # Combined cumulative PnL
=======
with PdfPages('cumulative_pnl_bps.pdf') as pdf:
    # Combined cumulative PnL in basis points
>>>>>>> aa48b4e3357220584afa5afb384715ff4cd47b00
    plt.figure(figsize=(10, 6))
    plt.plot(df['close_date'], df['cumulative_pnl'], label='Combined')
    plt.title('Cumulative PnL - Combined')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # EUR cumulative PnL
    plt.figure(figsize=(10, 6))
    plt.plot(df_eur['close_date'], df_eur['cumulative_pnl'], label='EUR', color='blue')
    plt.title('Cumulative PnL - EUR')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # GBP cumulative PnL
    plt.figure(figsize=(10, 6))
    plt.plot(df_gbp['close_date'], df_gbp['cumulative_pnl'], label='GBP', color='green')
    plt.title('Cumulative PnL - GBP')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # USD cumulative PnL
    plt.figure(figsize=(10, 6))
    plt.plot(df_usd['close_date'], df_usd['cumulative_pnl'], label='USD', color='red')
    plt.title('Cumulative PnL - USD')
    plt.xlabel('Close Date')
    plt.ylabel('Cumulative PnL')
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()