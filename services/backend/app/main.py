"""Service `backend` — orchestrateur (SQUELETTE À COMPLÉTER).

Rôle attendu : exposé au navigateur (via le frontend nginx), il valide
l'entrée avec le **même schéma Pydantic** que le modèle, appelle le service
`model` en interne (`http://model:8000/predict`), et expose `/health`,
`/score`, `/metrics`.

👉 Inspirez-vous du service `model` (déjà fourni) pour le pattern `/metrics`
   et le middleware de logging. Mini-cours : `02_FastAPI_metrics_Prometheus`.
"""
from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.middleware import LoggingMiddleware
from app.schemas import HealthResponse, LoanApplication, Prediction

# URL du service model — configurable par variable d'env (dev/staging/prod)
MODEL_URL = os.environ.get("MODEL_URL", "http://model:8000")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:8088").split(",")

app = FastAPI(title="Pyrenex Backend Orchestrator", version="1.0.0")
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Request-ID"],
)

# TODO 1 — exposer /metrics avec prometheus-fastapi-instrumentator
#   (cf. service model). Pensez à une métrique métier : compteur d'erreurs
#   upstream lors de l'appel au model.


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness du backend (ne dépend PAS du model)."""
    return HealthResponse(status="ok")


# TODO 2 — route POST /score :
#   - reçoit une LoanApplication (validée par Pydantic),
#   - appelle MODEL_URL/predict en interne (httpx async),
#   - propage le header X-Request-ID,
#   - gère les erreurs : model injoignable → 503, model en erreur → 502,
#   - retourne un objet Prediction.
#
# @app.post("/score", response_model=Prediction)
# async def score(application: LoanApplication, request: Request) -> Prediction:
#     ...
