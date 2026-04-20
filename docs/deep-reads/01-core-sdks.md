# DEEP-wave1a-core-sdks: Comprehensive SDK Analysis

Generated: 2026-04-20

---

## 1. xg-glass-sdk (HKUST SPARK Lab — Cross-Device Glasses SDK)

### Architecture

xg.glass is a Kotlin/Android SDK that provides a unified API for smart glasses app development across multiple hardware platforms. It abstracts away vendor-specific SDKs behind a common `GlassesClient` interface.

**Module Structure:**
```
xg-glass-sdk/
├── core/                       # Core API interfaces and models
├── app-contract/               # App entry-point contract (reflection-based)
├── devices/
│   ├── device-frame-embedded/  # Brilliant Labs Frame (embedded Flutter)
│   ├── device-frame-flutter/   # Frame Flutter bridge contract
│   ├── device-meta/            # Meta AI Wearables (DAT SDK)
│   ├── device-omi/             # Omi Glass (BLE audio)
│   ├── device-rokid/           # Rokid Glasses (CXR-M SDK)
│   ├── device-rayneo-installer/ # RayNeo phone-side (ADB installer)
│   ├── device-rayneo-runtime/  # RayNeo on-glasses (Camera2 + AudioTrack)
│   └── device-simulator/       # Simulator (Android Emulator + CameraX)
├── build-logic/                # Gradle convention plugins
├── templates/kotlin-app/       # Template project for `xg-glass init`
├── third_party/frame/frame_module/ # Flutter module for Frame BLE
└── tools/xg_glass_cli/         # Python CLI (`xg-glass` command)
```

**Design Pattern:** Interface-based abstraction with device-specific implementations. Apps program against `GlassesClient` and `UniversalAppEntry`; the host app selects a device backend at runtime.

**Supported Devices:** Rokid Glasses, Meta AI Wearables, Brilliant Labs Frame, RayNeo x2/x3 Pro, Omi Glass, Simulator

**Entry Points:**
- CLI: `xg-glass` (Python) — `tools/xg_glass_cli/cli.py` → `main()`
- Android Host: `templates/kotlin-app/app/.../MainActivity.kt`
- App Logic: Developer implements `UniversalAppEntry` / `UniversalAppEntrySimple`

### All Classes/Functions (Full Signatures)

#### core/ — Core API

**`interface GlassesClient`** (GlassesClient.kt)
- `val model: GlassesModel`
- `val capabilities: DeviceCapabilities`
- `val state: StateFlow<ConnectionState>`
- `val events: Flow<GlassesEvent>`
- `suspend fun connect(): Result<Unit>`
- `suspend fun disconnect()`
- `suspend fun capturePhoto(options: CaptureOptions = CaptureOptions()): Result<CapturedImage>`
- `suspend fun display(text: String, options: DisplayOptions = DisplayOptions()): Result<Unit>`
- `suspend fun playAudio(source: AudioSource, options: PlayAudioOptions = PlayAudioOptions()): Result<Unit>`
- `suspend fun startMicrophone(options: MicrophoneOptions = MicrophoneOptions()): Result<MicrophoneSession>`

**`enum class GlassesModel`** — FRAME, META, ROKID, RAYNEO, SIMULATOR, OMI

**`data class DeviceCapabilities`**
- canCapturePhoto: Boolean, canDisplayText: Boolean, canRecordAudio: Boolean
- canPlayTts: Boolean, canPlayAudioBytes: Boolean, supportsTapEvents: Boolean, supportsStreamingTextUpdates: Boolean

**`data class CaptureOptions`** — quality: Int?, targetWidth: Int?, targetHeight: Int?, timeoutMs: Long

**`enum class DisplayMode`** — REPLACE, APPEND

**`data class DisplayOptions`** — mode: DisplayMode, force: Boolean

**`data class CapturedImage`** — jpegBytes: ByteArray, timestampMs: Long, width: Int?, height: Int?, rotationDegrees: Int?, sourceModel: GlassesModel

**`sealed class ConnectionState`** — Disconnected, Connecting, Connected, Error(error: GlassesError)

