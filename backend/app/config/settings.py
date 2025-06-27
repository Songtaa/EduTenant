import secrets
import warnings
from typing import Annotated, Any, Literal
import os

from pydantic import (
    AnyUrl,
    BeforeValidator,
    ConfigDict,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")
    
    # --- Core Application Settings ---
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EduTenant Management App"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    DOMAIN: str = "localhost"
    DOCKER: bool = os.getenv("DOCKER", "false").lower() == "true"

    # --- Security Settings ---
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRY: int = 3600  # 1 hour
    REFRESH_TOKEN_EXPIRY: int = 86400  # 24 hours
    JTI_EXPIRY: int = 3600

    # --- Multi-Tenancy Specific Settings ---
    DEFAULT_TENANT_SCHEMA_PREFIX: str = "tenant_"
    TENANT_COOKIE_NAME: str = "X-Tenant-ID"
    TENANT_HEADER_NAME: str = "X-Tenant-ID"
    TENANT_SUBDOMAIN_PARTS: int = 1  # tenant1.domain.com

    # --- Database Settings ---
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "edutenant_db")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "postgres" if DOCKER else "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    #  --- Default Tenant and admin ---
    INIT_DEFAULT_TENANT: bool = os.getenv("INIT_DEFAULT_TENANT", "false").lower() == "true"
    DEFAULT_TENANT_SCHEMA: str = os.getenv("DEFAULT_TENANT_SCHEMA", "school_alpha")
    DEFAULT_TENANT_ADMIN_EMAIL: str = os.getenv("DEFAULT_TENANT_ADMIN_EMAIL", "admin@schoolalpha.com")
    DEFAULT_TENANT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_TENANT_ADMIN_PASSWORD", "securepass")
    DEFAULT_TENANT_NAME: str = os.getenv("DEFAULT_TENANT_NAME","ACME_Inc")
    DEFAULT_TENANT_ADMIN_NAME: str = os.getenv("DEFAULT_TENANT_NAME"," Admin")
    DEFAULT_TENANT_ADMIN_ROLE: str = os.getenv("DEFAULT_TENANT_ADMIN_ROLE", "admin")
    DEFAULT_BILLING_TIER: str = os.getenv("DEFAULT_BILLING_TIER", "Basic")


    # --- Redis Settings ---
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: str = "6379"
    REDIS_PASSWORD: str = ""
    REDIS_USER: str = ""
    REDIS_NODE: str = "0"
    REDIS_MAX_RETRIES: int = 3
    REDIS_RETRY_INTERVAL: int = 10

    # --- Email Settings ---
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEST_USER: str = "test@example.com"

     # ... other settings ...
    DEBUG: bool = False
    SQLALCHEMY_ECHO: bool = False  # Separate control for SQL logging


    # --- First Superuser ---
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "supersecure"
    FIRST_SUPERUSER_NAME: str = "Global Admin"
    FIRST_SUPERUSER_ROLE: str = "admin"

    # --- CORS Settings ---
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []
    

    # ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    DOCKER: bool = os.getenv("DOCKER", "false").lower() == "true"

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "edutenant_db")

    # Dynamically choose the Postgres server based on Docker environment
    POSTGRES_SERVER: str = (
        os.getenv("POSTGRES_SERVER", "localhost") if not DOCKER else "postgres"
    )
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    PROJECT_NAME: str ="FastEdu Management App"
    # SENTRY_DSN: HttpUrl | None = None
    # POSTGRES_SERVER: str = "postgres"
    # POSTGRES_PORT: int = 5432
    # POSTGRES_USER: str = "postgres"
    # POSTGRES_PASSWORD: str = "password"
    # POSTGRES_DB: str = "fastedu_db"
    # REDIS_HOST: str
    # REDIS_PORT: int
    # REDIS_URL: str
    JTI_EXPIRY: int = 3600



    REDIS_HOST:str="127.0.0.1"
    REDIS_PORT:str="6379"
    REDIS_PASSWORD:str=''
    REDIS_USER:str=''
    REDIS_NODE:str="0"
    REDIS_MAX_RETRIES:int = 3
    REDIS_RETRY_INTERVAL:int=10
    

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """Main database URL (used as base for both master and shared)"""
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def MASTER_DB_URL(self) -> PostgresDsn:
        """For public schema operations - returns the same URL as SQLALCHEMY_DATABASE_URI"""
        return self.SQLALCHEMY_DATABASE_URI  # No parentheses - it's a property

    @computed_field
    @property
    def SHARED_DB_URL(self) -> PostgresDsn:
        """For tenant schema operations - same URL but different usage context"""
        return self.SQLALCHEMY_DATABASE_URI  # No parentheses - it's a property

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        auth = f"{self.REDIS_USER}:{self.REDIS_PASSWORD}@" if self.REDIS_USER else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_NODE}"

    @computed_field
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # --- Validators ---
    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        def check_default(var_name: str, value: str | None) -> None:
            if value == "changeme":
                msg = f'{var_name} must be changed from default value "changeme"'
                if self.ENVIRONMENT == "local":
                    warnings.warn(msg, stacklevel=1)
                else:
                    raise ValueError(msg)

        check_default("SECRET_KEY", self.SECRET_KEY)
        check_default("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        check_default("FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD)
        return self
    
    @model_validator(mode="after")
    def _set_debug_mode(self) -> Self:
        """Automatically enable debug in local environment"""
        if self.ENVIRONMENT == "local" and not self.DEBUG:
            self.DEBUG = True
            self.SQLALCHEMY_ECHO = True
        return self


settings = Settings()
# print(settings.SHARED_DB_URL)
