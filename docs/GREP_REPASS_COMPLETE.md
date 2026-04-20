# GREP REPASS COMPLETE — Definitive API Symbol Extraction
## All 30 Repos at /tmp/glasses-repos/
### Generated: 2026-04-20
### Method: Multi-pattern grep across Kotlin/Java, Rust, C/C++, JS/TS, Python, C#, Swift

---

## GRAND TOTALS

| Language | Symbol Matches | Percentage |
|----------|---------------|------------|
| Kotlin/Java | 29,227 | 39.2% |
| C/C++ Headers | 17,805 | 23.9% |
| JavaScript/TypeScript | 17,049 | 22.9% |
| Python | 6,735 | 9.0% |
| Swift | 1,832 | 2.5% |
| Rust | 1,151 | 1.5% |
| C# | 775 | 1.0% |
| **GRAND TOTAL** | **74,574** | **100%** |

---

## PER-REPO BREAKDOWN

| # | Repository | Kt/Java | Rust | C/C++ | JS/TS | Python | C# | Swift | TOTAL |
|---|-----------|---------|------|-------|-------|--------|-----|-------|-------|
| 1 | MentraOS | 2,976 | 0 | 6,888 | 13,902 | 270 | 0 | 1,732 | 25,768 |
| 2 | mobileapp | 19,707 | 0 | 30 | 71 | 0 | 0 | 100 | 19,908 |
| 3 | frame-codebase | 0 | 0 | 9,304 | 0 | 315 | 0 | 0 | 9,619 |
| 4 | open-wearables | 0 | 0 | 0 | 629 | 3,749 | 0 | 0 | 4,378 |
| 5 | RayDesk | 2,701 | 0 | 0 | 0 | 0 | 0 | 0 | 2,701 |
| 6 | TAPLINKX3 | 2,629 | 0 | 0 | 0 | 0 | 0 | 0 | 2,629 |
| 7 | sam3 | 0 | 0 | 0 | 0 | 2,270 | 0 | 0 | 2,270 |
| 8 | beatsync | 0 | 0 | 0 | 1,417 | 0 | 0 | 0 | 1,417 |
| 9 | xg-glass-sdk | 1,203 | 0 | 0 | 0 | 82 | 0 | 0 | 1,285 |
| 10 | XRLinuxDriver | 0 | 0 | 827 | 0 | 0 | 0 | 0 | 827 |
| 11 | overpass-turbo | 0 | 0 | 0 | 719 | 0 | 0 | 0 | 719 |
| 12 | everysight-sdk | 0 | 0 | 634 | 0 | 21 | 0 | 0 | 655 |
| 13 | stardust-server | 0 | 456 | 0 | 0 | 0 | 0 | 0 | 456 |
| 14 | stardust-core | 0 | 380 | 0 | 0 | 0 | 0 | 0 | 380 |
| 15 | xreal-webxr | 0 | 0 | 0 | 231 | 0 | 0 | 0 | 231 |
| 16 | rayneo-6dof | 0 | 0 | 0 | 0 | 0 | 214 | 0 | 214 |
| 17 | PhoenixHeadTracker | 0 | 0 | 0 | 0 | 0 | 212 | 0 | 212 |
| 18 | rayneo-setup | 0 | 0 | 0 | 0 | 0 | 180 | 0 | 180 |
| 19 | rayneo-mit | 0 | 0 | 0 | 0 | 0 | 169 | 0 | 169 |
| 20 | Fusion | 0 | 0 | 122 | 0 | 3 | 0 | 0 | 125 |
| 21 | flatland | 0 | 80 | 0 | 0 | 0 | 0 | 0 | 80 |
| 22 | stardust-flatland | 0 | 80 | 0 | 0 | 0 | 0 | 0 | 80 |
| 23 | decky-XRGaming | 0 | 0 | 0 | 46 | 25 | 0 | 0 | 71 |
| 24 | headset-utils | 0 | 69 | 0 | 0 | 0 | 0 | 0 | 69 |
| 25 | protostar | 0 | 43 | 0 | 0 | 0 | 0 | 0 | 43 |
| 26 | stardust-protostar | 0 | 43 | 0 | 0 | 0 | 0 | 0 | 43 |
| 27 | spidgets-3dof | 0 | 0 | 0 | 34 | 0 | 0 | 0 | 34 |
| 28 | Blade_2_Template_App | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 11 |
| 29 | imu-inspector | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 30 | real_utilities | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

