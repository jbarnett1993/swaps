import pandas as pd
import numpy as np
from tia.bbg import LocalTerminal
import datetime as dt
df = pd.read_csv('eur_gbp_usd_swaps_strat.csv')
df.sort_values(by='close_date',inplace=True)

print(df)

df['cumulative_pnl'] = df['pnl'].cumsum()

print(df)






'''

            date  ccy  term      rate  direction            pnl  close_date  cumulative_pnl
0     2009-08-03  eur  1Y1Y  1.998478         -1  153031.773507  2009-09-01   153031.773507
1084  2009-08-03  gbp  6Y2Y  4.671492          1 -121363.154496  2009-09-01    31668.619011
1085  2009-08-03  gbp  6Y1Y  4.659134          1 -132249.802593  2009-09-01  -100581.183582
1081  2009-08-03  gbp  1Y2Y  3.480402         -1  273107.490513  2009-09-01   172526.306931
1080  2009-08-03  gbp  1Y1Y  2.760334         -1  259279.333160  2009-09-01   431805.640090
...          ...  ...   ...       ...        ...            ...         ...             ...
1075  2024-07-01  eur  6Y1Y  2.696077         -1            NaN  2024-08-01             NaN
1076  2024-07-01  eur  6Y3Y  2.769801         -1            NaN  2024-08-01             NaN
1077  2024-07-01  eur  1Y3Y  2.606411          1            NaN  2024-08-01             NaN
1079  2024-07-01  eur  1Y1Y  2.735405          1            NaN  2024-08-01             NaN
3239  2024-07-01  usd  1Y1Y  4.174796          1            NaN  2024-08-01             NaN




'''


# print(df.head(50))


# currencies = ['EURUSD Curncy', 'GBPUSD Curncy', 'USDCHF Curncy', 'USDSEK Curncy', 'USDNOK Curncy']
# rates = LocalTerminal.get_historical(currencies,'PX_LAST',df['date'][0],dt.datetime.today())
# rates = rates.as_frame()


# print(rates)