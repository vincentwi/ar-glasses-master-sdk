<div align="center">

# 🕶️ AR Glasses Master SDK

**The most comprehensive open-source AR glasses SDK knowledge base.**

Covers 30+ repositories · 200+ source files · Every major consumer AR platform

[![API Docs](https://img.shields.io/badge/API_Docs-Swagger_UI-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://vincentwi.github.io/ar-glasses-master-sdk/swagger/)
[![Full Reference](https://img.shields.io/badge/Full_Reference-Gist_API-2188FF?style=for-the-badge&logo=github&logoColor=white)](https://github.com/vincentwi/ar-glasses-master-sdk/blob/main/docs/FULL_API_REFERENCE.md)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-6BA539?style=for-the-badge&logo=openapiinitiative&logoColor=white)](./openapi.yaml)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](./LICENSE)

</div>

---

## What is this?

A deeply-researched, cross-referenced documentation repository for building software that targets AR glasses — **XREAL, RayNeo, Rokid, Frame, Meta, Vuzix, Everysight**, and more. Every claim is backed by actual source code analysis, not marketing material.

The SDK provides:
- **Unified API** — one interface to control any supported AR glasses
- **Complete API reference** — 500+ functions across 12 domains, 27 repos
- **OpenAPI spec** — machine-readable API definition with Swagger UI
- **Device matrix** — hardware + software capabilities for 9 device families
- **Fern SDK generation** — auto-generate TypeScript and Python clients

---

## Quick Start

### 1. Browse the API

Open the **[Interactive API Reference](https://vincentwi.github.io/ar-glasses-master-sdk/swagger/)** — dark-themed Swagger UI with every endpoint documented.

### 2. Use the SDK (Kotlin)

```kotlin
val client: GlassesClient = GlassesClientFactory.create(activity)
client.connect()

// Display text on any connected glasses
client.display("Hello from AR Glasses SDK")

// Read IMU sensor data
client.onImuData { data ->
    println("Quaternion: ${data.quaternion}")
    println("Acceleration: ${data.acceleration}")
}
```

### 3. Use the REST API

```bash
# List connected devices
curl http://localhost:8080/devices

# Display content
curl -X POST http://localhost:8080/devices/xreal-001/display \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello World", "mode": "replace"}'

# Stream IMU data
curl http://localhost:8080/devices/xreal-001/sensors/imu/stream
```

### 4. Generate a typed client (Fern)

```bash
npm install -g fern-api
fern generate --group ts-sdk
```

---

## Supported Devices

| Device | Transport | SDK Language | IMU Rate | Display | DoF | Camera | Standalone |
|--------|-----------|-------------|----------|---------|-----|--------|------------|
| **XREAL Air/One** | USB HID | C | 60–500 Hz | 1920×1080 SBS | 3DoF | ✗ | ✗ |
| **RayNeo X3 Pro** | USB HID | C / Kotlin | ~60 Hz | 1920×1080×2 | 6DoF | ✓ 16MP | Partial |
| **RayNeo Luma** | USB HID | C | up to 1kHz | 1920×1080 SBS | 3DoF | ✗ | ✗ |
| **Rokid Max** | BLE→Wi-Fi | Kotlin | ~100 Hz | 3840×1200 3D | 3DoF | ✗ | ✗ |
| **Brilliant Frame** | BLE GATT | Kotlin/Lua | Varies | 640×400 μOLED | — | ✓ Low-res | Partial |
| **Meta Ray-Ban** | BT HFP | Kotlin | N/A | Audio-only | — | ✓ 12MP | ✓ |
| **Vuzix Blade 2** | Android | Kotlin/Java | Varies | DLP Waveguide | — | ✓ 8MP | Partial |
| **Everysight** | BLE | Proprietary | Varies | Waveguide | — | ✓ | Partial |
| **Snap Spectacles 5** | Wi-Fi | TypeScript | — | Waveguide ~720p | 6DoF | ✓ | ✓ |

---

## Documentation

| Document | Description | Size |
|----------|-------------|------|
| [**API Reference (Swagger UI)**](https://vincentwi.github.io/ar-glasses-master-sdk/swagger/) | Interactive API explorer | — |
| [**OpenAPI Spec**](./openapi.yaml) | Machine-readable API definition | 15KB |
| [**Master SDK Reference**](./docs/MASTER_SDK_REFERENCE.md) | Complete API surface documentation | 66KB |
| [**Full API Reference**](./docs/FULL_API_REFERENCE.md) | Every callable function documented | 108KB |
| [**API Invocation Reference**](./docs/API_INVOCATION_REFERENCE.md) | Function-level docs (Part 1) | 60KB |
| [**API Invocation Reference Pt.2**](./docs/API_INVOCATION_REFERENCE_PART2.md) | Function-level docs (Part 2) | 63KB |
| [**Capabilities Matrix**](./docs/CAPABILITIES_MATRIX.md) | Device feature comparison | 4KB |
| [**Cross-Functionality**](./docs/CROSS_FUNCTIONALITY.md) | 45 integration opportunities | 99KB |
| [**JTBD Opportunities**](./docs/JTBD_OPPORTUNITIES.md) | 15 validated product opportunities | 75KB |
| [**Architecture**](./ARCHITECTURE.md) | System design & methodology | — |

### Quick Reference Cards

| Card | What's in it |
|------|-------------|
| [**VID/PID Registry**](./reference/vid-pid-registry.md) | USB Vendor/Product IDs and BLE identifiers for all devices |
| [**Protocol Cheatsheet**](./reference/protocol-cheatsheet.md) | Transport protocols at a glance — USB HID, BLE GATT, Wi-Fi |
| [**Sensor Fusion Guide**](./reference/sensor-fusion-guide.md) | IMU math, quaternions, complementary & Kalman filters |

### Deep Reads (18 individual repo analyses)

<details>
<summary>Click to expand full list</summary>

| # | Topic | Repos Covered |
|---|-------|--------------|
| 01 | [Core SDKs](./docs/deep-reads/01-core-sdks.md) | xg-glass-sdk, MentraOS, Vuzix |
| 02 | [Everysight + CoreDevices](./docs/deep-reads/02-everysight-coredevices.md) | Everysight Raptor, CoreDevices |
| 03 | [XR Tools](./docs/deep-reads/03-xr-tools.md) | open-wearables, xreal-webxr, XRGaming |
| 04 | [XR Drivers](./docs/deep-reads/04-xr-drivers.md) | PhoenixTracker, XRLinuxDriver, RayDesk |
| 05 | [StardustXR](./docs/deep-reads/05-stardustxr.md) | StardustXR Rust compositor |
| 06 | [IMU & Sensors](./docs/deep-reads/06-imu-sensors.md) | Fusion, headset-utils, real_utilities |
| 07 | [RayNeo + Frame](./docs/deep-reads/07-rayneo-frame.md) | RayNeo, Brilliant Frame |
| 08 | [Monado + Specs](./docs/deep-reads/08-monado-specs.md) | Monado OpenXR, platform specs |
| 09 | [RayNeo Docs](./docs/deep-reads/09-rayneo-docs.md) | RayNeo documentation |
| 10 | [Geo + Maps](./docs/deep-reads/10-geo-maps.md) | Overpass, Gemini Maps |
| 11 | [Platform Docs](./docs/deep-reads/11-platform-docs.md) | XREAL, OpenXR, SnapOS, Qualcomm |
| 12 | [xg-glass + MentraOS](./docs/deep-reads/12-xg-glass-mentraos.md) | Deep analysis |
| 13 | [Driver Internals](./docs/deep-reads/13-drivers-tools.md) | Driver internals + tools |
| 14 | [StardustXR + Frame Samples](./docs/deep-reads/14-stardust-frame-samples.md) | Samples |
| 15 | [Web Docs](./docs/deep-reads/15-web-docs.md) | Web documentation analysis |
| 16 | [Utilities + Samples](./docs/deep-reads/16-utilities-samples.md) | Utility libraries |
| 17 | [Hardware Platforms](./docs/deep-reads/17-xreal-rayneo-qualcomm.md) | XREAL, RayNeo, Qualcomm |
| 18 | [Verification](./docs/deep-reads/18-repass-wave5.md) | Repass/verification wave |

</details>

---

## API Domains

The unified API covers 12 domains:

| Domain | Endpoints | Description |
|--------|-----------|-------------|
| **Connection** | `GET /devices`, `POST /devices/{id}/connect` | Discovery, pairing, lifecycle |
| **Display** | `POST /devices/{id}/display` | Text, images, overlays |
| **Sensors** | `GET /devices/{id}/sensors/imu` | IMU, accelerometer, gyroscope |
| **Camera** | `POST /devices/{id}/camera/capture` | Photo/video capture |
| **Audio** | `POST /devices/{id}/audio/play` | Speaker playback, TTS |
| **Spatial** | `GET /devices/{id}/spatial/pose` | 6DoF tracking, SLAM, anchors |
| **Device** | `GET /devices/{id}/info` | Battery, firmware, capabilities |

---

## Project Structure

```
ar-glasses-master-sdk/
├── openapi.yaml                    ← OpenAPI 3.1 spec
├── README.md                       ← You are here
├── ARCHITECTURE.md                 ← System design & methodology
├── .github/workflows/
│   ├── docs.yml                    ← Swagger UI → GitHub Pages
│   └── fern.yml                    ← Fern SDK generation CI
├── fern/
│   ├── fern.config.json            ← Fern project config
│   ├── generators.yml              ← TypeScript + Python SDK generators
│   └── openapi/openapi.yaml        ← OpenAPI spec (Fern input)
├── docs/
│   ├── swagger/index.html          ← Dark-themed Swagger UI
│   ├── MASTER_SDK_REFERENCE.md     ← 66KB complete API reference
│   ├── FULL_API_REFERENCE.md       ← 108KB every function documented
│   ├── CAPABILITIES_MATRIX.md      ← Device feature comparison
│   └── deep-reads/                 ← 18 individual repo analyses
├── reference/
│   ├── vid-pid-registry.md         ← USB VID/PID + BLE identifiers
│   ├── protocol-cheatsheet.md      ← Transport protocols
│   └── sensor-fusion-guide.md      ← IMU math & quaternions
└── src/core/                       ← Kotlin SDK core
    ├── GlassesClient.kt
    ├── GlassesCallback.kt
    ├── Controllers.kt
    └── types.kt
```

---

## Key Findings

| Finding | Detail |
|---------|--------|
| **Best cross-device abstraction** | xg-glass-sdk — 6 device backends behind one API |
| **Linux standard** | XRLinuxDriver — 31 supported USB AR glasses models |
| **Most ambitious compositor** | StardustXR — full Rust, Flatbuffers IPC |
| **Most complete glasses OS** | MentraOS — full glasses-native OS framework |
| **Critical differentiator** | Sensor fusion — 60Hz vs 1000Hz IMU rates matter |

---

## Contributing

1. Clone the target repository you want to document
2. Read actual source files (not just README)
3. Document every public API with types and signatures
4. Add a numbered deep-read in `docs/deep-reads/`
5. Update `docs/CAPABILITIES_MATRIX.md` and `docs/LINK_REGISTRY.md`
6. If adding API endpoints, update `openapi.yaml`

---

## License

Documentation and analysis content © 2024–2026. Original source code belongs to respective repository owners.
See [`docs/LINK_REGISTRY.md`](./docs/LINK_REGISTRY.md) for all analyzed repositories and their licenses.
