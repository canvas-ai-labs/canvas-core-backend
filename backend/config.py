import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        self.canvas_api_url = os.getenv("CANVAS_API_URL")
        self.canvas_api_key = os.getenv("CANVAS_API_KEY")
        self.database_url = os.getenv("DATABASE_URL")
        
        if not self.canvas_api_url:
            raise ValueError("CANVAS_API_URL environment variable is required")
        if not self.canvas_api_key:
            raise ValueError("CANVAS_API_KEY environment variable is required")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()