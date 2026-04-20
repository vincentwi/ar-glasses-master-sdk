# Architecture

## System Design & Document Relationships

This document describes how the AR Glasses Master SDK Reference is organized, how documents relate to each other, and the methodology behind the analysis.

---

## Document Hierarchy

```
                    ┌─────────────────────┐
                    │     README.md       │  Entry point
                    │   (navigation hub)   │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────▼──────┐ ┌─────▼──────┐ ┌──────▼───────┐
     │  Reference/   │ │   docs/    │ │    src/      │
     │ Quick-lookup  │ │ Analysis   │ │  Source code │
     └────────┬──────┘ └─────┬──────┘ └──────────────┘
              │               │
    ┌─────────┤         ┌─────┼──────────────┐
    │         │         │     │              │
  VID/PID  Protocol   Core  Deep-reads   Strategic
  Registry Cheatsheet Refs  (01-18)      Analysis
           Sensor
           Fusion
```

## Layer 1: Quick Reference (reference/)

**Purpose**: Answer a specific question in under 30 seconds.

| Document                    | Answers                                          |
|-----------------------------|--------------------------------------------------|
| `vid-pid-registry.md`       | "What VID/PID does this device use?"             |
| `protocol-cheatsheet.md`    | "How does this device communicate?"              |
| `sensor-fusion-guide.md`    | "How do I work with IMU data?"                   |

**Design principle**: Tables and code blocks only. No prose. Scannable.

## Layer 2: Core References (docs/)

**Purpose**: Comprehensive API documentation for building software.

| Document                          | Size  | Scope                                      |
|-----------------------------------|-------|--------------------------------------------|
| `MASTER_SDK_REFERENCE.md`         | 66KB  | Every API in xg-glass-sdk + MentraOS + XRLinuxDriver |
| `API_INVOCATION_REFERENCE.md`     | 60KB  | Function-level callable API (Part 1)       |
| `API_INVOCATION_REFERENCE_PART2.md` | 63KB | Function-level callable API (Part 2)       |
| `CAPABILITIES_MATRIX.md`         | 4KB   | Device × feature comparison grid            |
| `LINK_REGISTRY.md`               | 5KB   | All 30+ analyzed repository URLs            |
| `MASTER_REFERENCE_SUMMARY.md`    | 7KB   | Condensed cross-reference                   |

**Relationship**: The Master SDK Reference is the single source of truth. API Invocation References are organized by callable entry point rather than by device. The Capabilities Matrix is derived from both.

## Layer 3: Deep Reads (docs/deep-reads/)

**Purpose**: Complete source code analysis of individual repositories.

Numbered for reading order — dependencies flow forward:

| #  | File                          | Repos Covered                                    | Size |
|----|-------------------------------|--------------------------------------------------|------|
| 01 | core-sdks.md                  | xg-glass-sdk, MentraOS, Vuzix                   | 26KB |
| 02 | everysight-coredevices.md     | Everysight Raptor, CoreDevices                   | 44KB |
| 03 | xr-tools.md                   | open-wearables, xreal-webxr, XRGaming            | 42KB |
| 04 | xr-drivers.md                 | PhoenixTracker, XRLinuxDriver, RayDesk, TAPLINKX3| 36KB |
| 05 | stardustxr.md                 | StardustXR Rust compositor                        | 37KB |
| 06 | imu-sensors.md                | Fusion, headset-utils, real_utilities             | 42KB |
| 07 | rayneo-frame.md               | RayNeo + Brilliant Frame                          | 27KB |
| 08 | monado-specs.md               | Monado OpenXR runtime + platform specs            | 44KB |
| 09 | rayneo-docs.md                | RayNeo documentation corpus                       | 8KB  |
| 10 | geo-maps.md                   | Overpass API + Gemini Maps                        | 23KB |
| 11 | platform-docs.md              | XREAL/OpenXR/SnapOS/Qualcomm docs                | 27KB |
| 12 | xg-glass-mentraos.md          | xg-glass + MentraOS deep analysis                 | 44KB |
| 13 | drivers-tools.md              | Driver internals + development tools              | 37KB |
| 14 | stardust-frame-samples.md     | StardustXR + Frame code samples                   | 27KB |
| 15 | web-docs.md                   | Web platform documentation analysis               | 27KB |
| 16 | utilities-samples.md          | Utility libraries + sample applications           | 32KB |
| 17 | xreal-rayneo-qualcomm.md      | Hardware platform deep analysis                   | 33KB |
| 18 | repass-wave5.md               | Verification pass / gap analysis                  | 27KB |

