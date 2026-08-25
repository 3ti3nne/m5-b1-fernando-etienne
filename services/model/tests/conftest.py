"""Fixtures pytest — service model (fourni).

Ajoute la racine du service au sys.path pour que `from app.main import app`
fonctionne quand pytest est lancé depuis la racine du repo
(`pytest services/model/tests`).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SERVICE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SERVICE_ROOT))


@pytest.fixture
def client():
    """TestClient FastAPI (déclenche le lifespan → charge le modèle)."""
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def valid_payload() -> dict:
    """Une demande de crédit valide alignée sur LoanApplication."""
    return {
        "loan_amnt": 10000.0,
        "int_rate": 13.5,
        "installment": 340.0,
        "annual_inc": 55000.0,
        "dti": 18.2,
        "delinq_2yrs": 0,
        "fico_range_low": 690,
        "revol_util": 42.5,
        "term": "36 months",
        "grade": "B",
        "home_ownership": "MORTGAGE",
        "verification_status": "Not Verified",
        "purpose": "debt_consolidation",
        "emp_length": "10+ years",
    }
