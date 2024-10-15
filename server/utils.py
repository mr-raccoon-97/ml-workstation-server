from uuid import UUID, NAMESPACE_DNS, uuid5
from json import dumps
from server.schemas import Model

def model_identifier(model: Model) -> UUID:
    return uuid5(NAMESPACE_DNS, model.model_dump_json(exclude={'id', 'epochs'}))
