import os
import dash
import dash_bootstrap_components as dbc
from dash import html
from monitor.config.config import read_config
from monitor.dashboard.layout import create_layout
from monitor.dashboard.callbacks import register_callbacks

print("Current working directory:", os.getcwd())
config_file_path = '../../config.ini'
remote_servers, email_config, ssh_config = read_config(config_file_path)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    requests_pathname_prefix='/server-monitor/',
    routes_pathname_prefix='/server-monitor/'
)

app.layout = create_layout()
register_callbacks(app, remote_servers, email_config, ssh_config)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