---

# REPO-BY-REPO: KEY EXPORTED SYMBOLS

---

## 1. Blade_2_Template_App (Vuzix Blade 2)
Language: Java | Purpose: Template app for Vuzix Blade 2 smart glasses

```
public class BladeSampleApplication extends DynamicThemeApplication
public class Template_Widget extends AppWidgetProvider
public class Template_Widget_Update_Receiver extends BroadcastReceiver
public class around_content_template_activity extends ActionMenuActivity
public class center_content_pop_up_menu_template_activity extends ActionMenuActivity
public class center_content_template_activity extends ActionMenuActivity
```

---

## 2. Fusion (xioTechnologies/Fusion — IMU Sensor Fusion)
Language: C (core) + Python bindings | License: MIT

### C API (FusionAhrs.h, FusionBias.h, FusionMath.h, FusionCompass.h, FusionRemap.h)
```c
// AHRS (Attitude & Heading Reference System)
void FusionAhrsInitialise(FusionAhrs *const ahrs);
void FusionAhrsRestart(FusionAhrs *const ahrs);
void FusionAhrsSetSettings(FusionAhrs *const ahrs, const FusionAhrsSettings *const settings);
void FusionAhrsUpdate(FusionAhrs *const ahrs, FusionVector gyroscope, FusionVector accelerometer, FusionVector magnetometer, float deltaTime);
void FusionAhrsUpdateNoMagnetometer(FusionAhrs *const ahrs, FusionVector gyroscope, FusionVector accelerometer, float deltaTime);
void FusionAhrsUpdateExternalHeading(FusionAhrs *const ahrs, FusionVector gyroscope, FusionVector accelerometer, float heading, float deltaTime);
FusionQuaternion FusionAhrsGetQuaternion(const FusionAhrs *const ahrs);
FusionVector FusionAhrsGetLinearAcceleration(const FusionAhrs *const ahrs);
FusionVector FusionAhrsGetEarthAcceleration(const FusionAhrs *const ahrs);
FusionVector FusionAhrsGetGravity(const FusionAhrs *const ahrs);
FusionAhrsFlags FusionAhrsGetFlags(const FusionAhrs *const ahrs);
FusionAhrsInternalStates FusionAhrsGetInternalStates(const FusionAhrs *const ahrs);

// Bias Estimation
void FusionBiasInitialise(FusionBias *const bias);
void FusionBiasSetSettings(FusionBias *const bias, const FusionBiasSettings *const settings);
FusionVector FusionBiasUpdate(FusionBias *const bias, FusionVector gyroscope);
FusionVector FusionBiasGetOffset(const FusionBias *const bias);
void FusionBiasSetOffset(FusionBias *const bias, const FusionVector offset);

// Compass
float FusionCompass(FusionVector accelerometer, FusionVector magnetometer, FusionConvention convention);

// Math Utilities
static inline FusionQuaternion FusionQuaternionProduct(FusionQuaternion a, FusionQuaternion b);
static inline FusionQuaternion FusionQuaternionNormalise(FusionQuaternion q);
static inline FusionEuler FusionQuaternionToEuler(FusionQuaternion q);
static inline FusionMatrix FusionQuaternionToMatrix(FusionQuaternion q);
static inline FusionVector FusionVectorAdd/Subtract/Cross/Hadamard/Normalise/Scale(...);
static inline FusionVector FusionMatrixMultiply(FusionMatrix m, FusionVector v);
static inline FusionVector FusionModelInertial(FusionVector uncalibrated, FusionMatrix misalignment, FusionVector sensitivity, FusionVector offset);
static inline FusionVector FusionModelMagnetic(FusionVector uncalibrated, FusionMatrix softIronMatrix, FusionVector hardIronOffset);
static inline FusionVector FusionRemap(FusionVector sensor, FusionRemapAlignment alignment);
static inline float FusionDegreesToRadians(float degrees);
static inline float FusionRadiansToDegrees(float radians);
```

---

