"""JSON logging configuration with request IDs."""
import json
import logging
import uuid
from typing import Any, Dict, Optional
from datetime import datetime
import sys

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        # Add user info if available
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        # Add entity info if available
        if hasattr(record, 'entity'):
            log_entry["entity"] = record.entity
        if hasattr(record, 'entity_id'):
            log_entry["entity_id"] = record.entity_id
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request IDs to all requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class StructuredLogger:
    """Structured logger with request context."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add console handler with JSON formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _log(self, level: int, message: str, request_id: Optional[str] = None, 
             user_id: Optional[str] = None, entity: Optional[str] = None, 
             entity_id: Optional[str] = None, extra_fields: Optional[Dict[str, Any]] = None):
        """Log with structured fields."""
        extra = {}
        if request_id:
            extra['request_id'] = request_id
        if user_id:
            extra['user_id'] = user_id
        if entity:
            extra['entity'] = entity
        if entity_id:
            extra['entity_id'] = entity_id
        if extra_fields:
            extra['extra_fields'] = extra_fields
        
        self.logger.log(level, message, extra=extra)
    
    def info(self, message: str, request_id: Optional[str] = None, 
             user_id: Optional[str] = None, entity: Optional[str] = None, 
             entity_id: Optional[str] = None, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, request_id, user_id, entity, entity_id, kwargs)
    
    def warning(self, message: str, request_id: Optional[str] = None, 
                user_id: Optional[str] = None, entity: Optional[str] = None, 
                entity_id: Optional[str] = None, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, request_id, user_id, entity, entity_id, kwargs)
    
    def error(self, message: str, request_id: Optional[str] = None, 
              user_id: Optional[str] = None, entity: Optional[str] = None, 
              entity_id: Optional[str] = None, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, message, request_id, user_id, entity, entity_id, kwargs)
    
    def debug(self, message: str, request_id: Optional[str] = None, 
              user_id: Optional[str] = None, entity: Optional[str] = None, 
              entity_id: Optional[str] = None, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, request_id, user_id, entity, entity_id, kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


# Global logger instance
logger = get_logger("tpmanuf")


def log_request(request: Request, message: str, level: str = "info", **kwargs):
    """Log a request with context."""
    request_id = getattr(request.state, 'request_id', None)
    user_id = getattr(request.state, 'user_id', None)
    
    log_method = getattr(logger, level.lower())
    log_method(message, request_id=request_id, user_id=user_id, **kwargs)


def log_entity_operation(entity: str, entity_id: str, operation: str, 
                        request_id: Optional[str] = None, user_id: Optional[str] = None, 
                        **kwargs):
    """Log an entity operation."""
    message = f"{operation} {entity} {entity_id}"
    logger.info(message, request_id=request_id, user_id=user_id, 
                entity=entity, entity_id=entity_id, **kwargs)
