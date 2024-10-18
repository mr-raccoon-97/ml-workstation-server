from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class MongoDBSettings(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=27017)
    database: str = Field(default='tests')
    model_config = SettingsConfigDict(env_prefix='mongodb_')

    @property
    def uri(self):
        return f"mongodb://{self.host}:{self.port}"

class APISettings(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=8000)

    @property
    def uri(self) -> str:
        return f"http://{self.host}:{self.port}"

class Settings(BaseSettings):
    api: APISettings = Field(default_factory=APISettings)
    mongodb: MongoDBSettings = Field(default_factory=MongoDBSettings)