import platform
import subprocess
import os
import uuid

def get_disk_serial(device_path):
    """Get disk serial number based on OS"""
    system = platform.system()
    try:
        if system == "Windows":
            cmd = f'wmic diskdrive get SerialNumber,DeviceID'
            result = subprocess.check_output(cmd, shell=True).decode()
            lines = result.strip().split('\n')
            for line in lines[1:]:
                if device_path in line:
                    return line.split()[-1]
        elif system == "Linux":
            cmd = f'ls -l /dev/disk/by-id/'
            result = subprocess.check_output(cmd, shell=True).decode()
            for line in result.split('\n'):
                if device_path in line:
                    return line.split('/')[-1]
        elif system == "Darwin":
            cmd = f'diskutil info {device_path}'
            result = subprocess.check_output(cmd, shell=True).decode()
            for line in result.split('\n'):
                if 'Serial Number' in line:
                    return line.split(':')[-1].strip()
    except:
        pass
    return str(uuid.uuid4())
