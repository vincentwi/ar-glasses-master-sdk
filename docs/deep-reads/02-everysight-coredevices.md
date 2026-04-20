# DEEP ANALYSIS: Everysight Maverick SDK & CoreDevices Mobile App (libpebble3)

Generated: 2026-04-20

---

## PART 1: EVERYSIGHT MAVERICK SDK

Repository: /tmp/glasses-sdk-repos/sdk/
Size: ~465MB (mostly pre-compiled binaries and simulator executables)

### 1.1 Overview

The Everysight Maverick SDK is a development kit for building applications for Maverick AR smart glasses. The SDK itself is distributed as pre-compiled libraries (iOS xcframeworks + Android AAR/JAR) with NO source code for the core libraries. The repo contains:

- Pre-compiled iOS frameworks (EvsKit.xcframework, NativeEvsKit.xcframework)
- Pre-compiled Android libraries (EvsKit.aar, NativeEvsKit.jar)
- Python utility tools (image converter, font converter)
- Simulator binaries (Windows, macOS, Linux)
- Documentation/release notes

### 1.2 Architecture

```
Everysight Maverick SDK
├── libraries/
│   ├── 2.5.0/
│   │   ├── IOS/
│   │   │   ├── EvsKit.xcframework      (Main Swift SDK framework)
│   │   │   └── NativeEvsKit.xcframework (Kotlin/Native bridge)
│   │   └── Android/
│   │       ├── EvsKit.aar              (Main Android SDK)
│   │       └── NativeEvsKit.jar        (Native bridge)
│   └── docs/README.md                  (Release notes)
├── tools/
│   ├── simulator/                      (Maverick glasses simulator)
│   ├── image_convert/                  (Image optimization tool)
│   └── font2sif/                       (Font conversion tool)
└── README.md
```

### 1.3 SDK Versions

| Version | Date | Firmware | Status |
|---------|------|----------|--------|
| 2.6.1 | Oct 2025 | - | Latest (Maven/SPM only) |
| 2.6.0 | Nov 2024 | 121 | Stable (Maven/SPM) |
| 2.5.0 | Jul 2023 | 119 | Stable (manual download) |

From v2.6.0, libraries distributed via Maven (Android) and SPM (iOS).

### 1.4 Dependencies

#### iOS
- Swift 5.8.1+, iOS 14.0+
- CoreBluetooth, CoreMedia, Network, SwiftUI, UIKit, Combine
- NativeEvsKit (Kotlin/Native bridge)
- JSONWebToken (MIT), zlib

#### Android
- Kotlin 2.0.0+ (2.6.0), Kotlin 1.8.10 (2.5.0)
- AndroidX, Material components
- jjwt (Apache)

### 1.5 iOS Swift Interface API (from EvsKit.swiftinterface v2.5.0)

#### Protocols (Interfaces)

```swift
protocol IBleScanListener : IBtAdapterStateListener {
    func onScanStarted()
    func onScanStopped()
    func onScanFailed()
    func onPeripheralFound(deviceUuid: String, localName: String, rssi: NSNumber)
}

protocol IBtAdapterStateListener {
    func onBtStateChanged(state: CBManagerState)
}
```

#### Main Entry Point: Evs Class

```swift
class Evs {
    static func instance() -> NativeEvsKit.IEvsApp
    static func initOptions(options: [String: String]) throws
    static func startDefaultLogger()
    static func stopDefaultLogger()
    static func setLogger(logger: NativeEvsKit.IEvsLogger?)
    static func getLogger() -> NativeEvsKit.IEvsLogger?
}
```

#### BLEPeripheral (BLE Device Communication)

```swift
class BLEPeripheral : NSObject, NEKIBleDevice, IBtAdapterStateListener {
    var last_RSSI: Int
    var enableAutoConnect: Bool
    
    init(sensorsManager: EvsSensorsManager, peripheral: CBPeripheral)
    init(sensorsManager: EvsSensorsManager, idOrAddress: String?)
    
    func setDeviceInfo(id: String, name: String)
    func name() -> String
    func registerNotify(serviceUUID: String, charaUUID: String, listener: IEvsCommunicationChannelListener)
    func registerEvents(listener: IEvsCommunicationChannelListener) -> Int32
    func unregisterEvents(withId: Int32)
    func unregisterNotify(serviceUUID: String, charaUUID: String, listener: IEvsCommunicationChannelListener)
    func clearNotifications()
    func hasConsumers() -> Bool
    func connect() -> Bool
    func connectSecured() -> Bool
    func disconnect() -> Bool
    func getMtuSize() -> Int32
    func isAdapterEnabled() -> Bool
    func isConnected() -> Bool
    func isConnecting() -> Bool
    func requestBatteryRead(callback: @escaping (KotlinInt) -> Void) -> Bool
    func requestRssiRead(callback: @escaping (KotlinInt) -> Void) -> Bool
}
```

#### EvsSensorsManager (External Sensor BLE Management)

```swift
class EvsSensorsManager : NSObject {
    static let shared: EvsSensorsManager
    var TAG: String
    var HR_SERVICE: String
    var POWER_SERVICE: String
    var CADENCE_SPEED_SERVICE: String
    var CADENCE_SERVICE: String
    var SPEED_SERVICE: String
    var CONTROLLER_EVS_SERVICE: String
    var CONTROLLER_SENA_SERVICE: String
    var btPowerState: CBManagerState
    
    func isAdapterOn() -> Bool
    func retrievePeripherals(idOrAddress: String) -> CBPeripheral?
    func connectedDevice(device: BLEPeripheral) -> Bool
    func disconnectDevice(device: BLEPeripheral) -> Bool
    func addScanListener(_ listener: IBleScanListener) -> Int
    func removeScanListener(listenerId: Int)
    func addBtAdapterStateListener(_ listener: IBtAdapterStateListener) -> Int
    func removeBtAdapterStateListener(listenerId: Int)
    func isScanning() -> Bool
    func scan(service: String?)
    func stopScan()
}
```

