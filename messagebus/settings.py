from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class RabbitMQSettings(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=5672)
    exchange: str = Field(default='')
    prefetch_count: int = Field(default=1)

    @property
    def uri(self) -> str:
        return f"amqp://{self.host}:{self.port}"
    
class HealthCheckSettings(BaseSettings):
    timeout: int = Field(default=5)
    retries: int = Field(default=3)
    interval: int = Field(default=5)

class APISettings(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=8000)

    @property
    def uri(self) -> str:
        return f"http://{self.host}:{self.port}"

class Settings(BaseSettings):
    api: APISettings = Field(default_factory=APISettings)
    rabbitmq: RabbitMQSettings = Field(default_factory=RabbitMQSettings)
    healthcheck: HealthCheckSettings = Field(default_factory=HealthCheckSettings)