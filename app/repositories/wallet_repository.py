from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet


class InsufficientFunds(Exception):
    pass


class WalletRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, wallet_uuid: UUID) -> Optional[Wallet]:
        result = await self.session.execute(
            select(Wallet).where(Wallet.uuid == wallet_uuid)
        )
        return result.scalar_one_or_none()

    async def change_balance(self, wallet_uuid: UUID, delta: Decimal) -> Wallet:
        async with self.session.begin():
            q = select(Wallet).where(Wallet.uuid == wallet_uuid).with_for_update()
            res = await self.session.execute(q)
            wallet = res.scalar_one_or_none()

            if wallet is None:
                wallet = Wallet(uuid=wallet_uuid, balance=Decimal("0.00"))
                self.session.add(wallet)
                await self.session.flush()
                # повторно захватить строку под блокировку
                res = await self.session.execute(q)
                wallet = res.scalar_one()

            delta = Decimal(delta)
            new_balance = Decimal(wallet.balance) + delta
            if new_balance < 0:
                raise InsufficientFunds("Insufficient funds")

            wallet.balance = new_balance
            await self.session.flush()
            return wallet

    async def deposit(self, wallet_uuid: UUID, amount: Decimal) -> Wallet:
        if Decimal(amount) <= 0:
            raise ValueError("amount must be > 0")
        return await self.change_balance(wallet_uuid, Decimal(amount))

    async def withdraw(self, wallet_uuid: UUID, amount: Decimal) -> Wallet:
        if Decimal(amount) <= 0:
            raise ValueError("amount must be > 0")
        return await self.change_balance(wallet_uuid, -Decimal(amount))