#### BtScanner (Glasses-Specific BLE Scanner)

```swift
class BtScanner : NSObject {
    static let shared: BtScanner
    func scanForGlasses(bleScanListener: IBleScanListener?)
    func stopScan()
}
```

#### EvsSystemLogger

```swift
class EvsSystemLogger : NSObject, NEKIEvsSystemLogger {
    static let shared: EvsSystemLogger
    static func initSDKWithSystemLogger()
    static let LOGS_FOLDER: URL
    
    func terminate()
    func isDebug() -> Bool
    func setDebugMode(isDebug: Bool)
    func doInit(type: String, headers: KotlinArray<NSString>) -> IEvsLogger?
    func logger(type: String) -> IEvsLogger?
}
```

#### UI Components

```swift
struct ProgressBarView : Animatable, View {
    enum FillAxis { case horizontal, vertical }
    init(progress: Binding<Double>, icon: UIImage, foregroundColor: Color, 
         backgroundColor: Color, borderColor: Color, cornerRadius: CGFloat, fillAxis: FillAxis)
}

struct BackgroundBlurBlackView : UIViewRepresentable
```

#### Enums

```swift
enum OtaState { case none, uploading, installing, completed, failed }
```

#### BLE Service UUIDs

```swift
let serviceCBUUID: CBUUID
let charNotifyCBUUID: CBUUID
let charControlCBUUID: CBUUID
let charPairingCBUUID: CBUUID
```

#### Type Aliases

```swift
typealias SliderHandler = (_ value: Float) -> Void
typealias SwHandler = (_ state: Bool) -> Void
```

#### Data Structure: LinkedList<T>

```swift
final class LinkedList<T> {
    class LinkedListNode<T> { init(value: T) }
    final var last: Node?
    final var isEmpty: Bool
    final var count: Int
    subscript(index: Int) -> T
    func node(at index: Int) -> Node
    func append(_ value: T)
    func insert(_ value: T, at index: Int)
    func removeAll()
    func remove(node: Node) -> T
    func removeLast() -> T
    func reverse()
    func map<U>(transform: (T) -> U) -> LinkedList<U>
    func filter(predicate: (T) -> Bool) -> LinkedList<T>
}
```

### 1.6 SDK API (from Release Notes - v2.6.0/2.6.1)

#### Core Interfaces (Kotlin/Android - documented but binary-only)

| Interface | Description |
|-----------|-------------|
| IEvsApp | Main app interface, exposes auth, services |
| IEvsAppEvents | Callback: onUnReady |
| IEvsAuthService | Authentication with sdk.key |
| IEvsGlassesStateService | Glasses state (type property removed in 2.6.0) |
| IEvsScreenService | Exposes Viewport class |
| IEvsSensorsService | Sensor control (accelerometer, gyro, mag, fusion) |
| IEvsOtaService | OTA firmware updates |

#### UI Kit Classes

| Class | Description |
|-------|-------------|
| Screen | Inherits from Viewport; main display surface |
| ArScreen | AR content display screen |
| Viewport | Base class for Screen and ArScreen |
| Drawable | Base class for UIElement and ArModel |
| UIElement | Base HUD element, methods: addTo(), removeAfter(), getYBottom(), getXEnd() |
| Text | Text display element |
| TextBlock | Multiline text control (new in 2.6.0) |
| Font | Font resource with StockFont enum; methods: trimUncovered, countCharsCoverage |
| ImgSrc | Image source, can generate from text via TextParams |
| AutoLayout | Automatic layout manager |
| Column | Vertical layout |
| Row | Horizontal layout |
| Modifier | Properties modifier (padding, gravity, visibility) for AutoLayout children |

#### AR/LOS Classes (Beta, v2.6.0)

| Class | Description |
|-------|-------------|
| ArScreen | AR content screen |
| IArElement | Interface for AR-drawable elements |
| ArWindow | 2D UI board in 3D AR space |
| ArModel | Collection of 3D primitives for AR |
| ArPrimitive | 3D primitive (world coordinates) |
| ArLines | Lines in 3D space |
| ArPoints | Points in 3D space |
| ArTriangles | Triangles in 3D space |
| ArFactory | Helper: creates cubes, stars, arrows |
| BoundingSphere | 3D bounding sphere |
| M | Math utility (3x3/4x4 matrices, vectors, rotations) |
| Quaternion | Quaternion for 3D rotations |

#### Sensors API

| Method | Description |
|--------|-------------|
| enableInertialSensors | Enable all inertial sensors |
| enableGyro | Enable gyroscope |
| enableMagnetometer | Enable magnetometer |
| enableAccelerometer | Enable accelerometer |
| setSensorsRate | Override default sensor rate |
| getSensorsRate | Get current sensor rate |
| setUsePrediction | Enable prediction for LOS YPR/quaternion data |
| enableMagneticDeclinationCorrection | Correct for magnetic declination |
| registerYprSensorsEvents | Register for Yaw/Pitch/Roll events |
| registerQuaternionSensorsEvents | Register for quaternion events |

