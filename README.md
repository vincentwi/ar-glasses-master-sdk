<div align="center">

# AR Glasses Master SDK

**The most comprehensive open-source AR glasses SDK knowledge base.**

27+ repositories · 510 API paths · 12 domains · Every major consumer AR platform

[![Fern Docs](https://img.shields.io/badge/Fern_Docs-Live-6366f1?style=for-the-badge&logo=bookstack&logoColor=white)](https://vincent.docs.buildwithfern.com)
[![Swagger UI](https://img.shields.io/badge/Swagger_UI-Live-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://vincentwi.github.io/ar-glasses-master-sdk/swagger/)
[![Gist Reference](https://img.shields.io/badge/Full_Reference-Gist-2188FF?style=for-the-badge&logo=github&logoColor=white)](https://gist.github.com/vincentwi/e3bbcf547c24890ee42495739101aef5)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-6BA539?style=for-the-badge&logo=openapiinitiative&logoColor=white)](./openapi.yaml)

</div>

---

## What is this?

A deeply-researched, cross-referenced documentation repository for building software that targets AR glasses — **XREAL, RayNeo, Rokid, Brilliant Labs Frame, Meta, Vuzix, Everysight, Snap Spectacles**, and more. Every claim is backed by actual source code analysis of 27+ GitHub repos, 10+ documentation sites (including RayNeo Feishu wikis, Khronos OpenXR spec, Monado headers), and device SDKs.

### Live Documentation

| Platform | URL | What it is |
|----------|-----|------------|
| **Fern Docs** | [vincent.docs.buildwithfern.com](https://vincent.docs.buildwithfern.com) | Polished API reference + guides. Auto-deploys on every push. |
| **Swagger UI** | [vincentwi.github.io/ar-glasses-master-sdk](https://vincentwi.github.io/ar-glasses-master-sdk/swagger/) | Interactive API explorer. 510 paths, dark theme, deep-linking. Auto-deploys via GitHub Pages. |
| **GitHub Gist** | [Full API Reference](https://gist.github.com/vincentwi/e3bbcf547c24890ee42495739101aef5) | 108KB markdown. Every function with params, types, returns, examples. |
| **OpenAPI Spec** | [openapi.yaml](./openapi.yaml) | 309KB, 510 paths, 42 schemas. Machine-readable. |

### CI/CD — All 3 workflows run on every push to main

| Workflow | Purpose | Status |
|----------|---------|--------|
| `docs.yml` | Deploy Swagger UI to GitHub Pages | Passing |
| `fern-docs.yml` | Publish to vincent.docs.buildwithfern.com | Passing |
| `fern.yml` | Validate OpenAPI spec with Fern | Passing |

---

## Quick Start

### 1. Browse the API

Open **[Fern Docs](https://vincent.docs.buildwithfern.com)** for a polished view, or **[Swagger UI](https://vincentwi.github.io/ar-glasses-master-sdk/swagger/)** for interactive exploration.

### 2. Use the xg-glass-sdk (Python — cross-device)

```python
from xg_glass_sdk import GlassesClient

client = GlassesClient()
client.connect()
client.display("Hello from AR Glasses SDK")

# Read IMU data
client.on_imu_data(lambda data: print(f"Quaternion: {data.quaternion}"))
```

### 3. RayNeo 3DOF (Unity C#)

```csharp
// Initialize head tracking
HeadTrackedPoseParams.AwakeDriver();

// Get pose updates
void OnPostUpdate(Pose pose) {
    transform.rotation = pose.rotation; // pitch, yaw, roll
}

// Reset heading
HeadTrackedPoseParams.ResetRotation();
```

### 4. Fusion AHRS (C — sensor fusion)

```c
FusionAhrs ahrs;
FusionAhrsInitialise(&ahrs);

// Update with sensor data every cycle
FusionAhrsUpdate(&ahrs, gyroscope, accelerometer, magnetometer, deltaTime);

// Get orientation
FusionQuaternion q = FusionAhrsGetQuaternion(&ahrs);
FusionEuler euler = FusionQuaternionToEuler(q);
printf("Roll: %.1f, Pitch: %.1f, Yaw: %.1f\n", euler.roll, euler.pitch, euler.yaw);
```

### 5. Generate a typed client (Fern)

```bash
npm install -g fern-api
cd fern && fern generate --docs
```

---

## Supported Devices

| Device | Vendor | Transport | DoF | Camera | Display | Key SDK |
|--------|--------|-----------|-----|--------|---------|---------|
| **XREAL Air 2 Ultra** | XREAL | USB HID (VID `0x3318`) | 6DoF | Dual stereo | 1920x1080 SBS, 52° | Unity XR Plugin |
| **XREAL Air/Air 2** | XREAL | USB HID (VID `0x3318`) | 3DoF | — | 1920x1080 SBS, 46° | XRLinuxDriver |
| **RayNeo X3 Pro** | RayNeo | USB HID (VID `0x1bbb`) | 3DoF (+SLAM) | 16MP | Micro-LED, 43° | Android ARDK + Unity |
| **RayNeo X2** | RayNeo | USB HID | 6DoF | VGA SLAM | 1920x1080, 33° | OpenXR Unity ARDK |
| **VITURE One/Pro** | VITURE | USB HID (VID `0x35ca`) | 3DoF | — | 1920x1080 SBS, 43° | XRLinuxDriver |
| **Rokid Air/Max** | Rokid | BLE→Wi-Fi | 3DoF | — | 3840x1200 3D, 45° | xg-glass-sdk |
| **Brilliant Labs Frame** | Brilliant | BLE GATT | — | Low-res | 640x400 OLED | nRF52840 + TFLite Micro |
| **Vuzix Blade 2** | Vuzix | Android | — | 8MP | DLP Waveguide | HUD SDK (Java) |
| **Everysight Maverick** | Everysight | BLE | — | Yes | Waveguide | iOS/Android binary SDK |
| **Snap Spectacles** | Snap | Wi-Fi | 6DoF | Yes | Waveguide ~720p | Snap OS 2.0 / WebXR |
| **MentraOS Glasses** | Mentra | BLE→WebSocket | — | Yes | — | React Native + cloud |

---

## API Domains (510 paths across 12 domains)

| Domain | Paths | Description | Key Repos |
|--------|-------|-------------|-----------|
| **device** | 137 | Connection lifecycle, drivers, firmware, config, CLI | XRLinuxDriver, xg-glass-sdk, MentraOS |
| **imu** | 86 | AHRS, quaternion math, bias estimation, head tracking | Fusion, headset-utils, real_utilities |
| **display** | 44 | Text, bitmap, HUD menus, binocular stereo, curved | Frame, Vuzix, RayDesk, TAPLINKX3 |
| **stardust** | 44 | 3D spatial nodes, drawables, fields, panels, Wayland | StardustXR server/core/flatland/protostar |
| **ml** | 36 | TFLite Micro, SAM3 segmentation, Groq LLM | frame-codebase, TAPLINKX3, MentraOS |
| **spatial** | 36 | OpenXR sessions, Monado runtime, SLAM, plane detection | Monado, XREAL SDK, RayNeo ARDK |
| **geo** | 31 | Overpass OSM queries, Gemini Maps grounding, health data | overpass-turbo, Google AI, open-wearables |
| **audio** | 26 | TTS, mic capture, BeatSync, transcription | MentraOS, TAPLINKX3, CoreDevices |
| **ble** | 19 | BLE GATT (NUS, DAT, CXR-M), Wi-Fi P2P, WebSocket | MentraOS, Everysight, CoreDevices |
| **gesture** | 16 | Temple touch, gaze ray, hand tracking, ring input | RayNeo, decky-XRGaming, Monado |
| **camera** | 11 | Photo capture, SLAM cameras, frame processing | RayNeo ShareCamera, CoreDevices |
| **gps** | 3 | Phone GPS IPC, location streaming | RayNeo GPSIPCHelper |

---

## USB VID/PID Registry

| Brand | VID | Product IDs (sample) |
|-------|-----|---------------------|
| XREAL | `0x3318` | Air: `0x0424`, Air 2: `0x0428`, Air 2 Pro: `0x0432`, Air 2 Ultra: `0x0436` (10 PIDs total) |
| VITURE | `0x35ca` | One: `0x1011`, One Lite: `0x1013`, Pro: `0x1017` (14 PIDs total) |
| Rokid | various | 7 PIDs across Air/Max models |
| RayNeo | `0x1bbb` | X2: `0xaf50` |

Full registry: [`reference/vid-pid-registry.md`](./reference/vid-pid-registry.md)

---

## Documentation Index

### Core References

| Document | Size | Description |
|----------|------|-------------|
| [OpenAPI Spec](./openapi.yaml) | 309KB | 510 paths, 42 schemas, 12 domain tags |
| [Master SDK Reference](./docs/MASTER_SDK_REFERENCE.md) | 66KB | Unified API surface by domain |
| [Full API Reference](./docs/FULL_API_REFERENCE.md) | 109KB | Every function with params, types, returns, examples |
| [API Invocation Reference](./docs/API_INVOCATION_REFERENCE.md) | 60KB | Part 1: core SDKs + drivers |
| [API Invocation Reference Pt.2](./docs/API_INVOCATION_REFERENCE_PART2.md) | 63KB | Part 2: utilities + companion apps |
| [Capabilities Matrix](./docs/CAPABILITIES_MATRIX.md) | 4KB | Hardware × software feature grid |
| [Cross-Functionality](./docs/CROSS_FUNCTIONALITY.md) | 99KB | 45 cross-repo integration opportunities |
| [JTBD Opportunities](./docs/JTBD_OPPORTUNITIES.md) | 75KB | 15 Jobs-to-be-Done product ideas |
| [Link Registry](./docs/LINK_REGISTRY.md) | 5KB | Every crawled URL with status |

### Quick Reference Cards

| Card | Content |
|------|---------|
| [VID/PID Registry](./reference/vid-pid-registry.md) | USB Vendor/Product IDs for all devices |
| [Protocol Cheatsheet](./reference/protocol-cheatsheet.md) | BLE GATT, USB HID, IPC, WebSocket, FlatBuffers |
| [Sensor Fusion Guide](./reference/sensor-fusion-guide.md) | Fusion AHRS, complementary filter, quaternion math |

### Deep Reads (18 individual repo analyses)

<details>
<summary>Click to expand full list</summary>

| # | Topic | Repos Covered | Size |
|---|-------|---------------|------|
| 01 | [Core SDKs](./docs/deep-reads/01-core-sdks.md) | xg-glass-sdk, MentraOS, Vuzix Blade 2 | 26KB |
| 02 | [Everysight + CoreDevices](./docs/deep-reads/02-everysight-coredevices.md) | Everysight Maverick SDK, CoreDevices mobileapp | 44KB |
| 03 | [XR Tools](./docs/deep-reads/03-xr-tools.md) | open-wearables, xreal-webxr, decky-XRGaming | 42KB |
| 04 | [XR Drivers](./docs/deep-reads/04-xr-drivers.md) | PhoenixHeadTracker, XRLinuxDriver, RayDesk, TAPLINKX3 | 36KB |
| 05 | [StardustXR](./docs/deep-reads/05-stardustxr.md) | server, core, flatland, protostar (Rust) | 37KB |
| 06 | [IMU & Sensors](./docs/deep-reads/06-imu-sensors.md) | Fusion AHRS, headset-utils, real_utilities, imu-inspector | 42KB |
| 07 | [RayNeo + Frame](./docs/deep-reads/07-rayneo-frame.md) | RayNeo Unity SDK, TFLite on Frame, overpass-turbo | 27KB |
| 08 | [Monado + Specs](./docs/deep-reads/08-monado-specs.md) | Monado OpenXR (219+ xrt_* types), platform specs | 44KB |
| 09 | [RayNeo Docs](./docs/deep-reads/09-rayneo-docs.md) | Feishu wiki docs (3DOF/6DOF/GPS/Ring/Gaze) | 8KB |
| 10 | [Geo + Maps](./docs/deep-reads/10-geo-maps.md) | Overpass API, Gemini Maps grounding | 23KB |
| 11 | [Platform Docs](./docs/deep-reads/11-platform-docs.md) | XREAL SDK, OpenXR 1.1, SnapOS 2.0, Qualcomm | 27KB |
| 12–18 | [Additional analyses](./docs/deep-reads/) | Cross-verification, utilities, samples | ~200KB |

</details>

---

## Source Repositories (27+ analyzed)

<details>
<summary>Click to expand full list of analyzed repos</summary>

**Core SDKs:**
- [hkust-spark/xg-glass-sdk](https://github.com/hkust-spark/xg-glass-sdk) — Cross-device glasses SDK (Python)
- [Mentra-Community/MentraOS](https://github.com/Mentra-Community/MentraOS) — Full OS for smart glasses
- [Vuzix/Blade_2_Template_App](https://github.com/Vuzix/Blade_2_Template_App) — Vuzix Blade 2 template
- [everysight-maverick/sdk](https://github.com/everysight-maverick/sdk) — Everysight Maverick SDK
- [coredevices/mobileapp](https://github.com/coredevices/mobileapp) — CoreDevices/Pebble companion app

**XR Drivers & Tools:**
- [wheaney/XRLinuxDriver](https://github.com/wheaney/XRLinuxDriver) — Linux XR driver (102 C files, 4 brands)
- [wheaney/decky-XRGaming](https://github.com/wheaney/decky-XRGaming) — Steam Deck XR plugin
- [iVideoGameBoss/PhoenixHeadTracker](https://github.com/iVideoGameBoss/PhoenixHeadTracker) — XREAL head tracker
- [jakedowns/xreal-webxr](https://github.com/jakedowns/xreal-webxr) — WebHID protocol for XREAL
- [Quad-Labs/RayDesk](https://github.com/Quad-Labs/RayDesk) — Moonlight streaming to RayNeo
- [informalTechCode/TAPLINKX3](https://github.com/informalTechCode/TAPLINKX3) — AR browser for RayNeo

**StardustXR (Rust 3D compositor):**
- [StardustXR/server](https://github.com/StardustXR/server), [core](https://github.com/StardustXR/core), [flatland](https://github.com/StardustXR/flatland), [protostar](https://github.com/StardustXR/protostar)

**IMU & Sensor Fusion:**
- [xioTechnologies/Fusion](https://github.com/xioTechnologies/Fusion) — Madgwick AHRS (C)
- [3rl-io/headset-utils](https://github.com/3rl-io/headset-utils) — Rust XR abstraction
- [edwatt/real_utilities](https://github.com/edwatt/real_utilities) — XREAL Air protocol (C++)
- [abls/imu-inspector](https://github.com/abls/imu-inspector) — IMU data viewer
- [3rl-io/spidgets-3dof](https://github.com/3rl-io/spidgets-3dof) — 3DOF web bridge

**RayNeo:**
- [MaxManausa/Metaverse-Max-RayNeo-X3-Pro-Set-Up](https://github.com/MaxManausa/Metaverse-Max-RayNeo-X3-Pro-Set-Up)
- [MaxManausa/Rayneo_OpenXR_ARDK_Project](https://github.com/MaxManausa/Rayneo_OpenXR_ARDK_Project)
- [MaxManausa/RayNeoX3Pro-MITSample](https://github.com/MaxManausa/RayNeoX3Pro-MITSample)
- RayNeo Feishu docs (8 wiki pages), GitBook, open.rayneo.com

**Standards & Runtimes:**
- [Monado](https://gitlab.freedesktop.org/monado/monado) — Open-source OpenXR runtime
- [OpenXR 1.1 Spec](https://registry.khronos.org/OpenXR/specs/1.1/man/html/openxr.html) — Khronos standard
- [the-momentum/open-wearables](https://github.com/the-momentum/open-wearables) — MCP health data server

**Other:**
- [pkrumpl/frame-codebase](https://github.com/pkrumpl/frame-codebase) — TFLite Micro on Brilliant Frame
- [tyrasd/overpass-turbo](https://github.com/tyrasd/overpass-turbo) — OSM query tool
- Google Gemini Maps grounding API, Scaniverse/Niantic VPS, Qualcomm AR1 docs

</details>

---

## Project Structure

```
ar-glasses-master-sdk/
├── README.md                           ← You are here
├── ARCHITECTURE.md                     ← System design & methodology
├── openapi.yaml                        ← OpenAPI 3.1 (309KB, 510 paths, 42 schemas)
├── .github/workflows/
│   ├── docs.yml                        ← Swagger UI → GitHub Pages (auto)
│   ├── fern-docs.yml                   ← Fern → vincent.docs.buildwithfern.com (auto)
│   └── fern.yml                        ← Fern check (validation)
├── fern/
│   ├── fern.config.json                ← org: "vincent"
│   ├── docs.yml                        ← Fern docs navigation + pages
│   ├── generators.yml                  ← OpenAPI → SDK generation
│   ├── openapi/openapi.yaml            ← Spec copy for Fern
│   ├── pages/*.mdx                     ← 6 documentation pages
│   └── assets/                         ← Logos
├── docs/
│   ├── swagger/index.html              ← Dark-themed Swagger UI
│   ├── FULL_API_REFERENCE.md           ← 109KB, every function documented
│   ├── MASTER_SDK_REFERENCE.md         ← 66KB, unified by domain
│   ├── API_INVOCATION_REFERENCE.md     ← 60KB, invocation guide pt.1
│   ├── API_INVOCATION_REFERENCE_PART2.md ← 63KB, invocation guide pt.2
│   ├── CROSS_FUNCTIONALITY.md          ← 99KB, 45 opportunities
│   ├── JTBD_OPPORTUNITIES.md           ← 75KB, 15 JTBD ideas
│   ├── CAPABILITIES_MATRIX.md          ← Device comparison
│   ├── LINK_REGISTRY.md                ← Crawled URLs + status
│   ├── GREP_REPASS_COMPLETE.md         ← 29KB grep extraction
│   └── deep-reads/                     ← 18 numbered repo analyses (~400KB)
├── reference/
│   ├── vid-pid-registry.md             ← USB VID/PID quick-lookup
│   ├── protocol-cheatsheet.md          ← BLE/USB/IPC/WS protocols
│   └── sensor-fusion-guide.md          ← IMU fusion libraries
└── src/core/                           ← Kotlin SDK core
    ├── GlassesClient.kt
    ├── GlassesCallback.kt
    ├── Controllers.kt
    └── types.kt
```

---

## Key Findings

| Finding | Detail |
|---------|--------|
| **Best cross-device abstraction** | xg-glass-sdk — Python CLI, 6 device backends (Rokid, Meta, Frame, RayNeo, Omi, Sim) |
| **Linux standard driver** | XRLinuxDriver — 31 USB AR glasses models, 4 brands, C with libusb hotplug |
| **Most ambitious compositor** | StardustXR — Rust + Bevy + OpenXR, FlatBuffers over Unix sockets |
| **Most complete glasses OS** | MentraOS — React Native + cloud + BLE, full app ecosystem |
| **Critical sensor fusion** | Fusion (C) — Madgwick revised AHRS, acceleration/magnetic rejection, gyro bias |
| **6 overlap clusters** | IMU fusion (4 impl), device abstraction (3), display rendering (4), geo querying (3) |
| **10 capability gaps** | Hand tracking, persistent SLAM, eye tracking, depth sensing, multi-user, offline maps |

---

## Contributing

1. Clone the target repo you want to document
2. Read actual source files (not just README)
3. Document every public API with types and signatures
4. Add a numbered deep-read in `docs/deep-reads/`
5. Update `openapi.yaml` with new paths
6. Push — Fern docs + Swagger UI auto-deploy

---

## License

Documentation and analysis content © 2024–2026 vincentwi. Original source code belongs to respective repository owners. See [`docs/LINK_REGISTRY.md`](./docs/LINK_REGISTRY.md) for all analyzed repositories and their licenses.
