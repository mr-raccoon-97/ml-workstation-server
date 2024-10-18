import pytest
from typing import AsyncGenerator
from server.settings import Settings, MongoDBSettings
from server.adapters import MongoDB
from server.adapters.experiments import Experiments

@pytest.fixture
def settings():
    return Settings(mongodb=MongoDBSettings(database='tests'))

@pytest.fixture
async def mongodb(settings: Settings) -> AsyncGenerator[MongoDB, None]:
    mongodb = MongoDB(settings)
    await mongodb.setup()
    try:
        yield mongodb
    finally:
        await mongodb.teardown()

@pytest.fixture
async def experiments(mongodb: MongoDB) -> AsyncGenerator[Experiments, None]:
    try:
        yield Experiments(mongodb.database)
    finally:
        await mongodb.database['experiments'].drop()
        await mongodb.database['models'].drop()