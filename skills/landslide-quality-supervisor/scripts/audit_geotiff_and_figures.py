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


def audit_figures(dirs, min_dpi=600):
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
        pdf_sibling = os.path.splitext(fp)[0] + ".pdf"
        if not (os.path.isfile(pdf_sibling) and os.path.getsize(pdf_sibling) >= 2000):
            issues.append("Missing/empty vector PDF sibling (dual-format export required)")
        if name.startswith("preview_"):
            issues.append("preview_*.png is a draft artifact; final figures must use canonical manuscript names")

        results.append({
            "file": name,
            "status": "PASS" if not issues else "FAIL",
            "size_px": f"{w}x{h}",
            "dpi": dpi_x,
            "issues": issues,
        })
    return results


# --- Pre-submission automated checks (see SKILL.md) ----------------------------

def _pdf_texts(dirs):
    """Yield (pdf_path, full_text) for every PDF under dirs using pymupdf.
    Returns None if pymupdf is unavailable."""
    try:
        import fitz  # pymupdf
    except ImportError:
        return None
    out = []
    pdfs = []
    for d in dirs:
        if os.path.isdir(d):
            pdfs.extend(sorted(glob.glob(os.path.join(d, "*.pdf"))))
    for fp in pdfs:
        try:
            doc = fitz.open(fp)
            out.append((fp, "\n".join(page.get_text() for page in doc)))
            doc.close()
        except Exception as exc:  # corrupt pdf -> fail loudly
            out.append((fp, f"__UNREADABLE__:{exc}"))
    return out


def audit_pdf_text(dirs):
    """Zero-tolerance scan for development artifacts (placeholder/TODO/NaN) in
    PDF text objects. Status SKIP when pymupdf is not installed."""
    import re
    texts = _pdf_texts(dirs)
    if texts is None:
        return [{"file": "*.pdf", "status": "SKIP",
                 "issues": ["pymupdf not installed; pip install pymupdf to enable PDF text hygiene scan"]}]
    pat = re.compile(r"\b(placeholder|todo|nan)\b", re.IGNORECASE)
    results = []
    for fp, txt in texts:
        name = os.path.basename(fp)
        if txt.startswith("__UNREADABLE__"):
            results.append({"file": name, "status": "FAIL", "issues": [f"Unreadable PDF: {txt[14:]}"]})
            continue
        hits = sorted(set(h.lower() for h in pat.findall(txt)))
        results.append({"file": name, "status": "FAIL" if hits else "PASS",
                        "issues": [f"Forbidden token(s) in PDF text: {hits}"] if hits else []})
    return results


def audit_csv_sync(dirs, tables_dir):
    """Statistics displayed in figure PDFs (tau_lag, r, p_eff, mu+/-sigma, ...)
    must appear in the authoritative tables/*.csv. Extracts numeric literals
    following stat-like keys in PDF text and checks membership (rel. tol 2%)
    across every numeric cell of the CSVs in tables_dir."""
    import re
    texts = _pdf_texts(dirs)
    if texts is None:
        return [{"file": "*.pdf", "status": "SKIP", "issues": ["pymupdf not installed"]}]
    if not tables_dir or not os.path.isdir(tables_dir):
        return [{"file": "*.pdf", "status": "SKIP", "issues": ["no --tables-dir provided or directory missing"]}]
    ref_values = []
    for csv in sorted(glob.glob(os.path.join(tables_dir, "*.csv"))):
        try:
            for tok in open(csv, encoding="utf-8", errors="ignore").read().replace(",", " ").split():
                try:
                    ref_values.append(float(tok))
                except ValueError:
                    pass
        except OSError:
            pass
    if not ref_values:
        return [{"file": "*.pdf", "status": "SKIP", "issues": ["no numeric values found in tables/*.csv"]}]
    key_re = re.compile(r"(?<![A-Za-z])(?:tau(?:_lag)?|lag|p_?eff|peff|mu|sigma|r)\s*[=±]\s*(-?\d+\.?\d*)", re.IGNORECASE)
    results = []
    for fp, txt in texts:
        name = os.path.basename(fp)
        missing = []
        for m in key_re.finditer(txt):
            v = float(m.group(1))
            if v == 0.0:
                continue
            if not any(abs(v - rv) <= 0.02 * max(abs(v), abs(rv), 1e-9) or abs(v - rv) < 0.02 for rv in ref_values):
                missing.append(v)
        results.append({"file": name, "status": "FAIL" if missing else "PASS",
                        "issues": [f"PDF statistics absent from tables/*.csv: {missing[:6]}"] if missing else []})
    return results


def audit_highlights(dirs, max_chars=85):
    """Elsevier Research Highlights bullets must be <= 85 characters incl. spaces.
    Scans any *highlight* .txt/.md file found in dirs."""
    results = []
    files = []
    for d in dirs:
        if os.path.isdir(d):
            for ext in ("txt", "md"):
                files.extend(sorted(glob.glob(os.path.join(d, f"*highlight*.{ext}"))))
    if not files:
        return [{"file": "*highlight*", "status": "SKIP", "issues": ["no highlights file found"]}]
    for fp in files:
        bad = []
        for i, line in enumerate(open(fp, encoding="utf-8", errors="ignore"), 1):
            t = line.strip().lstrip("-*• ").rstrip()
            if t and len(t) > max_chars:
                bad.append((i, len(t)))
        results.append({"file": os.path.basename(fp), "status": "FAIL" if bad else "PASS",
                        "issues": [f"lines exceeding {max_chars} chars (line, len): {bad}"] if bad else []})
    return results


def main():
    parser = argparse.ArgumentParser(description="Landslide Quality Supervisor Audit Tool")
    parser.add_argument("--qgis-dir", default="./qgis_outputs")
    parser.add_argument("--python-dir", default="./python_outputs")
    parser.add_argument("--expected-epsg", type=int, default=32610)
    parser.add_argument("--tables-dir", default="./tables")
    parser.add_argument("--report-out", default="./audit_report.json")
    args = parser.parse_args()

    scan_dirs = [args.qgis_dir, args.python_dir]
    raster_audit = audit_rasters(args.qgis_dir, args.expected_epsg)
    figure_audit = audit_figures(scan_dirs, min_dpi=600)
    pdf_text_audit = audit_pdf_text(scan_dirs)
    csv_sync_audit = audit_csv_sync(scan_dirs, args.tables_dir)
    highlights_audit = audit_highlights(scan_dirs)

    def failed(items):
        return any(r["status"] == "FAIL" for r in items)

    overall_pass = not any(failed(x) for x in (raster_audit, figure_audit, pdf_text_audit, csv_sync_audit, highlights_audit))
    report = {
        "overall_gate": "APPROVED" if overall_pass else "ACTION_REQUIRED",
        "raster_audit": raster_audit,
        "figure_audit": figure_audit,
        "pdf_text_audit": pdf_text_audit,
        "csv_sync_audit": csv_sync_audit,
        "highlights_audit": highlights_audit,
    }

    with open(args.report_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"=== Landslide Quality Supervisor Gate: {report['overall_gate']} ===")
    for item in raster_audit + figure_audit + pdf_text_audit + csv_sync_audit + highlights_audit:
        print(f"[{item['status']}] {item['file']} -> issues: {item['issues']}")


if __name__ == "__main__":
    main()
