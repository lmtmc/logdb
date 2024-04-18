#auto update everyday
# db is too large
import dash
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

astig_fields = ['M1ZC0']
focus_fields = ['M2XOffset', 'M2YOffset', 'M2ZOffset']
point_fields = [
    'AzPointOffset', 'ElPointOffset', 'Flag', 'FitFlag', 'FitRegion', 'PeakValue', 'PeakError', 'AzMapOffset',
    'ElMapOffset', 'AzMapOffsetError', 'ElMapOffsetError', 'AzHpbw', 'ElHpbw', 'AzHpbwError', 'ElHpbwError',
    'PeakSnrValue', 'PeakSnrError', 'PixelList'
]

def get_df(csv_file):
    if csv_file == "point":
        df = pd.read_csv(f'./lmtqldb/{csv_file}.csv', skiprows=[18361, 18362, 18364, 18985, 20372])
    else:
        df = pd.read_csv(f'./lmtqldb/{csv_file}.csv')
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    return df

date_selector = html.Div([
                    dbc.Row(html.H5('Select Date Range')),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date='2021-05-01',
                        end_date='2021-05-31',
                        display_format='YYYY-MM-DD',
                        start_date_placeholder_text='Start Date',
                        end_date_placeholder_text='End Date',
                        persistence=True,  # Enable persistence if required
                        persistence_type='session',  # Persist in session
                    ),
                ], className='mb-3'),
obsnum_selector = html.Div(

                        [
                            dbc.Row(html.H5('Select ObsNum Range')),

                            dbc.Row([
                                dbc.Col(dbc.Label('Start'),width=3), dbc.Col(dcc.Input(id='obsnum-start', type='number',)),
                            ]),
                            dbc.Row([
                                dbc.Col(dbc.Label('End'),width=3), dbc.Col(dcc.Input(id='obsnum-end', type='number',)),
                            ]),
                        ], className='mb-3'
                    ),


receiver_selector = html.Div([

                            dbc.Col(html.H5('Select Receivers'), width='auto'),
                            dbc.Col(dbc.Checklist(id='receiver'), width='auto'),
                ], className='mb-3'),

filter_button = html.Div([
                    dbc.Row([
                        dbc.Col(dbc.Button('Filter Data', color='primary', id='filter_btn'), width='auto'),
                        dbc.Col(dbc.Button('Reset Filter', color='primary', id='reset_btn'), width='auto'),
                    ])
                ], className='mb-3')

app.layout = dbc.Container([
     html.H1('Log Data'),
        html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                [
                    dbc.Row(date_selector, className='mb-3'),
                    dbc.Row(obsnum_selector),
                    dbc.Row(receiver_selector),
                    dbc.Row(filter_button),
                ], style={'padding': '10px', 'height': '75vh', 'overflow-y': 'auto'}
            )
           ,width=3),

        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(html.Div('Select a tab to view data', )),
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab(label="Astigmatism", tab_id="astig"),
                            dbc.Tab(label="Focus", tab_id="focus"),
                            dbc.Tab(label="Point", tab_id="point"),
                        ],
                            id="tabs", active_tab="astig",
                        ),
                        html.Div(id="content"),
                    ]),
                ], style={'padding': '10px', 'height': '75vh', 'overflow-y': 'auto'}
            ),width=9
        )
    ])

 ])


# get the date range and obsnum range from the csv file
@app.callback(
    Output('date-picker-range', 'start_date'),
    Output('date-picker-range', 'end_date'),
    Output('obsnum-start', 'value'),
    Output('obsnum-end', 'value'),
    Output('receiver', 'options'),
    Output('receiver', 'value'),
    Input('tabs', 'active_tab'),
)
def update_filter_range(at):
    if not at:  # If the active_tab is None, don't update anything
        raise PreventUpdate

    # Try to fetch and prepare the dataframe
    try:
        df = get_df(at)
        if 'DateTime' in df.columns and 'ObsNum' in df.columns and 'Receiver' in df.columns:
            receivers = df['Receiver'].unique()
            receivers = [receiver for receiver in receivers if pd.notna(receiver)]
            return (df['DateTime'].min(), df['DateTime'].max(), int(df['ObsNum'].min()), int(df['ObsNum'].max()),
                    [{'label': i, 'value': i} for i in receivers], receivers)
        else:
            raise ValueError("Necessary columns are missing in the dataframe")
    except Exception as e:
        print(f"Error updating date range for tab {at}: {e}")
        raise PreventUpdate

@app.callback(
    Output("content", "children"),
    Input("tabs", "active_tab"),
    Input('filter_btn', 'n_clicks'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('obsnum-start', 'value'),
    State('obsnum-end', 'value'),
    State('receiver', 'value'),
)
def switch_tab(at, n, start_date, end_date, obsnum_start, obsnum_end, receivers):

    df = get_df(at)
    #filter by date range
    mask_date = (df['DateTime'] >= start_date) & (df['DateTime'] <= end_date)
    df_date = df[mask_date]
    #filter by receivers
    if receivers is not None:
        mask_receiver = df_date['Receiver'].isin(receivers)
        df_receiver = df_date[mask_receiver]
    else:
        df_receiver = df_date

    #filter by obsnum range
    mask_obsnum = (df_receiver['ObsNum'] >= obsnum_start) & (df_receiver['ObsNum'] <= obsnum_end)
    df = df_receiver[mask_obsnum]


    fig = make_subplots(rows=2, cols=1, subplot_titles=(f'{at} by ObsNum', f'{at} by Time'))
    fields = astig_fields if at == "astig" else focus_fields if at == "focus" else point_fields

    for y in fields:
        fig.add_trace(
            go.Scatter(x=df['ObsNum'], y=df[y], mode='lines', name=f"{y} by ObsNum", legendgroup='group1'),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['DateTime'], y=df[y], mode='lines', name=f"{y} by DateTime", legendgroup='group2'),
            row=2, col=1
        )
    fig.update_layout(title=f'{at} Data')
    fig.update_yaxes(title_text=f'{at}', row=1, col=1)
    fig.update_yaxes(title_text=f'{at}', row=2, col=1)
    return dcc.Graph(figure=fig)


if __name__ == '__main__':
    app.run_server(debug=True)

