import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(
            self,
            log_record: Dict[str, Any],
            record: logging.LogRecord,
            message_dict: Dict[str, Any]
        ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add module, function, and line info
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Preserve extra fields passed via extra={}
        for key, value in message_dict.items():
            if key not in log_record:
                log_record[key] = value


def setup_logging(debug: bool = False) -> logging.Logger:
    """Configure JSON logging for the application.
    
    Args:
        debug: Enable debug level logging
        
    Returns:
        Configured logger instance
    """
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Set JSON formatter
    formatter = CustomJsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s',
        rename_fields={
            'levelname': 'level',
            'name': 'logger',
            'funcName': 'function',
            'lineno': 'line'
        }
    )
    handler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.handlers.clear()  # Remove existing handlers
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    return logger
