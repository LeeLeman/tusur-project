from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    TEST_DATABASE_URL: str = ""
    ROOT_PATH: str = ""


settings = Settings()
