import os
from unittest import mock

import aiopg
import pytest
from starlette.testclient import TestClient

from queries import clear_transactions, clear_wallets
from repository import TransactionRepository, WalletRepository


@pytest.fixture
def test_dsn():
    with mock.patch.dict(os.environ, {"DSN": "dbname=billing_task_tests"}, clear=True):
        yield


@pytest.fixture
async def pg_pool(test_dsn):
    from config import DSN

    pool = await aiopg.create_pool(DSN)
    yield pool
    pool.close()


@pytest.fixture
async def client(test_dsn):
    from app import app

    yield TestClient(app)


@pytest.fixture
async def wallet_repo(pg_pool):
    yield WalletRepository(pg_pool)
    with (await pg_pool.cursor()) as cur:
        await cur.execute(clear_wallets)


@pytest.fixture
async def transaction_repo(pg_pool):
    yield TransactionRepository(pg_pool)
    with (await pg_pool.cursor()) as cur:
        await cur.execute(clear_transactions)


@pytest.fixture
async def wallet1(wallet_repo):
    yield await wallet_repo.create("Roma", balance=100)


@pytest.fixture
async def wallet2(wallet_repo):
    yield await wallet_repo.create("Marina")


@pytest.fixture
async def transaction1(wallet1, wallet2, transaction_repo):
    yield await transaction_repo._create(
        from_id=wallet1,
        to_id=wallet2,
        amount=10,
        comment="test transaction",
        type="transfer",
    )


@pytest.fixture
async def transaction2(wallet1, wallet2, transaction_repo):
    yield await transaction_repo._create(
        from_id=None,
        to_id=wallet1,
        amount=10,
        comment="test transaction",
        type="transfer",
    )


@pytest.fixture
async def transaction3(wallet1, wallet2, transaction_repo):
    yield await transaction_repo._create(
        from_id=None,
        to_id=wallet2,
        amount=10,
        comment="test transaction",
        type="transfer",
    )