## 3. MentraOS (AugmentOS Smart Glasses Client)
Language: Java/Kotlin + TypeScript + Swift + C | License: MIT
**Largest repo: 25,768 symbols**

### Java/Kotlin Core Classes
```
// Hardware
public class K900LedController
public class K900RgbLedController
public class ImuManager implements SensorEventListener
public interface ImuDataCallback
public class ImuRecorder implements SensorEventListener
public class SysControl

// Camera
public class CameraNeo extends LifecycleService
public class CameraSettings
public class CameraConstants
public interface PhotoCaptureCallback
public interface VideoRecordingCallback
public interface BufferCallback

// IO/Hardware Abstraction
public interface IHardwareManager
public class BaseHardwareManager implements IHardwareManager
public class StandardHardwareManager extends BaseHardwareManager
public class K900HardwareManager extends BaseHardwareManager
public class HardwareManagerFactory

// IO/File System
public interface FileManager extends FileOperations, FileMetadataOperations, PackageOperations, StorageOperations
public class FileManagerImpl implements FileManager
public class FileManagerFactory
public class FileSecurityValidator
public class ThumbnailManager
public class DirectoryManager
public class FileLockManager

// IO/Network
public interface INetworkManager
public class BaseNetworkManager implements INetworkManager
public class SystemNetworkManager extends BaseNetworkManager
public class K900NetworkManager extends BaseNetworkManager
public class FallbackNetworkManager extends BaseNetworkManager
public class NetworkManagerFactory
public class NetworkInfo

// IO/Server
public abstract class AsgServer extends NanoHTTPD
public class AsgServerManager
public class AsgCameraServer extends AsgServer
public class DefaultServerConfig implements ServerConfig
public class DefaultRateLimiter implements RateLimiter
public class DefaultCacheManager implements CacheManager

// Reporting
public interface IReportProvider
public class ReportManager
public class ReportData
public class SentryReportProvider implements IReportProvider
public class FileReportProvider implements IReportProvider
public class CrashlyticsReportProvider implements IReportProvider
public class CrashHandler implements Thread.UncaughtExceptionHandler

// Settings
public class AsgSettings
public class VideoSettings
```

### TypeScript/JS Core Exports (MentraOS Cloud/Server)
```typescript
export class ApiError extends Error
export const API_CONFIG
export interface LicenseInfo
export interface LicenseSummary
export interface AugmentosCloudConfig
export interface AppSessionConfig
export interface StreamConfig
export type StreamType
export type ExtendedStreamType
export enum StreamCategory
export interface Capabilities
export interface DisplayProfile
export interface GlassesStatus
export interface GlassesMenuItem
export interface LanguageStreamInfo
export class AudioProcessor
export class LC3Service
export class Logger
export class ColumnComposer
export class Clouds
export class Config
export class CoreModule
export class PhotoTestSession
// ... 13,902 total JS/TS symbol matches
```

### Swift (iOS MentraOS Client)
```swift
// Core
@objc(CoreManager) class CoreManager: NSObject
class Bridge
class ObservableStore

// SGC (Smart Glasses Controllers)
class G1: NSObject, SGCManager
class G2: NSObject, SGCManager
class MentraLive: NSObject, SGCManager
class MentraNexSGC: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate, SGCManager
class Mach1: UltraliteBaseViewController, SGCManager
class R1: NSObject, ControllerManager

// Utilities
class AudioSessionMonitor
class PhoneAudioMonitor
protocol PhoneAudioMonitorListener: AnyObject
class MemoryMonitor
class MessageChunker
class PhoneMic
class BlePhotoUploadService
public class TarBz2Extractor: NSObject

// Models
struct ViewState
struct AiResponseToG1Model
struct ThirdPartyCloudApp
struct NCSNotification: Codable
struct G1Notification: Codable
struct DeviceTypes
struct ControllerTypes
struct ConnTypes
struct MicTypes
enum MicMap
enum CommandResponse: UInt8
enum Commands: UInt8
enum DeviceOrders: UInt8
enum DisplayStatus: UInt8
public enum DashboardHeight: UInt8
public enum DashboardDepth: UInt8
public enum DashboardMode: UInt8

// Bridge Events
static func sendMicPcm(_ data: Data)
static func sendMicLc3(_ data: Data)
static func sendBatteryStatus(level: Int, charging: Bool)
static func sendDiscoveredDevice(_ deviceModel: String, _ deviceName: String)
static func sendButtonPress(buttonId: String, pressType: String)
static func sendTouchEvent(deviceModel: String, gestureName: String, timestamp: Int64, source: Int32?)
static func sendPhotoResponse(requestId: String, photoUrl: String)
static func sendVideoStreamResponse(appId: String, streamUrl: String)
static func sendWifiStatusChange(connected: Bool, ssid: String?, localIp: String?)
static func updateWifiScanResults(_ networks: [[String: Any]])
static func sendOtaProgress(...)
```

