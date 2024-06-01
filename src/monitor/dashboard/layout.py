import dash_bootstrap_components as dbc
from dash import dcc, html


def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("System Monitoring Dashboard"), className="mb-2")
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H4("CPU Usage Over Time"),
                    dcc.Graph(id='cpu-graph')
                ])
            ), md=6),
            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H4("Memory Usage Over Time"),
                    dcc.Graph(id='memory-graph')
                ])
            ), md=6),
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H4("Service Statuses"),
                    html.Div(id='service-statuses')
                ])
            ), md=12)
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H4("Disk Space Usage"),
                    html.Div(id='disk-usage-container', style={'display': 'flex', 'flexWrapd': 'wrap'})
                ])
            ), md=12)
        ]),
        dcc.Interval(
            id='interval-component',
            interval=10 * 1000,
            n_intervals=0
        )
    ], fluid=True)
