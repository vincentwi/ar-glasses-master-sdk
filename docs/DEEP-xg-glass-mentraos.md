# DEEP SDK REFERENCE: xg-glass-sdk + MentraOS + hermes-glasses

Generated: 2026-04-19
Sources: /tmp/glasses-repos/xg-glass-sdk/, /tmp/glasses-repos/MentraOS/, ~/Desktop/APP/Glasses/hermes-glasses/

---

## TABLE OF CONTENTS

1. [xg-glass-sdk — Core Interface (GlassesClient)](#1-xg-glass-sdk-core)
2. [xg-glass-sdk — Models & Data Classes](#2-models-data-classes)
3. [xg-glass-sdk — Audio System](#3-audio-system)
4. [xg-glass-sdk — State & Events](#4-state-events)
5. [xg-glass-sdk — Error Types](#5-error-types)
6. [xg-glass-sdk — External Activity Bridge](#6-external-activity-bridge)
7. [xg-glass-sdk — App Contract (UniversalAppEntry)](#7-app-contract)
8. [xg-glass-sdk — Device: Rokid](#8-device-rokid)
9. [xg-glass-sdk — Device: Meta](#9-device-meta)
10. [xg-glass-sdk — Device: Omi](#10-device-omi)
11. [xg-glass-sdk — Device: Frame (Flutter Bridge)](#11-device-frame)
12. [xg-glass-sdk — Device: Frame (Embedded)](#12-device-frame-embedded)
13. [xg-glass-sdk — Device: RayNeo Installer (Phone-side)](#13-device-rayneo-installer)
14. [xg-glass-sdk — Device: RayNeo Runtime (On-glasses)](#14-device-rayneo-runtime)
15. [xg-glass-sdk — Device: Simulator](#15-device-simulator)
16. [xg-glass-sdk — Template App (MainActivity)](#16-template-app)
17. [xg-glass-sdk — Build Logic / Plugins](#17-build-logic)
18. [xg-glass-sdk — Capability Matrix (All Devices)](#18-capability-matrix)
19. [MentraOS — Architecture Overview](#19-mentraos-overview)
20. [MentraOS — SDK: AppServer](#20-mentraos-appserver)
21. [MentraOS — SDK: AppSession](#21-mentraos-appsession)
22. [MentraOS — SDK: LayoutManager](#22-mentraos-layouts)
23. [MentraOS — SDK: EventManager](#23-mentraos-events)
24. [MentraOS — SDK: Types & Enums](#24-mentraos-types)
25. [MentraOS — SDK: Models (AppI, Settings, Tools)](#25-mentraos-models)
26. [hermes-glasses — Existing App Architecture](#26-hermes-glasses)

---

## 1. xg-glass-sdk — Core Interface (GlassesClient)
<a name="1-xg-glass-sdk-core"></a>

**Package:** `com.universalglasses.core`
**File:** `core/src/main/java/com/universalglasses/core/GlassesClient.kt`

```kotlin
interface GlassesClient {
    val model: GlassesModel
    val capabilities: DeviceCapabilities

    /** Connection lifecycle state. */
    val state: StateFlow<ConnectionState>

    /** Non-fatal events (logs, warnings, tap events, etc.). */
    val events: Flow<GlassesEvent>

    /** Establish connection to the glasses. */
    suspend fun connect(): Result<Unit>

    /** Tear down connection. Safe to call multiple times. */
    suspend fun disconnect()

    /** Capture photo → JPEG bytes + metadata. */
    suspend fun capturePhoto(
        options: CaptureOptions = CaptureOptions()
    ): Result<CapturedImage>

    /** Display text on glasses. */
    suspend fun display(
        text: String,
        options: DisplayOptions = DisplayOptions()
    ): Result<Unit>

    /** Play audio on glasses (TTS or raw bytes). */
    suspend fun playAudio(
        source: AudioSource,
        options: PlayAudioOptions = PlayAudioOptions()
    ): Result<Unit>

    /** Start mic capture → streaming audio chunks. */
    suspend fun startMicrophone(
        options: MicrophoneOptions = MicrophoneOptions()
    ): Result<MicrophoneSession>
}
```

**Design Goals:**
- Stable API surface for app developers
- Hides transport differences (Frame BLE vs Rokid Wi-Fi P2P vs Meta DAT)
- Observability via state + events (Kotlin Flows)

---

## 2. xg-glass-sdk — Models & Data Classes
<a name="2-models-data-classes"></a>

**Package:** `com.universalglasses.core`
**File:** `core/src/main/java/com/universalglasses/core/Models.kt`

```kotlin
enum class GlassesModel {
    FRAME, META, ROKID, RAYNEO, SIMULATOR, OMI
}

data class DeviceCapabilities(
    val canCapturePhoto: Boolean = true,
    val canDisplayText: Boolean = true,
    val canRecordAudio: Boolean = false,
    val canPlayTts: Boolean = false,           // Built-in TTS engine (e.g. Rokid)
    val canPlayAudioBytes: Boolean = false,     // Raw/encoded audio playback
    val supportsTapEvents: Boolean = false,
    val supportsStreamingTextUpdates: Boolean = false
)

data class CaptureOptions(
    val quality: Int? = null,          // Rokid: JPEG quality 0..100; Frame: preset
    val targetWidth: Int? = null,
    val targetHeight: Int? = null,
    val timeoutMs: Long = 30_000
)

enum class DisplayMode { REPLACE, APPEND }

data class DisplayOptions(
    val mode: DisplayMode = DisplayMode.REPLACE,
    val force: Boolean = false         // Bypass throttling/dedup
)

data class CapturedImage(
    val jpegBytes: ByteArray,
    val timestampMs: Long = System.currentTimeMillis(),
    val width: Int? = null,
    val height: Int? = null,
    val rotationDegrees: Int? = null,
    val sourceModel: GlassesModel
)
```

---

## 3. xg-glass-sdk — Audio System
<a name="3-audio-system"></a>

**Package:** `com.universalglasses.core`
**File:** `core/src/main/java/com/universalglasses/core/Audio.kt`

```kotlin
enum class AudioEncoding {
    PCM_S16_LE,    // Signed 16-bit little-endian PCM
    PCM_S8,        // Signed 8-bit PCM
    OPUS           // Opus frames (container-less)
}

sealed class AudioSource {
    data class Tts(val text: String) : AudioSource()
    data class RawBytes(
        val data: ByteArray,
        val pcmFormat: PcmFormat? = null   // null = auto-detect container
    ) : AudioSource()
}

data class PcmFormat(
    val sampleRateHz: Int = 16_000,
    val channelCount: Int = 1,
    val encoding: AudioEncoding = AudioEncoding.PCM_S16_LE
)

data class PlayAudioOptions(
    val speechRate: Float? = null,     // TTS rate multiplier (Rokid: 0.75..4.0)
    val interrupt: Boolean = true      // Interrupt in-progress playback
)

data class AudioFormat(
    val encoding: AudioEncoding,
    val sampleRateHz: Int? = null,
    val channelCount: Int? = null
)

data class AudioChunk(
    val bytes: ByteArray,
    val format: AudioFormat,
    val sequence: Long,
    val timestampMs: Long = System.currentTimeMillis(),
    val endOfStream: Boolean = false
)

data class MicrophoneOptions(
    val preferredEncoding: AudioEncoding = AudioEncoding.PCM_S16_LE,
    val preferredSampleRateHz: Int? = 16_000,
    val preferredChannelCount: Int? = 1,
    val vendorMode: String? = null     // RayNeo: "voiceassistant"/"translation"/"camcorder"
)

interface MicrophoneSession {
    val format: AudioFormat
    val audio: Flow<AudioChunk>        // Hot stream
    suspend fun stop()
}
```

---

## 4. xg-glass-sdk — State & Events
<a name="4-state-events"></a>

**File:** `core/src/main/java/com/universalglasses/core/StateAndEvents.kt`

```kotlin
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
```

---

## 5. xg-glass-sdk — Error Types
<a name="5-error-types"></a>

**File:** `core/src/main/java/com/universalglasses/core/Errors.kt`

```kotlin
sealed class GlassesError(message: String, cause: Throwable? = null) : Exception(message, cause) {
    data object NotConnected : GlassesError("Not connected")
    data object PermissionDenied : GlassesError("Required permissions not granted")
    data object Busy : GlassesError("Device is busy")
    data class Timeout(val operation: String) : GlassesError("Timeout: $operation")
    data class Transport(val detail: String, val raw: Throwable? = null) : GlassesError(detail, raw)
    data class Unsupported(val detail: String) : GlassesError("Unsupported: $detail")
}
```

---

## 6. xg-glass-sdk — External Activity Bridge
<a name="6-external-activity-bridge"></a>

**File:** `core/src/main/java/com/universalglasses/core/ExternalActivityBridge.kt`

```kotlin
data class ExternalActivityResult(
    val resultCode: Int,
    val data: Intent?
)

fun interface ExternalActivityBridge {
    suspend fun launch(intent: Intent): ExternalActivityResult
}
```

Used by Meta adapter to launch registration activities.

---

## 7. xg-glass-sdk — App Contract (UniversalAppEntry)
<a name="7-app-contract"></a>

**Package:** `com.universalglasses.appcontract`
**File:** `app-contract/src/main/java/com/universalglasses/appcontract/UniversalAppEntry.kt`

```kotlin
enum class HostKind { PHONE, GLASSES }

data class HostEnvironment(
    val hostKind: HostKind,
    val model: GlassesModel
)

enum class UserSettingInputType { TEXT, PASSWORD, URL, NUMBER }

data class UserSettingField(
    val key: String,
    val label: String,
    val hint: String = "",
    val defaultValue: String = "",
    val inputType: UserSettingInputType = UserSettingInputType.TEXT
)

object AIApiSettings {
    const val KEY_BASE_URL = "ai_api_base_url"
    const val KEY_MODEL = "ai_api_model"
    const val KEY_API_KEY = "ai_api_key"

    fun fields(
        defaultBaseUrl: String = "",
        defaultModel: String = "",
        defaultApiKey: String = ""
    ): List<UserSettingField>

    fun baseUrl(settings: Map<String, String>): String
    fun model(settings: Map<String, String>): String
    fun apiKey(settings: Map<String, String>): String
}

data class UniversalAppContext(
    val environment: HostEnvironment,
    val client: GlassesClient,
    val scope: CoroutineScope? = null,
    val log: (String) -> Unit = {},
    val onCapturedImage: ((CapturedImage) -> Unit)? = null,
    val settings: Map<String, String> = emptyMap()
)

interface UniversalCommand {
    val id: String
    val title: String
    suspend fun run(ctx: UniversalAppContext): Result<Unit>
}

interface UniversalAppEntry {
    val id: String
    val displayName: String
    fun commands(env: HostEnvironment): List<UniversalCommand>
    fun userSettings(): List<UserSettingField> = emptyList()
}

interface UniversalAppEntrySimple : UniversalAppEntry {
    fun commands(): List<UniversalCommand>
    override fun commands(env: HostEnvironment): List<UniversalCommand> = commands()
}

object UniversalCommandPolicy {
    fun filterCommands(env: HostEnvironment, commands: List<UniversalCommand>): List<UniversalCommand>
    // RayNeo on PHONE host → empty list (installer-only)
}

// Extension function for hosts:
fun UniversalAppEntry.commandsWithDefaults(env: HostEnvironment): List<UniversalCommand>
```

---

## 8. xg-glass-sdk — Device: Rokid
<a name="8-device-rokid"></a>

**Package:** `com.universalglasses.device.rokid`
**Files:** `RokidGlassesClient.kt`, `RokidDisplayController.kt`

### RokidGlassesClient

```kotlin
class RokidGlassesClient(
    private val activity: AppCompatActivity,
    private val options: RokidOptions = RokidOptions()
) : GlassesClient

// Capabilities:
//   canCapturePhoto=true, canDisplayText=true, canRecordAudio=true,
//   canPlayTts=true, canPlayAudioBytes=true, supportsTapEvents=false,
//   supportsStreamingTextUpdates=true
```

**Connection flow:** BLE scan → initBluetooth() → connectBluetooth() → initWifiP2P()
**Photo flow:** takeGlassPhoto(w,h,quality) → syncSingleFile(remotePath) → readBytes()
**Audio:** CxrApi openAudioRecord (PCM/OPUS streams), AudioStreamListener
**TTS:** CxrApi.sendGlobalTtsContent(), setLocalTtsSpeed()
**Playback:** setCommunicationDevice() → AudioTrack (PCM only, explicit PcmFormat required)
**Display:** RokidDisplayController — openCustomView(JSON layout) → updateCustomView(JSON updates), throttled at 350ms min interval

```kotlin
data class RokidOptions(
    val connectTimeoutMs: Long = 30_000,
    val defaultWidth: Int = 2400,
    val defaultHeight: Int = 1800,
    val defaultJpegQuality: Int = 90,
    val authorization: RokidAuthorization? = null
)

data class RokidAuthorization(
    val snLc: ByteArray,        // SN authorization file (.lc)
    val clientSecret: String     // Developer credential
)
```

**Constants:**
- `ROKID_SERVICE_UUID = "00009100-0000-1000-8000-00805f9b34fb"`
- SharedPrefs: `"universal_glasses_rokid_bt_reconnect"`, keys `"socket_uuid"`, `"mac_address"`

### RokidDisplayController (internal)
- `showText(text: String, force: Boolean)` — throttled, uses CxrApi openCustomView/updateCustomView
- `close()` — calls CxrApi.closeCustomView()
- `lastText: String` — tracks last displayed text
- Min update interval: 350ms

---

## 9. xg-glass-sdk — Device: Meta
<a name="9-device-meta"></a>

**Package:** `com.universalglasses.device.meta`
**File:** `MetaWearablesGlassesClient.kt`

```kotlin
class MetaWearablesGlassesClient @JvmOverloads constructor(
    private val activity: AppCompatActivity,
    private val externalActivityBridge: ExternalActivityBridge? = null,
    private val options: MetaWearablesOptions = MetaWearablesOptions()
) : GlassesClient

// Capabilities:
//   canCapturePhoto=true, canDisplayText=FALSE, canRecordAudio=true,
//   canPlayTts=FALSE, canPlayAudioBytes=true, supportsTapEvents=false,
//   supportsStreamingTextUpdates=false
```

**Connection flow:** Wearables.initialize() → startRegistration() → awaitActiveDevice()
**Photo:** DAT SDK StreamSession → capturePhoto() (starts short-lived stream, captures, closes)
**Display:** UNSUPPORTED (returns GlassesError.Unsupported)
**TTS:** UNSUPPORTED
**Mic:** AudioRecord via VOICE_COMMUNICATION over Bluetooth HFP (8kHz mono)
**Playback:** PCM via AudioTrack (A2DP preferred output), encoded via MediaPlayer + temp file

```kotlin
data class MetaWearablesOptions(
    val deviceSelector: DeviceSelector? = null,
    val registrationTimeoutMs: Long = 90_000,
    val deviceDiscoveryTimeoutMs: Long = 30_000,
    val audioRouteWarmupMs: Long = 1_000
)
```

**Constants:**
- `HFP_SAMPLE_RATE_HZ = 8_000`

**Helper extension functions:**
- `PhotoData.toCapturedImage(quality: Int, sourceModel: GlassesModel): CapturedImage`
- `decodeHeicToBitmap(buffer: ByteBuffer): Bitmap`
- `readExifTransform(heicBytes: ByteArray): Matrix`

---

## 10. xg-glass-sdk — Device: Omi
<a name="10-device-omi"></a>

**Package:** `com.universalglasses.device.omi`
**File:** `OmiGlassesClient.kt`

```kotlin
class OmiGlassesClient(
    private val context: Context
) : GlassesClient

// Capabilities:
//   canCapturePhoto=true, canDisplayText=FALSE, canRecordAudio=true,
//   canPlayTts=FALSE, canPlayAudioBytes=FALSE, supportsTapEvents=false,
//   supportsStreamingTextUpdates=false
```

**Connection:** BLE scan for "Omi"/"OMI Glass" devices or AUDIO_SERVICE_UUID → GATT connect → MTU 512 → discover services
**Audio:** OPUS 16kHz mono, streamed via BLE notifications on AUDIO_DATA_UUID (3-byte header: 2b index + 1b sub-index)
**Photo:** BLE-based: write 0x05 to PHOTO_CONTROL_UUID, receive chunks on PHOTO_DATA_UUID, EOF marker=0xFFFF
**Display:** UNSUPPORTED
**Playback:** UNSUPPORTED

**BLE UUIDs:**
```kotlin
AUDIO_SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
AUDIO_DATA_UUID    = "19B10001-E8F2-537E-4F6C-D104768A1214"
AUDIO_CODEC_UUID   = "19B10002-E8F2-537E-4F6C-D104768A1214"
BATTERY_SERVICE_UUID = "0000180F-0000-1000-8000-00805F9B34FB"
BATTERY_LEVEL_UUID   = "00002A19-0000-1000-8000-00805F9B34FB"
DEVICE_INFO_SERVICE_UUID = "0000180A-0000-1000-8000-00805F9B34FB"
PHOTO_CONTROL_UUID = "19B10006-E8F2-537E-4F6C-D104768A1214"
PHOTO_DATA_UUID    = "19B10005-E8F2-537E-4F6C-D104768A1214"
TIME_SYNC_SERVICE_UUID = "19B10030-E8F2-537E-4F6C-D104768A1214"
TIME_SYNC_WRITE_UUID   = "19B10031-E8F2-537E-4F6C-D104768A1214"
```

**Internal interfaces:**
```kotlin
private interface OmiMicrophoneSession : MicrophoneSession {
    fun emitAudio(data: ByteArray)
}
```

---

## 11. xg-glass-sdk — Device: Frame (Flutter Bridge)
<a name="11-device-frame"></a>

**Package:** `com.universalglasses.device.frame.flutter`
**Files:** `FrameGlassesClient.kt`, `FrameFlutterBridge.kt`, `FrameFlutterChannelContract.kt`

### FrameGlassesClient
```kotlin
class FrameGlassesClient(
    private val bridge: FrameFlutterBridge
) : GlassesClient

// Capabilities:
//   canCapturePhoto=true, canDisplayText=true, canRecordAudio=true,
//   canPlayTts=FALSE, canPlayAudioBytes=FALSE, supportsTapEvents=true,
//   supportsStreamingTextUpdates=true
```

All operations delegate to the bridge.

### FrameFlutterBridge (interface)
```kotlin
interface FrameFlutterBridge {
    val state: StateFlow<FrameFlutterState>
    val events: Flow<GlassesEvent>
    val microphone: Flow<AudioChunk>

    suspend fun connect(): Result<Unit>
    suspend fun disconnect()
    suspend fun capturePhoto(options: CaptureOptions): Result<CapturedImage>
    suspend fun displayText(text: String, options: DisplayOptions): Result<Unit>
    suspend fun startMicrophone(options: MicrophoneOptions): Result<AudioFormat>
    suspend fun stopMicrophone(): Result<Unit>
}

sealed class FrameFlutterState {
    data object Disconnected
    data object Connecting
    data object Connected
    data class Error(val message: String)
}
```

### FrameFlutterChannelContract
```kotlin
object FrameFlutterChannelContract {
    const val METHOD_CHANNEL = "universal_glasses/frame/methods"

    object Methods {
        const val CONNECT = "connect"
        const val DISCONNECT = "disconnect"
        const val CAPTURE_PHOTO = "capturePhoto"
        const val DISPLAY_TEXT = "displayText"
        const val START_MICROPHONE = "startMicrophone"
        const val STOP_MICROPHONE = "stopMicrophone"
        const val ON_EVENT = "onEvent"       // Flutter → Android
    }

    object Args {
        const val QUALITY = "quality"
        const val TARGET_WIDTH = "targetWidth"
        const val TARGET_HEIGHT = "targetHeight"
        const val TIMEOUT_MS = "timeoutMs"
        const val TEXT = "text"
        const val FORCE = "force"
        const val MODE = "mode"              // "replace" | "append"
        const val AUDIO_ENCODING = "audioEncoding"
        const val AUDIO_SAMPLE_RATE_HZ = "sampleRateHz"
        const val AUDIO_CHANNEL_COUNT = "channelCount"
        const val AUDIO_VENDOR_MODE = "vendorMode"
    }

    object Events {
        const val TYPE = "type"
        const val TYPE_LOG = "log"
        const val TYPE_WARNING = "warning"
        const val TYPE_TAP = "tap"
        const val TYPE_STATE = "state"
        const val TYPE_AUDIO = "audio"
        const val MESSAGE = "message"
        const val TAP_COUNT = "count"
        const val STATE_VALUE = "value"      // "disconnected"|"connecting"|"connected"|"error"
        const val STATE_ERROR = "error"
        const val AUDIO_BYTES = "bytes"
        const val AUDIO_ENCODING = "encoding"
        const val AUDIO_SAMPLE_RATE_HZ = "sampleRateHz"
        const val AUDIO_CHANNEL_COUNT = "channelCount"
        const val AUDIO_SEQUENCE = "sequence"
        const val AUDIO_EOS = "eos"
    }
}
```

---

## 12. xg-glass-sdk — Device: Frame (Embedded)
<a name="12-device-frame-embedded"></a>

**Package:** `com.universalglasses.device.frame.embedded`

```kotlin
class EmbeddedFrameGlassesClient(context: Context)
    : GlassesClient by FrameGlassesClient(
        bridge = EmbeddedFrameFlutterBridge(context.applicationContext)
    )
```

**EmbeddedFrameFlutterBridge** — SDK-owned FlutterEngine + MethodChannel bridge. Implements `FrameFlutterBridge`. Auto-initializes Flutter runtime, registers plugins, routes events via MethodChannel.

---

## 13. xg-glass-sdk — Device: RayNeo Installer (Phone-side)
<a name="13-device-rayneo-installer"></a>

**Package:** `com.universalglasses.device.rayneo.installer`

```kotlin
class RayNeoInstallerGlassesClient(
    private val context: Context,
    private val config: RayNeoInstallerConfig
) : GlassesClient

// ALL capabilities = false (installer only, no runtime features from phone)
```

**connect()** = deploy/install APK via ADB-over-TCP (adbd:5555)
**capturePhoto/display/playAudio/startMicrophone** = all return GlassesError.Unsupported

**Additional methods:**
```kotlin
suspend fun pushUserSettings(settings: Map<String, String>): Result<Unit>
// Writes JSON to /data/local/tmp/ug_user_settings.json on glasses
```

**Config types:**
```kotlin
data class RayNeoInstallerConfig(
    val host: String,                         // Glasses IP
    val apk: RayNeoApkSource,
    val remoteDir: String = "/data/local/tmp",
    val preferredRemoteFileName: String? = null
)

sealed interface RayNeoApkSource {
    data class Bytes(val bytes: ByteArray)
    data class Asset(val assetPath: String)
    data class FilePath(val path: String)
    data class ContentUri(val uri: Uri, val totalBytes: Long? = null)
}
```

**Constants:**
- `SETTINGS_REMOTE_PATH = "/data/local/tmp/ug_user_settings.json"`

---

## 14. xg-glass-sdk — Device: RayNeo Runtime (On-glasses)
<a name="14-device-rayneo-runtime"></a>

**Package:** `com.universalglasses.device.rayneo.runtime`

```kotlin
class RayNeoRuntimeGlassesClient(
    private val context: Context,
    private val displaySink: RayNeoDisplaySink = ToastDisplaySink()
) : GlassesClient

// Capabilities:
//   canCapturePhoto=true, canDisplayText=true, canRecordAudio=true,
//   canPlayTts=FALSE, canPlayAudioBytes=true, supportsTapEvents=false,
//   supportsStreamingTextUpdates=false
```

**connect()** = immediate (already on-glasses)
**Photo:** Camera2 API, headless (no preview), JPEG capture, auto-selects closest supported size
**Display:** Pluggable RayNeoDisplaySink (default = Toast)
**Mic:** AudioRecord MIC source, supports vendorMode via `AudioManager.setParameters("audio_source_record=<mode>")`
**Playback:** PCM via AudioTrack, encoded via MediaPlayer + temp file

```kotlin
fun interface RayNeoDisplaySink {
    suspend fun display(context: Context, text: String, options: DisplayOptions)
}

class ToastDisplaySink : RayNeoDisplaySink {
    // Uses Toast.makeText(context, text, Toast.LENGTH_LONG)
}
```

---

## 15. xg-glass-sdk — Device: Simulator
<a name="15-device-simulator"></a>

**Package:** `com.universalglasses.device.sim`

```kotlin
class SimulatorGlassesClient(
    private val activity: AppCompatActivity,
    private val displaySink: ((String) -> Unit)? = null,
    private val videoPath: String? = null      // Video file → frame extraction mode
) : GlassesClient

// ALL capabilities = true (simulates all features)
```

**Photo:** CameraX (emulator webcam) OR video file frame extraction (looping playback)
**Display:** Invokes displaySink callback (or warns if null)
**TTS:** Android TextToSpeech engine
**Playback:** PCM via AudioTrack, encoded via MediaPlayer
**Mic:** Android AudioRecord (emulator mic passthrough)

**SimDisplayActivity:**
```kotlin
class SimDisplayActivity : AppCompatActivity() {
    companion object {
        fun newIntent(context: Context, text: String): Intent
    }
}
```

---

## 16. xg-glass-sdk — Template App
<a name="16-template-app"></a>

**MainActivity** (in `templates/kotlin-app/`) demonstrates:
- Device spinner: ROKID, META, FRAME, RAYNEO, OMI, SIMULATOR
- Permission management per device model
- Client creation for each device type
- State/event collection via Kotlin Flows
- UniversalAppEntry loading via reflection
- User settings UI (rendered from UserSettingField declarations)
- Rokid credential management (runtime file picker + SharedPrefs)
- RayNeo IP input + APK installer
- Meta client creation via reflection (optional dependency)

**ExampleAppEntry:**
```kotlin
class ExampleAppEntry : UniversalAppEntrySimple {
    override val id = "example_app"
    override val displayName = "Example XgGlass App"
    override fun commands(): List<UniversalCommand> = emptyList()
}
```

---

## 17. xg-glass-sdk — Build Logic
<a name="17-build-logic"></a>

**Plugins:**
- `UniversalGlassesAndroidApplicationPlugin` — Android app conventions
- `UniversalGlassesAndroidLibraryPlugin` — Android library conventions
- `UniversalGlassesRayneoAppPlugin` — RayNeo-specific app build
- `UniversalGlassesRayneoSettingsPlugin` — RayNeo settings injection

---

## 18. xg-glass-sdk — Capability Matrix
<a name="18-capability-matrix"></a>

| Feature                    | Rokid | Meta  | Frame | RayNeo-Runtime | Omi   | Simulator |
|----------------------------|-------|-------|-------|----------------|-------|-----------|
| capturePhoto               | ✅    | ✅    | ✅    | ✅             | ✅    | ✅        |
| displayText                | ✅    | ❌    | ✅    | ✅             | ❌    | ✅        |
| recordAudio                | ✅    | ✅    | ✅    | ✅             | ✅    | ✅        |
| playTts                    | ✅    | ❌    | ❌    | ❌             | ❌    | ✅        |
| playAudioBytes             | ✅    | ✅    | ❌    | ✅             | ❌    | ✅        |
| tapEvents                  | ❌    | ❌    | ✅    | ❌             | ❌    | ❌        |
| streamingTextUpdates       | ✅    | ❌    | ✅    | ❌             | ❌    | ❌        |
| **Transport**              | BLE+WiFi P2P | DAT SDK | Flutter BLE | Camera2/AudioRecord | BLE GATT | CameraX/AudioRecord |
| **Audio Encoding**         | PCM/OPUS | PCM 8kHz | via Flutter | PCM | OPUS 16kHz | PCM |

---

## 19. MentraOS — Architecture Overview
<a name="19-mentraos-overview"></a>

MentraOS is an open-source operating system, app store, and dev framework for smart glasses.

**Architecture:** Glasses ←BLE→ Phone ←WS→ Cloud ←WS→ App Servers (running MentraOS SDK)

**Monorepo structure:**
- `mobile/` — React Native phone app
- `android_core/` — Android library
- `asg_client/` — Android-based smart glasses client (Even Realities G1, etc.)
- `cloud/packages/sdk/` — **TypeScript SDK for third-party apps** (@mentra/sdk)
- `cloud/packages/cloud/` — Server implementation
- `cloud/packages/utils/` — Shared utilities
- `cloud/packages/react-sdk/` — React SDK for webviews
- `mobile/webview/sdk/` — Webview bridge SDK

**SDK npm package:** `@mentra/sdk`

---

## 20. MentraOS — SDK: AppServer
<a name="20-mentraos-appserver"></a>

**File:** `cloud/packages/sdk/src/app/server/index.ts`

```typescript
interface AppServerConfig {
    packageName: string;              // e.g., 'org.company.appname'
    apiKey: string;                   // Auth with MentraOS Cloud
    port?: number;                    // default: 7010
    cloudApiUrl?: string;             // default: 'api.mentra.glass'
    webhookPath?: string;             // DEPRECATED, auto-set to '/webhook'
    publicDir?: string | false;       // Static files dir
    healthCheck?: boolean;            // /health endpoint (default: true)
    cookieSecret?: string;            // Session cookie signing
    appInstructions?: string;         // Instructions shown to user
    logLevel?: "error" | "warn" | "info" | "debug";
}

class AppServer extends Hono<{ Variables: AuthVariables }> {
    protected config: AppServerConfig;
    public readonly logger: Logger;

    constructor(config: AppServerConfig);

    // Override these in your app:
    protected async onSession(session: AppSession, sessionId: string, userId: string): Promise<void>;
    protected async onStop(sessionId: string, userId: string, reason: string): Promise<void>;
    protected async onToolCall(toolCall: ToolCall): Promise<string | undefined>;

    // Session management:
    protected getActiveSessionById(sessionId: string): AppSession | null;
    protected getActiveSessionForUser(userId: string): AppSession | null;
    protected setActiveSession(sessionId: string, userId: string, session: AppSession): void;
    protected removeActiveSession(sessionId: string, userId: string): void;

    // Lifecycle:
    public async start(): Promise<void>;
    public async stop(): Promise<void>;

    // Photo request management:
    registerPhotoRequest(requestId: string, request: PendingPhotoRequest): void;
    getPhotoRequest(requestId: string): PendingPhotoRequest | undefined;
    completePhotoRequest(requestId: string): PendingPhotoRequest | undefined;
    cleanupPhotoRequestsForSession(sessionId: string): void;

    // Token:
    protected generateToken(userId: string, sessionId: string, secretKey: string): string;

    // Cleanup:
    protected addCleanupHandler(handler: () => void): void;

    // DEPRECATED:
    public getExpressApp(): Hono;
    public getHonoApp(): Hono;
}
```

---

## 21. MentraOS — SDK: AppSession
<a name="21-mentraos-appsession"></a>

**File:** `cloud/packages/sdk/src/app/session/index.ts`

```typescript
interface AppSessionConfig {
    packageName: string;
    apiKey: string;
    mentraOSWebsocketUrl?: string;    // default: 'ws://localhost:8002/app-ws'
    autoReconnect?: boolean;          // default: true
    maxReconnectAttempts?: number;     // default: 3
    reconnectDelay?: number;          // default: 1000ms (exponential backoff)
    userId: string;
    appServer: AppServer;
}

class AppSession {
    // Public modules:
    public readonly events: EventManager;
    public readonly layouts: LayoutManager;
    public readonly settings: SettingsManager;
    public readonly dashboard: DashboardAPI;
    public readonly location: LocationManager;
    public readonly camera: CameraModule;
    public readonly led: LedModule;
    public readonly audio: AudioManager;
    public readonly simpleStorage: SimpleStorage;
    public readonly device: { state: DeviceState };

    public readonly appServer: AppServer;
    public readonly logger: Logger;
    public readonly userId: string;
    public capabilities: Capabilities | null;

    constructor(config: AppSessionConfig);

    getSessionId(): string;
    getPackageName(): string;

    // Deprecated convenience methods (use session.events.* instead):
    onTranscription(handler): () => void;
    onTranscriptionForLanguage(language, handler, disableLanguageIdentification?): () => void;
    onTranslationForLanguage(sourceLanguage, targetLanguage, handler): () => void;
    onHeadPosition(handler): () => void;
    onButtonPress(handler): () => void;
    onTouchEvent(gestureOrHandler, handler?): () => void;
    // ... many more convenience wrappers

    // Connection:
    connect(sessionId: string): Promise<void>;
    disconnect(): void;
    send(message: AppToCloudMessage): void;
}
```

**Session Modules:**
- `CameraModule` — photo capture, streaming, FOV control, ROI
- `LedModule` — RGB LED control
- `AudioManager` — audio playback, streaming
- `LocationManager` — GPS polling
- `SimpleStorage` — key-value persistence
- `DeviceState` — reactive device state observables
- `DashboardManager` — dashboard UI control

---

## 22. MentraOS — SDK: LayoutManager
<a name="22-mentraos-layouts"></a>

**File:** `cloud/packages/sdk/src/app/session/layouts.ts`

```typescript
class LayoutManager {
    constructor(packageName: string, sendMessage: (msg: DisplayRequest) => void);

    showTextWall(text: string, options?: { view?: ViewType; durationMs?: number }): void;
    showDoubleTextWall(topText: string, bottomText: string, options?): void;
    showReferenceCard(title: string, text: string, options?): void;
    showDashboardCard(leftText: string, rightText: string, options?): void;
    async showBitmapView(base64Bitmap: string, options?: { view?; padding?: { left; top } }): void;
    showBitmapAnimation(bitmapDataArray: string[], intervalMs?: number, repeat?: boolean, options?): { stop: () => void };
    clearView(options?: { view?: ViewType }): void;
}
```

**Layout Types:**
```typescript
interface TextWall        { layoutType: "text_wall"; text: string }
interface DoubleTextWall  { layoutType: "double_text_wall"; topText: string; bottomText: string }
interface DashboardCard   { layoutType: "dashboard_card"; leftText: string; rightText: string }
interface ReferenceCard   { layoutType: "reference_card"; title: string; text: string }
interface BitmapView      { layoutType: "bitmap_view"; data: string }
interface BitmapAnimation { layoutType: "bitmap_animation"; frames: string[]; interval: number; repeat: boolean }
interface ClearView       { layoutType: "clear_view" }
```

---

## 23. MentraOS — SDK: EventManager
<a name="23-mentraos-events"></a>

**File:** `cloud/packages/sdk/src/app/session/events.ts`

```typescript
class EventManager {
    onTranscription(handler: (data: TranscriptionData) => void): () => void;
    onTranscriptionForLanguage(language: string, handler, options?): () => void;
    ontranslationForLanguage(sourceLanguage: string, targetLanguage: string, handler): () => void;
    onHeadPosition(handler: (data: HeadPosition) => void): () => void;
    onButtonPress(handler: (data: ButtonPress) => void): () => void;
    onTouchEvent(gesture?: string, handler?): () => void;
    onPhoneNotification(handler): () => void;
    onGlassesBatteryUpdate(handler): () => void;
    onPhoneBatteryUpdate(handler): () => void;
    onGlassesConnectionState(handler): () => void;
    onLocationUpdate(handler): () => void;
    onCalendarEvent(handler): () => void;
    onVad(handler): () => void;
    onAudioChunk(handler): () => void;
    onPhotoTaken(handler): () => void;
    onVpsCoordinates(handler): () => void;
    // System events:
    onConnected(handler): () => void;
    onDisconnected(handler): () => void;
    onError(handler): () => void;
    onSettingsUpdate(handler): () => void;
    onCapabilitiesUpdate(handler): () => void;
    // Generic:
    on(eventType: string, handler): () => void;
    off(eventType: string, handler): void;
}
```

**Stream Types:**
```typescript
enum StreamType {
    BUTTON_PRESS, HEAD_POSITION, PHONE_NOTIFICATION,
    TRANSCRIPTION, TRANSLATION, GLASSES_BATTERY_UPDATE,
    PHONE_BATTERY_UPDATE, GLASSES_CONNECTION_STATE,
    LOCATION_UPDATE, CALENDAR_EVENT, VAD,
    PHONE_NOTIFICATION_DISMISSED, AUDIO_CHUNK, VIDEO,
    STREAM_STATUS, MANAGED_STREAM_STATUS, VPS_COORDINATES,
    PHOTO_TAKEN, OPEN_DASHBOARD, START_APP, STOP_APP,
    ALL, WILDCARD
}
```

---

## 24. MentraOS — SDK: Types & Enums
<a name="24-mentraos-types"></a>

**File:** `cloud/packages/sdk/src/types/enums.ts`

```typescript
enum AppType {
    SYSTEM_DASHBOARD = "system_dashboard",
    BACKGROUND = "background",
    STANDARD = "standard"
}

enum LayoutType {
    TEXT_WALL, DOUBLE_TEXT_WALL, DASHBOARD_CARD,
    REFERENCE_CARD, BITMAP_VIEW, BITMAP_ANIMATION, CLEAR_VIEW
}

enum ViewType {
    DASHBOARD = "dashboard",
    MAIN = "main"
}

enum AppSettingType {
    TOGGLE, TEXT, SELECT, SLIDER, GROUP,
    TEXT_NO_SAVE_BUTTON, SELECT_WITH_SEARCH,
    MULTISELECT, TITLE_VALUE, NUMERIC_INPUT, TIME_PICKER
}

enum HardwareType {
    CAMERA, DISPLAY, MICROPHONE, SPEAKER,
    IMU, BUTTON, LIGHT, WIFI
}

enum HardwareRequirementLevel {
    REQUIRED, OPTIONAL
}
```

**Permission Types:**
```typescript
enum PermissionType {
    MICROPHONE, LOCATION, BACKGROUND_LOCATION,
    CALENDAR, CAMERA, NOTIFICATIONS,
    READ_NOTIFICATIONS, POST_NOTIFICATIONS, ALL
}
```

---

## 25. MentraOS — SDK: Models
<a name="25-mentraos-models"></a>

**File:** `cloud/packages/sdk/src/types/models.ts`

```typescript
interface ToolParameterSchema {
    type: "string" | "number" | "boolean";
    description: string;
    enum?: string[];
    required?: boolean;
}

interface ToolSchema {
    id: string;
    description: string;
    activationPhrases?: string[];
    parameters?: Record<string, ToolParameterSchema>;
}

interface AppI {
    packageName: string;
    name: string;
    publicUrl: string;
    isSystemApp?: boolean;
    uninstallable?: boolean;
    webviewURL?: string;
    logoURL: string;
    appType: AppType;
    appStoreId?: string;
    developerId?: string;
    organizationId?: any;
    permissions?: Permission[];
    description?: string;
    version?: string;
    settings?: AppSettings;
    tools?: ToolSchema[];
    hardwareRequirements?: HardwareRequirement[];
    previewImages?: PreviewImage[];
    isPublic?: boolean;
    appStoreStatus?: "DEVELOPMENT" | "SUBMITTED" | "REJECTED" | "PUBLISHED";
}

// Setting types:
type AppSetting =
    | { type: "toggle"; key: string; label: string; defaultValue: boolean; value?: boolean }
    | { type: "text"; key: string; label: string; defaultValue?: string; value?: string }
    | { type: "text_no_save_button"; key; label; defaultValue?; value?; maxLines? }
    | { type: "select"; key; label; options: {label,value}[]; defaultValue?; value? }
    | { type: "select_with_search"; key; label; options; defaultValue?; value? }
    | { type: "multiselect"; key; label; options; defaultValue?: any[]; value?: any[] }
    | { type: "slider"; key; label; min; max; defaultValue: number; value? }
    | { type: "numeric_input"; key; label; min?; max?; step?; placeholder?; defaultValue?; value? }
    | { type: "time_picker"; key; label; showSeconds?; defaultValue?; value? }
    | { type: "group"; title: string }
    | { type: "titleValue"; label; value; key?: never }

interface TranscriptSegment {
    speakerId?: string;
    resultId: string;
    text: string;
    timestamp: Date;
    isFinal: boolean;
}
```

---

## 26. hermes-glasses — Existing App Architecture
<a name="26-hermes-glasses"></a>

**Package:** `com.openclaw.app`
**Location:** `~/Desktop/APP/Glasses/hermes-glasses/app/src/main/java/com/openclaw/app/`

**Application class:** `MyApplication` — initializes MercurySDK (RayNeo), AppSettings, RuntimeConfig, UiStrings

### Core Files:

**AppConfig.kt** — Global tuning parameters:
- ASR_DEBOUNCE_MS = 2000L
- ASR_WS_PING_INTERVAL_SECONDS = 20L
- AGENT_READ_TIMEOUT_SECONDS = 120L
- AGENT_CONNECT_TIMEOUT_SECONDS = 10L
- AGENT_USER_ID = "ar-glasses-user"
- STREAM_RENDER_THROTTLE_MS = 120L
- Color constants for UI themes

**AgentConfig.kt** — OpenClaw gateway config:
- GATEWAY_TOKEN, BASE_URL, AGENT_ID (from RuntimeConfig → BuildConfig fallback)

**OpenClawClient.kt** — Agent HTTP client:
```kotlin
class OpenClawClient(
    baseUrl: String,
    agentId: String,
    token: String,
    user: String,
    timeoutSeconds: Long = 120
) {
    fun askStreaming(
        text: String,
        onDelta: (delta: String, fullText: String) -> Unit,
        onComplete: (fullText: String) -> Unit,
        onError: (error: String) -> Unit
    )
    fun release()
}
```
- Supports SSE streaming (OpenClaw gateway) and plain JSON (Hermes Agent / OpenAI-compatible)
- Parses both Responses API format (output array) and Chat Completions format (choices array)
- Retry once on connection failure

### Module Structure:
- `agent/` — AgentConfig, OpenClawClient
- `asr/` — AppLanguage, AsrConfig, LocalSpeechEngine, SpeechEngine
- `translation/` — TranslationConfig, TranslationManager, TranslationProvider
  - providers: Azure, Baidu, DeepL, MyMemory, Tencent, Youdao
- `tts/` — LocalTtsEngine, TtsService
- `ui/` — MarkdownRenderer
- Activities: AgentChatActivity, LanguagePickerActivity, SettingsActivity
- Config: AppConfig, AppSettings, RuntimeConfig, UiStrings

**Key architectural notes:**
- Uses MercurySDK for RayNeo display
- Supports Chinese and English UI via UiStrings
- RuntimeConfig loads from `openclaw.conf` file (adb push deployable)
- Multiple ASR backends (Vosk, etc.)
- Multiple translation providers
- Agent communication via HTTP SSE or plain JSON

---

## APPENDIX A: Full File Listing — xg-glass-sdk

```
app-contract/src/main/java/com/universalglasses/appcontract/UniversalAppEntry.kt
build-logic/src/main/kotlin/.../AndroidConventions.kt
build-logic/src/main/kotlin/.../UniversalGlassesAndroidApplicationPlugin.kt
build-logic/src/main/kotlin/.../UniversalGlassesAndroidLibraryPlugin.kt
build-logic/src/main/kotlin/.../rayneo/TemplateFiles.kt
build-logic/src/main/kotlin/.../rayneo/UniversalGlassesRayneoAppPlugin.kt
build-logic/src/main/kotlin/.../rayneo/UniversalGlassesRayneoSettingsPlugin.kt
core/src/main/java/com/universalglasses/core/Audio.kt
core/src/main/java/com/universalglasses/core/Errors.kt
core/src/main/java/com/universalglasses/core/ExternalActivityBridge.kt
core/src/main/java/com/universalglasses/core/GlassesClient.kt
core/src/main/java/com/universalglasses/core/Models.kt
core/src/main/java/com/universalglasses/core/StateAndEvents.kt
devices/device-frame-embedded/.../EmbeddedFrameFlutterBridge.kt
devices/device-frame-embedded/.../EmbeddedFrameGlassesClient.kt
devices/device-frame-flutter/.../FrameFlutterBridge.kt
devices/device-frame-flutter/.../FrameFlutterChannelContract.kt
devices/device-frame-flutter/.../FrameGlassesClient.kt
devices/device-meta/.../MetaWearablesGlassesClient.kt
devices/device-omi/.../OmiGlassesClient.kt
devices/device-rayneo-installer/.../RayNeoInstallerGlassesClient.kt
devices/device-rayneo-runtime/.../RayNeoRuntimeGlassesClient.kt
devices/device-rokid/.../RokidDisplayController.kt
devices/device-rokid/.../RokidGlassesClient.kt
devices/device-simulator/.../SimDisplayActivity.kt
devices/device-simulator/.../SimulatorGlassesClient.kt
templates/kotlin-app/app/.../MainActivity.kt
templates/kotlin-app/ug_app_logic/.../ExampleAppEntry.kt
```

## APPENDIX B: Full File Listing — MentraOS SDK

```
cloud/packages/sdk/src/app/server/index.ts          — AppServer class
cloud/packages/sdk/src/app/session/index.ts          — AppSession class
cloud/packages/sdk/src/app/session/layouts.ts         — LayoutManager
cloud/packages/sdk/src/app/session/events.ts          — EventManager
cloud/packages/sdk/src/app/session/settings.ts        — SettingsManager
cloud/packages/sdk/src/app/session/dashboard.ts       — DashboardManager
cloud/packages/sdk/src/app/session/device-state.ts    — DeviceState
cloud/packages/sdk/src/app/session/api-client.ts      — API client
cloud/packages/sdk/src/app/session/modules/audio.ts   — AudioManager
cloud/packages/sdk/src/app/session/modules/camera.ts  — CameraModule
cloud/packages/sdk/src/app/session/modules/led.ts     — LedModule
cloud/packages/sdk/src/app/session/modules/location.ts — LocationManager
cloud/packages/sdk/src/app/session/modules/simple-storage.ts — SimpleStorage
cloud/packages/sdk/src/app/session/modules/audio-output-stream.ts
cloud/packages/sdk/src/app/session/modules/camera-managed-extension.ts
cloud/packages/sdk/src/app/token/index.ts             — Token management
cloud/packages/sdk/src/app/token/utils.ts
cloud/packages/sdk/src/app/webview/index.ts           — Auth middleware
cloud/packages/sdk/src/types/index.ts                 — All type exports
cloud/packages/sdk/src/types/enums.ts                 — Enums
cloud/packages/sdk/src/types/models.ts                — Core models
cloud/packages/sdk/src/types/layouts.ts               — Layout types
cloud/packages/sdk/src/types/streams.ts               — Stream types
cloud/packages/sdk/src/types/capabilities.ts          — Capabilities
cloud/packages/sdk/src/types/webhooks.ts              — Webhook types
cloud/packages/sdk/src/types/photo-data.ts            — Photo data
cloud/packages/sdk/src/types/rtmp-stream.ts           — RTMP streaming
cloud/packages/sdk/src/types/message-types.ts         — Message type enums
cloud/packages/sdk/src/types/messages/base.ts         — Base message
cloud/packages/sdk/src/types/messages/app-to-cloud.ts
cloud/packages/sdk/src/types/messages/cloud-to-app.ts
cloud/packages/sdk/src/types/messages/glasses-to-cloud.ts
cloud/packages/sdk/src/types/messages/cloud-to-glasses.ts
cloud/packages/sdk/src/transport/Transport.ts
cloud/packages/sdk/src/transport/WebSocketTransport.ts
```

## APPENDIX C: hermes-glasses File Listing

```
com/openclaw/app/
├── AgentChatActivity.kt
├── AppConfig.kt
├── AppSettings.kt
├── LanguagePickerActivity.kt
├── MyApplication.kt
├── RuntimeConfig.kt
├── SettingsActivity.kt
├── UiStrings.kt
├── agent/
│   ├── AgentConfig.kt
│   └── OpenClawClient.kt
├── asr/
│   ├── AppLanguage.kt
│   ├── AsrConfig.kt
│   ├── LocalSpeechEngine.kt
│   └── SpeechEngine.kt
├── translation/
│   ├── TranslationConfig.kt
│   ├── TranslationManager.kt
│   ├── TranslationProvider.kt
│   └── providers/
│       ├── AzureProvider.kt
│       ├── BaiduProvider.kt
│       ├── DeepLProvider.kt
│       ├── MyMemoryProvider.kt
│       ├── TencentProvider.kt
│       └── YoudaoProvider.kt
├── tts/
│   ├── LocalTtsEngine.kt
│   └── TtsService.kt
└── ui/
    └── MarkdownRenderer.kt
```

---

*END OF DEEP SDK REFERENCE*
