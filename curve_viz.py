import pandas as pd
import datetime as dt
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

dates = get_eom_dates(dt.datetime.today() - relativedelta(years=1), dt.datetime.today(), 'bus')

# Function to batch requests
def batch_requests(curves, dates, batch_size=10):
    for i in range(0, len(curves), batch_size):
        for j in range(0, len(dates), batch_size):
            curve_batch = curves[i:i + batch_size]
            date_batch = dates[j:j + batch_size]
            for curve in curve_batch:
                for date in date_batch:
                    yield curve, date

# Create a dictionary to store the data
data = {}

# Batch the requests
for curve, date in batch_requests(curves, dates, batch_size=5):
    curve_id = curve
    resp = LocalTerminal.get_reference_data(curve_id, 'CURVE_TENOR_RATES', CURVE_DATE=date.strftime('%Y%m%d'))
    df = resp.as_frame()
    tenors = df['CURVE_TENOR_RATES'].iloc[0]['Tenor'].to_list()
    rates = df['CURVE_TENOR_RATES'].iloc[0]['Mid Yield'].to_list()
    df = pd.DataFrame({'Term': tenors, 'Rate': rates})
    print(df)
    # Store the data in the dictionary with keys as (curve, date)
    data[(curve, date)] = df

# Convert the dictionary to a multi-index DataFrame for better usability
multi_index_df = pd.concat(data.values(), keys=data.keys())

# Reset index to have a flat DataFrame if needed
multi_index_df = multi_index_df.reset_index(level=0, drop=True).reset_index()
multi_index_df.columns = ['Curve', 'Date'] + list(multi_index_df.columns[2:])

# Display the resulting DataFrame
print(multi_index_df)