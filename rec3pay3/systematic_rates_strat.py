import pandas as pd
import datetime as dt
from rateslib import *
from tia.bbg import LocalTerminal
from dateutil.relativedelta import relativedelta

sids = {'eur': 514, 'gbp': 141, 'usd': 490}
# sids = {'eur': 514, 'usd': 490, 'gbp': 141, 'chf': 234, 'sek': 185, 'nok': 487}
all_tenors = list(range(1, 31))

class SwapCreator():
    def __init__(self, ccy, date=dt.today()):
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
        data['Termination'] = [add_tenor(self.date, _, "F", defaults.spec[str(self.ccy + '_irs')]['calendar']) for _ in data["Term"]]

        curve = Curve(
            id=str(self.ccy + self.ccy),
            convention=defaults.spec[self.ccy + '_irs']['convention'],
            modifier=defaults.spec[self.ccy + '_irs']['modifier'],
            interpolation='log_linear',
            nodes={
                **{self.date: 1.0},
                **{_: 1.0 for _ in data["Termination"]},
            }
        )

        kws = dict(
            spec=str(self.ccy + '_irs'),
            curves=str(self.ccy + self.ccy)
        )

        solver = Solver(
            curves=[curve],
            instruments=[IRS(termination=_, effective=self.date, **kws) for _ in data["Termination"]],
            s=data['Rate'],
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
        for i in range(1, 10):
            for j in range(1, 11 - i):
                effective = add_tenor(self.date, f"{i}Y", "F", defaults.spec[str(self.ccy + '_irs')]['calendar'])
                termination = add_tenor(effective, f"{j}Y", "F", defaults.spec[str(self.ccy + '_irs')]['calendar'])

                swap = IRS(
                    effective=effective,
                    termination=termination,
                    notional=10e6,
                    **kws
                )

                rate = float(swap.rate(solver=solver))
                rolled_rate = float(swap.rate(curve.roll("1M")))
                roll = rolled_rate - rate
                swaps_data.append((f"{self.ccy} {i}Y{j}Y", f"{i}Y{j}Y", rate, rolled_rate, roll))

        swaps_df = pd.DataFrame(swaps_data, columns=['name', 'term', 'rate', 'rolled_rate', 'roll'])
        swaps_df.sort_values('roll', inplace=True)

        return swaps_df

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

def rebalance_swaps(start_date, end_date):
    all_positions = []

    for ccy in sids.keys():
        calendar = defaults.spec[str(ccy + '_irs')]['calendar']
        eom_dates = get_eom_dates(start_date, end_date, calendar)
        positions = []

        for date in eom_dates:
            swap_creator = SwapCreator(ccy, date)
            swaps_df = swap_creator.price_swaps()
            swaps_df['date'] = date

            receive_swaps = swaps_df.head(3)
            pay_swaps = swaps_df.tail(3)

            # Close out previous month's positions
            for position in positions:
                if position['close_date'] == date:
                    entry_rate = position['rate']
                    closing_swap = swaps_df[swaps_df['term'] == position['term']]
                    if not closing_swap.empty:
                        closing_rate = closing_swap['rolled_rate'].values[0]
                        pnl = (closing_rate - entry_rate) * position['direction'] * 100 * 5000
                        position['pnl'] = pnl
                        position['exit_rate'] = closing_rate
                    else:
                        position['pnl'] = None
                        position['exit_rate'] = None

            # Add new positions
            for _, swap in receive_swaps.iterrows():
                positions.append({
                    'date': date,
                    'ccy': ccy,
                    'term': swap['term'],
                    'rate': swap['rate'],
                    'direction': -1,  # Receive
                    'exit_rate': None,  # Initialize with None
                    'pnl': None,  # Initialize with None
                    'close_date': add_tenor(date, "1M", "F", calendar, 1),
                })

            for _, swap in pay_swaps.iterrows():
                positions.append({
                    'date': date,
                    'ccy': ccy,
                    'term': swap['term'],
                    'rate': swap['rate'],
                    'direction': 1,  # Pay
                    'exit_rate': None,  # Initialize with None
                    'pnl': None,  # Initialize with None
                    'close_date': add_tenor(date, "1M", "F", calendar, 1),
                })

            # Print positions for the month
            print(f"Positions for {ccy} on {date}")
            for position in positions:
                if position['date'] == date:
                    print(position)

        all_positions.extend(positions)

    return all_positions

start_date = dt.today() - relativedelta(years=15)
end_date = dt.today()
positions = rebalance_swaps(start_date, end_date)

# Convert positions to DataFrame and save to CSV
positions_df = pd.DataFrame(positions)
positions_df.to_csv('rec3pay3_txs', index=False)