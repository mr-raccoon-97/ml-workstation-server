from uuid import UUID
from uuid import uuid4
from typing import override
from typing import Optional
from server.ports import Experiments as Collection
from server.schemas import Experiment
from motor.motor_asyncio import AsyncIOMotorDatabase
from server.adapters.models import Models

class Experiments(Collection):
    def __init__(self, database: AsyncIOMotorDatabase):
        self.key = UUID('00000000-0000-0000-0000-000000000000')
        self.collection = database['experiments']
        self.models = Models(database)

    def create(self, **kwargs) -> Experiment:
        experiment = Experiment(id=uuid4(), **kwargs)
        return experiment

    @override
    async def add(self, experiment: Experiment):
        filter = {'_id': str(self.key)}
        update = {'$push': {'experiments': experiment.model_dump(mode='json')}}
        await self.collection.update_one(filter, update, upsert=True)
        
    @override
    async def update(self, experiment: Experiment):
        filter = {'_id': str(self.key), 'experiments.id': str(experiment.id)}
        update = {'$set': {'experiments.$': experiment.model_dump(mode='json')}}
        await self.collection.update_one(filter, update)

    @override
    async def remove(self, experiment: Experiment):
        await self.models.clean(experiment)
        filter = {'_id': str(self.key)}
        update = {'$pull': {'experiments': {'id': str(experiment.id)}}}
        await self.collection.update_one(filter, update)

    @override
    async def get(self, id: UUID) -> Optional[Experiment]:
        filter = {'_id': str(self.key), 'experiments.id': str(id)}
        document = await self.collection.find_one(filter, {'experiments.$': 1})
        if document is None:
            return None
        return Experiment.model_validate(document['experiments'][0])

    @override
    async def get_by_name(self, name: str) -> Optional[Experiment]:
        filter = {'_id': str(self.key), 'experiments.name': name}
        document = await self.collection.find_one(filter, {'experiments.$': 1})
        if document is None:
            return None
        return Experiment.model_validate(document['experiments'][0])

    @override
    async def exists(self, name: str) -> bool:
        filter = {'_id': str(self.key), 'experiments.name': name}
        document = await self.collection.find_one(filter, {'experiments.$': 1})
        return True if document else False

    @override
    async def list(self):
        filter = {'_id': str(self.key)}
        document = await self.collection.find_one(filter)
        if document is None:
            return []
        return [Experiment.model_validate(document) for document in document['experiments']]