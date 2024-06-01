import requests


def check_httpd(host, ports):
    statuses = {}
    for port in ports:
        try:
            url = f'http://{host}:{port}'
            response = requests.get(url)
            statuses[port] = 'running' if response.status_code == 200 else 'down'
        except:
            statuses[port] = 'down'
    return statuses
