# EURIBOR

import pandas as pd
import rateslib as rl
from datetime import datetime

# ESTR
estr_data = pd.DataFrame(
    {
        "Term": ["1W", "2W", "1M", "2M", "3M", "4M", "5M", "6M", "7M", "8M", "9M", "10M", "11M", "1Y", "18M",
                 "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10Y", "11Y", "12Y", "15Y", "20Y", "25Y", "30Y", "40Y", "50Y"],
        "Rate": [3.875,3.772,3.717,3.694,3.683,3.657,3.626,3.601,3.572,3.544,3.519,3.487,3.461,3.434,3.245,3.109,2.905,2.78,2.705,
                 2.663,2.644,2.637,2.644,2.656,2.669,2.684,2.716,2.683,2.601,2.522,2.391,2.273
],
    }
)

estr_data["Termination"] = [rl.add_tenor(datetime(2024,6,4), _, "F", "tgt") for _ in estr_data["Term"]]

estr = rl.Curve(
    id="eurrfr",
    convention="Act360",
    calendar="bus",
    modifier="MF",
    interpolation="log_linear",
    nodes={
        **{datetime(2024, 6, 4): 1.0},  # <- this is today's DF,
        **{_: 1.0 for _ in estr_data["Termination"]},
    },
)
estr_args = dict(effective=datetime(2024,6,4), spec="eur_irs", curves="eurrfr")

solver_estr = rl.Solver(
    curves=[estr],
    instruments=[rl.IRS(termination=_, **estr_args) for _ in estr_data["Termination"]],
    s=estr_data["Rate"],
    instrument_labels=estr_data["Term"],
    id="eurrfr",
)

estr_data["DF"] = [float(estr[_]) for _ in estr_data["Termination"]]
with pd.option_context("display.float_format", lambda x: "%.6f" % x):
    print(estr_data)

########################################################################################################################


euribor_data = pd.DataFrame(
    {
        "Term": ["6M", "7M", "8M", "9M", "10M", "11M", "12M", "15M",
                 "18M",
                 "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10Y", "11Y", "12Y", "15Y", "20Y", "25Y", "30Y", "40Y",
                 "50Y"],
        "Rate": [3.755,3.684,3.62,3.552,3.486,3.426,3.364,3.19,3.04,3.3149,3.1079,2.97825,2.8957,
                 2.8465,2.81685,2.8019,2.796,2.79625,2.79925,2.80325,2.80475,2.73025,2.616,2.5092,2.33325,2.1765],
    }
)
euribor_data["Termination"] = [rl.add_tenor(datetime(2024,6,4), _, "F", "tgt") for _ in euribor_data["Term"]]
input(euribor_data)

euribor_args = dict(curves="euribor6m", frequency="S", termination="6m", calendar="tgt")


euribor_args2 = dict(
    curves=["euribor6m", "eurrfr"],
    spec="eur_irs6"
)

euribor6m_curve = rl.Curve(
    id="euribor6m",
    convention="Act360",
    calendar="tgt",
    modifier="MF",
    interpolation="log_linear",
    nodes={
        **{datetime(2024, 6, 4): 1.0},  # <- this is today's DF,
        **{_: 1.0 for _ in euribor_data["Termination"]},
    },
)

instruments = [
    rl.FRA(datetime(2024,6,4), **euribor_args),  # 6M
    rl.FRA(datetime(2024, 7, 4), **euribor_args),  # 7M
    rl.FRA(datetime(2024, 8, 4), **euribor_args),  # 8M
    rl.FRA(datetime(2024, 9, 4), **euribor_args),  # 9M
    rl.FRA(datetime(2024, 10,4 ), **euribor_args),  # 10M
    rl.FRA(datetime(2024, 11, 4), **euribor_args),  # 11M
    rl.FRA(datetime(2024, 12, 4), **euribor_args),  # 12M
    rl.FRA(datetime(2025, 3, 4), **euribor_args),  # 15M
    rl.FRA(datetime(2025,6,4), **euribor_args),  # 18M
    rl.IRS(datetime(2024,6,4), "2y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "3y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "4y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "5y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "6y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "7y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "8y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "9y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "10y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "11y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "12y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "15y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "20y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "25y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "30y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "40y", **euribor_args2),
    rl.IRS(datetime(2024,6,4), "50y", **euribor_args2),
]

solver = rl.Solver(
    pre_solvers=[solver_estr],
    curves=[euribor6m_curve],
    instruments=instruments,
    s=euribor_data["Rate"],
    instrument_labels=euribor_data["Term"],
    id="euribor6m"
)

euribor_data["DF"] = [float(euribor6m_curve[_]) for _ in euribor_data["Termination"]]

with pd.option_context("display.float_format", lambda x: "%.6f" % x):
    print(euribor_data)

euriborswap = rl.IRS(
    notional = -10e6,
    effective = datetime(2024,6,6),
    termination = datetime(2025,6,6),
    **euribor_args2
                     ) 

euriborswaprate = euriborswap.rate(solver=solver)
print(euriborswaprate)