**`sealed class GlassesEvent`** — Log(message: String), Warning(message: String), Tap(count: Int)

**`sealed class GlassesError`** — NotConnected, PermissionDenied, Busy, Timeout(operation: String), Transport(detail: String, raw: Throwable?), Unsupported(detail: String)

**`enum class AudioEncoding`** — PCM_S16_LE, PCM_S8, OPUS

**`sealed class AudioSource`** — Tts(text: String), RawBytes(data: ByteArray, pcmFormat: PcmFormat?)

**`data class PcmFormat`** — sampleRateHz: Int, channelCount: Int, encoding: AudioEncoding

**`data class PlayAudioOptions`** — speechRate: Float?, interrupt: Boolean

**`data class AudioFormat`** — encoding: AudioEncoding, sampleRateHz: Int?, channelCount: Int?

**`data class AudioChunk`** — bytes: ByteArray, format: AudioFormat, sequence: Long, timestampMs: Long, endOfStream: Boolean

**`data class MicrophoneOptions`** — preferredEncoding: AudioEncoding, preferredSampleRateHz: Int?, preferredChannelCount: Int?, vendorMode: String?

**`interface MicrophoneSession`**
- `val format: AudioFormat`
- `val audio: Flow<AudioChunk>`
- `suspend fun stop()`

**`fun interface ExternalActivityBridge`** — `suspend fun launch(intent: Intent): ExternalActivityResult`

**`data class ExternalActivityResult`** — resultCode: Int, data: Intent?

#### app-contract/ — App Entry Contract

**`enum class HostKind`** — PHONE, GLASSES

**`data class HostEnvironment`** — hostKind: HostKind, model: GlassesModel

**`enum class UserSettingInputType`** — TEXT, PASSWORD, URL, NUMBER

**`data class UserSettingField`** — key: String, label: String, hint: String, defaultValue: String, inputType: UserSettingInputType

**`object AIApiSettings`**
- `fun fields(defaultBaseUrl: String, defaultModel: String, defaultApiKey: String): List<UserSettingField>`
- `fun baseUrl(settings: Map<String, String>): String`
- `fun model(settings: Map<String, String>): String`
- `fun apiKey(settings: Map<String, String>): String`

**`data class UniversalAppContext`** — environment: HostEnvironment, client: GlassesClient, scope: CoroutineScope?, log: (String)->Unit, onCapturedImage: ((CapturedImage)->Unit)?, settings: Map<String, String>

**`interface UniversalCommand`**
- `val id: String`, `val title: String`
- `suspend fun run(ctx: UniversalAppContext): Result<Unit>`

**`interface UniversalAppEntry`**
- `val id: String`, `val displayName: String`
- `fun commands(env: HostEnvironment): List<UniversalCommand>`
- `fun userSettings(): List<UserSettingField>`

**`interface UniversalAppEntrySimple : UniversalAppEntry`**
- `fun commands(): List<UniversalCommand>`

**`object UniversalCommandPolicy`**
- `fun filterCommands(env: HostEnvironment, commands: List<UniversalCommand>): List<UniversalCommand>`

**`fun UniversalAppEntry.commandsWithDefaults(env: HostEnvironment): List<UniversalCommand>`**

#### Device Implementations

**`class RokidGlassesClient(activity, options): GlassesClient`** — Full implementation using Rokid CXR-M SDK. BLE scan + Wi-Fi P2P for photo sync. Supports TTS via `CxrApi.sendGlobalTtsContent()`, raw PCM playback, mic via `openAudioRecord()`.
- Nested: `data class RokidOptions`, `data class RokidAuthorization`

**`class MetaWearablesGlassesClient(activity, externalActivityBridge?, options): GlassesClient`** — Uses Meta DAT SDK for camera. Mic via Bluetooth HFP AudioRecord. Speaker via AudioTrack/MediaPlayer to A2DP/BLE output.
- Nested: `data class MetaWearablesOptions`

**`class OmiGlassesClient(context): GlassesClient`** — BLE GATT connection to Omi devices. Audio via OPUS notifications on AUDIO_DATA_UUID. Photo capture via 0x05 command + PHOTO_DATA_UUID notifications.
- Private: `interface OmiMicrophoneSession : MicrophoneSession` with `fun emitAudio(data: ByteArray)`