#### Data/Enums

| Type | Description |
|------|-------------|
| EvsColor | Color constants (Green, etc.) with rgba |
| Align | Text alignment (center, etc.) |
| ScreenRenderRate | Rendering rate options (namespace: UIKit.app.data) |
| ControllerAction | Controller action enum |
| AppErrorCode | Error codes including ActivationError |

### 1.7 Python Tools

#### evsimgconvert.py (Image Converter)

Purpose: Convert images to Maverick-optimized PNG with 332 color format (3-bit R, 3-bit G, 2-bit B).

```python
# Key Functions
def color2index_m332(color) -> int                    # RGB color to 332 index
def rgb2index_m332(color) -> int                      # RGB tuple to 332 index
def index2color_m332(index) -> list[int]              # 332 index to RGBA
def is_eeps_chunk_present(img: PngImageFile) -> bool  # Check if already optimized
def which(program) -> str|None                        # Find executable in PATH
def get_image_magick_convert_tool(tool) -> str|None   # Find ImageMagick
def get_optipng_tool(tool) -> str|None                # Find optipng
def convert(fn, out_fn, keep_alpha) -> bool|None      # Main conversion
def view(fn) -> None                                  # Display converted image
def convert_to_png(convert, src, dst) -> bool         # SVG to PNG via ImageMagick
def optipng(optipng, image) -> bool                   # Optimize PNG

# Classes
class Message:                                        # Logging format helper
    def __init__(self, fmt, args)
    def __str__(self) -> str

class StyleAdapter(logging.LoggerAdapter):            # Logging adapter
    def __init__(self, logger, extra=None)
    def log(self, level, msg, *args, **kwargs)
```

Requirements: Python 3.8.6+, Pillow 8.1.0+, optipng (optional), ImageMagick (optional for SVG)

#### conv_folder.py (Batch Converter)

```python
def main():  # Batch convert all PNG/JPG in a folder using evsimgconvert.py
```

#### font2sif.py (Font to SIF Converter)

Purpose: Convert TrueType/OpenType/WOF fonts to SIF (System Independent Font) format for embedded displays.

```python
# Key Functions
def range_parser(s) -> tuple[int,int]    # Parse hex range "0x0020:0x007E"
def char_parser(s) -> int               # Parse hex char "0x00AA"

# Key Arguments
--path   # Path to font file (required)
--size   # Pixel font size (default: 36)
--bpp    # Bits per pixel: 1, 2, or 4 (default: 2)
--ranges # Character ranges to include
--exclude # Characters to exclude
```

Requirements: Python 3.x, numpy, Pillow, freetype-py

Output files:
- .sifz (compressed SIF, for app resources)
- .json (metadata with char widths, for app resources)
- .sif (uncompressed, back-compat)
- .png (visual preview)

### 1.8 Simulator

Maverick Simulator emulates specific firmware versions. Available for:
- Windows x64 (Windows 10+)
- macOS ARM (Ventura+)
- Linux x86_64 (Ubuntu 20.04+)

Structure: Firmware[Version]/[SimVersion]/MaverickSim[FW].[platform]

### 1.9 Hello World Example (Kotlin)

```kotlin
class HelloDeveloperScreen : Screen() {
    override fun onCreate() {
        Text()
            .setText("Hello Developer")
            .setResource(Font.StockFont.Medium)
            .setTextAlign(Align.center)
            .setXY(getWidth()/2, getHeight()/2)
            .setForegroundColor(EvsColor.Green.rgba)
            .addTo(this)
    }
}
```

---

## PART 2: COREDEVICES MOBILE APP (libpebble3)

Repository: /tmp/glasses-sdk-repos/mobileapp/
Size: ~97MB
Project name: libpebble3 / CoreApp
License: GPLv3 (with Apple App Store MPL 2.0 exception)

### 2.1 Overview

A Kotlin Multiplatform (KMP) library and companion mobile app for interacting with Pebble smartwatches. This is the open-source Core Devices project (successor to Rebble) providing a full replacement Pebble companion app. It includes:

- **libpebble3**: Core KMP library for Pebble protocol, BLE communication, data sync
- **composeApp**: Cross-platform Compose Multiplatform mobile app (Android + iOS)
- **experimental**: Index ring support, AI agent, recording/transcription
- **pebble**: Pebble-specific UI screens and actions
- **index-ai**: AI/agent data models, Notion integration, recording entities
- **mcp**: Model Context Protocol client (tool calling framework)
- **util**: Shared utilities, transcription, platform abstractions
- **cactus**: (Small module)
- **resampler**: Audio resampling
- **krisp-stubs**: Noise cancellation stubs
- **blobdbgen**: KSP annotation processor for BlobDB
- **blobannotations**: Annotations for blobdbgen

### 2.2 Project Structure

```
libpebbleroot/
├── build.gradle.kts              (Root build config)
├── settings.gradle.kts           (Module includes)
├── libpebble3/                   (Core library - 422 .kt files)
│   ├── src/commonMain/           (Shared Kotlin code)
│   ├── src/androidMain/
│   ├── src/iosMain/
│   ├── src/jvmMain/
│   ├── src/jvmTest/
│   └── libpebble-swift/          (Swift bridge for iOS)
├── composeApp/                   (Mobile app - 53 .kt files)
│   ├── src/commonMain/
│   ├── src/androidMain/
│   └── src/iosMain/
├── experimental/                 (Ring/AI features - 257 .kt files)
│   ├── src/commonMain/
│   ├── src/androidMain/
│   └── src/iosMain/
├── pebble/                       (Pebble UI - 99 .kt files)
├── util/                         (Utilities - 133 .kt files)
├── index-ai/                     (AI data layer - 33 .kt files)
├── mcp/                          (MCP protocol - 12 .kt files)
├── resampler/                    (Audio - 1 .kt file)
├── cactus/                       (3 .kt files)
├── krisp-stubs/                  (1 .kt file)
├── blobdbgen/                    (KSP processor)
├── blobannotations/              (Annotations)
└── iosApp/                       (iOS Xcode project)
```

