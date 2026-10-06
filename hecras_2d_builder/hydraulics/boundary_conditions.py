from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BoundaryCondition:
    location: str
    type: str
    value: float | str


def build_boundary_conditions(upstream_flow: float, downstream_type: str = "normal_depth", downstream_slope: float = 0.001) -> dict[str, BoundaryCondition]:
    if upstream_flow < 0:
        raise ValueError("Upstream flow cannot be negative.")

    return {
        "upstream": BoundaryCondition(location="upstream", type="flow", value=float(upstream_flow)),
        "downstream": BoundaryCondition(location="downstream", type=downstream_type, value=float(downstream_slope)),
    }
