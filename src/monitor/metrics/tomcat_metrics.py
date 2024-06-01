import requests


def check_tomcat(host, ports):
    statuses = {}
    for port in ports:
        try:
            url = f'http://{host}:{port}/health'
            response = requests.get(url)
            if response.status_code == 200 and 'Tomcat Running' in response.text:
                statuses[port] = 'running'
            else:
                statuses[port] = 'down'
        except:
            statuses[port] = 'down'
    return statuses
