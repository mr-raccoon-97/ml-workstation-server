from typing import Optional
from typing import Any
from uuid import UUID
from pydantic import BaseModel

class Schema(BaseModel):
    ...

class Experiment(Schema):
    id: Optional[UUID] = None
    name: str

class Model(Schema):
    id: Optional[UUID] = None
    name: str
    args: set[Any]
    kwargs: dict[str, Any]
    epochs: int

class Criterion(Schema):
    id: UUID
    name: str
    args: set[Any]
    kwargs: dict[str, Any]
    
class Optimizer(Schema):
    id: UUID
    name: str
    args: set[Any]
    kwargs: dict[str, Any]

class Dataset(Schema):
    id: UUID
    name: str
    args: set[Any]
    kwargs: dict[str, Any]

class Loader(Schema):
    dataset: Dataset
    args: set[Any]
    kwargs: dict[str, Any]

class Session(Schema):
    id: UUID
    criterion: Optional[Criterion]
    optimizer: Optional[Optimizer]
    loaders: list[tuple[str, Loader]]

class Metric(Schema):
    epoch: int
    batch: int
    name: str
    phase: str
    value: float