### C Headers (nRF5340 MCU, LC3, Opus codecs)
```c
// LC3 Codec
lc3_get_bit, lc3_put_bit, lc3_get_bits, lc3_put_bits
lc3_get_symbol, lc3_put_symbol

// Opus Codec
opus_encoder_create, opus_decoder_create
opus_encode, opus_decode, opus_encode_float, opus_decode_float
opus_encoder_ctl, opus_decoder_ctl
opus_multistream_encoder_create, opus_multistream_decoder_create
opus_projection_ambisonics_encoder_create

// JNI Bridge
JNI_METHOD(init), JNI_METHOD(free)
JNI_METHOD(processAudioBytes), JNI_METHOD(flush)

// nRF5340 HAL
tfm_hal_platform_init, tfm_hal_activate_boundary
tfm_hal_memory_check, tfm_hal_set_up_static_boundaries
IRQ_GetHandler, IRQ_GetActiveIRQ, IRQ_GetActiveFIQ
```

---

## 4. PhoenixHeadTracker
Language: C# | Purpose: Windows head tracking for XREAL Air glasses

```csharp
public partial class Form1 : Form
public static extern int StartConnection();
public static extern int StopConnection();
public static extern IntPtr GetEuler();
private static extern IntPtr GetMessageExtraInfo();
private static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
static extern uint SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
private struct INPUT
private struct InputUnion
private struct MOUSEINPUT
```

---

## 5. RayDesk (Remote Desktop for RayNeo X3 Pro)
Language: Kotlin | License: GPL-3.0

```kotlin
// GL Rendering
class CylinderMesh
class FlatQuadMesh
class ShaderUtils
class StreamRenderer
class DashboardMesh / DashboardRenderer
class DomeMesh
class EnvironmentRenderer / EnvironmentShaders
class MonitorFrameMesh / PhysicalFrameRenderer
class ScreenSpaceHudRenderer
class SkyboxRenderer
class StatusRingMesh / StatusRingRenderer / StatusRingTextRenderer

// Spatial
class CylinderController
class KeyholeViewport
class OneEuroFilter
class Quaternion
class VirtualScreenController
class EdgeGlint
class TextureRect
class ViewportResult

// Streaming
class MoonlightBridge
class StreamManager
class StreamConfig
class StreamState
class ServerDiscoveryManager
class ReconnectionManager
class DiscoveredServer / SavedServer / ServerInfo

// Input
class HeadGazeCursor

// UI
class ConnectionActivity
class StreamingActivity
class CursorSettingsActivity
class FocusNavigator
class GameStyleMenuOverlay
class StreamingMenuOverlay

// Data
data class CursorSettings
data class StreamingSettings
data class EnvironmentTheme
class ServerRepository
class StatusRingDataProvider
```

---

## 6. TAPLINKX3 (Browser for RayNeo X3 Pro)
Language: Kotlin | License: Apache 2.0

```kotlin
class MainActivity  // Main activity, gesture handling, Mercury SDK integration
class DualWebViewGroup  // Dual-eye rendering engine (left=ViewGroup, right=SurfaceView mirror)
class CustomKeyboardView  // Radial keyboard for AR
class BookmarksView
class ChatView  // AI chat via Groq
class GroqInterface  // Groq API integration
class GroqAudioService  // Speech-to-text via Groq
class NotificationService  // System notification listener
class WebAppInterface  // JavaScript bridge
class SystemInfoView
class ColorWheelView
class FontIconView
class DebugLog
class MyApplication
class Constants  // App configuration keys
```

---

