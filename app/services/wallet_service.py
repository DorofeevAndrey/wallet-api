from decimal import Decimal
from typing import Union
from uuid import UUID

from app.repositories.wallet_repository import (
    WalletRepository,
    InsufficientFunds,
)
from app.schemas.wallet_schema import OperationType, WalletOperation


class WalletNotFound(Exception):
    pass


class WalletService:
    def __init__(self, repo: WalletRepository):
        self.repo = repo

    async def get_balance(self, wallet_uuid: UUID) -> Decimal:
        wallet = await self.repo.get(wallet_uuid)
        if wallet is None:
            raise WalletNotFound("Wallet not found")
        return Decimal(wallet.balance)

    async def perform_operation(
        self, wallet_uuid: UUID, operation: Union[WalletOperation, tuple]
    ):
        if isinstance(operation, WalletOperation):
            op_type = operation.operation_type
            raw_amount = operation.amount
        else:
            op_type, raw_amount = operation

        amount = self._to_decimal(raw_amount)
        if amount <= 0:
            raise ValueError("amount must be > 0")

        try:
            if op_type == OperationType.DEPOSIT:
                wallet = await self.repo.deposit(wallet_uuid, amount)
            elif op_type == OperationType.WITHDRAW:
                wallet = await self.repo.withdraw(wallet_uuid, amount)
            else:
                raise ValueError("invalid operation_type")
        except InsufficientFunds as exc:
            raise exc

        return wallet

    @staticmethod
    def _to_decimal(value: Union[Decimal, str, float, int]) -> Decimal:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
