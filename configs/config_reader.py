from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    bot_token: SecretStr
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int
    
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8'
    )

config = Settings()
