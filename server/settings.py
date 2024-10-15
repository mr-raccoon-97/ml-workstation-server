from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class RabbitMQSettings(BaseSettings):
    host: str = Field('localhost')
    port: int = Field(5672)

    @property
    def uri(self) -> str:
        return f"amqp://{self.host}:{self.port}"

class MongoDBSettings(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=27017)
    database: str = Field(default='tests')
    model_config = SettingsConfigDict(env_prefix='mongodb_')

    @property
    def uri(self):
        return f"mongodb://{self.host}:{self.port}"

class APISettings(BaseSettings):
    host: str = Field('localhost')
    port: int = Field(8000)

    @property
    def uri(self) -> str:
        return f"http://{self.host}:{self.port}"

class Settings(BaseSettings):
    api: APISettings = Field(default_factory=APISettings)
    rabbitmq: RabbitMQSettings = Field(default_factory=RabbitMQSettings)
    mongodb: MongoDBSettings = Field(default_factory=MongoDBSettings)