from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

class Schema(BaseModel):
    ...
    
class Experiment(Schema):
    id: Optional[UUID] = Field(default=None)
    name: str

class Model(Schema):
    id: Optional[UUID] = Field(default=None)
    signature: dict
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
    signature: dict
    hash: str
    name: str
    args: tuple
    kwargs: dict    

class Optimizer(Schema):
    signature: dict
    hash: str
    name: str
    args: tuple
    kwargs: dict

class Dataset(Schema):
    signature: dict
    hash: str
    name: str
    args: tuple
    kwargs: dict

class Iteration(Schema):
    phase: str
    dataset: Dataset
    kwargs: dict

class Transaction(Schema):
    hash: str
    epochs: tuple[int, int]
    start: datetime
    end: datetime
    criterion: Optional[Criterion]
    optimizer: Optional[Optimizer]
    iterations: list[Iteration]