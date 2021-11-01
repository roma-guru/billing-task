from decimal import Decimal

import pytest


@pytest.mark.asyncio
async def test_create_wallet(client, wallet1):
    # wallet1 fixture needed to clean db
    # need ctx mgr to startup app correctly
    # https://github.com/encode/starlette/issues/1298#issuecomment-934634591
    with client:
        resp = client.post("/v1/wallets/", json={"username": "Roma"}).json()
        assert resp["id"] > 0
        assert resp["username"] == "Roma"
        assert Decimal(resp["balance"]) == 0


@pytest.mark.asyncio
async def test_wallet_get_all(client, wallet1, wallet2):
    with client:
        resp = client.get("/v1/wallets/").json()
        assert len(resp) == 2


@pytest.mark.asyncio
async def test_wallet_get_by_id(client, wallet1):
    with client:
        resp = client.get(f"/v1/wallets/{wallet1}").json()
        assert resp["username"] == "Roma" and resp["id"] == wallet1


@pytest.mark.asyncio
async def test_transaction_get_by_id(client, transaction1):
    with client:
        resp = client.get(f"/v1/transactions/{transaction1}").json()
        assert resp["id"] == transaction1 and Decimal(resp["amount"]) == 10


@pytest.mark.asyncio
async def test_transaction_get_by_wallet(
    client, wallet1, transaction1, transaction2, transaction3
):
    with client:
        resp = client.get(f"/v1/transactions/by/{wallet1}").json()
        assert len(resp) == 2
