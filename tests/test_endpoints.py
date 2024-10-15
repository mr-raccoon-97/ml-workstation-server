import pytest
from uuid import uuid4
from datetime import datetime, timezone
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from fastapi import status as status_code
from server.endpoints import experiments as experiments_endpoints
from server.endpoints import models as models_endpoints
from logging import getLogger

logger = getLogger(__name__)

@pytest.fixture
async def client(experiments) -> AsyncGenerator[AsyncClient, None]:
    api = FastAPI()
    api.include_router(experiments_endpoints.router)
    api.include_router(models_endpoints.router)
    api.dependency_overrides[experiments_endpoints.port] = lambda: experiments
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_add_experiment_and_session(client: AsyncClient):
    logger.info("Creating a new experiment: 'mnist-mlp'")
    response = await client.post('/experiments/', json={"name": "mnist-mlp"})
    assert response.status_code == status_code.HTTP_201_CREATED
    experiment_id = response.json()["id"]
    logger.info(f"Experiment created with ID: {experiment_id}")


    logger.info("Attempting to create the same experiment again")
    response = await client.post('/experiments/', json={"name": "mnist-mlp"})
    assert response.status_code == status_code.HTTP_409_CONFLICT

    logger.info("Listing all experiments")
    response = await client.get('/experiments/')
    assert response.status_code == status_code.HTTP_200_OK
    assert len(response.json()) == 1


    logger.info(f"Getting experiment by ID: {experiment_id}")
    response = await client.get(f"/experiments/{experiment_id}/")
    assert response.status_code == status_code.HTTP_200_OK
    assert response.json()['name'] == 'mnist-mlp'

    response = await client.get(f"/experiments?name=mnist-mlp")
    assert response.status_code == status_code.HTTP_200_OK
    assert response.json()['name'] == 'mnist-mlp'




@pytest.mark.asyncio
async def test_models(client: AsyncClient):
    logger.info("Creating a new experiment: 'mnist-mlp'")
    response = await client.post('/experiments/', json={"name": "mnist-mlp"})
    assert response.status_code == status_code.HTTP_201_CREATED
    experiment_id = response.json()["id"]
    logger.info(f"Experiment created with ID: {experiment_id}")

    logger.info("Creating a new model")
    response = await client.post(f'/experiments/{experiment_id}/models/', json={
        "name": "mnist-mlp",
        "args": [],
        "kwargs": {},
        "epochs": 10
    })
    assert response.status_code == status_code.HTTP_201_CREATED
    logger.info(f"Model created with ID {response.json()['id']}")

    logger.info("Listing all models")
    response = await client.get(f'/experiments/{experiment_id}/models/')
    assert response.status_code == status_code.HTTP_200_OK
    assert len(response.json()) == 1

    model_id = response.json()[0]['id']

    logger.info(f"Getting model by ID: {model_id}")
    response = await client.get(f"/models/{model_id}/")
    assert response.status_code == status_code.HTTP_200_OK
    assert response.json()['name'] == 'mnist-mlp'

    logger.info("Updating model")
    response = await client.patch(f"/models/{response.json()['id']}/", json={
        "name": "mnist-mlp",
        "args": [],
        "kwargs": {},
        "epochs": 20
    })
    assert response.status_code == status_code.HTTP_204_NO_CONTENT

    logger.info("Attempting to update a non-existent model")
    response = await client.patch(f"/models/{uuid4()}/", json={
        "name": "mnist-mlp",
        "args": [],
        "kwargs": {},
        "epochs": 20
    })
    assert response.status_code == status_code.HTTP_404_NOT_FOUND

    logger.info("Attempting to get a non-existent model")
    response = await client.get(f"/models/{uuid4()}/")
    assert response.status_code == status_code.HTTP_404_NOT_FOUND