Total: ~1020 Kotlin source files

### 2.3 Build Configuration

- Kotlin Multiplatform targeting: Android, iOS (arm64, x64, simulatorArm64), JVM
- Compose Multiplatform for UI
- Gradle with version catalogs
- KSP for code generation (Room, BlobDB)
- CocoaPods for iOS dependencies
- Firebase (Auth, Firestore, Crashlytics, Storage, Messaging)
- Google Sign-In

#### Key Dependencies
- kotlinx-coroutines, kotlinx-serialization, kotlinx-datetime, kotlinx-io
- Koin (DI), Kermit (logging), Kable (BLE)
- Ktor (HTTP client/server, WebSockets)
- Room (database), SQLite
- Compose Material3, Navigation
- Firebase (auth, firestore, crashlytics, storage)
- Coil (image loading)

### 2.4 Module: libpebble3 (Core Library)

584 classes/interfaces in commonMain alone. Key subsystems:

#### 2.4.1 Connection Layer

```kotlin
// Core device abstractions
interface PebbleDevice                              // Base device
interface DiscoveredPebbleDevice : PebbleDevice     // Discovered via scan
interface BleDiscoveredPebbleDevice : DiscoveredPebbleDevice  // BLE-specific
interface KnownPebbleDevice : PebbleDevice          // Previously paired
interface ConnectingPebbleDevice : PebbleDevice, ActiveDevice
interface ConnectedPebbleDeviceInRecovery : CommonConnectedDevice
interface ActiveDevice                              // Has active connection

// Connection management
class WatchManager                                  // Manages watch connections
class RealPebbleConnector : PebbleConnector         // Connection orchestrator
interface TransportConnector                        // Transport-level connector
class PebbleDeviceFactory                           // Creates device instances
class RealScanning                                  // BLE scanning
class Negotiator                                    // Protocol negotiation

// Transport
interface PebbleIdentifier                          // Device identifier
data class PebbleSocketIdentifier(val address: String) : PebbleIdentifier
sealed class PlatformIdentifier                     // Platform-specific ID

// Connection state
enum class ConnectionFailureReason { ... }
sealed class PebbleConnectionResult { ... }
sealed class ConnectingPebbleState { ... }
data class ConnectionFailureInfo(...)
data class ConnectionException(...)

// BLE internals
sealed class PPoGPacket                             // PebbleProtocol-over-GATT packets
class PpogClient                                    // PPoG client
class PpogServer                                    // PPoG server
class GATTPacket                                    // GATT packet handling
data class BlePlatformConfig(...)                   // BLE config
```

#### 2.4.2 Protocol Layer

```kotlin
// Protocol handling
open class PebblePacket                             // Base packet class
enum class ProtocolEndpoint(val value: UShort)      // All protocol endpoints
object PacketRegistry                               // Packet type registry
interface PebbleProtocolHandler                     // Protocol message handler
class RealPebbleProtocolHandler(...)                // Implementation

// Struct mapping (binary protocol serialization)
abstract class Mappable(val endianness: Endian)
abstract class StructMappable : Mappable
class StructMapper : Mappable
open class StructElement<T>(...)
class SUByte, SByte, SUInt, SInt, SULong, SUShort, SShort
class SBoolean, SUUID, SUUIDList
class SString, SLongString, SFixedString, SNullTerminatedString
class SBytes, SUnboundBytes, SFixedList<T>, SOptional<T>
```

#### 2.4.3 Packet Types

```kotlin
// Phone/Watch Communication
sealed class PhoneControl(message, cookie) : PebblePacket
sealed class AppFetchIncomingPacket : PebblePacket
class AppFetchRequest : AppFetchIncomingPacket
class AppFetchResponse(...) : AppFetchOutgoingPacket
sealed class AppRunStateMessage(message) : PebblePacket

// Music Control
open class MusicControl(val message: Message) : PebblePacket

// Voice/Audio
sealed class IncomingVoicePacket : PebblePacket
sealed class OutgoingVoicePacket(command) : PebblePacket
class SessionSetupCommand : IncomingVoicePacket
class SessionSetupResult(sessionType, result) : OutgoingVoicePacket
class DictationResult(sessionId, result, attributes) : OutgoingVoicePacket
sealed class AudioStream(command, sessionId) : PebblePacket

// Data/System
sealed class DataLoggingIncomingPacket : PebblePacket
sealed class SystemPacket(endpoint) : PebblePacket
open class TimeMessage(message) : SystemPacket
open class WatchVersion(message) : SystemPacket
open class PhoneAppVersion(message) : SystemPacket
open class WatchFactoryData(message) : SystemPacket
open class SystemMessage(message) : SystemPacket
class BLEControl(opcode, discoverable, duration) : SystemPacket
open class PingPong(message, cookie) : SystemPacket

// BlobDB (key-value database sync)
open class BlobCommand(message, token, database) : PebblePacket
open class BlobResponse(response) : PebblePacket
sealed class BlobDB2Command(message, token) : PebblePacket
sealed class BlobDB2Response : PebblePacket
class TimelineItem(...)                             // Timeline entries
open class TimelineAction(message) : PebblePacket

// Screenshots
class ScreenshotRequest : PebblePacket
sealed class ScreenshotResponse : PebblePacket

// PutBytes (binary data transfer)
sealed class PutBytesOutgoingPacket(command) : PebblePacket
class PutBytesInit, PutBytesAppInit, PutBytesPut, PutBytesCommit, PutBytesAbort, PutBytesInstall

// Health
sealed class HealthSyncOutgoingPacket : PebblePacket
class HealthSyncIncomingPacket : PebblePacket

// App Messages (JS app communication)
class AppMessageTuple : StructMappable
sealed class AppMessage(message, transactionId) : PebblePacket
```