**`class FrameGlassesClient(bridge: FrameFlutterBridge): GlassesClient`** — Delegates to Flutter via FrameFlutterBridge. No speaker support.

**`interface FrameFlutterBridge`** — Contract for host app to bridge to embedded Flutter module.

**`class EmbeddedFrameGlassesClient(context): GlassesClient by FrameGlassesClient(...)`** — One-line constructor; auto-starts embedded Flutter engine.

**`class EmbeddedFrameFlutterBridge(context): FrameFlutterBridge`** — Manages FlutterEngine lifecycle, MethodChannel communication.

**`object FrameFlutterChannelContract`** — Constants for METHOD_CHANNEL name, method names, arg keys, event types.

**`class RayNeoInstallerGlassesClient(context, config): GlassesClient`** — Phone-side: pushes APK to glasses via ADB-over-TCP. `connect()` = install APK.
- `suspend fun pushUserSettings(settings: Map<String, String>): Result<Unit>`
- Nested: `data class RayNeoInstallerConfig`, `sealed interface RayNeoApkSource`, private `class AdbRemoteInstaller`, `object SyncProtocol`, `object ShellProtocol`

**`class RayNeoRuntimeGlassesClient(context, displaySink): GlassesClient`** — On-glasses: Camera2 for photos, AudioRecord for mic, AudioTrack/MediaPlayer for playback.
- `fun interface RayNeoDisplaySink` — `suspend fun display(context, text, options)`
- `class ToastDisplaySink : RayNeoDisplaySink`

**`class SimulatorGlassesClient(activity, displaySink?, videoPath?): GlassesClient`** — CameraX or MediaMetadataRetriever (video looping). TTS via Android TextToSpeech. Mic via AudioRecord.

**`internal class RokidDisplayController(minUpdateIntervalMs)`** — Throttled Custom View text renderer for Rokid.
- `fun showText(text: String, force: Boolean)`
- `fun close()`

**`class SimDisplayActivity : AppCompatActivity`** — Simple text display activity for simulator.
- `companion object { fun newIntent(context, text): Intent }`

#### Flutter Module (Dart)

**`class UniversalFrameBridge`** (universal_frame_bridge.dart)
- Singleton: `static final instance`
- `void start()` — registers MethodChannel handler
- Private: `_connect()`, `_disconnect()`, `_capturePhoto(Map? args) -> Uint8List`, `_displayText(Map? args)`, `_startMicrophone(Map? args) -> Map<String, dynamic>`, `_stopMicrophone()`
- Uses `frame_ble` (BrilliantBluetooth) and `frame_msg` (RxPhoto, RxTap, TxCaptureSettings, TxPlainText)

#### Build Logic (Kotlin)

**`internal fun CommonExtension.applyUniversalGlassesAndroidDefaults()`** — compileSdk=34, minSdk=28

**Gradle Plugins:** `UniversalGlassesAndroidApplicationPlugin`, `UniversalGlassesAndroidLibraryPlugin`, `UniversalGlassesRayneoAppPlugin`, `UniversalGlassesRayneoSettingsPlugin`

#### CLI (Python)

**`cli.py`** — ~2200 lines
- `def main(argv) -> int` — argparse CLI entry
- Commands: `cmd_init(args)`, `cmd_build(args)`, `cmd_install(args)`, `cmd_run(args)`
- `@dataclass class XgConfig` — sdk_path, entry_class, rayneo_mercury_aar_dir, variant, module, application_id
- Auto-bootstrap: `_ensure_java_runtime()`, `_auto_download_jdk()`, `_auto_download_flutter()`, `_auto_download_android_sdk()`, `_resolve_android_sdk()`, `_ensure_emulator_running()`
- Video support: `_download_video_from_url()`, `_push_video_to_device()`, `_resolve_sim_video()`
- Env persistence: `_persist_env_macos_zshrc()`, `_persist_env_windows()`

### Dependencies

