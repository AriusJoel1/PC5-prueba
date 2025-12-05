# app/main.py
from fastapi import FastAPI
from app.routers import tenants
from app.db.base import Base
from app.db.session import engine
from fastapi.middleware.cors import CORSMiddleware

# Create DB tables on startup (simple approach)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tenant Config Service", version="0.1.0")

# Simple CORS (dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

app.include_router(tenants.router)
