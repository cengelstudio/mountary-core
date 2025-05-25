"""
Configuration settings for the application.
"""

# API Configuration
API_CONFIG = {
    'base_url': 'http://127.0.0.1:5000',
    'timeout': 30,  # seconds
    'retry_attempts': 3
}

# Logging Configuration
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(levelname)s - %(message)s',
    'log_file': 'logs/app.log'
}

# Disk Monitoring Configuration
DISK_CONFIG = {
    'scan_interval': 1,  # seconds
    'json_output_dir': 'logs'
}

# Terminal Colors Configuration
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
