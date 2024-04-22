import dash
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd

from plotly.subplots import make_subplots
import plotly.graph_objects as go

prefix = '/lmtqldb/'

import flask
from flask import redirect, url_for, render_template_string, request
# Create a Dash app
server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                requests_pathname_prefix=prefix,routes_pathname_prefix=prefix,
                server = server, title='LMT QL DB',
                prevent_initial_callbacks="initial_duplicate", suppress_callback_exceptions=True
                )
# Definine constants
def get_df(csv_file):
    if csv_file == "point":
        df = pd.read_csv(f'./lmtqldb/{csv_file}.csv', skiprows=[18361, 18362, 18364, 18985, 20372])
    else:
        df = pd.read_csv(f'./lmtqldb/{csv_file}.csv')
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    return df
astig_fields = ['M1ZC0']
focus_fields = ['M2XOffset', 'M2YOffset', 'M2ZOffset']
point_fields = [
    'AzPointOffset', 'ElPointOffset', 'Flag', 'FitFlag', 'FitRegion', 'PeakValue', 'PeakError', 'AzMapOffset',
    'ElMapOffset', 'AzMapOffsetError', 'ElMapOffsetError', 'AzHpbw', 'ElHpbw', 'AzHpbwError', 'ElHpbwError',
    'PeakSnrValue', 'PeakSnrError', 'PixelList'
]
focus_fields_default = focus_fields[2]
point_fields_default = point_fields[0:2]
default_receivers = [
    'HoloReceiver',
    'RedshiftReceiver',
    'AztecReceiver',
    'Vlbi1mmReceiver',
    'B4rReceiver',
    'Msip1mm',
    'Sequoia',
    'B4r',
    'DefaultReceiver',
    'Muscat',
    'Toltec']
default_tab = 'astig'
init_df = get_df('astig')
default_date_start = init_df['DateTime'].min().strftime('%Y-%m-%d')
default_date_end = init_df['DateTime'].max().strftime('%Y-%m-%d')
default_obsnum_start = int(init_df['ObsNum'].min())
default_obsnum_end = int(init_df['ObsNum'].max())
default_select_receivers = init_df['Receiver'].unique()
default_select_receivers = [receiver for receiver in default_receivers if pd.notna(receiver)]
default_x_axis = 'ObsNum'
default_fields = astig_fields
# Load the data from a CSV file



