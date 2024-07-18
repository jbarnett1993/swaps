from rateslib import *
import pandas as pd
from tia.bbg import LocalTerminal

today = dt.today()
effective = add_tenor(today,"2b","F",get_calendar('tgt'))
maturity = add_tenor(effective,"1Y","F",get_calendar('tgt'))


iborcurve = '514'


eurcurve_id = 'YCSW' + iborcurve.zfill(4) + ' Index'
eurresp = LocalTerminal.get_reference_data(eurcurve_id,'CURVE_TENOR_RATES')
eurdf = eurresp.as_frame()
eurtenors = eurdf['CURVE_TENOR_RATES'].iloc[0]['Tenor'].to_list()
eurrates = eurdf['CURVE_TENOR_RATES'].iloc[0]['Mid Yield'].to_list()