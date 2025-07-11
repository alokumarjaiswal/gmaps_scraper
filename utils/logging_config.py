"""
Logging Configuration Module

This module handles logging setup and custom formatters for the Google Maps scraper.

File: gmaps_scraper/utils/logging_config.py
"""

import logging
import sys
import os
import re
from pathlib import Path
from typing import Optional

try:
    from config import LOGGING_CONFIG, OUTPUT_CONFIG
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import LOGGING_CONFIG, OUTPUT_CONFIG


class ConsoleFormatter(logging.Formatter):
    """Custom formatter that removes emojis for console output on Windows."""
    
    def format(self, record):
        # Remove emojis and other Unicode symbols that cause issues on Windows console
        message = super().format(record)
        # Remove common emojis used in the script
        emoji_pattern = r'[🚀✅📊📅🔄🔍🖼️📸💾❌⚠️➡️🎉🤖📜🖱️]+'
        clean_message = re.sub(emoji_pattern, '', message)
        return clean_message


def setup_logging(log_file: Optional[str] = None, 
                 log_level: Optional[int] = None,
                 verbose: bool = False,
                 log_dir: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration for the scraper.
    
    Args:
        log_file: Name of the log file (defaults to config value)
        log_level: Logging level (defaults to config value)
        verbose: Enable verbose logging
        log_dir: Directory to store log files (defaults to config value)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Use config defaults if not provided
    if log_file is None:
        log_file = OUTPUT_CONFIG["log_file"]
    if log_dir is None:
        log_dir = "logs"  # Keep existing default
    if log_level is None:
        log_level = getattr(logging, LOGGING_CONFIG["level"])
    
    # Set console encoding for Windows
    if sys.platform == "win32":
        try:
            # Try to set console to UTF-8
            os.system('chcp 65001 >nul')
        except:
            pass
    
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Set log level based on verbose flag
    if verbose:
        log_level = logging.DEBUG
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(
        log_path / log_file, 
        encoding='utf-8'
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Console handler with custom formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        ConsoleFormatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, console_handler]
    )
    
    # Return logger for this module
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {logging.getLevelName(log_level or logging.INFO)}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the module/logger
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)