#### 2.4.4 Services Layer

```kotlin
interface ProtocolService                           // Base service interface

class SystemService(...)                            // System commands, time, version
class MusicService(...) : ProtocolService           // Music control
class PhoneControlService(...) : ProtocolService    // Phone call control
class AppFetchService(...) : ProtocolService        // App installation
class PutBytesService(...) : ProtocolService        // Binary data transfer
class AppRunStateService(...) : ProtocolService     // App lifecycle
class VoiceService(...) : ProtocolService           // Voice/dictation
class AudioStreamService(...) : ProtocolService     // Audio streaming
class ScreenshotService(...) : ProtocolService      // Screenshot capture
class DataLoggingService(...) : ProtocolService     // Data logging
class HealthService(...) : ProtocolService          // Health data sync
class GetBytesService(...) : ProtocolService        // Data retrieval
class LogDumpService(...) : ProtocolService         // Log retrieval
class AppLogService(...) : ProtocolService          // App logging
class AppReorderService(...) : ProtocolService      // App ordering
class AppMessageService(...) : ProtocolService      // JS app messaging
class BlobDBService(...) : ProtocolService          // BlobDB sync
class TimelineService(...) : ProtocolService        // Timeline management

// Data types
data class FirmwareVersion(...)
data class WatchInfo(...)
data class ScreenshotState { ... }
data class DataLoggingSession(...)
data class AppMessageData(...)
sealed class AppMessageResult(val transactionId: UByte)
```

#### 2.4.5 Endpoint Managers

```kotlin
class AppFetchProvider(...)                         // App fetch orchestration
class AppOrderManager(...)                          // App ordering
class CompanionAppLifecycleManager(...)             // Companion app lifecycle
class DebugPebbleProtocolSender(...)                // Debug protocol sender
class FirmwareUpdater(...)                          // Firmware update orchestration
class LanguagePackInstaller(...)                    // Language pack installation
class VoiceSessionManager(...)                      // Voice session management
class BlobDB(...)                                   // BlobDB manager
class MusicControlManager(...)                      // Music control manager
class PhoneControlManager(...)                      // Phone control manager
class PutBytesSession(...)                          // Binary transfer session
class TimelineActionManager(...)                    // Timeline action handler
```

#### 2.4.6 Database Layer

```kotlin
abstract class Database : RoomDatabase()            // Main Room database

// DAOs
interface KnownWatchDao                             // Known watches
interface LockerEntryRealDao : LockerEntryDao       // App locker
interface NotificationAppRealDao                    // Notification apps
interface TimelinePinRealDao                        // Timeline pins
interface TimelineNotificationRealDao               // Timeline notifications
interface TimelineReminderRealDao                   // Timeline reminders
interface WatchPrefRealDao                          // Watch preferences
interface HealthDao                                 // Health data
interface HealthSettingsEntryRealDao                // Health settings
interface CalendarDao                               // Calendar events
interface ContactDao                                // Contacts
interface NotificationDao                           // Notifications
interface NotificationRuleDao                       // Notification rules
interface VibePatternDao                            // Vibration patterns
interface WeatherAppRealDao                         // Weather apps
interface LockerAppPermissionDao                    // App permissions
interface BlobDbDao<T : BlobDbRecord>               // Generic BlobDB DAO

// Entities
data class KnownWatchItem(...)
data class LockerEntry(...)
data class NotificationAppItem(...)
data class TimelineNotification(...)
data class TimelinePin(...)
data class TimelineReminder(...)
data class WatchPrefItem(...)
data class HealthStat(...)
data class HealthDataEntity(...)
data class HealthSettingsEntry(...)
data class CalendarEntity(...)
data class ContactEntity(...)
data class NotificationEntity(...)
data class NotificationRuleEntity(...)
data class VibePatternEntity(...)
data class WeatherAppEntry(...)
data class AppPrefsEntry(...)
data class LockerAppPermission(...)
data class OverlayDataEntity(...)
```

#### 2.4.7 Other Subsystems

