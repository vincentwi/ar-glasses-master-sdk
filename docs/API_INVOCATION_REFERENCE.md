# AR Glasses Master SDK — API Invocation Reference

> Comprehensive API reference for cross-device SDKs and major tools.
> Generated from source analysis of repos at /tmp/glasses-repos/.

---

## Table of Contents

1. [xg-glass-sdk (Universal Glasses SDK)](#1-xg-glass-sdk)
2. [MentraOS SDK](#2-mentraos-sdk)
3. [XRLinuxDriver](#3-xrlinuxdriver)
4. [Fusion (IMU Sensor Fusion)](#4-fusion)
5. [TAPLINKX3](#5-taplinkx3)
6. [RayDesk](#6-raydesk)
7. [PhoenixHeadTracker](#7-phoenixheadtracker)
8. [StardustXR](#8-stardustxr)

---

## 1. xg-glass-sdk

**Language:** Kotlin (Android)
**Package:** `com.universalglasses.*`
**Purpose:** Universal cross-device SDK for smart glasses — write once, deploy to Frame, Rokid, Meta, RayNeo, XREAL, Omi, and Simulator.

### Setup & Installation

```groovy
// settings.gradle.kts — apply the settings plugin
plugins {
    id("com.universalglasses.rayneo-settings") // for RayNeo target
}

// build.gradle.kts — apply the app plugin
plugins {
    id("com.universalglasses.android-application")
}

dependencies {
    implementation(project(":core"))
    implementation(project(":app-contract"))
    // Pick your device module:
    implementation(project(":devices:device-simulator"))
    implementation(project(":devices:device-rokid"))
    implementation(project(":devices:device-meta"))
    implementation(project(":devices:device-frame-flutter"))
    implementation(project(":devices:device-omi"))
    implementation(project(":devices:device-rayneo-runtime"))
}
```

### Directory Structure

```
xg-glass-sdk/
├── core/                          Core interfaces and data models
│   └── src/main/java/com/universalglasses/core/
│       ├── GlassesClient.kt       Main device interface
│       ├── Models.kt               Data classes for capabilities, options
│       ├── Audio.kt                Audio types, microphone session
│       ├── Errors.kt               Error hierarchy
│       ├── StateAndEvents.kt       Connection states, event types
│       └── ExternalActivityBridge.kt  Activity launching bridge
├── app-contract/                  App entry point interfaces
│   └── src/main/java/com/universalglasses/appcontract/
│       └── UniversalAppEntry.kt   App registration, commands, settings
├── devices/
│   ├── device-simulator/          Simulator for dev/testing
│   ├── device-rokid/              Rokid Max/Air support
│   ├── device-meta/               Meta Ray-Ban Wearables
│   ├── device-omi/                Omi BLE pendant
│   ├── device-frame-flutter/      Brilliant Labs Frame (Flutter bridge)
│   ├── device-frame-embedded/     Brilliant Labs Frame (embedded)
│   ├── device-rayneo-runtime/     RayNeo runtime mode
│   └── device-rayneo-installer/   RayNeo installer mode
├── build-logic/                   Gradle convention plugins
└── templates/kotlin-app/          Project template
```

### Core API — `GlassesClient` Interface

```kotlin
package com.universalglasses.core

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

### Core Data Models

```kotlin
// --- Models.kt ---
enum class GlassesModel { SIMULATOR, FRAME, ROKID, RAYNEO, META_WEARABLES, OMI }

data class DeviceCapabilities(
    val canCapturePhoto: Boolean = true,
    val canDisplayText: Boolean = true,
    val canRecordAudio: Boolean = false,
    val canPlayTts: Boolean = false,
    val canPlayAudioBytes: Boolean = false,
    val supportsTapEvents: Boolean = false,
    val supportsStreamingTextUpdates: Boolean = false,
)

data class CaptureOptions(
    val quality: Int? = null,
    val targetWidth: Int? = null,
    val targetHeight: Int? = null,
    val timeoutMs: Long = 30_000,
)

enum class DisplayMode { REPLACE, APPEND }
data class DisplayOptions(val mode: DisplayMode = DisplayMode.REPLACE, val force: Boolean = false)

data class CapturedImage(
    val jpegBytes: ByteArray,
    val timestampMs: Long,
    val width: Int?, val height: Int?,
    val rotationDegrees: Int?,
    val sourceModel: GlassesModel,
)

// --- Audio.kt ---
enum class AudioEncoding { PCM_S16_LE, PCM_F32_LE, OPUS, MP3 }

sealed class AudioSource {
    data class Tts(val text: String) : AudioSource()
    data class RawBytes(val data: ByteArray, val pcmFormat: PcmFormat? = null) : AudioSource()
}

data class PcmFormat(
    val sampleRateHz: Int = 16_000,
    val channelCount: Int = 1,
    val encoding: AudioEncoding = AudioEncoding.PCM_S16_LE,
)

data class MicrophoneOptions(
    val preferredEncoding: AudioEncoding = AudioEncoding.PCM_S16_LE,
    val preferredSampleRateHz: Int? = 16_000,
    val preferredChannelCount: Int? = 1,
    val vendorMode: String? = null,
)

interface MicrophoneSession {
    val format: AudioFormat
    val audio: Flow<AudioChunk>
    suspend fun stop()
}

data class AudioChunk(
    val bytes: ByteArray, val format: AudioFormat,
    val sequence: Long, val timestampMs: Long, val endOfStream: Boolean = false,
)

// --- StateAndEvents.kt ---
sealed class ConnectionState {
    data object Disconnected : ConnectionState()
    data object Connecting : ConnectionState()
    data object Connected : ConnectionState()
    data class Error(val error: GlassesError) : ConnectionState()
}

sealed class GlassesEvent {
    data class Log(val message: String) : GlassesEvent()
    data class Warning(val message: String) : GlassesEvent()
    data class Tap(val count: Int) : GlassesEvent()
}

// --- Errors.kt ---
sealed class GlassesError(message: String, cause: Throwable? = null) : Exception(message, cause) {
    data object NotConnected : GlassesError("Not connected")
    data object PermissionDenied : GlassesError("Required permissions not granted")
    data object Busy : GlassesError("Device is busy")
    data class Timeout(val operation: String) : GlassesError("Timeout: $operation")
    data class Transport(val detail: String, val raw: Throwable? = null) : GlassesError(detail, raw)
    data class Unsupported(val detail: String) : GlassesError("Unsupported: $detail")
}
```

### App Contract — `UniversalAppEntry` Interface

```kotlin
package com.universalglasses.appcontract

interface UniversalAppEntry {
    val id: String
    val displayName: String
    fun commands(env: HostEnvironment): List<UniversalCommand>
    fun userSettings(): List<UserSettingField> = emptyList()
}

interface UniversalAppEntrySimple : UniversalAppEntry {
    fun commands(): List<UniversalCommand>
}

interface UniversalCommand {
    val id: String
    val title: String
    suspend fun run(ctx: UniversalAppContext): Result<Unit>
}

data class UniversalAppContext(
    val environment: HostEnvironment,
    val client: GlassesClient,
    val scope: CoroutineScope? = null,
    val log: (String) -> Unit = {},
    val onCapturedImage: ((CapturedImage) -> Unit)? = null,
    val settings: Map<String, String> = emptyMap(),
)

data class HostEnvironment(val hostKind: HostKind, val model: GlassesModel)
enum class HostKind { RAYNEO_LAUNCHER, ANDROID_APP }

// AI API Settings helper
object AIApiSettings {
    fun fields(/* overrides */): List<UserSettingField>
    fun baseUrl(settings: Map<String, String>): String
    fun model(settings: Map<String, String>): String
    fun apiKey(settings: Map<String, String>): String
}
```

### Device Implementations

Each device module implements `GlassesClient`:

| Class | Module | Description |
|-------|--------|-------------|
| `SimulatorGlassesClient(context, activityBridge?)` | device-simulator | Uses phone camera + TTS for testing |
| `RokidGlassesClient(context, activityBridge?)` | device-rokid | Rokid Max/Air via CxrApi SDK |
| `MetaWearablesGlassesClient(context, activityBridge?)` | device-meta | Meta Ray-Ban via Wearables SDK |
| `OmiGlassesClient(context)` | device-omi | Omi BLE pendant (audio-only) |
| `FrameGlassesClient(context, flutterEngine)` | device-frame-flutter | Brilliant Labs Frame |
| `EmbeddedFrameGlassesClient(context)` | device-frame-embedded | Brilliant Labs Frame (embedded) |
| `RayNeoRuntimeGlassesClient(context)` | device-rayneo-runtime | RayNeo runtime |
| `RayNeoInstallerGlassesClient(context)` | device-rayneo-installer | RayNeo installer |

### Usage Example

```kotlin
// In your app entry
class MyAppEntry : UniversalAppEntrySimple {
    override val id = "com.example.myapp"
    override val displayName = "My App"

    override fun commands() = listOf(
        object : UniversalCommand {
            override val id = "greet"
            override val title = "Say Hello"
            override suspend fun run(ctx: UniversalAppContext): Result<Unit> {
                ctx.client.display("Hello from ${ctx.environment.model}!")
                ctx.client.playAudio(AudioSource.Tts("Hello world"))
                val photo = ctx.client.capturePhoto()
                photo.onSuccess { ctx.onCapturedImage?.invoke(it) }
                return Result.success(Unit)
            }
        }
    )
}
```

---

## 2. MentraOS SDK

**Language:** TypeScript
**Package:** `@mentra/sdk` (v3.0.0-alpha.1)
**Purpose:** Build real-time smart glasses apps. Server-side SDK connects to MentraOS Cloud via WebSocket; WebView SDK for on-glasses web UIs.

### Setup & Installation

```bash
# Server SDK
bun add @mentra/sdk
# or
npm install @mentra/sdk

# WebView SDK (for on-glasses web apps)
bun add @mentra/webview-sdk
```

### Quick Start

```typescript
import { AppServer } from "@mentra/sdk";

const app = new AppServer({
  packageName: "com.example.myapp",
  apiKey: process.env.API_KEY!,
  port: 3000,
});

app.onSession((session) => {
  // Subscribe to transcription
  session.transcription.on((data) => {
    session.display.showTextWall(data.text);
  });
});

await app.start();
```

### Directory Structure

```
MentraOS/cloud/packages/sdk/
├── src/
│   ├── types/                    All TypeScript type definitions
│   │   ├── index.ts              Re-exports all types
│   │   ├── message-types.ts      Enum: GlassesToCloudMessageType, CloudToGlassesMessageType, etc.
│   │   ├── messages/
│   │   │   ├── base.ts           BaseMessage interface
│   │   │   ├── glasses-to-cloud.ts  ConnectionInit, ButtonPress, HeadPosition, etc.
│   │   │   ├── cloud-to-glasses.ts  DisplayEvent, ConnectionAck, AudioPlay, etc.
│   │   │   ├── app-to-cloud.ts      AppConnectionInit, PhotoRequest, StreamRequest, etc.
│   │   │   └── cloud-to-app.ts      AppConnectionAck, TranscriptionData, AudioChunk, etc.
│   │   ├── layouts.ts            TextWall, DoubleTextWall, DashboardCard, BitmapView, etc.
│   │   ├── streams.ts            StreamType enum, stream categories, language helpers
│   │   ├── models.ts             AppI, AppSettings, PermissionType, ToolSchema
│   │   ├── enums.ts              AppType, LayoutType, ViewType, AppSettingType
│   │   ├── dashboard/            DashboardMode, DashboardAPI, DashboardContentAPI
│   │   ├── webhooks.ts           WebhookRequestType, WebhookRequest/Response
│   │   ├── rtmp-stream.ts        VideoConfig, AudioConfig, StreamConfig
│   │   ├── capabilities.ts       Capabilities types
│   │   ├── photo-data.ts         PhotoData interface
│   │   └── token.ts              AppTokenPayload, TokenConfig
│   ├── transport/
│   │   ├── Transport.ts          Transport interface, TransportState
│   │   └── WebSocketTransport.ts WebSocketTransport class
│   └── app/
│       ├── index.ts              Re-exports AppServer, AppSession, token, webview
│       ├── server/index.ts       AppServer class (extends Hono)
│       ├── session/
│       │   ├── index.ts          AppSession class — main session handler
│       │   ├── layouts.ts        LayoutManager class
│       │   ├── settings.ts       SettingsManager class
│       │   ├── dashboard.ts      DashboardManager, DashboardSystemManager
│       │   ├── api-client.ts     ApiClient for HTTP calls
│       │   └── modules/
│       │       ├── camera.ts     CameraModule
│       │       ├── led.ts        LedModule
│       │       ├── audio.ts      AudioManager
│       │       └── simple-storage.ts  SimpleStorage
│       ├── token/
│       │   ├── index.ts          Token utilities
│       │   └── utils.ts          createToken, validateToken, generateWebviewUrl
│       └── webview/index.ts      Auth middleware for Hono, createAuthMiddleware
```

### Core Exported Classes

#### `AppServer` (extends Hono)

```typescript
import { AppServer } from "@mentra/sdk";

interface AppServerConfig {
  packageName: string;    // Your app's package name
  apiKey: string;         // MentraOS API key
  port?: number;          // Server port (default: 3000)
  cloudUrl?: string;      // MentraOS Cloud URL
}

class AppServer extends Hono {
  constructor(config: AppServerConfig);
  onSession(handler: (session: AppSession) => void): void;
  async start(): Promise<void>;
}
```

#### `AppSession`

```typescript
interface AppSessionConfig {
  token: string;
  cloudUrl?: string;
  // ...
}

class AppSession {
  // Sub-managers
  events: EventManager;
  display: LayoutManager;
  settings: SettingsManager;
  dashboard: DashboardManager;
  location: LocationModule;
  camera: CameraModule;
  led: LedModule;
  audio: AudioManager;
  storage: SimpleStorage;

  // Connection
  async connect(sessionId: string): Promise<void>;
  async disconnect(options?: { reason?: string }): Promise<void>;
  async releaseOwnership(reason: string): Promise<void>;

  // Event subscriptions — returns cleanup function
  onTranscription(handler: (data) => void): () => void;
  onHeadPosition(handler: (data) => void): () => void;
  onButtonPress(handler: (data) => void): () => void;
  onTouchEvent(gesture: string, handler: (data) => void): () => void;
  onPhoneNotification(handler: (data) => void): () => void;
  onGlassesBattery(handler: (data) => void): () => void;
  onConnectionState(handler: (state) => void): () => void;

  // Multi-user
  async discoverAppUsers(domain: string, includeProfiles?: boolean): Promise<any>;
  async isUserActive(userId: string): Promise<boolean>;
  async getUserCount(domain: string): Promise<number>;
  async broadcastToAppUsers(payload: any): Promise<void>;
  async sendDirectMessage(targetUserId: string, payload: any): Promise<boolean>;
  async joinAppRoom(roomId: string, options?: any): Promise<void>;
  async leaveAppRoom(roomId: string): Promise<void>;

  // Misc
  async getInstructions(): Promise<string | null>;
}
```

#### `LayoutManager`

```typescript
class LayoutManager {
  showTextWall(text: string): void;
  showDoubleTextWall(topText: string, bottomText: string): void;
  showDashboardCard(title: string, content: string): void;
  showReferenceCard(title: string, body: string): void;
  showBitmapView(data: string, width?: number, height?: number): void;
  clear(): void;
}
```

### Key Type Enums

```typescript
enum StreamType {
  TRANSCRIPTION, TRANSLATION, HEAD_POSITION, BUTTON_PRESS,
  PHONE_NOTIFICATION, GLASSES_BATTERY, PHONE_BATTERY,
  GLASSES_CONNECTION_STATE, LOCATION, AUDIO, VAD,
  CALENDAR_EVENT, TOUCH_EVENT, PHOTO, ...
}

enum LayoutType { TEXT_WALL, DOUBLE_TEXT_WALL, DASHBOARD_CARD, REFERENCE_CARD, BITMAP_VIEW }
enum DashboardMode { SYSTEM, CONTENT }
enum PermissionType { MICROPHONE, LOCATION, CAMERA, NOTIFICATIONS, ... }
```

### WebView SDK (On-Glasses)

```typescript
import { Bridge, CoreModule, Events, SocketBridge } from "@mentra/webview-sdk";

// Bridge — communication between WebView and React Native host
class Bridge {
  send(message: OutgoingMessage): void;
  subscribe(type: SubscriptionType, handler: SubscriptionHandler): () => void;
}

// CoreModule — display & microphone control
class CoreModule {
  displayText(args: DisplayTextArgs): void;
  setMicState(enabled: boolean): void;
}

// Events — subscribe to sensor/audio streams
class Events {
  onTranscription(handler: (text: string) => void): () => void;
  onMovement(handler: (data: MovementPayload) => void): () => void;
}

// SocketBridge — direct audio streaming
class SocketBridge {
  connect(url: string): void;
  disconnect(): void;
  onAudio(handler: (audio: ArrayBuffer) => void): () => void;
  onConnection(handler: (connected: boolean) => void): () => void;
}
```

### Token Utilities

```typescript
function createToken(payload: AppTokenPayload, secret: string, expiresIn?: string): string;
function validateToken(token: string, secret: string): TokenValidationResult;
function generateWebviewUrl(baseUrl: string, token: string): string;
function extractTokenFromUrl(url: string): string | null;
```

---

## 3. XRLinuxDriver

**Language:** C (C17)
**Build System:** CMake
**Purpose:** Linux driver for XR glasses (VITURE, RayNeo, Rokid, XREAL) — converts IMU data to mouse/joystick movement, provides virtual display IPC.

### Setup & Installation

```bash
# Download and run the setup script
wget https://github.com/wheaney/XRLinuxDriver/releases/latest/download/xr_driver_setup
chmod +x xr_driver_setup
sudo ./xr_driver_setup

# Build from source
git clone https://github.com/wheaney/XRLinuxDriver.git
cd XRLinuxDriver
mkdir build && cd build
cmake ..
make
```

### Directory Structure

```
XRLinuxDriver/
├── include/
│   ├── driver.h            Main driver entry points
│   ├── devices.h           Device properties and calibration
│   ├── imu.h               IMU data types (euler, quaternion, pose)
│   ├── ipc.h               Shared memory IPC for pose data
│   ├── config.h             Driver configuration struct
│   ├── buffer.h             Ring buffers for IMU data
│   ├── outputs.h            Mouse/joystick output handling
│   ├── multitap.h           Multi-tap gesture detection
│   ├── connection_pool.h    Device connection management
│   ├── runtime_context.h    Global runtime state
│   ├── logging.h            Logging utilities
│   ├── strings.h            String utilities
│   ├── curl.h               HTTP client init
│   ├── system.h             Hardware ID
│   ├── plugins/             Plugin system headers
│   │   ├── virtual_display.h     Virtual display plugin
│   │   ├── breezy_desktop.h      Breezy Desktop plugin
│   │   ├── smooth_follow.h       Smooth follow plugin
│   │   ├── sideview.h            Sideview plugin
│   │   ├── opentrack_source.h    OpenTrack UDP output
│   │   ├── opentrack_listener.h  OpenTrack UDP input
│   │   ├── metrics.h             Telemetry
│   │   ├── device_license.h      License management
│   │   ├── custom_banner.h       Custom banner overlay
│   │   └── gamescope_reshade_wayland.h  Gamescope integration
│   ├── features/            Feature flag headers
│   │   ├── breezy_desktop.h      Productivity feature checks
│   │   ├── sbs.h                 Side-by-side 3D
│   │   └── smooth_follow.h       Smooth follow feature
│   └── sdks/                Vendor SDK headers
│       ├── rayneo.h               RayNeo IMU/XR API
│       ├── rokid.h                Rokid sensor data types
│       ├── viture_device.h        VITURE IMU callbacks
│       ├── viture_device_carina.h VITURE Carina 6DoF
│       ├── viture_glasses_provider.h  VITURE device lifecycle
│       └── viture_protocol.h      VITURE protocol constants
```

### Core API

#### IMU Types (`imu.h`)

```c
struct imu_euler_t { float roll, pitch, yaw; };
struct imu_quat_t  { float x, y, z, w; };
struct imu_vec3_t  { float x, y, z; };
struct imu_pose_t  {
    struct imu_quat_t orientation;
    struct imu_vec3_t position;
    struct imu_euler_t euler;
    bool has_orientation;
    bool has_position;
};
```

#### Driver (`driver.h`)

```c
bool driver_reference_pose(imu_pose_type* out_pose, bool* pose_updated);
void driver_handle_pose(imu_pose_type pose);
bool driver_disabled();
```

#### IPC Shared Memory (`ipc.h`)

```c
struct ipc_values_t {
    float *display_res;
    bool  *disabled;
    float *date;
    float *pose_orientation;   // 16 floats (4x4 matrix)
    float *pose_position;      // 3 floats
    float *display_fov;
    float *lens_distance_ratio;
};

bool setup_ipc_values(ipc_values_type *ipc_values, bool debug);
void setup_ipc_value(const char *name, void **shmemValue, size_t size, bool debug);
```

#### Device Properties (`devices.h`)

```c
struct device_properties_t {
    char *brand; char *model;
    int hid_vendor_id, hid_product_id;
    int resolution_w, resolution_h;
    float fov;
    float lens_distance_ratio;
    int calibration_wait_s;
    int imu_cycles_per_s;
    int imu_buffer_size;
    float look_ahead_constant;
    bool sbs_mode_supported;
    bool firmware_update_recommended;
    bool provides_orientation; // 3DoF
};
```

#### Connection Pool (`connection_pool.h`)

```c
void connection_pool_init(pose_handler_t callback, reference_pose_getter_t getter);
void connection_pool_handle_device_added(const device_driver_type* driver, device_properties_type* device);
bool connection_pool_is_connected();
bool connection_pool_device_is_sbs_mode();
bool connection_pool_device_set_sbs_mode(bool enabled);
void connection_pool_disconnect_all(bool soft);
bool connection_pool_connect_active();
void connection_pool_block_on_active();
```

#### Buffer (`buffer.h`)

```c
buffer_type *create_buffer(int size);
void free_buffer(buffer_type *buffer);
float push(buffer_type *buffer, float next_value);
imu_buffer_type *create_imu_buffer(int buffer_size);
imu_buffer_response_type *push_to_imu_buffer(imu_buffer_type *buf, imu_quat_type quat, float timestamp_ms);
```

#### Vendor SDKs

```c
// RayNeo (rayneo.h)
void RegisterIMUEventCallback(IMUEventCallback callback);
int EstablishUsbConnection(int32_t vid, int32_t pid);
void StartXR(); void StopXR();
void SwitchTo2D(); void SwitchTo3D();
void OpenIMU(); void CloseIMU();
void Recenter();
void GetHeadTrackerPose(float rotation[4], float position[3], uint64_t* timeNsInDevice);

// VITURE (viture_glasses_provider.h)
XRDeviceProviderHandle xr_device_provider_create(int product_id, int fd, int bus, int dev);
int xr_device_provider_initialize(XRDeviceProviderHandle handle, const char* config);
int xr_device_provider_start(XRDeviceProviderHandle handle);
int xr_device_provider_stop(XRDeviceProviderHandle handle);
int xr_device_provider_shutdown(XRDeviceProviderHandle handle);
void xr_device_provider_destroy(XRDeviceProviderHandle handle);

// VITURE IMU (viture_device.h)
int register_raw_callback(XRDeviceProviderHandle handle, VitureImuRawCallback cb);
int register_pose_callback(XRDeviceProviderHandle handle, VitureImuPoseCallback cb);
int open_imu(XRDeviceProviderHandle handle, uint8_t mode, uint8_t freq);
int close_imu(XRDeviceProviderHandle handle, uint8_t mode);
```

---

## 4. Fusion

**Language:** C / Python (`imufusion`)
**Purpose:** Sensor fusion library for IMUs — AHRS algorithm combining gyroscope, accelerometer, and magnetometer.

### Setup & Installation

```bash
# Python
pip install imufusion

# C — include headers directly
#include "Fusion/Fusion.h"

# Build from source
git clone https://github.com/xioTechnologies/Fusion.git
cd Fusion
pip install .
```

### Header Files

```
Fusion/
├── Fusion.h               Master include (includes all below)
├── FusionAhrs.h           AHRS algorithm
├── FusionBias.h           Gyroscope bias estimation
├── FusionCompass.h        Tilt-compensated compass
├── FusionConvention.h     Earth axes convention enum
├── FusionMath.h           Math types and operations
├── FusionModel.h          Sensor calibration models
└── FusionRemap.h          Sensor axis remapping
```

### Core Types (`FusionMath.h`)

```c
typedef union { float array[3]; struct { float x, y, z; } axis; } FusionVector;
typedef union { float array[4]; struct { float w, x, y, z; } element; } FusionQuaternion;
typedef union { float array[9]; struct { float xx,xy,xz,yx,yy,yz,zx,zy,zz; } element; } FusionMatrix;
typedef union { float array[3]; struct { float roll, pitch, yaw; } angle; } FusionEuler;

// Constants
#define FUSION_VECTOR_ZERO
#define FUSION_QUATERNION_IDENTITY
#define FUSION_MATRIX_IDENTITY
#define FUSION_EULER_ZERO
```

### Math Functions (`FusionMath.h`)

```c
// Conversion
float FusionDegreesToRadians(float degrees);
float FusionRadiansToDegrees(float radians);
float FusionArcSin(float value);                    // Clamped asin

// Vector operations
bool          FusionVectorIsZero(FusionVector v);
FusionVector  FusionVectorAdd(FusionVector a, FusionVector b);
FusionVector  FusionVectorSubtract(FusionVector a, FusionVector b);
FusionVector  FusionVectorScale(FusionVector v, float s);
float         FusionVectorSum(FusionVector v);
FusionVector  FusionVectorHadamard(FusionVector a, FusionVector b);
FusionVector  FusionVectorCross(FusionVector a, FusionVector b);
float         FusionVectorDot(FusionVector a, FusionVector b);
float         FusionVectorNormSquared(FusionVector v);
float         FusionVectorNorm(FusionVector v);
FusionVector  FusionVectorNormalise(FusionVector v);

// Quaternion operations
FusionQuaternion FusionQuaternionAdd(FusionQuaternion a, FusionQuaternion b);
FusionQuaternion FusionQuaternionScale(FusionQuaternion q, float s);
FusionQuaternion FusionQuaternionProduct(FusionQuaternion a, FusionQuaternion b);
FusionQuaternion FusionQuaternionNormalise(FusionQuaternion q);
float            FusionQuaternionNorm(FusionQuaternion q);

// Matrix operations
FusionVector FusionMatrixMultiply(FusionMatrix m, FusionVector v);

// Conversions
FusionMatrix FusionQuaternionToMatrix(FusionQuaternion q);
FusionEuler  FusionQuaternionToEuler(FusionQuaternion q);
```

### AHRS Algorithm (`FusionAhrs.h`)

```c
typedef struct {
    FusionConvention convention;    // NWU, ENU, or NED
    float gain;                     // Filter gain (0 = gyro only)
    float gyroscopeRange;           // Degrees per second
    float accelerationRejection;    // Threshold in degrees
    float magneticRejection;        // Threshold in degrees
    unsigned int recoveryTriggerPeriod;
} FusionAhrsSettings;

// Lifecycle
void FusionAhrsInitialise(FusionAhrs *ahrs);
void FusionAhrsRestart(FusionAhrs *ahrs);
void FusionAhrsSetSettings(FusionAhrs *ahrs, const FusionAhrsSettings *settings);

// Update — call each sensor sample
void FusionAhrsUpdate(FusionAhrs *ahrs,
    FusionVector gyroscope,         // degrees/s
    FusionVector accelerometer,     // g
    FusionVector magnetometer,      // any unit
    float deltaTime);               // seconds

void FusionAhrsUpdateNoMagnetometer(FusionAhrs *ahrs,
    FusionVector gyroscope, FusionVector accelerometer, float deltaTime);

void FusionAhrsUpdateExternalHeading(FusionAhrs *ahrs,
    FusionVector gyroscope, FusionVector accelerometer,
    float heading, float deltaTime);

// Getters
FusionQuaternion         FusionAhrsGetQuaternion(const FusionAhrs *ahrs);
void                     FusionAhrsSetQuaternion(FusionAhrs *ahrs, FusionQuaternion q);
FusionVector             FusionAhrsGetGravity(const FusionAhrs *ahrs);
FusionVector             FusionAhrsGetLinearAcceleration(const FusionAhrs *ahrs);
FusionVector             FusionAhrsGetEarthAcceleration(const FusionAhrs *ahrs);
FusionAhrsInternalStates FusionAhrsGetInternalStates(const FusionAhrs *ahrs);
FusionAhrsFlags          FusionAhrsGetFlags(const FusionAhrs *ahrs);
void                     FusionAhrsSetHeading(FusionAhrs *ahrs, float heading);
```

### Bias Estimation (`FusionBias.h`)

```c
typedef struct {
    float sampleRate;           // Hz
    float stationaryThreshold;  // degrees per second
    float stationaryPeriod;     // seconds
} FusionBiasSettings;

void         FusionBiasInitialise(FusionBias *bias);
void         FusionBiasSetSettings(FusionBias *bias, const FusionBiasSettings *settings);
FusionVector FusionBiasUpdate(FusionBias *bias, FusionVector gyroscope);
FusionVector FusionBiasGetOffset(const FusionBias *bias);
void         FusionBiasSetOffset(FusionBias *bias, FusionVector offset);
```

### Compass (`FusionCompass.h`)

```c
float FusionCompass(FusionVector accelerometer, FusionVector magnetometer, FusionConvention convention);
```

### Sensor Models (`FusionModel.h`)

```c
FusionVector FusionModelInertial(FusionVector uncalibrated,
    FusionMatrix misalignment, FusionVector sensitivity, FusionVector offset);

FusionVector FusionModelMagnetic(FusionVector uncalibrated,
    FusionMatrix softIronMatrix, FusionVector hardIronOffset);
```

### Axis Remapping (`FusionRemap.h`)

```c
typedef enum { FusionRemapAlignmentPXPYPZ, /* 24 total orientations */ } FusionRemapAlignment;
FusionVector FusionRemap(FusionVector sensor, FusionRemapAlignment alignment);
```

### Python Usage

```python
import imufusion
import numpy as np

ahrs = imufusion.Ahrs()
ahrs.settings = imufusion.Settings(
    imufusion.CONVENTION_NWU,
    gain=0.5,
    gyroscope_range=2000,
    acceleration_rejection=10,
    magnetic_rejection=10,
    recovery_trigger_period=5 * sample_rate,
)

for gyro, accel, mag, dt in sensor_data:
    ahrs.update(gyro, accel, mag, dt)
    euler = ahrs.quaternion.to_euler()
    print(f"Roll={euler.roll:.1f} Pitch={euler.pitch:.1f} Yaw={euler.yaw:.1f}")
```

---

## 5. TAPLINKX3

**Language:** Kotlin (Android)
**Package:** `com.TapLink.app`
**Purpose:** Dual-display web browser for AR glasses with AI chat (Groq), bookmarks, custom keyboard, and QR scanning.

### Setup & Installation

```bash
cd TAPLINKX3
./gradlew assembleDebug
# Install on connected device:
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Directory Structure

```
TAPLINKX3/app/src/main/java/com/TapLink/app/
├── MainActivity.kt          Main Activity — browser, input, navigation
├── DualWebViewGroup.kt      Core dual-display WebView with stereo rendering
├── BookmarksView.kt         Bookmark management UI
├── ChatView.kt              AI chat panel (WebView-based)
├── CustomKeyboardView.kt    On-screen keyboard for glasses
├── ColorWheelView.kt        Color picker widget
├── FontIconView.kt          Font Awesome icon rendering
├── SystemInfoView.kt        Battery/time/connectivity status bar
├── GroqAudioService.kt      Microphone → Groq transcription
├── GroqInterface.kt         Groq LLM API integration (JS bridge)
├── WebAppInterface.kt       Legacy JS bridge for WebView
├── NotificationService.kt   System notification listener
├── MyApplication.kt         Application class
├── DebugLog.kt              Debug logging utility
└── Constants.kt             App constants
```

### Key Classes and Methods

#### `MainActivity` (extends AppCompatActivity)

Implements: `NavigationListener`, `LinkEditingListener`, keyboard/mic handling

```kotlin
// Navigation callbacks
fun onNavigationBackPressed()
fun onNavigationForwardPressed()
fun onQuitPressed()
fun onSettingsPressed()
fun onRefreshPressed()
fun onHomePressed()
fun onHyperlinkPressed()

// Link editing
fun onShowLinkEditing()
fun onSendCharacterToLink(character: String)
fun onSendBackspaceInLink()
fun onSendEnterInLink()
fun isLinkEditing(): Boolean

// Audio/TTS
fun prepareAudioForTtsPlayback()
fun getActiveWebViewUrlOrNull(): String?
```

#### `DualWebViewGroup` (extends ViewGroup)

Core rendering engine — duplicates WebView content for binocular display.

```kotlin
class DualWebViewGroup(context: Context, attrs: AttributeSet?, defStyleAttr: Int) : ViewGroup {
    interface WindowCallback { /* browser window events */ }
    interface KeyboardListener { fun onShowKeyboard(); fun onHideKeyboard() }

    // Internal scroll-aware WebView
    inner class InternalWebView(context: Context) : WebView {
        fun getHorizontalScrollRange(): Int
        fun getVerticalScrollRange(): Int
        // ... scroll metrics
    }
}
```

#### `BookmarksView` / `BookmarkManager`

```kotlin
data class BookmarkEntry(val id: String, val url: String, val isHome: Boolean)

class BookmarkManager(context: Context) {
    fun getBookmarks(): List<BookmarkEntry>
    fun addBookmark(url: String): BookmarkEntry
    fun updateBookmark(id: String, newUrl: String)
    fun deleteBookmark(id: String)
    fun setAsHome(id: String)
}

interface BookmarkListener {
    fun onBookmarkSelected(url: String)
    fun getCurrentUrl(): String
}
```

#### `CustomKeyboardView`

```kotlin
class CustomKeyboardView(context: Context, attrs: AttributeSet?) : ViewGroup {
    interface OnKeyboardActionListener {
        fun onKeyPressed(key: String)
        fun onBackspacePressed()
        fun onEnterPressed()
        fun onHideKeyboard()
        fun onClearPressed()
        fun onMoveCursorLeft()
        fun onMoveCursorRight()
        fun onMicrophonePressed()
    }

    fun setOnKeyboardActionListener(listener: OnKeyboardActionListener)
    fun updateHover(x: Float, y: Float)
    fun clearHover()
    fun handleAnchoredTap(x: Float, y: Float)
    fun copyStateFrom(source: CustomKeyboardView)
}
```

#### `GroqAudioService`

```kotlin
class GroqAudioService(context: Context) {
    interface TranscriptionListener {
        fun onTranscriptionResult(text: String)
        fun onError(message: String)
        fun onRecordingStart()
        fun onRecordingStop()
    }

    fun setListener(listener: TranscriptionListener)
    fun hasApiKey(): Boolean
    fun setApiKey(key: String)
    fun startRecording()
    fun stopRecording()
    fun isRecording(): Boolean
}
```

#### `GroqInterface` (JavaScript bridge)

```kotlin
class GroqInterface(context: Context, webView: WebView) {
    @JavascriptInterface fun ping(): String
    @JavascriptInterface fun getActivePageUrl(): String
    @JavascriptInterface fun chatWithGroq(message: String, historyJson: String, ttsEnabled: Boolean)
    @JavascriptInterface fun speakWithOrpheus(text: String)
    @JavascriptInterface fun openUrlInNewTab(url: String)
}
```

---

## 6. RayDesk

**Language:** Kotlin (Android)
**Package:** `com.raydesk.*`
**Purpose:** AR desktop streaming app for RayNeo glasses — streams PC desktop via Moonlight/GameStream with spatial display (curved monitor, keyhole viewport, head-tracked cursor).

### Setup & Installation

```bash
cd RayDesk
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Directory Structure

```
RayDesk/app/src/main/java/com/raydesk/
├── streaming/              Network streaming & server discovery
│   ├── MoonlightBridge.kt          Moonlight SDK integration
│   ├── StreamManager.kt            High-level stream lifecycle
│   ├── StreamState.kt              Connection state machine
│   ├── StreamConfig.kt             Resolution/bitrate/codec config
│   ├── ServerDiscoveryManager.kt   mDNS server discovery
│   ├── ServerInfo.kt               Server metadata
│   ├── DiscoveredServer.kt         Discovered server data
│   └── ReconnectionManager.kt      Auto-reconnect with backoff
├── spatial/                Head-tracking & virtual display math
│   ├── CylinderController.kt       Curved monitor projection control
│   ├── VirtualScreenController.kt  Flat virtual screen positioning
│   ├── KeyholeViewport.kt          Keyhole-mode viewport mapping
│   ├── OneEuroFilter.kt            1€ noise filter for head tracking
│   ├── Quaternion.kt               Quaternion math utilities
│   ├── TextureRect.kt              UV rect for texture sampling
│   ├── ViewportResult.kt           Combined viewport + cursor state
│   └── EdgeGlint.kt                Edge-of-screen cursor indicators
├── video/                  Video decode & texture management
│   ├── GLTextureRenderer.kt        GL render loop on TextureView
│   ├── VideoTextureProvider.kt     OES texture from decoder
│   ├── VideoSurfaceHolder.kt       SurfaceHolder adapter for Moonlight
│   ├── FrameSlot.kt                Lock-free frame exchange
│   └── TestPatternGenerator.kt     Test patterns for debugging
├── gl/                     OpenGL rendering
│   ├── StreamRenderer.kt           Main GL renderer (all display modes)
│   ├── CylinderMesh.kt             Curved screen geometry
│   ├── FlatQuadMesh.kt             Flat screen geometry
│   ├── ShaderUtils.kt              Shader compile/load utilities
│   └── environment/                Skybox, status ring, dashboard, frame
│       ├── EnvironmentRenderer.kt  Composite environment renderer
│       ├── SkyboxRenderer.kt       Procedural skybox
│       ├── StatusRingRenderer.kt   FPS/quality ring around monitor
│       ├── DashboardRenderer.kt    Info dashboard below monitor
│       ├── PhysicalFrameRenderer.kt Monitor bezel/frame
│       ├── DomeMesh.kt             Sky dome geometry
│       ├── StatusRingMesh.kt       Ring geometry
│       ├── MonitorFrameMesh.kt     Frame geometry
│       ├── DashboardMesh.kt        Dashboard geometry
│       └── EnvironmentShaders.kt   Shared shader programs
├── input/
│   └── HeadGazeCursor.kt           IMU → cursor position mapping
├── ui/                     Activities and UI components
│   ├── ConnectionActivity.kt       Server list & pairing screen
│   ├── StreamingActivity.kt        Main streaming activity
│   ├── CursorSettingsActivity.kt   Cursor sensitivity config
│   ├── StreamingMenuOverlay.kt     In-stream settings menu
│   ├── GameStyleMenuOverlay.kt     Full game-style menu system
│   ├── ConnectionOverlay.kt        Connection status overlay
│   ├── PinEntryDialog.kt           Pairing PIN entry dialog
│   ├── ServerListView.kt           Server list widget
│   ├── FocusNavigator.kt           Keyboard/head navigation
│   └── NumberGridView.kt           Grid-based number input
├── data/                   Persistence & configuration
│   ├── ServerRepository.kt         Save/load paired servers
│   ├── SavedServer.kt              Paired server data class
│   ├── CursorSettings.kt           Cursor sensitivity config
│   ├── StreamingSettings.kt        Display mode/input prefs
│   ├── EnvironmentTheme.kt         Theme data class
│   ├── EnvironmentThemes.kt        Built-in theme definitions
│   └── StatusRingDataProvider.kt   Interface for status data
└── test/
    └── RayDeskApplication.kt       Application class
```

### Key Classes

#### Streaming

```kotlin
// MoonlightBridge — core streaming integration
class MoonlightBridge(context: Context, decoderSurface: SurfaceProvider) {
    fun initializeDecoder(width: Int, height: Int, format: Int): Boolean
    fun setStreamConfig(config: StreamConfig)
    fun connect(address: String, port: Int, uniqueId: String, ...): Boolean
    fun disconnect()
    fun release()
    fun isStreaming(): Boolean
    fun isHevcSupported(): Boolean
    fun isAv1Supported(): Boolean
    fun sendAbsolutePosition(x: Int, y: Int, refWidth: Int, refHeight: Int)
    fun centerCursor(refWidth: Int, refHeight: Int)
    suspend fun quitExistingSession(address: String, port: Int, ...): Boolean
    suspend fun connectToSavedServer(server: SavedServer): Boolean
}

// StreamState
sealed class StreamState {
    object Disconnected : StreamState()
    object Connecting : StreamState()
    object Pairing : StreamState()
    data class Streaming(val width: Int, val height: Int) : StreamState()
    data class Error(val message: String) : StreamState()
}

// StreamConfig
data class StreamConfig(
    val width: Int, val height: Int, val fps: Int,
    val bitrate: Int, val audioEnabled: Boolean, ...
)
```

#### Spatial

```kotlin
// CylinderController — curved virtual monitor
class CylinderController {
    fun zoomIn() / fun zoomOut() / fun resetZoom()
    fun setRadius(radius: Float, immediate: Boolean = false)
    fun updateHeadPose(yaw: Float, pitch: Float, deltaTime: Float)
    fun recenter(currentYaw: Float, currentPitch: Float)
    fun updateCursorPosition(cursorX: Float, cursorY: Float)
    fun getViewMatrix(): FloatArray
    fun getMVPMatrix(): FloatArray
    fun getLeftEyeMVPMatrix(): FloatArray / fun getRightEyeMVPMatrix(): FloatArray
}

// HeadGazeCursor — head-tracking cursor
class HeadGazeCursor(screenWidth: Int, screenHeight: Int, ...) {
    fun updateHeadOrientation(yaw: Float, pitch: Float, timestamp: Long)
    fun updateFromQuaternion(sensorValues: FloatArray, timestamp: Long)
    fun getCursorPosition(): CursorPosition
    fun recenter()
    fun reset()
    fun updateScreenDimensions(newWidth: Int, newHeight: Int)
}

// Quaternion utility
data class Quaternion(val w: Float, val x: Float, val y: Float, val z: Float) {
    companion object {
        fun identity(): Quaternion
        fun fromSensorValues(values: FloatArray): Quaternion
        fun fromYawPitch(yawDegrees: Float, pitchDegrees: Float): Quaternion
    }
    fun multiply(other: Quaternion): Quaternion
    fun inverse(): Quaternion
    fun normalized(): Quaternion
    fun toYawPitch(): Pair<Float, Float>
}
```

---

## 7. PhoenixHeadTracker

**Language:** C# (.NET Framework 4.7.2, Windows Forms)
**Purpose:** Head-tracking app for gaming — reads IMU euler angles from XREAL Air glasses via `AirAPI_Windows.dll`, converts to mouse movement or OpenTrack UDP output.

### Setup & Installation

```
1. Open PhoenixHeadTracker.sln in Visual Studio
2. Build (Release or Debug)
3. Requires AirAPI_Windows.dll in the output directory
4. Run PhoenixHeadTracker.exe
```

### HID Protocol

Uses `AirAPI_Windows.dll` native library:

```csharp
[DllImport("AirAPI_Windows", CallingConvention = CallingConvention.Cdecl)]
public static extern int StartConnection();   // Returns 1 on success

[DllImport("AirAPI_Windows", CallingConvention = CallingConvention.Cdecl)]
public static extern int StopConnection();

[DllImport("AirAPI_Windows", CallingConvention = CallingConvention.Cdecl)]
public static extern IntPtr GetEuler();        // Returns float[3]: [roll, pitch, yaw]
```

### Form1 Class — Key Methods

```csharp
public partial class Form1 : Form {
    // === Connection ===
    void button2_Click(sender, e)           // Connect to glasses, start timer

    // === Core Loop (timer1_Tick) ===
    void timer1_Tick(sender, e)             // 60Hz loop:
        // 1. GetEuler() → arr[3]
        // 2. Calculate scaled x, y, roll from euler * screenScale / speed
        // 3. Kalman filter on deltas
        // 4. Update xRot, yRot, rollRot with drift compensation
        // 5. If isOpenTrack: send UDP [x, y, z, yaw, pitch, roll] (6 doubles)
        // 6. If isMouseTrack: SendInput() with filtered deltas
        // 7. Rotate visual indicators (pictureBox1-3)

    // === OpenTrack Mode ===
    void buttonStartOpentrack_Click(sender, e)   // Start UDP output
    void buttonStopOpentrack_Click(sender, e)     // Stop UDP output
    // Protocol: 6 doubles over UDP = {x, y, z, yaw, pitch, roll}
    // Default: 127.0.0.1:4242

    // === Mouse Mode ===
    void buttonMouseTrackOn_Click(sender, e)      // Start mouse control
    void buttonMouseTrackOff_Click(sender, e)     // Stop mouse control

    // === Calibration ===
    void buttonReset_Click(sender, e)             // Reset rotation to zero
    void ResetValues()                             // Zero all tracking state

    // === Drift Compensation ===
    void buttonFightDriftXPlus_Click(sender, e)   // Adjust X drift +1
    void buttonFightDriftXMinus_Click(sender, e)  // Adjust X drift -1
    // ... same for Y and Roll

    // === Raw Input ===
    void WndProc(ref Message m)                   // Handle WM_INPUT for mouse injection
}

// Kalman Filter helper
public class KalmanFilter {
    public KalmanFilter(double q, double r, double p, double x);
    public double Update(double measurement);
    // q = process noise, r = measurement noise, p = initial error covariance
}
```

### OpenTrack UDP Protocol

```
Target: configurable IP:port (default 127.0.0.1:4242)
Payload: 48 bytes = 6 × double (little-endian)
  [0] x        (always 0)
  [1] y        (always 0)
  [2] z        (always 0)
  [3] yaw      (degrees, from xRot)
  [4] pitch    (degrees, from yRot)
  [5] roll     (degrees, from rollRot)
```

### Configuration Controls

| Control | Purpose |
|---------|---------|
| `trackBarYawSpeed` | Yaw sensitivity (higher = slower) |
| `trackBarPitchSpeed` | Pitch sensitivity |
| `trackBarRollSpeed` | Roll sensitivity |
| `trackBarDrift` | Mouse speed multiplier |
| `trackBarMouseSmooth` | Smoothing iterations |
| `trackBarMouseDelay` | Delay between smoothing passes (ms) |
| `textBoxYawTrackValue` | Yaw scale factor |
| `textBoxPitchTrackValue` | Pitch scale factor |
| `textBoxRollTrackValue` | Roll scale factor |
| `checkBoxInvertYaw/Pitch/Roll` | Invert axes |
| `checkBoxYaw/Pitch/Roll` | Enable/disable axes |

---

## 8. StardustXR

**Language:** Rust
**Purpose:** XR spatial computing compositor ecosystem — server (Wayland + OpenXR compositor), client SDK (fusion), Wayland panel manager (flatland), and app launchers (protostar).

### Repos

```
stardust-server/     — Bevy-based OpenXR + Wayland compositor
stardust-core/       — Client libraries (fusion, wire, gluon, protocol)
stardust-flatland/   — Wayland panel item manager
stardust-protostar/  — App launchers (hexagon grid, single, sirius)
```

### Setup & Installation

```bash
# Build the server
cd stardust-server
cargo build --release

# Build a client (e.g., flatland)
cd stardust-flatland
cargo build --release

# Run
stardust-server &
stardust-flatland &

# Rust dependency
[dependencies]
stardust-xr-fusion = { path = "../stardust-core/fusion" }
```

### stardust-core/fusion — Client SDK

The main client library for building StardustXR apps.

#### Client Connection

```rust
pub struct Client { /* ... */ }

impl Client {
    pub async fn connect() -> Result<Self, ClientError>;
    pub fn from_connection(connection: UnixStream) -> Self;
    pub fn handle(&self) -> Arc<ClientHandle>;
    pub fn get_root(&self) -> &Root;
    pub fn setup_resources(&self, paths: &[&Path]) -> NodeResult<()>;
    pub async fn dispatch(&mut self) -> Result<(), MessengerError>;
    pub async fn flush(&mut self) -> Result<(), MessengerError>;
    pub async fn await_method<O, F: Future<Output = O>>(&mut self, method: F) -> O;
    pub async fn sync_event_loop<F: FnMut(&Arc<ClientHandle>, &mut ControlFlow)>(
        mut self, f: F);
    pub fn async_event_loop(mut self) -> AsyncEventLoop;
}
```

#### Spatial Types

```rust
pub struct Transform {
    pub translation: Option<Vector3<f32>>,
    pub rotation: Option<Quaternion>,
    pub scale: Option<Vector3<f32>>,
}

impl Transform {
    pub fn from_translation(translation: impl Into<Vector3<f32>>) -> Self;
    pub fn from_rotation(rotation: impl Into<Quaternion>) -> Self;
    pub fn from_scale(scale: impl Into<Vector3<f32>>) -> Self;
    pub fn from_translation_rotation(t, r) -> Self;
    pub fn from_rotation_scale(r, s) -> Self;
    pub fn from_translation_scale(t, s) -> Self;
    pub fn from_translation_rotation_scale(t, r, s) -> Self;
}
```

#### Drawables

```rust
impl Lines {
    pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
                  lines: &[Line]) -> NodeResult<Self>;
}

impl Model {
    pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
                  model_resource: &ResourceID) -> NodeResult<Self>;
    pub fn part(&self, relative_path: &str) -> NodeResult<ModelPart>;
}

impl Text {
    pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
                  text: &str, style: TextStyle, bounds: TextBounds) -> NodeResult<Self>;
}

impl Sound {
    pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
                  resource: &ResourceID) -> NodeResult<Self>;
}

impl Camera {
    pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
                  /* camera params */) -> NodeResult<Self>;
}
```

#### Fields (3D interaction volumes)

```rust
impl Field {
    pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
                  shape: FieldShape) -> NodeResult<Self>;
}

impl FieldRef {
    pub async fn import(client: &Arc<ClientHandle>, uid: u64) -> NodeResult<Self>;
}
```

#### Input

```rust
impl InputMethod {
    pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
                  datamap: Datamap) -> NodeResult<Self>;
}

impl InputHandler {
    pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
                  field: &impl FieldAspect, /* handler */) -> NodeResult<Self>;
}

