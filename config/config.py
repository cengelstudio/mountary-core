"""
Configuration settings for the application.
"""

API_CONFIG = {
    'base_url': 'http://127.0.0.1:5001',
    'timeout': 30,  # seconds
    'retry_attempts': 3
}

LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(levelname)s - %(message)s',
    'log_file': 'logs/app.log'
}

DISK_CONFIG = {
    'scan_interval': 1,  # seconds
    'json_output_dir': 'logs',
    'disk_label': {
        'enabled': True,  # Enable/disable disk label validation
        'pattern': r'^[SH]-PLKL\d+TB\d+$',  # Regex pattern for disk labels
        'description': {
            'pattern': 'S-PLKL2TB4 format where:',
            'rules': [
                'First character: S (SSD) or H (HDD)',
                'PLKL: Company identifier',
                'Number: Storage capacity in TB',
                'Last number: Disk sequence number'
            ]
        }
    }
}

COLORS = {
    'HEADER': '\033[95m',      # Purple
    'BLUE': '\033[94m',        # Blue
    'GREEN': '\033[92m',       # Green
    'YELLOW': '\033[93m',      # Yellow
    'RED': '\033[91m',         # Red
    'BOLD': '\033[1m',         # Bold
    'UNDERLINE': '\033[4m',    # Underline
    'ENDC': '\033[0m',         # End color
    'SUCCESS': '\033[92m',     # Green
    'WARNING': '\033[93m',     # Yellow
    'ERROR': '\033[91m',       # Red
    'INFO': '\033[94m',        # Blue
    'DISK_INFO': '\033[96m',   # Cyan
    'SEPARATOR': '\033[90m'    # Gray
}
