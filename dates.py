from dateutil.relativedelta import relativedelta
from rateslib import * 
from datetime import datetime

from sympy import N

today = dt.today()
date = today - relativedelta(years=1)

dates = []
while date < today:
    n = 1
    date = add_tenor(date,f"{n}M","MF","tgt",1)
    dates.append(date)
    n += 1

print(dates[:-1])
