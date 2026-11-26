---
name: landslide-quality-supervisor
description: Supervisor agent skill for auditing InSAR landslide figures, deformation time-series, and multi-source remote sensing workflows. Use after generating figures with insar-figure-python or geohazard-cartography-qgis, or when reviewing landslide deformation maps, LOS sign conventions, SAR geometric distortion masks, trigger-response plots, and international journal readiness.
---

# Landslide Quality Supervisor

Act as an independent scientific reviewer and quality gate between figure generation (`geohazard-cartography-qgis`, `insar-figure-python`) and final manuscript synthesis (`landslide-paper-architect`).

## When to Use

- Auditing generated GeoTIFF velocity rasters, SAR geometric distortion masks, and 600 DPI figure exports before drafting Results prose.
- Reviewing InSAR landslide figures for LOS sign ambiguity, unmasked layover/shadow zones, asymmetric diverging colormaps, or unquantified trigger-response claims.
- Verifying spatial CRS/extent alignment across multi-track maps and temporal synchronization across time-series plots.

## Five Mandatory Audit Gates

1. **LOS Sign & Colorbar Semantics:** Verify that positive (`+`) and negative (`-`) LOS directions are explicitly labeled in legends and captions, and that diverging colormaps are strictly centered on `0.0` with symmetric min/max limits.
2. **Visibility & Coherence Masking:** Confirm that SAR layover, radar shadow, water bodies, and low-coherence ($\gamma < 0.3$) pixels are masked as `NoData` or hatched so they cannot be misread as stable zero-velocity ground.
3. **Spatial & Temporal Alignment:** Check that multi-track rasters share identical EPSG codes, pixel resolutions, and bounding boxes, and that time-series and driver plots share aligned dates and failure markers.
4. **Atmospheric & Reference Point Plausibility:** Ensure the stable reference point (`P_ref`) lies outside the landslide boundary on comparable elevation bedrock to rule out stratified tropospheric delay artifacts.
5. **Journal Publication Readiness:** Run `scripts/audit_geotiff_and_figures.py` to programmatically verify raster metadata, masking ratios, and image DPI (>= 300 DPI required, 600 DPI recommended for line art/maps), and visually inspect exported PNGs.

## CLI Execution

Resolve `<skill-dir>` to the directory containing this SKILL.md. The audit needs `osgeo.gdal` + `PIL`, so on Windows run it through the QGIS-bundled Python; on Linux any `python3` with GDAL works.

**Windows + QGIS LTR (this machine):**

```powershell
& "D:\Program\QGIS\bin\python-qgis-ltr.bat" "<skill-dir>\scripts\audit_geotiff_and_figures.py" --qgis-dir "D:\InSAR形变\MudCreek_Experiment\qgis_outputs" --python-dir "D:\InSAR形变\MudCreek_Experiment\python_outputs" --expected-epsg 32610 --report-out "D:\InSAR形变\MudCreek_Experiment\audit_report.json"
```

**Linux / Devin cloud:**

```bash
python3 "<skill-dir>/scripts/audit_geotiff_and_figures.py" --qgis-dir ./qgis_outputs --python-dir ./python_outputs --expected-epsg 32610 --report-out ./audit_report.json
```

## Pre-Submission Automated Checks

`scripts/audit_geotiff_and_figures.py` additionally enforces the following before any figure set is declared final:

1. **Dual-format completeness:** every main manuscript figure must have both a 600 DPI `.png` and a non-empty vector `.pdf` — a lone `preview_*.png` fails the gate.
2. **Text hygiene:** zero occurrences of `placeholder`, `TODO`, or `NaN` across all PDF text objects, scanned with `pymupdf`/`fitz` (`pip install pymupdf`; the check reports SKIP when unavailable — do not treat SKIP as PASS for final submissions).
3. **CSV sync:** numeric statistics embedded in figure text (lag $\tau$, $r$, $p_{\text{eff}}$, $\mu \pm \sigma$) must match the authoritative `tables/*.csv` values; a displayed statistic absent from every CSV fails the gate.
4. **Research Highlights length:** every Elsevier Research Highlights bullet must be `<= 85` characters including spaces (checked whenever a highlights `.txt`/`.md` file is present in the audited directories).

## Gotchas

- **Approving figures with unmasked foreslopes:** Never clear ascending or descending maps over steep terrain (>35 deg) unless geometric distortion masks have been explicitly applied and inspected.
- **Accepting visual rainfall-displacement correlation without lag metrics:** Reject trigger-response plots that lack explicit lag windows ($\Delta t$), statistical correlation ($r$), or threshold annotations.