// Hand tracking types
pub struct Hand { pub thumb: Thumb, pub index: Finger, ... }
pub struct Finger { pub tip: Joint, pub distal: Joint, ... }
impl Finger {
    pub fn length(&self) -> f32;
    pub fn direction(&self) -> Vector3<f32>;
}
```

#### Panel Items (2D UI surfaces)

```rust
impl PanelItemUi {
    pub fn register(client: &Arc<ClientHandle>) -> NodeResult<Self>;
}

impl PanelItemAcceptor {
    pub fn create(client: &Arc<ClientHandle>,
                  parent: &impl SpatialRefAspect,
                  field: &impl FieldAspect) -> NodeResult<Self>;
}

impl ClientHandle {
    pub async fn register_xkb_keymap(&self, keymap: String) -> NodeResult<u64>;
    pub async fn get_xkb_keymap(&self, keymap_id: u64) -> NodeResult<Keymap>;
}
```

#### Client State

```rust
impl ClientState {
    pub fn new<T: Serialize>(data: T, root: &impl SpatialRefAspect,
        spatial_anchors: FxHashMap<String, &impl SpatialRefAspect>) -> Result<Self>;
    pub fn from_root(root: &impl SpatialRefAspect) -> Result<Self>;
    pub fn data<T: DeserializeOwned>(&self) -> Option<T>;
    pub fn root(&self, client: &Arc<ClientHandle>) -> SpatialRef;
    pub fn spatial_anchors(&self, client: &Arc<ClientHandle>) -> FxHashMap<String, SpatialRef>;
}
```

### stardust-core/gluon — D-Bus Object Registry

```rust
pub struct ObjectRegistry { /* ... */ }

