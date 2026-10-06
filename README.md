# HEC-RAS 2D Semi-Automatic Model Builder

This project is a Python-based MVP for preparing an initial HEC-RAS 2D model from a DEM and GIS information. The workflow is intentionally semi-automatic: it prepares a GIS-ready foundation, generates an initial 2D area, mesh, breaklines, and boundary definitions, but it does not execute HEC-RAS or claim the hydraulic setup is final.

> El modelo generado es una configuración inicial y debe ser revisado por un modelador antes de ejecutar la simulación hidráulica.

## Goals

- Load and validate a DEM.
- Compute a drainage network from flow accumulation.
- Allow manual selection of a river reach.
- Generate a preliminary study corridor and 2D flow area.
- Create a coarse mesh and breakline proposal.
- Set basic Manning values and boundary conditions.
- Produce a project scaffold and logs for HEC-RAS review.
- Keep all operations reproducible via configuration and logs.

## Project structure

```text
hecras_2d_builder/
├── application.py
├── app.py
├── dem/
├── geometry/
├── hecras/
├── hydraulics/
├── models/
├── river/
├── utils/
├── config/
├── dem_processing.py
└── __init__.py
```

## Installation on Windows

1. Install Python 3.11 or newer.
2. Open a terminal in the project folder.
3. Create a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

5. Validate the project:

```powershell
python -m pytest
```

6. Run the CLI builder:

```powershell
python app.py examples/example_config.yaml
```

## Example configuration

See [examples/example_config.yaml](examples/example_config.yaml).

## Design notes

The current MVP intentionally keeps the HEC-RAS export at a safe compatibility layer. It generates structured project metadata and configuration files, but does not claim to reproduce the internal binary or XML format of a real HEC-RAS project. In a production implementation, the writer should be validated against a concrete installed HEC-RAS version and an example project before writing the final official file set.

## Known limitations

- No true GIS editor or map UI is included in this MVP.
- HEC-RAS installation detection is only informative and only likely works on Windows.
- The DEM hydrology logic is a simplified algorithm and is designed for rapid prototyping, not final hydraulic modeling.
- The generated HEC-RAS files are structured exports for review, not final official HEC-RAS project specification files.

## Safety philosophy

This tool prepares a starting configuration for review, not a verified hydraulic simulation package. The workflow keeps the user responsible for reviewing source data, geometry, Manning values, boundary conditions, and final execution in HEC-RAS.

## Checklist after generation

- [x] DEM validated
- [x] CRS validated
- [x] River identified
- [x] 2D area generated
- [x] Mesh generated
- [x] Manning assigned
- [x] Upstream BC configured
- [x] Downstream BC configured
- [ ] Review channel geometry
- [ ] Review breaklines
- [ ] Review mesh
- [ ] Review Manning values
- [ ] Review boundary conditions
- [ ] Review structures
- [ ] Run stability check

## Notes on HEC-RAS compatibility

This MVP does not attempt to reverse-engineer unofficial HEC-RAS file formats. The intended next step is to identify the exact installed HEC-RAS version, create a small reference project manually, inspect the official generated files, and then implement a version-aware writer only after confirming the file layout against those examples.
