# AR Glasses Master SDK Reference

**The most comprehensive open-source AR glasses SDK knowledge base.**
Covers 30+ repositories, 200+ source files, and every major consumer AR glasses platform.

---

## What This Is

A deeply researched, cross-referenced documentation repository for building software that targets AR glasses — XREAL, RayNeo, Rokid, Frame, Meta, Vuzix, Everysight, and more. Every claim is backed by actual source code analysis, not marketing docs.

This repo contains:
- **66KB Master SDK Reference** — complete API surface for xg-glass-sdk, MentraOS, XRLinuxDriver
- **123KB API Invocation Reference** (2 parts) — every callable function across all analyzed repos
- **99KB Cross-Functionality Analysis** — 45 integration opportunities across the ecosystem
- **75KB Jobs-to-be-Done Opportunities** — 15 validated product opportunities
- **18 numbered deep-reads** — individual repo analyses totaling 500KB+
- **Quick-reference cards** — VID/PID registry, protocol cheatsheet, sensor fusion guide

## Quick Start

| I want to...                          | Start here                                    |
|---------------------------------------|-----------------------------------------------|
| Understand the full API surface       | `docs/MASTER_SDK_REFERENCE.md`                |
| Look up a specific function call      | `docs/API_INVOCATION_REFERENCE.md`            |
| Find device VID/PID codes             | `reference/vid-pid-registry.md`               |
| Understand transport protocols        | `reference/protocol-cheatsheet.md`            |
| Work with IMU/sensor data             | `reference/sensor-fusion-guide.md`            |
| See what devices can do               | `docs/CAPABILITIES_MATRIX.md`                 |
| Find cross-device opportunities       | `docs/CROSS_FUNCTIONALITY.md`                 |
| Deep-dive a specific technology       | `docs/deep-reads/` (numbered 01–18)           |
| Understand repo architecture          | `ARCHITECTURE.md`                             |

## Repository Structure

```
ar-glasses-master-sdk/
├── README.md                              ← You are here
├── ARCHITECTURE.md                        ← System design & methodology
├── docs/
│   ├── MASTER_SDK_REFERENCE.md            ← 66KB complete API reference
│   ├── API_INVOCATION_REFERENCE.md        ← 60KB function-level docs (Part 1)
│   ├── API_INVOCATION_REFERENCE_PART2.md  ← 63KB function-level docs (Part 2)
│   ├── CAPABILITIES_MATRIX.md             ← Device feature comparison
│   ├── LINK_REGISTRY.md                   ← All analyzed repo URLs
│   ├── CROSS_FUNCTIONALITY.md             ← 99KB cross-device opportunities
│   ├── JTBD_OPPORTUNITIES.md              ← 75KB product opportunities
│   ├── GREP_REPASS_COMPLETE.md            ← 29KB symbol-level grep analysis
│   ├── MASTER_REFERENCE_SUMMARY.md        ← 7KB condensed reference
│   └── deep-reads/                        ← 18 individual repo analyses
│       ├── 01-core-sdks.md                   xg-glass-sdk, MentraOS, Vuzix
│       ├── 02-everysight-coredevices.md      Everysight Raptor, CoreDevices
│       ├── 03-xr-tools.md                    open-wearables, xreal-webxr, XRGaming
│       ├── 04-xr-drivers.md                  PhoenixTracker, XRLinuxDriver, RayDesk
│       ├── 05-stardustxr.md                  StardustXR Rust compositor
│       ├── 06-imu-sensors.md                 Fusion, headset-utils, real_utilities
│       ├── 07-rayneo-frame.md                RayNeo + Brilliant Frame
│       ├── 08-monado-specs.md                Monado OpenXR + platform specs
│       ├── 09-rayneo-docs.md                 RayNeo documentation
│       ├── 10-geo-maps.md                    Overpass + Gemini Maps integration
│       ├── 11-platform-docs.md               XREAL/OpenXR/SnapOS/Qualcomm
│       ├── 12-xg-glass-mentraos.md           xg-glass + MentraOS deep analysis
│       ├── 13-drivers-tools.md               Driver internals + tools
│       ├── 14-stardust-frame-samples.md      StardustXR + Frame samples
│       ├── 15-web-docs.md                    Web documentation analysis
│       ├── 16-utilities-samples.md           Utility libraries + samples
│       ├── 17-xreal-rayneo-qualcomm.md       Hardware platform analysis
│       └── 18-repass-wave5.md                Repass/verification wave
├── reference/
│   ├── vid-pid-registry.md                ← USB VID/PID + BLE identifiers
│   ├── protocol-cheatsheet.md             ← Transport protocols at a glance
│   └── sensor-fusion-guide.md             ← IMU math, quaternions, fusion
├── src/
│   └── core/                              ← Kotlin SDK core (GlassesClient)
└── .gitignore
```

## Devices Covered

| Device          | Transport    | SDK Language | IMU Rate    | Display          |
|-----------------|-------------|--------------|-------------|------------------|
| XREAL Air/One   | USB HID     | C            | 60–500 Hz   | 1920×1080 / SBS  |
| RayNeo X3       | USB HID     | C / Kotlin   | ~60 Hz      | 640×480 per eye  |
| RayNeo Luma     | USB HID     | C            | up to 1kHz  | 1920×1080 / SBS  |
| Rokid           | BLE→Wi-Fi   | Kotlin       | ~100 Hz     | 3840×1200 3D     |
| Frame           | BLE GATT    | Kotlin/Lua   | Varies      | Micro-display    |
| Meta            | BT HFP      | Kotlin       | N/A         | Audio-only       |
| Omi             | BLE GATT    | Kotlin       | N/A         | Audio-only       |
| Vuzix           | Android     | Kotlin/Java  | Varies      | Waveguide        |
| Everysight      | BLE         | Proprietary  | Varies      | Holographic      |

## Methodology

Every document was generated through direct source code reading — not documentation scraping. The process:

1. **Clone** all 30+ repos in the AR glasses ecosystem
2. **Deep-read** every significant source file (Kotlin, C, Rust, Python, Lua)
3. **Extract** actual API signatures, data types, and protocol details
4. **Cross-reference** capabilities across all platforms
5. **Synthesize** into structured reference documents

See `ARCHITECTURE.md` for the complete methodology and document relationships.

## Key Findings

- **xg-glass-sdk** provides the most complete cross-device abstraction (6 device backends)
- **XRLinuxDriver** is the de-facto Linux standard for USB AR glasses (31 supported models)
- **StardustXR** offers the most ambitious spatial computing compositor (full Rust, Flatbuffers IPC)
- **MentraOS** provides the most complete glasses-native OS framework
- **Sensor fusion** is the critical differentiator — 60Hz vs 1000Hz IMU rates matter

## Contributing

This is a living reference. To add coverage for a new device or SDK:

1. Clone the target repository
2. Read actual source files (not just README)
3. Document every public API with types and signatures
4. Add a numbered deep-read in `docs/deep-reads/`
5. Update `docs/CAPABILITIES_MATRIX.md` and `docs/LINK_REGISTRY.md`

## License

Documentation and analysis content. Original source code belongs to respective repository owners.
See `docs/LINK_REGISTRY.md` for all analyzed repositories and their licenses.