impl ObjectRegistry {
    pub async fn new(connection: &Connection) -> Arc<Self>;
    pub fn get_objects(&self, interface: &str) -> HashSet<ObjectInfo>;
    pub fn get_watch(&self) -> watch::Receiver<Objects>;
    pub fn query<Q: Queryable<Ctx>, Ctx: QueryContext>(
        self: &Arc<Self>, context: impl Into<Arc<Ctx>>) -> QueryStream<Q, Ctx>;
}

// D-Bus interfaces
pub trait SpatialRef { fn node(&self) -> u64; fn get_transform(...); fn set_transform(...); }
pub trait FieldRef { fn node(&self) -> u64; fn distance(...); fn normal(...); fn closest_point(...); }
pub trait PlaySpace { fn bounds(&self) -> Vec<(f64,f64)>; fn center(&self) -> (f64,f64,f64); }
pub trait Reparentable { fn reparent(&self, ...); }
pub trait Destroy { fn destroy(&self); }
```

### stardust-core/wire — Low-Level Protocol

```rust
pub async fn connect() -> Result<UnixStream, std::io::Error>;

pub struct Message { /* flatbuffers message */ }
pub struct MethodResponse { /* ... */ }
pub struct MessageSender { /* ... */ }
pub struct MessageReceiver { /* ... */ }

