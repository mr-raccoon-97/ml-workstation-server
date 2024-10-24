from contextlib import asynccontextmanager
from logging import getLogger
from fastapi import FastAPI
from server.endpoints import experiments, models, metrics, transactions
from server.settings import Settings, MongoDBSettings
from server.adapters import MongoDB
from server.adapters.experiments import Experiments

settings = Settings(database=MongoDBSettings(database='tesis'))
logger = getLogger(__name__)
engine = MongoDB(settings)

@asynccontextmanager
async def lifespan(api: FastAPI):
    await engine.setup()
    yield
    await engine.teardown()

async def experiments_adapter() -> Experiments:
    return Experiments(engine.database)

api = FastAPI(lifespan=lifespan)
api.include_router(experiments.router)
api.include_router(models.router)
api.include_router(metrics.router)
api.include_router(transactions.router)
api.dependency_overrides[experiments.port] = experiments_adapter