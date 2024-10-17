from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID, uuid4
from server.schemas import Experiment, Model, Metric, Transaction

class Metrics(ABC):

    @abstractmethod
    def create(self, **kwargs) -> Metric:... 

    @abstractmethod
    async def add(self, metric: Metric, model: Model):...

    @abstractmethod
    async def list(self, model: Model) -> list[Metric]:...


class Transactions(ABC):

    @abstractmethod
    def create(self, **kwargs) -> Transaction:...
    
    @abstractmethod
    async def add(self, transaction: Transaction, model: Model):...

    @abstractmethod
    async def list(self, model: Model) -> list[Transaction]:...


class Models(ABC):
    metrics: Metrics
    transactions: Transactions

    @abstractmethod
    def create(self, **kwargs) -> Model:...
    
    @abstractmethod
    async def add(self, model: Model, experiment: Experiment):...

    @abstractmethod
    async def list(self, experiment: Experiment) -> list[Model]:...

    @abstractmethod
    async def get_by_hash(self, hash: str, experiment: Experiment) -> Optional[Model]:...

    @abstractmethod
    async def get(self, id: UUID) -> Optional[Model]:...

    @abstractmethod
    async def update(self, model: Model):...

    @abstractmethod
    async def remove(self, model: Model):...


class Experiments(ABC):
    models: Models

    def create(self, **kwargs) -> Experiment:
        return Experiment(id=uuid4(), **kwargs)

    @abstractmethod
    async def add(self, experiment: Experiment):...

    @abstractmethod
    async def update(self, experiment: Experiment):...

    @abstractmethod
    async def remove(self, experiment: Experiment):...
        
    @abstractmethod
    async def exists(self, name: str):...

    @abstractmethod
    async def get(self, id: UUID) -> Optional[Experiment]:...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Experiment]:...

    @abstractmethod
    async def list(self) -> list[Experiment]:...