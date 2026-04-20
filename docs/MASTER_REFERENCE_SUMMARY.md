# Master SDK Reference

> Unified API reference for all AR glasses platforms analyzed in this repository.
> Every major class, interface, protocol, and function signature consolidated.

## Table of Contents

1. [Unified API (xg-glass-sdk)](#unified-api)
2. [Device-Specific SDKs](#device-specific-sdks)
3. [Communication Protocols](#communication-protocols)
4. [Sensor Fusion](#sensor-fusion)
5. [Display & Rendering](#display--rendering)
6. [Platform Runtimes](#platform-runtimes)

---

## 1. Unified API (xg-glass-sdk)

### Core Interfaces

```kotlin
interface GlassesClient {
    val model: GlassesModel
    val capabilities: DeviceCapabilities
    val state: StateFlow<ConnectionState>
    val events: Flow<GlassesEvent>
    suspend fun connect(): Result<Unit>
    suspend fun disconnect()
    suspend fun capturePhoto(options: CaptureOptions = CaptureOptions()): Result<CapturedImage>
    suspend fun display(text: String, options: DisplayOptions = DisplayOptions()): Result<Unit>
    suspend fun playAudio(source: AudioSource, options: PlayAudioOptions = PlayAudioOptions()): Result<Unit>
    suspend fun startMicrophone(options: MicrophoneOptions = MicrophoneOptions()): Result<MicrophoneSession>
}
```

### Device Models
`GlassesModel`: FRAME, META, ROKID, RAYNEO, SIMULATOR, OMI

### Capabilities Model
```kotlin
data class DeviceCapabilities(
    canCapturePhoto: Boolean,
    canDisplayText: Boolean,
    canRecordAudio: Boolean,
    canPlayTts: Boolean,
    canPlayAudioBytes: Boolean,
    supportsTapEvents: Boolean,
    supportsStreamingTextUpdates: Boolean
)
```

### Connection States
`ConnectionState`: Disconnected, Connecting, Connected, Error(GlassesError)

### Events
`GlassesEvent`: Log(message), Warning(message), Tap(count)

### Audio
```kotlin
sealed class AudioSource {
    data class Tts(val text: String) : AudioSource()
    data class RawBytes(val data: ByteArray, val pcmFormat: PcmFormat?) : AudioSource()
}
// Encodings: PCM_S16_LE, PCM_S8, OPUS
```

---

## 2. Device-Specific SDKs

### RayNeo X3 Pro (Android ARDK)
- Camera: Camera2 API, 16MP, JPEG/YUV
- Display: Binocular MicroLED, SurfaceView rendering
- Audio: AudioTrack (playback), AudioRecord (capture)
- IMU: 6-axis, SensorManager
- SLAM: 6DoF via Qualcomm XR runtime
- Connection: USB-C (direct Android), WiFi (companion app)

### XREAL (NRSDK)
- Display: Micro-OLED, stereo rendering via NRFrame
- IMU: 6-axis via X1/X2 chip
- Head tracking: 3DoF (Air), 6DoF (One with phone SLAM)
- Connection: USB-C only (DP Alt Mode)
- Key classes: NRFrame, NRInput, NRSessionConfig

### Meta Ray-Ban (DAT SDK)
- Camera: 12MP, photo/video capture via companion app
- Audio: Open-ear speakers + mic array
- Connection: BLE to Meta companion app
- AI: Meta AI integration (cloud)
- No direct display output

### Brilliant Labs Frame
- Display: micro-OLED, 640x400, Lua scripting
- Camera: Low-res, ML inference via TFLite
- Connection: BLE (Nordic nRF)
- Programming: Lua on-device, Python companion (frame-sdk)
- Key API: frame.display, frame.camera, frame.microphone

### Snap Spectacles (Snap OS 2.0)
- Display: Dual waveguide, color
- Tracking: 6DoF SLAM, hand tracking
- Connection: WiFi/BLE
- Development: Lens Studio (TypeScript)
- AR: World mesh, plane detection, image tracking

### Everysight Maverick
- Display: Waveguide HUD
- Sensors: GPS, heart rate, cadence (cycling focus)
- Connection: BLE/WiFi
- SDK: Maverick SDK (Android), Element UI Kit
- Simulator available for desktop testing

---

## 3. Communication Protocols

### BLE (Bluetooth Low Energy)
- **Frame**: Nordic UART Service (NUS) — 6E400001-B5A3-F393-E0A9-E50E24DCCA9E
- **Meta**: Proprietary BLE profile via DAT SDK
- **Rokid**: CXR-M BLE protocol
- **Common pattern**: GATT services for command/response, notifications for events

### USB
- **XREAL**: USB-C DP Alt Mode + HID for IMU data
- **RayNeo**: USB-C Android (ADB), also WiFi
- **Viture**: USB-C DP Alt Mode + proprietary HID
- **HID Reports**: Gyro/accel data packed in HID report descriptors

### WiFi
- **RayNeo**: TCP socket for companion app communication
- **StardustXR**: Wayland-like protocol over Unix sockets
- **Snap**: WiFi Direct for low-latency data

### OpenXR
- **Monado**: Open-source OpenXR 1.1 runtime
- **Qualcomm Spaces**: OpenXR extensions for AR
- **Key extensions**: XR_EXT_hand_tracking, XR_MSFT_spatial_anchor, XR_FB_passthrough

---

## 4. Sensor Fusion

### IMU Processing Pipeline
```
Raw Gyro + Accel + Mag → Calibration → AHRS Filter → Quaternion → Euler Angles
```

### Algorithms (from xioTech/Fusion)
- **Madgwick filter**: Gradient descent, low compute, good for 6-axis
- **Mahony filter**: Complementary filter, robust to magnetic distortion
- **EKF**: Extended Kalman Filter for 9-axis fusion
- Key parameters: sample rate (typically 200-1000Hz), beta gain, recovery trigger

### Head Tracking Pipeline (XRLinuxDriver)
```
USB HID → Parse IMU report → Apply calibration → Madgwick AHRS → 
Quaternion → Virtual joystick output (uinput)
```

### Frame IMU (Brilliant Labs)
```lua
local imu = frame.imu
local heading = imu.heading()        -- compass heading
local roll = imu.roll()              -- roll angle
local pitch = imu.pitch()            -- pitch angle
local tap = imu.tap_callback(fn)     -- tap detection
```

---

## 5. Display & Rendering

### Display Technologies by Device
| Device | Tech | Resolution | FoV | Refresh |
|--------|------|-----------|-----|---------|
| RayNeo X3 Pro | MicroLED | 1920x1080×2 | 45° | 90Hz |
| XREAL Air 2 Ultra | Micro-OLED | 1920x1080×2 | 46° | 120Hz |
| Snap Spectacles 5 | Waveguide | ~720p equiv | 46° | 60Hz |
| Brilliant Frame | micro-OLED | 640x400 | 20° | 30Hz |
| Everysight Maverick | Waveguide | 320x240 | ~15° | 30Hz |

### Rendering Approaches
- **Android SurfaceView**: RayNeo, Rokid (native Android)
- **OpenGL ES**: XREAL NRSDK, Qualcomm Spaces
- **Lua Canvas**: Brilliant Frame (frame.display API)
- **Lens Studio**: Snap (TypeScript + visual editor)
- **StardustXR**: Wayland-based 3D compositor (Flatland protocol)

---

## 6. Platform Runtimes

### Qualcomm Snapdragon Spaces
- AR Foundation compatible
- OpenXR 1.1 runtime
- Hand tracking, plane detection, hit testing
- Target: Snapdragon AR1/AR2 chipsets

### Monado (Open Source OpenXR)
- Supports XREAL, Rokid via USB HID
- Linux-first, also Android
- Modular driver architecture
- SLAM via Basalt/ORB-SLAM

### StardustXR
- 3D XR desktop environment
- Flatland protocol (Wayland-inspired)
- Stardust protocol for 3D spatial items
- Server + client library (Rust)

---

## File Cross-Reference

| Topic | Primary File |
|-------|-------------|
| Unified API | DEEP-wave1a-core-sdks.md |
| Everysight / CoreDevice | DEEP-wave1b-everysight-coredevices.md |
| XR Tools | DEEP-wave1c-xr-tools.md |
| Linux Drivers | DEEP-wave2-xr-drivers.md |
| StardustXR | DEEP-wave3-stardustxr.md |
| IMU/Sensors | DEEP-wave4-imu-sensors.md |
| RayNeo/Frame | DEEP-wave5-rayneo-frame.md |
| Official Docs | DEEP-wave6-docs-specs.md |
| RayNeo Docs | DEEP-wave7-rayneo-docs.md |
| Geo/Maps | DEEP-wave8-geo-maps.md |
| Platform Docs | DEEP-wave9-platform-docs.md |
