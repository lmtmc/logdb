# Definine constants
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import datetime
from datetime import timedelta, datetime

# Define styles
NUMBER_INPUT_STYLE = {'width': '100px', 'height': '30px', 'textAlign': 'center'}
PLOT_STYLE= {'min-height':'800px', 'margin': '0px', 'padding': '0px', 'border': '1px solid black',
              # 'overflow-y':'auto',
              'padding':'5px'}
#Define constants
ASTIG_FIELDS = ['M1ZC0']
FOCUS_FIELDS = ['M2XOffset', 'M2YOffset', 'M2ZOffset']
POINT_FIELDS = [
    'AzPointOffset', 'ElPointOffset', 'Flag', 'FitFlag', 'FitRegion', 'PeakValue', 'PeakError', 'AzMapOffset',
    'ElMapOffset', 'AzMapOffsetError', 'ElMapOffsetError', 'AzHpbw', 'ElHpbw', 'AzHpbwError', 'ElHpbwError',
    'PeakSnrValue', 'PeakSnrError', 'PixelList'
]
# Get a pandas dataframe from a CSV file
def get_df(csv_file):
    df = pd.read_csv(f'./lmtqldb/{csv_file}.csv')
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    return df
# Get the fields for a given name
def get_fields(name):
    if name == 'astig':
        fields = ASTIG_FIELDS
    elif name == 'focus':
        fields = FOCUS_FIELDS
    elif name == 'point':
        fields = POINT_FIELDS
    return fields

# Get the range of the data
def get_range(name):
    df = get_df(name)
    return df['ObsNum'].min(), df['ObsNum'].max(), df['DateTime'].min(), df['DateTime'].max()

def adjust_date_range(triggered_id,start_date,end_date):
    triggered_id = triggered_id.split('-',1)[1]
    if triggered_id == 'last-month':
        end_date = pd.to_datetime(start_date)
        start_date = end_date - pd.DateOffset(months=1)

    elif triggered_id == 'next-month':

        start_date = pd.to_datetime(end_date)
        end_date = start_date + pd.DateOffset(months=1)

    elif triggered_id == 'last-week':
        end_date = pd.to_datetime(start_date)
        start_date = end_date - pd.DateOffset(weeks=1)

    elif triggered_id == 'next-week':
        start_date = pd.to_datetime(end_date)
        end_date = pd.to_datetime(start_date) + pd.DateOffset(weeks=1)

    elif triggered_id == 'last-year':
        end_date = pd.to_datetime(start_date)
        start_date = end_date - pd.DateOffset(years=1)

    elif triggered_id == 'next-year':
        start_date = pd.to_datetime(end_date)
        end_date = start_date + pd.DateOffset(years=1)

    elif triggered_id == 'all-data':
        start_date = get_range('astig')[2]
        end_date = get_range('astig')[3]

    elif triggered_id == 'this-week':
        # set start_date to today
        end_date = pd.to_datetime(datetime.now().date())
        start_date = end_date - pd.DateOffset(weeks=1)
    return start_date, end_date

point_x_axis = ['ObsNum', 'Time', 'Telescope_AzDesPos', 'Telescope_ElDesPos', 'AzPointOffset']
focus_fields_default = FOCUS_FIELDS[2]
point_fields_default = POINT_FIELDS[0:2]
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

# Lighter outline color style
lighter_outline_style = {
    'padding': '0px',
    'width': '20px',
    'margin': '0',
     'height': '20px',
    'border-radius': '0',
    'border-color': '#c0c0c0',  # Light gray color for the outline
}

