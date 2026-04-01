from enum import Enum
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletOperation(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(..., gt=0)

    model_config = ConfigDict(
        json_schema_extra={"example": {"operation_type": "DEPOSIT", "amount": "100.00"}}
    )


class WalletResponse(BaseModel):
    wallet_id: UUID
    balance: Decimal

    model_config = ConfigDict(
        from_attributes=True,
        json_serializers={Decimal: str},
    )
