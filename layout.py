# Definine constants
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import timedelta, datetime

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

default_date_end = init_df['DateTime'].max().strftime('%Y-%m-%d')
# set the default date range to 30 days before the end date
default_date_start = (datetime.strptime(default_date_end, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
default_obsnum_start = int(init_df['ObsNum'].min())
default_obsnum_end = int(init_df['ObsNum'].max())
default_select_receivers = init_df['Receiver'].unique()
default_select_receivers = [receiver for receiver in default_receivers if pd.notna(receiver)]
default_x_axis = 'ObsNum'
default_fields = astig_fields
# Load the data from a CSV file

btn_style = {
    'font-size': '12px',
    'width': '120px',  # Fixed width for all buttons
    'text-align': 'center',  # Centering the text
}


# dash layout components
sub_date_selector = html.Div([
    dbc.Row([
        dbc.Col(dbc.Button('Previous Week', id='prev-week',outline=True, color='primary',style=btn_style)),
        dbc.Col(dbc.Button('Next Week',id='next-week',outline=True, color='primary',style=btn_style))], className='mb-3'),
    dbc.Row([
        dbc.Col(dbc.Button('Previous Month', id='prev-month', outline=True, color='primary', style=btn_style)),
        dbc.Col(dbc.Button('Next Month', id='next-month', outline=True, color='primary', style=btn_style))], className='mb-3'),
    dbc.Row([
        dbc.Col(dbc.Button('Previous Year', id='prev-year', outline=True, color='primary', style=btn_style)),
        dbc.Col(dbc.Button('Next Year', id='next-year', outline=True, color='primary', style=btn_style))], className='mb-3'),
],)


date_selector = html.Div([
                    dbc.Row(html.H5('Select Date Range')),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        display_format='YYYY-MM-DD',
                        start_date=default_date_start,
                        end_date=default_date_end,
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
                                dbc.Col(html.H5('Select x-axis'), width='auto'),
                                dbc.Col(dcc.Dropdown(id='x-axis',options=['ObsNum','Time'],value='ObsNum'), width='auto'),
                    ], ),

y_axis_selector = html.Div([
                                dbc.Col(html.H5('Select y-axis'), width='auto'),
                                dbc.Col(dcc.Dropdown(id='y-axis', multi=True,options=default_fields, value=default_fields), width='auto'),
                    ], ),

filter_button = html.Div([
                    dbc.Row([
                        # dbc.Col(dbc.Button('Filter Data', color='primary', id='filter_btn'), width='auto'),
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
            rows=num_rows, cols=1, row_heights=[1] * num_rows, vertical_spacing=0.05,shared_xaxes=True,
        )

        for idx, y in enumerate(selected_fields, start=1):
            fig.add_trace(go.Scatter(x=df[x_axis], y=df[y], mode='markers'), row=idx, col=1)
            fig.update_yaxes(title_text=f'{y}', row=idx, col=1)
        fig.update_layout(height=total_height, showlegend=False, margin=dict(l=50, r=50, t=50, b=50))



    return fig


fig_init = make_plot(default_tab, default_date_start, default_date_end, default_obsnum_start, default_obsnum_end,
                     default_select_receivers, default_x_axis, default_fields)