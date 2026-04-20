# Capabilities Matrix

> Cross-platform comparison of AR glasses capabilities.
> Updated: 2026-04-20

## Hardware Capabilities

| Feature | RayNeo X3 Pro | XREAL Air 2 Ultra | Meta Ray-Ban | Brilliant Frame | Rokid Max | Snap Spectacles 5 | Vuzix Blade 2 | Everysight Maverick |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Display** | MicroLED | Micro-OLED | None | micro-OLED | Micro-OLED | Waveguide | DLP Waveguide | Waveguide |
| **Resolution** | 1920x1080×2 | 1920x1080×2 | — | 640x400 | 1920x1080×2 | ~720p | 480p | 320x240 |
| **FoV** | 45° | 46° | — | 20° | 50° | 46° | 28° | ~15° |
| **Camera** | 16MP | No | 12MP | Low-res | No | Yes | 8MP | Yes |
| **Microphone** | Yes | No | Yes (array) | No | No | Yes | Yes | Yes |
| **Speaker** | Yes | Yes | Yes (open-ear) | No | Yes | Yes | Yes | Yes |
| **IMU** | 6-axis | 6-axis | Yes | Yes | 6-axis | 6DoF | 9-axis | Yes |
| **SLAM** | 6DoF | 3DoF | No | No | 3DoF | 6DoF | No | No |
| **GPS** | No | No | No | No | No | No | No | Yes |
| **Hand Tracking** | No | No | No | No | No | Yes | No | No |
| **Weight** | 79g | 78g | 49g | 39g | 75g | 226g | 120g | 55g |
| **Battery** | 1hr (glasses) | Tethered | All day | 2-3hr | Tethered | 45min | 2hr | 4hr |
| **Standalone** | Partial | No | Yes | Partial | No | Yes | Partial | Partial |

## Software / SDK Capabilities

| Feature | RayNeo X3 Pro | XREAL | Meta Ray-Ban | Brilliant Frame | Rokid | Snap Spectacles | Vuzix |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Native SDK** | Android ARDK | NRSDK | DAT SDK | frame-sdk | CXR-M | Lens Studio | Blade SDK |
| **Languages** | Kotlin/Java | C#/Unity | Swift/Kotlin | Lua/Python | Java | TypeScript | Java |
| **OpenXR** | Via Spaces | Partial | No | No | No | No | No |
| **Unity Support** | Yes | Yes | No | No | Yes | No | Yes |
| **BLE API** | No | No | Yes | Yes (NUS) | Yes | Yes | No |
| **USB HID** | Yes | Yes (IMU) | No | No | Yes | No | Yes |
| **Camera API** | Camera2 | No | Companion | frame.camera | No | Lens API | Yes |
| **Audio API** | AudioTrack | No | Companion | No | No | Yes | Yes |
| **On-device ML** | Yes (Snapdragon) | No | Cloud (Meta AI) | TFLite | No | Yes | No |
| **Simulator** | No | No | No | Yes | No | Lens Studio | No |
| **Cross-device SDK** | xg-glass-sdk | xg-glass-sdk | xg-glass-sdk | xg-glass-sdk | xg-glass-sdk | No | No |

## Connection Methods

| Device | Primary | Secondary | Protocol |
|--------|---------|-----------|----------|
| RayNeo X3 Pro | USB-C (Android) | WiFi TCP | ADB + custom |
| XREAL Air 2 Ultra | USB-C DP Alt | — | HID (IMU) |
| Meta Ray-Ban | BLE | WiFi (sync) | DAT protocol |
| Brilliant Frame | BLE (NUS) | — | Nordic UART |
| Rokid Max | USB-C | BLE | CXR-M |
| Snap Spectacles 5 | WiFi | BLE | Proprietary |
| Vuzix Blade 2 | USB | WiFi | Custom |
| Everysight Maverick | BLE | WiFi | Maverick SDK |

## Best Device By Use Case

| Use Case | Best Device | Why |
|----------|------------|-----|
| **AR Development** | RayNeo X3 Pro | Full SDK, 6DoF SLAM, camera + display |
| **Head-up Display** | XREAL Air 2 Ultra | Best display quality, lightweight |
| **AI Assistant** | Meta Ray-Ban | All-day battery, camera, mic, AI built-in |
| **Prototyping** | Brilliant Frame | Cheapest, Lua scripting, open SDK |
| **Spatial Computing** | Snap Spectacles 5 | Hand tracking, 6DoF, world mesh |
| **Media Consumption** | Rokid Max | Large FoV, tethered (no battery concern) |
| **Cycling/Sports** | Everysight Maverick | GPS, heart rate, lightweight HUD |
| **Enterprise** | Vuzix Blade 2 | Rugged, 9-axis IMU, camera |
