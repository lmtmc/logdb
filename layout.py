# Definine constants
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import datetime
from datetime import timedelta, datetime
import os
import concurrent.futures

# Define styles
title_style = {'textAlign': 'center', 'margin': '10px','backgroundColor': '#17a2b8',}
NUMBER_INPUT_STYLE = {'width': '100px', 'height': '30px', 'textAlign': 'center'}
PLOT_STYLE= {'margin': '0px', 'backgroundColor': '#f8f9fa', 'padding':'10px'}
# Lighter outline color style
lighter_outline_style = {
    'padding': '0px',
    'width': '20px',
    'margin': '0',
     'height': '20px',
    'borderColor': '#c0c0c0',  # Light gray color for the outline
}
#Define constants
clean_base_dir = '/home/lmtmc/lmtqldb/cleaned_data'
raw_base_dir = '/raw/lmtqldb'
#
# clean_base_dir = '/home/lmt/raw_data/lmtqldb/cleaned_data'
# raw_base_dir = '/home/lmt/raw_data/lmtqldb/raw_data'
index_dir = os.path.join(clean_base_dir, 'index')
folder_paths = {
        'astigmatism': f'{clean_base_dir}/astigmatism_cleaned',
        'focus': f'{clean_base_dir}/focus_cleaned',
        'pointing': f'{clean_base_dir}/pointing_cleaned',
        'tel': f'{raw_base_dir}/tel',
    }

astig_fields = ['M1ZC0']
focus_fields = ['M2XOffset', 'M2YOffset', 'M2ZOffset']
pointing_fields = [
    'AzPointOffset', 'ElPointOffset', 'Flag', 'FitFlag', 'FitRegion', 'PeakValue', 'PeakError', 'AzMapOffset',
    'ElMapOffset', 'AzMapOffsetError', 'ElMapOffsetError', 'AzHpbw', 'ElHpbw', 'AzHpbwError', 'ElHpbwError',
    'PeakSnrValue', 'PeakSnrError', 'PixelList'
]
pointing_x_axis = ['ObsNum', 'Time', 'Telescope_AzDesPos', 'Telescope_ElDesPos', 'AzPointOffset']
astig_fields_default = astig_fields[0]
focus_fields_default = focus_fields[2]
pointing_fields_default = pointing_fields[0:2]
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


def create_index_file(folder_path, index_filename):
    index_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            try:
                parts = filename.split('_')

                if 'tel' in folder_path:
                    date_str = parts[1].split('.')[0] if len(parts) > 1 else None
                else:
                    date_str = parts[2].split('.')[0] if len(parts) > 2 else None

                if date_str is None:
                    print(f"Error processing file {filename}: Unable to extract date part")
                    continue

                file_date = pd.to_datetime(date_str, format='%Y-%m-%d', errors='coerce')
                if pd.isnull(file_date):
                    print(f"Error processing file {filename}: Invalid date format")
                    continue

                index_data.append([filename, file_date])
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue

    if index_data:
        index_df = pd.DataFrame(index_data, columns=['filename', 'file_date'])
        index_df = index_df.sort_values(by='file_date').reset_index(drop=True)
        # Ensure the directory exists
        os.makedirs(index_dir, exist_ok=True)
        index_df.to_csv(os.path.join(index_dir, index_filename), index=False)
    else:
        print(f"No valid files found in {folder_path}")
def create_index_files():
    for folder_key, folder_path in folder_paths.items():
        create_index_file(folder_path, f'{folder_key}.csv')

