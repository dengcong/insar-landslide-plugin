---
name: insar-figure-python
description: Executor skill for generating publication-grade InSAR and landslide deformation figures in Python. Use when creating multi-source data acquisition timelines, displacement time-series plots with semantic trigger background shading, dual-axis driver response plots, 3x3 spatio-temporal cumulative deformation matrices, or SAR side-looking geometric distortion schematics.
---

# InSAR Figure Python

Generate publication-ready quantitative, temporal, and mechanistic figures in Python (`matplotlib`, `scipy`, `pandas`, `numpy`) for InSAR landslide studies.

## When to Use

- Plotting multi-source SAR acquisition timelines alongside auxiliary datasets (LiDAR, UAV, GNSS) and daily meteorological/hydrological records.
- Drawing SAR side-looking geometric distortion schematics illustrating foreslope foreshortening/layover vs. backslope visibility and LOS displacement projection vectors.
- Rendering 3x3 spatio-temporal cumulative deformation matrices across key monitoring epochs using a unified zero-centered diverging color scale.
- Creating kinematic sub-zone displacement time-series with semantic trigger background shading and dual-axis driver-response lag correlation plots.

## Execution Workflow

1. **Standardize Publication Typography:** Configure sans-serif fonts (`Arial` / `Helvetica` / `DejaVu Sans`, 8-10 pt), thin axis spines (`0.8 pt`), colorblind-safe palettes, and dual export (`600 DPI PNG` + vector `PDF`).
2. **Synchronize Temporal & Color Scales:** Ensure all time-series panels share identical start/end timestamps and failure markers; enforce `TwoSlopeNorm(vmin=-V, vcenter=0.0, vmax=+V)` across all 9 panels of the 3x3 cumulative deformation matrix.
3. **Quantify Driver-Response Lag:** Compute normalized cross-correlation between displacement velocity/acceleration and antecedent cumulative rainfall or reservoir drawdown rate; annotate optimal lag window ($\Delta t$ days), correlation coefficient ($r$), and critical triggering threshold directly on the dual-axis plot.
4. **Execute Script:** Run `scripts/insar_publication_plots.py` to produce the full figure set.

## CLI Execution

Resolve `<skill-dir>` to the directory containing this SKILL.md. Requires `matplotlib`, `scipy`, `pandas`, `numpy`, `PIL` (`pip install matplotlib scipy pandas pillow`).

**Windows (this machine — use Anaconda `python`; `python3` resolves to a Store stub):**

```powershell
python "<skill-dir>\scripts\insar_publication_plots.py" --out-dir "D:\InSAR形变\MudCreek_Experiment\python_outputs" --failure-date 2017-05-20 --demo
```

**Linux / Devin cloud:**

```bash
python3 "<skill-dir>/scripts/insar_publication_plots.py" --out-dir ./python_outputs --failure-date 2017-05-20 --demo
```

## Gotchas

- **Inconsistent colorbars across 3x3 epochs:** Never auto-scale each epoch subplot independently; auto-scaling hides progressive acceleration and exaggerates early-stage noise.
- **Unquantified dual-axis overlays:** Always annotate the exact lag duration ($\Delta t$) and correlation metric rather than relying on visual overlap between rainfall bars and displacement curves.
