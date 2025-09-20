"""
Centralized logging configuration for SEO Manager
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = "seo_manager.log",
    console_output: bool = True,
    log_format: Optional[str] = None
):
    """
    Configure logging for the SEO Manager application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. None to disable file logging
        console_output: Whether to output logs to console
        log_format: Custom log format string
    """

    # Default log format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(exist_ok=True)

    # Configure root logger
    handlers = []

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=handlers,
        force=True  # Override existing configuration
    )

    return logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)


def set_log_level(level: str):
    """Change the log level for all handlers"""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    for handler in root_logger.handlers:
        handler.setLevel(numeric_level)


# Predefined logging configurations
class LoggingConfig:
    """Predefined logging configurations"""

    @staticmethod
    def development():
        """Development configuration with debug info"""
        setup_logging(
            log_level="DEBUG",
            log_file="logs/seo_debug.log",
            console_output=True
        )

    @staticmethod
    def production():
        """Production configuration with minimal console output"""
        setup_logging(
            log_level="INFO",
            log_file="logs/seo_production.log",
            console_output=False
        )

    @staticmethod
    def testing():
        """Testing configuration with detailed logging"""
        setup_logging(
            log_level="DEBUG",
            log_file="logs/seo_testing.log",
            console_output=True,
            log_format="%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s"
        )

    @staticmethod
    def console_only():
        """Console-only logging for demonstrations"""
        setup_logging(
            log_level="INFO",
            log_file=None,
            console_output=True,
            log_format="%(levelname)s - %(message)s"
        )