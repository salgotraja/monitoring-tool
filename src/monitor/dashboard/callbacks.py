from dash.dependencies import Input, Output
from dash import html, dcc
import plotly.graph_objs as go
from monitor.metrics.system_metrics import get_system_metrics
from monitor.metrics.disk_metrics import get_disk_metrics
from monitor.metrics.mysql_metrics import check_mysql
from monitor.metrics.redis_metrics import check_redis
from monitor.metrics.mongodb_metrics import check_mongodb
from monitor.metrics.tomcat_metrics import check_tomcat
from monitor.metrics.httpd_metrics import check_httpd
from monitor.utils.email_utils import send_email
import threading
import time
import collections
import paramiko
import subprocess

metrics_data = collections.defaultdict(lambda: {'cpu': [], 'memory': [], 'swap': [], 'disk': [], 'timestamps': []})
service_status_data = collections.defaultdict(dict)
disk_usage_data = {}


def register_callbacks(app, remote_servers, email_config, ssh_config):
    global metrics_data, service_status_data, disk_usage_data

    print("SSH Config:", ssh_config)

    SSH_USER = ssh_config.get('username')
    SSH_PASSWORD = ssh_config.get('password')

    def get_disk_usage(host, port=None):
        try:
            if port:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port=port, username=SSH_USER, password=SSH_PASSWORD)
                stdin, stdout, stderr = ssh.exec_command("df -kh")
                disk_usage_data[host] = stdout.read().decode()
                ssh.close()
            else:
                result = subprocess.run(["df", "-kh"], capture_output=True, text=True)
                if result.returncode == 0:
                    disk_usage_data[host] = result.stdout
                else:
                    disk_usage_data[host] = f"Error fetching disk usage: {result.stderr}"
        except Exception as e:
            disk_usage_data[host] = str(e)

    def collect_disk_usage():
        while True:
            try:
                for host_info in remote_servers['hosts']:
                    host = host_info['host']
                    port = host_info.get('ssh_port', None)
                    get_disk_usage(host, port)
                time.sleep(60)
            except Exception as e:
                print(f"Error in disk usage collection thread: {e}")

    def collect_service_statuses():
        while True:
            alerts = []
            for host_info in remote_servers['hosts']:
                host = host_info['host']
                services = host_info['services']
                service_status_data[host] = {}
                for service, ports in services.items():
                    if isinstance(ports, list):
                        statuses = {port: 'unknown' for port in ports}
                        if service == 'tomcat':
                            statuses = check_tomcat(host, ports)
                        elif service == 'httpd':
                            statuses = check_httpd(host, ports)
                        service_status_data[host][service] = statuses
                    else:
                        status = 'unknown'
                        if service == 'mysql':
                            status = check_mysql({
                                'host': host,
                                'port': ports,
                                'user': host_info.get('mysql_user', ''),
                                'password': host_info.get('mysql_password', '')
                            })
                        elif service == 'redis':
                            status = check_redis({'host': host, 'port': ports})
                        elif service == 'mongodb':
                            status = check_mongodb({'host': host, 'port': ports})
                        service_status_data[host][service] = status

                    if isinstance(service_status_data[host][service], dict):
                        for port, status in service_status_data[host][service].items():
                            if status == 'down':
                                alerts.append(f"{service.capitalize()} on {host}:{port} is down")
                    else:
                        if service_status_data[host][service] == 'down':
                            alerts.append(f"{service.capitalize()} on {host} is down")

            if alerts:
                subject = "Service Alert: Multiple Services Down"
                body = "\n".join(alerts)
                print(f"Sending email: {subject}")
                send_email(subject, body, email_config)

            time.sleep(30)

    @app.callback(
        Output('cpu-graph', 'figure'),
        Output('memory-graph', 'figure'),
        Output('service-statuses', 'children'),
        Output('disk-usage-container', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_graphs(n_intervals):
        global metrics_data, service_status_data, disk_usage_data

        print("Updating graphs...")

        cpu_fig = go.Figure()
        memory_fig = go.Figure()

        for host in metrics_data:
            print(f"Plotting data for {host}:")
            print(f"Timestamps: {metrics_data[host]['timestamps']}")
            print(f"CPU: {metrics_data[host]['cpu']}")
            print(f"Memory: {metrics_data[host]['memory']}")

            if len(metrics_data[host]['timestamps']) > 0:
                cpu_trace = go.Scatter(
                    x=metrics_data[host]['timestamps'],
                    y=[cpu / 100 for cpu in metrics_data[host]['cpu']],
                    mode='lines+markers',
                    name=f"{host} CPU"
                )
                memory_trace = go.Scatter(
                    x=metrics_data[host]['timestamps'],
                    y=[mem / 1024 for mem in metrics_data[host]['memory']],
                    mode='lines+markers',
                    name=f"{host} Memory"
                )
                cpu_fig.add_trace(cpu_trace)
                memory_fig.add_trace(memory_trace)

        cpu_fig.update_layout(
            title='CPU Usage Over Time',
            xaxis_title='Time',
            yaxis_title='CPU Usage (%)'
        )
        memory_fig.update_layout(
            title='Memory Usage Over Time',
            xaxis_title='Time',
            yaxis_title='Memory Usage (GB)'
        )

        disk_usage_elements = []
        for host_info in remote_servers['hosts']:
            host = host_info['host']
            disk_usage = disk_usage_data.get(host, "No data")
            disk_usage_elements.append(
                html.Div(
                    [
                        html.H5(f"Disk Usage for {host}"),
                        html.Pre(disk_usage)
                    ],
                    style={'border': '1px solid black', 'padding': '10px', 'margin': '10px', 'width': '45%'}
                )
            )

        service_status_elements = []
        for host_info in remote_servers['hosts']:
            host = host_info['host']
            services = host_info['services']
            host_status_elements = [html.H5(f"Host: {host}")]
            service_boxes = []
            for service, status in service_status_data[host].items():
                if isinstance(status, dict):
                    for port, port_status in status.items():
                        color = 'green' if port_status == 'running' else 'red'
                        service_boxes.append(
                            html.Div(
                                f"{service.capitalize()} (Port {port}): {port_status}",
                                style={'border': '1px solid black', 'padding': '5px', 'margin': '5px',
                                       'backgroundColor': color, 'width': '150px', 'textAlign': 'center'}
                            )
                        )
                else:
                    color = 'green' if status == 'running' else 'red'
                    service_boxes.append(
                        html.Div(
                            f"{service.capitalize()} (Port {services[service]}): {status}",
                            style={'border': '1px solid black', 'padding': '5px', 'margin': '5px',
                                   'backgroundColor': color, 'width': '150px', 'textAlign': 'center'}
                        )
                    )
            host_status_elements.append(html.Div(service_boxes, style={'display': 'flex', 'flexWrap': 'wrap'}))
            service_status_elements.append(html.Div(host_status_elements, style={'marginBottom': '20px'}))

        return cpu_fig, memory_fig, service_status_elements, disk_usage_elements

    def start_metric_collection():
        while True:
            try:
                for host_info in remote_servers['hosts']:
                    host = host_info['host']
                    system_metrics = get_system_metrics()
                    print(f"Collected system metrics for {host}: {system_metrics}")

                    if len(metrics_data[host]['cpu']) > 100:
                        metrics_data[host]['cpu'].pop(0)
                        metrics_data[host]['memory'].pop(0)
                        metrics_data[host]['swap'].pop(0)
                        metrics_data[host]['timestamps'].pop(0)

                    metrics_data[host]['cpu'].append(system_metrics['cpu'])
                    metrics_data[host]['memory'].append(system_metrics['memory'])
                    metrics_data[host]['swap'].append(system_metrics['swap'])
                    metrics_data[host]['timestamps'].append(time.time())

                time.sleep(1)
            except Exception as e:
                print(f"Error in metric collection thread: {e}")

    metric_collection_thread = threading.Thread(target=start_metric_collection)
    metric_collection_thread.daemon = True
    metric_collection_thread.start()

    service_status_collection_thread = threading.Thread(target=collect_service_statuses)
    service_status_collection_thread.daemon = True
    service_status_collection_thread.start()

    disk_usage_collection_thread = threading.Thread(target=collect_disk_usage)
    disk_usage_collection_thread.daemon = True
    disk_usage_collection_thread.start()
