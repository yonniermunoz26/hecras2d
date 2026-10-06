from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass
class DEMConfig:
    path: str = ""
    resolution: float = 10.0


@dataclass
class HydrologyConfig:
    flow_accumulation_threshold: int = 1000
    stream_snap_distance: float = 25.0


@dataclass
class StudyAreaConfig:
    river_buffer_m: float = 500.0
    upstream_extension_m: float = 300.0
    downstream_extension_m: float = 400.0


@dataclass
class MeshConfig:
    cell_size_m: float = 10.0
    refinement: float = 1.0


@dataclass
class ManningConfig:
    channel: float = 0.035
    floodplain: float = 0.060


@dataclass
class BoundaryConfig:
    upstream_flow: float = 250.0
    downstream_type: str = "normal_depth"
    downstream_slope: float = 0.001


@dataclass
class OutputConfig:
    project_folder: str = "./output"
    project_name: str = "hecras_model"


@dataclass
class ProjectConfig:
    project: Dict[str, Any] = field(default_factory=lambda: {"name": "hecras_model", "crs": "EPSG:32618"})
    dem: DEMConfig = field(default_factory=DEMConfig)
    hydrology: HydrologyConfig = field(default_factory=HydrologyConfig)
    study_area: StudyAreaConfig = field(default_factory=StudyAreaConfig)
    mesh: MeshConfig = field(default_factory=MeshConfig)
    manning: ManningConfig = field(default_factory=ManningConfig)
    boundary: BoundaryConfig = field(default_factory=BoundaryConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    hecras: Dict[str, Any] = field(default_factory=lambda: {"version": "6.x", "auto_run": False})

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ProjectConfig":
        with open(path, "r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        return cls.from_dict(raw)

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "ProjectConfig":
        project = raw.get("project", {})
        dem = raw.get("dem", {})
        hydrology = raw.get("hydrology", {})
        study_area = raw.get("study_area", {})
        mesh = raw.get("mesh", {})
        manning = raw.get("manning", {})
        boundary = raw.get("boundary", {})
        output = raw.get("output", {})
        hecras = raw.get("hecras", {})

        return cls(
            project={"name": project.get("name", "hecras_model"), "crs": project.get("crs", "EPSG:32618")},
            dem=DEMConfig(path=dem.get("path", ""), resolution=float(dem.get("resolution", 10.0))),
            hydrology=HydrologyConfig(
                flow_accumulation_threshold=int(hydrology.get("flow_accumulation_threshold", 1000)),
                stream_snap_distance=float(hydrology.get("stream_snap_distance", 25.0)),
            ),
            study_area=StudyAreaConfig(
                river_buffer_m=float(study_area.get("river_buffer_m", 500.0)),
                upstream_extension_m=float(study_area.get("upstream_extension_m", 300.0)),
                downstream_extension_m=float(study_area.get("downstream_extension_m", 400.0)),
            ),
            mesh=MeshConfig(
                cell_size_m=float(mesh.get("cell_size_m", 10.0)),
                refinement=float(mesh.get("refinement", 1.0)),
            ),
            manning=ManningConfig(
                channel=float(manning.get("channel", 0.035)),
                floodplain=float(manning.get("floodplain", 0.060)),
            ),
            boundary=BoundaryConfig(
                upstream_flow=float(boundary.get("upstream_flow", 250.0)),
                downstream_type=str(boundary.get("downstream_type", "normal_depth")),
                downstream_slope=float(boundary.get("downstream_slope", 0.001)),
            ),
            output=OutputConfig(
                project_folder=str(output.get("project_folder", "./output")),
                project_name=str(output.get("project_name", "hecras_model")),
            ),
            hecras={"version": str(hecras.get("version", "6.x")), "auto_run": bool(hecras.get("auto_run", False))},
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project": self.project,
            "dem": {"path": self.dem.path, "resolution": self.dem.resolution},
            "hydrology": {
                "flow_accumulation_threshold": self.hydrology.flow_accumulation_threshold,
                "stream_snap_distance": self.hydrology.stream_snap_distance,
            },
            "study_area": {
                "river_buffer_m": self.study_area.river_buffer_m,
                "upstream_extension_m": self.study_area.upstream_extension_m,
                "downstream_extension_m": self.study_area.downstream_extension_m,
            },
            "mesh": {"cell_size_m": self.mesh.cell_size_m, "refinement": self.mesh.refinement},
            "manning": {"channel": self.manning.channel, "floodplain": self.manning.floodplain},
            "boundary": {
                "upstream_flow": self.boundary.upstream_flow,
                "downstream_type": self.boundary.downstream_type,
                "downstream_slope": self.boundary.downstream_slope,
            },
            "output": {"project_folder": self.output.project_folder, "project_name": self.output.project_name},
            "hecras": self.hecras,
        }

    def save(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(self.to_dict(), fh, sort_keys=False)
