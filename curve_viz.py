import pandas as pd
import datetime as dt
from rateslib import add_tenor
from tia.bbg import LocalTerminal
from dateutil.relativedelta import relativedelta
import plotly.graph_objs as go
import plotly.io as pio

sids = {'eur': 514, 'gbp': 141, 'usd': 490}

curves = {}
for key, value in sids.items():
    curve = 'YCSW' + str(value).zfill(4) + ' Index'
    curves[curve] = key.upper()  # Store curve ID and corresponding currency

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

dates = get_eom_dates(dt.datetime.today() - relativedelta(years=15), dt.datetime.today(), 'bus')

# Function to batch requests
def batch_requests(curves, dates, batch_size=10):
    for i in range(0, len(curves), batch_size):
        for j in range(0, len(dates), batch_size):
            curve_batch = list(curves.keys())[i:i + batch_size]
            date_batch = dates[j:j + batch_size]
            for curve in curve_batch:
                for date in date_batch:
                    yield curve, date

# Create a dictionary to store the data
data = {}

# Batch the requests
for curve, date in batch_requests(curves, dates, batch_size=5):
    curve_id = curve
    resp = LocalTerminal.get_reference_data(curve_id, 'CURVE_TENOR_RATES', CURVE_DATE=date.strftime('%Y%m%d'))
    df = resp.as_frame()
    tenors = df['CURVE_TENOR_RATES'].iloc[0]['Tenor'].to_list()
    rates = df['CURVE_TENOR_RATES'].iloc[0]['Mid Yield'].to_list()
    df = pd.DataFrame({'Term': tenors, 'Rate': rates})
    print(df)
    # Store the data in the dictionary with keys as (curve, date)
    data[(curve, date)] = df

# Plotting with Plotly
def create_interactive_chart(data, curve, currency):
    fig = go.Figure()

    curve_data = [(date, df) for (c, date), df in data.items() if c == curve]
    curve_data.sort(key=lambda x: x[0])
    for date, df in curve_data:
        fig.add_trace(go.Scatter(x=df['Term'], y=df['Rate'], mode='lines', name=f'{date.strftime("%Y-%m-%d")}', visible=False))

    fig.data[0].visible = True  # Show the first curve initially

    # Create a slider for date selection
    steps = []
    for i, (date, _) in enumerate(curve_data):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)},
                  {"title": f"Yield Curve for {currency} - {date.strftime('%Y-%m-%d')}"}],
        )
        step["args"][0]["visible"][i] = True  # Toggle i-th trace to be visible
        steps.append(dict(step, label=date.strftime('%Y-%m-%d')))  # Add the date as the label

    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Date: "},
        pad={"t": 50},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders,
        title=f"Yield Curves for {currency}",
        xaxis_title="Term",
        yaxis_title="Rate"
    )

    # Save the plot as an HTML file
    file_name = f'yield_curves_{currency}.html'
    pio.write_html(fig, file_name)

    print(f"Interactive chart saved as '{file_name}'.")

for curve, currency in curves.items():
    create_interactive_chart(data, curve, currency)