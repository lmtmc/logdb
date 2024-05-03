# todo update database automatically
import dash
from dash import html, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from layout import (astig_plot, focus_plot, point_plot, make_plot, adjust_date_range)

prefix = '/lmtqldb/'

import flask

# Create a Dash app
server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
                                                "https://codepen.io/chriddyp/pen/bWLwgP.css",
                                                "https://use.fontawesome.com/releases/v5.8.1/css/all.css"],
                requests_pathname_prefix=prefix,routes_pathname_prefix=prefix,
                server = server, title='LMT QL DB',
                prevent_initial_callbacks="initial_duplicate", suppress_callback_exceptions=True
                )

app.layout = html.Div([
    html.H5('LMT QL DB PLOTS', style={'textAlign': 'left', 'padding': '10px', 'font-weight': 'bold',
                                      'font-size': '30px', 'background-color': '#17a2b8', 'margin': '10px',}),
    html.Div(
        [
                dbc.Row([
                    dbc.Col(astig_plot, width=4),
                    dbc.Col(focus_plot, width=4),
                    dbc.Col(point_plot, width=4),
                ], ),
            ],style={'padding': '10px'})

        ])

# astig plot the data based on the selection
@app.callback(
    Output('astig-plot', 'figure'),
Input('astig-x-axis', 'value'),
Input('astig-y-axis', 'value'),
Input('astig-date-picker-range', 'start_date'),
Input('astig-date-picker-range', 'end_date'),
Input('astig-obsnum-start', 'value'),
Input('astig-obsnum-end', 'value'),
Input('astig-receiver', 'value'),
)
def update_astig_plot(x_axis, selected_fields, start_date, end_date, obsnum_start, obsnum_end, receivers):

    return make_plot('astig', start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, selected_fields)

# focus plot the data based on the selection
@app.callback(
    Output('focus-plot', 'figure'),
Input('focus-x-axis', 'value'),
Input('focus-y-axis', 'value'),
Input('focus-date-picker-range', 'start_date'),
Input('focus-date-picker-range', 'end_date'),
Input('focus-obsnum-start', 'value'),
Input('focus-obsnum-end', 'value'),
Input('focus-receiver', 'value'),
)
def update_focus_plot(x_axis, selected_fields, start_date, end_date, obsnum_start, obsnum_end, receivers):

    return make_plot('focus', start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, selected_fields)

# point plot the data based on the selection
@app.callback(
    Output('point-plot', 'figure'),
Input('point-x-axis', 'value'),
Input('point-y-axis', 'value'),
Input('point-date-picker-range', 'start_date'),
Input('point-date-picker-range', 'end_date'),
Input('point-obsnum-start', 'value'),
Input('point-obsnum-end', 'value'),
Input('point-receiver', 'value'),
)
def update_point_plot(x_axis, selected_fields, start_date, end_date, obsnum_start, obsnum_end, receivers):

    return make_plot('point', start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, selected_fields)

# date range selector update
@app.callback(
    Output("astig-plot", "figure",allow_duplicate=True),
    Output('astig-date-picker-range', 'start_date'),
    Output('astig-date-picker-range', 'end_date'),
    Input('astig-x-axis', 'value'),
    Input('astig-y-axis', 'value'),
    Input('astig-date-picker-range', 'start_date'),
    Input('astig-date-picker-range', 'end_date'),
    Input('astig-obsnum-start', 'value'),
    Input('astig-obsnum-end', 'value'),
    Input('astig-receiver', 'value'),
    Input('astig-last-week', 'n_clicks'),
    Input('astig-next-week', 'n_clicks'),
    Input('astig-last-month', 'n_clicks'),
    Input('astig-next-month', 'n_clicks'),
    Input('astig-last-year', 'n_clicks'),
    Input('astig-next-year', 'n_clicks'),
    Input('astig-all-data', 'n_clicks'),
    Input('astig-this-week', 'n_clicks'),
    prevent_initial_call=True

)
def update_astig_date( x_axis, y_axis, start_date, end_date, obsnum_start, obsnum_end, receivers,
                       prev_week, next_week, prev_month, next_month, prev_year, next_year,all_data, today):

    start_date, end_date = adjust_date_range(ctx.triggered_id, start_date, end_date)

    try:
        plot_figure = make_plot('astig',start_date,end_date,obsnum_start,obsnum_end,receivers,x_axis, y_axis)
        return plot_figure, start_date, end_date
    except Exception as e:
        print(f"Error updating tab astig: {e}")
        raise PreventUpdate