**Total deep-read coverage**: ~540KB of source code analysis.

## Layer 4: Strategic Analysis (docs/)

**Purpose**: Synthesis and opportunity identification.

| Document                    | Size  | Content                                          |
|-----------------------------|-------|--------------------------------------------------|
| `CROSS_FUNCTIONALITY.md`    | 99KB  | 45 cross-device integration opportunities        |
| `JTBD_OPPORTUNITIES.md`    | 75KB  | 15 validated Jobs-to-be-Done product ideas        |
| `GREP_REPASS_COMPLETE.md`  | 29KB  | 74,574 symbol grep verification                  |

## Data Flow

```
30+ Git Repos
    │
    ▼
Source Code Reading (200+ files)
    │
    ├──▶ Deep Reads (01-18)         Raw analysis per repo
    │       │
    │       ▼
    ├──▶ Master SDK Reference        Unified API surface
    │       │
    │       ├──▶ API Invocation Refs   Function-level index
    │       ├──▶ Capabilities Matrix   Feature comparison
    │       └──▶ Reference Cards       Quick-lookup extracts
    │
    └──▶ Strategic Documents
            ├──▶ Cross-Functionality   Integration opportunities  
            └──▶ JTBD Opportunities    Product direction
```

## Analysis Methodology

### Phase 1: Repository Discovery
- GitHub search for AR glasses SDKs, drivers, tools
- Dependency graph traversal (what does each SDK import?)
- Community reference tracking (what do developers actually use?)

### Phase 2: Deep Reading (Waves 1–9)
Each wave targets a thematic cluster:
- **Wave 1** (a/b/c): Core SDKs, established platforms, XR tools
- **Wave 2**: Linux drivers and system-level integration
- **Wave 3**: StardustXR spatial computing compositor
- **Wave 4**: IMU and sensor fusion libraries
- **Wave 5**: RayNeo + Frame device-specific analysis
- **Wave 6**: Monado OpenXR and platform specifications
- **Wave 7**: RayNeo documentation corpus
- **Wave 8**: Geo/mapping integration (Overpass, Gemini)
- **Wave 9**: Platform documentation (XREAL, OpenXR, SnapOS, Qualcomm)

### Phase 3: Synthesis
- Cross-reference all APIs to find common patterns
- Identify capability gaps between devices
- Map integration opportunities between projects
- Validate via grep repass (74,574 symbols checked)

### Phase 4: Reference Extraction
- Pull quick-lookup data (VID/PIDs, protocols, IMU math) into reference cards
- Ensure every reference card cites its source document

## Source Code (src/)

The `src/core/` directory contains Kotlin source for the unified GlassesClient interface:

| File                   | Purpose                                    |
|------------------------|--------------------------------------------|
| `GlassesClient.kt`    | Main client interface for all devices      |
| `GlassesCallback.kt`  | Event callback definitions                 |
| `Controllers.kt`      | Input controller abstractions              |
| `types.kt`            | Shared type definitions                    |

This is the reference implementation extracted from xg-glass-sdk analysis.

## Design Decisions

1. **Larger version wins**: When both repos had overlapping content, the larger (more complete) version was kept. Old repo's 66KB Master Reference > New repo's 48KB. Old repo's 99KB Cross-Functionality > New repo's 65KB.

2. **Numbered deep-reads**: Sequential numbering (01–18) provides clear reading order and makes the scope immediately visible.

3. **Reference extraction**: Quick-lookup docs in `reference/` are derived from (not duplicating) the master docs. They cite their sources.

4. **Flat docs, nested deep-reads**: Top-level docs are the ones you'll use daily. Deep-reads are archival analysis you'll reference when needed.

5. **HTML preserved**: `DEEP_EXTRAPOLATION.html`, `FINAL_PRESENTATION.html`, and `opportunities-dashboard.html` are interactive visualizations kept for their unique presentation value.
