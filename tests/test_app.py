# tests/test_app.py
import os
import json
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db import models
from app.db.session import get_db

# Configurar DB en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Reemplazar dependencia get_db para usar la de testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Crear tablas
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_put_get_same_tenant():
    headers = {"X-Tenant-Id": "tenant-a"}
    payload = {"config": {"k": "v"}}
    # put
    r = client.put("/tenants/tenant-a/config", json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["tenant_id"] == "tenant-a"
    assert r.json()["config"] == payload["config"]

    # get
    r2 = client.get("/tenants/tenant-a/config", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["config"] == payload["config"]

def test_cross_tenant_forbidden():
    # Put as tenant-a but try to access tenant-b
    headers = {"X-Tenant-Id": "tenant-a"}
    payload = {"config": {"hello": "world"}}
    r = client.put("/tenants/tenant-b/config", json=payload, headers=headers)
    assert r.status_code == 403

    # Also test get forbidden
    r2 = client.get("/tenants/tenant-b/config", headers=headers)
    assert r2.status_code in (403, 404)  # either forbidden or not found depending on state
