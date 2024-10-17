from typing import override
from typing import Optional
from uuid import UUID, uuid4
from server.ports import Metrics as Collection
from server.schemas import Model, Metric
from motor.motor_asyncio import AsyncIOMotorDatabase

class Metrics(Collection):
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database['metrics']

    def create(self, **kwargs) -> Metric:
        metric = Metric(**kwargs)
        return metric
    
    @override
    async def add(self, metric: Metric, model: Model):
        filter = {'_id': str(model.id)}
        update = {'$push': {'metrics': metric.model_dump(mode='json')}}
        await self.collection.update_one(filter, update, upsert=True)

    @override
    async def list(self, model: Model) -> list[Metric]:
        document = await self.collection.find_one({'_id': str(model.id)})
        if document is None:
            return []
        return [Metric.model_validate(document) for document in document['metrics']]