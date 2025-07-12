import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    google_translate_api_key: Optional[str] = Field(None, env="GOOGLE_TRANSLATE_API_KEY")
    rapid_api_key: Optional[str] = Field(None, env="RAPID_API_KEY")
    
    # BrowserStack Configuration
    browserstack_username: Optional[str] = Field(None, env="BROWSERSTACK_USERNAME")
    browserstack_access_key: Optional[str] = Field(None, env="BROWSERSTACK_ACCESS_KEY")
    
    # Scraping Configuration
    base_url: str = "https://elpais.com"
    opinion_section_url: str = "https://elpais.com/opinion/"
    max_articles: int = 5
    request_timeout: int = 30
    implicit_wait: int = 10
    
    # File Storage
    images_dir: str = "scraped_images"
    data_dir: str = "scraped_data"
    
    # Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.images_dir, exist_ok=True)
os.makedirs(settings.data_dir, exist_ok=True)
