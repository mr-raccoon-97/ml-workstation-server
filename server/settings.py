from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class DatabaseSettings(BaseSettings):
    ...

class MongoDBSettings(DatabaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=27017)
    database: str = Field(default='tests')
    model_config = SettingsConfigDict(env_prefix='mongodb_')

    @property
    def uri(self):
        return f"mongodb://{self.host}:{self.port}"
    
class AtlasSettings(DatabaseSettings):
    uri: str = Field(...)
    database: str = Field(...)
    model_config = SettingsConfigDict(env_prefix='atlas_')


class APISettings(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=8000)

    @property
    def uri(self) -> str:
        return f"http://{self.host}:{self.port}"

class Settings(BaseSettings):
    api: APISettings = Field(default_factory=APISettings)
    database: DatabaseSettings = Field(default_factory=MongoDBSettings)