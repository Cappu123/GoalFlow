# access and loads the environmental varables placed in the .env file
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    #Security
    SECRET_KEY: str

    #Algorithm
    #ALGORITHM: str

    #Token
    #ACCESS_TOKEN_EXPIRE_MINUTES: str
    ALLOWED_ORIGINS: str

    #API keys
    GROQ_API_KEY: str

    # class Config:
    #     env_file = ".env" this doesnt workanymore(only for pydantic v1)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
