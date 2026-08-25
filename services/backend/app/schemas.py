"""Pydantic schemas for the Pyrenex Risk API — fourni.

Aligned with feature_columns from pyrenex_risk_v2.json (M1-B1 correctif).
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class LoanApplication(BaseModel):
    """Input schema for /predict.

    Bounds informed by EDA on Lending Club:
    - loan_amnt: 500-40k USD (LC limits)
    - int_rate: 0-50 % (annualized)
    - annual_inc: 0-10M USD (extreme outliers tolerated)
    - dti: 0-200 (DtI can exceed 100 in theory)
    - revol_util: 0-300 (LC allows > 100)
    """

    # Numeric features — aligned with feature_columns_numeric of pyrenex_risk_v2.json
    loan_amnt: float = Field(..., ge=500, le=40_000, description="Loan amount (USD)")
    int_rate: float = Field(..., ge=0, le=50, description="Interest rate (%)")
    installment: float = Field(..., ge=0, le=2000, description="Monthly installment (USD)")
    annual_inc: float = Field(..., ge=0, le=10_000_000, description="Annual income (USD)")
    dti: float = Field(..., ge=0, le=200, description="Debt-to-income ratio")
    delinq_2yrs: int = Field(..., ge=0, le=50, description="Delinquencies in past 2 years")
    fico_range_low: int = Field(..., ge=300, le=850, description="FICO score lower bound")
    revol_util: float = Field(..., ge=0, le=300, description="Revolving credit utilization (%)")

    # Categorical features — aligned with feature_columns_categorical of pyrenex_risk_v2.json
    term: Literal["36 months", "60 months"] = Field(..., description="Loan term")
    grade: Literal["A", "B", "C", "D", "E", "F", "G"]
    home_ownership: Literal["RENT", "OWN", "MORTGAGE", "OTHER", "NONE", "ANY"]
    verification_status: Literal["Verified", "Source Verified", "Not Verified"]
    purpose: str = Field(..., description="Purpose of the loan (e.g. debt_consolidation)")
    emp_length: str = Field(
        ...,
        description="Employment length, e.g. '< 1 year', '1 year', ..., '10+ years'",
    )


class Prediction(BaseModel):
    """Output schema for /predict."""

    prediction: int = Field(..., description="0 = Fully Paid, 1 = Charged Off")
    probability: float = Field(..., ge=0.0, le=1.0)
    model_version: str
    request_id: str


class HealthResponse(BaseModel):
    """Output schema for /health."""

    status: str


class InfoResponse(BaseModel):
    """Output schema for /info."""

    api_version: str
    model_name: str
    model_version: str
    model_created_at: str
    metrics_holdout: dict | None = None
    sklearn_version: str | None = None
    dataset_sha256: str | None = None
