from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.repositories.wallet_repository import WalletRepository, InsufficientFunds
from app.services.wallet_service import WalletService, WalletNotFound
from app.schemas.wallet_schema import WalletOperation, WalletResponse

router = APIRouter()


@router.get("/wallets/{wallet_uuid}", response_model=WalletResponse)
async def get_wallet_balance(wallet_uuid: UUID, db: AsyncSession = Depends(get_db)):
    repo = WalletRepository(db)
    service = WalletService(repo)
    try:
        balance = await service.get_balance(wallet_uuid)
    except WalletNotFound:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return WalletResponse(wallet_id=wallet_uuid, balance=balance)


@router.post("/wallets/{wallet_uuid}/operation", response_model=WalletResponse)
async def wallet_operation(
    wallet_uuid: UUID, op: WalletOperation, db: AsyncSession = Depends(get_db)
):
    repo = WalletRepository(db)
    service = WalletService(repo)
    try:
        wallet = await service.perform_operation(wallet_uuid, op)
    except InsufficientFunds:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return WalletResponse(wallet_id=wallet.uuid, balance=wallet.balance)