- Kotlin + Coroutines + Flow (kotlinx.coroutines)
- Android SDK 28+ (compileSdk 34)
- Rokid CXR-M SDK (com.rokid.cxr.client)
- Meta DAT SDK (com.meta.wearable.dat) — optional, requires GitHub Packages token
- Flutter (embedded via frame_module) — for Frame device
- frame_ble, frame_msg (Flutter packages) — Frame BLE communication
- adblib (com.tananaev.adblib) — ADB-over-TCP for RayNeo
- CameraX — Simulator camera
- Gson — Rokid display JSON
- Python 3.x — CLI tool
- yt-dlp — optional, for video URL download in sim mode

### Usage Examples

```bash
# Quick run a single Kotlin file
xg-glass run /path/to/MyEntry.kt

# Simulator mode with video
xg-glass run --sim --video_url https://youtube.com/... /path/to/MyEntry.kt

# Full project workflow
xg-glass init /path/to/myapp
cd /path/to/myapp
xg-glass build
xg-glass install
xg-glass run
```

---

## 2. MentraOS (Open Source Smart Glasses Operating System)

### Architecture

MentraOS is a **monorepo** providing an end-to-end operating system for smart glasses. The architecture is:
- **Smart Glasses** → BLE → **Phone App** → WebSocket → **Cloud Backend** → WebSocket → **Third-party App Servers (SDK)**

**Module Structure (key directories):**
```
MentraOS/
├── asg_client/          # Android-based smart glasses client (Java, 150+ files)
│   └── app/src/main/java/com/mentra/asg_client/
│       ├── AsgClientApplication.java   # Application entry
│       ├── AsgClientService.java       # Core foreground service
│       ├── io/bluetooth/               # BLE managers (K900, Nordic, Standard)
│       ├── io/network/                 # WiFi/network management
│       ├── io/media/                   # Camera, video buffer, upload
│       ├── io/streaming/              # RTMP, SRT, WHIP streaming
│       ├── io/server/                 # HTTP server on glasses
│       ├── io/ota/                    # OTA update system
│       ├── io/bes/                    # BES chip OTA protocol
│       ├── service/core/handlers/     # Command handlers (20+ types)
│       └── reporting/                 # Sentry/Crashlytics/File reporting
├── mobile/              # React Native (Expo) phone app
│   ├── modules/core/    # Native modules (Android Java + iOS Swift)
│   │   ├── android/     # CoreModule.java — BLE, display, transcription
│   │   ├── ios/Source/  # CoreManager.swift, SGCManager, G1, G2, Mach1...
│   │   └── src/         # TypeScript types & module interface
│   ├── modules/crust/   # Camera/video native module
│   ├── src/services/    # SocketComms, RestComms, Composer, Livekit, STT...
│   ├── src/stores/      # Zustand stores (glasses, connection, applets, settings)
│   └── webview/sdk/     # WebView bridge SDK for mini-apps
├── cloud/               # Backend services (TypeScript/Bun)
│   ├── packages/cloud/  # Express + WebSocket server
│   ├── packages/sdk/    # TypeScript SDK for third-party apps
│   ├── packages/types/  # Shared type definitions
│   ├── packages/utils/  # Logger, LLM provider, PostHog
│   ├── packages/agents/ # Built-in agents (Mira, News, Notifications)
│   ├── packages/apps/   # First-party apps using SDK
│   └── websites/        # Developer Console + App Store frontends
├── android_core/        # Shared Android library
├── mcu_client/          # MCU firmware tooling (protobuf)
└── docs/                # Architecture docs
```

**Supported Glasses:** Even Realities G1/G2, Mentra Mach 1, Mentra Live, Simulated

### All Classes/Functions (Key Signatures)

#### asg_client/ — Glasses-Side Android Client

**`class AsgClientApplication extends Application`**
- `void onCreate()` — Installs CrashHandler, initializes AppModule, ReportingModule
- `static AsgClientApplication getInstance()`
- `ReportManager getReportManager()`

