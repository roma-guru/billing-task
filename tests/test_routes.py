import pytest


@pytest.mark.asyncio
async def test_create_wallet(client):
    resp = client.post("/v1/wallets/", json={"username": "Roma"}).json()
    assert resp["id"] > 0 and resp["username"] == "Roma" and resp["balance"] == 0
