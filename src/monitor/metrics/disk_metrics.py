import psutil


def get_disk_metrics():
    partitions = psutil.disk_partitions()
    usage = {partition.mountpoint: psutil.disk_usage(partition.mountpoint)._asdict() for partition in partitions}
    return usage
