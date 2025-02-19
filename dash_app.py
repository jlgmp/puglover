import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import re
import requests
import datetime
import pandas as pd
import plotly.graph_objs as go
# pip install dash flask

user_device_id = None


app = dash.Dash(__name__, prevent_initial_callbacks='initial_duplicate')
# allows Dash to handle multiple callbacks which update the same Output('url', 'pathname')

app.config.suppress_callback_exceptions = True
# prevent callbacks from finding component-id in the initial layout


# the overall layout
app.layout = html.Div([
    html.H1("User Electricity Management"),
    dcc.Location(id='url', refresh=False),   
    # refresh=False to make sure we only refresh the children content instead of the whole page
    html.Div(id='page-content'),
])




### Define Page Content ###
# login page content
login_page = html.Div([
    html.H2("User Login: "),
    dcc.Input(id='device-id', type='text', placeholder='Please input your device ID: '),
    html.Button('Login', id='login-button', n_clicks=0),
    html.Div(id='login-error'),  # show the error information
    html.Br(),
    html.H2("No Account?"),
    html.Button('Register Now', id='register-button', n_clicks=0),
])


# register page content
register_page = html.Div([
    html.H2("User Register: "),
    dcc.Input(id='register-userid', type='text', placeholder='Please input your user name: '),
    dcc.Input(id='register-deviceid', type='text', placeholder='Please input your device ID: '),
    html.Button('Register', id='register-submit-button', n_clicks=0),
    html.Div(id='register-info'),  # show the register status information
    html.Button('Back to Login', id='back-login-button', n_clicks=0),
])


# function page content
function_page = html.Div([
    html.H2("Functions"),
    html.Button('View the Meter Reading', id='meter-reading-button', n_clicks=0),
    html.Br(),
    html.Button('View the Electricity Usage', id='electricity-usage-button', n_clicks=0),
])


# function: meter reading page content
meter_reading_page = html.Div([
    dcc.Graph(id='meter-graph'),
])


@app.callback(
    Output('meter-graph', 'figure'),
    Input('url', 'pathname')
)
def update_graph(pathname):
    if pathname!= '/function/meter-reading':
        return dash.no_update

    now = datetime.datetime.now()  # Ensure 'now' is defined inside the callback

    # Fetch data from the API
    url = f"http://127.0.0.1:5000/meterdata?device={user_device_id}"
    response = requests.get(url)
    if response.status_code!= 200:
        return dash.no_update, "Failed to retrieve data from the API."

    data_json = response.json().get(user_device_id, {})

    sorted_times = sorted(data_json.keys())
    end_time = sorted_times[-1]

    start_time = '01:00'
    x = []
    y = []
    for time, consumption in data_json.items():
        if time >= start_time:
            x.append(time)
            y.append(consumption)
    title = f'{now.strftime("%Y-%m-%d")} Meter reading from {start_time} to {end_time}'

    # Create the figure
    trace = go.Scatter(
        x=x,
        y=y,
        mode='lines+markers',
        name='Daily Meter Reading',
        hovertemplate='%{x}<br>%{y} kWh'
    )

    figure = {
        'data': [trace],
        'layout': go.Layout(
            title=title,
            xaxis={'title': 'Time'},
            yaxis={'title': 'Meter Reading (kWh)'},
        )
    }
    return figure







# function: electricity usage page content
electricity_usage_page = html.Div([
    dcc.Dropdown(
        id='time-range-dropdown',
        options=[
            {'label': 'Last 7 Days', 'value': '7days'},
            {'label': 'This Month', 'value': 'thismonth'},
            {'label': 'Last Month', 'value': 'lastmonth'}
        ],
        value='7days',  # Default value
    ),
    dcc.Graph(id='electricity-graph'),
    html.Div(id='electricity-consumption'),
])





### Define Button Event ###
# login -> function button event
@app.callback(
    [Output('url', 'pathname', allow_duplicate=True),
    Output('login-error', 'children')],  
    Input('login-button', 'n_clicks'),
    State('device-id', 'value')  
)
def login(n_clicks, device_id):
    global user_device_id

    if n_clicks > 0 and device_id:  
        with open('userDatabase.txt', 'r') as file:
            user_data = file.readlines()

        # check if the device id in the userDatabse
        device_found = False
        for line in user_data:
            stored_device_id = line.strip()
            if stored_device_id == device_id:
                device_found = True
                user_device_id = device_id
                break

        if device_found:
            return '/function', ''  # update the url to the function page, clear the login-error content
        else:
            return dash.no_update, "No device ID found. Please register first or check the format (standard device ID example: 999-999-999)."  
    return dash.no_update, dash.no_update  # if no clicks or no input, remain the current page


