from __future__ import annotations

import os
from pathlib import Path


def detect_hecras_installations() -> list[str]:
    """Look for HEC-RAS installations. The implementation is intentionally safe and informational."""
    candidates: list[str] = []
    if os.name == "nt":
        likely_paths = [
            Path(r"C:\\Program Files\\HEC\\HEC-RAS"),
            Path(r"C:\\Program Files\\HEC"),
            Path(r"C:\\Program Files (x86)\\HEC"),
        ]
        for base in likely_paths:
            if base.exists():
                for child in sorted(base.iterdir()):
                    if "HEC-RAS" in child.name:
                        candidates.append(child.name)
        return sorted(set(candidates))
    return []