impl MessageSender {
    pub async fn flush(&mut self) -> Result<(), MessengerError>;
    pub async fn send(&mut self, message: Message) -> Result<(), MessengerError>;
}

// Flex serialization
pub fn serialize<S: Serialize>(value: &S) -> Result<(Vec<u8>, Vec<OwnedFd>), FlexSerializeError>;
pub fn deserialize<'a, T: Deserialize<'a>>(data: &'a [u8], fds: impl IntoIterator<Item=OwnedFd>) -> Result<T>;

// Value types
pub type Quaternion = mint::Quaternion<f32>;
pub type Mat4 = mint::ColumnMatrix4<f32>;
pub type Color = color::Rgba<f32, LinearRgb>;
```

### stardust-core/protocol — IDL Parser

```rust
pub struct Protocol { pub interfaces: Vec<Interface>, pub custom_structs: Vec<CustomStruct>, ... }

impl Protocol {
    pub fn parse(sbs: &str) -> Result<Self, ParseError>;
}

pub fn resolve_inherits(protocols: &mut [&mut Protocol]) -> Result<(), String>;
```

### stardust-flatland — Wayland Panel Manager

Manages Wayland toplevel windows as 3D panel items in StardustXR.

```rust
// Key public structs
pub struct ToplevelInner { /* manages a single Wayland toplevel */ }
impl ToplevelInner {
    pub fn create(panel_item: PanelItem, ...) -> Self;
    pub fn frame(&mut self, info: &FrameInfo);
    pub fn handle_events(&mut self, acceptors: &FxHashMap<...>);
    pub fn set_enabled(&mut self, enabled: bool);
}

// Panel wrapper builder
pub struct PanelWrapper<State: ValidState> { /* ... */ }
impl PanelWrapper {
    pub fn new(panel_item: PanelItem) -> Self;
    pub fn on_toplevel_title_changed(self, f: impl Fn(&mut State, String)) -> Self;
    pub fn on_toplevel_size_changed(self, f: impl Fn(&mut State, Vector2<u32>)) -> Self;
    pub fn on_toplevel_move_request(self, f: impl Fn(&mut State)) -> Self;
    pub fn on_set_cursor(self, f: impl Fn(&mut State, Geometry)) -> Self;
    pub fn on_create_child(self, f: impl Fn(&mut State, ChildInfo)) -> Self;
    // ... more event hooks
}

// Input planes
pub struct PointerPlane<State: ValidState> { /* ... */ }
impl PointerPlane {
    pub fn on_mouse_button(self, f: impl Fn(&mut State, u32, bool)) -> Self;
    pub fn on_pointer_motion(self, f: impl Fn(&mut State, Vector3<f32>)) -> Self;
    pub fn on_scroll(self, f: impl Fn(&mut State, MouseEvent)) -> Self;
}

pub struct TouchPlane<State: ValidState> { /* ... */ }
impl TouchPlane {
    pub fn on_touch_down(self, f: impl Fn(&mut State, u32, Vector3<f32>)) -> Self;
    pub fn on_touch_move(self, f: impl Fn(&mut State, u32, Vector3<f32>)) -> Self;
    pub fn on_touch_up(self, f: impl Fn(&mut State, u32)) -> Self;
}

// Grab ball (3D handle for moving panels)
pub struct GrabBall<H: GrabBallHead> { /* ... */ }
impl GrabBall {
    pub fn create(head: H, offset: impl Into<Vector3<f32>>, ...) -> Self;
    pub fn update(&mut self);
    pub fn pos(&self) -> &Vec3;
    pub fn set_enabled(&mut self, enabled: bool);
}

pub trait GrabBallHead {
    fn root(&self) -> &impl SpatialAspect;
}

// Resize handles
pub struct ResizeHandlesInner { /* ... */ }
impl ResizeHandlesInner {
    pub fn create(parent: &impl SpatialRefAspect, ...) -> Self;
    pub fn handle_events(&mut self);
    pub fn set_handle_positions(&mut self, panel_size: Vector2<f32>);
    pub fn set_enabled(&mut self, enabled: bool);
}

// Close/exposure button
pub struct ExposureButtonInner { /* ... */ }
impl ExposureButtonInner {
    pub fn new(parent: &impl SpatialRefAspect, ...) -> Self;
    pub fn frame(&mut self, frame_info: &FrameInfo, gain: f32) -> bool;
    pub fn set_enabled(&mut self, enabled: bool);
}
```

### stardust-protostar — App Launchers

```rust
// Application model
pub struct Application { /* desktop file wrapper */ }
impl Application {
    pub fn create(desktop_file: DesktopFile) -> Result<Self, NodeError>;
    pub fn name(&self) -> Option<&str>;
    pub fn categories(&self) -> &[String];
    pub fn icon(&self, preferred_px_size: u16, prefer_3d: bool) -> Option<Icon>;
    pub fn launch<T: SpatialRefAspect + Clone>(&self, launch_space: &T) -> NodeResult<()>;
}

// XDG Desktop file parser
pub struct DesktopFile { pub name: Option<String>, pub exec: Option<String>, ... }
impl DesktopFile {
    pub fn parse(path: PathBuf) -> Result<Self, String>;
    pub fn get_icon(&self, preferred_px_size: u16) -> Option<Icon>;
}

pub fn get_desktop_files() -> impl Iterator<Item = PathBuf>;

// Icon handling
pub struct Icon { pub path: PathBuf, pub icon_type: IconType, pub size: u16 }
impl Icon {
    pub fn from_path(path: PathBuf, size: u16) -> Option<Icon>;
    pub fn cached_process(self, size: u16) -> Result<Icon, std::io::Error>;
}

// Hexagon math (for hex-grid launcher)
pub struct Hex { q: isize, r: isize, s: isize }
impl Hex {
    pub fn new(q: isize, r: isize, s: isize) -> Self;
    pub fn get_coords(&self) -> [f32; 3];
    pub fn neighbor(self, direction: usize) -> Self;
    pub fn spiral(i: usize) -> Self;
}

// App launcher component
pub struct AppLauncher<State: ValidState>(Application, Box<dyn Fn(&mut State)>);
impl AppLauncher {
    pub fn new(app: &Application) -> Self;
    pub fn done<F: Fn(&mut State) + Send + Sync>(mut self, f: F) -> Self;
}
```

### stardust-server — Compositor Internals

Key server-side types (for compositor development):

```rust
// Node system
pub struct Node { /* scene graph node */ }
pub struct Scenegraph { /* node storage */ }
impl Scenegraph {
    pub fn add_node(&self, node: Node) -> Arc<Node>;
    pub fn get_node(&self, id: Id) -> Option<Arc<Node>>;
    pub fn remove_node(&self, id: Id);
}

// Client management
pub struct Client { /* connected client */ }
impl Client {
    pub fn from_connection(connection: UnixStream) -> Result<Arc<Self>>;
    pub fn generate_id(&self) -> Id;
    pub fn get_node(&self, name: &str, id: Id) -> Result<Arc<Node>>;
    pub fn disconnect(&self, reason: Result<()>);
    pub async fn save_state(&self) -> Option<ClientStateParsed>;
}

// Session persistence
pub async fn save_session(project_dirs: &ProjectDirs);
pub fn launch_start(cli_args: &CliArgs, project_dirs: &ProjectDirs) -> Vec<Child>;
pub fn restore_session(session_dir: &Path, debug: bool) -> Vec<Child>;

// Wayland implementation
pub struct Wayland { /* Wayland compositor */ }
impl Wayland {
    pub fn new() -> Result<Self>;
}

// Foundation types
pub struct Id(pub u64);
pub struct Registry<T: Send + Sync + ?Sized> { /* ... */ }
impl Registry<T> {
    pub fn add(&self, t: T) -> Arc<T>;
    pub fn get_valid_contents(&self) -> Vec<Arc<T>>;
    pub fn remove(&self, t: &T);
}

pub struct Delta<T> { /* change tracking */ }
impl Delta<T> {
    pub fn peek_delta(&self) -> Option<&T>;
    pub fn delta(&mut self) -> Option<&mut T>;
    pub fn mark_changed(&mut self);
}

// Method response
pub struct MethodResponseSender(MethodResponse);
impl MethodResponseSender {
    pub fn send<T: Serialize>(self, result: Result<T, ServerError>);
    pub fn wrap<T: Serialize, F: FnOnce() -> Result<T>>(self, f: F);
    pub fn wrap_async<T: Serialize>(self, f: impl Future<Output = Result<T>>);
}

// Codegen proc macros
pub fn codegen_root_protocol(_: TokenStream) -> TokenStream;
pub fn codegen_spatial_protocol(_: TokenStream) -> TokenStream;
pub fn codegen_field_protocol(_: TokenStream) -> TokenStream;
pub fn codegen_drawable_protocol(_: TokenStream) -> TokenStream;
pub fn codegen_input_protocol(_: TokenStream) -> TokenStream;
pub fn codegen_item_protocol(_: TokenStream) -> TokenStream;
pub fn codegen_camera_protocol(_: TokenStream) -> TokenStream;
```

---

## Cross-Reference: Which SDK for What

| Use Case | SDK/Repo | Language |
|----------|----------|----------|
| Write once, run on any glasses (Android) | xg-glass-sdk | Kotlin |
| Build cloud-connected glasses app | MentraOS SDK | TypeScript |
| Linux head tracking + virtual display | XRLinuxDriver | C |
| IMU sensor fusion (any platform) | Fusion | C/Python |
| AR web browser for glasses | TAPLINKX3 | Kotlin |
| PC desktop streaming to glasses | RayDesk | Kotlin |
| Windows head tracking for gaming | PhoenixHeadTracker | C# |
| Spatial XR compositor (Linux) | StardustXR | Rust |

---

*Generated from source analysis. Last updated: 2026-04-19.*
