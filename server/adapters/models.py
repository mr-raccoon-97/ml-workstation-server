from typing import override
from typing import Optional
from uuid import UUID, NAMESPACE_DNS, uuid5
from server.ports import Models as Collection
from server.schemas import Model, Experiment
from motor.motor_asyncio import AsyncIOMotorDatabase

def model_identifier(model: Model) -> UUID:
    return uuid5(NAMESPACE_DNS, model.model_dump_json(exclude={'id', 'epochs'}))

class Models(Collection):
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database['models']

    def create(self, **kwargs) -> Model:
        model = Model.model_validate(kwargs)
        model.id = model_identifier(model)
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