from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from hecras_2d_builder.utils.logging import setup_logger


class HECRASWriter:
    def __init__(self, version: str = "6.x") -> None:
        self.version = version
        self.logger = setup_logger("hecras_writer")

    def write_project(self, project_dir: str | Path, config: dict[str, Any], geometry: dict[str, Any], mesh: dict[str, Any], breaklines: dict[str, Any], manning: dict[str, Any], boundary_conditions: dict[str, Any]) -> dict[str, Any]:
        project_root = Path(project_dir)
        project_root.mkdir(parents=True, exist_ok=True)
        hecras_dir = project_root / "hecras"
        hecras_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "version": self.version,
            "model_name": config.get("project", {}).get("name", "hecras_model"),
            "auto_run": False,
            "human_review_required": True,
            "warning": "The generated model is an initial configuration and must be reviewed by a hydraulic engineer before simulation execution.",
            "generated_files": [],
        }

        docs = {
            "project": {"name": config.get("project", {}).get("name", "hecras_model")},
            "geometry": geometry,
            "mesh": mesh,
            "breaklines": breaklines,
            "manning": manning,
            "boundary_conditions": boundary_conditions,
            "version": self.version,
        }

        with open(hecras_dir / "project_manifest.yaml", "w", encoding="utf-8") as fh:
            yaml.safe_dump(metadata, fh, sort_keys=False)
            fh.write("\n")

        with open(hecras_dir / "geometry.json", "w", encoding="utf-8") as fh:
            json.dump(geometry, fh, indent=2)

        with open(hecras_dir / "plan.json", "w", encoding="utf-8") as fh:
            json.dump({"version": self.version, "auto_run": False, "requires_human_review": True}, fh, indent=2)

        with open(hecras_dir / "unsteady_flow.json", "w", encoding="utf-8") as fh:
            json.dump({"boundary_conditions": boundary_conditions, "upstream_flow": config.get("boundary", {}).get("upstream_flow", 250)}, fh, indent=2)

        with open(hecras_dir / "README.txt", "w", encoding="utf-8") as fh:
            fh.write(
                "HEC-RAS 2D semi-automatic model builder\n"
                "===================================\n\n"
                "This project contains a GIS and configuration export for HEC-RAS review.\n"
                "It is not a verified official HEC-RAS file set and the model must be reviewed manually before execution.\n"
                "AUTO-RUN = FALSE\n"
                "REQUIRES HUMAN REVIEW\n"
            )

        metadata["generated_files"] = [
            str(hecras_dir / "project_manifest.yaml"),
            str(hecras_dir / "geometry.json"),
            str(hecras_dir / "plan.json"),
            str(hecras_dir / "unsteady_flow.json"),
            str(hecras_dir / "README.txt"),
        ]
        with open(hecras_dir / "project_manifest.yaml", "w", encoding="utf-8") as fh:
            yaml.safe_dump(metadata, fh, sort_keys=False)
            fh.write("\n")

        self.logger.info("HEC-RAS project scaffolding generated at %s", project_root)
        return {"project_dir": str(project_root), "hecras_dir": str(hecras_dir), "metadata": metadata, "docs": docs}
