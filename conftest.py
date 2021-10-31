import pytest
import aiopg

from config import TEST_DSN
from queries import clear_wallets, clear_transactions
from repository import WalletRepository, TransactionRepository

@pytest.fixture
async def pg_pool():
    pool = await aiopg.create_pool(TEST_DSN)
    yield pool
    

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
    return await wallet_repo.create("Roma", balance=100)

@pytest.fixture
async def wallet2(wallet_repo):
    return await wallet_repo.create("Marina")

@pytest.fixture
async def transaction1(wallet1, wallet2, transaction_repo):
    return await transaction_repo._create(from_id=wallet1, to_id=wallet2, amount=10, comment="test transaction", type="transfer")

@pytest.fixture
async def transaction2(wallet1, wallet2, transaction_repo):
    return await transaction_repo._create(from_id=None, to_id=wallet1, amount=10, comment="test transaction", type="transfer")

@pytest.fixture
async def transaction3(wallet1, wallet2, transaction_repo):
    return await transaction_repo._create(from_id=None, to_id=wallet2, amount=10, comment="test transaction", type="transfer")
