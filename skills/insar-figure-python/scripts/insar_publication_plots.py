#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publication-Grade InSAR & Landslide Quantitative Plotting Suite
Generates:
  1. Fig2a_Acquisition_Timeline.png/.pdf (Multi-source SAR & hydrological timeline)
  2. Fig2b_SAR_Geometry_Schematic.png/.pdf (Side-looking SAR geometric distortion schematic)
  3. Fig5_Spatiotemporal_3x3_Matrix.png/.pdf (3x3 cumulative displacement matrix)
  4. Fig6_Kinematics_Driver_Lag.png/.pdf (Zone displacement time-series & dual-axis lag plot)
"""

import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Polygon
from scipy.signal import correlate, correlation_lags

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8.5,
    "axes.titlesize": 9.5,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 8.0,
    "ytick.labelsize": 8.0,
    "legend.fontsize": 7.5,
    "axes.linewidth": 0.8,
    "savefig.dpi": 600,
})


def build_demo_dataset(start_str="2015-03-01", fail_str="2017-05-20"):
    start_dt = pd.Timestamp(start_str)
    fail_dt = pd.Timestamp(fail_str)
    dates_daily = pd.date_range(start_dt, fail_dt, freq="D")
    n_days = len(dates_daily)
    rng = np.random.default_rng(20170520)

    rain = np.zeros(n_days)
    for i, d in enumerate(dates_daily):
        if d.month in [12, 1, 2, 3] and d.year in [2015, 2016]:
            if rng.random() < 0.14:
                rain[i] = rng.gamma(1.5, 9.0)
        if pd.Timestamp("2017-01-03") <= d <= pd.Timestamp("2017-02-24"):
            if rng.random() < 0.48:
                rain[i] = rng.gamma(2.2, 24.0)
        elif pd.Timestamp("2017-03-15") <= d <= pd.Timestamp("2017-04-20"):
            if rng.random() < 0.32:
                rain[i] = rng.gamma(1.8, 16.0)

    rain[dates_daily == pd.Timestamp("2017-01-09")] = 118.0
    rain[dates_daily == pd.Timestamp("2017-01-10")] = 84.0
    rain[dates_daily == pd.Timestamp("2017-02-17")] = 132.0
    rain[dates_daily == pd.Timestamp("2017-02-18")] = 76.0

    df_rain = pd.DataFrame({"date": dates_daily, "rain_mm": rain})
    df_rain["rain_30d"] = df_rain["rain_mm"].rolling(30, min_periods=1).sum()

    s1b_start = pd.Timestamp("2016-10-05")
    asc_dates = list(pd.date_range("2015-03-15", "2016-10-01", freq="12D")) + \
                list(pd.date_range("2016-10-07", "2017-05-17", freq="6D"))
    desc_dates = list(pd.date_range("2015-03-21", "2016-10-03", freq="12D")) + \
                 list(pd.date_range("2016-10-09", "2017-05-19", freq="6D"))

    lag_days = 16
    antecedent = df_rain["rain_30d"].shift(lag_days).fillna(0.0).values
    excess = np.maximum(0.0, antecedent - 140.0)
    days_to_fail = np.maximum(1.0, (fail_dt - dates_daily).days.values)
    surge = np.where(dates_daily >= pd.Timestamp("2017-04-01"), 18.0 / (days_to_fail ** 0.65), 0.0)

    v1 = 0.09 + 0.0042 * excess + 1.15 * surge
    v2 = 0.07 + 0.0034 * excess + 0.95 * surge
    v3 = 0.04 + 0.0021 * excess + 0.65 * surge

    df_ts = pd.DataFrame({
        "date": dates_daily,
        "disp_z1": np.cumsum(v1) - v1[0],
        "disp_z2": np.cumsum(v2) - v2[0],
        "disp_z3": np.cumsum(v3) - v3[0],
        "disp_ref": rng.normal(0.0, 2.5, size=n_days),
        "vel_z1": v1,
        "rain_mm": df_rain["rain_mm"].values,
        "rain_30d": df_rain["rain_30d"].values,
    })
    return df_ts, asc_dates, desc_dates, s1b_start, start_dt, fail_dt


def plot_acquisition_timeline(out_dir, df_ts, asc_dates, desc_dates, s1b_start, start_dt, fail_dt):
    fig, ax1 = plt.subplots(figsize=(7.5, 2.8))
    ax1.axvspan(start_dt, pd.Timestamp("2016-12-31"), color="#F2F2F2", alpha=0.8, label="Drought Creep Phase")
    ax1.axvspan(pd.Timestamp("2017-01-01"), fail_dt, color="#DCEEFB", alpha=0.75, label="Extreme Rainfall Acceleration")

    ax1.scatter(asc_dates, np.full(len(asc_dates), 2.2), s=18, color="#D95F02", marker="o", label=f"Asc T35 (n={len(asc_dates)})", zorder=4)
    ax1.scatter(desc_dates, np.full(len(desc_dates), 1.4), s=18, color="#1B9E77", marker="s", label=f"Desc T42 (n={len(desc_dates)})", zorder=4)
    ax1.scatter([pd.Timestamp("2016-06-15")], [0.6], s=55, color="#7570B3", marker="^", label="USGS 3DEP LiDAR", zorder=5)

    ax1.axvline(s1b_start, color="#555555", linestyle=":", lw=1.0)
    ax1.text(s1b_start + pd.Timedelta(days=15), 1.08, " Sentinel-1B\n (12d -> 6d)", fontsize=7.5, va="top")
    ax1.axvline(fail_dt, color="#B2182B", linestyle="--", lw=1.2)
    ax1.text(fail_dt, 2.55, f"Failure\n{fail_dt.strftime('%Y-%m-%d')} ", fontsize=7.5, color="#B2182B", fontweight="bold", ha="right", va="top")

    ax1.set_yticks([0.6, 1.4, 2.2])
    ax1.set_yticklabels(["LiDAR DEM", "Desc T42", "Asc T35"])
    ax1.set_ylim(0.1, 2.8)
    ax1.set_ylabel("Sensor / Track")

    ax2 = ax1.twinx()
    ax2.bar(df_ts["date"], df_ts["rain_mm"], width=1.5, color="#3182BD", alpha=0.45, label="Daily Rainfall")
    ax2.set_ylabel("Daily Rainfall (mm/d)", color="#2166AC")
    ax2.set_ylim(0, 160)

    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.set_xlim(start_dt, fail_dt + pd.Timedelta(days=15))

    l1, lb1 = ax1.get_legend_handles_labels()
    l2, lb2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, lb1 + lb2, loc="upper left", ncol=3, frameon=True, facecolor="white", framealpha=0.9)
    ax1.set_title("(a) Multi-Source SAR & Hydrological Observation Timeline", fontweight="bold", loc="left")

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "Fig2a_Acquisition_Timeline.png"))
    fig.savefig(os.path.join(out_dir, "Fig2a_Acquisition_Timeline.pdf"))
    plt.close(fig)


def plot_sar_geometry_schematic(out_dir):
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    x_terrain = np.array([0.0, 1.5, 4.8, 7.2, 9.0])
    z_terrain = np.array([0.2, 0.2, 3.1, 3.5, 2.2])
    poly_pts = np.vstack([np.column_stack([x_terrain, z_terrain]), [[9.0, 0.0], [0.0, 0.0]]])
    ax.add_patch(Polygon(poly_pts, closed=True, facecolor="#E5E0D8", edgecolor="#4D4D4D", lw=1.2))
    ax.fill_between([0.0, 1.5], 0.0, 0.25, color="#A6CEE3", alpha=0.8)
    ax.text(0.75, 0.08, "Pacific Ocean", ha="center", fontsize=7.5, color="#08519C", fontweight="bold")

    ax.plot([1.8, 4.5], [0.46, 2.84], color="#B2182B", lw=3.0, label="Active Landslide Slope (~41 deg)")
    ax.annotate("", xy=(2.5, 1.08), xytext=(3.6, 2.05),
                arrowprops=dict(arrowstyle="->", color="#B2182B", lw=2.0))
    ax.text(3.35, 1.35, "True Downslope\nMotion (d_slope)", color="#B2182B", fontsize=8, fontweight="bold")

    ax.scatter([1.0], [5.4], s=80, color="#D95F02", marker="s", zorder=5)
    ax.text(1.0, 5.65, "Ascending Orbit (Right-Looking)\nForeslope -> Layover / Foreshortening", color="#D95F02", ha="center", fontsize=8, fontweight="bold")
    for xt, zt in [(2.0, 0.64), (4.3, 2.66)]:
        ax.plot([1.0, xt], [5.4, zt], "--", color="#D95F02", lw=1.0, alpha=0.8)

    ax.scatter([8.2], [5.4], s=80, color="#1B9E77", marker="s", zorder=5)
    ax.text(8.2, 5.65, "Descending Orbit (Right-Looking)\nBackslope -> Optimal Visibility", color="#1B9E77", ha="center", fontsize=8, fontweight="bold")
    for xt, zt in [(2.0, 0.64), (4.3, 2.66)]:
        ax.plot([8.2, xt], [5.4, zt], "-.", color="#1B9E77", lw=1.0, alpha=0.8)

    ax.set_xlim(0, 9.2)
    ax.set_ylim(0, 6.3)
    ax.set_xlabel("Cross-Shore Distance SW -> NE (km)")
    ax.set_ylabel("Relative Elevation (km)")
    ax.legend(loc="lower right", frameon=True)
    ax.set_title("(b) Side-Looking SAR Geometric Visibility Schematic on Steep Coastal Slope", fontweight="bold", loc="left")

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "Fig2b_SAR_Geometry_Schematic.png"))
    fig.savefig(os.path.join(out_dir, "Fig2b_SAR_Geometry_Schematic.pdf"))
    plt.close(fig)


def plot_spatiotemporal_matrix(out_dir, df_ts, start_dt):
    slices = [
        "2015-09-15", "2016-03-15", "2016-09-15",
        "2016-12-15", "2017-01-20", "2017-02-25",
        "2017-03-25", "2017-04-25", "2017-05-15"
    ]
    nx, ny = 120, 120
    x = np.linspace(-1.0, 1.0, nx)
    y = np.linspace(-1.0, 1.0, ny)
    xx, yy = np.meshgrid(x, y)
    xr = xx * np.cos(np.deg2rad(-35)) - yy * np.sin(np.deg2rad(-35))
    yr = xx * np.sin(np.deg2rad(-35)) + yy * np.cos(np.deg2rad(-35))
    ls_boundary = (xr / 0.55) ** 2 + (yr / 0.72) ** 2 <= 1.0

    fig, axes = plt.subplots(3, 3, figsize=(8.2, 7.6), sharex=True, sharey=True)
    norm = TwoSlopeNorm(vmin=-280.0, vcenter=0.0, vmax=280.0)
    rng = np.random.default_rng(99)

    for idx, date_str in enumerate(slices):
        ax = axes[idx // 3, idx % 3]
        dt = pd.Timestamp(date_str)
        row = df_ts[df_ts["date"] == dt].iloc[0]
        peak_disp = row["disp_z1"]
        r30 = row["rain_30d"]

        spread = 0.28 + 0.24 * np.clip(peak_disp / 260.0, 0, 1)
        spatial_pattern = np.exp(-((xr / spread) ** 2 + ((yr - 0.12 * (1 - peak_disp / 280.0)) / (spread * 1.25)) ** 2))
        field = -peak_disp * spatial_pattern * ls_boundary + rng.normal(0.0, 3.0, size=xx.shape)
        ocean = (xr + 0.85 * yr) < -0.78
        field = np.ma.masked_where(ocean, field)

        im = ax.imshow(field, extent=[640.05, 642.95, 3968.85, 3971.30], origin="lower", cmap="RdBu_r", norm=norm)
        ax.contour(np.linspace(640.05, 642.95, nx), np.linspace(3968.85, 3971.30, ny), ls_boundary.astype(float), levels=[0.5], colors="k", linewidths=0.9, linestyles="--")
        ax.set_title(f"({chr(97+idx)}) {date_str}", fontsize=8.5, fontweight="bold", loc="left", pad=3)
        ax.text(0.96, 0.92, f"R30d: {r30:.0f} mm", transform=ax.transAxes, ha="right", va="top",
                fontsize=7.2, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
        if idx // 3 == 2:
            ax.set_xlabel("Easting (km, UTM 10N)")
        if idx % 3 == 0:
            ax.set_ylabel("Northing (km)")

    cbar_ax = fig.add_axes([0.22, 0.058, 0.56, 0.017])
    cbar = fig.colorbar(im, cax=cbar_ax, orientation="horizontal")
    cbar.set_label(f"Cumulative Displacement Relative to {start_dt.strftime('%Y-%m-%d')} (mm)", fontweight="bold", labelpad=2)

    plt.subplots_adjust(left=0.08, right=0.97, top=0.95, bottom=0.15, wspace=0.08, hspace=0.16)
    fig.savefig(os.path.join(out_dir, "Fig5_Spatiotemporal_3x3_Matrix.png"))
    fig.savefig(os.path.join(out_dir, "Fig5_Spatiotemporal_3x3_Matrix.pdf"))
    plt.close(fig)


def plot_kinematics_and_lag(out_dir, df_ts, start_dt, fail_dt):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.6, 6.2), gridspec_kw={"height_ratios": [1.15, 1.0]})

    ax1.axvspan(start_dt, pd.Timestamp("2016-12-31"), color="#F0F0F0", alpha=0.85, label="Stage I: Drought Steady Creep")
    ax1.axvspan(pd.Timestamp("2017-01-01"), pd.Timestamp("2017-02-28"), color="#D1E5F0", alpha=0.75, label="Atmospheric River Storms")
    ax1.axvspan(pd.Timestamp("2017-03-01"), fail_dt, color="#FDDBC7", alpha=0.65, label="Stage II: Tertiary Creep Surge")

    sub = df_ts.iloc[::6]
    ax1.plot(sub["date"], sub["disp_z1"], "-o", markersize=2.8, color="#B2182B", lw=1.4, label="Zone I: Upper Tensile Scarp (P1)")
    ax1.fill_between(sub["date"], sub["disp_z1"] - 6.5, sub["disp_z1"] + 6.5, color="#B2182B", alpha=0.15)
    ax1.plot(sub["date"], sub["disp_z2"], "-s", markersize=2.6, color="#EF8A62", lw=1.3, label="Zone II: Central Block (P3)")
    ax1.plot(sub["date"], sub["disp_z3"], "-^", markersize=2.6, color="#2166AC", lw=1.3, label="Zone III: Coastal Toe (P5)")
    ax1.plot(sub["date"], sub["disp_ref"], "--", color="#4D4D4D", lw=1.0, label="Stable Reference (P_ref)")

    ax1.axvline(fail_dt, color="#67001F", linestyle="--", lw=1.3)
    ax1.set_ylabel("Cumulative Displacement (mm)")
    ax1.set_xlim(start_dt, fail_dt + pd.Timedelta(days=12))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.legend(loc="upper left", ncol=2, frameon=True, facecolor="white", framealpha=0.92)
    ax1.set_title("(a) Kinematic Sub-Zone Displacement Time-Series Across Climate Regimes", fontweight="bold", loc="left")

    zoom = df_ts[df_ts["date"] >= pd.Timestamp("2016-10-01")].copy()
    v_norm = (zoom["vel_z1"] - zoom["vel_z1"].mean()) / zoom["vel_z1"].std()
    r_norm = (zoom["rain_30d"] - zoom["rain_30d"].mean()) / zoom["rain_30d"].std()
    corr = correlate(v_norm, r_norm, mode="full") / len(zoom)
    lags = correlation_lags(len(zoom), len(zoom), mode="full")
    mask = (lags >= 0) & (lags <= 40)
    best_lag = int(lags[mask][np.argmax(corr[mask])])
    best_r = float(np.max(corr[mask]))

    ax2.plot(zoom["date"], zoom["vel_z1"], color="#B2182B", lw=1.8, label="Zone I Velocity (mm/day)")
    ax2.set_ylabel("Displacement Rate (mm/day)", color="#B2182B")
    ax2.set_ylim(0, 3.8)

    ax2_r = ax2.twinx()
    ax2_r.bar(zoom["date"], zoom["rain_mm"], width=1.2, color="#67A9CF", alpha=0.55, label="Daily Rainfall (mm/d)")
    ax2_r.plot(zoom["date"], zoom["rain_30d"] / 4.0, color="#053061", lw=1.3, linestyle="-.", label="30d Antecedent Rain (1:4)")
    ax2_r.axhline(35.0, color="#053061", linestyle=":", lw=1.0)
    ax2_r.set_ylabel("Daily / Scaled 30d Rain (mm)", color="#053061")
    ax2_r.set_ylim(0, 150)

    t_peak = pd.Timestamp("2017-01-09")
    t_resp = t_peak + pd.Timedelta(days=best_lag)
    ax2.axvspan(t_peak, t_resp, color="#FEE08B", alpha=0.55)
    ax2.annotate(
        f"Hydro-Mechanical Lag\nΔt = {best_lag} days (r = {best_r:.2f})",
        xy=(t_resp, 1.35), xytext=(pd.Timestamp("2016-11-05"), 2.65),
        arrowprops=dict(arrowstyle="->", color="#333333", lw=1.0),
        fontsize=8.0, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="#FFFDF0", ec="#D95F02", lw=0.8)
    )

    ax2.axvline(fail_dt, color="#67001F", linestyle="--", lw=1.3)
    ax2.set_xlim(pd.Timestamp("2016-10-01"), fail_dt + pd.Timedelta(days=5))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    l1, lb1 = ax2.get_legend_handles_labels()
    l2, lb2 = ax2_r.get_legend_handles_labels()
    ax2.legend(l1 + l2, lb1 + lb2, loc="upper left", frameon=True, facecolor="white", framealpha=0.92)
    ax2.set_title("(b) Dual-Axis Velocity Acceleration vs. Antecedent Rainfall Lag Window", fontweight="bold", loc="left")

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "Fig6_Kinematics_Driver_Lag.png"))
    fig.savefig(os.path.join(out_dir, "Fig6_Kinematics_Driver_Lag.pdf"))
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Publication-Grade InSAR Figure Suite")
    parser.add_argument("--out-dir", default="./python_outputs")
    parser.add_argument("--start-date", default="2015-03-01")
    parser.add_argument("--failure-date", default="2017-05-20")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    df_ts, asc_d, desc_d, s1b, s_dt, f_dt = build_demo_dataset(args.start_date, args.failure_date)
    plot_acquisition_timeline(args.out_dir, df_ts, asc_d, desc_d, s1b, s_dt, f_dt)
    plot_sar_geometry_schematic(args.out_dir)
    plot_spatiotemporal_matrix(args.out_dir, df_ts, s_dt)
    plot_kinematics_and_lag(args.out_dir, df_ts, s_dt, f_dt)
    print(f"[insar-figure-python] All figures exported to {args.out_dir}")


if __name__ == "__main__":
    main()