# dash layout components
date_selector = html.Div([
                    dbc.Row(html.H5('Select Date Range')),
                    dcc.DatePickerRange(
                        id='date-picker-range',
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
                            dbc.Col(dbc.Checklist(id='receiver',options=[
                                {'label': i, 'value': i} for i in default_receivers
                            ]), width='auto'),
                ], className='mb-3'),

x_axis_selector = html.Div([
                                dbc.Col(html.H5('Select X-axis'), width='auto'),
                                dbc.Col(dcc.Dropdown(id='x-axis',options=['ObsNum','Time'],value='ObsNum'), width='auto'),
                    ], className='mb-3'),

y_axis_selector = html.Div([
                                dbc.Col(html.H5('Select fields to plot'), width='auto'),
                                dbc.Col(dcc.Dropdown(id='y-axis', multi=True,options=default_fields, value=default_fields), width='auto'),
                    ], className='mt-3 mb-3'),

filter_button = html.Div([
                    dbc.Row([
                        dbc.Col(dbc.Button('Filter Data', color='primary', id='filter_btn'), width='auto'),
                        dbc.Col(dbc.Button('Reset Filter', color='primary', id='reset_btn'), width='auto'),
                    ])
                ], className='mb-3')


def make_plot(tab, date_start, date_end, obsnum_start, obsnum_end, receivers, x_axis, selected_fields):
    # Get the dataframe
    df = get_df(tab)

    # Check if x_axis and selected_fields are in the dataframe
    if x_axis not in df.columns:
        raise KeyError(f"X-axis '{x_axis}' does not exist in the dataframe.")

    if not all(field in df.columns for field in selected_fields):
        invalid_fields = [field for field in selected_fields if field not in df.columns]
        raise KeyError(f"The following selected fields are invalid: {', '.join(invalid_fields)}")

    # Apply filters
    mask_date = (df['DateTime'] >= date_start) & (df['DateTime'] <= date_end)
    df_date = df[mask_date]
    if receivers and len(receivers) > 0:
        df_date = df_date[df_date['Receiver'].isin(receivers)]

    mask_obsnum = (df_date['ObsNum'] >= obsnum_start) & (df_date['ObsNum'] <= obsnum_end)
    df = df_date[mask_obsnum]

    # If no selected fields, return an empty plot with an annotation
    if not selected_fields:
        fig = go.Figure()
        fig.add_annotation(text='No data selected', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)
        return fig

    # Set row heights and create subplots
    num_rows = len(selected_fields)
    min_row_height = 200
    total_height = num_rows * min_row_height
    x_axis = 'DateTime' if x_axis == 'Time' else x_axis
    # Create subplots with shared x-axes
    if num_rows == 1:
        # Single subplot case
        fig = go.Figure(
            go.Scatter(x=df[x_axis], y=df[selected_fields[0]], mode='markers')
        )
        fig.update_yaxes(title_text=f'{selected_fields[0]}')
    else:
        # Multiple subplot case
        fig = make_subplots(
            rows=num_rows, cols=1, row_heights=[1] * num_rows, vertical_spacing=0.05
        )

        for idx, y in enumerate(selected_fields, start=1):
            fig.add_trace(go.Scatter(x=df[x_axis], y=df[y], mode='markers'), row=idx, col=1)
            fig.update_yaxes(title_text=f'{y}', row=idx, col=1)
        fig.update_layout(height=total_height, showlegend=False)

    return fig


fig_init = make_plot(default_tab, default_date_start, default_date_end, default_obsnum_start, default_obsnum_end,
                     default_select_receivers, default_x_axis, default_fields)


app.layout = dbc.Container([
     html.H1('Log Data'),
        html.Br(),
    dcc.Store(id='data-store', data={'astig': astig_fields, 'focus': focus_fields_default, 'point': point_fields_default}),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                [
                    dbc.Row(date_selector, className='mb-3'),
                    dbc.Row(obsnum_selector),
                    dbc.Row(receiver_selector),
                    dbc.Row(x_axis_selector),
                    dbc.Row(filter_button),

                ], style={'padding': '10px', 'height': '75vh',
                          'overflow-y': 'auto'
                          }
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
                            id="tabs", active_tab=default_tab,
                        ),
                        html.Div([
                            dbc.Row(y_axis_selector),
                            html.Div(id="content", children = dcc.Graph(figure=fig_init))]),
                    ]),
                ], style={'padding': '10px', 'height': '75vh',
                        'overflow-y': 'auto'
                          }
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
    Output('y-axis', 'options'),
    Output('y-axis', 'value'),
    Input('tabs', 'active_tab'),
    Input('reset_btn', 'n_clicks'),
    State('data-store', 'data'),
)
def update_filter_range(at, n, data_store):
    if not at:  # If the active_tab is None, don't update anything
        raise PreventUpdate

    # Try to fetch and prepare the dataframe
    try:
        df = get_df(at)
        if 'DateTime' in df.columns and 'ObsNum' in df.columns and 'Receiver' in df.columns:
            receivers = df['Receiver'].unique()
            receivers = [receiver for receiver in receivers if pd.notna(receiver)]
            receiver_options = [{'label': i, 'value': i, 'disabled': i not in receivers} for i in default_receivers]

            if at == "astig":
                fields = astig_fields
            elif at == "focus":
                fields = focus_fields
            else:
                fields = point_fields

            y_axis = data_store[at]
            fields_options = [{'label': i, 'value': i} for i in fields]

            start_date = df['DateTime'].min().strftime('%Y-%m-%d')
            end_date = df['DateTime'].max().strftime('%Y-%m-%d')
            start_obsnum = int(df['ObsNum'].min())
            end_obsnum = int(df['ObsNum'].max())


            return (start_date, end_date, start_obsnum, end_obsnum,
                    receiver_options, receivers, fields_options, y_axis)
        else:
            raise ValueError("Necessary columns are missing in the dataframe")
    except Exception as e:
        print(f"Error updating date range for tab {at}: {e}")
        raise PreventUpdate

@app.callback(
    Output('data-store','data'),
    Input('y-axis', 'value'),
    State('tabs','active_tab'),
    State('data-store','data')
)
def field_save(fields, tab, data):
    if tab == 'astig':
        data['astig'] = fields
    elif tab == 'focus':
        data['focus'] = fields
    else:
        data['point'] = fields
    return data

@app.callback(
    Output("content", "children"),
    Input("tabs", "active_tab"),
    Input('filter_btn', 'n_clicks'),
    Input('y-axis', 'value'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('obsnum-start', 'value'),
    State('obsnum-end', 'value'),
    State('receiver', 'value'),
    State('x-axis', 'value'),

)
def switch_tab(at, n, selected_fields,start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis):
    if not at:
        raise PreventUpdate

    if selected_fields is None:
        selected_fields = []
    elif not isinstance(selected_fields, list):
        selected_fields = [selected_fields]
    try:
        plot_figure = make_plot(at,start_date,end_date,obsnum_start,obsnum_end,receivers,x_axis, selected_fields)
        return dcc.Graph(figure=plot_figure)
    except Exception as e:
        print(f"Error updating tab {at}: {e}")
        raise PreventUpdate



if __name__ == '__main__':
    app.run_server(debug=False)

