import redis


def check_redis(config):
    try:
        client = redis.StrictRedis(host=config['host'], port=config['port'])
        if client.ping():
            return 'running'
    except:
        return 'down'
    return 'down'
