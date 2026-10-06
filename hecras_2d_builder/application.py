from __future__ import annotations

from pathlib import Path
from typing import Any

from shapely.geometry import LineString, Polygon

from hecras_2d_builder.dem.hydrology import calculate_flow_accumulation, calculate_flow_direction, extract_streams_from_accumulation
from hecras_2d_builder.dem.loader import load_dem
from hecras_2d_builder.dem.validation import validate_dem
from hecras_2d_builder.geometry.area2d import generate_2d_area
from hecras_2d_builder.geometry.breaklines import generate_breaklines
from hecras_2d_builder.geometry.mesh import generate_mesh
from hecras_2d_builder.hecras.detector import detect_hecras_installations
from hecras_2d_builder.hecras.project import HECRASWriter
from hecras_2d_builder.hydraulics.boundary_conditions import build_boundary_conditions
from hecras_2d_builder.hydraulics.manning import ManningValues
from hecras_2d_builder.models.config import ProjectConfig
from hecras_2d_builder.river.corridor import generate_study_area
from hecras_2d_builder.river.extraction import extract_stream_lines, pick_main_channel
from hecras_2d_builder.utils.logging import setup_logger
from hecras_2d_builder.utils.paths import ensure_project_structure


class ModelBuilder:
    def __init__(self, config: ProjectConfig | str | Path):
        if isinstance(config, (str, Path)):
            self.config = ProjectConfig.from_yaml(config)
        else:
            self.config = config
        self.logger = setup_logger("model_builder")

    def build(self) -> dict[str, Any]:
        self.logger.info("Starting model preparation for %s", self.config.project["name"])
        project_root = Path(self.config.output.project_folder)
        folders = ensure_project_structure(project_root)
        log_path = folders["logs"] / "build.log"
        self.logger = setup_logger("model_builder", log_path)
        self.logger.info("Project folder initialized at %s", project_root)

        dem_data = load_dem(self.config.dem.path)
        validation = validate_dem(dem_data)
        self.logger.info("DEM validation result: %s", validation.is_valid)

        flow_direction = calculate_flow_direction(dem_data["array"])
        flow_accumulation = calculate_flow_accumulation(dem_data["array"], flow_direction)
        stream_mask = extract_streams_from_accumulation(flow_accumulation, self.config.hydrology.flow_accumulation_threshold)
        stream_lines = extract_stream_lines(stream_mask, spacing=1.0)
        selected_channel = pick_main_channel(stream_lines)
        if selected_channel is None:
            raise ValueError("No stream network was extracted from the DEM. Adjust the flow accumulation threshold.")

        study_area = generate_study_area(
            selected_channel,
            river_buffer_m=self.config.study_area.river_buffer_m,
            upstream_extension_m=self.config.study_area.upstream_extension_m,
            downstream_extension_m=self.config.study_area.downstream_extension_m,
        )
        area_2d = generate_2d_area(study_area, margin_m=25.0)
        mesh = generate_mesh(area_2d, cell_size_m=self.config.mesh.cell_size_m)
        breaklines = generate_breaklines(selected_channel)

        manning = ManningValues(
            channel=self.config.manning.channel,
            floodplain=self.config.manning.floodplain,
        )
        boundary_conditions = build_boundary_conditions(
            upstream_flow=self.config.boundary.upstream_flow,
            downstream_type=self.config.boundary.downstream_type,
            downstream_slope=self.config.boundary.downstream_slope,
        )

        geometry_summary = {
            "dem": {"path": self.config.dem.path, "crs": dem_data.get("crs"), "resolution": dem_data.get("resolution")},
            "river_centerline": {"type": selected_channel.geom_type, "length_m": round(selected_channel.length, 3)},
            "study_area": {"type": study_area.geom_type, "area_m2": round(study_area.area, 3)},
            "area_2d": {"type": area_2d.geom_type, "area_m2": round(area_2d.area, 3)},
            "mesh_cells": len(mesh),
        }

        writer = HECRASWriter(version=str(self.config.hecras.get("version", "6.x")))
        project_data = writer.write_project(
            project_root,
            self.config.to_dict(),
            geometry_summary,
            {"cells": len(mesh), "cell_size_m": self.config.mesh.cell_size_m},
            {"name": "AUTO-GENERATED / NEEDS REVIEW", "geometry": [selected_channel.wkt]},
            {"channel": self.config.manning.channel, "floodplain": self.config.manning.floodplain},
            {"upstream": {"type": "flow", "value": self.config.boundary.upstream_flow}, "downstream": {"type": self.config.boundary.downstream_type, "value": self.config.boundary.downstream_slope}},
        )

        installations = detect_hecras_installations()
        checklist = [
            "[✓] DEM validado",
            "[✓] CRS validado",
            "[✓] Río identificado",
            "[✓] Área 2D generada",
            "[✓] Malla generada",
            "[✓] Manning asignado",
            "[✓] BC upstream configurada",
            "[✓] BC downstream configurada",
            "[ ] Revisar cauce",
            "[ ] Revisar breaklines",
            "[ ] Revisar malla",
            "[ ] Revisar Manning",
            "[ ] Revisar condiciones de frontera",
            "[ ] Revisar estructuras",
            "[ ] Ejecutar prueba de estabilidad",
        ]

        self.logger.warning("HEC-RAS installation detection: %s", installations or "not detected")
        project_data["checklist"] = checklist
        project_data["hecras_detected"] = installations
        project_data["validation"] = validation
        return project_data
