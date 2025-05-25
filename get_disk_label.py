import platform
import subprocess

def get_disk_label(mountpoint):
    """Get disk label/name based on OS"""
    system = platform.system()
    try:
        if system == "Windows":
            cmd = f'wmic logicaldisk get VolumeName,DeviceID'
            result = subprocess.check_output(cmd, shell=True).decode()
            for line in result.split('\n'):
                if mountpoint[0] in line:
                    parts = line.split()
                    if len(parts) > 1:
                        return parts[1]
        elif system == "Linux":
            cmd = f'blkid -s LABEL -o value {mountpoint}'
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            if result:
                return result
        elif system == "Darwin":
            cmd = f'diskutil info {mountpoint}'
            result = subprocess.check_output(cmd, shell=True).decode()
            for line in result.split('\n'):
                if 'Volume Name' in line:
                    return line.split(':')[-1].strip()
    except:
        pass
    return "Unnamed Drive"
