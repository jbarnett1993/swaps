from rateslib import *
import tia.bbg.datamgr as dm
import tia.analysis.ta as ta
import tia.analysis.model as model
import pandas as pd
import numpy as np
from tia.bbg import LocalTerminal
import datetime
# from pandas.tseries.offsets import Bday

today = dt.today()
start = add_tenor(dt.today(),"1Y","F",get_calendar("tgt"))
maturity = add_tenor(start,"1Y","F",get_calendar("tgt"))

# print(test_date,oneyear)
# usddefaults = defaults.spec["usd_irs"]["modifier"]

eurd = '45'
eur = '514'

# refactor this code so that it outputs {ccy} data as it loops through the curves

eurd = 'YCSW' + eurd.zfill(4) + ' Index'
eurdresp = LocalTerminal.get_reference_data(eurd, 'CURVE_TENOR_RATES')
eurddf = eurdresp.as_frame()
eurdtenors = eurddf['CURVE_TENOR_RATES'].iloc[0]['Tenor'].to_list()
eurdrates = eurddf['CURVE_TENOR_RATES'].iloc[0]['Mid Yield'].to_list()

print(eurdrates)
eurcurve_id  = 'YCSW' + eur.zfill(4) + ' Index'
eurresp = LocalTerminal.get_reference_data(eurcurve_id, 'CURVE_TENOR_RATES')
eurdf = eurresp.as_frame()
eurtenors = eurdf['CURVE_TENOR_RATES'].iloc[0]['Tenor'].to_list()
eurrates = eurdf['CURVE_TENOR_RATES'].iloc[0]['Mid Yield'].to_list()


eurddata = pd.DataFrame({"Term": eurdtenors,
                     "Rate":eurdrates})

eurddata["Termination"] = [add_tenor(start, _, "F", "tgt") for _ in eurddata["Term"]]


eurdata = pd.DataFrame({"Term":eurtenors,
                        "Rate":eurrates})

eurdata["Termination"] = [add_tenor(start,_,"F","tgt")for _ in eurdata["Term"]]



# can i write a global curve here or do i need to write all separate curves, i.e euruer, usdusd, noknok (lol)?

eurdeurd = Curve(
    id="eurdeurd",
    convention= defaults.spec["eur_irs6"]["convention"],
    calendar=defaults.spec["eur_irs6"]["calendar"],
    modifier=defaults.spec["eur_irs6"]["modifier"],
    interpolation="log_linear",
    nodes={
        **{today: 1.0},
        # **{dt(2024, 3, 1): 1.0},  # <- this is today's DF,
        **{_: 1.0 for _ in eurddata["Termination"]},
    }
)
eureur = Curve(
    id="eureur",
    convention= defaults.spec["eur_irs"]["convention"],
    calendar=defaults.spec["eur_irs"]["calendar"],
    modifier=defaults.spec["eur_irs"]["modifier"],
    interpolation="log_linear",
    nodes={
        **{today: 1.0},
        # **{dt(2024, 3, 1): 1.0},  # <- this is today's DF,
        **{_: 1.0 for _ in eurdata["Termination"]},
    }
)

eurd_kws = dict(
    effective=start,
    spec="eur_irs6",
    curves=["eurdeurd"]
)

eur_kws = dict(
    effective = start,
    spec = "eur_irs",
    curves = ["eureur"],
)

eurdsolver = Solver(
    curves=[eurdeurd],
    instruments=[IRS(termination=_, **eurd_kws) for _ in eurddata["Termination"]],
    s=eurddata["Rate"],
    instrument_labels=eurddata["Term"],
    id="eurd",
)

eurddata["DF"] = [float(eurdeurd[_]) for _ in eurddata["Termination"]]



eursolver = Solver(
    curves=[eureur],
    instruments = [IRS(termination=_,**eur_kws)for _ in eurdata["Termination"]],
    s=eurdata["Rate"],
    instrument_labels=eurdata["Term"],
    id="eur_rates",
)

eurdata["DF"] = [float(eureur[_]) for _ in eurdata["Termination"]]

eurirs = IRS(
    termination=maturity,
    notional=-100e6,
    **eur_kws,
)

eurdirs = IRS(
    termination=maturity,
    notional=-100e6,
    **eurd_kws,
)



eurnpv = eurirs.npv(solver=eursolver)
eurdv01 = eurirs.delta(solver=eursolver).sum()
eur_swap_rate = eurirs.rate(solver=eursolver)
# print(eurnpv)
# print(eurdv01)

eur_irs6 = eurdirs.rate(solver=eurdsolver)


print(eur_irs6)


print(eur_swap_rate)