from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ManningValues:
    channel: float
    floodplain: float

    @classmethod
    def from_config(cls, config: dict) -> "ManningValues":
        return cls(channel=float(config.get("channel", 0.035)), floodplain=float(config.get("floodplain", 0.060)))


def validate_manning(values: ManningValues) -> list[str]:
    warnings: list[str] = []
    if values.channel <= 0:
        warnings.append("Channel Manning value must be positive.")
    if values.floodplain <= 0:
        warnings.append("Floodplain Manning value must be positive.")
    if values.floodplain > 0.1:
        warnings.append("Manning floodplain value is unusually high. Verify it is appropriate for the land cover.")
    return warnings
