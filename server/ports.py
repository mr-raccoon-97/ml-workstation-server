from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID, uuid4
from server.schemas import Experiment, Model

class Models(ABC):
    experiment: Experiment

    @abstractmethod
    def create(self, **kwargs) -> Model: ...
    
    @abstractmethod
    async def add(self, model: Model, experiment: Experiment):
        ...

    @abstractmethod
    async def list(self, experiment: Experiment) -> list[Model]:
        ...

    @abstractmethod
    async def get(self, id: UUID) -> Optional[Model]:
        ...

    @abstractmethod
    async def update(self, model: Model):
        ...

    @abstractmethod
    async def remove(self, model: Model):
        ...


class Experiments(ABC):
    models: Models

    def create(self, **kwargs) -> Experiment:
        return Experiment(id=uuid4(), **kwargs)

    @abstractmethod
    async def add(self, experiment: Experiment):
        ...

    @abstractmethod
    async def update(self, experiment: Experiment):
        ...

    @abstractmethod
    async def remove(self, experiment: Experiment):
        ...
        
    @abstractmethod
    async def exists(self, name: str):
        ...

    @abstractmethod
    async def get(self, id: UUID) -> Optional[Experiment]:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Experiment]:
        ...

    @abstractmethod
    async def list(self) -> list[Experiment]:
        ...