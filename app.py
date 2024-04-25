import dash
from dash import dcc, html, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
from layout import (get_df, astig_fields, focus_fields, point_fields, focus_fields_default, point_fields_default,
                    default_date_start,default_date_end, point_x_axis,astig_date_start, astig_date_end, focus_date_start,
                    focus_date_end, point_date_start, point_date_end,
                    default_receivers, default_tab, date_selector, obsnum_selector, receiver_selector, x_axis_selector,
                    y_axis_selector,filter_button, fig_init, make_plot)

prefix = '/lmtqldb/'

import flask
from flask import redirect, url_for, render_template_string, request
# Create a Dash app
server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,"https://use.fontawesome.com/releases/v5.8.1/css/all.css"],
                requests_pathname_prefix=prefix,routes_pathname_prefix=prefix,
                server = server, title='LMT QL DB',
                prevent_initial_callbacks="initial_duplicate", suppress_callback_exceptions=True
                )



app.layout = html.Div([
     html.H1('Log Data'),
        html.Br(),
    dcc.Store(id='data-store', data={'astig': astig_fields, 'focus': focus_fields_default, 'point': point_fields_default}),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                [
                    dbc.Row(date_selector),
                    dbc.Row(obsnum_selector),
                    dbc.Row(receiver_selector),
                    dbc.Row(filter_button),
                ], style={'padding': '10px', 'height': '75vh',
                          'overflow-y': 'auto'
                          }
            )
           ,width=3),

        dbc.Col(
            dbc.Card(
                [
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab(label="Astigmatism", tab_id="astig"),
                            dbc.Tab(label="Focus", tab_id="focus"),
                            dbc.Tab(label="Point", tab_id="point"),
                        ],
                            id="tabs", active_tab=default_tab,style={'font-size': '24px','font-weight': 'bold',
                                                                     'color': '#333','border-bottom': '2px solid #ccc',
                                                                     'padding': '10px'}
                        ),
                        html.Div([
                            dbc.Row([dbc.Col(x_axis_selector),dbc.Col(y_axis_selector)],className='mt-3'),

                            html.Div(id="content", children = dcc.Graph(figure=fig_init)),
                            dbc.FormText('Tip: Click the start or end point of the x-axis and y-axis to change the range',)
                        ]),
                    ]),
                ], style={'padding': '10px', 'height': '75vh',
                        'overflow-y': 'auto'
                          }
            ),width=9
        )
    ])

 ], style={'padding': '20px'})


# get the date range and obsnum range from the csv file
@app.callback(
    Output('date-picker-range', 'start_date',allow_duplicate=True),
    Output('date-picker-range', 'end_date',allow_duplicate=True),
    Output('obsnum-start', 'value'),
    Output('obsnum-end', 'value'),
    Output('receiver', 'options'),
    Output('receiver', 'value'),
    Output('x-axis', 'options'),
    Output('x-axis', 'value'),
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
                x_axis_options = ['ObsNum','Time']
                x_axis = 'ObsNum'
            elif at == "focus":
                fields = focus_fields
                x_axis_options = ['ObsNum','Time']
                x_axis = 'ObsNum'
            else:
                fields = point_fields
                x_axis_options = point_x_axis
                x_axis = 'ObsNum'

            y_axis = data_store[at]
            fields_options = [{'label': i, 'value': i} for i in fields]

            start_obsnum = int(df['ObsNum'].min())
            end_obsnum = int(df['ObsNum'].max())


            return (default_date_start, default_date_end, start_obsnum, end_obsnum,
                    receiver_options, receivers, x_axis_options,x_axis, fields_options, y_axis)
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
    Output("content", "children",allow_duplicate=True),
    Output('date-picker-range', 'start_date'),
    Output('date-picker-range', 'end_date'),
    Input("tabs", "active_tab"),
    # Input('filter_btn', 'n_clicks'),
    Input('x-axis', 'value'),
    Input('y-axis', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('obsnum-start', 'value'),
    Input('obsnum-end', 'value'),
    Input('receiver', 'value'),
    Input('prev-week', 'n_clicks'),
    Input('next-week', 'n_clicks'),
    Input('prev-month', 'n_clicks'),
    Input('next-month', 'n_clicks'),
    Input('prev-year', 'n_clicks'),
    Input('next-year', 'n_clicks'),
    Input('all-data', 'n_clicks'),
    Input('today', 'n_clicks'),

)
def switch_tab(at, x_axis,selected_fields,start_date, end_date, obsnum_start, obsnum_end, receivers,
               prev_week, next_week, prev_month, next_month, prev_year, next_year,all_data, today):
    if not at:
        raise PreventUpdate

    if ctx.triggered_id == 'prev-month':
        start_date = pd.to_datetime(start_date) - pd.DateOffset(months=1)
        end_date = pd.to_datetime(end_date) - pd.DateOffset(months=1)

    elif ctx.triggered_id == 'next-month':
        start_date = pd.to_datetime(start_date) + pd.DateOffset(months=1)
        end_date = pd.to_datetime(end_date) + pd.DateOffset(months=1)

    elif ctx.triggered_id == 'prev-week':
        start_date = pd.to_datetime(start_date) - pd.DateOffset(weeks=1)
        end_date = start_date + pd.DateOffset(weeks=1)

    elif ctx.triggered_id == 'next-week':
        start_date = pd.to_datetime(start_date) + pd.DateOffset(weeks=1)
        end_date = pd.to_datetime(end_date) + pd.DateOffset(weeks=1)

    elif ctx.triggered_id == 'prev-year':
        start_date = pd.to_datetime(start_date) - pd.DateOffset(years=1)
        end_date = start_date + pd.DateOffset(years=1)

    elif ctx.triggered_id == 'next-year':
        start_date = pd.to_datetime(start_date) + pd.DateOffset(years=1)
        end_date = start_date + pd.DateOffset(years=1)

    elif ctx.triggered_id == 'all-data':
        if at == 'astig':
            start_date = astig_date_start
            end_date = astig_date_end
        elif at == 'focus':
            start_date = focus_date_start
            end_date = focus_date_end
        elif at == 'point':
            start_date = point_date_start
            end_date = point_date_end

    elif ctx.triggered_id == 'today':
        # set start_date to today
        start_date = pd.to_datetime(datetime.datetime.now().date())
        end_date = start_date

    if selected_fields is None:
        selected_fields = []
    elif not isinstance(selected_fields, list):
        selected_fields = [selected_fields]
    try:
        plot_figure = make_plot(at,start_date,end_date,obsnum_start,obsnum_end,receivers,x_axis, selected_fields)
        return dcc.Graph(figure=plot_figure), start_date, end_date
    except Exception as e:
        print(f"Error updating tab {at}: {e}")
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=False)

