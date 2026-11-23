---
name: geohazard-cartography-qgis
description: Executor skill for multi-scale landslide GIS cartography and PyQGIS map rendering. Use when creating four-panel nested study area overview maps, multi-directional DEM hillshade micro-geomorphology comparisons, 2.5D/3D terrain perspective velocity overlays, or matched-extent ascending/descending SAR geometric distortion and slope/aspect grids.
---

# Geohazard Cartography QGIS

Execute publication-grade spatial cartography, terrain geomorphometry, SAR geometric visibility modeling, and PyQGIS print layout exports for landslide and geohazard research.

## When to Use

- Rendering four-panel nested study area overview maps (regional tectonic setting, watershed topography, lithology/faults, and slope-scale inventory).
- Computing and visualizing matched-extent ascending and descending SAR geometric distortion grids (foreshortening, active/passive layover, radar shadow) alongside slope and aspect rasters.
- Generating multi-directional DEM hillshade composites to highlight micro-geomorphic scarps, grabens, lateral shear cracks, and toe bulging.
- Producing mean LOS velocity maps, 2D vertical/east-west decomposed velocity fields, and 2.5D/3D terrain-draped deformation maps.

## Execution Workflow

1. **Enforce CRS and Bounding Box Alignment:** Reproject all input rasters (DEM, ascending/descending LOS velocities, coherence) and vectors (faults, landslide boundaries, reference points) to a single metric projected CRS (e.g., local UTM zone) and clip to an identical bounding box (`X_MIN, X_MAX, Y_MIN, Y_MAX`).
2. **Compute SAR Geometric Distortion Masks:** From the DEM slope ($\alpha$) and aspect ($\psi$) and satellite orbit parameters (heading $\phi$, incidence angle $\theta$), compute range-facing slope angle $\beta_r = \arctan(\tan\alpha \cos(\psi - \psi_{\text{look}}))$ to classify normal visibility, foreshortening, layover, and shadow.
3. **Perform 2D Velocity Decomposition:** Mask out layover, shadow, and low-coherence ($\gamma < 0.3$) pixels before inverting ascending and descending LOS velocities into vertical ($V_{\text{up}}$) and east-west ($V_{\text{east}}$) components.
4. **Apply Zero-Centered Diverging Symbology:** Render all velocity rasters using a perceptually uniform diverging color ramp (`RdBu_r` or `vik`) strictly centered at `0.0 mm/yr` with explicit physical direction labels (`+` Toward/Uplift, `-` Away/Subsidence).
5. **Export 600 DPI Print Layouts:** Use `scripts/qgis_geohazard_pipeline.py` to generate multi-panel vector PDFs and 600 DPI PNGs.

## CLI Execution

Resolve `<skill-dir>` to the directory containing this SKILL.md (the skill's installed source path). Outputs go to the active experiment directory (e.g. `D:\InSAR形变\MudCreek_Experiment\` locally, `./outputs/` in cloud workspaces).

**Windows + QGIS LTR (this machine):** `QT_QPA_PLATFORM=windows` is required — the script's internal `offscreen` default leaves Qt with zero fonts (blank labels) and blank map exports on this desktop.

```powershell
$env:QT_QPA_PLATFORM="windows"; & "D:\Program\QGIS\bin\python-qgis-ltr.bat" "<skill-dir>\scripts\qgis_geohazard_pipeline.py" --work-dir "D:\InSAR形变\MudCreek_Experiment\qgis_outputs" --epsg 32610 --bbox 640050 642950 3968850 3971300 --demo
```

**Linux / Devin cloud (headless; needs `qgis`, `python3-qgis`, `xvfb`):**

```bash
QT_QPA_PLATFORM=offscreen xvfb-run -a python3 "<skill-dir>/scripts/qgis_geohazard_pipeline.py" --work-dir ./qgis_outputs --epsg 32610 --bbox 640050 642950 3968850 3971300 --demo
```

For real datasets, omit `--demo` and pass `--dem`, `--vel-asc`, and `--vel-desc` GeoTIFF paths.

## Gotchas

- **Unmasked layover/shadow pixels:** Never display raw LOS velocities over steep foreslopes without masking layover/shadow zones, as phase decorrelation and geometric folding produce extreme false spikes.
- **Asymmetric colorbars:** Never set diverging colormap limits to raw min/max (e.g., `[-145, +62]`); always enforce symmetric limits (`[-150, +150]`) so `0` stays neutral white.
- **Headless Qt crash in Linux sandboxes:** On Linux, always prefix `python3` calls with `QT_QPA_PLATFORM=offscreen xvfb-run -a` before `QgsApplication` initializes. On this Windows machine, run through `"D:\Program\QGIS\bin\python-qgis-ltr.bat"` so `qgis.core` and `osgeo.gdal` resolve correctly.