```kotlin
// Calendar sync
interface SystemCalendar
class PhoneCalendarSyncer(...)
data class CalendarEvent(...)

// Music control
interface SystemMusicControl
enum class MusicAction
enum class PlaybackState
data class PlayerInfo(...)
data class PlaybackStatus(...)

// Health
class Health(...)
data class HealthSettings(...)
data class StackedSleepData(...)
data class WeeklyAggregatedData(...)

// Contacts
interface SystemContacts
class PhoneContactsSyncer(...)
data class SystemContact(...)

// Locker (app store)
class Locker(...)
abstract class LockerPBWCache(...)
sealed class LockerWrapper

// Weather
class WeatherManager(...)
enum class WeatherType(val code: Byte)

// Voice/Transcription
interface TranscriptionProvider
sealed class TranscriptionResult
sealed class VoiceEncoderInfo
data class TranscriptionWord(...)

// Disk I/O
class PbwApp(private val path: Path)               // PBW app file handler
class PbzFirmware(private val path: Path)           // PBZ firmware file handler
class PbwBinHeader : StructMappable                 // PBW binary header

// Metadata
enum class WatchType(val codename: String)          // aplite, basalt, chalk, diorite, emery
enum class WatchHardwarePlatform(...)               // Hardware platform variants
enum class WatchColor(...)                          // Watch color options

// DI
class LibPebbleCoroutineScope(...) : CoroutineScope
class ConnectionCoroutineScope(...) : CoroutineScope
interface ConnectionScope
class RealConnectionScope(...)
interface ConnectionScopeFactory
data class PlatformConfig(...)
data class ConnectionScopeProperties(...)
fun initKoin(...)                                   // Koin DI initialization

// Config
data class LibPebbleConfig(...)
data class WatchConfig(...)
data class BleConfig(...)
data class NotificationConfig(...)

// PebbleKit compatibility
// PebbleKit Android 2 and Classic support via ContentProviders
```

### 2.5 Module: experimental (Index Ring + AI)

Namespace: coredevices.ring

#### 2.5.1 Ring Device Management

```kotlin
class ExperimentalDevices(...)                      // Ring device manager
class RingDelegate                                  // Platform-specific ring delegate
class RingAndroidDelegate                           // Android ring delegate
```

#### 2.5.2 AI Agent System

```kotlin
// Agent interfaces
interface Agent                                     // AI agent interface
interface ServletRepository                         // Tool/servlet repository

// Agent implementations
class AgentNenya(...)                               // Nenya cloud AI agent
class AgentCactus(...)                              // Cactus local AI agent
class AgentFactory : KoinComponent                  // Creates appropriate agent
enum class ChatMode                                 // Chat mode selection

// MCP (Model Context Protocol)
interface McpTool                                   // Tool interface
abstract class BuiltInMcpTool(...)                  // Built-in tool base
class RemoteMcpTool(...)                            // Remote HTTP MCP tool
interface McpIntegration                            // Integration interface
open class BuiltInMcpIntegration(name, tools)       // Built-in integration base
class HttpMcpIntegration(...)                       // HTTP-based MCP integration
class McpSession(...)                               // MCP session manager
class McpSessionFactory(...)                        // Session factory
class BuiltinServletRepository : ServletRepository  // Built-in tool repository

// Data structures
data class ToolDeclaration(...)
data class FunctionDeclaration(...)
data class FunctionDeclarationParameters(...)
data class FunctionDeclarationParameter(...)
data class FunctionCallArgs(...)
data class ToolCallResult(...)
sealed class SemanticResult
data class McpPrompt(...)
data class McpSessionTool(...)
```

#### 2.5.3 Built-in MCP Tools/Servlets

```kotlin
// Notes
class CreateNoteTool(...) : BuiltInMcpTool          // Create notes
class NoteServlet(createNoteTool) : BuiltInMcpIntegration
class NoteIntegrationFactory(...)                   // Note provider factory
class LocalNoteClient : NoteIntegration
enum class NoteProvider(val id, val title)           // Note providers

// Reminders
class ReminderTool : BuiltInMcpTool                 // Create reminders
class ListTool : BuiltInMcpTool                     // List reminders
object ReminderServlet : BuiltInMcpIntegration
class ReminderFactory(preferences)                  // Reminder provider factory
enum class ReminderProvider(val id, val title)

// Clock
class SetTimerTool : BuiltInMcpTool                 // Set timer
class SetAlarmTool : BuiltInMcpTool                 // Set alarm

// Messaging
object MessagingServlet : BuiltInMcpIntegration     // Beeper messaging
data class ApprovedBeeperContact(...)

// JavaScript
class EvaluateJSTool : BuiltInMcpTool               // JS evaluation
object JsServlet : BuiltInMcpIntegration
interface JsEngine                                  // JS engine interface

// Shortcuts
class ShortcutActionHandler(...)                    // Handle shortcut actions
```

#### 2.5.4 Integrations

```kotlin
interface Integration                               // Base integration
interface ReminderIntegration : Integration          // Reminder integration
interface NoteIntegration : Integration             // Note integration

class NotionIntegration(...)                        // Notion API integration
class GTasksIntegration(...)                        // Google Tasks integration
abstract class GoogleAPIIntegration(...)            // Google API base
class UIEmailIntegration : NoteIntegration          // Email integration
```

#### 2.5.5 Recording & Transcription

```kotlin
// Storage
class RecordingRepository(...)                      // Recording data access
class RingTransferRepository(...)                   // Ring transfer tracking
class RecordingProcessingTaskRepository(...)        // Processing task queue

// Audio
class M4AReader(source: Source) : AutoCloseable     // M4A file reader
sealed class PlaybackState                          // Audio playback state
sealed class MessagePlaybackState                   // Message playback state

// Database
abstract class RingDatabase : RoomDatabase()        // Ring-specific database
interface LocalReminderDao                          // Local reminders
interface RingTransferDao                           // Transfer records
interface TraceSessionDao                           // Trace sessions
interface CachedRecordingMetadataDao                // Cached metadata
interface RecordingProcessingTaskDao                // Processing tasks

// Encryption
class DocumentEncryptor(...)                        // E2E encryption
class KeyFingerprintMismatchException(...)
class TamperedException(message) : Exception
data class KeyResult(...)
data class StoredKeyEntry(...)
```

