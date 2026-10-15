import os

class Settings:
    PROJECT_NAME: str = "DomainLens API"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")

settings = Settings()
