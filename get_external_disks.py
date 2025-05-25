import psutil
import platform
import os
from get_disk_label import get_disk_label
from get_disk_serial import get_disk_serial

def generate_disk_id(disk_info):
    """
    Generate a safe identifier for a disk using its label.
    Converts spaces to underscores and makes all letters lowercase.
    """
    label = disk_info.get('label', 'unnamed_drive')
    # Convert to lowercase and replace spaces with underscores
    safe_label = label.lower().replace(' ', '_')
    return safe_label

def get_external_disks():
    partitions = psutil.disk_partitions(all=True)
    external_disks = []

    # Sistem disklerini ve özel mount noktalarını içeren patternler
    system_patterns = [
        'macintosh hd',
        'bootcamp'
    ]

    for partition in partitions:
        if not partition.mountpoint or not partition.device:
            continue

        # Sadece /Volumes altındaki diskleri kontrol et (macOS için)
        if not partition.mountpoint.startswith('/Volumes/'):
            continue

        # Sistem patternlerini kontrol et
        if any(pattern in partition.mountpoint.lower() for pattern in system_patterns):
            continue

        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info = {
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total_size': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent,
                'label': get_disk_label(partition.mountpoint),
                'serial': get_disk_serial(partition.device)
            }

            # Skip unnamed drives
            if disk_info['label'] == 'unnamed_drive':
                continue

            # Add unique disk ID before appending to list
            disk_info['disk_id'] = generate_disk_id(disk_info)
            external_disks.append(disk_info)
        except (PermissionError, OSError) as e:
            print(f"Error accessing disk {partition.mountpoint}: {str(e)}")
            continue

    return external_disks