**`class AsgClientService extends Service implements NetworkStateListener, BluetoothStateListener`**
- Core foreground service (1593 lines)
- Uses SOLID architecture with ServiceContainer DI
- Managers: IServiceLifecycle, ICommunicationManager, IConfigurationManager, IStateManager, IMediaManager
- `CommandProcessor` dispatches to 20+ command handlers

**Command Handlers (service/core/handlers/):**
- AuthTokenCommandHandler, BaseMediaCommandHandler, BatteryCommandHandler, BleConfigCommandHandler
- GalleryCommandHandler, GalleryModeCommandHandler, I2SAudioCommandHandler, ImuCommandHandler
- K900CommandHandler, KeepAwakeCommandHandler, MicrophoneCommandHandler, OtaCommandHandler
- PhoneReadyCommandHandler, PhotoCommandHandler, PingCommandHandler + more

**I/O Layer:**
- `interface IBluetoothManager` / `BaseBluetoothManager` / `K900BluetoothManager` / `NordicBluetoothManager` / `StandardBluetoothManager`
- `interface INetworkManager` / `SystemNetworkManager` / `K900NetworkManager` / `FallbackNetworkManager`
- `interface IHardwareManager` / `K900HardwareManager` / `StandardHardwareManager`
- `class FileManager` / `FileManagerImpl` / `FileOperationsManager` / `FileLockManager` / `FileSecurityManager`
- `class MediaCaptureService` / `CircularVideoBuffer` / `MediaUploadQueueManager` / `PhotoQueueManager`
- `interface IStreamingService` / `RtmpStreamingService` / `SrtStreamingService` / `WhipStreamingService`
- `class AsgServer` / `AsgServerManager` / `AsgCameraServer`
- `class OtaService` / `OtaHelper` / `BesOtaManager` (BES chip firmware update protocol)

**Reporting:**
- `class ReportManager` / `interface IReportProvider`
- Providers: `SentryReportProvider`, `CrashlyticsReportProvider`, `FileReportProvider`, `ConsoleReportProvider`

#### mobile/ — Phone App (React Native + Expo)

**TypeScript Module Interface (`CoreModule.ts`):**
- `getGlassesStatus(): GlassesStatus`
- `getCoreStatus(): CoreStatus`
- `displayEvent(params)`, `displayText(params)`, `clearDisplay()`
- `connectDefault()`, `connectByName(deviceName)`, `connectSimulated()`, `disconnect()`, `forget()`
- `findCompatibleDevices(deviceModel)`, `ping()`
- `requestWifiScan()`, `sendWifiCredentials(ssid, password)`, `setHotspotState(enabled)`
- `photoRequest(requestId, appId, size, webhookUrl, authToken, compress, flash, sound)`
- `startBufferRecording()`, `stopBufferRecording()`, `saveBufferVideo(requestId, durationSeconds)`
- `startVideoRecording(requestId, save, flash, sound)`, `stopVideoRecording(requestId)`
- `startStream(params)`, `stopStream()`, `keepStreamAlive(params)`
- `setMicState(sendPcmData, sendTranscript, bypassVad)`, `restartTranscriber()`
- `getGlassesMediaVolume()`, `setGlassesMediaVolume(level)`
- `rgbLedControl(requestId, packageName, action, color, ...)`

**Core Event Types (`Core.types.ts`):**
- GlassesNotReadyEvent, ButtonPressEvent, TouchEvent, HeadUpEvent, BatteryStatusEvent
- LocalTranscriptionEvent, LogEvent, WifiStatusChangeEvent, HotspotStatusChangeEvent
- PhotoResponseEvent, GalleryStatusEvent, GlassesMediaVolumeGetResult/SetResult

**iOS Native (Swift):**
- `CoreManager.swift` — Main bridge manager
- `SGCManager.swift` — Smart Glasses Connection manager
- Device drivers: `G1.swift`, `G2.swift`, `Mach1.swift`, `MentraLive.swift`, `MentraNex.swift`, `Frame.swift`, `Simulated.swift`
- `SherpaOnnxTranscriber.swift` — On-device speech-to-text
- `PhoneMic.swift` — Phone microphone capture
- VAD: `SileroVAD.swift`, `SileroVADStrategy.swift`

