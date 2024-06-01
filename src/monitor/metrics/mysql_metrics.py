import pymysql


def check_mysql(config):
    try:
        print(f"Checking MySQL on {config['host']}:{config.get('port', 3306)} with user {config['user']}")
        connection = pymysql.connect(
            host=config['host'],
            port=config.get('port', 3306),
            user=config['user'],
            password=config['password']
        )
        if connection.open:
            print(f"MySQL on {config['host']}:{config.get('port', 3306)} is running")
            connection.close()
            return 'running'
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return 'down'
    return 'down'
