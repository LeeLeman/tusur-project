from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    SECRET_KEY: str


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