**Services (TypeScript):**
- `SocketComms.ts` — WebSocket communication with cloud
- `RestComms.ts` — REST API client
- `Composer.ts` — Display composition engine
- `DisplayProcessor.ts` — Display content processing
- `MantleManager.ts` — Core service orchestrator
- `Livekit.ts` — LiveKit streaming integration
- `STTModelManager.ts` — Speech-to-text model management
- `UdpManager.ts`, `UdpCrypto.ts` — UDP audio transport
- `WebSocketManager.ts`, `MiniSockets.ts`, `MiniComms.ts` — WebSocket variants

**Stores (Zustand):**
- `glasses.ts`, `connection.ts`, `core.ts`, `applets.ts`, `settings.ts`, `display.ts`, `debug.ts`, `gallerySync.ts`

#### cloud/ — Backend

**Key Packages:**
- `packages/cloud` — Express + WebSocket server, session management
- `packages/sdk` — TypeScript SDK for building MentraOS apps
- `packages/types` — Shared types including device capabilities per model
- `packages/utils` — Logger, LLMProvider, PostHog analytics

**Device Capabilities (cloud/packages/types/src/capabilities/):**
- `even-realities-g1.ts`, `even-realities-g2.ts`, `mentra-live.ts`, `mentra-display.ts`
- `vuzix-z100.ts`, `simulated-glasses.ts`, `none.ts`

### Dependencies

**asg_client:** Android SDK, EventBus (greenrobot), Hilt/Dagger (DI), Sentry, Firebase Crashlytics, OkHttp, protobuf, WebRTC (WHIP streaming), librtmp (RTMP), Camera2, MediaRecorder
**mobile:** React Native, Expo, expo-router, Zustand, react-native-ble-plx, livekit-client, sherpa-onnx (on-device STT), react-native-track-player
**cloud:** Bun runtime, Express, ws (WebSocket), MongoDB, Docker, PostHog, Cloudflare

---

## 3. Vuzix Blade 2 Template App

### Architecture

A simple Android template application for Vuzix Blade 2 smart glasses. Demonstrates three UI layout patterns using Vuzix's HUD SDK (`com.vuzix.hud`). Pure Java, single-module Android project.

**Structure:**
```
Blade_2_Template_App/
└── app/src/main/java/devkit/blade/vuzix/com/blade_template_app/
    ├── BladeSampleApplication.java          # Application class (dynamic themes)
    ├── center_content_template_activity.java # Center-lock UI with always-visible action menu
    ├── around_content_template_activity.java # Bottom-lock navigation style
    ├── center_content_pop_up_menu_template_activity.java # Pop-up menu style
    ├── Template_Widget.java                 # AppWidgetProvider for BladeOS launcher
    └── Template_Widget_Update_Receiver.java # BroadcastReceiver for theme changes
```

### All Classes/Functions (Full Signatures)

**`class BladeSampleApplication extends DynamicThemeApplication`**
- `protected int getNormalThemeResId()` → returns `R.style.AppTheme`
- `protected int getLightThemeResId()` → returns `R.style.AppTheme_Light`
- Enables dynamic light/dark theme switching based on ambient light sensor

**`class center_content_template_activity extends ActionMenuActivity`**
- `protected void onCreate(Bundle savedInstanceState)`
- `protected boolean onCreateActionMenu(Menu menu)` — inflates main_menu, sets up menu items
- `protected boolean alwaysShowActionMenu()` → `true` (always visible action menu)
- `protected int getDefaultAction()` → `1` (default focused menu item)
- `public void showHello(MenuItem item)` — shows "Hello" toast + updates main text
- `public void showVuzix(MenuItem item)` — shows "Vuzix" toast
- `public void showBlade(MenuItem item)` — toggles switch state, increments counter
- `public void showbottomlock(MenuItem item)` — navigates to around_content activity
- `public void showpopUp(MenuItem item)` — navigates to pop-up menu activity
- private `void showToast(String text)`
- **Inner class `SwitchMenuItemView extends DefaultActionMenuItemView`**
  - `SwitchMenuItemView(Context context)`
  - `void setSwitchState(boolean on, int times)` — toggles icon/tint/title