#### 2.5.6 UI (Compose)

```kotlin
// ViewModels
class FeedViewModel(...)                            // Recording feed
class RecordingDetailsViewModel(...)                // Recording details
class ListenDialogViewModel(...)                    // Listen dialog
class SettingsViewModel(...)                        // Ring settings
class NotesViewModel(...)                           // Notes/reminders
class ReminderDetailsViewModel(...)                 // Reminder details
class RecordingTraceTimelineViewModel(...)           // Trace timeline
class McpSandboxSettingsViewModel(...)              // MCP sandbox

// Navigation
object RingRoutes                                   // Ring navigation routes

// Preferences
interface Preferences                               // Settings interface
class PreferencesImpl(settings) : Preferences       // Implementation
enum class MusicControlMode(val id: Int)
enum class SecondaryMode(val id: Int)
```

### 2.6 Module: composeApp (Mobile App)

Namespace: coredevices.coreapp
Android package: coredevices.coreapp

#### Entry Points

```kotlin
// Android
class MainActivity : ComponentActivity()            // Android entry
class MainApplication : Application()               // Android Application

// iOS
object IOSDelegate : KoinComponent                  // iOS app delegate
object IOSDelegateShortcuts : KoinComponent          // iOS shortcuts

// Common
class CommonAppDelegate(...)                        // Shared app delegate
```

#### Key Classes

```kotlin
class CoreDeepLinkHandler                           // Deep link handling
class BugReportProcessor(...)                       // Bug report submission
class PushMessaging(...)                            // Push notification handling
class BugReportsService(...)                        // Bug report API
class BugApi(...)                                   // Bug report API client
class PushService(...)                              // Push token management
class OnboardingViewModel : ViewModel()             // Onboarding flow
class SyncWorker(...) : Worker                      // Background sync (Android)
class BugReportService : Service()                  // Bug report service (Android)
class FileLogWriter : LogWriter()                   // File-based logging
```

### 2.7 Module: pebble (Pebble UI)

```kotlin
// ViewModels
class ModelManagementScreenViewModel(...)
class AppStoreCollectionScreenViewModel(...)
class NotificationAppsScreenViewModel : ViewModel()
class ContactsViewModel(...)
class NotificationScreenViewModel : ViewModel()
class NotificationAppScreenViewModel : ViewModel()
class LockerAppViewModel(...)
class SharedLockerViewModel : ViewModel()
class NativeLockerAddUtil(...)

// Navigation
object PebbleRoutes
object PebbleNavBarRoutes
interface NavBarRoute
interface NavBarNav

// iOS Actions
interface PebbleAppActions
interface PebbleNotificationActions
interface PebbleQuietTimeActions
interface PebbleTimelineActions
interface PebbleWatchInfoActions
interface PebbleHealthActions
class IosPebbleAppActions(...)
class IosPebbleNotificationActions(...)
class IosPebbleQuietTimeActions(...)
class IosPebbleTimelineActions(...)
class IosPebbleWatchInfoActions(...)
class IosPebbleHealthActions(...)
```

### 2.8 Module: index-ai (AI Data Layer)

```kotlin
// Agent
interface Agent                                     // AI agent interface
interface ServletRepository                         // Servlet/tool repository

// Time parsing
class HumanDateTimeParser(...)                      // Natural language date/time
sealed class InterpretedDateTime
data class ParsedDateTimeResult(...)

// Database DAOs
interface HttpMcpServerDao
interface ConversationMessageDao
interface LocalRecordingDao
interface BuiltinMcpGroupAssociationDao
interface HttpMcpGroupAssociationDao
interface McpSandboxGroupDao
interface RecordingEntryDao

// Data entities
data class RecordingFeedItem(...)
data class LocalRecording(...)
data class RecordingEntryEntity(...)
data class RecordingDocument(...)
data class RecordingEntry(...)
data class AssistantSessionDocument(...)
data class ConversationMessageDocument(...)
data class ConversationMessageEntity(...)
data class MessageContentPart(...)
data class ContentInputAudio(...)
data class EncryptedEnvelope(...)
data class RingTransferInfo(...)
data class ToolCall(...)
data class FunctionToolCall(...)
data class ToolCallResponse(...)
data class ConversationToolCallResponse(...)

// Notion
data class NotionSearchResponse(...)
data class NotionSearchResult(...)
data class NotionBlock(...)
data class NotionRichText(...)
data class NotionParentInfo(...)
data class NotionErrorResponse(...)

// MCP Sandbox
data class HttpMcpGroupAssociation(...)
data class BuiltinMcpGroupAssociation(...)
data class McpSandboxGroupEntity(...)
data class HttpMcpServerEntity(...)
data class McpServerDefinition(...)

// OAuth
data class OAuthURLResponse(val url: String)
data class OAuthTokenResponse(...)

// Enums
enum class RecordingEntryStatus
enum class ContentPartType
enum class MessageRole
enum class NotionBlockType
```

### 2.9 Module: util (Shared Utilities)

