from fastapi import FastAPI
from asyncio import gather
from messagebus.settings import Settings
from messagebus.handlers import handle_metrics, handle_transactions, handle_models
from messagebus.adapter import RabbitMQ
from logging import getLogger

logger = getLogger(__name__)
settings = Settings()
mq = RabbitMQ(settings)
mq.include_handler('models', handle_models)
mq.include_handler('metrics', handle_metrics)
mq.include_handler('transactions', handle_transactions)

async def lifespan(api: FastAPI):
    await mq.setup()
    await mq.start_consuming()
    yield
    await mq.teardown()

api = FastAPI(lifespan=lifespan)