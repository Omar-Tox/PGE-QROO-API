from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de datos
    DB_CONNECTION: str = "postgresql"
    DB_HOST: str
    DB_PORT: int
    DB_DATABASE: str
    DB_USERNAME: str
    DB_PASSWORD: str

    #Configuración de CORS
    # Definimos que es una lista de URLs
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
      # Integraciones
    LARAVEL_LOGIN_URL: str
    
    # 📌 NUEVO: API Key de Google Gemini
    GEMINI_API_KEY: str  
    # Validador: Convierte el string del .env a una lista real de Python
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Esto permite variables extra en el .env sin que falle, 
        # aunque es mejor tenerlas definidas arriba.
        extra = "ignore" 

settings = Settings()