# Define the row of buttons with the lighter outline style
def create_time_buttons(name):
    return dbc.Row(
    [

        dbc.Col(
            dbc.Button(
                html.I(className='fas fa-calendar-alt'),
                id=f'{name}-this-week',
                title='This Week',
                style=lighter_outline_style,
                outline=True,
            ),
            width='auto',
            style={'padding': '0', 'margin': '0'},
        ),
        # Last Week
        dbc.Col(
            dbc.Button(
                html.I(className='fas fa-calendar-week'),
                id=f'{name}-last-week',
                title='Last Week',
                style=lighter_outline_style,
                outline=True,
            ),
            width='auto',
            style={'padding': '0', 'margin': '0'},
        ),

        # Next Week
        dbc.Col(
            dbc.Button(
                html.I(className='fas fa-calendar-plus'),
                id=f'{name}-next-week',
                title='Next Week',
                style=lighter_outline_style,
                outline=True,
            ),
            width='auto',
            style={'padding': '0', 'margin': '0'},
        ),

        # Previous Month
        dbc.Col(
            dbc.Button(
                html.I(className='fas fa-arrow-left'),
                id=f'{name}-last-month',
                title='Previous Month',
                style=lighter_outline_style,
                outline=True,
            ),
            width='auto',
            style={'padding': '0', 'margin': '0'},
        ),

        # Next Month
        dbc.Col(
            dbc.Button(
                html.I(className='fas fa-arrow-right'),
                id=f'{name}-next-month',
                title='Next Month',
                style=lighter_outline_style,
                outline=True,
            ),
            width='auto',
            style={'padding': '0', 'margin': '0'},
        ),

        # Previous Year
        dbc.Col([
            dbc.Button(
                html.I(className='fas fa-angle-double-left'),
                id=f'{name}-last-year',
                title='Previous Year',
                style=lighter_outline_style,
                color='secondary',
                outline=True,
            ),
        ], width='auto',
            style={'padding': '0', 'margin': '0'},
        ),

        # Next Year
        dbc.Col(
            dbc.Button(
                html.I(className='fas fa-angle-double-right'),
                id=f'{name}-next-year',
                title='Next Year',
                style=lighter_outline_style,
                outline=True,
            ),
            width='auto',
            style={'padding': '0', 'margin': '0'},
        ),
        dbc.Col(
            dbc.Button(
                html.I(className='fas fa-calendar-day'),
                id=f'{name}-all-data',
                title='All Time',
                style=lighter_outline_style,
                outline=True,
            ),
            width='auto',
            style={'padding': '0', 'margin': '0'},
        ),
        dbc.Col(
            dbc.Button(
                [html.I(className='fas solid fa-plus'),],

            id=f'{name}-another-range',
            title='Add Another Range to Compare',
            style=lighter_outline_style,
            outline=True,)
        ),

    ],
    style={'padding': '0', 'margin': '0'}, justify='end'
)

def create_compare_modal(name):
    return dbc.Modal(
    [
        dbc.ModalHeader(html.H5(f"Compare Date Range for {name} Plot", style={'textAlign': 'center'})),
        dbc.ModalBody(
            [
                dbc.Row([
                    dbc.Col(dbc.Label('Date Range1'), width='auto'),
                    dbc.Col(
                        dcc.DatePickerRange(
                            id=f'{name}-compare-date-picker-range1',
                            display_format='YYYY-MM-DD',
                            start_date_placeholder_text='Start Date',
                            end_date_placeholder_text='End Date',
                            start_date=datetime.now() - timedelta(days=7),
                            end_date=datetime.now(),
                            persistence=True,  # Enable persistence if required
                            persistence_type='session',  # Persist in session
                            className='datepicker__input'
                        ),width='auto'
                    ),
                    dbc.Col(dbc.Label('Date Range2'), width='auto'),
                    dbc.Col(
                        dcc.DatePickerRange(
                            id=f'{name}-compare-date-picker-range2',
                            display_format='YYYY-MM-DD',
                            start_date_placeholder_text='Start Date',
                            end_date_placeholder_text='End Date',
                            start_date=datetime.now() - timedelta(days=7),
                            end_date=datetime.now(),
                            persistence=True,  # Enable persistence if required
                            persistence_type='session',  # Persist in session
                            className='datepicker__input'
                        ), width='auto'
                    ),
                    dbc.Col(dbc.Button('Apply/Refresh', id=f'{name}-compare-btn', color='primary', className='ml-auto'),
                            width='auto')


                ], align='center'),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=go.Figure(), id=f'{name}-compare-plot1')),
                    dbc.Col(dcc.Graph(figure=go.Figure(), id=f'{name}-compare-plot2'))]
                ),
            ]
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id=f"{name}-compare-modal-close", className="ml-auto")
        ),
    ],
    id=f"{name}-compare-modal",
    size='xl',
)


