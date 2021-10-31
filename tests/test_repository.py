from decimal import Decimal
import pytest

from exceptions import *


@pytest.mark.asyncio
async def test_wallet_create(wallet_repo):
    assert await wallet_repo.create("Leo") > 0

@pytest.mark.asyncio
async def test_wallet_get_by_id(wallet_repo, wallet1):
    assert (await wallet_repo.get_by_id(wallet1)).username == "Roma"

@pytest.mark.asyncio
async def test_wallet_get_all(wallet_repo, wallet1, wallet2):
    assert len(await wallet_repo.get_all()) == 2


@pytest.mark.asyncio
async def test_transaction_get_by_id(wallet1, wallet2, transaction_repo, transaction1):
    obj = await transaction_repo.get_by_id(transaction1)
    assert obj.id == transaction1
    assert obj.from_id==wallet1 and obj.to_id==wallet2

@pytest.mark.asyncio
async def test_transaction_get_by_wallet(wallet1, transaction_repo, transaction1, transaction2, transaction3):
    objs = await transaction_repo.get_by_wallet(wallet1)
    assert len(objs) == 2
    for obj in objs:
        assert obj.from_id == wallet1 or obj.to_id == wallet1

@pytest.mark.asyncio
async def test_transaction_make_transfer(wallet_repo, wallet1, wallet2, transaction_repo):
    assert (await wallet_repo.get_by_id(wallet1)).balance == Decimal(100)
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(0)
    assert await transaction_repo.make_transfer(wallet1, wallet2, Decimal(10)) > 0
    assert (await wallet_repo.get_by_id(wallet1)).balance == Decimal(90)
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(10)

@pytest.mark.asyncio
async def test_transaction_make_transfer_not_enough(wallet_repo, wallet1, wallet2, transaction_repo):
    assert (await wallet_repo.get_by_id(wallet1)).balance == Decimal(100)
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(0)
    with pytest.raises(NotEnoughMoney):
        await transaction_repo.make_transfer(wallet2, wallet1, Decimal(100)) 
    # should left unchanged
    assert (await wallet_repo.get_by_id(wallet1)).balance == Decimal(100)
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(0)

@pytest.mark.asyncio
async def test_transaction_make_deposit(wallet_repo, wallet2, transaction_repo):
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(0)
    assert await transaction_repo.make_deposit(wallet2, Decimal(10)) > 0
    assert (await wallet_repo.get_by_id(wallet2)).balance == Decimal(10)

