import configparser
import os


def read_config(config_file='config.ini'):
    print("Current working directory in config:", os.getcwd())
    print("Config file:", config_file)
    config = configparser.ConfigParser()
    print(f"Reading configuration from {config_file}")
    config.read(config_file)

    print("Configuration sections:", config.sections())

    remote_servers = {'hosts': []}
    for section in config.sections():
        if section.startswith('server'):
            server_info = {'host': config[section]['host'], 'services': {}}
            if 'ssh_port' in config[section]:
                server_info['ssh_port'] = int(config[section]['ssh_port'])
            if 'mysql_user' in config[section]:
                server_info['mysql_user'] = config[section]['mysql_user']
            if 'mysql_password' in config[section]:
                server_info['mysql_password'] = config[section]['mysql_password']

            for key, value in config[section].items():
                if key.endswith('_port') and 'ssh_port' not in key:
                    service_name = key.replace('_port', '')
                    if ',' in value:
                        server_info['services'][service_name] = [int(port) for port in value.split(',')]
                    else:
                        server_info['services'][service_name] = int(value)

            remote_servers['hosts'].append(server_info)

    if 'email' in config:
        email_config = {key: value for key, value in config['email'].items()}
        email_config['to_emails'] = email_config['to_emails'].split(',')
    else:
        email_config = {}

    if 'ssh' in config:
        ssh_config = {key: value for key, value in config['ssh'].items()}
        if 'local_bind_port' in ssh_config:
            ssh_config['local_bind_port'] = int(ssh_config['local_bind_port'])
        if 'remote_bind_port' in ssh_config:
            ssh_config['remote_bind_port'] = int(ssh_config['remote_bind_port'])
    else:
        ssh_config = {}

    print("Remote Servers:", remote_servers)
    print("Email Config:", email_config)
    print("SSH Config:", ssh_config)

    return remote_servers, email_config, ssh_config