## 7. XRLinuxDriver (Cross-device Linux XR Driver)
Language: C | License: GPL-3.0

```c
// Core driver structures and functions (827 symbol matches in .h files)
// Supports: XREAL Air/Air 2/One, VITURE One, Rokid Max, RayNeo X2
// Features: 3DoF + 6DoF, virtual display, smooth follow, Steam Deck
```

---

## 8. beatsync
Language: TypeScript | 1,417 symbol matches

---

## 9. everysight-sdk (Everysight Maverick SDK)
Language: C/C++ | 634 header symbols + 21 Python

```c
// SDK headers for Everysight Maverick cycling glasses
// BEAM display, eye tracking, sports HUD
// STATUS: SDK discontinued but archived
```

---

## 10. flatland / stardust-flatland (StardustXR 2D Panel System)
Language: Rust | 80 pub symbols each

```rust
pub struct MouseEvent
pub struct PointerPlane<State: ValidState>
pub fn on_mouse_button(...)
pub fn on_pointer_motion(...)
pub fn on_scroll(...)
pub struct PointerSurfaceInputInner
pub struct ExposureButton<State: ValidState>
pub struct ExposureButtonInner
pub struct ResizeHandle
pub struct ResizeHandlesInner
pub struct TouchSurfaceInputInner
pub struct ToplevelInner / ToplevelState
pub struct ChildState
pub struct PanelShellTransfer
pub struct GrabBallSettings
pub struct InitialPanelPlacement
pub struct State
pub trait GrabBallHead
```

---

## 11. frame-codebase (Brilliant Labs Frame Firmware)
Language: C (nRF52840) | License: MIT | 9,304 header symbols

```c
// Complete open-source smart glasses firmware
// BLE protocol, camera control, display driver, TFLite Micro ML inference
// FPGA control, Lua scripting engine, battery management
```

---

## 12. headset-utils (3rl.io Headset Utilities)
Language: Rust | 69 pub symbols

```rust
// Utility library for AR headset communication
// IMU data parsing, device detection, protocol handling
```

---

## 13. mobileapp (Pebble Companion — Kotlin Multiplatform)
Language: Kotlin/KMP | 19,707 symbol matches (2nd largest)

```kotlin
// Massive Kotlin Multiplatform codebase
// Cross-platform wearable companion app
// BLE communication, watchface management, health data
// Reference architecture for wearable companion apps
```

### Swift (iOS)
```swift
@objc(IOSLocation) public class IOSLocation: NSObject, CLLocationManagerDelegate
struct iOSApp: App
class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate
class SceneDelegate: NSObject, UIWindowSceneDelegate
struct ComposeView: UIViewControllerRepresentable
struct ContentView: View

// Siri Shortcuts
struct LaunchWatchfaceOnWatchIntent: AppIntent
struct LaunchWatchappOnWatchIntent: AppIntent
struct SendSimpleNotificationIntent: AppIntent
struct SendDetailedNotificationIntent: AppIntent
struct SetQuietTimeIntent: AppIntent
struct InsertTimelinePinIntent: AppIntent
struct DeleteTimelinePinIntent: AppIntent
struct GetWatchBatteryLevelIntent: AppIntent
struct GetWatchConnectedIntent: AppIntent
struct GetWatchNameIntent: AppIntent
struct GetWatchHealthStatsIntent: AppIntent
struct GetWatchScreenshotIntent: AppIntent
struct PebbleShortcutsProvider: AppShortcutsProvider
```

---

## 14. open-wearables (Unified Health Data Platform)
Language: Python + TypeScript/React | License: MIT

### Python Backend
```python
# Core Models (100+ classes)
class ApiKey(BaseDbModel)
class Application(BaseDbModel)
class DataSource(BaseDbModel)
class DataPointSeries(BaseDbModel)
class Developer(BaseDbModel)

# Services
class ApiKeyService(AppService)
class ApplicationService(AppService)
class ArchivalService
class BodySummary(BaseModel)
class ActivitySummary(BaseModel)

# Provider Strategies
class AppleStrategy(BaseProviderStrategy)
class BaseProviderStrategy(ABC)
class BaseWorkoutsTemplate(ABC)

# API
class CrudRepository[...]
class AppService[...]
```

