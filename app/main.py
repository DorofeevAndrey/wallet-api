from fastapi import FastAPI

from app.api.v1 import wallets

app = FastAPI(title="Wallet API")

app.include_router(wallets.router, prefix="/api/v1")
