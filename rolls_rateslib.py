import pandas as pd
import datetime as dt
from rateslib import *
from tia.bbg import LocalTerminal

sids = {'eur': 514, 'usd': 490, 'gbp': 141, 'chf': 234}

today = dt.today()
all_tenors = list(range(1, 31))

class SwapCreator():
    def __init__(self, ccy):
        self.ccy = ccy
        self.curvenum = sids.get(ccy)

    def create_curve(self):
        curve_id = 'YCSW' + str(self.curvenum).zfill(4) + ' Index'

        resp = LocalTerminal.get_reference_data(curve_id, 'CURVE_TENOR_RATES')
        df = resp.as_frame()
        tenors = df['CURVE_TENOR_RATES'].iloc[0]['Tenor'].to_list()
        rates = df['CURVE_TENOR_RATES'].iloc[0]['Mid Yield'].to_list()

        data = pd.DataFrame({'Term': tenors, 'Rate': rates})
        data['Termination'] = [add_tenor(today, _, "F", defaults.spec[str(self.ccy + '_irs')]['calendar']) for _ in data["Term"]]

        curve = Curve(
            id=str(self.ccy + self.ccy),
            convention=defaults.spec[str(self.ccy + '_irs')]['convention'],
            modifier=defaults.spec[str(self.ccy + '_irs')]['modifier'],
            interpolation='log_linear',
            nodes={
                **{today: 1.0},
                **{_: 1.0 for _ in data["Termination"]},
            }
        )

        kws = dict(
            spec=str(self.ccy + '_irs'),
            curves=str(self.ccy + self.ccy)
        )

        solver = Solver(
            curves=[curve],
            instruments=[IRS(termination=_, effective=today, **kws) for _ in data["Termination"]],
            s=data["Rate"],
            instrument_labels=data["Term"],
            id=str(self.ccy + '_rates')
        )
        data['DF'] = [float(curve[_]) for _ in data["Termination"]]
        
        return curve, solver

    def price_swaps(self):
        curve, solver = self.create_curve()
        kws = dict(
            spec=str(self.ccy + '_irs'),
            curves=str(self.ccy + self.ccy)
        )

        swaps_data = []
        delta_target = 5000
        # Spot Swaps
        for i in all_tenors:
            termination = add_tenor(today, f"{i}Y", "F", defaults.spec[str(self.ccy + '_irs')]['calendar'])
            swap = IRS(
                effective=today,
                termination=termination,
                notional=10e6,
                **kws
            )
            initial_delta = float(swap.delta(solver=solver).sum().iloc[0])
            scaling_factor = delta_target/initial_delta
            notional = round(10e6 * scaling_factor,-5)
            swap = IRS(
                effective=today,
                termination=termination,
                notional=notional,
                **kws
            )
                
            rate = float(swap.rate(solver=solver))
            rolled_rate_3m = float(swap.rate(curve.roll("3m")))
            roll_3m = rate - rolled_rate_3m
            delta = float(swap.delta(solver=solver).sum().iloc[0])

            swaps_data.append((f"{self.ccy} {i}Y", f"{i}Y", rate, roll_3m, delta, notional))

        # Forward Swaps
        for i in range(1, 30):
            for j in range(1, 31 - i):
                effective = add_tenor(today, f"{i}Y", "F", defaults.spec[str(self.ccy + '_irs')]['calendar'])
                termination = add_tenor(effective, f"{j}Y", "F", defaults.spec[str(self.ccy + '_irs')]['calendar'])

                swap = IRS(
                    effective=effective,
                    termination=termination,
                    notional=10e6,
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
                rolled_rate_3m = float(swap.rate(curve.roll("3m")))
                roll_3m = rate - rolled_rate_3m
                delta = float(swap.delta(solver=solver).sum().iloc[0])
                swaps_data.append((f"{self.ccy} {i}Y{j}Y", f"{i}Y{j}Y", rate, roll_3m,delta, notional))

        swaps_df = pd.DataFrame(swaps_data, columns=['name','term', 'rate', '3m roll','DV01','notional'])


        return swaps_df

estr = SwapCreator('eur')
swaps_df = estr.price_swaps()

print(swaps_df)
swaps_df.to_csv('swaps_df.csv')