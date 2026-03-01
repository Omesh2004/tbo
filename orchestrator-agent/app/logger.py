"""Logging configuration"""
import logging
import json
from pythonjsonlogger import jsonlogger
from app.config import settings
import sys


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[92m',       # Green
        'WARNING': '\033[93m',    # Yellow
        'ERROR': '\033[91m',      # Red
        'CRITICAL': '\033[95m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Add color to level name
        record.levelname = f"{color}[{levelname}]{reset}"
        
        # Format the message
        if record.name.startswith('orchestrator'):
            record.name = f"{color}{record.name}{reset}"
        
        return super().format(record)


def setup_logger(name: str, verbose: bool = True) -> logging.Logger:
    """Setup logger with JSON and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Console Handler (Human readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if verbose or settings.debug:
        console_format = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_format = ColoredFormatter(
            '%(levelname)s | %(message)s'
        )
    
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # JSON Handler (for logging systems)
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setLevel(logging.INFO)
    json_formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        timestamp=True
    )
    json_handler.setFormatter(json_formatter)
    # Only add JSON handler if not in debug mode
    if not settings.debug:
        logger.addHandler(json_handler)
    
    return logger


# Main logger instance
logger = setup_logger("orchestrator.main")
