#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Scientific & Cartographic Audit Script for InSAR Landslide Outputs
Audits:
  1. Raster CRS consistency, geotransform alignment, and valid-pixel masking ratio
  2. Exported figure resolution (DPI >= 300) and file integrity
  3. Outputs a structured JSON audit report
"""

import os
import json
import glob
import argparse
import numpy as np
from osgeo import gdal, osr
from PIL import Image


def audit_rasters(qgis_dir, expected_epsg):
    results = []
    tif_files = sorted(glob.glob(os.path.join(qgis_dir, "*.tif")))
    ref_gt = None

    for fp in tif_files:
        name = os.path.basename(fp)
        ds = gdal.Open(fp)
        if ds is None:
            results.append({"file": name, "status": "FAIL", "reason": "Unreadable GeoTIFF"})
            continue

        srs = osr.SpatialReference(wkt=ds.GetProjection())
        epsg = srs.GetAuthorityCode(None)
        gt = ds.GetGeoTransform()
        band = ds.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        arr = band.ReadAsArray().astype(np.float32)
        ds = None

        if ref_gt is None:
            ref_gt = gt

        gt_match = np.allclose(gt, ref_gt, atol=1e-3)
        epsg_match = (str(epsg) == str(expected_epsg))

        if nodata is not None:
            valid = arr[np.isfinite(arr) & (~np.isclose(arr, nodata))]
        else:
            valid = arr[np.isfinite(arr)]

        masked_pct = 100.0 * (1.0 - len(valid) / arr.size)
        vmin = float(np.min(valid)) if len(valid) > 0 else np.nan
        vmax = float(np.max(valid)) if len(valid) > 0 else np.nan

        issues = []
        if not epsg_match:
            issues.append(f"EPSG mismatch (got {epsg}, expected {expected_epsg})")
        if not gt_match:
            issues.append("Geotransform/BBox mismatch against reference raster")
        if "vel_" in name and masked_pct < 1.0:
            issues.append("Suspiciously low masked ratio (<1%); check layover/water mask")

        results.append({
            "file": name,
            "status": "PASS" if not issues else "WARN",
            "epsg": epsg,
            "masked_pct": round(masked_pct, 2),
            "min_val": round(vmin, 2),
            "max_val": round(vmax, 2),
            "issues": issues,
        })
    return results


def audit_figures(dirs, min_dpi=300):
    results = []
    png_files = []
    for d in dirs:
        if os.path.isdir(d):
            png_files.extend(sorted(glob.glob(os.path.join(d, "*.png"))))

    for fp in png_files:
        name = os.path.basename(fp)
        with Image.open(fp) as im:
            w, h = im.size
            dpi_info = im.info.get("dpi", (0, 0))
            dpi_x = round(float(dpi_info[0])) if dpi_info else 0

        issues = []
        if dpi_x < min_dpi:
            issues.append(f"DPI too low ({dpi_x} < {min_dpi})")
        if w < 1500:
            issues.append(f"Pixel width too small ({w}px < 1500px)")

        results.append({
            "file": name,
            "status": "PASS" if not issues else "FAIL",
            "size_px": f"{w}x{h}",
            "dpi": dpi_x,
            "issues": issues,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Landslide Quality Supervisor Audit Tool")
    parser.add_argument("--qgis-dir", default="./qgis_outputs")
    parser.add_argument("--python-dir", default="./python_outputs")
    parser.add_argument("--expected-epsg", type=int, default=32610)
    parser.add_argument("--report-out", default="./audit_report.json")
    args = parser.parse_args()

    raster_audit = audit_rasters(args.qgis_dir, args.expected_epsg)
    figure_audit = audit_figures([args.qgis_dir, args.python_dir], min_dpi=300)

    overall_pass = all(r["status"] == "PASS" for r in raster_audit) and all(f["status"] == "PASS" for f in figure_audit)
    report = {
        "overall_gate": "APPROVED" if overall_pass else "ACTION_REQUIRED",
        "raster_audit": raster_audit,
        "figure_audit": figure_audit,
    }

    with open(args.report_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"=== Landslide Quality Supervisor Gate: {report['overall_gate']} ===")
    for item in raster_audit + figure_audit:
        print(f"[{item['status']}] {item['file']} -> issues: {item['issues']}")


if __name__ == "__main__":
    main()