def get_receivers(name):
    if name == 'astig':
        receivers = [default_receivers[i] for i in [1,5,6,9,10]
                        ]
    elif name == 'focus':
        receivers = [default_receivers[i] for i in [1,2,3,5,6,7,9,10]]
    elif name == 'point':
        receivers = default_receivers
    return receivers

def get_obsnum_range(name):
    df = get_df(name)
    return int(df['ObsNum'].min()), int(df['ObsNum'].max())

def make_plot(name, date_start, date_end, obsnum_start, obsnum_end, receivers, x_axis, selected_fields):
    if selected_fields is None:
        selected_fields = []
    if not isinstance(selected_fields, list):
        selected_fields = [selected_fields]
    # Get the dataframe
    df = get_df(name)
    if x_axis == 'Telescope_AzDesPos' or x_axis == 'Telescope_ElDesPos' or x_axis == 'ElPointOffset':
        df = get_df('point_tel')
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
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(
            go.Scatter(x=df[x_axis], y=df[selected_fields[0]], mode='markers')
        )
        fig.update_yaxes(title_text=f'{selected_fields[0]}')
        fig.update_xaxes(title_text=f'{x_axis}')
    else:
        # Multiple subplot case
        fig = make_subplots(
            rows=num_rows, cols=1, row_heights=[1] * num_rows, vertical_spacing=0.05,shared_xaxes=True,
        )

        for idx, y in enumerate(selected_fields, start=1):
            fig.add_trace(go.Scatter(x=df[x_axis], y=df[y], mode='markers'), row=idx, col=1)
            fig.update_yaxes(title_text=f'{y}', row=idx, col=1)
        fig.update_xaxes(title_text=f'{x_axis}', row=num_rows, col=1)
        fig.update_layout(height=total_height, showlegend=False, margin=dict(l=50, r=50, t=50, b=50))

    fig.update_xaxes(rangeslider_visible=True,
                     rangeselector=dict(
                         buttons=list([
                             dict(count=7, label="1w", step="day", stepmode="backward"),
                             dict(count=6, label="1m", step="month", stepmode="backward"),
                             dict(count=1, label="YTD", step="year", stepmode="todate"),
                             dict(count=1, label="1y", step="year", stepmode="backward"),
                             dict(step="all")
                         ])
                     ),row=num_rows, col=1)

    return fig
# dash layout components

def make_compare_plot(name, start_date, end_date, compare_start_date, compare_end_date, obsnum_start, obsnum_end, receivers, x_axis, y_axis):
    title1 = f'{pd.to_datetime(start_date).date()} to {pd.to_datetime(end_date).date()} '
    title2 = f'{pd.to_datetime(start_date).date()} to {pd.to_datetime(compare_end_date).date()}'
    fig = make_subplots(rows=1, cols=2, subplot_titles=(title1, title2))
    fig.add_trace(make_plot(name, start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, y_axis).data[0],
                  row=1, col=1)
    fig.add_trace(make_plot(name, compare_start_date, compare_end_date, obsnum_start, obsnum_end, receivers, x_axis,
                            y_axis).data[0], row=1, col=2)
    fig.update_layout(showlegend=False)
    return fig
def create_date_selector(name):
    return html.Div([
        dbc.Row([
            dbc.Col(dbc.Label('Date'), width=2),
            dbc.Col(
                dcc.DatePickerRange(
                    id=f'{name}-date-picker-range',
                    display_format='YYYY-MM-DD',
                    start_date_placeholder_text='Start Date',
                    end_date_placeholder_text='End Date',
                    start_date=datetime.now() - timedelta(days=7),
                    end_date=datetime.now(),
                    persistence=True,  # Enable persistence if required
                    persistence_type='session',  # Persist in session
                    className='datepicker__input'
                ),width='auto'
            ),
            dbc.Col(create_time_buttons(name)),
        ], align='center'),
    ], className='mb-1')
