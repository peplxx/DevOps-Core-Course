from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    
    # Application Metadata
    app_name: str = "devops-info-service"
    app_version: str = "1.0.0"
    app_description: str = "DevOps course info service"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
