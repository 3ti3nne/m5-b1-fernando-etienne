"""Single source of truth for loading the Pyrenex risk model.

Used by three independent consumers:
- ``app.main.lifespan``     — boot the API (long-running uvicorn process)
- ``scripts.sanity_check``  — manual dev-time check (ephemeral process)
- ``tests.test_model_contract`` — CI-time machine asserts (pytest process)

DRY on the loading recipe, not on the RAM: each consumer loads its own
copy in its own Python process. That is the expected ML serving pattern.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib

MODEL_FILENAME = "pyrenex_risk_v2.joblib"
METADATA_FILENAME = "pyrenex_risk_v2.json"


def load_model_and_metadata(models_dir: Path) -> tuple[Any, dict]:
    """Load the Pyrenex risk model and its metadata from a models directory.

    Args:
        models_dir: Directory containing ``pyrenex_risk_v2.joblib`` and
            ``pyrenex_risk_v2.json``.

    Returns:
        A ``(model, metadata)`` tuple where ``model`` is a fitted
        scikit-learn estimator and ``metadata`` is the parsed JSON.

    Raises:
        FileNotFoundError: If either the model or the metadata file is
            missing from ``models_dir``.
    """
    model_path = models_dir / MODEL_FILENAME
    meta_path = models_dir / METADATA_FILENAME

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at {model_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata file not found at {meta_path}")

    model = joblib.load(model_path)
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    return model, metadata