@app.callback(
    Output("focus-plot", "figure",allow_duplicate=True),
    Output('focus-date-picker-range', 'start_date'),
    Output('focus-date-picker-range', 'end_date'),
    Input('focus-x-axis', 'value'),
    Input('focus-y-axis', 'value'),
    Input('focus-date-picker-range', 'start_date'),
    Input('focus-date-picker-range', 'end_date'),
    Input('focus-obsnum-start', 'value'),
    Input('focus-obsnum-end', 'value'),
    Input('focus-receiver', 'value'),
    Input('focus-last-week', 'n_clicks'),
    Input('focus-next-week', 'n_clicks'),
    Input('focus-last-month', 'n_clicks'),
    Input('focus-next-month', 'n_clicks'),
    Input('focus-last-year', 'n_clicks'),
    Input('focus-next-year', 'n_clicks'),
    Input('focus-all-data', 'n_clicks'),
    Input('focus-this-week', 'n_clicks'),
    prevent_initial_call=True

)
def update_astig_plot( x_axis, selected_fields, start_date, end_date, obsnum_start, obsnum_end, receivers,
                        prev_week, next_week, prev_month, next_month, prev_year, next_year,all_data, today):
    start_date, end_date = adjust_date_range(ctx.triggered_id, start_date, end_date)

    try:
        plot_figure = make_plot('focus',start_date,end_date,obsnum_start,obsnum_end,receivers,x_axis, selected_fields)
        return plot_figure, start_date, end_date
    except Exception as e:
        print(f"Error updating tab focus: {e}")
        raise PreventUpdate

@app.callback(
    Output("point-plot", "figure",allow_duplicate=True),
    Output('point-date-picker-range', 'start_date'),
    Output('point-date-picker-range', 'end_date'),
    Input('point-x-axis', 'value'),
    Input('point-y-axis', 'value'),
    Input('point-date-picker-range', 'start_date'),
    Input('point-date-picker-range', 'end_date'),
    Input('point-obsnum-start', 'value'),
    Input('point-obsnum-end', 'value'),
    Input('point-receiver', 'value'),
    Input('point-last-week', 'n_clicks'),
    Input('point-next-week', 'n_clicks'),
    Input('point-last-month', 'n_clicks'),
    Input('point-next-month', 'n_clicks'),
    Input('point-last-year', 'n_clicks'),
    Input('point-next-year', 'n_clicks'),
    Input('point-all-data', 'n_clicks'),
    Input('point-this-week', 'n_clicks'),
    prevent_initial_call=True
)
def update_point_plot( x_axis, selected_fields, start_date, end_date, obsnum_start, obsnum_end, receivers,
                        prev_week, next_week, prev_month, next_month, prev_year, next_year,all_data, today):
    start_date, end_date = adjust_date_range(ctx.triggered_id, start_date, end_date)

    try:
        plot_figure = make_plot('point',start_date,end_date,obsnum_start,obsnum_end,receivers,x_axis, selected_fields)
        return plot_figure, start_date, end_date
    except Exception as e:
        print(f"Error updating tab point: {e}")
        raise PreventUpdate

# click astig another range to open compare modal
@app.callback(
Output('astig-compare-modal', 'is_open'),
Input('astig-another-range', 'n_clicks'),
Input('astig-compare-modal-close', 'n_clicks'),
State('astig-compare-modal', 'is_open'),
prevent_initial_call=True
)
def toggle_astig_compare_modal(n1, n2,is_open):
    if n1 or n2:
        return not is_open
    return is_open

# click focus another range to open compare modal
@app.callback(
Output('focus-compare-modal', 'is_open'),
Input('focus-another-range', 'n_clicks'),
Input('focus-compare-modal-close', 'n_clicks'),
State('focus-compare-modal', 'is_open'),
prevent_initial_call=True
)
def toggle_focus_compare_modal(n1, n2,is_open):
    if n1 or n2:
        return not is_open
    return is_open