def create_obsnum_selector(name):
    return html.Div([
                            dbc.Row([
                                dbc.Col(dbc.Label('ObsNum'), width=2),
                                dbc.Col(dcc.Input(id=f'{name}-obsnum-start', type='number',style=NUMBER_INPUT_STYLE,
                                                  value=get_obsnum_range(name)[0]),width='auto'),
                                dbc.Col(dbc.Label('to'), width='auto', style={'textAlign': 'center'}),
                                dbc.Col(dcc.Input(id=f'{name}-obsnum-end', type='number',style=NUMBER_INPUT_STYLE,
                                        value=get_obsnum_range(name)[1]),width='auto'),
                            ],align='center'),
                        ], className='mb-1'
                    ),
def create_receiver_selector(name):
    return html.Div(dbc.Row([
                            dbc.Col(dbc.Label('Receivers'), width='auto'),
                            dbc.Col(dbc.Checklist(id=f'{name}-receiver',options=[
                                {'label': i, 'value': i} for i in get_receivers(name)
                            ], value=get_receivers(name), inline=True),),
                ]), ),

astig_plot = [
            html.Div([html.H5('Astigmatism Plot',style={'textAlign': 'center'}),

            html.Div([
                dbc.Row(create_date_selector('astig')),
                dbc.Row(create_obsnum_selector('astig')),
                dbc.Row(create_receiver_selector('astig')),
                dbc.Row([
                    dbc.Col(dbc.Label('x-axis'), width=2),
                    dbc.Col(dcc.Dropdown(id='astig-x-axis', options=['ObsNum', 'Time'], value='ObsNum'),width=10),
                ],className='mb-1'),
                dbc.Row([
                    dbc.Col(dbc.Label('y-axis'), width=2),
                    dbc.Col(dcc.Dropdown(id='astig-y-axis', multi=True, options=ASTIG_FIELDS,
                                     value=ASTIG_FIELDS[0]),width=10)])
            ]),
            dcc.Graph(figure=go.Figure(), id='astig-plot')],style=PLOT_STYLE),
            create_compare_modal('astig')
            ]

focus_plot = [
            html.Div([
                html.H5('Focus Plot',style={'textAlign': 'center'}),
            html.Div([dbc.Row(create_date_selector('focus')),
            dbc.Row(create_obsnum_selector('focus')),
            dbc.Row(create_receiver_selector('focus')),
            dbc.Row([
                dbc.Col(dbc.Label('x-axis'), width=2),
                dbc.Col(dcc.Dropdown(id='focus-x-axis', options=['ObsNum', 'Time'], value='ObsNum')),
            ], className='mb-1'),
            dbc.Row([
                dbc.Col(dbc.Label('y-axis'), width=2),
                dbc.Col(dcc.Dropdown(id='focus-y-axis', multi=True, options=FOCUS_FIELDS,
                                     value=focus_fields_default))
            ],
                className='mb-1')]),
            dcc.Graph(figure=go.Figure(), id='focus-plot')],style=PLOT_STYLE),
            create_compare_modal('focus')

]

point_plot = [
            html.Div([
                html.H5('Point Plot',style={'textAlign': 'center'}),
            html.Div([dbc.Row(create_date_selector('point')),
            dbc.Row(create_obsnum_selector('point')),
            dbc.Row(create_receiver_selector('point')),
            dbc.Row([
                dbc.Col(dbc.Label('x-axis'), width=2),
                dbc.Col(dcc.Dropdown(id='point-x-axis', options=point_x_axis, value='ObsNum')),
            ], className='mb-1'),
            dbc.Row([
                dbc.Col(dbc.Label('y-axis'), width=2),
                dbc.Col(dcc.Dropdown(id='point-y-axis', multi=True, options=POINT_FIELDS,
                                     value=point_fields_default))
            ],
                className='mb-1')]),
            dcc.Graph(figure=go.Figure(), id='point-plot')],style=PLOT_STYLE),
            create_compare_modal('point')
        ]

