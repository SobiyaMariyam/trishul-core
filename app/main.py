from fastapi import FastAPI, Request

from app.middleware.tenancy import tenancy_middleware

app = FastAPI(title="Trishul Core API")


@app.middleware("http")
async def tenancy(request: Request, call_next):
    return await tenancy_middleware(request, call_next)


@app.get("/health")
def health():
    return {"ok": True}
