# todo update database automatically
# add a unselect all button
import dash
from dash import html, Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from layout import (title, same_setting, plots, make_plot, adjust_date_range,get_obsnum_range)
import flask

prefix = '/lmtqldb/'

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
    html.Div(plots)])

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

# get the obsnum range when date range is changed
@app.callback(
    Output('same-obsnum-start', 'value'),
    Output('same-obsnum-end', 'value'),
    Input('same-date-picker-range', 'start_date'),
    Input('same-date-picker-range', 'end_date'),
)
def update_same_obsnum_range(start_date, end_date):
    return get_obsnum_range(start_date, end_date)


# Callback for updating astig-plot
@app.callback(
    Output('astig-plot', 'figure'),
    Input('same-x-axis', 'value'),
    Input('astig-y-axis', 'value'),
    Input('same-date-picker-range', 'start_date'),
    Input('same-date-picker-range', 'end_date'),
    Input('same-obsnum-start', 'value'),
    Input('same-obsnum-end', 'value'),
    Input('same-receiver', 'value'),
)
def update_astig_plot(x_axis, astig_y_axis, start_date, end_date, obsnum_start, obsnum_end, receivers):
    try:
        return make_plot('astig', start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, astig_y_axis)
    except Exception as e:
        return no_update

# Callback for updating focus-plot
@app.callback(
    Output('focus-plot', 'figure'),
    Input('same-x-axis', 'value'),
    Input('focus-y-axis', 'value'),
    Input('same-date-picker-range', 'start_date'),
    Input('same-date-picker-range', 'end_date'),
    Input('same-obsnum-start', 'value'),
    Input('same-obsnum-end', 'value'),
    Input('same-receiver', 'value'),
)
def update_focus_plot(x_axis, focus_y_axis, start_date, end_date, obsnum_start, obsnum_end, receivers):
    try:
        return make_plot('focus', start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, focus_y_axis)
    except Exception as e:
        return no_update

# Callback for updating pointing-plot
@app.callback(
    Output('pointing-plot', 'figure'),
    Input('same-x-axis', 'value'),
    Input('pointing-y-axis', 'value'),
    Input('same-date-picker-range', 'start_date'),
    Input('same-date-picker-range', 'end_date'),
    Input('same-obsnum-start', 'value'),
    Input('same-obsnum-end', 'value'),
    Input('same-receiver', 'value'),
)
def update_pointing_plot(x_axis, pointing_y_axis, start_date, end_date, obsnum_start, obsnum_end, receivers):
    try:
        return make_plot('pointing', start_date, end_date, obsnum_start, obsnum_end, receivers, x_axis, pointing_y_axis)
    except Exception as e:
        return no_update

def create_toggle_and_update_modal_callback(modal_type):
    @app.callback(
        [
            Output(f'{modal_type}-compare-modal', 'is_open'),
            Output(f'{modal_type}-compare-date-picker-range1', 'start_date'),
            Output(f'{modal_type}-compare-date-picker-range1', 'end_date'),
            Output(f'{modal_type}-compare-date-picker-range2', 'start_date'),
            Output(f'{modal_type}-compare-date-picker-range2', 'end_date'),
            Output(f'{modal_type}-obsnum-start', 'value', allow_duplicate=True),
            Output(f'{modal_type}-obsnum-end', 'value', allow_duplicate=True),
            Output(f'{modal_type}-receiver', 'value'),
            Output(f'{modal_type}-x-axis', 'value'),
            Output(f'{modal_type}-compare-y-axis', 'value'),
            Output(f'{modal_type}-compare-plot1', 'figure', allow_duplicate=True),
            Output(f'{modal_type}-compare-plot2', 'figure', allow_duplicate=True)
        ],
        [
            Input(f'{modal_type}-another-range', 'n_clicks'),
            Input(f'{modal_type}-compare-modal-close', 'n_clicks'),
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

def create_obsnum_range_callback(modal_type):
    @app.callback(
        Output(f'{modal_type}-obsnum-start', 'value'),
        Output(f'{modal_type}-obsnum-end', 'value'),
        Input(f'{modal_type}-compare-date-picker-range1', 'start_date'),
        Input(f'{modal_type}-compare-date-picker-range1', 'end_date'),
        Input(f'{modal_type}-compare-date-picker-range2', 'start_date'),
        Input(f'{modal_type}-compare-date-picker-range2', 'end_date'),
        prevent_initial_call=True
    )
    def update_obsnum_range(start_date1, end_date1, start_date2, end_date2):
        start = min(get_obsnum_range(start_date1, end_date1)[0], get_obsnum_range(start_date2, end_date2)[0])
        end = max(get_obsnum_range(start_date1, end_date1)[1], get_obsnum_range(start_date2, end_date2)[1])
        return start, end

    return update_obsnum_range


def create_update_plot1_callback(modal_type):
    @app.callback(
        Output(f'{modal_type}-compare-plot1', 'figure'),
        [
            Input(f'{modal_type}-compare-date-picker-range1', 'start_date'),
            Input(f'{modal_type}-compare-date-picker-range1', 'end_date'),
            Input(f'{modal_type}-obsnum-start', 'value'),
            Input(f'{modal_type}-obsnum-end', 'value'),
            Input(f'{modal_type}-receiver', 'value'),
            Input(f'{modal_type}-x-axis', 'value'),
            Input(f'{modal_type}-compare-y-axis', 'value')
        ],
        prevent_initial_call=True
    )
    def update_plot1(start_date1, end_date1, obsnum_start, obsnum_end, receivers, x_axis, y_axis):
        try:
            if None in [start_date1, end_date1, obsnum_start, obsnum_end, receivers, x_axis, y_axis]:
                print("One or more inputs are None, skipping plot update.")
                return {}
            fig1 = make_plot(modal_type, start_date1, end_date1, obsnum_start, obsnum_end, receivers, x_axis, y_axis)
            return fig1
        except Exception as e:
            print(f"Error generating plots: {e}")
            return {}

    return update_plot1

def create_update_plot2_callback(modal_type):
    @app.callback(
        Output(f'{modal_type}-compare-plot2', 'figure'),
        [
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
    def update_plot2(start_date2, end_date2, obsnum_start, obsnum_end, receivers, x_axis, y_axis):
        try:
            if None in [start_date2, end_date2, obsnum_start, obsnum_end, receivers, x_axis, y_axis]:
                print("One or more inputs are None, skipping plot update.")
                return {}
            fig2 = make_plot(modal_type, start_date2, end_date2, obsnum_start, obsnum_end, receivers, x_axis, y_axis)
            return fig2
        except Exception as e:
            print(f"Error generating plots: {e}")
            return {}

    return update_plot2

# Create callbacks for each type
toggle_and_update_astig = create_toggle_and_update_modal_callback('astig')
update_astig_plot1 = create_update_plot1_callback('astig')
update_astig_plots2 = create_update_plot2_callback('astig')
update_astig_obsnum_range = create_obsnum_range_callback('astig')

toggle_and_update_focus = create_toggle_and_update_modal_callback('focus')
update_focus_plot1 = create_update_plot1_callback('focus')
update_focus_plots2 = create_update_plot2_callback('focus')
update_focus_obsnum_range = create_obsnum_range_callback('focus')

toggle_and_update_pointing = create_toggle_and_update_modal_callback('pointing')
update_pointing_plot1 = create_update_plot1_callback('pointing')
update_pointing_plots2 = create_update_plot2_callback('pointing')
update_pointing_obsnum_range = create_obsnum_range_callback('pointing')


if __name__ == '__main__':
    app.run_server(debug=False)

