"""Error handlers for FastAPI application."""
from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging_config import logger, log_request


class ValidationErrorResponse(JSONResponse):
    """Custom response for validation errors (422)."""
    
    def __init__(self, errors: List[Dict[str, Any]], request_id: Optional[str] = None):
        content = {
            "error": "Validation Error",
            "message": "The request data is invalid",
            "details": errors,
            "request_id": request_id
        }
        super().__init__(status_code=422, content=content)


class ConflictErrorResponse(JSONResponse):
    """Custom response for conflict errors (409)."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 request_id: Optional[str] = None):
        content = {
            "error": "Conflict",
            "message": message,
            "request_id": request_id
        }
        if details:
            content["details"] = details
        super().__init__(status_code=409, content=content)


class NotFoundErrorResponse(JSONResponse):
    """Custom response for not found errors (404)."""
    
    def __init__(self, message: str, entity: Optional[str] = None, 
                 entity_id: Optional[str] = None, request_id: Optional[str] = None):
        content = {
            "error": "Not Found",
            "message": message,
            "request_id": request_id
        }
        if entity and entity_id:
            content["entity"] = entity
            content["entity_id"] = entity_id
        super().__init__(status_code=404, content=content)


class InternalServerErrorResponse(JSONResponse):
    """Custom response for internal server errors (500)."""
    
    def __init__(self, message: str, request_id: Optional[str] = None, 
                 include_details: bool = False):
        content = {
            "error": "Internal Server Error",
            "message": message,
            "request_id": request_id
        }
        super().__init__(status_code=500, content=content)


def format_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format Pydantic validation errors for API response."""
    formatted_errors = []
    
    for error in errors:
        formatted_error = {
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        }
        formatted_errors.append(formatted_error)
    
    return formatted_errors


def register_error_handlers(app: FastAPI) -> None:
    """Register error handlers for the FastAPI application."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors (422)."""
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the validation error
        log_request(
            request, 
            f"Validation error: {exc.errors()}",
            level="warning",
            validation_errors=exc.errors()
        )
        
        # Format errors for response
        formatted_errors = format_validation_errors(exc.errors())
        
        return ValidationErrorResponse(formatted_errors, request_id)
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic ValidationError (422)."""
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the validation error
        log_request(
            request,
            f"Pydantic validation error: {exc.errors()}",
            level="warning",
            validation_errors=exc.errors()
        )
        
        # Format errors for response
        formatted_errors = format_validation_errors(exc.errors())
        
        return ValidationErrorResponse(formatted_errors, request_id)
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors (409)."""
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the integrity error
        log_request(
            request,
            f"Database integrity error: {str(exc.orig)}",
            level="error",
            sql_error=str(exc.orig)
        )
        
        # Determine conflict type and message
        error_str = str(exc.orig).lower()
        
        if "unique constraint" in error_str or "duplicate key" in error_str:
            message = "A record with this information already exists"
            details = {"constraint": "unique_violation"}
        elif "foreign key constraint" in error_str:
            message = "Referenced record does not exist"
            details = {"constraint": "foreign_key_violation"}
        elif "check constraint" in error_str:
            message = "Data violates business rules"
            details = {"constraint": "check_violation"}
        else:
            message = "Database constraint violation"
            details = {"constraint": "unknown"}
        
        return ConflictErrorResponse(message, details, request_id)
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """Handle general SQLAlchemy errors (500)."""
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the SQLAlchemy error
        log_request(
            request,
            f"SQLAlchemy error: {str(exc)}",
            level="error",
            sql_error=str(exc)
        )
        
        return InternalServerErrorResponse(
            "A database error occurred",
            request_id,
            include_details=False
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the HTTP exception
        log_request(
            request,
            f"HTTP exception: {exc.status_code} - {exc.detail}",
            level="warning" if exc.status_code < 500 else "error",
            status_code=exc.status_code
        )
        
        # Handle specific status codes
        if exc.status_code == 404:
            return NotFoundErrorResponse(
                str(exc.detail),
                request_id=request_id
            )
        elif exc.status_code == 409:
            return ConflictErrorResponse(
                str(exc.detail),
                request_id=request_id
            )
        elif exc.status_code == 422:
            return ValidationErrorResponse(
                [{"field": "request", "message": str(exc.detail), "type": "value_error"}],
                request_id
            )
        
        # Default HTTP exception response
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "message": str(exc.detail),
                "request_id": request_id
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle Starlette HTTP exceptions."""
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the Starlette HTTP exception
        log_request(
            request,
            f"Starlette HTTP exception: {exc.status_code} - {exc.detail}",
            level="warning" if exc.status_code < 500 else "error",
            status_code=exc.status_code
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "message": str(exc.detail),
                "request_id": request_id
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions (500)."""
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the general exception
        log_request(
            request,
            f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
            level="error",
            exception_type=type(exc).__name__,
            exception_message=str(exc)
        )
        
        return InternalServerErrorResponse(
            "An unexpected error occurred",
            request_id,
            include_details=False
        )


# Custom exception classes for business logic
class BusinessRuleViolation(Exception):
    """Raised when a business rule is violated."""
    
    def __init__(self, message: str, rule: Optional[str] = None, 
                 entity: Optional[str] = None, entity_id: Optional[str] = None):
        self.message = message
        self.rule = rule
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(message)


class InsufficientInventoryError(BusinessRuleViolation):
    """Raised when there's insufficient inventory for an operation."""
    
    def __init__(self, product_id: str, required_qty: float, available_qty: float):
        self.product_id = product_id
        self.required_qty = required_qty
        self.available_qty = available_qty
        message = f"Insufficient inventory for product {product_id}: required {required_qty}, available {available_qty}"
        super().__init__(message, rule="inventory_check", entity="product", entity_id=product_id)


class InvalidUnitConversionError(BusinessRuleViolation):
    """Raised when a unit conversion is invalid."""
    
    def __init__(self, from_unit: str, to_unit: str, product_id: Optional[str] = None):
        self.from_unit = from_unit
        self.to_unit = to_unit
        self.product_id = product_id
        message = f"Cannot convert from {from_unit} to {to_unit}"
        if product_id:
            message += f" for product {product_id}"
        super().__init__(message, rule="unit_conversion", entity="product", entity_id=product_id)


class PricingResolutionError(BusinessRuleViolation):
    """Raised when pricing resolution fails."""
    
    def __init__(self, product_id: str, pack_unit_id: str, customer_id: Optional[str] = None):
        self.product_id = product_id
        self.pack_unit_id = pack_unit_id
        self.customer_id = customer_id
        message = f"Cannot resolve price for product {product_id} with pack unit {pack_unit_id}"
        if customer_id:
            message += f" for customer {customer_id}"
        super().__init__(message, rule="pricing_resolution", entity="product", entity_id=product_id)


# Exception handler for custom business exceptions
async def business_exception_handler(request: Request, exc: BusinessRuleViolation):
    """Handle business rule violations (422)."""
    request_id = getattr(request.state, 'request_id', None)
    
    # Log the business rule violation
    log_request(
        request,
        f"Business rule violation: {exc.message}",
        level="warning",
        rule=exc.rule,
        entity=exc.entity,
        entity_id=exc.entity_id
    )
    
    content = {
        "error": "Business Rule Violation",
        "message": exc.message,
        "rule": exc.rule,
        "request_id": request_id
    }
    
    if exc.entity and exc.entity_id:
        content["entity"] = exc.entity
        content["entity_id"] = exc.entity_id
    
    return JSONResponse(status_code=422, content=content)
