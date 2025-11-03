"""Pydantic settings for environment configuration."""

from pathlib import Path
from typing import List, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    # Database URL
    database_url: str = Field(
        default="sqlite:///./tpmanuf.db", description="Database connection URL"
    )

    # Connection pool settings
    pool_size: int = Field(default=5, ge=1, le=20)
    max_overflow: int = Field(default=10, ge=0, le=50)
    pool_timeout: int = Field(default=30, ge=1, le=300)
    pool_recycle: int = Field(default=3600, ge=300, le=7200)

    # Migration settings
    alembic_config_path: str = Field(default="alembic.ini")

    class Config:
        env_prefix = "DB_"


class APISettings(BaseSettings):
    """API configuration settings."""

    # Server settings
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000, ge=1, le=65535)
    debug: bool = Field(default=False)
    reload: bool = Field(default=False)

    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:8050"]
    )
    cors_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    cors_headers: List[str] = Field(default=["*"])

    # Security settings
    secret_key: str = Field(default="your-secret-key-change-in-production")
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)

    # Rate limiting
    rate_limit_per_minute: int = Field(default=100, ge=1, le=10000)

    class Config:
        env_prefix = "API_"


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    # Log level
    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # Log format
    format: str = Field(default="json", pattern="^(json|text)$")

    # Log file settings
    file_enabled: bool = Field(default=False)
    file_path: Optional[str] = Field(default=None)
    file_max_size: int = Field(default=10485760, ge=1024)  # 10MB
    file_backup_count: int = Field(default=5, ge=1, le=50)

    # Structured logging fields
    include_request_id: bool = Field(default=True)
    include_user_id: bool = Field(default=True)
    include_entity_info: bool = Field(default=True)

    class Config:
        env_prefix = "LOG_"


class UISettings(BaseSettings):
    """UI configuration settings."""

    # Dash server settings
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8050, ge=1, le=65535)
    debug: bool = Field(default=False)

    # API connection
    api_base_url: str = Field(default="http://127.0.0.1:8000")
    api_timeout: int = Field(default=30, ge=1, le=300)

    # UI features
    enable_demo_mode: bool = Field(default=True)
    show_debug_info: bool = Field(default=False)

    class Config:
        env_prefix = "UI_"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""

    # JWT settings
    jwt_secret_key: str = Field(default="your-jwt-secret-key-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    jwt_refresh_token_expire_days: int = Field(default=7, ge=1, le=30)

    # Password settings
    password_min_length: int = Field(default=8, ge=6, le=128)
    password_require_uppercase: bool = Field(default=True)
    password_require_lowercase: bool = Field(default=True)
    password_require_numbers: bool = Field(default=True)
    password_require_special_chars: bool = Field(default=True)

    # Session settings
    session_cookie_name: str = Field(default="tpmanuf_session")
    session_cookie_secure: bool = Field(default=False)
    session_cookie_httponly: bool = Field(default=True)
    session_cookie_samesite: str = Field(default="lax")

    class Config:
        env_prefix = "SECURITY_"


class BusinessSettings(BaseSettings):
    """Business logic configuration settings."""

    # Default tax rate (as percentage)
    default_tax_rate: float = Field(default=10.0, ge=0.0, le=100.0)

    # Inventory settings
    allow_negative_inventory: bool = Field(default=False)
    require_lot_expiry_dates: bool = Field(default=False)
    default_lot_expiry_days: int = Field(default=365, ge=1, le=3650)

    # Pricing settings
    enable_dynamic_pricing: bool = Field(default=False)
    price_rounding_precision: int = Field(default=2, ge=0, le=6)

    # Batch settings
    require_qc_for_completion: bool = Field(default=True)
    auto_generate_batch_codes: bool = Field(default=True)
    batch_code_prefix: str = Field(default="B")

    # Invoice settings
    invoice_number_prefix: str = Field(default="INV-")
    invoice_due_days: int = Field(default=30, ge=1, le=365)

    class Config:
        env_prefix = "BUSINESS_"


class ShopifySettings(BaseSettings):
    """Shopify integration configuration settings."""

    store: AnyHttpUrl = Field(
        default="https://yourstore.myshopify.com", description="Shopify store URL"
    )
    access_token: str = Field(default="shpat_xxx", description="Shopify access token")
    location_id: Optional[str] = Field(
        default=None, description="Shopify location ID (for multi-location setups)"
    )
    webhook_secret: Optional[str] = Field(
        default=None, description="Shopify webhook secret for HMAC verification"
    )

    class Config:
        env_prefix = "SHOPIFY_"


class Settings(BaseSettings):
    """Main application settings."""

    # Environment
    environment: str = Field(
        default="development", pattern="^(development|staging|production)$"
    )
    app_name: str = Field(default="TPManuf Modern System")
    app_version: str = Field(default="1.0.0")

    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: APISettings = Field(default_factory=APISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    ui: UISettings = Field(default_factory=UISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    business: BusinessSettings = Field(default_factory=BusinessSettings)
    shopify: ShopifySettings = Field(default_factory=ShopifySettings)

    # File paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "data"
    )
    logs_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "logs"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env

        # Allow nested settings
        env_nested_delimiter = "__"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def get_database_url() -> str:
    """Get the database URL from settings."""
    return settings.database.database_url


def is_development() -> bool:
    """Check if running in development mode."""
    return settings.environment == "development"


def is_production() -> bool:
    """Check if running in production mode."""
    return settings.environment == "production"
