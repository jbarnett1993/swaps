import pandas as pd
import datetime as dt
from pandas.core.arrays.datetimelike import DatelikeOps
from rateslib import *
from tia.bbg import LocalTerminal
from dateutil.relativedelta import relativedelta

sids = {'eur': 514, 'gbp': 141, 'usd': 490}

curves = []
for key, value in sids.items():
    print(str(value).zfill(4))
    curve = 'YCSW' + str(value).zfill(4) + ' Index'
    curves.append(curve)


def get_eom_dates(start_date, end_date, calendar):
    dates = []
    current_date = start_date
    while current_date <= end_date:
        eom_date = add_tenor(current_date, "1M", "F", calendar, 1)
        if eom_date > end_date:
            break
        dates.append(eom_date)
        current_date = eom_date
    return dates

dates = get_eom_dates(dt.datetime.today() - relativedelta(years=15), dt.datetime.today(), 'bus')

# Create a dictionary to store the data
data = {}

for curve in curves:
    for date in dates:
        curve_id = curve
        resp = LocalTerminal.get_reference_data(curve_id, 'CURVE_TENOR_RATES', CURVE_DATE=date.strftime('%Y%m%d'))
        df = resp.as_frame()
        # Store the data in the dictionary with keys as (curve, date)
        data[(curve, date)] = df

# Convert the dictionary to a multi-index DataFrame for better usability
multi_index_df = pd.concat(data.values(), keys=data.keys())

# Reset index to have a flat DataFrame if needed
multi_index_df = multi_index_df.reset_index(level=0, drop=True).reset_index()
multi_index_df.columns = ['Curve', 'Date'] + list(multi_index_df.columns[2:])

# Display the resulting DataFrame
print(multi_index_df)