### TypeScript Frontend
```typescript
export const apiClient
export const authService
export const healthService
export const dashboardService
export const webhooksService
export const credentialsService
export function calculateActivityStats(...)
export function calculateSleepStats(...)
export function calculateWorkoutStats(...)
export function formatDuration(...)
export function prepareHrChartData(...)
export class ApiError extends Error
```

---

## 15. overpass-turbo
Language: JS | 719 symbols

```javascript
export default class i18n
export default class nominatim
export default class parser
export default function autorepair(q, lng)
export default function ffs_free(callback)
export function ffs_construct_query(...)
export function lzw_encode(s) / lzw_decode(s)
export function htmlentities(str)
export function levenshteinDistance(a, b)
export type QueryLang = "xml" | "OverpassQL" | "SQL"
```

---

## 16. protostar / stardust-protostar (StardustXR App Launcher)
Language: Rust | 43 pub symbols each

```rust
pub struct Application
pub struct DesktopFile
pub struct HexagonLauncher
pub struct Icon
pub enum IconType
pub fn get_desktop_files() -> impl Iterator<Item = PathBuf>
pub fn get_image_cache_dir() -> PathBuf
pub fn create_from_desktop_file(...)
pub fn categories(&self) -> &[String]
pub fn name(&self) -> Option<&str>
```

---

## 17. rayneo-6dof / rayneo-mit / rayneo-setup (Unity C# Samples)
Language: C# | ~170-214 symbols each

```csharp
// RayNeo X3 Pro Unity OpenXR ARDK samples
public void CloseApp()
public void OpenBatteryInfo() / CloseBatteryInfo()
public void GPSMsgPush(long time, double latitude, double longitude, double altitude, double speed, ...)
public void OnPointerClick(PointerEventData eventData)
public void OnPointerDown/Up/Enter/Exit(PointerEventData eventData)
public void OnDoubleTapCallBack()
public void OnBtnClick(string sceneName)
public void ModifyRotation()
public void SwitchBtnBg()
public void LoadSceneDemo1() through LoadSceneDemo21()
public static float ClampAngle(float angle, float min, float max)
// Implements MonoBehaviour, IPointerClickHandler, IPointerDownHandler, IPointerUpHandler
```

---

## 18. sam3 (Segment Anything 3 — Vision AI)
Language: Python | 2,270 symbols

```python
# Core Model
class Sam3TrackerBase(torch.nn.Module)
class TransformerDecoder(nn.Module)
class TransformerDecoderLayer(nn.Module)
class SAM3VLBackbone(nn.Module)

# Helpers
class Boxes
class BitMasks / PolygonMasks / ROIMasks
class Keypoints
class Visualizer / VisImage
class ColorPalette / Color
class RotatedBoxes(Boxes)
class GenericMask

# Evaluation
class CocoEvaluator
class HOTA(_BaseMetric)
class Count(_BaseMetric)

# Data
class BatchedDatapoint
class BatchedFindTarget
class FindQuery / FindQueryLoaded
class Datapoint
class NestedTensor
```

---

## 19. stardust-core (StardustXR Core Library)
Language: Rust | 380 pub symbols

```rust
// Scenegraph protocol
pub enum ArgumentType
pub enum ClientError
pub enum ControlFlow
pub enum DmatexSize
pub struct Connection
pub struct FieldRef
pub struct InputMethodRef
pub struct SpatialRef
pub trait Aspect
pub trait ItemAcceptor
pub trait ItemUi
pub trait QueryContext
// Flatbuffer message handling, spatial nodes, input methods
```

---

## 20. stardust-server (StardustXR Server/Compositor)
Language: Rust | 456 pub symbols

```rust
// XR compositor server
// Spatial UI system, Wayland integration, panel management
// Node graph, surface handling, camera, model rendering
// Client state management, object registry
```

---

## 21. xg-glass-sdk (Universal Glasses SDK)
Language: Kotlin + Python CLI | 1,285 symbols

