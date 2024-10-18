from typing import Callable
from aio_pika import Channel, connect_robust
from aiohttp import ClientSession
from asyncio import gather, create_task, Task
from logging import getLogger
from functools import partial
from messagebus.settings import Settings

logger = getLogger(__name__)

async def consume(topic: str, channel: Channel, callback: Callable, session: ClientSession):
    queue = await channel.get_queue(topic)
    await queue.consume(partial(callback, session=session))

class RabbitMQ:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.handlers = dict[str, Callable]()
        self.channels = dict[str, Channel]()
        self.tasks = list[Task]()
    
    def include_handler(self, topic: str, handler: Callable):
        self.handlers[topic] = handler

    async def setup(self):
        logger.info("Establishing connection")
        self.connection = await connect_robust(self.settings.rabbitmq.uri)
        logger.info("Connection established.")
        logger.info("Creating channels ")
        for topic, handler in self.handlers.items():
            channel = await self.connection.channel()
            await channel.set_qos(prefetch_count=self.settings.rabbitmq.prefetch_count)
            await channel.declare_queue(topic, durable=True)
            self.channels[topic] = channel
        
        logger.info("Channels created.")
        logger.info("Creating session")
        self.session = ClientSession(base_url=self.settings.api.uri)
    
    async def start_consuming(self):
        logger.info("Consuming messages (Press CTRL+C to quit)")
        for topic, channel in self.channels.items():
            self.tasks.append(create_task(consume(topic, channel, self.handlers[topic], self.session)))
        await gather(*self.tasks)        
    
    async def teardown(self):
        for task in self.tasks:
            task.cancel()
        
        await self.session.close()
        logger.info("Closing channels")
        for topic, channel in self.channels.items():
            await channel.close()
            logger.info(f"Channel {topic} closed.")

        logger.info("Closing connection")
        await self.connection.close()
        logger.info("Connection closed.")