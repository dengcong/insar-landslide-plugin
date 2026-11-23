---
name: landslide-paper-architect
description: Architect and orchestrator skill for planning, structuring, and synthesizing international journal manuscripts on InSAR landslide monitoring and geohazard mechanisms. Completes the closed-loop workflow across geohazard-cartography-qgis, insar-figure-python, and landslide-quality-supervisor. Use when outlining a landslide or InSAR research paper, designing a Figure-to-Claim Storyboard, dispatching figure tasks to QGIS/Python executors, integrating audited figures into Results and Discussion prose, writing publication-grade figure captions, or preparing peer-review defense matrices for journals such as Landslides, Remote Sensing of Environment, Engineering Geology, or ISPRS JPRS.
---

# Landslide Paper Architect

Orchestrate the end-to-end academic manuscript lifecycle for InSAR-based landslide and geohazard studies. This skill serves as the top-level architect that closes the four-skill toolchain loop: planning the narrative and Figure-to-Claim Storyboard, dispatching spatial mapping to `geohazard-cartography-qgis` and quantitative/schematic plotting to `insar-figure-python`, routing outputs through `landslide-quality-supervisor` for scientific and cartographic auditing, and synthesizing audited evidence into publication-grade journal prose.

## When to Use

- Outlining a complete research paper or structuring section-by-section arguments for InSAR landslide monitoring, deformation kinematics, or failure mechanism studies.
- Designing a **Figure-to-Claim Storyboard** that assigns every figure and panel to `geohazard-cartography-qgis` or `insar-figure-python` without visual redundancy.
- Coordinating the closed-loop workflow from research hypothesis to figure generation, `landslide-quality-supervisor` audit, and manuscript synthesis.
- Drafting publication-grade **Figure Captions**, **Results**, **Discussion**, **Abstract**, and **Research Highlights** grounded in verified InSAR and GIS metrics.
- Building a **Peer-Review Defense Matrix** tailored to top geohazard and remote sensing journals (*Landslides*, *Remote Sensing of Environment*, *Engineering Geology*, *ISPRS JPRS*, *IEEE TGRS*).

## Closed-Loop Toolchain Architecture

Operate the four-skill suite as an iterative, quality-gated feedback loop rather than isolated one-off tools:

1. **Stage 1 - Architectural Blueprint (`landslide-paper-architect`):** Define the core scientific problem, target journal framing, kinematic hypotheses, and the Figure-to-Claim Storyboard before generating maps or charts.
2. **Stage 2 - Parallel Figure Execution (`geohazard-cartography-qgis` and `insar-figure-python`):** Dispatch geographic, terrain, and SAR geometric visibility maps to `geohazard-cartography-qgis`; dispatch acquisition timelines, displacement time-series, driver-response plots, 3x3 spatio-temporal matrices, and SAR side-looking schematics to `insar-figure-python`.
3. **Stage 3 - Scientific & Cartographic Audit (`landslide-quality-supervisor`):** Submit generated figures to `landslide-quality-supervisor` to audit LOS sign conventions, layover/shadow masks, colorbar semantics, multi-source consistency, and journal readiness.
4. **Stage 4 - Manuscript Synthesis & Loop Closure (`landslide-paper-architect`):** Ingest audited figures and quantitative metrics to draft structured captions, Results, Discussion, and reviewer-proofing tables. If evidence gaps or audit failures surface during drafting, loop back to Stage 2 with revised specifications.

## Step-by-Step Workflow

### Step 1: Anchor the Scientific Core and Target Journal

Establish the research framing before drafting outlines or figures so every section reinforces one coherent thesis:

- **Classify the Landslide System:** Identify failure typology and setting (e.g., deep-seated gravitational slope deformation, reactivated ancient landslide, reservoir-impounded slope, rainfall-triggered translational/rotational slide, alpine permafrost/rock glacier creep).
- **Calibrate to Target Journal Expectations:**
  - *Landslides* / *Engineering Geology*: Prioritize structural geology, kinematic sub-zoning, hydro-mechanical triggering thresholds, field/UAV fissure validation, and hazard/early-warning implications.
  - *Remote Sensing of Environment* / *ISPRS JPRS* / *IEEE TGRS*: Prioritize multi-track/multi-sensor fusion, 2D/3D displacement decomposition, SAR geometric distortion mitigation, phase unwrapping/atmospheric correction robustness, and workflow transferability.
- **Formulate Three Core Contributions:** Draft three concise, verifiable claims covering (1) data/methodological capability, (2) spatio-temporal kinematic discovery, and (3) physical triggering or failure mechanism insight.

