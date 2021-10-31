import asyncio
import random
from decimal import Decimal

import pytest


@pytest.mark.asyncio
async def test_bulk_deposit(wallet_repo, wallet2, transaction_repo):
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(0)
    await asyncio.gather(
        *[transaction_repo.make_deposit(wallet2, Decimal(10)) for _ in range(100)]
    )
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(1000)


@pytest.mark.asyncio
async def test_bulk_transfers(wallet_repo, wallet1, wallet2, transaction_repo):
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(0)
    assert (await wallet_repo.get_by_id(wallet1)).balance == Decimal(100)
    await asyncio.gather(
        *[
            transaction_repo.make_transfer(wallet1, wallet2, Decimal(1))
            for _ in range(100)
        ]
    )
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(100)
    assert (await wallet_repo.get_by_id(wallet1)).balance == Decimal(0)


@pytest.mark.asyncio
async def test_random_transfers(wallet_repo, wallet1, wallet2, transaction_repo):
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(0)
    assert (await wallet_repo.get_by_id(wallet1)).balance == Decimal(100)
    coros = []
    for _ in range(100):
        amount = Decimal(random.randint(1, 10))
        if random.random() > 0.5:
            args = (wallet1, wallet2, amount)
        else:
            args = (wallet2, wallet1, amount)
        coros.append(transaction_repo.make_transfer(*args))
    await asyncio.gather(*coros, return_exceptions=True)
    assert (await wallet_repo.get_by_id(wallet2)).balance + (
        await wallet_repo.get_by_id(wallet1)
    ).balance == Decimal(100)
