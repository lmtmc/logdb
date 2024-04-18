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
        df = pd.read_csv(f'./logdb/lmtqldb/{csv_file}.csv', skiprows=[18361, 18362, 18364, 18985, 20372])
    else:
        df = pd.read_csv(f'./logdb/lmtqldb/{csv_file}.csv')
    return df

app.layout = dbc.Container([
    html.H1('Log Data'),
    html.Br(),
    dbc.Card([
        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Row(dbc.Label('Select Date Range')),
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
            ], ),
            dbc.Col([
                html.Div([
                    dbc.Label('Select ObsNum Range'),
                    dbc.Row(
                        [
                            dbc.Col(dbc.Label('Start'), width='auto'),
                            dbc.Col(dcc.Input(id='obsnum-start', type='number', value=0), width='auto'),
                            dbc.Col(dbc.Label('End'), width='auto'),
                            dbc.Col(dcc.Input(id='obsnum-end', type='number', value=1000), width='auto'),
                        ],

                    ),
                ], className='mb-3'),
            ]),
        ]),
        dbc.Row(dbc.Col(dbc.Button('Apply Filters', color='primary',id='apply')))],
        body=True,  # Add this if you want card styling around the content
    ),
    html.Br(),
    dbc.Label('Select a tab to view data'),
    dbc.Tabs(
        [
            dbc.Tab(label="Astigmatism", tab_id="astig"),
            dbc.Tab(label="Focus", tab_id="focus"),
            dbc.Tab(label="Point", tab_id="point"),
        ],
        id="tabs",
        active_tab="astig",
    ),
    html.Div(id="content"),
], fluid=True)

# get the date range and obsnum range from the csv file
@app.callback(
    Output('date-picker-range', 'start_date'),
    Output('date-picker-range', 'end_date'),
    Output('obsnum-start', 'value'),
    Output('obsnum-end', 'value'),
    Input('tabs', 'active_tab')
)
def update_date_range(at):
    if not at:  # If the active_tab is None, don't update anything
        raise PreventUpdate

    # Try to fetch and prepare the dataframe
    try:
        df = get_df(at)
        if 'Date' in df.columns and 'Time' in df.columns and 'ObsNum' in df.columns:
            df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
            print(df['DateTime'].min(), df['DateTime'].max(), int(df['ObsNum'].min()), int(df['ObsNum'].max()))
            return df['DateTime'].min(), df['DateTime'].max(), int(df['ObsNum'].min()), int(df['ObsNum'].max())
        else:
            raise ValueError("Necessary columns are missing in the dataframe")
    except Exception as e:
        print(f"Error updating date range for tab {at}: {e}")
        raise PreventUpdate
@app.callback(
    Output("content", "children"),
    Input("tabs", "active_tab"),
    Input('apply', 'n_clicks'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('obsnum-start', 'value'),
    State('obsnum-end', 'value'),
)
def switch_tab(at, n, start_date, end_date, obsnum_start, obsnum_end):

    df = get_df(at)
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    mask_date = (df['DateTime'] >= start_date) & (df['DateTime'] <= end_date)
    df_date = df[mask_date]
    mask_obsnum = (df['ObsNum'] >= obsnum_start) & (df['ObsNum'] <= obsnum_end)
    df_obsnum = df[mask_obsnum]

    fig = make_subplots(rows=2, cols=1, subplot_titles=(f'{at} by ObsNum', f'{at} by Time'))
    fields = astig_fields if at == "astig" else focus_fields if at == "focus" else point_fields

    for y in fields:
        fig.add_trace(
            go.Scatter(x=df_obsnum['ObsNum'], y=df_obsnum[y], mode='lines', name=f"{y} by ObsNum", legendgroup='group1'),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df_date['DateTime'], y=df_date[y], mode='lines', name=f"{y} by DateTime", legendgroup='group2'),
            row=2, col=1
        )
    fig.update_layout(title=f'{at} Data')
    fig.update_yaxes(title_text=f'{at}', row=1, col=1)
    fig.update_yaxes(title_text=f'{at}', row=2, col=1)
    return dcc.Graph(figure=fig)


if __name__ == '__main__':
    app.run_server(debug=True)

