"""Service `backend` — orchestrateur."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from app.metrics import observe_upstream_error
from app.middleware import LoggingMiddleware
from app.schemas import HealthResponse, LoanApplication, Prediction

MODEL_URL = os.environ.get("MODEL_URL", "http://model:8000")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:8088").split(",")
MODEL_TIMEOUT_S = float(os.environ.get("MODEL_TIMEOUT_S", "5"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(
        base_url=MODEL_URL, timeout=MODEL_TIMEOUT_S
    ) as client:
        app.state.model_client = client
        logger.info("Backend ready, model upstream: {url}", url=MODEL_URL)
        yield


app = FastAPI(
    title="Pyrenex Backend Orchestrator", version="1.0.0", lifespan=lifespan
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Request-ID"],
)

Instrumentator(should_group_status_codes=False).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness du backend (ne dépend PAS du model)."""
    return HealthResponse(status="ok")


@app.post("/score", response_model=Prediction)
async def score(application: LoanApplication, request: Request) -> Prediction:
    request_id = getattr(request.state, "request_id", "n/a")
    log = logger.bind(request_id=request_id)

    try:
        response = await request.app.state.model_client.post(
            "/predict",
            json=application.model_dump(),
            headers={"X-Request-ID": request_id},
        )
    except httpx.TimeoutException as exc:
        observe_upstream_error("timeout")
        log.error("Model service timed out after {t}s", t=MODEL_TIMEOUT_S)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model service timed out",
        ) from exc
    except httpx.RequestError as exc:
        observe_upstream_error("unreachable")
        log.error("Model service unreachable: {err}", err=exc.__class__.__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model service unreachable",
        ) from exc

    if response.status_code != status.HTTP_200_OK:
        observe_upstream_error("http_error")
        log.error("Model service returned {status}", status=response.status_code)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Model service error (HTTP {response.status_code})",
        )

    return Prediction(**response.json())