# login -> register button event
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('register-button', 'n_clicks')
)
def go_to_register(n_clicks):
    if n_clicks > 0:
        return '/register' 
    return dash.no_update


# register in-page button event
@app.callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('register-info', 'children')],
    Input('register-submit-button', 'n_clicks'),
    [State('register-userid', 'value'),
     State('register-deviceid', 'value')]
)
def register(n_clicks, user_id, device_id):
    if n_clicks > 0 and user_id and device_id:
        pattern = r'^\d{3}-\d{3}-\d{3}$'
        if not re.match(pattern, device_id):
            return dash.no_update, "Invalid device ID format (standard device ID example: 999-999-999)."
        else: 
            # write the new user info into database
            with open('userDatabase.txt', 'a') as file:
                file.write(f"{device_id}\n")
            return dash.no_update, "Register successfully."
    return dash.no_update, dash.no_update


# register -> login button event
@app.callback(
    Output('url', 'pathname'),
    Input('back-login-button', 'n_clicks')
)
def back_to_login(n_clicks):
    if n_clicks > 0:
        return "/login"
    return dash.no_update


# function -> meter reading / electricity usage button event
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('meter-reading-button', 'n_clicks'),
    Input('electricity-usage-button', 'n_clicks')] 
)
def update_output(latest_clicks, usage_clicks):
    if latest_clicks > 0:
        return '/function/meter-reading'
    if usage_clicks > 0:
        return '/function/electricity-usage'
    return dash.no_update


# electricity usage in-page button event

# Helper functions to filter data
def filter_data(time_range, user_device_id):
    df = pd.read_csv('meterDatabase.txt', delimiter=",") 
    df['Date'] = pd.to_datetime(df['Date'])  
    df = df[df['DeviceID'] == user_device_id]

    now = datetime.datetime.now()
    if time_range == '7days':
        start_time = now - pd.Timedelta(days=7)
        data = df[df['Date'] >= start_time]
    elif time_range == 'thismonth':
        start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        data = df[(df['Date'] >= start_time) & (df['Date'].dt.month == now.month)]
    elif time_range == 'lastmonth':
        start_time = (now.replace(day=1) - pd.Timedelta(days=1)).replace(day=1)
        end_time = start_time + pd.DateOffset(months=1) - pd.Timedelta(seconds=1)
        data = df[(df['Date'] >= start_time) & (df['Date'] <= end_time)]      
    return data


@app.callback(
    [Output('electricity-graph', 'figure'),
     Output('electricity-consumption', 'children')],
    [Input('time-range-dropdown', 'value')]
)
def update_graph(time_range):
    now = datetime.datetime.now()  # Ensure 'now' is defined inside the callback
    data = filter_data(time_range, user_device_id)
    
    # Calculate total consumption and average consumption
    total_consumption = data['Daily_Consumption'].sum()
    avg_consumption = data['Daily_Consumption'].mean()

    # Create the figure
    if time_range == '7days':
        title = 'Last 7 Days Electricity Consumption'
        x = data['Date']
    elif time_range == 'thismonth':
        title = 'This Month\'s Electricity Consumption'
        x = data['Date']
    elif time_range == 'lastmonth':
        title = 'Last Month\'s Electricity Consumption'
        x = data['Date']
    trace = go.Scatter(
        x=x, 
        y=data['Daily_Consumption'],
        mode='lines+markers', 
        name='Electricity Consumption',
        hovertemplate='%{x}<br>%{y} kWh'
        )
    
    avg_line = go.Scatter(
        x=x, y=[avg_consumption] * len(x),
        mode='lines', name='Average Consumption', line=dict(dash='dash')
    )
    
    figure = {
        'data': [trace, avg_line],
        'layout': go.Layout(
            title=title,
            xaxis={'title': 'Date'},
            yaxis={'title': 'Electricity Consumption (kWh)'},
        )
    }

    consumption_text = html.Div([
            html.P(f'Total Consumption: {total_consumption:.2f} kWh', style={'font-size': '16px', 'font-weight': 'bold'}),
            html.P(f'Average Consumption: {avg_consumption:.2f} kWh', style={'font-size': '16px', 'font-weight': 'bold'})
        ])

    return figure, consumption_text




# adjust page content based on URL changes
@app.callback(
    Output('page-content', 'children'),  
    Input('url', 'pathname')  
)
def display_page(pathname):
    if pathname == '/function': 
        return function_page
    elif pathname == '/function/meter-reading':
        return meter_reading_page
    elif pathname == '/function/electricity-usage':
        return electricity_usage_page
    elif pathname == '/register':
        return register_page
    return login_page 




if __name__ == '__main__':
    app.run(debug=True,port=8050)




