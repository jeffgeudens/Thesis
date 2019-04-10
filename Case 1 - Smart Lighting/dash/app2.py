# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
from datetime import timedelta  
import time
import plotly
from dash.dependencies import Input, Output
import json
import requests
import mysql.connector
from sqlalchemy import create_engine
import base64

import utils.dash_reusable_components as drc

# Help function to load the data of a selected battery
def load_voltage(startDate, endDate, thingID, myToken):
    ##### Specify time range #####
    ##### Adjust this time range to specify which period you want to query - Mostly I use periods of one month #####
    startTime = int(startDate.timestamp())*1000;  #print(startTime)
    endTime = int(endDate.timestamp())*1000;  #print(endTime)

    ##### Choose scope #####
    scopeID = 'cot.smart_lighting'

    ##### Specify query #####
    metricID = 'Power.BatteryVoltHR'
    myUrlQuery = 'https://idlab-iot.tengu.io/api/v1/scopes/{scope}/query/{metric}/events?from={start}&to={end}&things={thing}&orderByTime=asc'\
        .format(scope = scopeID, metric = metricID, start=startTime, end=endTime, thing=thingID)

    headers = {
        'accept': 'application/json',
        'authorization': 'Bearer {0}'.format(myToken),
    }

    ##### Execute query #####
    response = requests.get(myUrlQuery, headers=headers)

    try:
        data = response.json(); 
        column_names = data['columns']; 
        values = data['values']
        df = pd.DataFrame.from_dict(values)
        df.columns = column_names
        df["value"] = pd.to_numeric(df.value, errors='coerce')

        ##### Clean up dataFrame #####
        # Rename the column
        df.rename(columns={'value':'Power.BatteryVoltHR'}, inplace=True)
        # Set timestamp as index
        df = df.set_index(pd.DatetimeIndex(pd.to_datetime(df.time, unit='ms')))
        df.drop(['time'], axis=1,inplace=True)
        message = 'All good'

        return df, message

    except ValueError:
        df = None
        errorMessage = "Decoding JSON has failed. Probably the token has expired"
        return df, errorMessage

def load_data_on_startup(myToken):
    endDate = datetime.now()
    startDate = datetime(2018, 8, 1, 1, 0)
    things = ['munisense.msup1g30034', 'munisense.msup1i70124', 'munisense.msup1h90115', 'munisense.msup1h90103']
    battery_voltages = pd.DataFrame()
    for thingID in things:
        df,message = load_voltage(startDate, endDate, thingID, myToken)
        battery_voltages = battery_voltages.append(df)

    return battery_voltages

def label_anomaly_moving_std (row, sigma):
    if (row['Power.BatteryVoltHR'] > (row['moving_average'] + (sigma * row['moving_std']))) | (row['Power.BatteryVoltHR'] < (row['moving_average'] - (sigma * row['moving_std']))):
        return 1
    else:
        return 0

def label_anomaly_fixed_std (row, sigma, fixed_std):
    if (row['Power.BatteryVoltHR'] > (row['moving_average'] + (sigma * fixed_std))) | (row['Power.BatteryVoltHR'] < (row['moving_average'] - (sigma * fixed_std))):
        return 1
    else:
        return 0

def low_pass_filtering(df, window_size, sigma, fixed_std):
    # Calculate moving average
    df['moving_average'] = df['Power.BatteryVoltHR'].rolling(window_size).mean()

    # Calculate anomalies
    df['residual'] = df['Power.BatteryVoltHR'] - df['moving_average']
    df['moving_std'] = df['Power.BatteryVoltHR'].rolling(window_size).std()
    df.dropna(inplace=True)
    df['anomaly_flag_moving_std']=df.apply (lambda row: label_anomaly_moving_std(row, sigma), axis=1)
    df['anomaly_flag_fixed_std']=df.apply (lambda row: label_anomaly_fixed_std(row, sigma, fixed_std), axis=1)

    return df

def find_last_datapoint(thingID, df):
    result = df[df['sourceId']==thingID].iloc[-1]
    return result.name

def find_first_datapoint(thingID):
    result = df[df['sourceId']==thingID].iloc[0]
    return result.name

