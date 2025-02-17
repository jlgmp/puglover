import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State  # ⚠️ 添加 State

# 初始化 Dash 应用
app = dash.Dash(__name__)

# 假设有一个用户设备 ID 的数据字典
device_data = {}

# 页面布局
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # 用于控制页面跳转
    html.Div(id='page-content')  # 页面内容部分
])

'''
当你跳转到不同的 URL 时，只有 page-content 部分的内容会根据 pathname（即 URL 地址）发生变化，
而页面的其他部分（如标题 H1）保持不变。
这种方式常用于单页应用（SPA）中，减少了整个页面的重新加载，提升了用户体验。
所以，在页面布局上，html.Div(id='page-content') 是一个容器，
里面的内容会根据 URL 的变化而更新，但整个页面的框架不会改变。
'''


# 登录页面内容
login_page = html.Div([
    html.H2("用户登录"),
    dcc.Input(id='device-id', type='text', placeholder='请输入电表 Device ID'),
    html.Button('登录', id='login-button', n_clicks=0),
])

# 功能页面内容
function_page = html.Div([
    html.H2("功能页面"),
    html.Button('查询最新电表读数', id='latest-reading-button', n_clicks=0),
    html.Br(),
    html.Button('查询用电量', id='electricity-usage-button', n_clicks=0),
    html.Div(id='output-container')  # 用于显示点击按钮后的内容
])

# **更新页面内容**   通过URL的变化调整输出
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/main':
        return login_page
    elif pathname == '/function':  # ⚠️ 修正 `/function` 显示功能页面
        return function_page
    return login_page  # 默认返回登录页面



# **登录逻辑，跳转到功能页面**  根据用户的点击事件来调整 URL
@app.callback(
    Output('url', 'pathname'),
    Input('login-button', 'n_clicks'),
    State('device-id', 'value')  # ⚠️ 修正：用 State 读取输入框的值
)
def login(n_clicks, device_id):
    if n_clicks > 0 and device_id:  # ⚠️ 设备 ID 不为空时才能跳转
        device_data['device_id'] = device_id
        return '/function'  # ⚠️ 这里要返回 `/function`
    return dash.no_update  # ⚠️ 保持当前页面

# **功能页面的按钮事件**
@app.callback(
    Output('output-container', 'children'),
    Input('latest-reading-button', 'n_clicks'),
    Input('electricity-usage-button', 'n_clicks')
)
def update_output(latest_clicks, usage_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ''
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'latest-reading-button':
        return "查询最新电表读数的功能正在开发中"
    elif button_id == 'electricity-usage-button':
        return "查询用电量的功能正在开发中"

if __name__ == '__main__':
    app.run_server(debug=True,port=8051)


