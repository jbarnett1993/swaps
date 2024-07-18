from rateslib import *
from tia.bbg import LocalTerminal
import pandas as pd
from datetime import datetime


# datetime(2024,6,4) = dt.today()
start = add_tenor(datetime(2024,6,4),"2b","F",get_calendar("tgt"))
maturity = add_tenor(start,"1Y","F",get_calendar("tgt"))

estrcurve = '514'

estrcurveid = 'YCSW' + estrcurve.zfill(4) + ' Index'
estrresp = LocalTerminal.get_reference_data(estrcurveid,'CURVE_TENOR_RATES')
estrdf = estrresp.as_frame()
estrtenors = estrdf['CURVE_TENOR_RATES'].iloc[0]['Tenor'].to_list()
estrrates = estrdf['CURVE_TENOR_RATES'].iloc[0]['Mid Yield'].to_list()

estrdata = pd.DataFrame({"Term": estrtenors, 
                        "Rate":estrrates})
# estrdata = pd.DataFrame(
#     {
#         "Term": ["1W", "2W", "1M", "2M", "3M", "4M", "5M", "6M", "7M", "8M", "9M", "10M", "11M", "1Y", "18M",
#                  "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10Y", "11Y", "12Y", "15Y", "20Y", "25Y", "30Y", "40Y", "50Y"],
#         "Rate": [3.875,3.772,3.717,3.694,3.683,3.657,3.626,3.601,3.572,3.544,3.519,3.487,3.461,3.434,3.245,3.109,2.905,2.78,2.705,
#                  2.663,2.644,2.637,2.644,2.656,2.669,2.684,2.716,2.683,2.601,2.522,2.391,2.273
# ],
#     }
# )


estrdata["Termination"] = [add_tenor(datetime(2024,6,4),_,"F","tgt") for _ in estrdata["Term"]]

estr_curve = Curve(
    id = "estr",
    convention=defaults.spec["eur_irs"]["convention"],
    calendar=defaults.spec["eur_irs"]["calendar"],
    modifier=defaults.spec["eur_irs"]["modifier"],
    interpolation="log_linear",
    nodes={
        **{datetime(2024,6,4):1.0},
        **{_:1.0 for _ in estrdata["Termination"]},
    }
)
        

eur_kws = dict(
    effective = datetime(2024,6,4),
    spec="eur_irs",
    curves ="estr"
)


estrsolver = Solver(
    curves=[estr_curve],
    instruments=[IRS(termination=_,**eur_kws)for _ in estrdata["Termination"]],
    s = estrdata["Rate"],
    instrument_labels=estrdata["Term"],
    id = "estr"
)


estrdata["DF"] = [float(estr_curve[_]) for _ in estrdata["Termination"]]

with pd.option_context("display.float_format", lambda x: "%.6f" % x):
    print(estrdata)

########################################################################################

euribor_curve = '45'


euribor_curve_id = 'YCSW' + euribor_curve.zfill(4) + ' Index'
euriborresp = LocalTerminal.get_reference_data(euribor_curve_id,'CURVE_TENOR_RATES')
euribordf = euriborresp.as_frame()
euribortenors = euribordf['CURVE_TENOR_RATES'].iloc[0]['Tenor'].to_list()
euriborrates = euribordf['CURVE_TENOR_RATES'].iloc[0]['Mid Yield'].to_list()

# print(euribortenors)
# print(euriborrates)


euribor_data = pd.DataFrame({"Term": euribortenors, 
                        "Rate":euriborrates})

# euribor_data = pd.DataFrame(
#     {
#         "Term": ["6M", "7M", "8M", "9M", "10M", "11M", "12M", "15M",
#                  "18M",
#                  "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10Y", "11Y", "12Y", "15Y", "20Y", "25Y", "30Y", "40Y",
#                  "50Y"],
#         "Rate": [3.755,3.684,3.62,3.552,3.486,3.426,3.364,3.19,3.04,3.3149,3.1079,2.97825,2.8957,
#                  2.8465,2.81685,2.8019,2.796,2.79625,2.79925,2.80325,2.80475,2.73025,2.616,2.5092,2.33325,2.1765],
#     }
# )
euribor_data["Termination"] = [add_tenor(datetime(2024,6,4),_,"F","tgt") for _ in euribor_data["Term"]]

euribor_fra_kws = dict(curves="eureur", frequency="S", termination="6m", calendar="tgt")

euribor_kws = dict(
    curves=["eureur", "estr"],
    spec="eur_irs6"
)

eureur_curve = Curve(
    id = "eureur",
    convention=defaults.spec["eur_irs6"]["convention"],
    calendar=defaults.spec["eur_irs6"]["calendar"],
    modifier=defaults.spec["eur_irs6"]["modifier"],
    interpolation="log_linear",
    nodes={
        **{datetime(2024,6,4):1.0},
        **{_:1.0 for _ in euribor_data["Termination"]},
    }
)
        



instruments = [
    FRA(datetime(2024,6,4), **euribor_fra_kws),  # 6M
    FRA(datetime(2024, 7, 4), **euribor_fra_kws),  # 7M
    FRA(datetime(2024, 8, 4), **euribor_fra_kws),  # 8M
    FRA(datetime(2024, 9, 4), **euribor_fra_kws),  # 9M
    FRA(datetime(2024, 10,4 ), **euribor_fra_kws),  # 10M
    FRA(datetime(2024, 11, 4), **euribor_fra_kws),  # 11M
    FRA(datetime(2024, 12, 4), **euribor_fra_kws),  # 12M
    FRA(datetime(2025, 3, 4), **euribor_fra_kws),  # 15M
    FRA(datetime(2025,6,4), **euribor_fra_kws),  # 18M
    IRS(datetime(2024,6,4), "2y", **euribor_kws),
    IRS(datetime(2024,6,4), "3y", **euribor_kws),
    IRS(datetime(2024,6,4), "4y", **euribor_kws),
    IRS(datetime(2024,6,4), "5y", **euribor_kws),
    IRS(datetime(2024,6,4), "6y", **euribor_kws),
    IRS(datetime(2024,6,4), "7y", **euribor_kws),
    IRS(datetime(2024,6,4), "8y", **euribor_kws),
    IRS(datetime(2024,6,4), "9y", **euribor_kws),
    IRS(datetime(2024,6,4), "10y", **euribor_kws),
    IRS(datetime(2024,6,4), "11y", **euribor_kws),
    IRS(datetime(2024,6,4), "12y", **euribor_kws),
    IRS(datetime(2024,6,4), "15y", **euribor_kws),
    IRS(datetime(2024,6,4), "20y", **euribor_kws),
    IRS(datetime(2024,6,4), "25y", **euribor_kws),
    IRS(datetime(2024,6,4), "30y", **euribor_kws),
    IRS(datetime(2024,6,4), "40y", **euribor_kws),
    IRS(datetime(2024,6,4), "50y", **euribor_kws),
]

euriborsolver = Solver(
    pre_solvers=[estrsolver],
    curves=[eureur_curve],
    instruments = instruments,
    s = euribor_data["Rate"],
    instrument_labels=euribor_data["Term"],
    id = "eureur"
)

euribor_data["DF"] = [float(eureur_curve[_]) for _ in euribor_data["Termination"]]

with pd.option_context("display.float_format", lambda x: "%.6f" % x):
    print(euribor_data)


euriborirs = IRS(
    notional = -10e6,
    effective = start,
    termination = maturity,
    **euribor_kws
)


euriborrate = euriborirs.rate(solver=euriborsolver)
print(euriborrate)


