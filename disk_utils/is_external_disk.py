import platform
import os
import subprocess

def is_external_disk(device_path, mountpoint, system):
    """Check if the disk is external based on OS-specific methods"""
    try:
        if system == "Windows":
            cmd = f'wmic diskdrive where "DeviceID=\'{device_path}\'" get InterfaceType,MediaType'
            result = subprocess.check_output(cmd, shell=True).decode()
            return any(x in result.lower() for x in ['usb', 'external', 'removable'])
        elif system == "Linux":
            cmd = f'lsblk -d -o NAME,TRAN,ROTA'
            result = subprocess.check_output(cmd, shell=True).decode()
            device_name = os.path.basename(device_path)
            for line in result.split('\n'):
                if device_name in line:
                    return 'usb' in line.lower() or '0' in line.split()[-1]
        elif system == "Darwin":
            cmd = f'diskutil info {device_path}'
            result = subprocess.check_output(cmd, shell=True).decode()
            return any(x in result.lower() for x in ['external', 'removable', 'usb'])
    except:
        pass
    return False
