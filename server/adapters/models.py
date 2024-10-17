from typing import override
from typing import Optional
from uuid import UUID, uuid4
from server.ports import Models as Collection
from server.schemas import Model, Experiment
from server.adapters.metrics import Metrics
from server.adapters.transactions import Transactions
from motor.motor_asyncio import AsyncIOMotorDatabase

class Models(Collection):
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database['models']
        self.metrics = Metrics(database)
        self.transactions = Transactions(database)

    def create(self, **kwargs) -> Model:
        model = Model(id=uuid4(), **kwargs)
        return model

    @override
    async def add(self, model: Model, experiment: Experiment):
        filter = {'_id': str(experiment.id)}
        update = {'$push': {'models': model.model_dump(mode='json')}}
        await self.collection.update_one(filter, update, upsert=True)

    @override
    async def list(self, experiment: Experiment) -> list[Model]:
        document = await self.collection.find_one({'_id': str(experiment.id)})
        if document is None:
            return []
        return [Model.model_validate(document) for document in document['models']]
    
    @override
    async def get_by_hash(self, hash: str, experiment: Experiment) -> Optional[Model]:
        filter = {'_id': str(experiment.id), 'models.hash': hash}
        document = await self.collection.find_one(filter, {'models.$': 1})
        if document is None:
            return None
        return Model.model_validate(document['models'][0])

    @override
    async def get(self, id: UUID) -> Optional[Model]:
        filter = {'models.id': str(id)}
        document = await self.collection.find_one(filter, {'models.$': 1})
        if document is None:
            return None
        return Model.model_validate(document['models'][0])
    
    @override
    async def update(self, model: Model):
        filter = {'models.id': str(model.id)}
        update = {'$set': {'models.$': model.model_dump(mode='json')}}
        await self.collection.update_one(filter, update)

    @override
    async def remove(self, model: Model):
        filter = {'models.id': str(model.id)}
        update = {'$pull': {'models': {'id': str(model.id)}}}
        await self.collection.update_one(filter, update)