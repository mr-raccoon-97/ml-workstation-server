from uuid import UUID, uuid4
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends, Query, Path
from fastapi import status as status_code
from fastapi import Response
from server.ports import Models, Experiments
from server.schemas import Model
from server.endpoints.experiments import port

router = APIRouter(tags=['Models'])

@router.post('/experiments/{id}/models/', status_code=status_code.HTTP_201_CREATED)
async def add_model_to_experiment(model: Model, id: UUID = Path(...), experiments: Experiments = Depends(port)) -> Model:
    experiment = await experiments.get(id)
    if experiment is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Experiment not found')
    model = experiments.models.create(**model.model_dump(exclude='id'))
    await experiments.models.add(model, experiment)
    return model

@router.get('/experiments/{id}/models/')
async def get_models_from_experiment(id: UUID = Path(...), experiments: Experiments = Depends(port)) -> list[Model]:
    experiment = await experiments.get(id)
    if experiment is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Experiment not found')
    return await experiments.models.list(experiment)

@router.get('/models/{id}/')
async def get_model(id: UUID = Path(...), experiments: Experiments = Depends(port)) -> Model:
    model = await experiments.models.get(id)
    if model is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Model not found')
    return model

@router.patch('/models/{id}/', status_code=status_code.HTTP_204_NO_CONTENT)
async def update_model(model: Model, id: UUID = Path(...), experiments: Experiments = Depends(port)):
    model = await experiments.models.get(id)
    if model is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Model not found')
    await experiments.models.update(model)
    return Response(status_code=status_code.HTTP_204_NO_CONTENT)

@router.delete('/models/{id}/', status_code=status_code.HTTP_204_NO_CONTENT)
async def delete_model(id: UUID = Path(...), experiments: Experiments = Depends(port)):
    model = await experiments.models.get(id)
    if model is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Model not found')
    await experiments.models.remove(model)
    return Response(status_code=status_code.HTTP_204_NO_CONTENT)