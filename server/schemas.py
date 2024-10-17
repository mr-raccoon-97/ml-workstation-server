from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
from pydantic import Field

class Schema(BaseModel):
    ...

class Experiment(Schema):
    id: Optional[UUID] = Field(default=None)
    name: str

class Model(Schema):
    id: Optional[UUID] = Field(default=None)
    hash: str
    name: str
    args: tuple
    kwargs: dict
    epochs: int

class Metric(Schema):
    name: str
    phase: str
    batch: int
    epoch: int
    value: float

class Criterion(Schema):
    hash: str
    name: str
    args: tuple
    kwargs: dict    

class Optimizer(Schema):
    hash: str
    name: str
    args: tuple
    kwargs: dict

class Dataset(Schema):
    hash: str
    name: str
    args: tuple
    kwargs: dict

class Iteration(Schema):
    phase: str
    dataset: Dataset
    kwargs: dict

class Transaction(Schema):
    id: Optional[UUID] = Field(default=None)
    epochs: tuple[int, int]
    start: datetime
    end: datetime
    criterion: Optional[Criterion]
    optimizer: Optional[Optimizer]
    iterations: list[Iteration]