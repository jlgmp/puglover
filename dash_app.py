import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

# pip install dash flask
# 网页注册/登录页面
# 最新电表数据查询页面


app = dash.Dash(__name__, prevent_initial_callbacks='initial_duplicate')
# 这个设置允许 Dash 在页面加载时同时处理多个回调更新同一输出，并且会适当处理回调调用顺序的问题。

# 页面布局
app.layout = html.Div([
    html.H1("User Electricity Management"),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

# 登录页面内容
login_page = html.Div([
    html.H2("User Login"),
    dcc.Input(id='device-id', type='text', placeholder='Please input your device ID: '),
    html.Button('Login', id='login-button', n_clicks=0),
    html.Div(id='login-error')  # 显示错误信息
])

# 功能页面内容
function_page = html.Div([
    html.H2("Functions"),
    html.Button('View the meter reading', id='latest-reading-button', n_clicks=0),
    html.Br(),
    html.Button('View the electricity usage', id='electricity-usage-button', n_clicks=0),
    html.Div(id='output-container')  # 用于显示点击按钮后的内容
])


# 功能-读电表页面内容
meterreading_page = html.Div([
    html.H2("Meter Reading"),
    html.Div(id='meter-reading-content')  # 用于显示电表读数
])

# 功能-看用电量页面内容
electricityusage_page = html.Div([
    html.H2("Electricity Usage"),
    html.Div(id='electricity-usage-content')  # 用于显示电表读数
])


# 根据URL变化来调整页面内容
@app.callback(
    Output('page-content', 'children'),  
    Input('url', 'pathname')  
)
def display_page(pathname):
    if pathname == '/function': 
        return function_page
    elif pathname == '/function/meterreading':
        return meterreading_page
    elif pathname == '/function/electricityusage':
        return electricityusage_page
    return login_page 


# 登录页面按钮事件->跳转到功能页面，根据用户行为来调整URL
@app.callback(
    [Output('url', 'pathname',allow_duplicate=True),
    Output('login-error', 'children')],   # 添加一个 Output 来显示错误信息
    Input('login-button', 'n_clicks'),
    State('device-id', 'value')  
)
def login(n_clicks, device_id):
    if n_clicks > 0 and device_id:  
        with open('userdatabase.txt', 'r') as file:
            user_data = file.readlines()

        # 检查 device_id 是否在文件中
        device_found = False
        for line in user_data:
            user, stored_device_id = line.strip().split(',')
            if stored_device_id == device_id:
                device_found = True
                break

        if device_found:
            return '/function', ''  # 如果设备 ID 在文件中，跳转到功能页面，并清空错误信息
        else:
            return dash.no_update, "No device ID found. Please register first."  
    return dash.no_update, dash.no_update  # 如果没有点击或设备 ID 为空，保持当前页面，不更新错误信息


# 功能页面按钮事件
@app.callback(
    Output('url', 'pathname'),
    [Input('latest-reading-button', 'n_clicks'),
    Input('electricity-usage-button', 'n_clicks')] 
)
def update_output(latest_clicks, usage_clicks):
    if latest_clicks > 0:
        return '/function/meterreading'
    if usage_clicks > 0:
        return '/function/electricityusage'
    return dash.no_update







if __name__ == '__main__':
    app.run(debug=True, port=8051)





'''
login = html.Div([
    html.H2("User Login"),
    dcc.Input(id='login-userID', type='text', placeholder='Please input your device ID: '),
    html.Button('Login', id='login-button'),
    html.Br(),
    html.H2("No account?"),
    html.Button('Register', id='register-button'),
])


register = html.Div([
    html.H2("User Register"),
    dcc.Input(id='register-userID', type='text', placeholder='Please input your user name: '),
    dcc.Input(id='register-password', type='text', placeholder='Please input your password: '),
    dcc.Input(id='register-deviceID', type='text', placeholder='Please input your device ID'),
    html.Button('Register', id='register-submit-button'),
])
'''