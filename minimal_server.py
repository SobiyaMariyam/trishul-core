#!/usr/bin/env python3
"""
Minimal test server to debug the health endpoint issue
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "message": "minimal health check"}

@app.get("/")
async def root():
    return {"message": "minimal server running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)