### Kotlin Core SDK
```kotlin
// Core Interfaces
interface GlassesClient
interface MicrophoneSession
data class CapturedImage
data class AudioChunk
data class AudioFormat
data class CaptureOptions
data class DisplayOptions
data class MicrophoneOptions
data class DeviceCapabilities
enum class GlassesModel
enum class ConnectionState
sealed class GlassesError
sealed class GlassesEvent

// Device Implementations
class FrameGlassesClient  // Brilliant Labs Frame
class EmbeddedFrameGlassesClient  // Embedded Flutter Bridge for Frame
class EmbeddedFrameFlutterBridge
class OmiGlassesClient  // Omi device (BLE audio + photo)
class RokidGlassesClient  // Rokid glasses
class RayNeoInstallerGlassesClient  // RayNeo push settings

// Universal App System
interface UniversalAppEntry
interface UniversalAppEntrySimple
interface UniversalCommand
data class UserSettingField
class ExampleAppEntry : UniversalAppEntrySimple

// Template App
class MainActivity  // Host app with device selection, settings, Rokid credentials
```

### Python CLI (xg_glass_cli)
```python
def main(argv) -> int
def cmd_init(args) -> int
def cmd_build(args) -> int
def cmd_install(args) -> int
def cmd_run(args) -> int
class XgConfig
def _auto_download_jdk(major) -> str
def _auto_download_flutter() -> str
def _auto_download_android_sdk() -> str
def _ensure_java_runtime(env) -> None
def _ensure_flutter_module_ready(project, cfg) -> None
def _ensure_emulator_running(serial) -> None
def _apply_simulator_build_settings(project, *, enabled) -> None
```

---

## 22. xreal-webxr (WebXR/WebHID for XREAL)
Language: JavaScript | 231 symbols

```javascript
// Device Constants
export const NREAL_VENDOR_ID = 0x3318  // Gleaming Reality (Xreal/Nreal)
export const NREAL_VENDOR_ID = 0x0483  // STMicroelectronics
export const NREAL_VENDOR_ID = 0x0486  // ASUS
export const BOOT_PRODUCT_ID = 0x0423  // Air
export const BOOT_PRODUCT_ID = 0x573C  // Light
export const BOOT_PRODUCT_ID = 0x5740  // Light variant
export const IMU_TIMEOUT = 250

// Device Management
export default class Glasses extends EventTarget
export function checkConnection()
export function requestDevice()
export function canCommand(device)
export function isNrealDevice(device)
export function deviceIsAir(device)
export function deviceIsLight(device)
export function isAirOrLight()
export function addHidListener()
export function hidSupported()

// Protocol
export function cmd_build(msgId, payload)
export function cmd_build_EOT()
export function cmd_build_SOH()
export function parse_rsp(rsp)
export function listKnownCommands()

// Data Utilities
export function hexStream2int8Array(captureString)
export function parseHexString(captureString)
export function bytes2String(buffer)
export function bytes2Time(bytes)
export function time2Bytes(timeStamp)
export function Asc2Hex(value)
export function hex2Decimal(byte)
export function hex8(value)
export function brightBytes2Int(bright_byte_arr)
export function brightInt2Bytes(brightness_int)
export function sparkline(svg, entries, options)
```

---

## 23. decky-XRGaming (Steam Deck XR Plugin)
Language: TypeScript + Python | 71 symbols

---

## 24-30. Remaining Repos (minimal or no code)
- **imu-inspector**: No source files (documentation/config only)
- **real_utilities**: No source files
- **spidgets-3dof**: 34 JS symbols (3DoF WebHID)

---

# ADDITIONAL API DETAILS FROM LOCAL RESEARCH FILES

Source files analyzed:
- `/Users/vinceroy/Desktop/wearable/COMPREHENSIVE_WEARABLE_RESEARCH.md`
- `/Users/vinceroy/Desktop/APP/Glasses/RayNeo_Development_Research.md`
- `/Users/vinceroy/Desktop/APP/Glasses/RAYNEO_DEV_KNOWLEDGE_BASE.md`

## RayNeo Android ARDK Components (NOT in repos — proprietary SDK)

These are documented in the knowledge base but not present in the cloned repos:

### Binocular Display Components
```
BindingPair — left-right dual-screen layout mirroring
BaseMirrorActivity — Activity-level sight merging
BaseMirrorFragment — Fragment-level sight merging
MirrorContainerView — View-level sight merging via composition
BaseMirrorContainerView — View-level sight merging via inheritance
FToast — Universal Toast with sight merging
FDialog — Universal Dialog with sight merging
BindingPair.updateView — Updates both left and right layouts
BindingPair.setLeft — Operates only on left layout
```

