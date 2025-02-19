import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import re
# pip install dash flask


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
    html.H2("Meter Reading"),
    html.Div(id='meter-reading-content')  
])


# function: electricity usage page content
electricity_usage_page = html.Div([
    html.H2("Electricity Usage"),
    html.Div(id='electricity-usage-content')  
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
    if n_clicks > 0 and device_id:  
        with open('userdatabase.txt', 'r') as file:
            user_data = file.readlines()

        # check if the device id in the userdatabse
        device_found = False
        for line in user_data:
            user, stored_device_id = line.strip().split(',')
            if stored_device_id == device_id:
                device_found = True
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


# register -> userdatabase button event
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
            with open('userdatabase.txt', 'a') as file:
                file.write(f"{user_id},{device_id}\n")
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
    app.run(debug=True)





