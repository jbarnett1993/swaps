import pandas as pd
import datetime as dt
from rateslib import *
from tia.bbg import LocalTerminal
from dateutil.relativedelta import relativedelta

sids = {'eur':514}

all_tenors = list(range(1,31))

class SwapCreator():
    def __init__(self,ccy,date= dt.today()):
        
        self.ccy = ccy
        self.curvenum = sids.get(ccy)
        self.date = date

    def create_curve(self):
        curve_id = 'YCSW' + str(self.curvenum).zfill(4) + ' Index'

        resp = LocalTerminal.get_reference_data(curve_id, 'CURVE_TENOR_RATES', CURVE_DATE=self.date.strftime('%Y%m%d'))
        df = resp.as_frame()
        tenors = df['CURVE_TENOR_RATES'].iloc[0]['Tenor'].to_list()
        rates = df['CURVE_TENOR_RATES'].iloc[0]['Mid Yield'].to_list()

        data = pd.DataFrame({'Term': tenors, 'Rate': rates})

        data['Termination'] = [add_tenor(self.date,_,"F",defaults.spec[str(self.ccy+'_irs')]['calendar']) for _ in data["Term"]]

        curve = Curve(
            id = str(self.ccy + self.ccy),
            convention = defaults.spec[self.ccy+'_irs']['convention'],
            modifier=defaults.spec[self.ccy+'_irs']['modifier'],
            interpolation='log_linear',
            nodes = {
                **{self.date: 1.0},
                **{_: 1.0 for _ in data["Termination"]},
            }
        )

        kws = dict(
            spec = str(self.ccy + '_irs'),
            curves = str(self.ccy + self.ccy)
        )

        solver = Solver(
            curves = [curve],
            instruments = [IRS(termination=_,effective=self.date,**kws) for _ in data["Termination"]],
            s = data['Rate'],
            instrument_labels = data["Term"],
            id = str(self.ccy + '_rates')
        )

        data['DF'] = [float(curve[_]) for _ in data["Termination"]]

        return curve, solver

    def price_swaps(self):
        curve, solver = self.create_curve()

        kws = dict(
        spec = str(self.ccy+'_irs'),
        curves = str(self.ccy + self.ccy)
        )
        
        swaps_data = []
        #Forward Swaps Only
        delta_target = 5000 
        for i in range (1, 30):
            for j in range(1, 31-i):
                effective = add_tenor(self.date, f"{i}Y","F", defaults.spec[str(self.ccy+'_irs')]['calendar'])
                termination = add_tenor(effective, f"{j}Y","F", defaults.spec[str(self.ccy+'_irs')]['calendar'])

                swap = IRS(
                    effective = effective,
                    termination = termination,
                    notional = 10e6,
                    **kws
                )
                initial_delta = float(swap.delta(solver=solver).sum().iloc[0])
                scaling_factor = delta_target/initial_delta
                notional = round(10e6 * scaling_factor,-5)


                swap = IRS(
                effective=effective,
                termination=termination,
                notional=notional,
                **kws
                )


                rate = float(swap.rate(solver=solver)) 
                rolled_rate = float(swap.rate(curve.roll("1M"))) 
                roll = rolled_rate - rate
                swaps_data.append((f"{self.ccy} {i}Y{j}Y", f"{i}Y{j}Y", rate, rolled_rate, roll, notional))


        swaps_df = pd.DataFrame(swaps_data, columns=['name','term','rate','rolled_rate', 'roll','notional'])
        swaps_df.sort_values('roll',inplace=True) 
        
        return swaps_df

# Function to get end-of-month dates for the past 5 years
def get_eom_dates(start_date, end_date):
    dates = []
    current_date = start_date
    while current_date <= end_date:
        eom_date = add_tenor(current_date,"1M","F",'tgt',1)
        if eom_date > end_date:
            break
        dates.append(eom_date)
        current_date = eom_date
        
    return dates

# Generate historical curves and calculate swaps
start_date = dt.today() - relativedelta(months=4)
end_date = dt.today()
eom_dates = get_eom_dates(start_date, end_date)

all_swaps_data = []
for date in eom_dates:
    swap_creator = SwapCreator('eur', date)
    
    swaps_df = swap_creator.price_swaps()
    swaps_df['date'] = date
    print(f"Swaps for {date}")
    print(swaps_df)
    all_swaps_data.append(swaps_df)    


final_swaps_df = pd.concat(all_swaps_data,ignore_index=True)


final_swaps_df.to_csv('master.csv')