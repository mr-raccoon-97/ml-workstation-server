from uuid import UUID, uuid4
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends, Query, Path
from fastapi import status as status_code
from server.ports import Models, Experiments
from server.schemas import Metric
from server.endpoints import experiments

router = APIRouter(tags=['Metrics'])

async def port(experiments: Experiments = Depends(experiments.port)) -> Models:
    return experiments.models

@router.post('/models/{id}/metrics/', status_code=status_code.HTTP_201_CREATED)
async def add_metric_to_model(metric: Metric, id: UUID = Path(...), models: Models = Depends(port)) -> Metric:
    model = await models.get(id)
    if model is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Model not found')
    metric = models.metrics.create(**metric.model_dump())
    await models.metrics.add(metric, model)
    return metric

@router.get('/models/{id}/metrics/')
async def get_metrics_from_model(id: UUID = Path(...), models: Models = Depends(port)) -> list[Metric]:
    model = await models.get(id)
    if model is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Model not found')
    return await models.metrics.list(model)