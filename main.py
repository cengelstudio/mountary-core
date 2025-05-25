import os
import platform
import time
import json
import requests
import unicodedata
from datetime import datetime
from get_connected_disks import get_connected_disks
from get_external_disks import get_external_disks
from save_to_json import save_to_json
from format_size import format_size
from config import COLORS, API_CONFIG
from colorama import init
import psutil
from disk_monitor import DiskMonitor
from save_disk_contents import save_disk_contents

# Initialize colorama
init()

def print_colored(text, color):
    print(f"{color}{text}{COLORS['ENDC']}")

def normalize_path(path):
    """Normalize path to handle special characters and long paths."""
    # Convert to absolute path
    abs_path = os.path.abspath(path)

    # Normalize unicode characters
    normalized = unicodedata.normalize('NFC', abs_path)

    # Handle long paths on Windows
    if platform.system() == 'Windows' and len(normalized) > 260:
        normalized = '\\\\?\\' + normalized

    return normalized

def should_exclude(path):
    """Check if the path should be excluded based on various criteria."""
    # Convert path to lowercase for case-insensitive comparison
    path_lower = path.lower()

    # Get the filename/directory name
    name = os.path.basename(path)

    # Exclude all hidden files and directories (starting with .)
    if name.startswith('.'):
        return True

    # Exclude System Volume Information directory
    if 'system volume information' in path_lower:
        return True

    # List of patterns to exclude (except .PKInstallSandboxManager)
    exclude_patterns = [
        'trash',
        'recycle.bin',
        'cache',
        'temp',
        'tmp',
        '.git',
        '.svn',
        'node_modules',
        '__pycache__',
        '.ds_store',
        'thumbs.db',
        '.spotlight-v100',
        '.documentrevisions-v100',
        '.fseventsd',
        '.trashes',
        '.apdisk',
        '.vol',
        '.temporaryitems',
        '.appledouble',
        '.lsoverride',
        '.db',
        '.localized',
        '.symvers',
        '.file',
        '.metadata_never_index',
        '.tmplist',
        '.tmpshare',
        '.pkinstalllog',
        # .PKInstallSandboxManager deliberately not excluded
    ]
    # Do not exclude .PKInstallSandboxManager
    if '.pkinstallsandboxmanager' in path_lower:
        return False
    if any(pattern in path_lower for pattern in exclude_patterns):
        return True
    # Check if directory is read-only
    if os.path.isdir(path):
        try:
            test_file = os.path.join(path, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except (OSError, IOError):
            return True
    return False

def get_file_info(path):
    """Get file information with error handling."""
    try:
        stats = os.stat(path)
        return {
            'size': stats.st_size if os.path.isfile(path) else None,
            'created': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    except (OSError, IOError) as e:
        return {
            'size': None,
            'created': None,
            'modified': None,
            'error': str(e)
        }

def scan_directory(path, retry_count=3, retry_delay=1):
    """Scan directory and return list of files and folders with their details."""
    items = []
    normalized_path = normalize_path(path)

    try:
        # List directory contents with retry mechanism
        for attempt in range(retry_count):
            try:
                dir_contents = os.listdir(normalized_path)
                break
            except (OSError, IOError) as e:
                if attempt == retry_count - 1:
                    print_colored(f"Failed to access directory after {retry_count} attempts: {normalized_path}", COLORS['ERROR'])
                    return items
                time.sleep(retry_delay)

        for item in dir_contents:
            try:
                full_path = os.path.join(normalized_path, item)
                normalized_full_path = normalize_path(full_path)

                # Skip excluded paths
                if should_exclude(normalized_full_path):
                    continue

                # Get file information with retry mechanism
                file_info = None
                for attempt in range(retry_count):
                    try:
                        file_info = get_file_info(normalized_full_path)
                        break
                    except (OSError, IOError) as e:
                        if attempt == retry_count - 1:
                            print_colored(f"Failed to get file info after {retry_count} attempts: {normalized_full_path}", COLORS['ERROR'])
                            continue
                        time.sleep(retry_delay)

                if file_info is None:
                    continue

                item_info = {
                    'name': item,
                    'type': 'directory' if os.path.isdir(normalized_full_path) else 'file',
                    'path': normalized_full_path,
                    **file_info
                }

                if os.path.isdir(normalized_full_path):
                    # Recursively scan subdirectories
                    sub_items = scan_directory(normalized_full_path, retry_count, retry_delay)
                    if sub_items:  # Only add directory if it has non-excluded contents
                        item_info['contents'] = sub_items
                        items.append(item_info)
                else:
                    items.append(item_info)

            except (OSError, IOError) as e:
                print_colored(f"Error processing {item}: {str(e)}", COLORS['ERROR'])
                continue

    except (OSError, IOError) as e:
        print_colored(f"Error scanning directory {normalized_path}: {str(e)}", COLORS['ERROR'])

    return items

def send_to_api(data):
    """Send disk data to the API endpoint."""
    try:
        response = requests.post(
            f"{API_CONFIG['base_url']}/api/get_disk_data",
            json=data,
            timeout=API_CONFIG['timeout']
        )
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        return False, str(e)

def save_disk_contents(disk_info):
    """Save disk contents to a JSON file and send to API."""
    # Use disk_id for the filename to ensure consistency
    filename = f"logs/disk_{disk_info['disk_id']}.json"

    print_colored("\nScanning disk contents (excluding trash, cache, and read-only directories)...", COLORS['INFO'])
    contents = scan_directory(disk_info['mountpoint'])

    data = {
        'timestamp': datetime.now().isoformat(),
        'system_info': {
            'os': platform.system(),
            'os_version': platform.version(),
            'hostname': platform.node()
        },
        'disk_info': disk_info,
        'contents': contents
    }

    # Save to local file
    os.makedirs('logs', exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Send to API
    print_colored("\nSending data to API...", COLORS['INFO'])
    success, response = send_to_api(data)

    if success:
        print_colored("Data successfully sent to API", COLORS['SUCCESS'])
    else:
        print_colored(f"Failed to send data to API: {response}", COLORS['ERROR'])

    return filename

def print_header():
    """Print a nice header for the application."""
    header = """
    ██████╗ ███████╗██╗     ██╗  ██╗██╗   ██╗██╗      ██████╗
    ██╔══██╗██╔════╝██║     ██║ ██╔╝██║   ██║██║     ██╔═══██╗
    ██████╔╝█████╗  ██║     █████╔╝ ██║   ██║██║     ██║   ██║
    ██╔═══╝ ██╔══╝  ██║     ██╔═██╗ ██║   ██║██║     ██║   ██║
    ██║     ███████╗███████╗██║  ██╗╚██████╔╝███████╗╚██████╔╝
    ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ╚═════╝
    """
    print_colored(header, COLORS['HEADER'])
    print_colored("Disk Monitoring System", COLORS['BOLD'])
    print_colored("=" * 50, COLORS['SEPARATOR'])

def print_disk_info(disk):
    """Print formatted disk information."""
    print_colored(f"\nDisk Information:", COLORS['BOLD'])
    print_colored(f"Name: {disk['label']}", COLORS['DISK_INFO'])
    print_colored(f"Device: {disk['device']}", COLORS['DISK_INFO'])
    print_colored(f"Mount Point: {disk['mountpoint']}", COLORS['DISK_INFO'])
    print_colored(f"File System: {disk['fstype']}", COLORS['DISK_INFO'])
    print_colored(f"Unique ID: {disk['serial']}", COLORS['DISK_INFO'])
    print_colored(f"Total Size: {format_size(disk['total_size'])}", COLORS['DISK_INFO'])
    print_colored(f"Used Space: {format_size(disk['used'])} ({disk['percent']}%)",
                 COLORS['GREEN'] if disk['percent'] < 80 else COLORS['WARNING'])
    print_colored(f"Free Space: {format_size(disk['free'])}",
                 COLORS['GREEN'] if disk['percent'] < 80 else COLORS['WARNING'])
    print_colored(f"Read/Write Status: {'Read-Write' if os.access(disk['mountpoint'], os.W_OK) else 'Read-Only'}",
                 COLORS['GREEN'] if os.access(disk['mountpoint'], os.W_OK) else COLORS['WARNING'])
    print_colored(f"Mount Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(disk['mountpoint'])))}",
                 COLORS['DISK_INFO'])
    print_colored(f"Device Type: {'Removable' if disk['device'].startswith('/dev/disk') else 'Fixed'}",
                 COLORS['DISK_INFO'])

def main():
    print_header()
    print_colored("Disk izleme sistemi başlatılıyor...", COLORS['INFO'])
    print_colored("Çıkmak için Ctrl+C tuşlarına basın", COLORS['INFO'])
    print_colored("-" * 50, COLORS['SEPARATOR'])

    # Disk izleme sistemini başlat
    monitor = DiskMonitor()
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print_colored("\nProgram sonlandırılıyor...", COLORS['INFO'])
        monitor.stop_all_monitoring()

if __name__ == "__main__":
    main()
