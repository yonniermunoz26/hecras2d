from __future__ import annotations

import numpy as np
from shapely.geometry import LineString, Polygon

from hecras_2d_builder.dem.hydrology import calculate_flow_accumulation, calculate_flow_direction
from hecras_2d_builder.dem.validation import validate_dem
from hecras_2d_builder.geometry.mesh import generate_mesh
from hecras_2d_builder.hecras.orchestrator import HECRASProjectBuilder
from hecras_2d_builder.hydraulics.boundary_conditions import build_boundary_conditions
from hecras_2d_builder.models.config import ProjectConfig
from hecras_2d_builder.river.corridor import generate_study_area


def test_project_config_loads_from_dict():
    cfg = ProjectConfig.from_dict({
        "project": {"name": "test_model", "crs": "EPSG:32618"},
        "dem": {"path": "data/dem.tif", "resolution": 10},
        "hydrology": {"flow_accumulation_threshold": 1000, "stream_snap_distance": 20},
        "study_area": {"river_buffer_m": 500, "upstream_extension_m": 300, "downstream_extension_m": 400},
        "mesh": {"cell_size_m": 10, "refinement": 1},
        "manning": {"channel": 0.035, "floodplain": 0.060},
        "boundary": {"upstream_flow": 250, "downstream_type": "normal_depth", "downstream_slope": 0.001},
        "output": {"project_folder": "./output", "project_name": "test_model"},
        "hecras": {"version": "6.x", "auto_run": False},
    })
    assert cfg.project["name"] == "test_model"
    assert cfg.mesh.cell_size_m == 10
    assert cfg.boundary.upstream_flow == 250


def test_validate_dem_detects_simple_problem():
    dem = {"array": np.array([[1.0, 2.0], [3.0, 4.0]]), "crs": "EPSG:32618", "resolution": 10.0, "nodata": None}
    result = validate_dem(dem)
    assert result.is_valid is True
    assert result.stats["resolution"] == 10.0


def test_flow_direction_and_accumulation_are_generated():
    dem = np.array([
        [10.0, 9.0, 8.0],
        [9.0, 7.0, 6.0],
        [8.0, 7.0, 5.0],
    ])
    flow_dir = calculate_flow_direction(dem)
    flow_acc = calculate_flow_accumulation(dem, flow_dir)
    assert flow_dir.shape == dem.shape
    assert flow_acc.shape == dem.shape
    assert np.all(flow_acc >= 1.0)


def test_flow_accumulation_counts_upstream_points():
    dem = np.zeros((30, 30), dtype=float)
    dem[:, :] = np.linspace(0, 29, 30)
    dem = dem + np.arange(30)[:, None]
    flow_dir = calculate_flow_direction(dem)
    flow_acc = calculate_flow_accumulation(dem, flow_dir)
    assert flow_acc.max() > 10


def test_generate_study_area_and_mesh():
    line = LineString([(0, 0), (100, 0), (200, 0)])
    area = generate_study_area(line, river_buffer_m=50, upstream_extension_m=20, downstream_extension_m=20)
    mesh = generate_mesh(area, cell_size_m=20)
    assert area.is_valid
    assert len(mesh) > 0
    assert mesh.geometry.iloc[0].area > 0


def test_boundary_conditions_are_valid():
    bc = build_boundary_conditions(250, downstream_type="normal_depth", downstream_slope=0.001)
    assert bc["upstream"].value == 250
    assert bc["downstream"].type == "normal_depth"
    assert bc["downstream"].value == 0.001


def test_hecras_native_files_are_written(tmp_path):
    builder = HECRASProjectBuilder(project_dir=str(tmp_path), project_name="Modelo2D")
    perimeter = [(100.0, 100.0), (500.0, 100.0), (500.0, 800.0), (100.0, 800.0)]
    upstream = [(150.0, 800.0), (450.0, 800.0)]
    downstream = [(150.0, 100.0), (450.0, 100.0)]

    prj = builder.write_prj()
    builder.write_p01("01JAN2025,00:00", "01JAN2025,12:00", time_step="1MIN")
    builder.write_g01("Area2D", perimeter, dx=10.0, dy=10.0, manning=0.035, upstream_line=upstream, downstream_line=downstream)
    builder.write_u01("Area2D", [10.0, 25.0, 50.0, 30.0, 10.0], time_interval="1HOUR", friction_slope=0.0015)
    builder.write_rasmap(".\\Terreno_Base.tif")

    assert prj.exists()
    assert (tmp_path / "Modelo2D.g01").exists()
    assert (tmp_path / "Modelo2D.u01").exists()
    assert (tmp_path / "Modelo2D.p01").exists()
    assert (tmp_path / "Modelo2D.rasmap").exists()
    assert "Geom File=g01" in prj.read_text(encoding="ascii")
    assert "2D Flow Area=Area2D" in (tmp_path / "Modelo2D.g01").read_text(encoding="ascii")
    assert "Boundary Location=Area2D,BC_Upstream,Flow Hydrograph" in (tmp_path / "Modelo2D.u01").read_text(encoding="ascii")
