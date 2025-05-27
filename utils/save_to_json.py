import json
from datetime import datetime
import platform
import os

def save_to_json(disks):
    data = {
        'timestamp': datetime.now().isoformat(),
        'system_info': {
            'os': platform.system(),
            'os_version': platform.version(),
            'hostname': platform.node()
        },
        'disks': disks
    }

    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)

    # Create filename with timestamp in logs directory
    filename = os.path.join('logs', f"external_disks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return filename
