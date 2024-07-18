from bdb import effective
from rateslib import *
from tia.bbg import LocalTerminal
import pandas as pd
import datetime


today = dt.today()
effective = add_tenor(today,"2b","MF",get_calendar('tgt'))
maturity = add_tenor(effective,"1Y","MF",get_calendar('tgt'))

print(effective)
print(maturity)
