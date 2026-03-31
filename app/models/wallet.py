from decimal import Decimal
import uuid
from uuid import UUID as PyUUID

from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric

from app.db.base import Base


class Wallet(Base):
    __tablename__ = "wallets"

    uuid: Mapped[PyUUID] = mapped_column(
        SQLUUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )

    __table_args__ = CheckConstraint("balance >= 0", name="positive_balance")