### Step 2: Build the Figure-to-Claim Storyboard

Assign every figure a single, non-overlapping scientific claim and route it to the appropriate executor skill. Enforce strict division of labor so QGIS handles geographic/terrain layers and Python handles temporal, statistical, and cross-sectional plots:

- **Fig. 1 - Multi-Scale Study Area & Geological Setting (`geohazard-cartography-qgis`):** Four-panel nested regional-to-slope overview showing tectonic faults, lithology, drainage/reservoir boundary, landslide inventory, and field verification photos.
- **Fig. 2 - Multi-Source SAR Coverage & Geometric Visibility (`insar-figure-python` + `geohazard-cartography-qgis`):** Paired acquisition timeline and SAR side-looking schematic (`insar-figure-python`) alongside matched-extent ascending/descending geometric distortion (layover, foreshortening, shadow) and slope/aspect grids (`geohazard-cartography-qgis`).
- **Fig. 3 - Mean LOS Velocity & 2D/3D Kinematic Decomposition (`geohazard-cartography-qgis`):** Ascending and descending mean LOS velocity maps paired with decomposed vertical/east-west or downslope-projected velocity fields.
- **Fig. 4 - Micro-Geomorphology & 3D Terrain-Velocity Coupling (`geohazard-cartography-qgis`):** Multi-directional DEM hillshade comparison and 2.5D/3D perspective velocity overlay linking head scarps, lateral shear cracks, grabens, and toe bulging to velocity gradients.
- **Fig. 5 - Spatio-Temporal Deformation Evolution (`insar-figure-python`):** 3x3 cumulative displacement time-slice matrix revealing progressive headward retrogressive expansion or toe-driven destabilization.
- **Fig. 6 - Kinematic Time-Series & Environmental Triggering (`insar-figure-python`):** Representative monitoring point (P1-Pn) displacement curves with semantic trigger background shading and dual-axis driver-response plots (antecedent rainfall, reservoir water level fluctuations, or snowmelt).
- **Fig. 7 - Conceptual Geomechanical & Kinematic Model (`insar-figure-python`):** Annotated geological cross-section or 3D block diagram synthesizing surface InSAR sub-zones, inferred basal shear surface geometry, groundwater/seepage pathways, and failure mode.

Present the storyboard as a structured dispatch table before execution:

| Figure | Panels | Executor Skill | Core Scientific Claim | Audit Gate (`landslide-quality-supervisor`) |
| :--- | :--- | :--- | :--- | :--- |
| Fig. 1 | (a)-(d) | `geohazard-cartography-qgis` | Structural and lithological control on landslide boundary | Coordinate grid, scale bar, fault legend clarity |
| Fig. 2 | (a)-(d) | `insar-figure-python` + `geohazard-cartography-qgis` | Orbit complementarity overcomes single-track SAR distortion | Matched extent, layover/shadow mask consistency |
| Fig. 3 | (a)-(d) | `geohazard-cartography-qgis` | Spatial partitioning of upper vs. lower kinematic zones | LOS sign convention, diverging colorbar zero-anchor |
| Fig. 4 | (a)-(c) | `geohazard-cartography-qgis` | Micro-geomorphic scarps align with high velocity gradients | Hillshade illumination azimuth, 3D drape legibility |
| Fig. 5 | 3x3 grid | `insar-figure-python` | Progressive spatial propagation across monitoring epochs | Unified color scale across all 9 epochs |
| Fig. 6 | (a)-(b) | `insar-figure-python` | Nonlinear acceleration lags peak hydrological forcing | Synchronized date axis, lag window annotation |
| Fig. 7 | Schematic | `insar-figure-python` | Coupled retrogressive-translational failure mechanism | Alignment between surface velocity & subsurface kinematics |

### Step 3: Enforce the Supervisor Audit Gate

Never write final Results prose around unaudited visuals. Before advancing from Stage 3 to Stage 4, confirm that `landslide-quality-supervisor` has verified:

- **LOS Sign & Colorbar Semantics:** Positive (`+`) and negative (`-`) LOS directions are explicitly stated in the legend, caption, and text, with diverging colormaps centered on zero stability.
- **Visibility & Coherence Masking:** SAR shadow, layover, foreshortening, and low-coherence areas are masked or hatched so data gaps are not misread as stable ground.
- **Spatial & Temporal Alignment:** Multi-track maps share identical bounding boxes and coordinate frames; time-series and driver plots share aligned temporal axes and consistent reference dates.
- **Kinematic Plausibility:** Inferred motion vectors agree with downslope aspect and structural boundaries rather than atmospheric phase screen (APS) stratification artifacts.

