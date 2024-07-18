from rateslib import *
import pandas as pd
from tia.bbg import LocalTerminal

today = dt.today()
start = add_tenor(today,"2Y","F",get_calendar("tgt"))
mat = add_tenor(start,"2Y","F",get_calendar("tgt"))

curves = {
    'EUR':'514', 
}
curve_ids = []


for ccy, curve in curves.items():
    curve_id = 'YCSW' + curve.zfill(4) + ' Index'
    curve_ids.append(curve_id)
resp = LocalTerminal.get_reference_data(curve_ids, 'CURVE_TENOR_RATES')
df = resp.as_frame()
tenors = df['CURVE_TENOR_RATES'].iloc[0]['Tenor'].to_list()
rates = df['CURVE_TENOR_RATES'].iloc[0]['Mid Yield'].to_list()

data = pd.DataFrame({"Term": tenors,
                     "Rate":rates})


data["Termination"] = [add_tenor(today, _, "F", "tgt") for _ in data["Term"]]


ESTR = Curve(
    id="ESTR",
    convention = defaults.spec["eur_irs"]['convention'],
    modifier = defaults.spec["eur_irs"]['modifier'],
    interpolation="log_linear",
    nodes={
        **{today: 1.0},
        # **{dt(2024, 3, 1): 1.0},  # <- this is today's DF,
        **{_: 1.0 for _ in data["Termination"]},
    }
)

estr_args = dict(spec="eur_irs", curves="ESTR")

solver = Solver(
    curves=[ESTR],
    instruments=[IRS(termination=_,effective=today, **estr_args) for _ in data["Termination"]],
    s=data["Rate"],
    instrument_labels=data["Term"],
    id="eur_rates",
)


data["DF"] = [float(ESTR[_]) for _ in data["Termination"]]


irs = IRS(
    effective= start ,
    termination=mat,
    notional=-10e6,
    **estr_args
)

swap_rate = float(irs.rate(solver=solver))
print(swap_rate)

rolled_swap_rate = float(irs.rate(ESTR.roll("3m")))

print(rolled_swap_rate)