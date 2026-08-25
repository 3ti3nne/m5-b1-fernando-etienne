"""Tests API + contract test du modèle — service model (fourni)."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

MODELS_DIR = Path(__file__).parent.parent / "models"


# --- Tests API --------------------------------------------------------------

def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_predict_valid_returns_class_and_proba(client, valid_payload):
    resp = client.post("/predict", json=valid_payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["prediction"] in (0, 1)
    assert 0.0 <= body["probability"] <= 1.0
    assert body["model_version"] == "v2.0.0"


def test_predict_invalid_returns_422(client, valid_payload):
    bad = dict(valid_payload)
    bad["fico_range_low"] = 9999  # hors bornes (300-850)
    resp = client.post("/predict", json=bad)
    assert resp.status_code == 422


def test_metrics_endpoint_exposes_prometheus(client, valid_payload):
    client.post("/predict", json=valid_payload)  # génère au moins 1 observation
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "pyrenex_predictions_total" in resp.text


# --- Contract test du modèle (bloque la release en CI) ----------------------

def test_model_contract_features_and_output():
    """Le modèle chargé accepte EXACTEMENT les features attendues et sort
    une proba dans [0, 1] — garde-fou anti-régression schéma."""
    model = joblib.load(MODELS_DIR / "pyrenex_risk_v2.joblib")
    meta = json.loads((MODELS_DIR / "pyrenex_risk_v2.json").read_text())

    cols = meta["feature_columns_numeric"] + meta["feature_columns_categorical"]
    row = {
        "loan_amnt": 10000.0, "int_rate": 13.5, "installment": 340.0,
        "annual_inc": 55000.0, "dti": 18.2, "delinq_2yrs": 0,
        "fico_range_low": 690, "revol_util": 42.5, "term": "36 months",
        "grade": "B", "home_ownership": "MORTGAGE",
        "verification_status": "Not Verified", "purpose": "debt_consolidation",
        "emp_length": "10+ years",
    }
    X = pd.DataFrame([row])[cols]
    proba = float(model.predict_proba(X)[0, 1])
    assert 0.0 <= proba <= 1.0
