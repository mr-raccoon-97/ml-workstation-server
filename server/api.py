from contextlib import asynccontextmanager
from uuid import UUID
from logging import getLogger
from fastapi import FastAPI
from fastapi import Depends
from fastapi import WebSocket, WebSocketDisconnect
from server.endpoints import experiments, models
from server.settings import Settings
from server.adapters import MongoDB
from server.adapters import RabbitMQ
from server.adapters.experiments import Experiments
from server.handlers import handle_sessions, handle_models, handle_metrics

settings = Settings()
logger = getLogger(__name__)

mq = RabbitMQ(settings)
db = MongoDB(settings)

async def experiments_adapter() -> Experiments:
    return Experiments(db.database)

@asynccontextmanager
async def lifespan(api: FastAPI):
    await db.setup(), await mq.setup()
    yield
    await db.teardown(), await mq.teardown()

api = FastAPI(lifespan=lifespan)
api.include_router(experiments.router)
api.include_router(models.router)
api.dependency_overrides[experiments.port] = experiments_adapter

mq.handlers['models'] = handle_models
mq.handlers['sessions'] = handle_sessions
mq.handlers['metrics'] = handle_metrics

@api.websocket('/ws')
async def heartbeat(ws: WebSocket):
    await ws.accept()
    try:
        await mq.start()
        while True:
            await ws.receive_text()
            await ws.send_text('health')
    except WebSocketDisconnect:
        pass
    finally:
        await mq.stop()