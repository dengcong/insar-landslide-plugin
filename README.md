# InSAR Landslide Research Suite

A four-skill closed-loop toolchain for InSAR-based landslide monitoring and geohazard manuscripts, packaged as a Devin plugin.

## Skills

| Skill | Role | Entry point |
| :--- | :--- | :--- |
| `landslide-paper-architect` | Orchestrator: Figure-to-Claim Storyboard, captions, Results/Discussion, reviewer defense matrix | prompt-only |
| `geohazard-cartography-qgis` | Executor: DEM hillshade, SAR geometric-distortion masks, 2-D velocity decomposition, 600 DPI QGIS layouts | `scripts/qgis_geohazard_pipeline.py` |
| `insar-figure-python` | Executor: acquisition timelines, 3x3 displacement matrices, driver-response lag plots | `scripts/insar_publication_plots.py` |
| `landslide-quality-supervisor` | Auditor: raster CRS/extent/mask checks, figure DPI gates, JSON audit report | `scripts/audit_geotiff_and_figures.py` |

## Install

```bash
devin plugins install <your-github-user>/insar-landslide-plugin
```

Or install as a repo-scoped skill set: copy `skills/` contents into a checkout's `.devin/skills/`.

## Runtime dependencies

- **Windows (QGIS 3.40 LTR):** `"D:\Program\QGIS\bin\python-qgis-ltr.bat"` provides `qgis.core`, `osgeo.gdal`, `numpy`, `PIL`. Set `QT_QPA_PLATFORM=windows`.
- **Linux / cloud sessions:** `apt-get install qgis python3-qgis xvfb` and `pip install matplotlib scipy pandas pillow`. Run QGIS scripts under `QT_QPA_PLATFORM=offscreen xvfb-run -a`.
