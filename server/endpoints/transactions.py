from uuid import UUID, uuid4
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends, Query, Path
from fastapi import status as status_code
from fastapi import Response
from server.ports import Models, Experiments
from server.schemas import Transaction
from server.endpoints import experiments

router = APIRouter(tags=['Transactions'])

async def port(experiments: Experiments = Depends(experiments.port)) -> Models:
    return experiments.models

@router.post('/models/{id}/transactions/', status_code=status_code.HTTP_201_CREATED)
async def add_transaction_to_model(transaction: Transaction, id: UUID = Path(...), models: Models = Depends(port)) -> Transaction:
    model = await models.get(id)
    if model is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Model not found')
    transaction = models.transactions.create(**transaction.model_dump())
    await models.transactions.add(transaction, model)
    return transaction

@router.put('/models/{id}/transactions/{hash}/')
async def put_create_or_update_transaction(transaction: Transaction, id: UUID = Path(...), hash: str = Path(...), models: Models = Depends(port)) -> Response:
    model = await models.get(id)
    if model is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Model not found')
    transaction = models.transactions.create(**transaction.model_dump())
    if await models.transactions.exists(hash, model):
        await models.transactions.update(transaction, model)
        return Response(status_code=status_code.HTTP_204_NO_CONTENT)
    else:
        await models.transactions.add(transaction, model)
        return Response(status_code=status_code.HTTP_201_CREATED)

@router.get('/models/{id}/transactions/')
async def get_transactions_from_model(id: UUID = Path(...), models: Models = Depends(port)) -> list[Transaction]:
    model = await models.get(id)
    if model is None:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND, detail='Model not found')
    return await models.transactions.list(model)