create_index_files()
def load_data(folder_path, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if 'astigmatism' in folder_path:
        index_filename = 'astigmatism.csv'
    elif 'focus' in folder_path:
        index_filename = 'focus.csv'
    elif 'pointing' in folder_path:
        index_filename = 'pointing.csv'
    elif 'tel' in folder_path:
        index_filename = 'tel.csv'
    else:
        raise ValueError(f"Invalid folder_path: {folder_path}")

    index_df = pd.read_csv(os.path.join(index_dir, index_filename))
    index_df['file_date'] = pd.to_datetime(index_df['file_date'])

    valid_files = index_df[(index_df['file_date'] >= start_date) & (index_df['file_date'] <= end_date)][
        'filename'].tolist()
    def read_and_process_file(filename):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)
        if not df.empty:
            df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        return df

    with concurrent.futures.ThreadPoolExecutor() as executor:
        dataframes = list(executor.map(read_and_process_file, valid_files))

    dataframes = [df for df in dataframes if not df.empty]

    if not dataframes:
        return pd.DataFrame()

    return pd.concat(dataframes, ignore_index=True)

def get_dates(name):
    if name == 'astig':
       name = 'astigmatism'
    index_filename = f'{name}.csv'
    index_df = pd.read_csv(os.path.join(index_dir, index_filename))
    dates = index_df['file_date'].tolist()
    dates.reverse()
    return dates

def get_df(name, start_date, end_date):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    if name == 'astig':
       name = 'astigmatism'

    df_main = load_data(folder_paths[name], start_date, end_date)
    if df_main.empty:
        return pd.DataFrame()

    df_tel = load_data(folder_paths['tel'], start_date, end_date)

    if df_tel.empty:
        return pd.DataFrame()

    df_tel = df_tel.drop_duplicates(subset='ObsNum', keep='first')
    required_columns = ['ObsNum', 'Telescope_AzDesPos', 'Telescope_ElDesPos']
    if not all(col in df_tel.columns for col in required_columns):
        print(f"Required columns not found in df_tel: {required_columns}")
        return pd.DataFrame()

    df_tel = df_tel[required_columns]
    df = pd.merge(df_main, df_tel, on='ObsNum', how='inner')
    if df.empty:
        return pd.DataFrame()
    df['Telescope_AzDesPos'] = df['Telescope_AzDesPos']*180/3.14159
    df['Telescope_ElDesPos'] = df['Telescope_ElDesPos']*180/3.14159

    return df


# Get the fields for a given name
def get_fields(name):
    fields_var_name = f'{name}_fields'
    fields = globals().get(fields_var_name, [])
    return fields


def get_x_axis(name):
    if name == 'astig' or name == 'focus':
        return ['ObsNum','Time','Telescope_AzDesPos']
    elif name == 'pointing':
        return pointing_x_axis

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

    elif triggered_id == 'this-week':
        # set start_date to today
        end_date = pd.to_datetime(datetime.now().date())
        start_date = end_date - pd.DateOffset(weeks=1)
    return start_date, end_date



def create_title(title, name):
    return html.Div(
        dbc.Row(
            [
                dbc.Col(html.H5(title), width='auto', lg=6, md=6, sm=12),  # Adjust widths as needed
                dbc.Col(
                    dbc.Button(
                        [html.I(className='fas fa-plus'),'Compare Plot'],  # Assuming 'solid' is a typo
                        id=f'{name}-another-range',
                        title='Add Another Range to Compare',
                        style={'color': '#17a2b8', 'backgroundColor': 'white'},
                    ),
                    width='auto'
                ),

            ],
            style=title_style,  # Ensure this style supports side-by-side layout
            align='center',
        )
    )

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
        # Previous Week
        dbc.Col(
            dbc.Button(
                html.I(className='fas fa-calendar-week'),
                id=f'{name}-last-week',
                title='Previous Week',
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

    ],
    style={'padding': '0', 'margin': '0'}, justify='end'
)