external_css = [
    # Normalize the CSS
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
    # Fonts
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto",
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    # Base Stylesheet, replace this with your own base-styles.css using Rawgit
    "https://rawgit.com/xhlulu/9a6e89f418ee40d02b637a429a876aa9/raw/f3ea10d53e33ece67eb681025cedc83870c9938d/base-styles.css",
    # Custom Stylesheet, replace this with your own custom-styles.css using Rawgit
    "https://cdn.rawgit.com/plotly/dash-svm/bb031580/custom-styles.css"
]

# Set token
myToken = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIwUnhaVzd0N1d5aEczaEo3cUhoM3hQa3MzbkthTUE5Zy04SnozY2trQ3EwIn0.eyJqdGkiOiJkYmNmMzNjNy1hMzg2LTRiNDQtYWNjMC03MzViZWZiMjU1YTEiLCJleHAiOjE1NTQ4ODcyNTMsIm5iZiI6MCwiaWF0IjoxNTU0ODg2NjUzLCJpc3MiOiJodHRwczovL2lkbGFiLWlvdC50ZW5ndS5pby9hdXRoL3JlYWxtcy9pZGxhYi1pb3QiLCJhdWQiOiJwb2xpY3ktZW5mb3JjZXIiLCJzdWIiOiI3NGVjNTQzYi03Yjc1LTQ1ZGItOWExNy0xMDY5OTlmYmU3OWEiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJzd2FnZ2VyLXVpIiwibm9uY2UiOiJiZTFkODg5My01MGI2LTRiZDEtODIzYi1jZWE4N2NlNDY3N2UiLCJhdXRoX3RpbWUiOjE1NTQ4ODIwMjMsInNlc3Npb25fc3RhdGUiOiI4ZjZhOGQ1Zi1jZDk2LTRiNDQtYTY0MC01NjgyYjI1MTJiZTEiLCJhY3IiOiIwIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vaWRsYWItaW90LnRlbmd1LmlvIiwiaHR0cDovL2xvY2FsaG9zdDo1NTU1Il0sInJlc291cmNlX2FjY2VzcyI6eyJwb2xpY3ktZW5mb3JjZXIiOnsicm9sZXMiOlsidXNlcjp2aWV3Il19fSwiYXV0aG9yaXphdGlvbiI6eyJwZXJtaXNzaW9ucyI6W3sicnNpZCI6IjQxOGFiMGYzLWE5NTQtNGEwMS04ZTdlLWFlZGQzN2VjZTcyMyIsInJzbmFtZSI6ImRhdGE6c2NvcGVkOnZpZXcifV19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIGNvdC1zY29wZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicmlnaHRzIjpbXSwibmFtZSI6IkplZmYgR2V1ZGVucyIsImdyb3VwcyI6WyIvYWxsLXVzZXJzIiwiL2NvdC90aGVzaXMiXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiZ2V1ZGVucy5qZWZmQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZWZmIiwiZmFtaWx5X25hbWUiOiJHZXVkZW5zIiwiZW1haWwiOiJnZXVkZW5zLmplZmZAZ21haWwuY29tIiwicGljdHVyZSI6Imh0dHBzOi8vbGg1Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tRTYxVzBvTmFlOUkvQUFBQUFBQUFBQUkvQUFBQUFBQUFCd2MvUExDNy1mNTdnek0vcGhvdG8uanBnP3N6PTUwIn0.m4uGNlcGrnpDiqz2lVeSyIby580_4Eqy0Qn5Wcp-4txhjuU6WDUaROyzC3hfb1us7W5HABDbvj8KSbzU74e0tEHSQH_AdvCGiRZSK2Z1HDQg7LlFtk8-lkEf2xnuMFZqtFb1tnj4KD5jyuvJwgknARAufxSlZg3H_1tKdq_kZpXa7zCmMG0Yk5pIIIMHrvNaPgB7QuZJ7UQ4K8Z36fkFtE6BLorB5IpRsOjaPI3pFGBuivjQO7LJcIVv_iltslXELrWJTW0UdOnD2ZnxqldAc1mk1nySEhonh5TlGbKMxTCPBpHSbDikX3LCIn39N0K-f9eKWHvb04cgvjYTy5woDg'

# Load data on startup in a DataFrame
data = load_data_on_startup(myToken)

app = dash.Dash(__name__)

for css in external_css:
    app.css.append_css({"external_url": css})

app.scripts.config.serve_locally = True

image_directory = 'C:/Users/Jeff/Dropbox/ICT-Elektronica/Thesis/scripts/Case 1 - Smart Lighting/dash/images/'
static_image_route = '/static/'

