from rateslib import *
import pandas as pd

curve_r = Curve(
    nodes={
        dt(2022, 1, 1): 1.0,
        dt(2023, 1, 1): 0.99,
        dt(2024, 1, 1): 0.98,
        dt(2025, 1, 1): 0.97,
        dt(2026, 1, 1): 0.96,
        dt(2027, 1, 1): 0.95,
    },
    id="r"
)

curve_z = Curve(
    nodes={
        dt(2022, 1, 1): 1.0,
        dt(2023, 1, 1): 0.99,
        dt(2024, 1, 1): 0.98,
        dt(2025, 1, 1): 0.97,
        dt(2026, 1, 1): 0.96,
        dt(2027, 1, 1): 0.95,
    },
    id="z"
)

curve_s = Curve(
    nodes={
        dt(2022, 1, 1): 1.0,
        dt(2023, 1, 1): 0.99,
        dt(2024, 1, 1): 0.98,
        dt(2025, 1, 1): 0.97,
        dt(2026, 1, 1): 0.96,
        dt(2027, 1, 1): 0.95,
    },
    id="s"
)

args = dict(termination="1Y", frequency="A", fixing_method="ibor", leg2_fixing_method="ibor")

instruments = [
    SBS(dt(2022, 1, 1), curves=["r", "s", "s", "s"], **args),
    SBS(dt(2023, 1, 1), curves=["r", "s", "s", "s"], **args),
    SBS(dt(2024, 1, 1), curves=["r", "s", "s", "s"], **args),
    SBS(dt(2025, 1, 1), curves=["r", "s", "s", "s"], **args),
    SBS(dt(2026, 1, 1), curves=["r", "s", "s", "s"], **args),
    SBS(dt(2022, 1, 1), curves=["r", "s", "z", "s"], **args),
    SBS(dt(2023, 1, 1), curves=["r", "s", "z", "s"], **args),
    SBS(dt(2024, 1, 1), curves=["r", "s", "z", "s"], **args),
    SBS(dt(2025, 1, 1), curves=["r", "s", "z", "s"], **args),
    SBS(dt(2026, 1, 1), curves=["r", "s", "z", "s"], **args),
    IRS(dt(2022, 1, 1), "1Y", "A", curves=["r", "s"], leg2_fixing_method="ibor"),
    IRS(dt(2023, 1, 1), "1Y", "A", curves=["r", "s"], leg2_fixing_method="ibor"),
    IRS(dt(2024, 1, 1), "1Y", "A", curves=["r", "s"], leg2_fixing_method="ibor"),
    IRS(dt(2025, 1, 1), "1Y", "A", curves=["r", "s"], leg2_fixing_method="ibor"),
    IRS(dt(2026, 1, 1), "1Y", "A", curves=["r", "s"], leg2_fixing_method="ibor"),
]

solver = Solver(
    curves=[curve_r, curve_s, curve_z],
    instruments=instruments,
    s=[0.]*5 + [0.]*5 + [1.5]*5,
    id="sonia",
    instrument_labels=[
        "s1", "s2", "s3", "s4", "s5",
        "z1", "z2", "z3", "z4", "z5",
        "r1", "r2", "r3", "r4", "r5",
    ],
)

irs = IRS(dt(2022, 1, 1), "5Y", "A", notional=-8.3e8, curves=["z", "s"], leg2_fixing_method="ibor", fixed_rate=25.0)

print(irs.delta(solver=solver))