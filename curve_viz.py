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

dates = get_eom_dates(dt.today() - relativedelta(years=15), dt.today(), 'bus')

#ADJUST THIS CODE SO THAT IT LOOPS OVER ALL THE CURVES AND DATES
resp = LocalTerminal.get_reference_data(curve_id, 'CURVE_TENOR_RATES', CURVE_DATE=self.date.strftime('%Y%m%d'))
df = resp.as_frame()