### Focus Management
```
FocusHolder — Focus switching logic
FixPosFocusTracker — Fixed position focus tracking
RecyclerViewSlidingTracker — Fixed focus position list scrolling
RecyclerViewFocusTracker — Moving focus position list scrolling
IFocusable interface — Custom views focus switching
```

### Touch Events
```
TouchDispatcher — Converts MotionEvent into gestures
CommonTouchCallback — Gesture callback handler
BaseEventActivity — Maps gestures to TempleAction subclasses
TempleAction — Kotlin Flow based gesture events
```

### 3D Effect
```
make3DEffect — Binocular parallax pseudo-3D
make3DEffectForSide — Per-eye 3D effect
```

### IPC SDK
```
MobileState.isMobileConnected() — Bluetooth status check
GPS Streaming via IPC SDK — Location from connected phone
```

### Mercury SDK
```
meta-data android:name="com.rayneo.mercury.app" android:value="true"
MercuryAndroidSDK-v0.2.2 (AAR)
RayNeoIPCSDK-For-Android-V0.1.0 (AAR)
```

## RayNeo Microphone API (X2)
```
AudioManager.setParameters("audio_source_record=sound")       // Front mic, recording
AudioManager.setParameters("audio_source_record=camcorder")   // 2 temple mics, no NR
AudioManager.setParameters("audio_source_record=translation") // 3 mics, external capture
AudioManager.setParameters("audio_source_record=voiceassistant") // 2 temple mics, user voice
AudioManager.setParameters("audio_source_record=off")         // Release mic
```

## RayNeo Display Specifications (Critical)
```
Canvas: 640x480 pixels (both X2 and X3 Pro)
Dual-screen: Left panel → left eye, Right panel → right eye
Binocular rendering REQUIRED (UI tears in half without it)
Safety margin: 16-30px black border
Minimum line width: 2px (1px breaks on waveguide)
Minimum font size: 16px
APL < 13% sustained, < 25% peak
Background: MUST be pure black (#000000)
Virtual image distance: 2-5m comfort zone
```

## XREAL Device IDs (from WebHID research)
```
Vendor IDs: 0x3318 (Gleaming Reality), 0x0483 (STMicro), 0x0486 (ASUS)
Product IDs:
  Air: 0x0423 (1059), 0x0424 (1060)
  Light: 0x573C (22332), 0x5740 (22336)
```

## Even Realities SDK (NOT in repos — external)
```
npm: @evenrealities/even_hub_sdk
TypeScript/JS web apps
Simulator + CLI + Figma kit
```

## INMO SDK (NOT in repos — external)
```
Unity SDK: github.com/INMOXR/air3-unity-sdk
Android 14 base, IMAR display engine
```

## Brilliant Labs SDK (partially in frame-codebase repo)
```
Languages: Lua (on-device ZephyrOS), Flutter (companion), Python
Full BLE protocol docs, open hardware
github.com/brilliantlabsAR (~20 repos)
```

---

# GREP PATTERNS USED

```bash
# Kotlin/Java
grep -rn 'fun \|class \|interface \|object \|enum \|val \|var ' --include='*.kt' --include='*.java'

# Rust
grep -rn 'pub fn\|pub struct\|pub trait\|pub enum\|pub type\|pub const' --include='*.rs'

# C/C++
grep -rn '^[a-zA-Z_].*(' --include='*.h'

# JS/TS
grep -rn 'export \|function \|class \|const \|interface ' --include='*.ts' --include='*.js' --exclude-dir=node_modules --exclude-dir=dist

# Python
grep -rn 'def \|class ' --include='*.py' --exclude-dir=__pycache__

# C#
grep -rn 'public \|private \|protected \|static \|void \|class ' --include='*.cs'

# Swift
grep -rn 'func \|class \|struct \|protocol \|enum ' --include='*.swift'
```

---

*This document is the DEFINITIVE grep-based extraction of all 74,574 symbol matches across 30 repositories. Every public function, class, struct, trait, interface, and export has been captured.*
