# MASTER ULTIMATE AR GLASSES SDK REFERENCE
## Complete Cross-Device API Reference, Source Code Analysis & Documentation
### Compiled: 2026-04-19 | 30+ repos deeply analyzed | 200+ source files read
### Total size: ~200KB | Living Document

---

# PART 1: CROSS-DEVICE SDK (xg-glass-sdk + MentraOS + hermes-glasses)

     1|# DEEP SDK REFERENCE: xg-glass-sdk + MentraOS + hermes-glasses
     2|
     3|Generated: 2026-04-19
     4|Sources: /tmp/glasses-repos/xg-glass-sdk/, /tmp/glasses-repos/MentraOS/, ~/Desktop/APP/Glasses/hermes-glasses/
     5|
     6|---
     7|
     8|## TABLE OF CONTENTS
     9|
    10|1. [xg-glass-sdk — Core Interface (GlassesClient)](#1-xg-glass-sdk-core)
    11|2. [xg-glass-sdk — Models & Data Classes](#2-models-data-classes)
    12|3. [xg-glass-sdk — Audio System](#3-audio-system)
    13|4. [xg-glass-sdk — State & Events](#4-state-events)
    14|5. [xg-glass-sdk — Error Types](#5-error-types)
    15|6. [xg-glass-sdk — External Activity Bridge](#6-external-activity-bridge)
    16|7. [xg-glass-sdk — App Contract (UniversalAppEntry)](#7-app-contract)
    17|8. [xg-glass-sdk — Device: Rokid](#8-device-rokid)
    18|9. [xg-glass-sdk — Device: Meta](#9-device-meta)
    19|10. [xg-glass-sdk — Device: Omi](#10-device-omi)
    20|11. [xg-glass-sdk — Device: Frame (Flutter Bridge)](#11-device-frame)
    21|12. [xg-glass-sdk — Device: Frame (Embedded)](#12-device-frame-embedded)
    22|13. [xg-glass-sdk — Device: RayNeo Installer (Phone-side)](#13-device-rayneo-installer)
    23|14. [xg-glass-sdk — Device: RayNeo Runtime (On-glasses)](#14-device-rayneo-runtime)
    24|15. [xg-glass-sdk — Device: Simulator](#15-device-simulator)
    25|16. [xg-glass-sdk — Template App (MainActivity)](#16-template-app)
    26|17. [xg-glass-sdk — Build Logic / Plugins](#17-build-logic)
    27|18. [xg-glass-sdk — Capability Matrix (All Devices)](#18-capability-matrix)
    28|19. [MentraOS — Architecture Overview](#19-mentraos-overview)
    29|20. [MentraOS — SDK: AppServer](#20-mentraos-appserver)
    30|21. [MentraOS — SDK: AppSession](#21-mentraos-appsession)
    31|22. [MentraOS — SDK: LayoutManager](#22-mentraos-layouts)
    32|23. [MentraOS — SDK: EventManager](#23-mentraos-events)
    33|24. [MentraOS — SDK: Types & Enums](#24-mentraos-types)
    34|25. [MentraOS — SDK: Models (AppI, Settings, Tools)](#25-mentraos-models)
    35|26. [hermes-glasses — Existing App Architecture](#26-hermes-glasses)
    36|
    37|---
    38|
    39|## 1. xg-glass-sdk — Core Interface (GlassesClient)
    40|<a name="1-xg-glass-sdk-core"></a>
    41|
    42|**Package:** `com.universalglasses.core`
    43|**File:** `core/src/main/java/com/universalglasses/core/GlassesClient.kt`
    44|
    45|```kotlin
    46|interface GlassesClient {
    47|    val model: GlassesModel
    48|    val capabilities: DeviceCapabilities
    49|
    50|    /** Connection lifecycle state. */
    51|    val state: StateFlow<ConnectionState>
    52|
    53|    /** Non-fatal events (logs, warnings, tap events, etc.). */
    54|    val events: Flow<GlassesEvent>
    55|
    56|    /** Establish connection to the glasses. */
    57|    suspend fun connect(): Result<Unit>
    58|
    59|    /** Tear down connection. Safe to call multiple times. */
    60|    suspend fun disconnect()
    61|
    62|    /** Capture photo → JPEG bytes + metadata. */
    63|    suspend fun capturePhoto(
    64|        options: CaptureOptions = CaptureOptions()
    65|    ): Result<CapturedImage>
    66|
    67|    /** Display text on glasses. */
    68|    suspend fun display(
    69|        text: String,
    70|        options: DisplayOptions = DisplayOptions()
    71|    ): Result<Unit>
    72|
    73|    /** Play audio on glasses (TTS or raw bytes). */
    74|    suspend fun playAudio(
    75|        source: AudioSource,
    76|        options: PlayAudioOptions = PlayAudioOptions()
    77|    ): Result<Unit>
    78|
    79|    /** Start mic capture → streaming audio chunks. */
    80|    suspend fun startMicrophone(
    81|        options: MicrophoneOptions = MicrophoneOptions()
    82|    ): Result<MicrophoneSession>
    83|}
    84|```
    85|
    86|**Design Goals:**
    87|- Stable API surface for app developers
    88|- Hides transport differences (Frame BLE vs Rokid Wi-Fi P2P vs Meta DAT)
    89|- Observability via state + events (Kotlin Flows)
    90|
    91|---
    92|
    93|## 2. xg-glass-sdk — Models & Data Classes
    94|<a name="2-models-data-classes"></a>
    95|
    96|**Package:** `com.universalglasses.core`
    97|**File:** `core/src/main/java/com/universalglasses/core/Models.kt`
    98|
    99|```kotlin
   100|enum class GlassesModel {
   101|    FRAME, META, ROKID, RAYNEO, SIMULATOR, OMI
   102|}
   103|
   104|data class DeviceCapabilities(
   105|    val canCapturePhoto: Boolean = true,
   106|    val canDisplayText: Boolean = true,
   107|    val canRecordAudio: Boolean = false,
   108|    val canPlayTts: Boolean = false,           // Built-in TTS engine (e.g. Rokid)
   109|    val canPlayAudioBytes: Boolean = false,     // Raw/encoded audio playback
   110|    val supportsTapEvents: Boolean = false,
   111|    val supportsStreamingTextUpdates: Boolean = false
   112|)
   113|
   114|data class CaptureOptions(
   115|    val quality: Int? = null,          // Rokid: JPEG quality 0..100; Frame: preset
   116|    val targetWidth: Int? = null,
   117|    val targetHeight: Int? = null,
   118|    val timeoutMs: Long = 30_000
   119|)
   120|
   121|enum class DisplayMode { REPLACE, APPEND }
   122|
   123|data class DisplayOptions(
   124|    val mode: DisplayMode = DisplayMode.REPLACE,
   125|    val force: Boolean = false         // Bypass throttling/dedup
   126|)
   127|
   128|data class CapturedImage(
   129|    val jpegBytes: ByteArray,
   130|    val timestampMs: Long = System.currentTimeMillis(),
   131|    val width: Int? = null,
   132|    val height: Int? = null,
   133|    val rotationDegrees: Int? = null,
   134|    val sourceModel: GlassesModel
   135|)
   136|```
   137|
   138|---
   139|
   140|## 3. xg-glass-sdk — Audio System
   141|<a name="3-audio-system"></a>
   142|
   143|**Package:** `com.universalglasses.core`
   144|**File:** `core/src/main/java/com/universalglasses/core/Audio.kt`
   145|
   146|```kotlin
   147|enum class AudioEncoding {
   148|    PCM_S16_LE,    // Signed 16-bit little-endian PCM
   149|    PCM_S8,        // Signed 8-bit PCM
   150|    OPUS           // Opus frames (container-less)
   151|}
   152|
   153|sealed class AudioSource {
   154|    data class Tts(val text: String) : AudioSource()
   155|    data class RawBytes(
   156|        val data: ByteArray,
   157|        val pcmFormat: PcmFormat? = null   // null = auto-detect container
   158|    ) : AudioSource()
   159|}
   160|
   161|data class PcmFormat(
   162|    val sampleRateHz: Int = 16_000,
   163|    val channelCount: Int = 1,
   164|    val encoding: AudioEncoding = AudioEncoding.PCM_S16_LE
   165|)
   166|
   167|data class PlayAudioOptions(
   168|    val speechRate: Float? = null,     // TTS rate multiplier (Rokid: 0.75..4.0)
   169|    val interrupt: Boolean = true      // Interrupt in-progress playback
   170|)
   171|
   172|data class AudioFormat(
   173|    val encoding: AudioEncoding,
   174|    val sampleRateHz: Int? = null,
   175|    val channelCount: Int? = null
   176|)
   177|
   178|data class AudioChunk(
   179|    val bytes: ByteArray,
   180|    val format: AudioFormat,
   181|    val sequence: Long,
   182|    val timestampMs: Long = System.currentTimeMillis(),
   183|    val endOfStream: Boolean = false
   184|)
   185|
   186|data class MicrophoneOptions(
   187|    val preferredEncoding: AudioEncoding = AudioEncoding.PCM_S16_LE,
   188|    val preferredSampleRateHz: Int? = 16_000,
   189|    val preferredChannelCount: Int? = 1,
   190|    val vendorMode: String? = null     // RayNeo: "voiceassistant"/"translation"/"camcorder"
   191|)
   192|
   193|interface MicrophoneSession {
   194|    val format: AudioFormat
   195|    val audio: Flow<AudioChunk>        // Hot stream
   196|    suspend fun stop()
   197|}
   198|```
   199|
   200|---
   201|
   202|## 4. xg-glass-sdk — State & Events
   203|<a name="4-state-events"></a>
   204|
   205|**File:** `core/src/main/java/com/universalglasses/core/StateAndEvents.kt`
   206|
   207|```kotlin
   208|sealed class ConnectionState {
   209|    data object Disconnected : ConnectionState()
   210|    data object Connecting : ConnectionState()
   211|    data object Connected : ConnectionState()
   212|    data class Error(val error: GlassesError) : ConnectionState()
   213|}
   214|
   215|sealed class GlassesEvent {
   216|    data class Log(val message: String) : GlassesEvent()
   217|    data class Warning(val message: String) : GlassesEvent()
   218|    data class Tap(val count: Int) : GlassesEvent()
   219|}
   220|```
   221|
   222|---
   223|
   224|## 5. xg-glass-sdk — Error Types
   225|<a name="5-error-types"></a>
   226|
   227|**File:** `core/src/main/java/com/universalglasses/core/Errors.kt`
   228|
   229|```kotlin
   230|sealed class GlassesError(message: String, cause: Throwable? = null) : Exception(message, cause) {
   231|    data object NotConnected : GlassesError("Not connected")
   232|    data object PermissionDenied : GlassesError("Required permissions not granted")
   233|    data object Busy : GlassesError("Device is busy")
   234|    data class Timeout(val operation: String) : GlassesError("Timeout: $operation")
   235|    data class Transport(val detail: String, val raw: Throwable? = null) : GlassesError(detail, raw)
   236|    data class Unsupported(val detail: String) : GlassesError("Unsupported: $detail")
   237|}
   238|```
   239|
   240|---
   241|
   242|## 6. xg-glass-sdk — External Activity Bridge
   243|<a name="6-external-activity-bridge"></a>
   244|
   245|**File:** `core/src/main/java/com/universalglasses/core/ExternalActivityBridge.kt`
   246|
   247|```kotlin
   248|data class ExternalActivityResult(
   249|    val resultCode: Int,
   250|    val data: Intent?
   251|)
   252|
   253|fun interface ExternalActivityBridge {
   254|    suspend fun launch(intent: Intent): ExternalActivityResult
   255|}
   256|```
   257|
   258|Used by Meta adapter to launch registration activities.
   259|
   260|---
   261|
   262|## 7. xg-glass-sdk — App Contract (UniversalAppEntry)
   263|<a name="7-app-contract"></a>
   264|
   265|**Package:** `com.universalglasses.appcontract`
   266|**File:** `app-contract/src/main/java/com/universalglasses/appcontract/UniversalAppEntry.kt`
   267|
   268|```kotlin
   269|enum class HostKind { PHONE, GLASSES }
   270|
   271|data class HostEnvironment(
   272|    val hostKind: HostKind,
   273|    val model: GlassesModel
   274|)
   275|
   276|enum class UserSettingInputType { TEXT, PASSWORD, URL, NUMBER }
   277|
   278|data class UserSettingField(
   279|    val key: String,
   280|    val label: String,
   281|    val hint: String = "",
   282|    val defaultValue: String = "",
   283|    val inputType: UserSettingInputType = UserSettingInputType.TEXT
   284|)
   285|
   286|object AIApiSettings {
   287|    const val KEY_BASE_URL = "ai_api_base_url"
   288|    const val KEY_MODEL = "ai_api_model"
   289|    const val KEY_API_KEY="***"
   290|
   291|    fun fields(
   292|        defaultBaseUrl: String = "",
   293|        defaultModel: String = "",
   294|        defaultApiKey: String = ""
   295|    ): List<UserSettingField>
   296|
   297|    fun baseUrl(settings: Map<String, String>): String
   298|    fun model(settings: Map<String, String>): String
   299|    fun apiKey(settings: Map<String, String>): String
   300|}
   301|
   302|data class UniversalAppContext(
   303|    val environment: HostEnvironment,
   304|    val client: GlassesClient,
   305|    val scope: CoroutineScope? = null,
   306|    val log: (String) -> Unit = {},
   307|    val onCapturedImage: ((CapturedImage) -> Unit)? = null,
   308|    val settings: Map<String, String> = emptyMap()
   309|)
   310|
   311|interface UniversalCommand {
   312|    val id: String
   313|    val title: String
   314|    suspend fun run(ctx: UniversalAppContext): Result<Unit>
   315|}
   316|
   317|interface UniversalAppEntry {
   318|    val id: String
   319|    val displayName: String
   320|    fun commands(env: HostEnvironment): List<UniversalCommand>
   321|    fun userSettings(): List<UserSettingField> = emptyList()
   322|}
   323|
   324|interface UniversalAppEntrySimple : UniversalAppEntry {
   325|    fun commands(): List<UniversalCommand>
   326|    override fun commands(env: HostEnvironment): List<UniversalCommand> = commands()
   327|}
   328|
   329|object UniversalCommandPolicy {
   330|    fun filterCommands(env: HostEnvironment, commands: List<UniversalCommand>): List<UniversalCommand>
   331|    // RayNeo on PHONE host → empty list (installer-only)
   332|}
   333|
   334|// Extension function for hosts:
   335|fun UniversalAppEntry.commandsWithDefaults(env: HostEnvironment): List<UniversalCommand>
   336|```
   337|
   338|---
   339|
   340|## 8. xg-glass-sdk — Device: Rokid
   341|<a name="8-device-rokid"></a>
   342|
   343|**Package:** `com.universalglasses.device.rokid`
   344|**Files:** `RokidGlassesClient.kt`, `RokidDisplayController.kt`
   345|
   346|### RokidGlassesClient
   347|
   348|```kotlin
   349|class RokidGlassesClient(
   350|    private val activity: AppCompatActivity,
   351|    private val options: RokidOptions = RokidOptions()
   352|) : GlassesClient
   353|
   354|// Capabilities:
   355|//   canCapturePhoto=true, canDisplayText=true, canRecordAudio=true,
   356|//   canPlayTts=true, canPlayAudioBytes=true, supportsTapEvents=false,
   357|//   supportsStreamingTextUpdates=true
   358|```
   359|
   360|**Connection flow:** BLE scan → initBluetooth() → connectBluetooth() → initWifiP2P()
   361|**Photo flow:** takeGlassPhoto(w,h,quality) → syncSingleFile(remotePath) → readBytes()
   362|**Audio:** CxrApi openAudioRecord (PCM/OPUS streams), AudioStreamListener
   363|**TTS:** CxrApi.sendGlobalTtsContent(), setLocalTtsSpeed()
   364|**Playback:** setCommunicationDevice() → AudioTrack (PCM only, explicit PcmFormat required)
   365|**Display:** RokidDisplayController — openCustomView(JSON layout) → updateCustomView(JSON updates), throttled at 350ms min interval
   366|
   367|```kotlin
   368|data class RokidOptions(
   369|    val connectTimeoutMs: Long = 30_000,
   370|    val defaultWidth: Int = 2400,
   371|    val defaultHeight: Int = 1800,
   372|    val defaultJpegQuality: Int = 90,
   373|    val authorization: RokidAuthorization? = null
   374|)
   375|
   376|data class RokidAuthorization(
   377|    val snLc: ByteArray,        // SN authorization file (.lc)
   378|    val clientSecret: String     // Developer credential
   379|)
   380|```
   381|
   382|**Constants:**
   383|- `ROKID_SERVICE_UUID = "00009100-0000-1000-8000-00805f9b34fb"`
   384|- SharedPrefs: `"universal_glasses_rokid_bt_reconnect"`, keys `"socket_uuid"`, `"mac_address"`
   385|
   386|### RokidDisplayController (internal)
   387|- `showText(text: String, force: Boolean)` — throttled, uses CxrApi openCustomView/updateCustomView
   388|- `close()` — calls CxrApi.closeCustomView()
   389|- `lastText: String` — tracks last displayed text
   390|- Min update interval: 350ms
   391|
   392|---
   393|
   394|## 9. xg-glass-sdk — Device: Meta
   395|<a name="9-device-meta"></a>
   396|
   397|**Package:** `com.universalglasses.device.meta`
   398|**File:** `MetaWearablesGlassesClient.kt`
   399|
   400|```kotlin
   401|class MetaWearablesGlassesClient @JvmOverloads constructor(
   402|    private val activity: AppCompatActivity,
   403|    private val externalActivityBridge: ExternalActivityBridge? = null,
   404|    private val options: MetaWearablesOptions = MetaWearablesOptions()
   405|) : GlassesClient
   406|
   407|// Capabilities:
   408|//   canCapturePhoto=true, canDisplayText=FALSE, canRecordAudio=true,
   409|//   canPlayTts=FALSE, canPlayAudioBytes=true, supportsTapEvents=false,
   410|//   supportsStreamingTextUpdates=false
   411|```
   412|
   413|**Connection flow:** Wearables.initialize() → startRegistration() → awaitActiveDevice()
   414|**Photo:** DAT SDK StreamSession → capturePhoto() (starts short-lived stream, captures, closes)
   415|**Display:** UNSUPPORTED (returns GlassesError.Unsupported)
   416|**TTS:** UNSUPPORTED
   417|**Mic:** AudioRecord via VOICE_COMMUNICATION over Bluetooth HFP (8kHz mono)
   418|**Playback:** PCM via AudioTrack (A2DP preferred output), encoded via MediaPlayer + temp file
   419|
   420|```kotlin
   421|data class MetaWearablesOptions(
   422|    val deviceSelector: DeviceSelector? = null,
   423|    val registrationTimeoutMs: Long = 90_000,
   424|    val deviceDiscoveryTimeoutMs: Long = 30_000,
   425|    val audioRouteWarmupMs: Long = 1_000
   426|)
   427|```
   428|
   429|**Constants:**
   430|- `HFP_SAMPLE_RATE_HZ = 8_000`
   431|
   432|**Helper extension functions:**
   433|- `PhotoData.toCapturedImage(quality: Int, sourceModel: GlassesModel): CapturedImage`
   434|- `decodeHeicToBitmap(buffer: ByteBuffer): Bitmap`
   435|- `readExifTransform(heicBytes: ByteArray): Matrix`
   436|
   437|---
   438|
   439|## 10. xg-glass-sdk — Device: Omi
   440|<a name="10-device-omi"></a>
   441|
   442|**Package:** `com.universalglasses.device.omi`
   443|**File:** `OmiGlassesClient.kt`
   444|
   445|```kotlin
   446|class OmiGlassesClient(
   447|    private val context: Context
   448|) : GlassesClient
   449|
   450|// Capabilities:
   451|//   canCapturePhoto=true, canDisplayText=FALSE, canRecordAudio=true,
   452|//   canPlayTts=FALSE, canPlayAudioBytes=FALSE, supportsTapEvents=false,
   453|//   supportsStreamingTextUpdates=false
   454|```
   455|
   456|**Connection:** BLE scan for "Omi"/"OMI Glass" devices or AUDIO_SERVICE_UUID → GATT connect → MTU 512 → discover services
   457|**Audio:** OPUS 16kHz mono, streamed via BLE notifications on AUDIO_DATA_UUID (3-byte header: 2b index + 1b sub-index)
   458|**Photo:** BLE-based: write 0x05 to PHOTO_CONTROL_UUID, receive chunks on PHOTO_DATA_UUID, EOF marker=0xFFFF
   459|**Display:** UNSUPPORTED
   460|**Playback:** UNSUPPORTED
   461|
   462|**BLE UUIDs:**
   463|```kotlin
   464|AUDIO_SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
   465|AUDIO_DATA_UUID    = "19B10001-E8F2-537E-4F6C-D104768A1214"
   466|AUDIO_CODEC_UUID   = "19B10002-E8F2-537E-4F6C-D104768A1214"
   467|BATTERY_SERVICE_UUID = "0000180F-0000-1000-8000-00805F9B34FB"
   468|BATTERY_LEVEL_UUID   = "00002A19-0000-1000-8000-00805F9B34FB"
   469|DEVICE_INFO_SERVICE_UUID = "0000180A-0000-1000-8000-00805F9B34FB"
   470|PHOTO_CONTROL_UUID = "19B10006-E8F2-537E-4F6C-D104768A1214"
   471|PHOTO_DATA_UUID    = "19B10005-E8F2-537E-4F6C-D104768A1214"
   472|TIME_SYNC_SERVICE_UUID = "19B10030-E8F2-537E-4F6C-D104768A1214"
   473|TIME_SYNC_WRITE_UUID   = "19B10031-E8F2-537E-4F6C-D104768A1214"
   474|```
   475|
   476|**Internal interfaces:**
   477|```kotlin
   478|private interface OmiMicrophoneSession : MicrophoneSession {
   479|    fun emitAudio(data: ByteArray)
   480|}
   481|```
   482|
   483|---
   484|
   485|## 11. xg-glass-sdk — Device: Frame (Flutter Bridge)
   486|<a name="11-device-frame"></a>
   487|
   488|**Package:** `com.universalglasses.device.frame.flutter`
   489|**Files:** `FrameGlassesClient.kt`, `FrameFlutterBridge.kt`, `FrameFlutterChannelContract.kt`
   490|
   491|### FrameGlassesClient
   492|```kotlin
   493|class FrameGlassesClient(
   494|    private val bridge: FrameFlutterBridge
   495|) : GlassesClient
   496|
   497|// Capabilities:
   498|//   canCapturePhoto=true, canDisplayText=true, canRecordAudio=true,
   499|//   canPlayTts=FALSE, canPlayAudioBytes=FALSE, supportsTapEvents=true,
   500|//   supportsStreamingTextUpdates=true
   501|

---

# PART 2: DRIVERS, BROWSER, REMOTE DESKTOP & HEAD TRACKING
## (XRLinuxDriver, TapLink X3, RayDesk, PhoenixHeadTracker, Fusion)

     1|# DEEP Driver & Tools Reference
     2|## Comprehensive Source-Level Documentation
     3|
     4|Generated from full source reading of:
     5|- XRLinuxDriver (C, Linux head-tracking driver)
     6|- TapLink X3 (Kotlin, Android browser for RayNeo)
     7|- RayDesk (Kotlin, Android remote desktop streaming)
     8|- PhoenixHeadTracker (C#, Windows head tracker)
     9|- Fusion (C, xioTechnologies sensor fusion library)
    10|
    11|---
    12|
    13|# 1. XRLinuxDriver — Linux AR Glasses Head-Tracking Driver
    14|
    15|## 1.1 Architecture Overview
    16|
    17|Multi-threaded C driver that:
    18|1. Detects USB AR glasses via libusb hotplug
    19|2. Reads IMU data (quaternion orientation + optional 6DoF position)
    20|3. Applies calibration, reference pose, and plugin transformations
    21|4. Outputs pose data via IPC (shared memory), mouse, joystick, or OpenTrack UDP
    22|
    23|### Thread Model (5 pthreads + main)
    24|- `block_on_device_thread` — waits for device, connects, blocks while connected
    25|- `monitor_config_file_thread` — inotify watcher on config.ini
    26|- `manage_state_thread` — periodic state write to /dev/shm/xr_driver_state
    27|- `monitor_control_flags_file_thread` — watches /dev/shm/xr_driver_control
    28|- `monitor_usb_devices_thread` — libusb hotplug event loop
    29|
    30|### Main Entry Point (driver.c:main)
    31|```c
    32|int main(int argc, const char** argv)
    33|```
    34|- Sets SIGSEGV handler, acquires file lock (single instance)
    35|- Initializes: config, state, connection_pool
    36|- Creates 5 pthreads, joins all on exit
    37|
    38|---
    39|
    40|## 1.2 Core Data Types
    41|
    42|### IMU Types (imu.h)
    43|```c
    44|struct imu_euler_t { float roll, pitch, yaw; };
    45|struct imu_quat_t  { float x, y, z, w; };
    46|struct imu_vec3_t  { float x, y, z; };
    47|struct imu_pose_t  {
    48|    imu_quat_t orientation;
    49|    imu_vec3_t position;
    50|    imu_euler_t euler;
    51|    bool has_orientation, has_position;
    52|    uint32_t timestamp_ms;
    53|};
    54|```
    55|
    56|### IMU Math Functions (imu.h / imu.c)
    57|```c
    58|float degree_to_radian(float deg);
    59|float radian_to_degree(float rad);
    60|imu_quat_type normalize_quaternion(imu_quat_type q);
    61|imu_quat_type conjugate(imu_quat_type q);
    62|imu_quat_type multiply_quaternions(imu_quat_type q1, imu_quat_type q2);
    63|imu_quat_type euler_to_quaternion_xyz(imu_euler_type euler);
    64|imu_quat_type euler_to_quaternion_zyx(imu_euler_type euler);
    65|imu_quat_type euler_to_quaternion_zxy(imu_euler_type euler);
    66|imu_euler_type quaternion_to_euler_xyz(imu_quat_type q);
    67|imu_euler_type quaternion_to_euler_zyx(imu_quat_type q);
    68|imu_euler_type quaternion_to_euler_zxy(imu_quat_type q);
    69|imu_quat_type device_pitch_adjustment(float adjustment_degrees);
    70|imu_vec3_type vector_rotate(imu_vec3_type v, imu_quat_type q);
    71|bool quat_equal(imu_quat_type q1, imu_quat_type q2);
    72|float quat_small_angle_rad(imu_quat_type q1, imu_quat_type q2);
    73|// Inline helpers:
    74|void imu_pose_sync_euler_from_orientation(imu_pose_type *p);
    75|void imu_pose_sync_orientation_from_euler(imu_pose_type *p);
    76|```
    77|
    78|### Device Properties (devices.h)
    79|```c
    80|struct device_properties_t {
    81|    char* brand, *model;
    82|    int hid_vendor_id, hid_product_id;
    83|    uint8_t usb_bus, usb_address;
    84|    calibration_setup_type calibration_setup;  // AUTOMATIC or INTERACTIVE
    85|    int resolution_w, resolution_h;
    86|    float fov;                    // diagonal FOV in degrees
    87|    float lens_distance_ratio;    // lens_dist / perceived_display_dist
    88|    int calibration_wait_s;
    89|    int imu_cycles_per_s;
    90|    int imu_buffer_size;
    91|    float look_ahead_constant, look_ahead_frametime_multiplier;
    92|    float look_ahead_scanline_adjust, look_ahead_ms_cap;
    93|    bool sbs_mode_supported, firmware_update_recommended;
    94|    bool provides_orientation, provides_position;
    95|    bool can_be_supplemental;
    96|};
    97|```
    98|Constants: `LENS_TO_PIVOT_CM = 5.0 * 2.54` (~12.7cm neck-to-lens)
    99|
   100|### Device Driver Interface (devices.h)
   101|```c
   102|struct device_driver_t {
   103|    char* id;
   104|    device_properties_type* (*supported_device_func)(uint16_t vendor, uint16_t product, uint8_t bus, uint8_t addr);
   105|    bool (*device_connect_func)();
   106|    void (*block_on_device_func)();
   107|    bool (*device_is_sbs_mode_func)();
   108|    bool (*device_set_sbs_mode_func)(bool enabled);
   109|    bool (*is_connected_func)();
   110|    void (*disconnect_func)(bool soft);
   111|};
   112|```
   113|
   114|### Driver Config (config.h)
   115|```c
   116|struct driver_config_t {
   117|    bool disabled, mouse_mode, joystick_mode, external_mode;
   118|    bool use_roll_axis, vr_lite_invert_x, vr_lite_invert_y;
   119|    int mouse_sensitivity;
   120|    char *output_mode;
   121|    bool multi_tap_enabled, metrics_disabled;
   122|    float dead_zone_threshold_deg;
   123|    bool debug_threads, debug_joystick, debug_multi_tap;
   124|    bool debug_ipc, debug_license, debug_device, debug_connections;
   125|};
   126|```
   127|
   128|### Driver State (state.h)
   129|```c
   130|enum calibration_state_t { NOT_CALIBRATED, CALIBRATED, CALIBRATING, WAITING_ON_USER };
   131|struct driver_state_t {
   132|    uint32_t heartbeat;
   133|    char *connected_device_brand, *connected_device_model;
   134|    float connected_device_full_distance_cm, connected_device_full_size_cm;
   135|    bool connected_device_pose_has_position;
   136|    calibration_setup_type calibration_setup;
   137|    calibration_state_type calibration_state;
   138|    bool sbs_mode_supported, sbs_mode_enabled;
   139|    bool breezy_desktop_smooth_follow_enabled;
   140|    float breezy_desktop_follow_threshold, breezy_desktop_display_distance;
   141|    bool firmware_update_recommended, is_gamescope_reshade_ipc_connected;
   142|    int granted_features_count; char** granted_features;
   143|    int license_features_count; char** license_features;
   144|    char* device_license;
   145|    float *smooth_follow_origin; bool smooth_follow_origin_ready;
   146|};
   147|struct control_flags_t {
   148|    bool recenter_screen, recalibrate, force_quit;
   149|    sbs_control_type sbs_mode;  // UNSET, ENABLE, DISABLE
   150|    char* request_features;
   151|};
   152|```
   153|State files: `/dev/shm/xr_driver_state`, `/dev/shm/xr_driver_control`
   154|
   155|### Connection Pool (connection_pool.h)
   156|```c
   157|typedef struct connection_t {
   158|    const device_driver_type* driver;
   159|    device_properties_type* device;
   160|    bool supplemental, active;
   161|    pthread_t thread; bool thread_running;
   162|} connection_t;
   163|
   164|void connection_pool_init(pose_handler_t, reference_pose_getter_t);
   165|void connection_pool_handle_device_added(const device_driver_type*, device_properties_type*);
   166|void connection_pool_handle_device_removed(const char* driver_id);
   167|bool connection_pool_is_connected();
   168|bool connection_pool_connect_active();
   169|void connection_pool_block_on_active();
   170|void connection_pool_disconnect_all(bool soft);
   171|device_properties_type* connection_pool_primary_device();
   172|device_properties_type* connection_pool_supplemental_device();
   173|const device_driver_type* connection_pool_primary_driver();
   174|void connection_pool_ingest_pose(const char* driver_id, imu_pose_type pose);
   175|```
   176|
   177|### IPC Shared Memory (ipc.h)
   178|```c
   179|struct ipc_values_t {
   180|    float *display_res;       // [w, h]
   181|    bool *disabled;
   182|    float *date;              // [4] keepalive
   183|    float *pose_orientation;  // [16] 4 rows of quaternion data
   184|    float *pose_position;     // [3]
   185|    pthread_mutex_t *pose_orientation_mutex;
   186|    float *display_fov, *lens_distance_ratio;  // deprecated
   187|};
   188|```
   189|
   190|### Buffer System (buffer.h)
   191|```c
   192|buffer_type *create_buffer(int size);
   193|float push(buffer_type *buffer, float next_value);
   194|imu_buffer_type *create_imu_buffer(int buffer_size);
   195|imu_buffer_response_type *push_to_imu_buffer(imu_buffer_type*, imu_quat_type, float timestamp_ms);
   196|```
   197|
   198|### Runtime Context (runtime_context.h)
   199|```c
   200|struct runtime_context_t {
   201|    driver_config_type *config;
   202|    device_properties_type *device;
   203|    driver_state_type *state;
   204|    connection_pool_type *conn_pool;
   205|};
   206|// Inline accessors: state(), config(), device_checkout(), device_checkin()
   207|```
   208|
   209|---
   210|
   211|## 1.3 Device Drivers
   212|
   213|### XREAL Driver (devices/xreal.c)
   214|- **Driver ID**: `"xreal"`
   215|- **Vendor**: 0x3318
   216|- **Supported models** (10 PIDs): Air, Air 2, Air 2 Pro, Air 2 Ultra, One Pro, One, 1S
   217|- **FOVs**: 45°–57° depending on model
   218|- **IMU**: 1000Hz native, forced to 250Hz; buffer ~10ms smoothing
   219|- **Pitch adjustments**: 0° for Air series, 35° for One Pro
   220|- **SBS modes**: Maps between non-SBS (1920x1080) and SBS (3840x1080) display modes
   221|- **Coordinate conversion**: NWU via `nwu_conversion_quat = {x=1, y=0, z=0, w=0}`
   222|- Uses `device_imu_*` and `device_mcu_*` SDK for HID communication
   223|
   224|### Viture Driver (devices/viture.c)
   225|- **Driver ID**: `"viture"`
   226|- **Vendor**: 0x35CA
   227|- **Supported models** (14 PIDs): One, One Lite, Pro, Luma, Luma Pro, Luma Ultra, Luma Cyber, Beast
   228|- **FOVs**: 40°–58° depending on model
   229|- **IMU frequency**: 60-500Hz configurable, Carina devices at 1000Hz
   230|- **6DoF**: Carina-based devices provide position via `get_gl_pose_carina()`
   231|- **SBS modes**: 0x31 (1920x1080@60), 0x32 (3840x1080@60), etc.
   232|- **Coordinate conversion**: EUS (GL) → NWU for Carina; direct NWU for legacy
   233|- **Pitch adjustments**: One=6°, Pro=3°, Luma=-8.5°, Beast=-8.5°
   234|
   235|### Rokid Driver (devices/rokid.c)
   236|- **Driver ID**: `"rokid"`
   237|- **Vendor**: ROKID_GLASS_VID (from SDK header)
   238|- **Supported PIDs**: 7 variants (0x162B-0x2180)
   239|- **IMU**: 90Hz via `GlassWaitEvent()` with GAME_ROTATION_EVENT
   240|- **Coordinate conversion**: EUS → NWU with 5° factory offset
   241|- **SBS modes**: 2D (3840x1080@60), 3D (3840x1200@60/90)
   242|
   243|### RayNeo Driver (devices/rayneo.c)
   244|- **Driver ID**: `"rayneo"`
   245|- **Vendor/Product**: 0x1BBB / 0xAF50
   246|- **IMU**: 500Hz native, forced to 250Hz
   247|- **Coordinate conversion**: EUS → NWU with 15° factory offset
   248|- **SDK functions**: `RegisterIMUEventCallback`, `StartXR`, `OpenIMU`, `GetHeadTrackerPose`
   249|- **SBS**: `SwitchTo3D()` / `SwitchTo2D()` / `GetSideBySideStatus()`
   250|
   251|---
   252|
   253|## 1.4 Plugin System
   254|
   255|### Plugin Interface (plugins.h)
   256|```c
   257|struct plugin_t {
   258|    char* id;
   259|    start_func start;
   260|    default_config_func default_config;
   261|    handle_config_line_func handle_config_line;
   262|    handle_control_flag_line_func handle_control_flag_line;
   263|    set_config_func set_config;
   264|    setup_ipc_func setup_ipc;
   265|    handle_ipc_change_func handle_ipc_change;
   266|    modify_reference_pose_func modify_reference_pose;
   267|    handle_reference_pose_updated_func handle_reference_pose_updated;
   268|    modify_pose_func modify_pose;
   269|    handle_pose_data_func handle_pose_data;
   270|    reset_pose_data_func reset_pose_data;
   271|    handle_state_func handle_state;
   272|    handle_device_connect_func handle_device_connect;
   273|    handle_device_disconnect_func handle_device_disconnect;
   274|};
   275|```
   276|
   277|### Registered Plugins (11 total, plugins.c)
   278|1. **device_license** — license key management
   279|2. **virtual_display** — head-locked virtual screen with IPC to shader
   280|3. **sideview** — follow-mode display
   281|4. **metrics** — usage telemetry
   282|5. **custom_banner** — overlay banner display
   283|6. **smooth_follow** — slerp-based screen follow with configurable thresholds
   284|7. **breezy_desktop** — Wayland compositor integration via /dev/shm binary protocol
   285|8. **gamescope_reshade_wayland** — SteamOS/gamescope shader injection
   286|9. **neck_saver** — ergonomic posture alerts
   287|10. **opentrack_source** — sends pose data as OpenTrack UDP (6 doubles: x,y,z,yaw,pitch,roll + frame#)
   288|11. **opentrack_listener** — receives OpenTrack UDP packets as a synthetic IMU device (supplemental)
   289|
   290|### Virtual Display Plugin (plugins/virtual_display.c)
   291|```c
   292|struct virtual_display_config_t {
   293|    bool enabled;
   294|    float look_ahead_override, display_size, display_distance;
   295|    bool sbs_content, sbs_mode_stretched;
   296|    bool follow_mode_enabled, passthrough_smooth_follow_enabled;
   297|    bool curved_display;
   298|};
   299|```
   300|IPC values: enabled, show_banner, look_ahead_cfg[4], display_size, display_north_offset,
   301|sbs_enabled, sbs_content, sbs_mode_stretched, curved_display, half_fov_z_rads, half_fov_y_rads,
   302|fov_half_widths[2], fov_widths[2], texcoord_x_limits[2], texcoord_x_limits_r[2],
   303|lens_vector[3], lens_vector_r[3]
   304|
   305|### Smooth Follow Plugin (plugins/smooth_follow.c)
   306|- States: NONE → INIT → WAITING → SLERPING
   307|- 3 parameter presets: init_params, sticky_params, loose_follow_params
   308|- Implements quaternion slerp with return-to-angle margin
   309|- Tracks origin pose for snap-back when disabled
   310|- Supports per-axis tracking: roll, pitch, yaw independently
   311|- 6DoF: allows half-meter freedom in forward/back direction
   312|
   313|### Breezy Desktop Plugin (plugins/breezy_desktop.c)
   314|- Writes binary data to `/dev/shm/breezy_desktop_imu`
   315|- Layout version 5: config header + IMU record with parity byte
   316|- Config: version, enabled, look_ahead[4], display_res[2], fov, lens_ratio, sbs, banner
   317|- IMU record: smooth_follow_enabled, orientation[16], position[3], epoch_ms, orientation[16], parity
   318|
   319|### OpenTrack Source Plugin (plugins/opentrack_source.c)
   320|- Sends UDP packets: 6 doubles (x,y,z,yaw,pitch,roll) + uint32 frame number
   321|- Coordinate conversion: NWU → EUS (x=-pos.y, y=pos.z, z=-pos.x)
   322|- Configurable: `opentrack_app_ip`, `opentrack_app_port` (default 127.0.0.1:4242)
   323|
   324|### OpenTrack Listener Plugin (plugins/opentrack_listener.c)
   325|- Binds UDP socket, receives OpenTrack 6-double payloads
   326|- Creates synthetic device (brand="OpenTrack", model="UDP")
   327|- Converts EUS yaw/pitch/roll → NWU quaternion via euler_to_quaternion_zyx
   328|- Feedback loop detection: ignores packets when source plugin targets same localhost:port
   329|- Timeout: disconnects if no packets for 500ms
   330|
   331|---
   332|
   333|## 1.5 Pose Processing Pipeline (driver.c:driver_handle_pose)
   334|
   335|1. **Calibration wait** (device-specific seconds, typically 1-15s)
   336|2. **Reference pose capture** (first valid pose after calibration)
   337|3. **Plugin modify_reference_pose** hooks (smooth follow slerp)
   338|4. **Relative orientation**: `multiply_quaternions(reference_conj, pose.orientation)`
   339|5. **Relative position**: vector subtraction + rotation by reference_conj
   340|6. **Multi-tap detection** (double=recenter, triple=recalibrate)
   341|7. **Plugin modify_pose** hooks (neck saver, etc.)
   342|8. **Euler velocity computation**
   343|9. **handle_imu_update** → output to mouse/joystick/IPC
   344|
   345|---
   346|
   347|# 2. TapLink X3 — Android AR Browser for RayNeo
   348|
   349|## 2.1 Architecture Overview
   350|
   351|Kotlin Android app implementing a binocular web browser for RayNeo X3 AR glasses (1280x480 display, 640x480 per eye). Uses SurfaceView pixel-copying for right eye mirroring.
   352|
   353|### Package: `com.TapLinkX3.app`
   354|
   355|## 2.2 Key Classes
   356|
   357|### MainActivity (6339 lines)
   358|Implements: AppCompatActivity, DualWebViewGroup.DualWebViewGroupListener, NavigationListener,
   359|CustomKeyboardView.OnKeyboardActionListener, BookmarkListener, LinkEditingListener,
   360|DualWebViewGroup.MaskToggleListener, DualWebViewGroup.AnchorToggleListener, DualWebViewGroup.WindowCallback
   361|
   362|**Key features:**
   363|- **Sensor-based head tracking**: Uses `SensorManager` with rotation vector for anchored mode
   364|- **Cursor system**: Virtual cursor (320x240 coordinate space) with IMU-based movement
   365|- **Mouse tap mode**: Direct mouse input from Mudra ring controller
   366|- **Triple-tap detection**: Re-centering in anchored mode (400ms tap interval, 800ms sequence)
   367|- **GPS integration**: RayNeo Mercury IPC (`com.ffalconxr.mercury.ipc.Launcher`) for location
   368|- **QR scanning**: ZXing barcode scanner with camera integration
   369|- **Notification relay**: BroadcastReceiver for system notifications
   370|
   371|**Cursor parameters:**
   372|- `TRANSLATION_SCALE = 2000f` (anchored mode)
   373|- `cursorSensitivity` 0-100, mapped to `cursorGain` 0.0-0.9
   374|- Smoothing: double-exponential with configurable `smoothnessLevel` (0-100)
   375|- Frame timing: `MIN_FRAME_INTERVAL_MS = 8` (~120fps cap)
   376|
   377|### DualWebViewGroup (8439 lines)
   378|Core binocular rendering component.
   379|
   380|**Structure:**
   381|- `webViewsContainer` (FrameLayout) — holds the primary WebView
   382|- `rightEyeView` (SurfaceView) — receives pixel-copied left eye content
   383|- `leftEyeUIContainer` — overlay for navigation, keyboard, bookmarks
   384|- `fullScreenOverlayContainer` — fullscreen video container
   385|- `leftEyeClipParent` — 640px wide clipping parent
   386|
   387|**Multi-window support:**
   388|```kotlin
   389|data class BrowserWindow(
   390|    val id: String = UUID.randomUUID().toString(),
   391|    val webView: InternalWebView,
   392|    var thumbnail: Bitmap? = null,
   393|    var title: String = "New Tab"
   394|)
   395|```
   396|
   397|**Rendering pipeline:**
   398|- Refresh interval: 16ms (~60fps normal), 100ms (idle/masked)
   399|- Idle detection: 5s threshold → drops to ~10fps
   400|- PixelCopy for right eye mirroring
   401|- UI scale: 0.5-1.0 with pivot at (320, 240)
   402|- Progress bar for page loading
   403|
   404|**Navigation bar buttons:** Back, Forward, Home, Refresh, Quit, Settings, Hyperlink/URL, Bookmarks, Mode toggle, Anchor toggle, Zoom in/out, Windows manager
   405|
   406|**Interfaces:**
   407|```kotlin
   408|interface DualWebViewGroupListener { fun onCursorPositionChanged(x, y, isVisible) }
   409|interface MaskToggleListener { fun onMaskTogglePressed() }
   410|interface AnchorToggleListener { fun onAnchorTogglePressed() }
   411|interface FullscreenListener { fun onEnterFullscreen(); fun onExitFullscreen() }
   412|interface KeyboardListener { fun onShowKeyboard(); fun onHideKeyboard() }
   413|interface WindowCallback { fun onWindowCreated(webView); fun onWindowSwitched(webView) }
   414|```
   415|
   416|### CustomKeyboardView (1020 lines)
   417|Full custom on-screen keyboard with:
   418|- Two modes: LETTERS and SYMBOLS
   419|- Caps lock (double-tap shift)
   420|- Dynamic keys (@ in letters, ← arrow in symbols)
   421|- Cursor-aware hover system (for head-tracking input)
   422|- Auto-lowercase after key press (unless caps locked)
   423|- Anchored mode tap support
   424|
   425|```kotlin
   426|interface OnKeyboardActionListener {
   427|    fun onKeyPressed(key: String)
   428|    fun onBackspacePressed()
   429|    fun onEnterPressed()
   430|    fun onHideKeyboard()
   431|    fun onClearPressed()
   432|    fun onMoveCursorLeft()
   433|    fun onMoveCursorRight()
   434|    fun onMicrophonePressed()
   435|}
   436|```
   437|
   438|### GroqAudioService
   439|Voice-to-text using Groq's Whisper API:
   440|- Records M4A audio via MediaRecorder (VOICE_RECOGNITION source, 44.1kHz AAC 128kbps)
   441|- Sends to `https://api.groq.com/openai/v1/audio/transcriptions`
   442|- Model: `whisper-large-v3`
   443|- API key stored in SharedPreferences
   444|
   445|### WebAppInterface
   446|JavaScript bridge (`@JavascriptInterface`):
   447|- `ping()` → "pong"
   448|- `chatWithGroq(message, historyJson)` — Groq chat completions API
   449|  - Model: `llama3-70b-8192`
   450|  - System prompt includes location context
   451|  - Response via `evaluateJavascript("receiveGroqResponse('...')")`
   452|
   453|### Constants
   454|```kotlin
   455|DEFAULT_URL = "file:///android_asset/AR_Dashboard_Landscape_Sidebar.html"
   456|PREFS_NAME = "TapLinkPrefs"
   457|BROWSER_PREFS_NAME = "BrowserPrefs"
   458|```
   459|
   460|### Other Components
   461|- **BookmarksView** — bookmark management UI
   462|- **ChatView** — AI chat interface with mic input
   463|- **ColorWheelView** — color picker for text customization
   464|- **SystemInfoView** — battery, time, connectivity status
   465|- **FontIconView** — icon font rendering
   466|- **NotificationService** — system notification listener
   467|- **GroqInterface** — Groq API interface
   468|- **DebugLog** — conditional logging wrapper
   469|- **MyApplication** — Application subclass
   470|
   471|---
   472|
   473|# 3. RayDesk — Android Remote Desktop Streaming
   474|
   475|## 3.1 Architecture Overview
   476|
   477|Kotlin Android app for streaming a remote PC desktop to RayNeo X3 Pro AR glasses. Built on Moonlight (open-source NVIDIA GameStream/Sunshine client). Renders video in OpenGL with head-tracked virtual screen positioning.
   478|
   479|### Package: `com.raydesk`
   480|
   481|## 3.2 Streaming Layer (com.raydesk.streaming)
   482|
   483|### MoonlightBridge
   484|Core integration with Moonlight's `NvConnection`:
   485|- `initializeDecoder()` — creates `MediaCodecDecoderRenderer`, wires `VideoSurfaceHolder`
   486|- `connect()` — builds `StreamConfiguration`, creates `NvConnection`, starts streaming
   487|- `connectToSavedServer()` — suspend function, looks up app by name, handles certificates
   488|- `quitExistingSession()` — kills stale sessions before reconnecting
   489|- `disconnect()` — stops connection
   490|- Supports H.264, H.265 (HEVC), AV1
   491|- Input methods: `sendMouseMove()`, `sendMouseClick()`, `sendKeyboard()`, `sendScroll()`
   492|
   493|### StreamConfig
   494|```kotlin
   495|data class StreamConfig(
   496|    val width: Int = 1920,
   497|    val height: Int = 1080,
   498|    val fps: Int = 60,
   499|    val bitrate: Int = 20000  // kbps
   500|)
   501|

---

# PART 3: 3D XR ENVIRONMENT, FRAME FIRMWARE & SAMPLES
## (StardustXR, headset-utils, frame-codebase, BeatSync, RayNeo Unity samples)

     1|# DEEP Source-Level Reference: StardustXR, Frame, Headset-Utils, BeatSync, RayNeo
     2|
     3|Generated from complete source reading of all repos at /tmp/glasses-repos/
     4|
     5|---
     6|
     7|## 1. STARDUST XR SERVER (stardust-server)
     8|
     9|### 1.1 Architecture Overview
    10|
    11|StardustXR is a **3D spatial UI server** built on Bevy ECS + OpenXR. It runs as a Unix socket server
    12|accepting client connections, each client getting a scenegraph of Nodes with Aspects (traits).
    13|
    14|**Main Loop** (`src/main.rs`):
    15|- Tokio async runtime wraps a Bevy app
    16|- `LockedSocket::get_free()` finds free socket at `$XDG_RUNTIME_DIR/stardust-*`
    17|- Unix socket accept loop spawns `Client::from_connection()` for each
    18|- Bevy runs with Vulkan backend, OpenXR integration via `bevy_mod_openxr`
    19|- `PreFrameWait` schedule runs before each XR frame
    20|- `xr_step()` calls `Root::send_frame_events(delta)` to tick all clients
    21|
    22|**Key Resources:**
    23|```
    24|struct CliArgs          - CLI flags: force_flatscreen, spectator, overlay_priority, etc.
    25|struct PreFrameWait     - ScheduleLabel for pre-frame systems
    26|struct ObjectRegistryRes(Arc<ObjectRegistry>) - D-Bus object registry
    27|struct DbusConnection(Connection) - D-Bus session connection
    28|type BevyMaterial = StandardMaterial
    29|```
    30|
    31|**Plugin Architecture:**
    32|- `SpatialNodePlugin` - spatial hierarchy + Bevy transform sync
    33|- `ModelNodePlugin` - GLTF model loading via Bevy asset system
    34|- `TextNodePlugin` - 3D text rendering
    35|- `LinesNodePlugin` - 3D line drawing
    36|- `AudioNodePlugin` - spatial audio
    37|- `CameraNodePlugin` - virtual cameras
    38|- `SkyPlugin` - equirectangular sky textures
    39|- `PlaySpacePlugin` - XR play space tracking
    40|- `HmdPlugin` - head-mounted display tracking
    41|- `HandPlugin` - OpenXR hand tracking (26 joints)
    42|- `ControllerPlugin` - OpenXR controllers
    43|- `FlatscreenInputPlugin` - mouse pointer for flatscreen mode
    44|- `WaylandPlugin` (feature-gated) - Wayland compositor integration
    45|- `EntityHandlePlugin`, `DmatexPlugin`, `VulkanoPlugin` - infrastructure
    46|
    47|### 1.2 Core: Node System
    48|
    49|**`struct Node`** (`src/nodes/mod.rs`):
    50|The fundamental unit. Every object in the scenegraph is a Node.
    51|```rust
    52|struct Node {
    53|    enabled: AtomicBool,
    54|    id: Id,                              // u64 wrapped in newtype
    55|    client: Weak<Client>,
    56|    message_sender_handle: Option<MessageSenderHandle>,
    57|    aliases: Registry<Alias>,            // Cross-client references
    58|    aspects: Aspects,                    // DashMap<u64, Arc<dyn Aspect>>
    59|    destroyable: bool,
    60|}
    61|```
    62|
    63|**Key methods:**
    64|- `Node::generate(client, destroyable)` - create with auto-generated ID
    65|- `Node::from_id(client, id, destroyable)` - create with specific ID
    66|- `node.add_to_scenegraph()` -> `Arc<Node>` - register in client's scenegraph
    67|- `node.add_aspect(aspect)` -> `Arc<A>` - attach behavior
    68|- `node.get_aspect::<A>()` -> `Result<Arc<A>>` - retrieve typed aspect
    69|- `node.send_remote_signal(aspect_id, method, message)` - send to client
    70|- `node.execute_remote_method_typed::<S, D>(aspect, method, input)` - RPC call
    71|- `node.send_local_signal(client, aspect_id, method, message)` - handle incoming signal
    72|- `node.execute_local_method(client, aspect_id, method, message, response)` - handle incoming method
    73|
    74|**`trait Aspect: Any + Send + Sync`:**
    75|```rust
    76|fn run_signal(&self, client, node, signal, message) -> Result<()>
    77|fn run_method(&self, client, node, method, message, response)
    78|```
    79|
    80|**`trait AspectIdentifier: Aspect`:**
    81|```rust
    82|const ID: u64;  // Compile-time unique ID per aspect type
    83|```
    84|
    85|Aspects are identified by u64 IDs (generated by codegen). The `Aspects` struct uses a `DashMap<u64, Arc<dyn Aspect>>` for concurrent access.
    86|
    87|**`struct OwnedNode(Arc<Node>)`** - RAII wrapper that destroys node on drop.
    88|
    89|### 1.3 Core: Client System
    90|
    91|**`struct Client`** (`src/core/client.rs`):
    92|```rust
    93|struct Client {
    94|    pid: Option<i32>,
    95|    exe: Option<PathBuf>,
    96|    dispatch_join_handle: OnceLock<JoinHandle>,
    97|    flush_join_handle: OnceLock<JoinHandle>,
    98|    disconnect_status: OnceLock<Result<()>>,
    99|    id_counter: CounterU32,
   100|    message_last_received: watch::Receiver<Instant>,
   101|    message_sender_handle: Option<MessageSenderHandle>,
   102|    scenegraph: Arc<Scenegraph>,
   103|    root: OnceLock<Arc<Root>>,
   104|    base_resource_prefixes: Mutex<Vec<PathBuf>>,
   105|    state: OnceLock<ClientState>,
   106|    dmatexes: DashMap<Id, Arc<ImportedDmatex>>,
   107|}
   108|```
   109|
   110|**Connection flow:**
   111|1. `Client::from_connection(UnixStream)` - reads PID, exe path from peer creds
   112|2. Creates `Scenegraph`, `messenger::create()` for bidirectional comms
   113|3. Creates `Root` node at ID 0 with spatial transform
   114|4. Creates interface nodes for: spatial, fields, drawable, audio, input, camera, panel items
   115|5. Spawns dispatch task (reads messages) and flush task (writes messages)
   116|6. Client is tracked in `CLIENTS: OwnedRegistry<Client>`
   117|
   118|**`INTERNAL_CLIENT: LazyLock<Arc<Client>>`** - server's own client for internal nodes (e.g., panel items from Wayland).
   119|
   120|**`struct Scenegraph`** (`src/core/scenegraph.rs`):
   121|```rust
   122|struct Scenegraph {
   123|    client: OnceLock<Weak<Client>>,
   124|    nodes: DashMap<Id, Arc<Node>, FxBuildHasher>,
   125|}
   126|```
   127|Implements `scenegraph::Scenegraph` trait from stardust-core wire protocol.
   128|
   129|### 1.4 Spatial Hierarchy
   130|
   131|**`struct Spatial`** (`src/nodes/spatial.rs`):
   132|```rust
   133|struct Spatial {
   134|    node: Weak<Node>,
   135|    entity: RwLock<Option<EntityHandle>>,    // Bevy Entity
   136|    parent: RwLock<Option<Arc<Spatial>>>,
   137|    transform: RwLock<Mat4>,
   138|    children: Registry<Spatial>,
   139|    bounding_box_calc: OnceLock<fn(&Node) -> Pin<Box<dyn Future<Output = Aabb>>>>,
   140|}
   141|```
   142|
   143|**Bevy Integration:**
   144|- `SpatialNodePlugin` runs in `PostUpdate` before `TransformPropagate`
   145|- `spawn_spatial_nodes()` - creates Bevy entities for new spatials
   146|- `update_spatial_nodes()` - syncs Mat4 transforms to Bevy `Transform` + parent `ChildOf`
   147|- `UPDATED_SPATIALS_NODES: Mutex<EntityHashMap<...>>` - dirty tracking
   148|
   149|**`SpatialNode(Weak<Spatial>)`** - Bevy Component linking entity to spatial.
   150|
   151|**Key spatial operations:**
   152|- `space_to_space_matrix(from, to)` - compute relative transform via global transforms
   153|- `set_local_transform_components(reference_space, transform)` - set pos/rot/scale relative to any space
   154|- `set_spatial_parent(parent)` / `set_spatial_parent_in_place(parent)` - reparenting
   155|- `export_spatial()` -> `Id` - export for cross-client sharing via `EXPORTED_SPATIALS` DashMap
   156|- `is_ancestor_of(spatial)` - loop detection for parent setting
   157|- `visible()` - checks entire parent chain for zero-scale
   158|
   159|**`struct Transform`** (codegen'd):
   160|```rust
   161|struct Transform {
   162|    translation: Option<Vector3<f32>>,
   163|    rotation: Option<Quaternion>,
   164|    scale: Option<Vector3<f32>>,
   165|}
   166|```
   167|All components optional - only set values are applied.
   168|
   169|### 1.5 Input System
   170|
   171|**`struct InputMethod`** (`src/nodes/input/method.rs`):
   172|```rust
   173|struct InputMethod {
   174|    spatial: Arc<Spatial>,
   175|    data: Mutex<InputDataType>,          // Pointer | Hand | Tip
   176|    datamap: Mutex<Datamap>,             // Flexbuffer map of extra data
   177|    handler_links: OwnedRegistry<InputMethodHandlerLink>,
   178|    handler_order: Mutex<Vec<Weak<InputHandler>>>,
   179|    capture_attempts: Registry<InputHandler>,
   180|    captures: Registry<InputHandler>,
   181|}
   182|```
   183|
   184|**`struct InputHandler`** (`src/nodes/input/handler.rs`):
   185|```rust
   186|struct InputHandler {
   187|    spatial: Arc<Spatial>,
   188|    field: Arc<Field>,                   // SDF field for distance calculations
   189|}
   190|```
   191|
   192|**Input flow:**
   193|1. InputMethods register globally in `INPUT_METHOD_REGISTRY`
   194|2. InputHandlers register in `INPUT_HANDLER_REGISTRY`
   195|3. When either is created, bidirectional `InputMethodHandlerLink` aliases are created
   196|4. `update_state()` sends `InputData` to all handlers in order
   197|5. Handlers can request capture via `try_capture()` / `release()`
   198|6. `InputDataType` variants: `Pointer`, `Hand` (26 joints), `Tip`
   199|
   200|**`trait InputDataTrait`:**
   201|- `transform(method, handler)` - transform input data from method space to handler space
   202|- `distance(space, field)` - compute distance to handler's field
   203|
   204|### 1.6 Fields (Signed Distance Fields)
   205|
   206|**`struct Field`** (`src/nodes/fields.rs`):
   207|```rust
   208|struct Field {
   209|    spatial: Arc<Spatial>,
   210|    shape: Mutex<FieldShape>,
   211|    polyline_cache: Mutex<(u64, Option<Vec<Vec<Vec3>>>)>,  // Debug gizmos
   212|}
   213|```
   214|
   215|**Field shapes** (codegen'd): Sphere, Box, Cylinder, Torus, CubicSpline (Bezier curves with thickness).
   216|
   217|**Key operations:**
   218|- `distance(point)` -> f32 (SDF evaluation)
   219|- `normal(point)` -> Vec3
   220|- `closest_point(point)` -> Vec3
   221|- `ray_march(origin, direction)` -> (f32, Vec3) - ray marching through SDF
   222|
   223|**Debug gizmos:** Marching squares algorithm generates polyline contours of fields, rendered as Bevy Gizmos. Toggled via D-Bus.
   224|
   225|### 1.7 Drawable System
   226|
   227|**Models** (`src/nodes/drawable/model.rs`):
   228|- GLTF loading via Bevy AssetServer
   229|- `ModelNodePlugin` with systems: `load_models`, `gen_model_parts`, `apply_materials`
   230|- `ModelPart` - per-mesh-group node with material parameter overrides
   231|- Supports holdout materials (for passthrough AR), dmatex (DMA-buf texture sharing)
   232|- Material deduplication via `MaterialRegistry` using FxHash
   233|
   234|**Lines** (`src/nodes/drawable/lines.rs`): 3D line drawing with per-vertex color/thickness.
   235|
   236|**Text** (`src/nodes/drawable/text.rs`): 3D text with font, size, bounds, alignment.
   237|
   238|**Sky** (`src/nodes/drawable/sky.rs`): HDR equirectangular skybox + environment lighting.
   239|
   240|### 1.8 Panel Items (2D in 3D)
   241|
   242|**`trait Backend`** (`src/nodes/items/panel.rs`):
   243|Interface for Wayland surfaces to be presented as 3D objects:
   244|```rust
   245|trait Backend: Send + Sync + 'static {
   246|    fn start_data(&self) -> Result<PanelItemInitData>;
   247|    fn apply_cursor_material(&self, model_part: &Arc<ModelPart>);
   248|    fn apply_surface_material(&self, surface: SurfaceId, model_part: &Arc<ModelPart>);
   249|    fn close_toplevel(&self);
   250|    fn set_toplevel_size(&self, size: Vector2<u32>);
   251|    fn absolute_pointer_motion(&self, surface: &SurfaceId, position: Vector2<f32>);
   252|    fn pointer_button(&self, surface: &SurfaceId, button: u32, pressed: bool);
   253|    fn keyboard_key(&self, surface: &SurfaceId, keymap_id: Id, key: u32, pressed: bool);
   254|    fn touch_down(&self, surface: &SurfaceId, id: u32, position: Vector2<f32>);
   255|    // ... more input methods
   256|}
   257|```
   258|
   259|Panel items bridge Wayland 2D apps into the 3D space. They support:
   260|- Surface materials applied to model parts
   261|- Cursor rendering
   262|- Full input: pointer, keyboard, touch, scroll
   263|- Child surfaces (popups, subsurfaces)
   264|
   265|### 1.9 HMD & Object Tracking
   266|
   267|**`struct Hmd`** (`src/objects/hmd.rs`):
   268|- Creates OpenXR VIEW reference space
   269|- Updates spatial transform from XR pose each frame
   270|- Falls back to flatscreen camera transform
   271|
   272|**Hand tracking** (`src/objects/input/oxr_hand.rs`):
   273|- `HandPlugin` creates OpenXR hand trackers
   274|- Reads 26 joint positions/rotations per hand
   275|- Converts to `InputDataType::Hand` with full finger articulation
   276|- Supports holdout materials for passthrough transparency
   277|- Publishes via D-Bus for external consumers
   278|
   279|**Play Space** (`src/objects/play_space.rs`):
   280|- Tracks OpenXR STAGE reference space
   281|- Published via D-Bus at `/org/stardustxr/PlaySpace`
   282|
   283|### 1.10 Session Management
   284|
   285|**`struct ClientStateParsed`** (`src/core/client_state.rs`):
   286|```rust
   287|struct ClientStateParsed {
   288|    launch_info: Option<LaunchInfo>,     // cmdline, cwd, env
   289|    data: Option<Vec<u8>>,              // App-specific state blob
   290|    root: Mat4,                         // Root spatial transform
   291|    spatial_anchors: FxHashMap<String, Mat4>,  // Named spatial anchors
   292|}
   293|```
   294|Clients can save/restore state across sessions using `STARDUST_STARTUP_TOKEN` env var.
   295|
   296|---
   297|
   298|## 2. STARDUST XR CORE (stardust-core)
   299|
   300|### 2.1 Wire Protocol (`wire/`)
   301|
   302|**Transport:** Unix domain sockets with FD passing (SCM_RIGHTS).
   303|
   304|**Message format:** FlatBuffers-serialized `Message`:
   305|```
   306|Header: 4 bytes (u32 body_length, native endian)
   307|Body: FlatBuffer message
   308|FDs: passed via ancillary data (SCM_RIGHTS)
   309|```
   310|
   311|**`struct Message`** (FlatBuffers, `wire/src/message.rs`):
   312|```
   313|type_: u8          - 0=Error, 1=Signal, 2=MethodCall, 3=MethodReturn
   314|message_id: u64    - Unique ID for request/response matching
   315|node_id: u64       - Target node
   316|aspect: u64        - Target aspect on node
   317|method: u64        - Method/signal ID within aspect
   318|error: Option<String>
   319|data: Option<Vec<u8>>  - FlexBuffer-serialized payload
   320|```
   321|
   322|**Message types:**
   323|- **Signal (1):** Fire-and-forget. Node dispatches to aspect's `run_signal()`.
   324|- **Method Call (2):** Request-response. Creates `MethodResponse` for async reply.
   325|- **Method Return (3):** Response to a method call. Resolves pending oneshot channel.
   326|- **Error (0):** Error response. Resolves pending future with error string.
   327|
   328|**`struct MessageSender`** (`wire/src/messenger.rs`):
   329|- Queues messages via `mpsc::unbounded_channel`
   330|- `flush()` sends all queued messages
   331|- Header + body sent separately; FDs via `sendmsg` with `ControlMessage::ScmRights`
   332|
   333|**`struct MessageReceiver`:**
   334|- `dispatch(scenegraph)` - reads one message, routes to scenegraph
   335|- Maintains `pending_futures: FxHashMap<u64, PendingFuture>` for method call responses
   336|
   337|**`MessageSenderHandle`** (Clone-able):
   338|- `signal(node_id, aspect, signal, data, fds)` - queue signal
   339|- `method(node_id, aspect, method, data, fds)` -> `Result<Message>` - async method call
   340|- `error(...)` - queue error response
   341|
   342|### 2.2 Serialization (`wire/src/flex/`)
   343|
   344|Custom FlexBuffers serializer/deserializer with **struct field name stripping** for space efficiency.
   345|Structs serialize as FlexBuffer vectors (positional), maps keep string keys.
   346|
   347|Supports **file descriptor serialization** via thread-local context (`fd.rs`).
   348|
   349|**`Datamap`** (`wire/src/flex/datamap.rs`): A FlexBuffer map used for input method extra data.
   350|
   351|### 2.3 Scenegraph Trait
   352|
   353|**`trait Scenegraph`** (`wire/src/scenegraph.rs`):
   354|```rust
   355|trait Scenegraph {
   356|    fn send_signal(&self, node_id, aspect, method, data, fds) -> Result<(), ScenegraphError>;
   357|    fn execute_method(&self, node_id, aspect, method, data, fds, response: MethodResponse);
   358|}
   359|```
   360|
   361|### 2.4 Client SDK (fusion/)
   362|
   363|**`struct NodeCore`** (`fusion/src/node.rs`):
   364|```rust
   365|struct NodeCore {
   366|    client: Arc<ClientHandle>,
   367|    id: u64,
   368|    owned: bool,
   369|}
   370|```
   371|- `send_signal<S>(aspect, signal, data)` - serialize + send signal
   372|- `call_method<S, D>(aspect, method, data)` -> async `D` - serialize + call + deserialize
   373|- Auto-destroys on drop if owned
   374|
   375|**Spatial types** (`fusion/src/spatial.rs`):
   376|- `Spatial::create(parent, transform)` - create owned spatial
   377|- `SpatialRef::import(client, uid)` - import exported spatial
   378|- `Transform` with constructors: `identity()`, `from_translation()`, `from_rotation_scale()`, etc.
   379|
   380|### 2.5 Protocol IDL (`protocol/`)
   381|
   382|Protocol definitions parsed from `.prot` IDL files. The `codegen` crate generates:
   383|- Aspect trait implementations
   384|- Signal/method dispatch tables
   385|- Client-side wrapper functions
   386|- Alias info for cross-client access control
   387|
   388|---
   389|
   390|## 3. FLATLAND (2D Panel Shell)
   391|
   392|### 3.1 Overview
   393|
   394|Flatland is a **Stardust XR client** that acts as a panel shell - it manages Wayland 2D windows
   395|in 3D space. Built on the `stardust-xr-asteroids` framework (declarative UI).
   396|
   397|### 3.2 Architecture
   398|
   399|**`struct State`** (`src/main.rs`):
   400|```rust
   401|struct State {
   402|    toplevels: FxHashMap<u64, ToplevelState>,
   403|    mouse_scroll_multiplier: f32,
   404|}
   405|```
   406|Implements `ClientState`, `Reify`, `Migrate` traits from asteroids framework.
   407|
   408|**`struct ToplevelState`:**
   409|```rust
   410|struct ToplevelState {
   411|    enabled: bool,
   412|    panel_item: PanelItem,
   413|    info: ToplevelInfo,
   414|    cursor_pos: Vector2<f32>,      // Cursor position in pixels
   415|    cursor: Option<Geometry>,
   416|    children: Vec<ChildState>,     // Popup/child surfaces
   417|    density: f32,                  // pixels per meter (default 3000)
   418|    mouse_scroll_multiplier: f32,
   419|}
   420|```
   421|
   422|### 3.3 UI Components
   423|
   424|Each toplevel gets a full 3D UI:
   425|
   426|1. **InitialPositioner** - positions new windows relative to panel item's spatial
   427|2. **InitialPanelPlacement** - initial placement logic
   428|3. **PanelWrapper** - handles panel item signals (size changes, cursor, children)
   429|4. **ResizeHandles** - edge/corner resize with min/max constraints
   430|5. **ExposureButton** (close button) - positioned at top-right corner
   431|6. **Title Text** - rotated 90° along the right edge
   432|7. **PointerPlane** - converts 3D pointer input to 2D pixel coordinates
   433|8. **TouchPlane** - converts 3D touch input to 2D touch events
   434|9. **KeyboardHandler** - keyboard input via fields
   435|10. **MouseHandler** - mouse input with scroll
   436|11. **GrabBall** - grab handle for repositioning
   437|12. **Derezzable** - close on derezz gesture
   438|
   439|**Surface rendering:** Each surface (toplevel + children) gets:
   440|- A model with panel item material applied
   441|- Input handlers for pointer, touch, keyboard
   442|- Proper pixel-to-meter coordinate conversion using density
   443|
   444|---
   445|
   446|## 4. HEADSET-UTILS
   447|
   448|### 4.1 The ARGlasses Trait
   449|
   450|**`trait ARGlasses: Send`** (`src/lib.rs`):
   451|```rust
   452|trait ARGlasses: Send {
   453|    fn serial(&mut self) -> Result<String>;
   454|    fn read_event(&mut self) -> Result<GlassesEvent>;
   455|    fn get_display_mode(&mut self) -> Result<DisplayMode>;
   456|    fn set_display_mode(&mut self, mode: DisplayMode) -> Result<()>;
   457|    fn display_fov(&self) -> f32;
   458|    fn imu_to_display_matrix(&self, side: Side, ipd: f32) -> Isometry3<f64>;
   459|    fn name(&self) -> &'static str;
   460|    fn cameras(&self) -> Result<Vec<CameraDescriptor>>;
   461|    fn display_matrices(&self) -> Result<(DisplayMatrices, DisplayMatrices)>;
   462|    fn display_delay(&self) -> u64;
   463|}
   464|```
   465|
   466|### 4.2 Supported Devices
   467|
   468|- **Rokid Air** (`src/rokid.rs`) - USB HID, 50° FOV
   469|- **Nreal Light** (`src/nreal_light.rs`) - USB HID
   470|- **Nreal Air** (`src/nreal_air.rs`) - USB HID
   471|- **Mad Gaze Glow** (`src/mad_gaze.rs`) - USB HID
   472|- **Grawoow** (`src/grawoow.rs`) - serial port
   473|
   474|### 4.3 Sensor Events
   475|
   476|**`enum GlassesEvent`:**
   477|- `AccGyro { accelerometer: Vec3, gyroscope: Vec3, timestamp: u64 }` - IMU at ~100-200Hz
   478|- `Magnetometer { magnetometer: Vec3, timestamp: u64 }` - compass
   479|- `KeyPress(u8)` - button presses
   480|- `ProximityNear` / `ProximityFar` - wear detection
   481|- `AmbientLight(u16)` - light sensor
   482|- `VSync` - display vsync
   483|
   484|Coordinate system: RUB (Right-Up-Back), same as Android sensors.
   485|
   486|### 4.4 Sensor Fusion
   487|
   488|**`trait Fusion: Send`:**
   489|```rust
   490|trait Fusion {
   491|    fn glasses(&mut self) -> &mut Box<dyn ARGlasses>;
   492|    fn attitude_quaternion(&self) -> UnitQuaternion<f32>;
   493|    fn inconsistency_frd(&self) -> f32;
   494|    fn update(&mut self);
   495|}
   496|```
   497|
   498|**NaiveCF** (`src/naive_cf.rs`): Complementary filter implementation:
   499|- Roll/pitch from accelerometer + gyroscope
   500|- Yaw from gyroscope integration + magnetometer correction
   501|

---

# PART 4: PLATFORM DOCUMENTATION
## (XREAL SDK, RayNeo ARDK, Qualcomm Guide, Japanese setup)

File unchanged since last read. The content from the earlier read_file result in this conversation is still current — refer to that instead of re-reading.

---

# PART 5: UTILITY LIBRARIES & EARLIER ANALYSIS

File unchanged since last read. The content from the earlier read_file result in this conversation is still current — refer to that instead of re-reading.

