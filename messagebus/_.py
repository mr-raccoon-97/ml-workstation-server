from contextlib import asynccontextmanager
from aiohttp import ClientSession, WSMessage, WSMsgType
from asyncio import TimeoutError
from asyncio import wait_for, sleep
from logging import getLogger
from messagebus.settings import Settings

logger = getLogger(__name__)

def is_ok(response: WSMessage):
    match response.type:
        case WSMsgType.PONG:
            logger.info(f"Server health")
            return True
        case WSMsgType.BINARY:  
            logger.info(f"Server health")
            return True
        case WSMsgType.CLOSE:
            logger.error(f"Healthcheck failed, server closed connection")
            return False
        case WSMsgType.ERROR:
            logger.error(f"Healthcheck failed, server returned an error")
            return False
        case default:
            raise Exception(f"Healthcheck failed, unexpected response type {default}")
            
@asynccontextmanager
async def healthcheck(session: ClientSession, settings: Settings):
    logger.info("Starting healthcheck")
    for retry in range(1, settings.healthcheck.retries + 1):
        try:
            logger.info(f"Healthcheck attempt {retry}")
            async with session.ws_connect(f'{settings.api.uri}/ws') as ws:
                await ws.ping(b'\x01')
                try:
                    response = await wait_for(ws.receive(), timeout=settings.healthcheck.timeout)
                    if is_ok(response):
                        yield
                        break
                except TimeoutError:
                    raise Exception("Healthcheck timed out")

        except Exception as error:
            logger.error(error)
            await sleep(settings.healthcheck.interval)
