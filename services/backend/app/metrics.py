from __future__ import annotations

from typing import Literal

from prometheus_client import Counter

UPSTREAM_ERRORS = Counter(
    "backend_upstream_errors_total",
    "Failed calls to the model service, by failure kind.",
    labelnames=("kind",),
)

UpstreamErrorKind = Literal["timeout", "unreachable", "http_error"]


def observe_upstream_error(kind: UpstreamErrorKind) -> None:
    UPSTREAM_ERRORS.labels(kind=kind).inc()