def create_obsnum_selector(name):
    return html.Div([
                            dbc.Row([
                                dbc.Col(dbc.Label('ObsNum'), width='auto'),
                                dbc.Col(dcc.Input(id=f'{name}-obsnum-start', type='number',style=NUMBER_INPUT_STYLE,
                                                  value=get_obsnum_range(name,datetime.now() - timedelta(days=7), datetime.now())[0]
                                                  ),
                                        width='auto'),
                                dbc.Col(dbc.Label('to'), width='auto', style={'textAlign': 'center'}),
                                dbc.Col(dcc.Input(id=f'{name}-obsnum-end', type='number',style=NUMBER_INPUT_STYLE,
                                        value=get_obsnum_range(name,datetime.now() - timedelta(days=7), datetime.now())[1]
                                                  ),width='auto'),
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

def create_filter(name):
    value = globals().get(f'{name}_fields_default', [])
    if not isinstance(value, list):
        value = [value]
    return html.Div([
                    dbc.Row([
                        dbc.Col(create_obsnum_selector(name), width='auto'),
                        dbc.Col(create_receiver_selector(name), width='auto')],className='mb-1'),
                    dbc.Row([

                        dbc.Col(dbc.Label('y-axis'), width='auto'),
                        dbc.Col(dcc.Dropdown(id=f'{name}-compare-y-axis', multi=True, options=get_fields(name), value=value))],className='mb-1'),
                    ]),
def create_compare_modal(name):
    return dbc.Modal(
    [
        dbc.ModalHeader(html.H5(f"Compare {name.capitalize()} Plot")),
        dbc.ModalBody(
            [
                dbc.Row(dbc.Col([
                    dbc.Label('Select Dates'), dcc.Dropdown(
                    id=f'{name}-multi-date-picker',
                    options=[{'label': date, 'value': date} for date in get_dates(name)],
                        value=get_dates(name)[0],
                    multi=True
                    )]),className='mb-3'),
                dbc.Row(create_filter(name)),
                dbc.Row([
                    dbc.Col(dcc.Loading(dcc.Graph(figure=go.Figure(), id=f'{name}-compare-plot1'))),
                   ]
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
    elif name == 'pointing':
        receivers = default_receivers
    return receivers

def get_obsnum_range(name, start_date, end_date):
    df_astig = get_df('astig', start_date, end_date)
    df_focus = get_df('focus', start_date, end_date)
    df_pointing = get_df('pointing', start_date, end_date)
    df_dict = {
        'astig': df_astig,
        'focus': df_focus,
        'pointing': df_pointing,
    }

    obsnum_start_list = []
    obsnum_end_list = []

    # Check if DataFrame is not empty before accessing 'ObsNum'
    for key, df in df_dict.items():
        if not df.empty:
            obsnum_start_list.append(df['ObsNum'].min())
            obsnum_end_list.append(df['ObsNum'].max())

    # If no valid 'ObsNum' values are found, return None or appropriate default values
    if not obsnum_start_list or not obsnum_end_list:
        return None, None

    obsnum_start = min(obsnum_start_list)
    obsnum_end = max(obsnum_end_list)
    if name in df_dict:
        return df_dict[name]['ObsNum'].min(), df_dict[name]['ObsNum'].max()
    elif name == 'same':
        return obsnum_start, obsnum_end

def apply_filters(df, receivers, obsnum_start, obsnum_end):
    if receivers and len(receivers) > 0:
        df = df[df['Receiver'].isin(receivers)]
    mask_obsnum = (df['ObsNum'] >= obsnum_start) & (df['ObsNum'] <= obsnum_end)
    df = df[mask_obsnum]
    return df

def make_plot(name, date_start, date_end, obsnum_start, obsnum_end, receivers, x_axis, selected_fields):
    if selected_fields is None:
        selected_fields = []
    if not isinstance(selected_fields, list):
        selected_fields = [selected_fields]
    # Get the dataframe
    df = get_df(name,date_start,date_end)
    if not selected_fields or not x_axis or x_axis not in df.columns or df.empty:
        fig = go.Figure()
        fig.add_annotation(text='No data selected', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)
        return fig

    # Apply filters
    df = apply_filters(df, receivers, obsnum_start, obsnum_end)
    if df.empty:
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
    return fig
# dash layout components

def make_compare_plot(modal_type, dates, obsnum_start, obsnum_end, receivers, y_axis):
    fig = go.Figure()
    for date in dates:
        df = get_df(modal_type, date, date)
        if df.empty:
            continue
        df = apply_filters(df, receivers, obsnum_start, obsnum_end)
        if df.empty:
            continue
        for y in y_axis:
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(df['Time']),
                y=df[y],
                mode='lines+markers',
                name=f'{date} {y}'))
    fig.update_layout(showlegend=True,
                      xaxis=dict(
                          tickmode='array',
                          # tickvals=[i for i in range(0, 12, 2)],
                          # ticktext=[f'{i}:00' for i in range(0, 12, 2)],
                          type='date',
                          tickformat='%H:%M:%S',
                          title = 'Time of Day (UTC)',
                          range=[pd.to_datetime('00:00:00').strftime('%Y-%m-%d %H:%M:%S'),
                                 pd.to_datetime('12:00:00').strftime('%Y-%m-%d %H:%M:%S')]),
                      # yaxis=dict(title=f'{modal_type.capitalize()} (mm)'),
                      )
    return fig



# def make_compare_plot(name, start_date, end_date, compare_start_date, compare_end_date, obsnum_start, obsnum_end, receivers, x_axis, y_axis):
#     title1 = f'{pd.to_datetime(start_date).date()} to {pd.to_datetime(end_date).date()} '
#     title2 = f'{pd.to_datetime(start_date).date()} to {pd.to_datetime(compare_end_date).date()}'
#     fig = make_subplots(rows=1, cols=2, subplot_titles=(title1, title2))
#     fig.add_trace(make_plot(name, start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, y_axis).data[0],
#                   row=1, col=1)
#     fig.add_trace(make_plot(name, compare_start_date, compare_end_date, obsnum_start, obsnum_end, receivers, x_axis,
#                             y_axis).data[0], row=1, col=2)
#     fig.update_layout(showlegend=False)
#     return fig
def create_date_selector(name):
    return html.Div([
        dbc.Row([
            dbc.Col(dbc.Label('Date'), width='auto'),
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


def plot_content(name):
    value = globals().get(f'{name}_fields_default',[])
    if not isinstance(value, list):
        value = [value]
    return html.Div([
        html.Div([
            create_title(f'{name.capitalize()} Plot', name),
            dbc.Row([
            dbc.Col(dbc.Label('y-axis'), width='auto'),
            dbc.Col(dcc.Dropdown(id=f'{name}-y-axis', multi=True, options=get_fields(name),
                                 value=value)),
        ],className='mb-1'),
        dcc.Loading(dcc.Graph(figure=go.Figure(), id=f'{name}-plot'))], style=PLOT_STYLE),
        create_compare_modal(f'{name}')
    ])

plots = html.Div(dbc.Row([
    dbc.Col(plot_content('astig'), width=4),
    dbc.Col(plot_content('focus'), width=4),
    dbc.Col(plot_content('pointing'), width=4),]),
)

same_setting = html.Div(
    [
        dbc.Row([
            dbc.Col(create_date_selector('same'), width='auto'),
            dbc.Col(dbc.Label('ObsNum'), width='auto'),
            dbc.Col(dcc.Input(id='same-obsnum-start', type='number', style=NUMBER_INPUT_STYLE,

                              ), width='auto'),
            dbc.Col(dbc.Label('to'),width='auto'),
            dbc.Col(dcc.Input(id='same-obsnum-end', type='number', style=NUMBER_INPUT_STYLE,

                              ), width='auto'),
            dbc.Col(dbc.Label('Receivers'), width='auto'),
            dbc.Col(dbc.Checklist(id='same-receiver', options=get_receivers('pointing'), value=get_receivers('pointing'), inline=True)),
            dbc.Col(dbc.Label('x-axis'), width='auto'),
            dbc.Col(dcc.Dropdown(id='same-x-axis', options=pointing_x_axis, value='ObsNum'), width='2'),
        ]),

    ], style={'padding': '20px'})

title = dbc.Row(html.H5('LMT QL DB PLOTS', ),className='mb-3',style=title_style)