# click point another range to open compare modal
@app.callback(
Output('point-compare-modal', 'is_open'),
Input('point-another-range', 'n_clicks'),
Input('point-compare-modal-close', 'n_clicks'),
State('point-compare-modal', 'is_open'),
prevent_initial_call=True
)
def toggle_point_compare_modal(n1, n2,is_open):
    if n1 or n2:
        return not is_open
    return is_open

#create a astig compare plot in the modal
@app.callback(
Output('astig-compare-plot1', 'figure'),
Output('astig-compare-plot2', 'figure'),
    Input('astig-compare-btn', 'n_clicks'),
State('astig-compare-date-picker-range1', 'start_date'),
State('astig-compare-date-picker-range1', 'end_date'),
State('astig-compare-date-picker-range2', 'start_date'),
State('astig-compare-date-picker-range2', 'end_date'),
State('astig-obsnum-start', 'value'),
State('astig-obsnum-end', 'value'),
State('astig-receiver', 'value'),
State('astig-x-axis', 'value'),
State('astig-y-axis', 'value'),
prevent_initial_call=True
)
def update_astig_compare_plot(compare_btn, start_date1, end_date1, start_date2,
                              end_date2,obsnum_start, obsnum_end, receivers, x_axis, y_axis, ):
    if compare_btn:
        fig1= make_plot('astig', start_date1, end_date1,obsnum_start, obsnum_end, receivers, x_axis, y_axis)
        fig2 = make_plot('astig', start_date2, end_date2,obsnum_start, obsnum_end, receivers, x_axis, y_axis)
        return fig1, fig2
    raise PreventUpdate

# create a focus compare plot in the modal
@app.callback(
Output('focus-compare-plot1', 'figure'),
Output('focus-compare-plot2', 'figure'),
    Input('focus-compare-btn', 'n_clicks'),
State('focus-compare-date-picker-range1', 'start_date'),
State('focus-compare-date-picker-range1', 'end_date'),
State('focus-compare-date-picker-range2', 'start_date'),
State('focus-compare-date-picker-range2', 'end_date'),
State('focus-obsnum-start', 'value'),
State('focus-obsnum-end', 'value'),
State('focus-receiver', 'value'),
State('focus-x-axis', 'value'),
State('focus-y-axis', 'value'),
prevent_initial_call=True
)
def update_focus_compare_plot(compare_btn, start_date1, end_date1, start_date2,
                                end_date2,obsnum_start, obsnum_end, receivers, x_axis, y_axis, ):
    if compare_btn:
        fig1 = make_plot('focus', start_date1, end_date1, obsnum_start, obsnum_end, receivers, x_axis, y_axis)
        fig2 = make_plot('focus', start_date2, end_date2, obsnum_start, obsnum_end, receivers, x_axis, y_axis)
        return fig1, fig2
    raise PreventUpdate

# create a point compare plot in the modal
@app.callback(
Output('point-compare-plot1', 'figure'),
Output('point-compare-plot2', 'figure'),
    Input('point-compare-btn', 'n_clicks'),
State('point-compare-date-picker-range1', 'start_date'),
State('point-compare-date-picker-range1', 'end_date'),
State('point-compare-date-picker-range2', 'start_date'),
State('point-compare-date-picker-range2', 'end_date'),
State('point-obsnum-start', 'value'),
State('point-obsnum-end', 'value'),
State('point-receiver', 'value'),
State('point-x-axis', 'value'),
State('point-y-axis', 'value'),
prevent_initial_call=True
)
def update_point_compare_plot(compare_btn, start_date1, end_date1, start_date2,
                                end_date2,obsnum_start, obsnum_end, receivers, x_axis, y_axis, ):
    if compare_btn:
        if y_axis is None:
            y_axis = []
        elif not isinstance(y_axis, list):
            y_axis = [y_axis]
        fig1 = make_plot('point', start_date1, end_date1, obsnum_start, obsnum_end, receivers, x_axis, y_axis)
        fig2 = make_plot('point', start_date2, end_date2, obsnum_start, obsnum_end, receivers, x_axis, y_axis)
        return fig1, fig2
    raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=False)

