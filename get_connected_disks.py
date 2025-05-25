import psutil

def get_connected_disks():
    """Get a set of currently connected disk identifiers"""
    partitions = psutil.disk_partitions(all=True)
    return {f"{p.device}:{p.mountpoint}" for p in partitions if p.device and p.mountpoint}
