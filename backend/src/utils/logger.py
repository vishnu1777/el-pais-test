import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class Logger:
    """Centralized logging configuration."""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Configure the logger with appropriate handlers and formatting."""
        self._logger = logging.getLogger('elpais_scraper')
        self._logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self._logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self._logger
    
    @classmethod
    def info(cls, message: str) -> None:
        """Log info message."""
        logger = cls().get_logger()
        logger.info(message)
    
    @classmethod
    def error(cls, message: str) -> None:
        """Log error message."""
        logger = cls().get_logger()
        logger.error(message)
    
    @classmethod
    def warning(cls, message: str) -> None:
        """Log warning message."""
        logger = cls().get_logger()
        logger.warning(message)
    
    @classmethod
    def debug(cls, message: str) -> None:
        """Log debug message."""
        logger = cls().get_logger()
        logger.debug(message)