```kotlin
// Platform abstraction
interface Platform
interface CompanionDevice
class IosCompanionDevice : CompanionDevice

// Config
data class CoreConfig(...)
class CoreConfigHolder(...)
class CoreConfigFlow(...)
enum class WeatherUnit(val code, val displayName)
data class STTConfig(...)

// Transcription
interface TranscriptionService
class WisprFlowTranscriptionService(...)
data class STTConversationMessage(...)
data class STTConversationContext(...)
enum class STTConvoRole

// Audio
enum class AudioEncoding
class KrispAudioProcessor : AutoCloseable

// Database
abstract class CoreDatabase : RoomDatabase()
data class HeartEntity(...)
data class MemfaultChunkEntity(...)
data class AppstoreCollection(...)
data class UserConfig(...)
data class HeartbeatStateEntity(...)
data class AppstoreSource(...)
data class WeatherLocationEntity(...)
data class AnalyticsHeartbeatEntity(...)

// UI
interface PebbleWebviewUrlInterceptor
interface PebbleWebviewNavigator
data class TopBarParams(...)
class SearchState
object CoreIcons
```

### 2.10 Module: mcp (Model Context Protocol)

```kotlin
interface McpTool {                                 // Tool interface
    val name: String
    val description: String
    val inputSchema: JsonObject
    suspend fun call(arguments: JsonObject): ToolCallResult
}

abstract class BuiltInMcpTool(
    override val name: String,
    override val description: String,
    inputType: KClass<*>
) : McpTool

interface McpIntegration {                          // Integration interface
    val name: String
    suspend fun listTools(): List<McpTool>
}

interface PromptProvider : McpIntegration {          // Prompt-providing integration
    suspend fun listPrompts(): List<McpPrompt>
}

class McpSession(...)                               // Session with tools
class RemoteMcpTool(...)                            // Remote tool proxy
open class BuiltInMcpIntegration(name, tools)       // Built-in integration
class HttpMcpIntegration(...)                       // HTTP MCP client
enum class HttpMcpProtocol                          // SSE vs StreamableHTTP

data class ToolCallResult(...)
sealed class SemanticResult
data class McpPrompt(...)
data class McpSessionTool(...)
```

### 2.11 Index Webhook API

The experimental module includes an Index Ring webhook API for sending recording data to HTTP endpoints:

```
POST <webhook URL>
Content-Type: multipart/form-data
X-Widget-Token: <auth token>
X-Audio-Size: <byte count>

Fields:
- audio: audio/mp4 (AAC-LC, mono, 16kHz) - conditional
- transcription: plain text - conditional
- recordedAt: Unix timestamp ms - always
- client: "ring" - always

Modes: Recording only | Transcription only | Both
```

---

## PART 3: EVERYSIGHT ONLINE DOCUMENTATION

Note: Direct web extraction from https://everysight.github.io/maverick_docs/ failed (unauthorized). Information reconstructed from SDK references and release notes.

### Documentation Structure (from README links)

1. **SDK Developer Portal**: https://everysight.github.io/maverick_docs/
2. **Libraries API Overview**: https://everysight.github.io/maverick_docs/libraries-api/overview/
3. **SDK Engine / Simulator**: https://everysight.github.io/maverick_docs/sdk-engine/simulator/
4. **UI Kit / Resources**: https://everysight.github.io/maverick_docs/ui-kit/resources/
5. **Samples Repository**: https://github.com/everysight-maverick/samples

### Getting Started Flow

1. Order Maverick Smart-glasses + developer key at www.everysight.com/developer
2. Read documentation at developer portal
3. Configure SDK libraries via Maven (Android) or SPM (iOS)
4. Use sdk.key for glasses communication authentication
5. Explore samples for iOS and Android

---

## PART 4: CROSS-REFERENCE & RELEVANCE TO GLASSES SDK

### Key Patterns for Smart Glasses Development

1. **BLE Communication**: Both repos use CoreBluetooth/BLE for device communication
   - Everysight: serviceCBUUID, charNotifyCBUUID, charControlCBUUID, charPairingCBUUID
   - CoreDevices: PPoG (Pebble Protocol over GATT), Kable library

2. **Protocol Abstraction**: Both use structured binary protocols
   - Everysight: NativeEvsKit bridge layer
   - CoreDevices: StructMapper/StructMappable binary serialization

3. **Screen/Display API**: Everysight has rich HUD rendering
   - Screen, ArScreen, UIElement, Text, TextBlock
   - Layout managers: AutoLayout, Column, Row

4. **Sensor Integration**: Everysight has comprehensive sensor APIs
   - Gyro, Accelerometer, Magnetometer, Inertial fusion
   - Line of Sight (LOS) for AR positioning

5. **OTA Updates**: Both support firmware updates
   - Everysight: IEvsOtaService, OtaState
   - CoreDevices: FirmwareUpdater, PutBytesService

6. **AI/Agent Architecture** (CoreDevices only):
   - MCP protocol for tool calling
   - Multiple agent backends (Nenya cloud, Cactus local)
   - Built-in tools: notes, reminders, messaging, JS eval, timers
   - Notion/Google Tasks integrations

7. **Voice/Audio Pipeline** (Both):
   - Everysight: No details in binary SDK
   - CoreDevices: VoiceService, AudioStreamService, TranscriptionService, Krisp noise cancellation

### Architecture Differences

| Aspect | Everysight Maverick | CoreDevices/libpebble3 |
|--------|-------------------|----------------------|
| Source | Closed (binary SDK) | Open source (GPLv3) |
| Language | Kotlin/Swift | Kotlin Multiplatform |
| Platform | iOS + Android | iOS + Android + JVM |
| Display | AR HUD (glasses) | E-ink (watch) |
| UI Framework | Custom (Screen/UIElement) | Compose Multiplatform |
| BLE Protocol | Custom (Evs protocol) | PPoG (Pebble protocol) |
| AI | None | MCP-based agent system |
| Distribution | Maven/SPM + manual | Source + Gradle |
