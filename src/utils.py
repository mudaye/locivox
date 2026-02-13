"""
Utility functions for Locivox
"""

import os
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"{Fore.RED}Config file not found: {config_path}{Style.RESET_ALL}")
        raise
    except yaml.YAMLError as e:
        print(f"{Fore.RED}Error parsing config file: {e}{Style.RESET_ALL}")
        raise


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """Setup logging based on config"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    
    # Create logs directory if it doesn't exist
    log_file = log_config.get('file', './logs/locivox.log')
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Setup logger
    logger = logging.getLogger('locivox')
    logger.setLevel(log_level)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (if enabled)
    if log_config.get('console', True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


def generate_output_filename(config: Dict[str, Any], prefix: str = "transcript") -> str:
    """Generate output filename with optional timestamp"""
    output_config = config.get('output', {})
    output_dir = output_config.get('directory', './output')
    output_format = output_config.get('format', 'txt')
    use_timestamp = output_config.get('timestamp', True)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    if use_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{output_format}"
    else:
        filename = f"{prefix}.{output_format}"
    
    return os.path.join(output_dir, filename)


def format_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def print_banner():
    """Print Locivox banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════╗
║         LOCIVOX v0.1.0               ║
║   Local Voice Transcription System   ║
╚══════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_status(message: str, status: str = "info"):
    """Print colored status messages"""
    colors = {
        "info": Fore.BLUE,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED
    }
    color = colors.get(status, Fore.WHITE)
    print(f"{color}[{status.upper()}] {message}{Style.RESET_ALL}")
