"""
Structured logging configuration for Flask application.
Provides consistent logging across all modules with proper formatting and handlers.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

try:
    import colorama
    colorama.init()  # Initialize colorama for Windows support
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

from .config import BaseConfig


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'  # Reset color
    BOLD = '\033[1m'   # Bold text
    
    def __init__(self, *args, use_colors=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_colors = use_colors and self._supports_color()
    
    def _supports_color(self):
        """Check if the terminal supports colors."""
        # Check if we're in a terminal that supports colors
        if not (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()):
            return False
        
        # If colorama is available, we can use colors on Windows
        if COLORAMA_AVAILABLE:
            return True
            
        # Check for other color-supporting terminals
        return (
            sys.platform != 'win32' or 
            'ANSICON' in os.environ or 
            'WT_SESSION' in os.environ or 
            os.environ.get('TERM_PROGRAM') == 'vscode' or
            os.environ.get('COLORTERM') is not None
        )
    
    def format(self, record):
        # Add request ID if available (for future request tracking)
        if hasattr(record, 'request_id'):
            record.msg = f"[{record.request_id}] {record.msg}"
        
        # Format the message
        formatted = super().format(record)
        
        if not self.use_colors:
            return formatted
        
        # Apply colors based on log level
        level_name = record.levelname
        if level_name in self.COLORS:
            color = self.COLORS[level_name]
            # Color the entire message for better visibility
            formatted = f"{color}{self.BOLD}{level_name}{self.RESET}{color} - {formatted[len(level_name)+3:]}{self.RESET}"
        
        return formatted


class RequestFormatter(ColoredFormatter):
    """Custom formatter that includes request context and colors."""
    pass


def setup_logging(config: BaseConfig) -> None:
    """
    Configure logging based on application configuration.
    
    Args:
        config: Application configuration instance
    """
    # Create logs directory if it doesn't exist
    if config.LOG_FILE:
        log_path = Path(config.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    console_formatter = ColoredFormatter(config.LOG_FORMAT, use_colors=True)
    file_formatter = logging.Formatter(config.LOG_FORMAT)  # No colors for file output
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation (if configured) - no colors
    if config.LOG_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    _configure_library_loggers(config)
    
    # Log configuration startup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {config.LOG_LEVEL}, File: {config.LOG_FILE}")


def _configure_library_loggers(config: BaseConfig) -> None:
    """Configure logging levels for third-party libraries."""
    
    # Reduce noise from third-party libraries
    library_loggers = {
        'urllib3.connectionpool': logging.WARNING,
        'requests.packages.urllib3': logging.WARNING,
        'werkzeug': logging.WARNING if config.LOG_LEVEL != 'DEBUG' else logging.INFO,
        'flask.app': logging.INFO,
    }
    
    for logger_name, level in library_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with consistent configuration.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class RequestLoggingMiddleware:
    """Middleware to log HTTP requests and responses."""
    
    def __init__(self, app, config: BaseConfig):
        self.app = app
        self.config = config
        self.logger = get_logger(__name__)
    
    def __call__(self, environ, start_response):
        """WSGI middleware to log requests."""
        
        def new_start_response(status, response_headers, exc_info=None):
            # Log response
            if self.config.LOG_LEVEL == 'DEBUG':
                self.logger.debug(
                    f"Response: {status} - "
                    f"{environ.get('REQUEST_METHOD')} {environ.get('PATH_INFO')}"
                )
            return start_response(status, response_headers, exc_info)
        
        # Log request
        if self.config.LOG_LEVEL == 'DEBUG':
            self.logger.debug(
                f"Request: {environ.get('REQUEST_METHOD')} {environ.get('PATH_INFO')} - "
                f"Remote: {environ.get('REMOTE_ADDR')}"
            )
        
        return self.app(environ, new_start_response)