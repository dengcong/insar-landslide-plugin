#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQGIS Geohazard Cartography & SAR Visibility Pipeline
Supports:
  1. Multi-directional DEM hillshade generation (315 deg + 45 deg azimuth blend)
  2. Ascending & Descending SAR geometric distortion classification (Foreshortening, Layover, Shadow)
  3. Slope & Aspect grid generation
  4. Masked 2D velocity decomposition (V_up, V_east)
  5. 600 DPI multi-panel QGIS Print Layout export (PDF & PNG)
"""

import os
import sys
import argparse
import numpy as np
from osgeo import gdal, osr

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import (
    QgsApplication, QgsProject, QgsRasterLayer, QgsPalettedRasterRenderer,
    QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer,
    QgsPrintLayout, QgsLayoutItemMap, QgsLayoutItemLabel, QgsLayoutPoint,
    QgsLayoutSize, QgsUnitTypes, QgsLayoutExporter, QgsRectangle,
    QgsCoordinateReferenceSystem, QgsLayoutItemScaleBar, QgsLayoutItemShape
)
from qgis.PyQt.QtGui import QColor, QFont



# --- Layout Metadata Hygiene (see SKILL.md) -----------------------------------
# Development artifacts must never reach an exported layout label or
# attribution bar. Word-boundary matching avoids false positives inside normal
# words (e.g. "latest", "protest").
import re as _re

FORBIDDEN_LAYOUT_STRINGS = ("placeholder", "todo", "test")
_FORBIDDEN_RE = _re.compile(r"\b(" + "|".join(FORBIDDEN_LAYOUT_STRINGS) + r")\b", _re.IGNORECASE)


def validate_layout_text(text):
    """Raise ValueError if a layout label carries development artifacts."""
    hits = _FORBIDDEN_RE.findall(text or "")
    if hits:
        raise ValueError(f"Layout label contains forbidden development string(s) {sorted(set(h.lower() for h in hits))}: {text!r}")


def hillshade_source_label(lidar_available, resampled=False):
    """Explicit attribution string for hillshade panels.

    Never imply LiDAR when 1 m LiDAR is unavailable — label the actual source.
    """
    if lidar_available:
        return "1 m LiDAR hillshade (NRCan HRDEM)"
    return "Hillshade: GLO-30 resampled" if resampled else "Hillshade: Copernicus GLO-30 (30 m)"


def write_geotiff(filepath, array, x_min, y_max, res, epsg=32610, nodata=-9999.0):
    rows, cols = array.shape
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(filepath, cols, rows, 1, gdal.GDT_Float32, ["COMPRESS=LZW"])
    ds.SetGeoTransform((x_min, res, 0.0, y_max, 0.0, -res))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    ds.SetProjection(srs.ExportToWkt())
    band = ds.GetRasterBand(1)
    band.SetNoDataValue(nodata)
    band.WriteArray(array.astype(np.float32))
    band.FlushCache()
    ds = None


def read_geotiff(filepath):
    ds = gdal.Open(filepath)
    if ds is None:
        raise FileNotFoundError(f"Cannot open GeoTIFF: {filepath}")
    gt = ds.GetGeoTransform()
    arr = ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
    nodata = ds.GetRasterBand(1).GetNoDataValue()
    ds = None
    return arr, gt, nodata


def generate_demo_rasters(work_dir, bbox, res, epsg, asc_h, asc_i, desc_h, desc_i):
    x_min, x_max, y_min, y_max = bbox
    cols = int(round((x_max - x_min) / res))
    rows = int(round((y_max - y_min) / res))
    x = np.linspace(x_min + res / 2, x_max - res / 2, cols)
    y = np.linspace(y_max - res / 2, y_min + res / 2, rows)
    xx, yy = np.meshgrid(x, y)

    cx, cy = (x_min + x_max) / 2.0, (y_min + y_max) / 2.0
    u_sw = (xx - cx) * np.sin(np.deg2rad(235.0)) + (yy - cy) * np.cos(np.deg2rad(235.0))
    v_nw = -(xx - cx) * np.cos(np.deg2rad(235.0)) + (yy - cy) * np.sin(np.deg2rad(235.0))

    dist_from_coast = 420.0 - u_sw
    dem = np.where(dist_from_coast < 0, 0.0, dist_from_coast * np.tan(np.deg2rad(39.0)))
    dem += 18.0 * np.sin(v_nw / 160.0) * np.clip(dist_from_coast / 400.0, 0, 1)
    dem += 12.0 * np.exp(-((dist_from_coast - 320.0) ** 2) / (2 * 45.0 ** 2))
    dem = np.maximum(dem, 0.0)

    ls_mask = ((dist_from_coast - 240.0) / 210.0) ** 2 + (v_nw / 260.0) ** 2 <= 1.0
    core = np.exp(-(((dist_from_coast - 230.0) / 145.0) ** 2 + (v_nw / 185.0) ** 2))
    v_slope = np.where(ls_mask, 165.0 * core, 0.0)

    slope_rad = np.deg2rad(38.0)
    v_horiz = v_slope * np.cos(slope_rad)
    v_up_true = -v_slope * np.sin(slope_rad)
    v_east_true = v_horiz * np.sin(np.deg2rad(235.0))
    v_north_true = v_horiz * np.cos(np.deg2rad(235.0))

    dem_path = os.path.join(work_dir, "dem_utm.tif")
    asc_path = os.path.join(work_dir, "vel_los_asc.tif")
    desc_path = os.path.join(work_dir, "vel_los_desc.tif")

    rng = np.random.default_rng(42)
    for h_deg, i_deg, out_p in [(asc_h, asc_i, asc_path), (desc_h, desc_i, desc_path)]:
        hr, ir = np.deg2rad(h_deg), np.deg2rad(i_deg)
        v_los = (
            v_east_true * (-np.sin(ir) * np.cos(hr))
            + v_north_true * (np.sin(ir) * np.sin(hr))
            + v_up_true * np.cos(ir)
            + rng.normal(0.0, 3.0, size=dem.shape)
        )
        v_los = np.where(dem <= 0.5, -9999.0, v_los)
        write_geotiff(out_p, v_los, x_min, y_max, res, epsg=epsg)

    write_geotiff(dem_path, dem, x_min, y_max, res, epsg=epsg)
    return dem_path, asc_path, desc_path


def compute_terrain_and_sar_products(work_dir, dem_path, asc_path, desc_path, epsg, asc_h, asc_i, desc_h, desc_i):
    dem, gt, _ = read_geotiff(dem_path)
    x_min, res, _, y_max, _, _ = gt
    res = abs(res)

    dz_dy, dz_dx = np.gradient(dem, res, res)
    dz_dy = -dz_dy
    slope_rad = np.arctan(np.hypot(dz_dx, dz_dy))
    aspect_rad = np.arctan2(-dz_dx, -dz_dy) % (2 * np.pi)

    slope_deg = np.rad2deg(slope_rad)
    aspect_deg = np.rad2deg(aspect_rad)
    write_geotiff(os.path.join(work_dir, "terrain_slope_deg.tif"), slope_deg, x_min, y_max, res, epsg=epsg)
    write_geotiff(os.path.join(work_dir, "terrain_aspect_deg.tif"), aspect_deg, x_min, y_max, res, epsg=epsg)

    def calc_hillshade(az_deg, alt_deg=35.0):
        az = np.deg2rad(az_deg)
        zen = np.deg2rad(90.0 - alt_deg)
        hs = np.cos(zen) * np.cos(slope_rad) + np.sin(zen) * np.sin(slope_rad) * np.cos(az - aspect_rad)
        return np.clip(hs * 255.0, 0, 255)

    hs_multi = 0.65 * calc_hillshade(315.0, 35.0) + 0.35 * calc_hillshade(45.0, 35.0)
    hs_path = os.path.join(work_dir, "multidir_hillshade.tif")
    write_geotiff(hs_path, hs_multi, x_min, y_max, res, epsg=epsg)

    dist_paths = {}
    invalid_masks = {}
    for tag, h_deg, i_deg in [("asc", asc_h, asc_i), ("desc", desc_h, desc_i)]:
        look_az = np.deg2rad((h_deg + 90.0) % 360.0)
        inc_rad = np.deg2rad(i_deg)
        beta_r = np.arctan(np.tan(slope_rad) * np.cos(aspect_rad - look_az))

        cls = np.ones_like(dem, dtype=np.float32)
        cls = np.where((beta_r < 0) & (np.abs(beta_r) < inc_rad), 2, cls)
        cls = np.where((beta_r < 0) & (np.abs(beta_r) >= inc_rad), 3, cls)
        cls = np.where((beta_r > 0) & (beta_r >= (np.pi / 2.0 - inc_rad)), 4, cls)
        cls = np.where(dem <= 0.5, 0, cls)

        out_p = os.path.join(work_dir, f"sar_distortion_{tag}.tif")
        write_geotiff(out_p, cls, x_min, y_max, res, epsg=epsg, nodata=0)
        dist_paths[tag] = out_p
        invalid_masks[tag] = (cls == 3) | (cls == 4) | (cls == 0)

    v_asc, _, _ = read_geotiff(asc_path)
    v_desc, _, _ = read_geotiff(desc_path)
    valid = (v_asc > -9000) & (v_desc > -9000) & (~invalid_masks["asc"]) & (~invalid_masks["desc"])

    ha, ia = np.deg2rad(asc_h), np.deg2rad(asc_i)
    hd, id_ = np.deg2rad(desc_h), np.deg2rad(desc_i)
    design = np.array([
        [-np.sin(ia) * np.cos(ha), np.cos(ia)],
        [-np.sin(id_) * np.cos(hd), np.cos(id_)]
    ])
    design_inv = np.linalg.inv(design)

    v_east = np.full_like(v_asc, -9999.0)
    v_up = np.full_like(v_asc, -9999.0)
    sol = design_inv @ np.vstack([v_asc[valid], v_desc[valid]])
    v_east[valid] = sol[0]
    v_up[valid] = sol[1]

    v_east_path = os.path.join(work_dir, "vel_2d_east.tif")
    v_up_path = os.path.join(work_dir, "vel_2d_up.tif")
    write_geotiff(v_east_path, v_east, x_min, y_max, res, epsg=epsg)
    write_geotiff(v_up_path, v_up, x_min, y_max, res, epsg=epsg)

    return dist_paths, hs_path, v_east_path, v_up_path


def apply_diverging_style(layer, vlim=120.0):
    shader = QgsRasterShader()
    ramp = QgsColorRampShader()
    ramp.setColorRampType(QgsColorRampShader.Interpolated)
    ramp.setColorRampItemList([
        QgsColorRampShader.ColorRampItem(-vlim, QColor("#2166AC"), f"-{vlim:.0f} mm/yr"),
        QgsColorRampShader.ColorRampItem(-vlim / 2, QColor("#67A9CF"), f"-{vlim/2:.0f}"),
        QgsColorRampShader.ColorRampItem(0.0, QColor("#F7F7F7"), "0 mm/yr"),
        QgsColorRampShader.ColorRampItem(vlim / 2, QColor("#EF8A62"), f"+{vlim/2:.0f}"),
        QgsColorRampShader.ColorRampItem(vlim, QColor("#B2182B"), f"+{vlim:.0f} mm/yr"),
    ])
    shader.setRasterShaderFunction(ramp)
    layer.setRenderer(QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader))
    layer.triggerRepaint()


def apply_distortion_style(layer):
    classes = [
        QgsPalettedRasterRenderer.Class(1, QColor("#E8ECEF"), "Normal Visibility"),
        QgsPalettedRasterRenderer.Class(2, QColor("#FDB863"), "Foreshortening"),
        QgsPalettedRasterRenderer.Class(3, QColor("#C51B7D"), "Layover (Masked)"),
        QgsPalettedRasterRenderer.Class(4, QColor("#252525"), "Shadow (Masked)"),
    ]
    layer.setRenderer(QgsPalettedRasterRenderer(layer.dataProvider(), 1, classes))
    layer.triggerRepaint()


def export_four_panel_layout(project, panels, extent_rect, out_pdf, out_png, dpi=600):
    manager = project.layoutManager()
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName("Geohazard_4Panel_Layout")
    layout.pageCollection().page(0).setPageSize(
        QgsLayoutSize(297, 258, QgsUnitTypes.LayoutMillimeters)
    )
    manager.addLayout(layout)

    coords = [(12, 15), (152, 15), (12, 110), (152, 110)]
    map_items = []
    for (title, lyr), (xm, ym) in zip(panels, coords):
        m = QgsLayoutItemMap(layout)
        m.setRect(20, 20, 20, 20)
        m.setLayers([lyr])
        m.setExtent(extent_rect)
        m.attemptMove(QgsLayoutPoint(xm, ym, QgsUnitTypes.LayoutMillimeters))
        m.attemptResize(QgsLayoutSize(130, 82, QgsUnitTypes.LayoutMillimeters))
        m.setFrameEnabled(True)
        layout.addLayoutItem(m)
        map_items.append(m)

        lbl = QgsLayoutItemLabel(layout)
        lbl.setText(title)
        lbl.setFont(QFont("Arial", 9, QFont.Bold))
        lbl.attemptMove(QgsLayoutPoint(xm, ym - 6, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(lbl)

    ramp_stops = [
        (0.00, QColor("#2166AC")),
        (0.25, QColor("#67A9CF")),
        (0.50, QColor("#F7F7F7")),
        (0.75, QColor("#EF8A62")),
        (1.00, QColor("#B2182B")),
    ]

    def ramp_color(t):
        for (p1, c1), (p2, c2) in zip(ramp_stops, ramp_stops[1:]):
            if t <= p2:
                f = (t - p1) / (p2 - p1)
                return QColor(
                    round(c1.red() + (c2.red() - c1.red()) * f),
                    round(c1.green() + (c2.green() - c1.green()) * f),
                    round(c1.blue() + (c2.blue() - c1.blue()) * f),
                )
        return ramp_stops[-1][1]

    title_lbl = QgsLayoutItemLabel(layout)
    title_lbl.setText("Mean LOS / Decomposed Velocity (mm/yr)   [- Away | + Toward]")
    title_lbl.setFont(QFont("Arial", 9, QFont.Bold))
    title_lbl.attemptMove(QgsLayoutPoint(12, 199, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(title_lbl)

    bar_x, bar_y, bar_w, bar_h, n_seg = 12.0, 206.0, 55.0, 5.5, 80
    seg_w = bar_w / n_seg
    for i in range(n_seg):
        sh = QgsLayoutItemShape(layout)
        sh.setShapeType(QgsLayoutItemShape.Rectangle)
        sh.attemptMove(QgsLayoutPoint(bar_x + i * seg_w, bar_y, QgsUnitTypes.LayoutMillimeters))
        sh.attemptResize(QgsLayoutSize(seg_w + 0.08, bar_h, QgsUnitTypes.LayoutMillimeters))
        c = ramp_color((i + 0.5) / n_seg)
        sh.symbol().setColor(c)
        sh.symbol().symbolLayer(0).setStrokeColor(c)
        layout.addLayoutItem(sh)

    tick_lbls = [
        (bar_x, "-120 (Away)"),
        (bar_x + bar_w / 2.0 - 1.5, "0"),
        (bar_x + bar_w - 16.0, "+120 (Toward)"),
    ]
    for tx, tt in tick_lbls:
        tl = QgsLayoutItemLabel(layout)
        tl.setText(tt)
        tl.setFont(QFont("Arial", 8))
        tl.attemptMove(QgsLayoutPoint(tx, 213, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(tl)

    scalebar = QgsLayoutItemScaleBar(layout)
    scalebar.setStyle("Single Box")
    scalebar.setLinkedMap(map_items[0])
    scalebar.setUnits(QgsUnitTypes.DistanceMeters)
    scalebar.setNumberOfSegments(2)
    scalebar.setNumberOfSegmentsLeft(0)
    scalebar.setUnitsPerSegment(500)
    scalebar.setUnitLabel("m")
    scalebar.update()
    scalebar.attemptMove(QgsLayoutPoint(232, 200, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(scalebar)

    for item in layout.items():
        if isinstance(item, QgsLayoutItemLabel):
            validate_layout_text(item.text())

    exporter = QgsLayoutExporter(layout)
    pdf_cfg = QgsLayoutExporter.PdfExportSettings()
    pdf_cfg.dpi = dpi
    exporter.exportToPdf(out_pdf, pdf_cfg)

    img_cfg = QgsLayoutExporter.ImageExportSettings()
    img_cfg.dpi = dpi
    exporter.exportToImage(out_png, img_cfg)


def main():
    parser = argparse.ArgumentParser(description="PyQGIS Geohazard Cartography Pipeline")
    parser.add_argument("--work-dir", default="./qgis_outputs")
    parser.add_argument("--epsg", type=int, default=32610)
    parser.add_argument("--bbox", nargs=4, type=float, default=[640050.0, 642950.0, 3968850.0, 3971300.0])
    parser.add_argument("--res", type=float, default=10.0)
    parser.add_argument("--vlim", type=float, default=120.0)
    parser.add_argument("--asc-heading", type=float, default=348.0)
    parser.add_argument("--asc-inc", type=float, default=37.5)
    parser.add_argument("--desc-heading", type=float, default=192.0)
    parser.add_argument("--desc-inc", type=float, default=39.0)
    parser.add_argument("--dem", default=None)
    parser.add_argument("--vel-asc", default=None)
    parser.add_argument("--vel-desc", default=None)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.work_dir, exist_ok=True)
    if args.demo or not (args.dem and args.vel_asc and args.vel_desc):
        dem_p, asc_p, desc_p = generate_demo_rasters(
            args.work_dir, args.bbox, args.res, args.epsg,
            args.asc_heading, args.asc_inc, args.desc_heading, args.desc_inc
        )
    else:
        dem_p, asc_p, desc_p = args.dem, args.vel_asc, args.vel_desc

    dist_paths, _, v_east_p, v_up_p = compute_terrain_and_sar_products(
        args.work_dir, dem_p, asc_p, desc_p, args.epsg,
        args.asc_heading, args.asc_inc, args.desc_heading, args.desc_inc
    )

    qgs = QgsApplication([], False)
    qgs.initQgis()
    try:
        proj = QgsProject.instance()
        proj.setCrs(QgsCoordinateReferenceSystem(f"EPSG:{args.epsg}"))

        lyr_asc = QgsRasterLayer(asc_p, "Asc_LOS")
        lyr_desc = QgsRasterLayer(desc_p, "Desc_LOS")
        lyr_up = QgsRasterLayer(v_up_p, "Vel_2D_Up")
        lyr_east = QgsRasterLayer(v_east_p, "Vel_2D_East")
        for lyr in [lyr_asc, lyr_desc, lyr_up, lyr_east]:
            apply_diverging_style(lyr, vlim=args.vlim)
            proj.addMapLayer(lyr)

        lyr_da = QgsRasterLayer(dist_paths["asc"], "Distortion_Asc")
        lyr_dd = QgsRasterLayer(dist_paths["desc"], "Distortion_Desc")
        apply_distortion_style(lyr_da)
        apply_distortion_style(lyr_dd)
        proj.addMapLayer(lyr_da)
        proj.addMapLayer(lyr_dd)

        rect = QgsRectangle(args.bbox[0], args.bbox[2], args.bbox[1], args.bbox[3])
        export_four_panel_layout(
            proj,
            [
                ("(a) Ascending Mean LOS Velocity", lyr_asc),
                ("(b) Descending Mean LOS Velocity", lyr_desc),
                ("(c) Decomposed Vertical Velocity (V_up)", lyr_up),
                ("(d) Decomposed East-West Velocity (V_east)", lyr_east),
            ],
            rect,
            os.path.join(args.work_dir, "Fig3_Kinematics_600DPI.pdf"),
            os.path.join(args.work_dir, "Fig3_Kinematics_600DPI.png"),
            dpi=600,
        )
    finally:
        qgs.exitQgis()


if __name__ == "__main__":
    main()
