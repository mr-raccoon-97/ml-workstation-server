from uuid import UUID, uuid4
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends, Query, Path
from fastapi import status as status_code
from fastapi import Response
from server.ports import Experiments
from server.schemas import Experiment, Model

router = APIRouter(tags=['Experiments'])

async def port() -> Experiments: ...

@router.post('/experiments/', status_code=status_code.HTTP_201_CREATED)
async def add_experiment(experiment: Experiment, experiments: Experiments = Depends(port)) -> Experiment:
    if await experiments.exists(experiment.name):
        raise HTTPException(status_code.HTTP_409_CONFLICT, detail='Experiment already exists')
    experiment = experiments.create(**experiment.model_dump(exclude='id'))
    await experiments.add(experiment)
    return experiment

@router.get('/experiments/')
async def get_experiments(experiments: Experiments = Depends(port)) -> list[Experiment]:
    return await experiments.list()    

@router.get('/experiments/{id}/')
async def get_experiment(id: UUID = Path(...), experiments: Experiments = Depends(port)) -> Experiment:
    experiment = await experiments.get(id)
    if experiment is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Experiment not found')
    return experiment

@router.get('/experiments')
async def get_experiment_by_name(name: str = Query(...), experiments: Experiments = Depends(port)) -> Experiment:
    experiment = await experiments.get_by_name(name)
    if experiment is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Experiment not found')
    return experiment

@router.delete('/experiments/{id}/')
async def delete_experiment(id: UUID = Path(...), experiments: Experiments = Depends(port)):
    experiment = await experiments.get(id)
    if experiment is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Experiment not found')
    await experiments.remove(experiment)
    return Response(status_code=status_code.HTTP_204_NO_CONTENT)