from pathlib import Path


def ensure_project_structure(project_root: str | Path) -> dict[str, Path]:
    root = Path(project_root)
    folders = {
        "root": root,
        "input": root / "input",
        "intermediate": root / "intermediate",
        "output": root / "output",
        "hecras": root / "hecras",
        "gis": root / "gis",
        "logs": root / "logs",
    }
    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)
    return folders
