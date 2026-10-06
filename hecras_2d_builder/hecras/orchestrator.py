from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


class HECRASProjectBuilder:
    """Build a minimal native HEC-RAS ASCII project scaffold for manual review."""

    def __init__(self, project_dir: str, project_name: str):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.name = project_name

    def _render_coord_block(self, points: Sequence[Tuple[float, float]]) -> str:
        return "    ".join(f"{x:.2f},{y:.2f}" for x, y in points)

    def write_prj(self) -> Path:
        content = (
            f"Proj Title={self.name}\n"
            "Current Plan=p01\n"
            "Default Exp/Contr=0.3,0.1\n"
            "SI Units\n"
            "Geom File=g01\n"
            "Unsteady File=u01\n"
            "Plan File=p01\n"
            f"RasMap File={self.name}.rasmap\n"
            "Description=Modelo 2D generado automaticamente via Python\n"
            "Y Axis Title=Elevation\n"
            "X Axis Title=Station\n"
        )
        file_path = self.project_dir / f"{self.name}.prj"
        file_path.write_text(content, encoding="ascii")
        return file_path

    def write_p01(self, start_date: str, end_date: str | None = None, time_step: str = "1MIN") -> Path:
        if end_date is not None:
            simulation_date = f"{start_date},{end_date}"
        else:
            simulation_date = start_date
        content = (
            "Plan Title=Plan Automatizado 01\n"
            "Program Name=RasUnsteady\n"
            "Short Identifier=p01\n"
            f"Simulation Date={simulation_date}\n"
            f"Computation Interval={time_step}\n"
            "Output Interval=5MIN\n"
            "Mapping Interval=5MIN\n"
            "Hydrograph Output Interval=5MIN\n"
            "Run Unsteady= 1\n"
            "Run PostProcess= 1\n"
            "Geom File=g01\n"
            "Unsteady File=u01\n"
            "2D Flow Equation=Diffusion Wave\n"
            "Theta= 1.0\n"
            "Theta WarmUp= 1.0\n"
            "Diffusion Wave Tolerance= 0.003\n"
        )
        file_path = self.project_dir / f"{self.name}.p01"
        file_path.write_text(content, encoding="ascii")
        return file_path

    def write_g01(
        self,
        area_name: str,
        perimeter_coords: Sequence[Tuple[float, float]],
        dx: float,
        dy: float,
        manning: float,
        upstream_line: Sequence[Tuple[float, float]],
        downstream_line: Sequence[Tuple[float, float]],
    ) -> Path:
        content = (
            "Geom Title=Geometria_Automatica_2D\n"
            "Program Name=RasGeometry\n\n"
            f"2D Flow Area={area_name}\n"
            f"Cell Size={dx:.2f},{dy:.2f}\n"
            f"Default Mann={manning:.4f}\n"
            f"Outer Perimeter= {len(perimeter_coords)}\n"
            f"    {self._render_coord_block(perimeter_coords)}\n\n"
            "Boundary Line=BC_Upstream\n"
            f"Boundary Line Point Count= {len(upstream_line)}\n"
            f"    {self._render_coord_block(upstream_line)}\n\n"
            "Boundary Line=BC_Downstream\n"
            f"Boundary Line Point Count= {len(downstream_line)}\n"
            f"    {self._render_coord_block(downstream_line)}\n"
        )
        file_path = self.project_dir / f"{self.name}.g01"
        file_path.write_text(content, encoding="ascii")
        return file_path

    def write_u01(
        self,
        area_name: str,
        hydrograph: Sequence[float],
        time_interval: str,
        friction_slope: float,
    ) -> Path:
        flow_values = " ".join(f"{val:10.2f}" for val in hydrograph)
        content = (
            "Flow Title=Hidrograma_Diseno\n"
            "Program Name=RasUnsteady\n"
            f"Boundary Location={area_name},BC_Upstream,Flow Hydrograph\n"
            "Stage Hydrograph TW Check= 0\n"
            f"Flow Hydrograph= {len(hydrograph)}\n"
            f"     {flow_values}\n"
            f"Interval={time_interval}\n"
            "Flow Hydrograph Slope= 0.002\n\n"
            f"Boundary Location={area_name},BC_Downstream,Normal Depth\n"
            f"Friction Slope= {friction_slope:.5f}\n"
        )
        file_path = self.project_dir / f"{self.name}.u01"
        file_path.write_text(content, encoding="ascii")
        return file_path

    def write_rasmap(self, dem_relative_path: str) -> Path:
        content = (
            "<RASMapper>\n"
            "  <Version>2.0.0</Version>\n"
            "  <Terrains Checked=\"True\" Expanded=\"True\">\n"
            f'    <Terrain Name="Terreno_Base" Type="Raster" Filename="{dem_relative_path}"/>\n'
            "  </Terrains>\n"
            "  <Geometries Checked=\"True\" Expanded=\"True\">\n"
            f'    <Layer Name="Geometria_Automatica_2D" Filename=".\\{self.name}.g01"/>\n'
            "  </Geometries>\n"
            "</RASMapper>\n"
        )
        file_path = self.project_dir / f"{self.name}.rasmap"
        file_path.write_text(content, encoding="utf-8")
        return file_path


class HECRASRunner:
    """Optional COM automation hook for Windows installations of HEC-RAS."""

    def __init__(self, ras_prog_id: str = "RAS61.HECRASController"):
        self.prog_id = ras_prog_id

    def execute_project(self, prj_path: str | Path) -> bool:
        prj_path = Path(prj_path).resolve()
        try:
            import win32com.client  # type: ignore
        except Exception as exc:  # pragma: no cover - platform-specific path
            raise RuntimeError(f"Windows COM automation is unavailable on this system: {exc}")

        hec = win32com.client.Dispatch(self.prog_id)
        hec.ShowRas()
        try:
            hec.Project_Open(str(prj_path))
            success, messages, blocked = hec.Compute_CurrentPlan(None, None, True)
            if success:
                return True
            raise RuntimeError(f"HEC-RAS returned an execution error: {messages}")
        finally:
            hec.Project_Close()
            hec.QuitRas()