**`class around_content_template_activity extends ActionMenuActivity`**
- `protected void onCreate(Bundle savedInstanceState)`
- `public boolean onCreateActionMenu(Menu menu)` — inflates around_content_menu
- `protected int getActionMenuGravity()` → `Gravity.CENTER`
- `protected boolean alwaysShowActionMenu()` → `true`
- `protected int getDefaultAction()` → `0`
- `public void showHello(MenuItem)`, `showVuzix(MenuItem)`, `showBlade(MenuItem)`
- `protected void onActionItemFocused(MenuItem item)` — updates title/value/image on focus change

**`class center_content_pop_up_menu_template_activity extends ActionMenuActivity`**
- Same structure as center_content_template_activity except:
- `protected boolean alwaysShowActionMenu()` → `false` (pop-up on gesture only)
- **Inner class `SwitchMenuItemView extends DefaultActionMenuItemView`** (same as above)

**`class Template_Widget extends AppWidgetProvider`**
- `static void updateAppWidget(Context, AppWidgetManager, int appWidgetId)`
- `void onReceive(Context, Intent)` — calls `update(context, isLightMode(context))`
- `void onUpdate(Context, AppWidgetManager, int[] appWidgetIds)`
- `static void update(Context, boolean isLightMode)` — delegates to full update
- `static void update(Context, AppWidgetManager, int[], boolean isLightMode)` — switches between light/dark widget layouts
- `void onEnabled(Context)`, `void onDisabled(Context)` — lifecycle stubs
- `private static boolean isLightMode(Context)` — queries `BladeSampleApplication.isLightMode()`

**`class Template_Widget_Update_Receiver extends BroadcastReceiver`**
- `void onReceive(Context, Intent)` — forwards UI_DISPLAY_MODE change as ACTION_APPWIDGET_UPDATE broadcast

### Dependencies

- Vuzix HUD SDK (`com.vuzix.hud.resources.DynamicThemeApplication`, `com.vuzix.hud.actionmenu.ActionMenuActivity`, `com.vuzix.hud.actionmenu.DefaultActionMenuItemView`)
- Android SDK (AppWidgetProvider, BroadcastReceiver, standard Activity/Menu APIs)
- Target: Vuzix Blade 2 (BladeOS) — small-screen HUD display

### Usage Examples

The template demonstrates three UI patterns for Blade 2 glasses:

1. **Center Content + Always-Visible Action Menu** — Like the Vuzix Camera app style. Menu items rotate via swipe, center layout is your content.

2. **Around Content (Bottom Lock)** — Like the Vuzix Settings app. Menu items at center, content updates based on focused item via `onActionItemFocused()`.

3. **Pop-Up Menu** — Same as center content but `alwaysShowActionMenu()` returns false. Menu appears only on 1-finger hold gesture.

4. **Widget** — AppWidgetProvider that appears on BladeOS launcher rail. Supports light/dark mode switching via `DynamicThemeApplication`.

---

## Cross-Repo Comparison

| Feature | xg-glass-sdk | MentraOS | Blade 2 Template |
|---------|-------------|----------|-------------------|
| Language | Kotlin + Dart + Python | Java + Swift + TypeScript | Java |
| Platform | Android (phone/glasses) | Android + iOS + Cloud | Vuzix Blade 2 only |
| Multi-device | Yes (6 vendors) | Yes (5+ vendors) | No (Blade 2 only) |
| Architecture | SDK library | Full OS + app store | Template app |
| Display | vendor-abstracted | Cloud-routed layouts | ActionMenuActivity |
| Audio | Mic + Speaker unified | BLE audio + STT + TTS | N/A |
| Camera | Unified capturePhoto | Camera + video + streaming | N/A |
| App Model | UniversalAppEntry (reflection) | WebSocket SDK + mini-apps | Standard Android |
| Distribution | Source/includeBuild | App Store (Mentra Store) | APK sideload |
| CLI | xg-glass (Python) | bun/npm scripts | Gradle only |
| Total Source Files | ~35 | ~1474 | 6 |
