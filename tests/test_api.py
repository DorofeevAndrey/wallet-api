import asyncio
from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


class FakeWallet:
    def __init__(self, uuid, balance: Decimal):
        self.uuid = uuid
        self.balance = Decimal(balance)


class FakeRepo:
    store: dict = {}

    def __init__(self, session):
        pass

    async def get(self, wallet_uuid):
        return self.store.get(str(wallet_uuid))

    async def deposit(self, wallet_uuid, amount: Decimal):
        key = str(wallet_uuid)
        if key not in self.store:
            self.store[key] = FakeWallet(wallet_uuid, Decimal("0.00"))
        self.store[key].balance = Decimal(self.store[key].balance) + Decimal(amount)
        return self.store[key]

    async def withdraw(self, wallet_uuid, amount: Decimal):
        key = str(wallet_uuid)
        if key not in self.store:
            self.store[key] = FakeWallet(wallet_uuid, Decimal("0.00"))
        if Decimal(self.store[key].balance) < Decimal(amount):
            from app.repositories.wallet_repository import InsufficientFunds

            raise InsufficientFunds("Insufficient funds")
        self.store[key].balance = Decimal(self.store[key].balance) - Decimal(amount)
        return self.store[key]


@pytest.mark.asyncio
async def test_get_wallet_not_found(monkeypatch):
    from app.api.v1 import wallets

    wallets.WalletRepository = FakeRepo
    FakeRepo.store = {}

    wallet_id = uuid4()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get(f"/api/v1/wallets/{wallet_id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_deposit_creates_wallet(monkeypatch):
    from app.api.v1 import wallets

    wallets.WalletRepository = FakeRepo
    FakeRepo.store = {}

    wallet_id = uuid4()
    payload = {"operation_type": "DEPOSIT", "amount": "100.00"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post(f"/api/v1/wallets/{wallet_id}/operation", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["wallet_id"] == str(wallet_id)
    assert data["balance"] == "100.00"


@pytest.mark.asyncio
async def test_withdraw_insufficient(monkeypatch):
    from app.api.v1 import wallets

    wallets.WalletRepository = FakeRepo
    FakeRepo.store = {}

    wallet_id = uuid4()
    payload = {"operation_type": "WITHDRAW", "amount": "50.00"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post(f"/api/v1/wallets/{wallet_id}/operation", json=payload)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_withdraw_success(monkeypatch):
    from app.api.v1 import wallets

    wallets.WalletRepository = FakeRepo
    FakeRepo.store = {}

    wallet_id = uuid4()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r1 = await ac.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "200.00"},
        )
        assert r1.status_code == 200

        r2 = await ac.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "WITHDRAW", "amount": "50.00"},
        )
        assert r2.status_code == 200
        data = r2.json()
        assert data["balance"] == "150.00"
