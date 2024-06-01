import psutil


def get_system_metrics():
    return {
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory().percent,
        'total_memory': psutil.virtual_memory().total / (1024 ** 3),
        'swap': psutil.swap_memory().percent
    }
