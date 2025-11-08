"""Main FastAPI application with logging, settings, and error handling."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    assemblies,
    batches,
    contacts,
    excise_rates,
    formulas,
    invoices,
    packing,
    pricing,
    products,
    purchase_formats,
    raw_materials,
    reports,
    sales,
    shopify,
    suppliers,
    units,
    work_areas,
    work_orders,
)
from app.error_handlers import (
    BusinessRuleViolation,
    business_exception_handler,
    register_error_handlers,
)
from app.logging_config import RequestIDMiddleware, logger
from app.settings import settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="TPManuf Modern API - Trade Paints Manufacturing System",
        version=settings.app_version,
        debug=settings.api.debug,
        docs_url="/docs" if settings.api.debug else None,
        redoc_url="/redoc" if settings.api.debug else None,
    )

    # Add middleware
    app.add_middleware(RequestIDMiddleware)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=settings.api.cors_methods,
        allow_headers=settings.api.cors_headers,
    )

    # Register error handlers
    register_error_handlers(app)
    app.add_exception_handler(BusinessRuleViolation, business_exception_handler)

    # Include routers
    app.include_router(products.router, prefix="/api/v1")
    app.include_router(pricing.router, prefix="/api/v1")
    app.include_router(packing.router, prefix="/api/v1")
    app.include_router(invoices.router, prefix="/api/v1")
    app.include_router(batches.router, prefix="/api/v1")
    app.include_router(raw_materials.router, prefix="/api/v1")
    app.include_router(formulas.router, prefix="/api/v1")
    app.include_router(reports.router, prefix="/api/v1")
    app.include_router(suppliers.router, prefix="/api/v1")
    app.include_router(contacts.router, prefix="/api/v1")
    app.include_router(assemblies.router, prefix="/api/v1")
    app.include_router(shopify.router, prefix="/api/v1")
    app.include_router(units.router, prefix="/api/v1")
    app.include_router(excise_rates.router, prefix="/api/v1")
    app.include_router(purchase_formats.router, prefix="/api/v1")
    app.include_router(work_areas.router, prefix="/api/v1")
    app.include_router(work_orders.router, prefix="/api/v1")
    app.include_router(sales.router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health")
    def health():
        """Health check endpoint."""
        return {
            "status": "ok",
            "version": settings.app_version,
            "environment": settings.environment,
        }

    # Root endpoint
    @app.get("/")
    def root():
        """Root endpoint with API information."""
        return {
            "message": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "docs": "/docs" if settings.api.debug else "disabled",
            "health": "/health",
        }

    # Log application startup
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version}",
        environment=settings.environment,
        debug_mode=settings.api.debug,
        database_url=settings.database.database_url.split("://")[
            0
        ],  # Log only protocol, not credentials
    )

    return app


# Create the app instance
app = create_app()
