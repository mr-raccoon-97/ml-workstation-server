from server.settings import Settings
from logging import getLogger
from aio_pika import connect_robust
from asyncio import create_task, gather, Future
from motor.motor_asyncio import AsyncIOMotorClient
from functools import partial
from aiohttp import ClientSession

logger = getLogger(__name__)

class RabbitMQ:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.handlers = {}
    
    async def setup(self):
        self.connection = await connect_robust(self.settings.rabbitmq.uri)

    async def teardown(self):
        await self.connection.close()

    async def start(self):
        logger.info("Connecting to RabbitMQ...")
        self.channel = await self.connection.channel()
        await self.channel.declare_queue('sessions', durable=True)
        await self.channel.declare_queue('transactions', durable=True)
        await self.channel.declare_queue('metrics', durable=True)
        await gather(
            create_task(self.consume('sessions')),
            create_task(self.consume('transactions')),
            create_task(self.consume('metrics'))
        )
        logger.info("[*] Waiting for messages. To exit press CTRL+C")
        await Future()

    async def consume(self, route: str):
        queue = await self.channel.get_queue(route)
        async with ClientSession(self.settings.api.uri) as session:
            await queue.consume(partial(self.handlers[route], session))

    async def stop(self):
        await self.channel.close()


class MongoDB:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncIOMotorClient(self.settings.mongodb.uri)

    async def setup(self):
        self.database = self.client[self.settings.mongodb.database]

    async def teardown(self):
        self.client.close()