image_filename = 'Check.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

# Choose options
sigma = 3




# Generate app
app.layout = dcc.Loading(
    type='cube',
    children=[html.Div(children=[
    # .container class is fixed, .container.scalable is scalable
    html.Div(className="banner", children=[
        # Change App Name here
        html.Div(className='container scalable', children=[
            # Change App Name here
            html.H2(html.A(
                'Smart Lighting - Battery voltage anomaly detection',
                href='https://github.com/jeffgeudens/Thesis/tree/master/Case%201%20-%20Smart%20Lighting',
                style={
                    'text-decoration': 'none',
                    'color': 'inherit'
                }
            )),

            html.A(
                html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"),
                href='https://plot.ly/products/dash/'
            )
        ]),
    ]),

    html.Div(id='body', className='container scalable', children=[
        html.Div(className='row', children=[

            html.Div(
                className='nine columns',
                children=[
                    html.H2(children='Introduction'),

                    html.Div(children='''
                        This dashboard prototype shows three battery packs that are being used in the Smart Lighting project at Sint-Andriesplein in Antwerp.
                        The raw data is shown together with the moving average. In case the moving average is more than three standard deviations
                        different from the raw data, an anomaly is indicated.
                    '''),

                    html.H2(children='Instructions'),
                    html.Div(children=[
                        html.Div("The panel on the right hand side is divided in two sections."),
                        html.Div("1) Data settings - Here you can choose the source of the data (which battery) and the time period"),
                        html.Div("2) Low pass filter settings - Here you can set the window size for the sliding window and the threshold for the standard deviation") ]   
                    ),

                    html.H3(id='battery-id'),
                    html.Div(
                        id='div-graphs',
                        children=dcc.Loading(id='live-update-graph-1', type='graph', color='gold')
                    ),
                    dcc.Interval(
                        id='interval-component',
                        interval=60*1000, # in milliseconds
                        n_intervals=0
                    ),
                    dcc.Interval(
                        id='interval-component-2',
                        interval=5*60*1000, # in milliseconds
                        n_intervals=0
                    )
                ]),

            html.Div(
                className='three columns',
                style={
                    'min-width': '24.5%',
                    'max-height': 'calc(100vh - 85px)',
                    'overflow-y': 'auto',
                    'overflow-x': 'hidden',
                },
                children=[
                    drc.Card([
                        html.H4(children="Overview"),
                        html.Img(id='overview-picture',
                            style={'width': '50px',
                                    'height': '50px'}),
                        html.Span(id='overview-text',
                            style={'margin-left': '10px'})
                    ]),
                    drc.Card([
                        html.H4(children="Data settings"),
                        drc.NamedDropdown(
                            name='Select Battery Packs',
                            id='dropdown-select-pack',
                            options=[
                                {'label': 'East', 'value': 'munisense.msup1h90115'},
                                {'label': 'South', 'value': 'munisense.msup1i70124'},
                                {'label': 'West', 'value': 'munisense.msup1g30034'}
                            ],
                            value='munisense.msup1h90115',
                            clearable=False,
                            searchable=False
                        ),

                        dcc.DatePickerRange(
                            id='my-date-picker-range',
                            min_date_allowed=datetime(2017,8,1),
                            max_date_allowed=datetime.today(),
                            initial_visible_month=datetime(datetime.today().year, datetime.today().month, 1),
                            display_format='DD/MM/YYYY',
                            end_date=datetime.now().date(),
                            start_date=(datetime.now() - timedelta(1/12*365)).date(),
                            with_portal=True
                        ),
                        html.Div(id='live-update-text')
                    ]),

                    drc.Card([
                        html.H4(children="Low pass filtering settings"),
                        drc.NamedSlider(
                            name='Window size',
                            id='slider-window-size',
                            min=32,
                            max=512,
                            marks={i: i for i in [32, 64, 128, 256, 512]},
                            value=256
                        ),

                        drc.NamedSlider(
                            name='Standard deviation',
                            id='slider-standard-deviation',
                            min=0.1,
                            max=0.5,
                            marks={i / 10: str(i / 10) for i in
                                                       range(0, 6, 1)},
                            step=0.1,
                            value=0.3,
                        ),

                        # html.Button(
                        #     'Reset Threshold',
                        #     id='button-zero-threshold'
                        # ),
                    ]),

                    drc.Card([
                        html.Button(
                            'Refresh graph',
                            id='button-refresh-graph'
                        )
                    ]),
                ]
            ),
        ]),
    ])
])])

