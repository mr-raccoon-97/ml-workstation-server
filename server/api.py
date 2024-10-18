from contextlib import asynccontextmanager
from logging import getLogger
from fastapi import FastAPI
from fastapi import WebSocket, WebSocketDisconnect
from server.endpoints import experiments, models, metrics, transactions
from server.settings import Settings
from server.adapters import MongoDB
from server.adapters.experiments import Experiments

settings = Settings()
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


from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status

@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    
    logger.error(request, exc_str)
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@api.websocket('/ws')
async def healthcheck(ws: WebSocket):
    await ws.accept()
    try:
        data = await ws.receive_bytes()
        if data == b'\x01':
            await ws.send_bytes(b'\x01')
        else:
            raise Exception("Healthcheck failed, unexpected data received")
    except WebSocketDisconnect:
        pass