from server.settings import Settings
from logging import getLogger
from motor.motor_asyncio import AsyncIOMotorClient

logger = getLogger(__name__)

class MongoDB:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncIOMotorClient(self.settings.database.uri)

    async def setup(self):
        self.database = self.client[self.settings.database.database]

    async def teardown(self):
        self.client.close()