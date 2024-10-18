from typing import Callable
from aio_pika import IncomingMessage, Queue, Channel
from aiohttp import ClientSession

async def handle_models(message: IncomingMessage, session: ClientSession):
    async with message.process(requeue=True):
        id = message.headers['X-Resource-ID']
        async with await session.patch(f'/models/{id}/', data=message.body) as response:
            if response.status == 204:
                message.ack()
            elif response.status == 404:
                message.nack(requeue=False)
            elif response.status == 500:
                raise Exception(f"Server error {response.status}")
            else:
                raise Exception(f"Unexpected response status {response.status}")

                
async def handle_transactions(message: IncomingMessage, session: ClientSession):
    async with message.process(requeue=True):
        id = message.headers['X-Resource-ID']
        async with await session.post(f'/models/{id}/transactions/', data=message.body) as response:
            if response.status == 201:
                message.ack()
            elif response.status == 404:
                message.nack(requeue=False)
            elif response.status == 500:
                raise Exception(f"Server error {response.status}")
            else:
                raise Exception(f"Unexpected response status {response.status}")
            

async def handle_metrics(message: IncomingMessage, session: ClientSession):
    async with message.process(requeue=True):
        id = message.headers['X-Resource-ID']
        async with await session.post(f'/models/{id}/metrics/', data=message.body) as response:
            if response.status == 201:
                message.ack()
            elif response.status == 404:
                message.nack(requeue=False)
            elif response.status == 500:
                raise Exception(f"Server error {response.status}")
            else:
                raise Exception(f"Unexpected response status {response.status}")