@app.callback([Output('live-update-text', 'children'),
               Output('overview-picture', 'src'),
               Output('overview-text', 'children')],
              [Input('interval-component-2', 'n_intervals')])
def update_metrics(n):
    # Check for every thing when the last datapoint was added and do an API call to fill up the database
    things = ['munisense.msup1i70124', 'munisense.msup1h90115', 'munisense.msup1h90103']
    for thingID in things:
        startDate = data[data['sourceId']==thingID].iloc[-1].name
        endDate = datetime.now()
        data_new, message = load_voltage(startDate, endDate, thingID, myToken)
        data = data.append(data_new)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return [
        html.Span('Last update database: {}'.format(timestamp)),
        'https://raw.githubusercontent.com/jeffgeudens/Thesis/master/Case%201%20-%20Smart%20Lighting/dash/images/Check.png',
        'This is a test ...'
    ]

@app.callback(Output('battery-id', 'children'),
              [Input('dropdown-select-pack', 'value')])
def set_title(thingID):
    return [
        html.Span('Battery ID: {}'.format(thingID))
    ]

@app.callback(Output('live-update-graph-1', 'children'),
              [Input('button-refresh-graph', 'n_clicks'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input('dropdown-select-pack', 'value'),
              Input('slider-standard-deviation', 'value'),
              Input('slider-window-size', 'value')])

def update_graph_live(n, start_date, end_date, thingID, fixed_std, window_size):
    # Set start date and end date
    if end_date is not None:
        endDate = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        endDate = datetime.now()

    if start_date is not None:
        startDate = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        startDate = endDate - timedelta(1/12*365)
    
    if thingID == 'munisense.msup1g30034':
        middleDate = datetime(2019,1,23,0,0) 
        df1 = data[(data['sourceId']==thingID) & (data.index<middleDate) & (data.index>startDate)]
        df2 = data[(data['sourceId']=='munisense.msup1h90103') & (data.index<endDate) & (data.index>middleDate)]
        df_filt = df1.append(df2)
    else:
        df_filt = data[(data['sourceId']==thingID) & (data.index<endDate) & (data.index>startDate)]

    if df_filt.empty: 
        return html.Div(id='loading-1', children=[
            html.Span('{}'.format("No data"), style={'color': 'red'})
        ])

    else:
        df_filt = low_pass_filtering(df_filt, window_size, sigma, fixed_std)
        moving_anomalies = df_filt[df_filt['anomaly_flag_moving_std']==1]
        fixed_anomalies = df_filt[df_filt['anomaly_flag_fixed_std']==1]
        last_timestamp = df_filt.last_valid_index().strftime("%Y-%m-%d %H:%M")

        return html.Div(id='loading-1', children=[
            html.Div('Last received data point: {} (UTC)'.format(last_timestamp)),
            html.Div('Number of detected anomalies in this period: {}'.format(len(fixed_anomalies))),
            # html.Span('Last detected anomaly: {}'.format(fixed_anomalies['time'].iloc[-1])),
            dcc.Graph(
                id='graph-2-tabs',
                figure=go.Figure(
                    data=[
                        go.Scatter(
                            x=df_filt.index,
                            y=df_filt['Power.BatteryVoltHR'],
                            mode='markers',
                            opacity=0.7,
                            marker={
                            'size': 6
                            },
                            name='Raw data'
                            ),
                        go.Scatter(
                            x=df_filt.index,
                            y=df_filt['moving_average'],
                            mode='lines',
                            name='Moving average'
                            ),
                        go.Scatter(
                            x=fixed_anomalies.index,
                            y=fixed_anomalies['Power.BatteryVoltHR'],
                            mode='markers',
                            marker={
                            'size': 10,
                            'symbol': 'x',
                            'color': 'red'
                            },
                            name='anomalies'   
                            )
                    ],
                    layout=go.Layout(
                        xaxis={'title': 'Time'},
                        yaxis={'title': 'Battery voltage [V]',
                        'range': [0,17.5]},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 0},
                        hovermode='closest',
                    )
                ),
            )
        ])

        
    
if __name__ == '__main__':
    app.run_server(debug=True)