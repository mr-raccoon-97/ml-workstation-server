from typing import override
from typing import Optional
from server.ports import Transactions as Collection
from server.schemas import Transaction, Model
from motor.motor_asyncio import AsyncIOMotorDatabase

class Transactions(Collection):
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database['transactions']

    def create(self, **kwargs) -> Transaction:
        metric = Transaction(**kwargs)
        return metric
    
    @override
    async def add(self, transaction: Transaction, model: Model):
        filter = {'_id': str(model.id)}
        update = {'$push': {'transactions': transaction.model_dump(mode='json')}}
        await self.collection.update_one(filter, update, upsert=True)

    @override
    async def list(self, model: Model) -> list[Transaction]:
        document = await self.collection.find_one({'_id': str(model.id)})
        if document is None:
            return []
        return [Transaction.model_validate(document) for document in document['transactions']]