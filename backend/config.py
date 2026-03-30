"""
FORTIS SENTINEL - Application Configuration

Uses Pydantic Settings for validated environment configuration.
Supports development (SQLite) and production (PostgreSQL) modes.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = Field(default="fortis-sentinel", description="Application name")
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    app_debug: bool = Field(default=True, description="Debug mode")
    app_version: str = Field(default="0.1.0", description="Application version")
    app_host: str = Field(default="0.0.0.0", description="Server host")
    app_port: int = Field(default=8000, description="Server port")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./fortis_sentinel.db",
        description="Database connection URL",
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # RabbitMQ / Celery
    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost:5672//", description="RabbitMQ URL")
    celery_broker_url: str = Field(default="amqp://guest:guest@localhost:5672//", description="Celery broker URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/1", description="Celery result backend")

    # JWT Authentication
    jwt_secret_key: str = Field(default="dev-secret-key-change-in-production", description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=60, description="JWT token expiration in minutes")

    # CORS
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated allowed origins",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format: json or text")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, description="API rate limit per minute")

    # Encryption
    encryption_key: str = Field(
        default="dev-encryption-key-change-in-prod!",
        description="AES encryption key",
    )

    # Frontend
    frontend_url: str = Field(default="http://localhost:5173", description="Frontend URL")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return "sqlite" in self.database_url

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
