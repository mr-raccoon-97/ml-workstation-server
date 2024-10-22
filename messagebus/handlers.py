from typing import Callable
from aio_pika import IncomingMessage, Queue, Channel
from aiohttp import ClientSession, ClientResponse
from logging import getLogger

logger = getLogger(__name__)
        
def is_ok(response: ClientResponse):
    match response.status:
        case 200 | 201 | 204:
            logger.info(f"Response OK with status {response.status}")
            return True            
        case 404 | 409 | 422:
            logger.info(f"Response failed with status {response.status}")
            return False
        case default:
            raise Exception(f"Unexpected response {response} with status {response.status}")
        

async def handle_models(message: IncomingMessage, session: ClientSession):
    async with message.process(requeue=True, ignore_processed=True):
        id = message.headers['X-Resource-ID']
        logger.info(f"Processing model with ID {id}")
        async with await session.patch(f'/models/{id}/', data=message.body, headers={'Content-Type': 'application/json'}) as response:
            await message.ack() if is_ok(response) else await message.nack(requeue=False)

                
async def handle_transactions(message: IncomingMessage, session: ClientSession):
    async with message.process(requeue=True, ignore_processed=True):
        id = message.headers['X-Resource-ID']
        logger.info(f"Processing transaction for model with ID {id}")
        async with await session.post(f'/models/{id}/transactions/', data=message.body, headers={'Content-Type': 'application/json'}) as response:
            await message.ack() if is_ok(response) else await message.nack(requeue=False)

async def handle_metrics(message: IncomingMessage, session: ClientSession):
    async with message.process(requeue=True, ignore_processed=True):
        id = message.headers['X-Resource-ID']
        logger.info(f"Processing metric for model with ID {id}")
        async with await session.post(f'/models/{id}/metrics/', data=message.body, headers={'Content-Type': 'application/json'}) as response:
            await message.ack() if is_ok(response) else await message.nack(requeue=False)