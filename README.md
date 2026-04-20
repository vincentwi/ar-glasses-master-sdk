# AR Glasses Master SDK

> A unified, cross-device SDK for building AR glasses applications.
> Abstracts away device-specific APIs behind a common interface.

## Supported Devices

| Device | Connection | Display | Camera | Mic | Speaker | IMU | SLAM |
|--------|-----------|---------|--------|-----|---------|-----|------|
| RayNeo X3 Pro | USB/WiFi | Binocular MicroLED | 16MP | Yes | Yes | 6-axis | 6DoF |
| RayNeo X2 | USB/WiFi | Binocular MicroLED | 16MP | Yes | Yes | 9-axis | 6DoF |
| XREAL Air/One | USB-C | Micro-OLED | No* | No | Yes | 6-axis | 3DoF |
| Meta Ray-Ban | BLE | No* | 12MP | Yes | Yes | Yes | No |
| Brilliant Frame | BLE | micro-OLED | Yes | No | No | Yes | No |
| Rokid Max/Air | BLE/USB | Micro-OLED | No | No | Yes | 6-axis | 3DoF |
| Viture Luma Pro | USB-C | Micro-OLED | Yes* | No | Yes | 6-axis | 3DoF |
| Vuzix Blade 2 | USB/WiFi | DLP Waveguide | 8MP | Yes | Yes | 9-axis | No |

## Architecture

```
ar-glasses-master-sdk/
├── src/
│   ├── core/                    # Core abstractions
│   │   ├── GlassesClient.kt    # Main unified interface
│   │   ├── GlassesCallback.kt  # Event callbacks
│   │   ├── GlassesInfo.kt      # Device capabilities model
│   │   ├── BinocularRenderer.kt # Dual-eye rendering abstraction
│   │   └── types.kt            # Shared types, enums, data classes
│   ├── devices/                 # Per-device implementations
│   │   ├── rayneo/              # RayNeo X2/X3 Pro (Android ARDK)
│   │   ├── xreal/              # XREAL Air/One (X1 chip)
│   │   ├── meta/               # Meta Ray-Ban (DAT SDK)
│   │   ├── rokid/              # Rokid (BLE/WiFi)
│   │   ├── frame/              # Brilliant Labs Frame (BLE+Lua)
│   │   └── viture/             # Viture (USB-C tethered)
│   ├── drivers/                 # Low-level drivers
│   │   ├── imu/                # IMU sensor fusion (wraps xioTech/Fusion)
│   │   ├── display/            # Display management
│   │   └── input/              # Touch, gesture, voice input
│   └── utils/                   # Shared utilities
├── docs/                        # API reference documentation
├── examples/                    # Sample applications
└── tests/                       # Unit and integration tests
```

## Quick Start

```kotlin
// 1. Create a client for your target device
val client = GlassesClientFactory.create(DeviceType.RAYNEO_X3)

// 2. Connect with lifecycle callbacks
client.connect(context, object : GlassesCallback {
    override fun onConnected(info: GlassesInfo) {
        // 3. Use unified API
        client.display().showText("Hello AR World!", TextPosition.CENTER)
        client.sensors().startIMU { data ->
            // Head rotation tracking
            Log.d("IMU", "Yaw: ${data.euler.yaw}")
        }
    }
})
```

## Sources & References

This SDK is built on knowledge extracted from 30+ open-source repos:
- [xg-glass-sdk](https://github.com/hkust-spark/xg-glass-sdk) — Cross-device abstraction
- [MentraOS](https://github.com/Mentra-Community/MentraOS) — Server-side glasses apps
- [XRLinuxDriver](https://github.com/wheaney/XRLinuxDriver) — Linux head tracking
- [xioTechnologies/Fusion](https://github.com/xioTechnologies/Fusion) — IMU sensor fusion
- [TapLink X3](https://github.com/informalTechCode/TAPLINKX3) — Binocular browser
- [RayDesk](https://github.com/Quad-Labs/RayDesk) — Remote desktop streaming
- [StardustXR](https://github.com/StardustXR/server) — 3D XR desktop
- [headset-utils](https://github.com/3rl-io/headset-utils) — Rust XR abstraction
- [PhoenixHeadTracker](https://github.com/iVideoGameBoss/PhoenixHeadTracker) — Head tracking
- [frame-codebase](https://github.com/pkrumpl/frame-codebase) — TFLite on Frame

Full API reference: see `docs/MASTER_SDK_REFERENCE.md` (200KB+)

## License

Apache 2.0