### Step 4: Synthesize Publication-Grade Captions and Manuscript Sections

Convert audited figures and verified quantitative outputs into concise, high-impact academic text:

- **Four-Part Figure Caption Formula:**
  1. *Headline statement:* Summarize the overarching spatial or temporal finding in one clear sentence.
  2. *Panel-by-panel breakdown:* Decode `(a)`, `(b)`, `(c)` sequentially with sensor/orbit names, observation periods, and overlaid structural features.
  3. *Quantitative anchor:* Cite peak velocities (mm/yr), cumulative displacements (mm), or correlation/lag metrics directly in the caption.
  4. *Technical convention note:* Specify coordinate system, LOS direction convention, reference point location, and mask definitions.
- **Results Section Structure (Observe -> Quantify -> Partition):**
  - Open each subsection with the dominant spatial or temporal pattern rather than tool mechanics.
  - Anchor every qualitative adjective ("rapid", "accelerated", "concentrated") with exact values (mean +/- SD, peak rate, cumulative displacement, acceleration onset date).
  - Partition the slope into coherent kinematic sub-zones (e.g., Zone I upper tensile scarp, Zone II central translational block, Zone III lower compressional toe) instead of reciting raw point IDs one by one.
- **Discussion Section Structure (Mechanism -> Validation -> Uncertainty):**
  - *Hydro-Mechanical & Kinematic Mechanism:* Explain physical drivers behind sub-zone differences (e.g., rainfall infiltration elevating pore-water pressure along the basal shear zone vs. rapid reservoir drawdown reducing buttressing stress).
  - *Cross-Validation & Regional Context:* Compare deformation rates and failure style against field fissures, UAV DEMs of Difference (DoD), GNSS benchmarks, or published regional landslides.
  - *Visibility & Methodological Boundaries:* Explicitly address near-north-south insensitivity of polar-orbiting SAR, phase unwrapping limits during rapid surges, and residual tropospheric delays.

### Step 5: Generate Peer-Review Defense Matrix

Conclude manuscript packages with a proactive reviewer-proofing matrix addressing the most common critiques in InSAR geohazard peer review:

| Anticipated Reviewer Critique | Root Cause | Pre-Emptive Manuscript Fix | Supporting Evidence |
| :--- | :--- | :--- | :--- |
| 1D LOS underestimates true downslope movement | Oblique angle between slope aspect and SAR look vector | Present multi-track 2D decomposition or downslope projection with sensitivity index | Fig. 2, Fig. 3, Methods Eq. |
| Seasonal oscillations reflect tropospheric delay rather than creep | Elevation-dependent stratified water vapor in steep terrain | Show phase-elevation decorrelation stats and compare stable bedrock reference points | Methods, Fig. 6 baseline |
| Rainfall vs. reservoir level attribution is ambiguous | Co-occurring wet season and reservoir operation cycles | Quantify cross-correlation lag times and separate drawdown vs. impoundment phases | Fig. 6(b), Discussion |
| Lack of independent ground validation | Remote or hazardous terrain without continuous GNSS | Cross-check InSAR velocity gradients against field cracks, scarps, and multi-temporal hillshades | Fig. 1, Fig. 4 |
| Kinematic sub-zone boundaries appear subjective | Visual thresholding without quantitative criteria | Define zone boundaries using velocity gradient inflection points and geomorphic scarps | Fig. 3, Fig. 4 |

## Gotchas

- **Drafting prose before auditing figures:** Never finalize quantitative Results paragraphs before `landslide-quality-supervisor` clears the visuals. An inverted LOS sign or unmasked layover zone invalidates entire sections.
- **Point-by-point time-series recitation:** Do not narrate P1, P2, P3, and P4 sequentially with repetitive templates. Group monitoring points by structural/kinematic sub-zone and synthesize spatial gradients and phase lags.
- **Treating visual overlap as causal proof:** Placing rainfall bars behind a displacement curve does not prove causation. Always specify lag duration, antecedent rainfall threshold, or pore-pressure/buttressing mechanics in the Discussion.
- **Duplicating figures across executors:** Keep 2D/3D geographic maps and DEM hillshades in `geohazard-cartography-qgis`, and keep timelines, time-series, 3x3 matrices, and conceptual cross-sections in `insar-figure-python`.
- **Ignoring north-south SAR blindness:** Polar-orbiting satellites have poor sensitivity to north-south displacement. Always evaluate slope aspect relative to ascending/descending look vectors before claiming a slope is stable.
