"""Example pipeline for assembling HEC-RAS 2D ASCII files and previewing the project layout."""

from hecras_2d_builder.hecras.orchestrator import HECRASProjectBuilder


if __name__ == "__main__":
    out_dir = "./modelo_generado"
    nombre = "EstudioHidraulico2D"

    builder = HECRASProjectBuilder(project_dir=out_dir, project_name=nombre)

    perimetro = [
        (450100.0, 1120000.0),
        (450800.0, 1120000.0),
        (450800.0, 1122500.0),
        (450100.0, 1122500.0),
    ]
    borde_aguas_arriba = [(450150.0, 1122500.0), (450750.0, 1122500.0)]
    borde_aguas_abajo = [(450150.0, 1120000.0), (450750.0, 1120000.0)]
    hidrograma = [15.0, 28.0, 75.5, 120.0, 85.0, 42.0, 20.0]

    builder.write_prj()
    builder.write_p01(start_date="01JAN2025,00:00", end_date="01JAN2025,06:00", time_step="30SEC")
    builder.write_g01(
        area_name="RioPrincipal",
        perimeter_coords=perimetro,
        dx=20.0,
        dy=20.0,
        manning=0.040,
        upstream_line=borde_aguas_arriba,
        downstream_line=borde_aguas_abajo,
    )
    builder.write_u01(
        area_name="RioPrincipal",
        hydrograph=hidrograma,
        time_interval="1HOUR",
        friction_slope=0.0025,
    )
    builder.write_rasmap(dem_relative_path=r".\Terreno_Base.tif")

    print(f"Archivos ensamblados en: {out_dir}")
