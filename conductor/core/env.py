from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"


load_dotenv()

settings = Settings()
