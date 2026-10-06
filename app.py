from __future__ import annotations

import argparse
from pathlib import Path

from hecras_2d_builder.application import ModelBuilder
from hecras_2d_builder.models.config import ProjectConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="HEC-RAS 2D semi-automatic model builder")
    parser.add_argument("config", type=str, help="Path to a YAML project configuration file")
    args = parser.parse_args()

    config_path = Path(args.config)
    builder = ModelBuilder(config_path)
    result = builder.build()
    print("Configuration initial generated. Human review required before simulation.")
    print(result["project_dir"])


if __name__ == "__main__":
    main()
