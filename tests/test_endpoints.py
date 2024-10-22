import pytest
from uuid import uuid4
from uuid import UUID
from datetime import datetime, timezone
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from fastapi import status as status_code
from server.endpoints import experiments as experiments_endpoints
from server.endpoints import models as models_endpoints
from server.endpoints import metrics as metrics_endpoints
from server.endpoints import transactions as transactions_endpoints
from logging import getLogger, basicConfig, INFO

basicConfig(level=INFO)
logger = getLogger(__name__)

@pytest.fixture
async def client(experiments) -> AsyncGenerator[AsyncClient, None]:
    api = FastAPI()
    api.include_router(experiments_endpoints.router)
    api.include_router(models_endpoints.router)
    api.include_router(metrics_endpoints.router)
    api.include_router(transactions_endpoints.router)
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
        "signature": {"input_size": "int", "output_size": "int"},
        "hash": "123",
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

    logger.info(f"Getting model by hash: 123")
    response = await client.get(f"/experiments/{experiment_id}/models/123/")
    assert response.status_code == status_code.HTTP_200_OK
    assert response.json()['name'] == 'mnist-mlp'

    logger.info("Updating model")
    response = await client.patch(f"/models/{response.json()['id']}/", json={
        "signature": {"input_size": "int", "output_size": "int"},
        "hash": "123",
        "name": "mnist-mlp",
        "args": [],
        "kwargs": {},
        "epochs": 20
    })
    assert response.status_code == status_code.HTTP_204_NO_CONTENT

    logger.info("Attempting to update a non-existent model")
    response = await client.patch(f"/models/{uuid4()}/", json={
        "signature": {"input_size": "int", "output_size": "int"},
        "hash": "123",
        "name": "mnist-mlp",
        "args": [],
        "kwargs": {},
        "epochs": 20
    })
    assert response.status_code == status_code.HTTP_404_NOT_FOUND

    logger.info("Attempting to get a non-existent model")
    response = await client.get(f"/models/{uuid4()}/")
    assert response.status_code == status_code.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_metrics(client: AsyncClient):
    logger.info("Creating a new experiment: 'mnist-mlp'")
    response = await client.post('/experiments/', json={"name": "mnist-mlp"})
    assert response.status_code == status_code.HTTP_201_CREATED
    experiment_id = response.json()["id"]
    logger.info(f"Experiment created with ID: {experiment_id}")

    logger.info("Creating a new model")
    response = await client.post(f'/experiments/{experiment_id}/models/', json={
        "signature": {"input_size": "int", "output_size": "int"},
        "hash": "123",
        "name": "mnist-mlp",
        "args": [],
        "kwargs": {},
        "epochs": 10
    })
    assert response.status_code == status_code.HTTP_201_CREATED
    model_id = response.json()["id"]
    logger.info(f"Model created with ID: {model_id}")

    logger.info("Adding metrics to model")
    response = await client.post(f'/models/{model_id}/metrics/', json={
        "name": "accuracy",
        "phase": "train",
        "batch": 1,
        "epoch": 1,
        "value": 0.99
    })

    assert response.status_code == status_code.HTTP_201_CREATED

    logger.info("Listing all metrics")
    response = await client.get(f'/models/{model_id}/metrics/')
    assert response.status_code == status_code.HTTP_200_OK
    assert len(response.json()) == 1

    logger.info("Attempting to add metrics to a non-existent model")
    response = await client.post(f'/models/{uuid4()}/metrics/', json={
        "name": "accuracy",
        "phase": "train",
        "batch": 1,
        "epoch": 1,
        "value": 0.99
    })

    assert response.status_code == status_code.HTTP_404_NOT_FOUND

    logger.info("Attempting to list metrics from a non-existent model")
    response = await client.get(f'/models/{uuid4()}/metrics/')
    assert response.status_code == status_code.HTTP_404_NOT_FOUND
        

@pytest.mark.asyncio
async def test_transactions(client: AsyncClient):
    logger.info("Creating a new experiment: 'mnist-mlp'")
    response = await client.post('/experiments/', json={"name": "mnist-mlp"})
    assert response.status_code == status_code.HTTP_201_CREATED
    experiment_id = response.json()["id"]
    logger.info(f"Experiment created with ID: {experiment_id}")

    logger.info("Creating a new model")
    response = await client.post(f'/experiments/{experiment_id}/models/', json={
        "signature": {"input_size": "int", "output_size": "int"},
        "hash": "123",
        "name": "mnist-mlp",
        "args": [],
        "kwargs": {},
        "epochs": 10
    })
    assert response.status_code == status_code.HTTP_201_CREATED
    model_id = response.json()["id"]
    logger.info(f"Model created with ID: {model_id}")
    
    start_time = datetime.now(timezone.utc).isoformat()
    end_time = datetime.now(timezone.utc).isoformat()
    
    logger.info("Adding transactions to model")
    response = await client.post(f'/models/{model_id}/transactions/', json={"epochs": [1, 10],
        "start": start_time,
        "end": end_time,
        "criterion": {
            "signature": {},
            "hash": "123",
            "name": "CrossEntropy",
            "args": [],
            "kwargs": {}
        },
        "optimizer": {
            "signature": {"lr": "str"},
            "hash": "456",
            "name": "Adam",
            "args": [],
            "kwargs": {"lr": 0.001}
        },
        "iterations": [
            {
                "phase": "train",
                "dataset": {
                    "signature": {"normalize": "bool"},
                    "hash": "789",
                    "name": "mnist",
                    "args": [],
                    "kwargs": {}
                },
                "kwargs": {}
            }
        ]
        })
        
    assert response.status_code == status_code.HTTP_201_CREATED

    logger.info("Listing all transactions")
    response = await client.get(f'/models/{model_id}/transactions/')
    assert response.status_code == status_code.HTTP_200_OK
    assert len(response.json()) == 1