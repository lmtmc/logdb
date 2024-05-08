# todo update database automatically
# add a unselect all button
import dash
from dash import html, Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from layout import (title, same_setting, plots, make_plot, adjust_date_range)

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

    html.Div(title),
    html.Div(id = 'same-setting', children=same_setting),
    html.Div(plots)
        ])

# update date range for same setting
@app.callback(
    Output('same-date-picker-range', 'start_date'),
    Output('same-date-picker-range', 'end_date'),
    Input('same-last-week', 'n_clicks'),
    Input('same-next-week', 'n_clicks'),
    Input('same-last-month', 'n_clicks'),
    Input('same-next-month', 'n_clicks'),
    Input('same-last-year', 'n_clicks'),
    Input('same-next-year', 'n_clicks'),
    Input('same-all-data', 'n_clicks'),
    Input('same-this-week', 'n_clicks'),
    State('same-date-picker-range', 'start_date'),
    State('same-date-picker-range', 'end_date'),
    prevent_initial_call=True
)
def update_same_date(prev_week, next_week, prev_month, next_month, prev_year, next_year, all_data, today, start_date, end_date):
    start_date, end_date = adjust_date_range(ctx.triggered_id, start_date, end_date)
    return start_date, end_date

# use same setting to plot astig, focus and point
@app.callback(
    Output('astig-plot', 'figure'),
    Output('focus-plot', 'figure'),
    Output('point-plot', 'figure'),
    Input('same-x-axis', 'value'),
    Input('astig-y-axis', 'value'),
    Input('focus-y-axis', 'value'),
    Input('point-y-axis', 'value'),
    Input('same-date-picker-range', 'start_date'),
    Input('same-date-picker-range', 'end_date'),
    Input('same-obsnum-start', 'value'),
    Input('same-obsnum-end', 'value'),
    Input('same-receiver', 'value'),
)
def update_same_setting(x_axis, astig_y_axis, focus_y_axis, point_y_axis, start_date, end_date, obsnum_start, obsnum_end, receivers):
    astig_fig = make_plot('astig', start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, astig_y_axis)
    focus_fig = make_plot('focus', start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, focus_y_axis)
    point_fig = make_plot('point', start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, point_y_axis)
    return astig_fig, focus_fig, point_fig

def create_toggle_and_update_modal_callback(modal_type):
    @app.callback(
        [
            Output(f'{modal_type}-compare-modal', 'is_open'),
            Output(f'{modal_type}-compare-date-picker-range1', 'start_date'),
            Output(f'{modal_type}-compare-date-picker-range1', 'end_date'),
            Output(f'{modal_type}-compare-date-picker-range2', 'start_date'),
            Output(f'{modal_type}-compare-date-picker-range2', 'end_date'),
            Output(f'{modal_type}-obsnum-start', 'value'),
            Output(f'{modal_type}-obsnum-end', 'value'),
            Output(f'{modal_type}-receiver', 'value'),
            Output(f'{modal_type}-x-axis', 'value'),
            Output(f'{modal_type}-compare-y-axis', 'value'),
            Output(f'{modal_type}-compare-plot1', 'figure', allow_duplicate=True),
            Output(f'{modal_type}-compare-plot2', 'figure', allow_duplicate=True)
        ],
        [
            Input(f'{modal_type}-another-range', 'n_clicks'),
            Input(f'{modal_type}-compare-modal-close', 'n_clicks')
        ],
        [
            State(f'{modal_type}-compare-modal', 'is_open'),
            State('same-date-picker-range', 'start_date'),
            State('same-date-picker-range', 'end_date'),
            State('same-obsnum-start', 'value'),
            State('same-obsnum-end', 'value'),
            State('same-receiver', 'value'),
            State('same-x-axis', 'value'),
            State(f'{modal_type}-y-axis', 'value'),
            State(f'{modal_type}-plot', 'figure')
        ],
        prevent_initial_call=True
    )
    def toggle_and_update_modal(n1, n2, is_open, start_date, end_date, obsnum_start, obsnum_end, receiver, x_axis, y_axis, current_figure):
        if n1 or n2:
            if not is_open:
                figure = make_plot(modal_type, start_date, end_date, obsnum_start, obsnum_end, receiver, x_axis, y_axis)
                return [not is_open, start_date, end_date, start_date, end_date,
                        obsnum_start, obsnum_end, receiver, x_axis, y_axis,
                        figure, figure]
            else:
                return [not is_open] + [no_update] * 11
        raise PreventUpdate

    return toggle_and_update_modal

def create_update_plot_callback(modal_type):
    @app.callback(
        [
            Output(f'{modal_type}-compare-plot1', 'figure'),
            Output(f'{modal_type}-compare-plot2', 'figure')
        ],
        [
            Input(f'{modal_type}-compare-date-picker-range1', 'start_date'),
            Input(f'{modal_type}-compare-date-picker-range1', 'end_date'),
            Input(f'{modal_type}-compare-date-picker-range2', 'start_date'),
            Input(f'{modal_type}-compare-date-picker-range2', 'end_date'),
            Input(f'{modal_type}-obsnum-start', 'value'),
            Input(f'{modal_type}-obsnum-end', 'value'),
            Input(f'{modal_type}-receiver', 'value'),
            Input(f'{modal_type}-x-axis', 'value'),
            Input(f'{modal_type}-compare-y-axis', 'value')
        ],
        prevent_initial_call=True
    )
    def update_plot(start_date1, end_date1, start_date2, end_date2, obsnum_start, obsnum_end, receivers, x_axis, y_axis):
        fig1 = make_plot(modal_type, start_date1, end_date1, obsnum_start, obsnum_end, receivers, x_axis, y_axis)
        fig2 = make_plot(modal_type, start_date2, end_date2, obsnum_start, obsnum_end, receivers, x_axis, y_axis)
        return fig1, fig2

    return update_plot

# Create callbacks for each type
toggle_and_update_astig = create_toggle_and_update_modal_callback('astig')
update_astig_plots = create_update_plot_callback('astig')

toggle_and_update_focus = create_toggle_and_update_modal_callback('focus')
update_focus_plots = create_update_plot_callback('focus')

toggle_and_update_point = create_toggle_and_update_modal_callback('point')
update_point_plots = create_update_plot_callback('point')


if __name__ == '__main__':
    app.run_server(debug=False)

