from fastapi import FastAPI

app = FastAPI(title="Wallet-API")


@app.get("/")
def root():
    return {"status": "ok"}
