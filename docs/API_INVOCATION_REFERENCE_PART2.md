# API Invocation Reference — Part 2: Utilities, Samples & Companion Apps

Generated: 2026-04-19
Covers: Blade_2_Template_App, everysight-sdk, xreal-webxr, decky-XRGaming, mobileapp (Pebble),
        open-wearables, headset-utils, spidgets-3dof, real_utilities, imu-inspector,
        frame-codebase, beatsync, sam3, overpass-turbo, rayneo-setup/6dof/mit

---

## Table of Contents

1.  [Blade_2_Template_App — Vuzix Blade 2 HUD API](#1-blade_2_template_app)
2.  [everysight-sdk — Maverick Smart-Glasses SDK](#2-everysight-sdk)
3.  [xreal-webxr — XREAL WebHID Protocol](#3-xreal-webxr)
4.  [decky-XRGaming — Steam Deck XR Plugin](#4-decky-xrgaming)
5.  [mobileapp — Pebble Ring KMP Companion](#5-mobileapp)
6.  [open-wearables — Health Data MCP Server](#6-open-wearables)
7.  [headset-utils — Rust AR Glasses Abstraction](#7-headset-utils)
8.  [spidgets-3dof — Socket.IO 3DOF Server](#8-spidgets-3dof)
9.  [real_utilities — C++ XREAL HID Protocol](#9-real_utilities)
10. [imu-inspector — C HID IMU Report Parser](#10-imu-inspector)
11. [frame-codebase — Brilliant Frame Firmware + TFLite](#11-frame-codebase)
12. [beatsync — Multi-Device Audio Sync](#12-beatsync)
13. [sam3 — Segment Anything Model 3](#13-sam3)
14. [overpass-turbo — OSM Query Engine](#14-overpass-turbo)
15. [rayneo-setup / rayneo-6dof / rayneo-mit — Unity Projects](#15-rayneo-unity)

---

## 1. Blade_2_Template_App

Vuzix Blade 2 Android HUD template application demonstrating the Vuzix HUD SDK patterns.

### Installation / Setup

    Prerequisites: Android Studio, Vuzix Blade 2 device or emulator
    SDK: com.vuzix:hud-actionmenu (via Vuzix Maven repo)

    1. Clone repo
    2. Open in Android Studio
    3. Sync Gradle (app/build.gradle references Vuzix SDK)
    4. Deploy to Blade 2 via ADB

### File Structure

    app/
      build.gradle                              — Dependencies, Vuzix SDK config
      src/main/
        AndroidManifest.xml                     — App permissions, activities, widget
        java/devkit/blade/vuzix/com/blade_template_app/
          BladeSampleApplication.java           — DynamicThemeApplication subclass
          Template_Widget.java                  — AppWidgetProvider for HUD widget
          Template_Widget_Update_Receiver.java  — BroadcastReceiver for widget updates
          around_content_template_activity.java — ActionMenuActivity with side menu
          center_content_template_activity.java — ActionMenuActivity with center menu + switch
          center_content_pop_up_menu_template_activity.java — Pop-up menu variant
        res/
          layout/
            activity_center_content_template_style.xml
            activity_around_content_template_style.xml
            template_widget_dark.xml
            template_widget_light.xml
          menu/
            bottom_lock_menu.xml
            around_content_menu.xml
            main_menu.xml
          xml/template_widget_info.xml
          values/colors.xml, dimens.xml, styles.xml, strings.xml, attr.xml

### Java Classes & Methods

    class BladeSampleApplication extends DynamicThemeApplication
      int getNormalThemeResId()           — Returns dark theme resource ID
      int getLightThemeResId()            — Returns light theme resource ID

    class Template_Widget extends AppWidgetProvider
      static void updateAppWidget(Context, AppWidgetManager, int)
      void onReceive(Context, Intent)
      void onUpdate(Context, AppWidgetManager, int[])
      static void update(Context, boolean isLightMode)
      static void update(Context, AppWidgetManager, int[], boolean isLightMode)
      void onEnabled(Context)
      void onDisabled(Context)
      static boolean isLightMode(Context)

    class Template_Widget_Update_Receiver extends BroadcastReceiver
      void onReceive(Context, Intent)

    class around_content_template_activity extends ActionMenuActivity
      void onCreate(Bundle)
      boolean onCreateActionMenu(Menu)
      int getActionMenuGravity()          — Returns Gravity.RIGHT
      int getDefaultAction()
      boolean alwaysShowActionMenu()      — Returns true
      void showHello(MenuItem)
      void showVuzix(MenuItem)
      void showBlade(MenuItem)
      void onActionItemFocused(MenuItem)

    class center_content_template_activity extends ActionMenuActivity
      void onCreate(Bundle)
      boolean onCreateActionMenu(Menu)
      boolean alwaysShowActionMenu()
      int getDefaultAction()
      void showHello(MenuItem)
      void showVuzix(MenuItem)
      void showBlade(MenuItem)
      void showbottomlock(MenuItem)
      void showpopUp(MenuItem)
      inner class SwitchMenuItemView extends DefaultActionMenuItemView
        SwitchMenuItemView(Context)
        void setSwitchState(boolean on, int times)

    class center_content_pop_up_menu_template_activity extends ActionMenuActivity
      (same pattern as center_content_template_activity, with pop-up menu support)

### Usage Example

    // In your Activity extending ActionMenuActivity:
    @Override
    protected boolean onCreateActionMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, menu);
        return true;
    }

    @Override
    protected int getActionMenuGravity() {
        return Gravity.RIGHT;  // Side menu
    }

    @Override
    protected boolean alwaysShowActionMenu() {
        return true;  // Persistent menu on HUD
    }

---

## 2. everysight-sdk

Everysight Maverick smart-glasses SDK — binary SDK libraries for iOS and Android with BLE connectivity.

### Installation / Setup

    1. Order Maverick glasses + developer key at www.everysight.com/developer
    2. Read docs at https://everysight.github.io/maverick_docs/
    3. Configure SDK libraries:
       - iOS: libraries/2.5.0/IOS/EvsKit.xcframework/
       - Android: available via Everysight Maven repo
    4. Explore samples at https://github.com/everysight-maverick/samples

### File Structure

    README.md                               — Getting started guide
    LICENSE.md                              — License terms
    libraries/
      README.md                             — Library overview
      docs/README.md                        — Release notes
      2.5.0/
        IOS/
          EvsKit.xcframework/
            ios-arm64/EvsKit.framework/     — Device binary
            ios-arm64_x86_64-simulator/     — Simulator binary
              ota/ota_info.json             — OTA update metadata
    tools/
      README.md                             — Tools overview
      image_convert/README.md               — Image conversion tool docs
      simulator/README.md                   — Simulator tool docs
      font2sif/README.md                    — Font to SIF converter docs

### SDK API (Kotlin example from docs)

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

### BLE Protocol

    - Uses EvsKit framework for BLE communication
    - OTA firmware updates via ota_info.json metadata
    - Screen rendering API: Text, Image, Shape primitives
    - Alignment: Align.center, Align.left, Align.right
    - Colors: EvsColor.Green, EvsColor.White, etc.
    - Fonts: Font.StockFont.Small/Medium/Large

---

## 3. xreal-webxr

WebHID-based control library for XREAL Air/Light glasses — firmware updates, IMU streaming, activation.

### Installation / Setup

    1. Serve files via any HTTP server (uses ES modules)
    2. Open index.html in Chrome (requires WebHID API support)
    3. Connect XREAL glasses via USB
    4. Browser prompts for HID device access

### File Structure

    index.html                  — Main UI for Air glasses
    index_old.html              — Legacy UI
    common.js                   — Shared utilities
    tools/
      sparkline.js              — SVG sparkline charting
      http.js                   — HTTP request utilities
    js_air/                     — XREAL Air protocol
      protocol.js               — Air HID packet protocol (v3)
      glasses.js                — Air glasses EventTarget class
      manager.js                — Air device management functions
    js_light/                   — XREAL Light protocol
      protocol.js               — Light HID packet protocol
      protocolYmodem.js         — Ymodem firmware upload protocol
      glasses.js                — Light glasses EventTarget class
      manager.js                — Light device management functions

### js_air/protocol.js — Air Protocol Constants & Functions

    export const NREAL_VENDOR_ID = 0x3318
    export const BOOT_PRODUCT_ID = 0x0423
    export const IMU_TIMEOUT = 250
    export const ERRORS = { ... }                  — Error code map
    export const MESSAGES = { ... }                — Command ID map

    class Device3Packet                            — Internal packet builder
    export function keyForHex(hex)                 — Command name from hex ID
    export function listKnownCommands()            — Dump all known commands
    export function cmd_build(msgId, payload)      — Build HID command packet
    export function parse_rsp(rsp)                 — Parse HID response packet
    export function brightInt2Bytes(brightness)    — Brightness int to byte array
    export function brightBytes2Int(bytes)         — Byte array to brightness int
    export function bytes2Time(bytes)              — Bytes to timestamp
    export function time2Bytes(timeStamp)          — Timestamp to bytes
    export function hex8(value)                    — Format as 2-digit hex
    export function bytes2String(buffer)           — Buffer to string

### js_air/glasses.js — Glasses Class

    export default class Glasses extends EventTarget {
        // Events: 'imu', 'button', 'brightness', 'display_mode', etc.
        // Internal: HID report polling, quaternion parsing
    }
    class RepeatingDeviceReportPoll                — Periodic HID report reader

### js_air/manager.js — Device Management

    export function hidSupported()                         — Check WebHID support
    export function canCommand(device)                     — Check device is commandable
    export async function hasActivated()                   — Check activation status
    export async function getFirmwareVersionInMcu()        — Read MCU firmware version
    export async function getFirmwareVersionInDp()         — Read DP firmware version
    export async function getFirmwareVersionInDsp()        — Read DSP firmware version
    export function Asc2Hex(value)                         — ASCII to hex conversion
    export async function upgradeInDsp(data)               — DSP firmware upgrade
    export async function isNeedUpgradeInDp()              — Check DP upgrade needed
    export async function upgradeInDp()                    — DP firmware upgrade

### js_light/protocol.js — Light Protocol

    export const NREAL_VENDOR_ID = 0x0486
    export const BOOT_PRODUCT_ID = 0x573C
    export const MESSAGES = { ... }
    export function cmd_build(msgId, payload, option)
    export function parse_rsp(rsp)
    export function bytes2Time(bytes)
    export function hex8(value)
    export function bytes2String(buffer)

### js_light/manager.js — Light Device Management

    export function hidSupported()
    export function canCommand(device)
    export async function hasActivated(glasses)
    export async function activate(timeStamp, flag)
    export async function deactivate()
    export async function getFirmwareVersionInMcu()
    export async function getFirmwareVersionInAudio()
    export async function getFirmwareVersionInOv580()
    export async function selectBinFile()
    export async function getSerialPort()
    export async function upgradeInMcuForSerial(data)
    export async function upgradeInMcu(data)
    export async function upgradeInDp()
    export async function getSN()

### Usage Example

    import { hidSupported, canCommand, getFirmwareVersionInMcu } from './js_air/manager.js';
    import Glasses from './js_air/glasses.js';

    if (hidSupported()) {
        const glasses = new Glasses();
        glasses.addEventListener('imu', (e) => {
            console.log('Quaternion:', e.detail);
        });
        const version = await getFirmwareVersionInMcu();
        console.log('MCU FW:', version);
    }

---

## 4. decky-XRGaming

Decky Loader plugin for Steam Deck XR gaming — manages Breezy XR driver, display modes, licensing.

### Installation / Setup

    1. Install Decky Loader on Steam Deck
    2. Install XRGaming plugin from Decky store
    3. Plugin auto-installs Breezy GNOME XR driver
    4. Connect supported AR glasses via USB-C

### File Structure

    plugin.json                         — Decky plugin metadata
    package.json                        — NPM dependencies
    tsconfig.json                       — TypeScript config
    main.py                             — Python backend (Decky RPC)
    src/
      index.tsx                         — Main plugin component + definePlugin()
      stableState.ts                    — Delayed state hook
      license.ts                        — License/tier management types
      types.d.ts                        — Module declarations (SVG, PNG, CSS)
      SupporterTierFeatureLabel.tsx      — Feature label component
      SupporterTierModal.tsx            — Supporter tier modal dialogs
      QrButton.tsx                      — QR code button component
      tutorials.tsx                     — Setup tutorial components
      showQrModal.tsx                   — QR modal launcher
      SupporterTierStatus.tsx           — Tier status display

### Python Backend (main.py)

    class Plugin:
        async def is_breezy_install_pending()    — Check if install in progress
        async def retrieve_config()              — Get XR driver config
        async def write_config(config)           — Write XR driver config
        async def write_control_flags(flags)     — Set driver control flags
        async def retrieve_driver_state()        — Get current driver state
        async def check_installation()           — Verify Breezy installed
        async def request_token(email)           — Request license token
        async def verify_token(token)            — Verify license token
        async def refresh_license()              — Refresh license status
        async def get_dont_show_again_keys()     — Get dismissed tutorial keys
        async def set_dont_show_again(key)       — Dismiss a tutorial
        async def reset_dont_show_again()        — Reset all tutorials
        async def force_reset_driver()           — Hard reset XR driver

    Uses: PyXRLinuxDriverIPC.xrdriveripc.XRDriverIPC for driver communication

### TypeScript Frontend — Key Exports

    // index.tsx
    export default definePlugin(() => { ... })   — Plugin entry point
    async function refreshConfig()
    async function retrieveDriverState(): Promise<DriverState>
    async function writeConfig(newConfig: Config)
    async function writeControlFlags(flags: Partial<ControlFlags>)
    async function requestToken(email: string): Promise<boolean>
    async function verifyToken(token: string): Promise<boolean>
    async function refreshLicense(): Promise<RefreshLicenseResponse>
    async function forceResetDriver()

    // license.ts
    export enum FeatureStatus { ACTIVE, TRIAL, EXPIRED, NONE }
    export interface License { features, tiers, trial_end, ... }
    export function featureEnabled(license, featureName): boolean
    export function trialTimeRemaining(license): number | undefined
    export function timeRemainingText(seconds): string | undefined
    export function featureSubtext(license, featureName): string

    // stableState.ts
    export function useStableState<T>(initialState, delay): [T, T, Dispatch]

    // tutorials.tsx
    export const tutorials: { [key: string]: tutorial }
    export function onChangeTutorial(key, brand, model, onConfirm, ...)

    // SupporterTierStatus.tsx
    export interface SupporterTierDetails { ... }
    export function supporterTierDetails(license): SupporterTierDetails
    export function SupporterTierStatus({details, ...}: Props)

---

## 5. mobileapp (Pebble Ring)

Kotlin Multiplatform (KMP) companion app for the Pebble smart ring — iOS/Android with BLE, MCP agent, encryption.

### Installation / Setup

    Prerequisites: Android Studio / Xcode, Kotlin 2.x, KMP plugin
    1. Clone repo
    2. Open in Android Studio (for shared + Android) or Xcode (for iOS)
    3. Sync Gradle (experimental/build.gradle.kts)

### Architecture (KMP)

    experimental/
      build.gradle.kts
      src/
        commonMain/kotlin/coredevices/    — Shared KMP code
        iosMain/kotlin/coredevices/       — iOS platform implementations
        androidMain/kotlin/coredevices/   — Android platform implementations

### Key Modules — commonMain

    coredevices/experimentalModule.kt           — DI module
    coredevices/ExperimentalDevices.kt          — Device registration

    ring/
      encryption/
        DocumentEncryptor.kt                    — Document encryption wrapper
        AesGcmCrypto.kt                         — AES-GCM encrypt/decrypt (expect)
        EncryptionKeyManager.kt                 — Key generation/storage (expect)
      ui/
        viewmodel/
          FeedViewModel.kt                      — Feed tab ViewModel
          SettingsViewModel.kt                  — Settings ViewModel
          RecordingDetailsViewModel.kt          — Recording details ViewModel
          NotesViewModel.kt                     — Notes ViewModel
          ReminderDetailsViewModel.kt           — Reminder details ViewModel
          ListenDialogViewModel.kt              — Audio listen dialog
          FilePicker.kt                         — File picker (expect)
        navigation/RingRoutes.kt                — Navigation routes
        screens/
          settings/
            SettingsBeeperContactsDialog.kt     — Beeper contacts dialog
            McpSandboxSettings.kt               — MCP sandbox config
            IndexSettings.kt                    — Index settings
            AddIntegration.kt                   — Integration add screen
          home/FeedTabContents.kt               — Feed tab
          home/NotesTabContents.kt              — Notes tab
          recording/RecordingDetails.kt         — Recording detail screen
          RingPairing.kt                        — Pairing flow (expect)
          RingDebug.kt                          — Debug screen (expect)
        components/
          chat/ChatInput.kt, ChatBubble.kt, ResponseBubble.kt, etc.
          recording/RecordingConversation.kt, RecordingTraceTimeline.kt
          QrCodeImage.kt                        — QR code display (expect)
      database/IntegrationTokenStorage.kt       — Token storage (expect)
      agent/
        builtin_servlets/
          messaging/
            SendBeeperMessageTool.kt            — MCP tool: send Beeper msg
            SearchBeeperForContactTool.kt       — MCP tool: search contacts
          reminders/NativeReminderFactory.kt    — Create native reminders
          clock/SetAlarmTool.kt, SetTimerTool.kt
      storage/RecordingStorage.kt               — Audio recording storage
      audio/M4aDecoder.kt, M4aEncoder.kt        — M4A codec
      model/CactusModelProvider.kt              — On-device AI model
      service/
        RingSync.kt                             — BLE sync service
        IndexNotificationManager.kt             — Notification manager
        RingBackgroundManager.kt                — Background service

### Key iOS-Specific Implementations

    actual class EncryptionKeyManager {
        actual fun generateKey(): KeyResult
        actual suspend fun saveKeyLocally(key, email)
        actual suspend fun getLocalKey(email): String?
        actual suspend fun saveToCloudKeychain(uiContext, key)
        actual suspend fun readFromCloudKeychain(uiContext): String?
    }

    actual object AesGcmCrypto {
        actual fun encrypt(plaintext: ByteArray, keyBase64: String): ByteArray
        actual fun decrypt(ivAndCiphertext: ByteArray, keyBase64: String): ByteArray
        actual fun keyFingerprint(keyBase64: String): String
    }

    actual class AudioRecorder : AutoCloseable {
        actual suspend fun startRecording(): RawSource
        actual suspend fun stopRecording()
        actual override fun close()
    }

    actual class AudioPlayer : AutoCloseable {
        actual fun playRaw(samples, sampleRate, encoding, channels)
        actual fun playAAC(samples: Source, sampleRate: Long)
        actual fun stop()
    }

    actual class RingCompanionDeviceManager(scope) {
        actual suspend fun unregister(satellite)
        actual suspend fun unregisterAll()
        actual suspend fun openPairingPicker(): CompanionRegisterResult
    }

    class IosRingPairingViewModel {
        sealed class PairingState { WaitingForBluetooth, Scanning, WaitingForPairing, Paired }
        fun startScanning()
        fun closePairingDialogue(result: Boolean)
    }

---

## 6. open-wearables

Health/wearable data aggregation platform — FastAPI backend, React frontend, MCP server for AI assistants.

### Installation / Setup

    # Docker (recommended)
    docker compose up -d
    # Admin: admin@admin.com / your-secure-password
    make seed                    # Optional: seed sample data

    # MCP Server
    cd mcp && uv sync --group code-quality
    cp config/.env.example config/.env
    # Edit config/.env: OPEN_WEARABLES_API_URL, OPEN_WEARABLES_API_KEY
    uv run start

    Access: Frontend :3000, API :8000, Docs :8000/docs, Flower :5555

### MCP Server Tools

    get_users(search?, limit=10) -> dict
        Discover users accessible via API key

    get_activity_summary(user_id, start_date, end_date) -> dict
        Daily activity: steps, calories, heart rate, intensity minutes

    get_sleep_summary(user_id, start_date, end_date) -> dict
        Sleep data for date range

    get_workout_events(user_id, start_date, end_date) -> dict
        Workout/exercise sessions

    get_timeseries(user_id, series_type, start_date, end_date) -> dict
        Granular time-series: weight, SpO2, HRV, intraday HR, etc.

### MCP Server Architecture

    mcp/
      app/
        main.py                              — FastMCP server entry
        config.py                            — Settings(BaseSettings)
        prompts.py                           — present_health_data() prompt
        utils.py                             — normalize_datetime()
        tools/
          users.py                           — get_users tool
          activity.py                        — get_activity_summary tool
          sleep.py                           — get_sleep_summary tool
          workouts.py                        — get_workout_events tool
          timeseries.py                      — get_timeseries tool
        services/
          api_client.py                      — OpenWearablesClient HTTP client
            __init__(self)
            _request(method, path, **kwargs)
            get_users(search?, limit)
            get_user(user_id)
            get_sleep_summaries(user_id, start, end)
            get_workouts(user_id, start, end)
            get_activity_summaries(user_id, start, end)
            get_timeseries(user_id, series_type, start, end)

### Claude Desktop Config

    {
      "mcpServers": {
        "open-wearables": {
          "command": "uv",
          "args": ["run", "--frozen", "--directory", "/path/to/mcp", "start"]
        }
      }
    }

### Backend API Routes (FastAPI)

    Auth:
      POST /auth/login           — Login, returns JWT
      POST /auth/logout          — Logout
      POST /auth/change-password — Change password
      GET  /auth/me              — Current developer info
      PUT  /auth/me              — Update developer info

    Users:
      GET    /users              — List users (paginated)
      GET    /users/{id}         — Get user
      POST   /users              — Create user
      DELETE /users/{id}         — Delete user
      PUT    /users/{id}         — Update user

    Health Data:
      GET /events/workouts                 — List workouts
      GET /events/sleep                    — List sleep sessions
      GET /health-scores                   — List health scores
      GET /data-sources/{user_id}          — User data sources

    Webhooks:
      POST /webhooks/{provider}            — Provider webhook push
      GET  /webhooks/{provider}/verify     — Provider webhook verify

    Applications:
      GET/POST/DELETE /applications        — CRUD
      POST /applications/{id}/rotate       — Rotate secret

    API Keys:
      GET/POST/DELETE/PUT /api-keys        — CRUD
      POST /api-keys/{id}/rotate           — Rotate key

### Backend Models

    User, Developer, Application, ApiKey, RefreshToken
    DataSource, DataPointSeries, DataPointSeriesArchive
    EventRecord, EventRecordDetail, WorkoutDetails, SleepDetails
    HealthScore, PersonalRecord, SeriesTypeDefinition
    UserConnection, ProviderSetting, ProviderPriority
    DeviceTypePriority, ArchivalSetting
    Invitation, UserInvitationCode

### Algorithms

    sleep.py:
      calculate_duration_score(start, end, awake_minutes) -> int
      calculate_total_stages_score(deep_minutes, rem_minutes) -> int
      calculate_bedtime_consistency_score(...) -> int
      calculate_interruptions_score(...) -> int
      calculate_overall_sleep_score(duration, stages, bedtime, interruptions) -> int

    resilience.py:
      hr_to_rr_intervals_ms(hr_series) -> ndarray
      calculate_rmssd(hr_series) -> float
      calculate_sdnn(hr_series) -> float
      calculate_hrv_cv(hrv_series) -> float

---

## 7. headset-utils

Rust library for unified AR glasses access — abstracts XREAL Air/Light, Rokid Air, Grawoow G530, MadGaze Glow.

### Installation / Setup

    # Add to Cargo.toml
    [dependencies]
    headset-utils = { path = "./headset-utils" }

    # Build
    cargo build

    # Run examples
    cargo run --example euler_60
    cargo run --example set_to_3d

### File Structure

    Cargo.toml          — Package manifest
    src/
      lib.rs            — Core traits, enums, connection manager
      nreal_air.rs      — XREAL Air implementation
      nreal_light.rs    — XREAL Light implementation (+ SLAM camera)
      rokid.rs          — Rokid Air implementation
      grawoow.rs        — Grawoow G530 implementation
      mad_gaze.rs       — MadGaze Glow implementation
      naive_cf.rs       — Naive complementary filter fusion
      util.rs           — USB device helpers
    examples/
      euler_60.rs       — Print Euler angles at 60Hz
      set_to_3d.rs      — Set display to 3D mode

### Core Trait — ARGlasses

    pub trait ARGlasses: Send {
        // Implemented by all glasses types
        // Provides: read_packet, set_display_mode, get_serial, etc.
    }

### Core Trait — Fusion

    pub trait Fusion: Send {
        fn attitude_frd_rad(&self) -> Vector3<f32>    — Euler angles (radians)
        fn attitude_frd_deg(&self) -> Vector3<f32>    — Euler angles (degrees)
    }

### Public Enums

    pub enum Error { ... }                     — Error types
    pub enum GlassesEvent {
        AccGyro { ... }                        — IMU accelerometer + gyroscope
        Magnetometer { ... }                   — Magnetometer data
        KeyEvent(u8)                           — Button press
        AmbientLight(u16)                      — Ambient light sensor
        Vsync                                  — Display vsync
        ProximityNear / ProximityFar           — Proximity sensor
    }
    pub enum DisplayMode { SameOnBoth, Stereo, HighRefreshRate }
    pub enum Side { Left, Right, Both }

### Public Structs

    pub struct NrealAir
      pub fn new() -> Result<Self>
      pub fn new(fd: isize) -> Result<Self>    — From file descriptor
      pub fn get_config_json() -> &JsonValue
      pub fn read_packet() -> Result<(GlassesEvent, GlassesEvent)>

    pub struct NrealLight
      pub fn new() -> Result<Self>
      pub fn new(mcu_fd, ov580_fd) -> Result<Self>
      pub fn get_config_json() -> &JsonValue
      pub fn read_packet() -> Result<GlassesEvent>

    pub struct NrealLightSlamCamera
      pub fn new() -> Result<Self>
      pub fn new(fd) -> Result<Self>
      pub fn get_frame(timeout: Duration) -> Result<NrealLightSlamCameraFrame>

    pub struct RokidAir
      pub fn new() -> Result<Self>
      pub fn new(fd: isize) -> Result<Self>

    pub struct GrawoowG530
      pub fn new() -> Result<Self>
      pub fn new(mcu_fd, ov580_fd) -> Result<Self>

    pub struct MadGazeGlow
      pub fn new() -> Result<Self>
      pub fn set_sceen_brightness(brightness: u8) -> Result<()>

    pub struct NaiveCF
      pub fn new(glasses: Box<dyn ARGlasses>) -> Result<Self>
      pub fn get_correction(...) -> ...
      pub fn get_rotation(...) -> ...

    pub struct Connection
      pub fn start() -> Result<&'static Connection>
      pub fn stop() -> Result<()>
      pub fn read_fusion<T>(f: &dyn Fn(&mut Box<dyn Fusion>) -> T) -> Result<T>

    pub struct CameraDescriptor { ... }
    pub struct DisplayMatrices { ... }

### Factory Functions

    pub fn any_glasses_or_fail() -> Result<Box<dyn ARGlasses>>
    pub fn any_glasses() -> Result<Box<dyn ARGlasses>>
    pub fn any_fusion() -> Result<Box<dyn Fusion>>

### Utility Functions (util.rs)

    pub fn get_device_vid_pid(vid, pid) -> Result<Device<GlobalContext>>
    pub fn get_interface_for_endpoint(device, endpoint) -> Result<u8>

### Usage Example

    use headset_utils::*;

    let glasses = any_glasses()?;
    let mut fusion = NaiveCF::new(glasses)?;

    loop {
        let angles = fusion.attitude_frd_deg();
        println!("Yaw: {}, Pitch: {}, Roll: {}", angles.x, angles.y, angles.z);
    }

---

## 8. spidgets-3dof

Socket.IO + Node.js server for streaming 3DOF head-tracking data to web-based SBS (side-by-side) AR displays.

### Installation / Setup

    npm install
    node ar-server.js [--port 3000] [--drift 0.0001]

### File Structure

    package.json                        — Dependencies: socket.io, express
    ar-server.js                        — Main server + IMU subprocess
    webroot/
      app.js                            — Main SBS client (Alpine.js + Socket.IO)
      compat/
        data.json                       — Compatibility data
        app.js                          — Legacy compatibility client
      widgets/
        chart-widget.js                 — ChartWidget extends SDiv
        weather-widget.js               — WeatherWidget extends SDiv
      vendor/
        sbs.min.js                      — SBS layer custom element
        socket.io.min.js                — Socket.IO client
        spidgets-core.min.js            — Spidgets core framework
        alpinejs.min.js                 — Alpine.js reactive framework

### Server API (ar-server.js)

    Socket.IO Events (server -> client):
      'cam'      — Camera Euler angles [x, y, z]
      'camstart' — Initial camera position on connect

    Socket.IO Events (client -> server):
      'tare'     — Recalibrate zero position

    Functions:
      emit(event, data)                — Broadcast to all clients
      broadcastCam(x, y, z, first)     — Send camera update
      calibrate()                      — Tare/zero position

    CLI Options:
      --port <number>                  — Server port (default 3000)
      --drift <float>                  — Drift compensation rate

    IMU Subprocess:
      Spawns external IMU reader process
      Parses stdout for Euler angles (space-separated)
      Applies drift compensation over time

### Client API (webroot/app.js)

    Alpine.js Store 'app':
      x, y, z                          — Current rotation (degrees)

    Functions:
      initCamera(yaw, firstConnect)    — Set initial camera
      setCamera(vecArr)                — Update camera from socket data

    Socket.IO:
      socket.on('cam', setCamera)
      socket.on('camstart', (data) => initCamera(data[1], true))

### Widget API

    class ChartWidget extends window.spidgets.SDiv { ... }
    class WeatherWidget extends window.spidgets.SDiv { ... }

### Usage Example

    # Start server with custom port
    node ar-server.js --port 8080

    # Client connects automatically via Socket.IO
    # SBS display renders at http://localhost:8080/

---

## 9. real_utilities

C++ HID library for XREAL glasses — two protocol versions for control and IMU interfaces.

### Installation / Setup

    Prerequisites: hidapi library, C++17 compiler
    # Build
    g++ -std=c++17 real_utilities.cpp protocol.cpp protocol3.cpp -lhidapi -o real_utilities

### File Structure

    protocol.h              — Protocol v1 (control interface) header
    protocol.cpp            — Protocol v1 implementation
    protocol3.h             — Protocol v3 (IMU interface) header
    protocol3.cpp           — Protocol v3 implementation
    real_utilities.cpp      — Main program, HID device management

### Protocol v1 — Control Interface (protocol.h)

    class protocol {
        typedef struct {
            uint16_t msgId;
            uint8_t status;
            uint8_t payload[200];
            uint16_t payload_size;
        } parsed_rsp;

        static void listKnownCommands();
        static std::string keyForHex(uint16_t hex);
        static uint16_t hexForKey(std::string key);
        static void parse_rsp(const uint8_t* buffer_in, int size, parsed_rsp* result);
        static int cmd_build(uint16_t msgId, const uint8_t* p_buf, int p_size,
                             uint8_t* cmd_buf, int cb_size);
        static int cmd_build(std::string msg_id, const uint8_t* p_buf, int p_size,
                             uint8_t* cmd_buf, int cb_size);
        static void print_summary_rsp(parsed_rsp* result);
    };

### Protocol v3 — IMU Interface (protocol3.h)

    class protocol3 {
        typedef struct {
            uint8_t msgId;
            uint8_t payload[200];
            uint16_t payload_size;
        } parsed_rsp;

        static void listKnownCommands();
        static std::string keyForHex(uint8_t hex);
        static uint8_t hexForKey(std::string key);
        static void parse_rsp(const uint8_t* buffer_in, int size, parsed_rsp* result);
        static int cmd_build(uint8_t msgId, const uint8_t* p_buf, int p_size,
                             uint8_t* cmd_buf, int cb_size);
        static int cmd_build(std::string msg_id, const uint8_t* p_buf, int p_size,
                             uint8_t* cmd_buf, int cb_size);
        static void print_summary_rsp(parsed_rsp* result);
    };

### Main Program Functions (real_utilities.cpp)

    hid_device* open_device(int interface_num)       — Open HID device by interface
    void print_bytes(const uint8_t* buf, int size)   — Hex dump
    void print_chars(const uint8_t* buf, int size)   — ASCII dump

    int write_control(hid_device*, uint16_t msgId, const uint8_t* p, int p_size)
    int write_control(hid_device*, std::string msg_id, const uint8_t* p, int p_size)
    protocol::parsed_rsp read_control(hid_device*, int timeout_ms)

    int write_imu(hid_device*, uint8_t msgId, const uint8_t* p, int p_size)
    int write_imu(hid_device*, std::string msg_id, const uint8_t* p, int p_size)
    protocol3::parsed_rsp read_imu(hid_device*, int timeout_ms)
    void read_imu_get_rsp(hid_device*, int timeout_ms, protocol3::parsed_rsp* out)

### Usage Example

    // Open control and IMU interfaces
    hid_device* ctrl = open_device(3);   // Control interface
    hid_device* imu = open_device(4);    // IMU interface

    // Send command
    write_control(ctrl, "GET_FIRMWARE_VERSION", nullptr, 0);
    auto rsp = read_control(ctrl, 1000);

    // Read IMU data
    auto imu_rsp = read_imu(imu, 250);

---

## 10. imu-inspector

Single-file C program for inspecting XREAL glasses HID IMU reports.

### Installation / Setup

    Prerequisites: hidapi library
    gcc inspector.c -lhidapi -o inspector
    ./inspector

### File: inspector.c

    void fix_report()                                  — Fix/normalize raw HID report
    void print_report()                                — Pretty-print parsed IMU data
    void print_bytes(const uint8_t* buf, size_t len)   — Hex dump of raw bytes
    void print_line(const char* s)                     — Formatted line output
    hid_device* open_device()                          — Open XREAL HID device
    int main(void)                                     — Entry: open device, read loop

### Usage

    ./inspector
    # Continuously prints IMU quaternion/acceleration data from connected glasses

---

## 11. frame-codebase

Brilliant Labs Frame AR glasses firmware — nRF52840 + FPGA + Lua VM + TFLite Micro.

### Installation / Setup

    Prerequisites: nRF Connect SDK, ARM GCC, nrfjprog
    1. Clone repo
    2. Build with nRF Connect SDK / west build
    3. Flash via nrfjprog or DFU bootloader

### File Structure

    source/
      application/
        main.c, main.h                   — App entry, shutdown()
        bluetooth.c, bluetooth.h          — BLE setup/communication
        spi.c, spi.h                      — SPI bus driver
        flash.c, flash.h                  — Flash storage
        watchdog.c, watchdog.h            — Watchdog timer
        compression.h                     — Decompression API
        camera_configuration.h            — Camera config
        luaport.h                         — Lua VM integration
        tflm_wrapper.h                    — TFLite Micro wrapper
        models/
          hello_world_int8.h              — Hello world TFLite model
          person_detect.h                 — Person detection model
          person_detect_rgb.h             — RGB person detection model
          fomo_beer_can.h                 — FOMO object detection model
        lua_libraries/
          frame_lua_libraries.h           — All Lua library registrations
          led.c                           — LED control (Lua binding)
          display.c                       — Display rendering (Lua binding)
          system.c                        — System control (Lua binding)
          time.c                          — Time/date (Lua binding)
          file.c                          — LittleFS file system (Lua binding)
          imu.c                           — IMU sensor (Lua binding)
          experiment_common.c/h           — ML experiment utilities
          experiment_vww_rgb.c            — Person detection experiment
      bootloader/
        main.c                            — DFU bootloader
      radio_test/
        main.c, radio_test.c/h            — RF test suite
      fpga/
        fpga_application.h                — FPGA application interface
        modules/camera/                   — Camera pipeline
        cocotb/                           — FPGA verification tests
      error_logging.h                     — Error macros

### TFLite Micro API (tflm_wrapper.h)

    // Hello World model
    tflm_status_t tflm_initialize(void)
    tflm_status_t tflm_infer(float input, float* output)
    tflm_status_t tflm_initialize_int8(void)
    tflm_status_t tflm_infer_int8(float input, float* output)
    tflm_status_t tflm_get_float_model_info(tflm_model_info_t* info)
    tflm_status_t tflm_get_int8_model_info(tflm_model_info_t* info)

    // FOMO object detection
    tflm_status_t fomo_initialize(void)
    tflm_status_t fomo_infer(const uint8_t* input_grayscale, int8_t* output_grid)
    bool fomo_is_initialized(void)

    // Person detection
    tflm_status_t person_detect_initialize(void)
    tflm_status_t person_detect_infer(const uint8_t* input_image, int8_t* output_scores)
    bool person_detect_is_initialized(void)

### Bluetooth API (bluetooth.h)

    void bluetooth_setup(void)
    bool bluetooth_is_paired(void)
    void bluetooth_unpair(void)
    bool bluetooth_is_connected(void)
    bool bluetooth_send_data(const uint8_t* data, size_t length)

### Lua Libraries (exposed to Lua VM)

    -- LED
    frame.led.set_color(r, g, b)

    -- Display
    frame.display.assign_color(index, r, g, b)
    frame.display.assign_color_ycbcr(index, y, cb, cr)
    frame.display.bitmap(x, y, width, data)
    frame.display.text(text, x, y, options)
    frame.display.show()
    frame.display.set_brightness(level)
    frame.display.write_register(addr, value)
    frame.display.power_save(enable)

    -- System
    frame.update()
    frame.sleep(seconds)
    frame.stay_awake(enable)
    frame.battery_level()
    frame.fpga_read(addr, len)
    frame.fpga_write(addr, data)

    -- Time
    frame.time.utc()
    frame.time.zone()
    frame.time.date()

    -- File (LittleFS)
    frame.file.open(path, mode)
    frame.file.read(handle, bytes)
    frame.file.write(handle, data)
    frame.file.close(handle)
    frame.file.remove(path)
    frame.file.rename(old, new)
    frame.file.mkdir(path)
    frame.file.listdir(path)
    frame.file.require(module)

    -- IMU
    frame.imu (callback-based sensor data)

    -- Experiment (ML)
    frame.experiment.run_person_detection()

### Flash / SPI / Compression

    void flash_erase_page(uint32_t address)
    void flash_write(uint32_t address, const uint32_t* data, size_t length)
    void flash_wait_until_complete(void)
    void flash_get_info(size_t* page_size, size_t* total_size)
    uint32_t flash_base_address(void)

    void spi_configure(void)
    void spi_read(spi_device_t device, uint8_t* tx, uint8_t* rx, size_t len)
    void spi_write(spi_device_t device, uint8_t* tx, size_t len)

    int compression_decompress(size_t dst_size, const uint8_t* src, ...)

### Experiment Utilities (experiment_common.h)

    int jpeg_decode_grayscale_scaled(const uint8_t* data, size_t size, ...)
    int jpeg_decode_grayscale(const uint8_t* data, size_t size, ...)
    void upscale_90_to_96_with_rotation(const uint8_t* src, uint8_t* dst)
    int jpeg_decode_rgb_scaled(const uint8_t* data, size_t size, ...)
    void upscale_90_to_96_rgb_with_rotation(const uint8_t* src, uint8_t* dst)
    const char* experiment_get_name(void)
    void experiment_register_lua_functions(lua_State* L, int table)
    void lua_open_experiment_library(lua_State* L)

---

## 12. beatsync

Turborepo monorepo for multi-device synchronized audio playback — Bun server + Next.js client.

### Installation / Setup

    bun install                  # Install all deps
    bun dev                      # Start client + server
    bun client                   # Client only (port 3000)
    bun server                   # Server only (port 8080)
    bun build                    # Build all

    # Environment
    apps/client/.env: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_WS_URL
    apps/server/.env: S3_BUCKET_NAME, S3_PUBLIC_URL, S3_ENDPOINT, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY

### Architecture

    apps/
      client/               — Next.js 15, React 19, Tailwind v4, Shadcn/ui
      server/               — Bun HTTP + WebSocket server
    packages/
      shared/               — Zod schemas (@beatsync/shared)

### Server Managers

    class GlobalManager        — Singleton, manages all rooms
    class RoomManager          — Per-room: clients, audio, playback, spatial, chat
    class ChatManager          — Per-room: message history
    class BackupManager        — Periodic state backup to R2
    class MusicProviderManager — External music search/streaming

### WebSocket Protocol (Zod-validated discriminated unions)

    Client -> Server (WSRequest types):
      PLAY                     — Request play at synced time
      PAUSE                    — Request pause
      NTP_REQUEST              — NTP time sync request
      MOVE_CLIENT              — Move client position (spatial)
      SYNC                     — Request state sync
      SET_PLAYBACK_CONTROLS    — Set admin/everyone permissions
      SEARCH_MUSIC             — Search external music
      STREAM_MUSIC             — Start music stream
      SET_GLOBAL_VOLUME        — Set master volume
      SEND_CHAT_MESSAGE        — Chat message
      AUDIO_SOURCE_LOADED      — Confirm audio ready
      REORDER_AUDIO_SOURCES    — Reorder playlist
      SET_METRONOME            — Configure metronome
      SET_LOW_PASS_FREQ        — Set low-pass filter
      SET_LISTENING_SOURCE     — Set spatial listening position
      START_SPATIAL_AUDIO      — Enable spatial audio
      STOP_SPATIAL_AUDIO       — Disable spatial audio
      LOAD_DEFAULT_TRACKS      — Load preset tracks
      REORDER_CLIENT           — Reorder client position
      SET_ADMIN                — Promote/demote admin
      DELETE_AUDIO_SOURCES     — Remove audio sources
      SEND_IP                  — Send client IP

    Server -> Client (WSBroadcast types):
      ROOM_STATE               — Full room state
      SET_AUDIO_SOURCES        — Audio source list update
      CHAT_UPDATE              — New chat messages
      LOAD_AUDIO_SOURCE        — Load audio request
      SPATIAL_CONFIG           — Spatial audio gain config
      STOP_SPATIAL_AUDIO       — Spatial audio stopped
      GLOBAL_VOLUME_CONFIG     — Volume update
      METRONOME_CONFIG         — Metronome update
      LOW_PASS_CONFIG          — Filter update
      STREAM_JOB_UPDATE        — Stream progress
      SCHEDULED_ACTION         — Synchronized play/pause
      DEMO_USER_COUNT          — Demo mode user count
      DEMO_AUDIO_READY_COUNT   — Demo audio ready count

    Server -> Single Client (WSUnicast types):
      NTP_RESPONSE             — NTP time sync response
      MUSIC_SEARCH_RESPONSE    — Search results

### Shared Types (packages/shared/)

    types/basic.ts:
      PositionSchema, AudioSourceSchema, ChatMessageSchema

    types/WSRequest.ts:
      LocationSchema, ClientActionEnum, NTPRequestPacketSchema
      PlayActionSchema, PauseActionSchema, MoveClientSchema
      SetPlaybackControlsSchema, SearchMusicSchema, StreamMusicSchema
      SetGlobalVolumeSchema, SendChatMessageSchema, etc.

    types/WSBroadcast.ts:
      ClientDataSchema, SetAudioSourcesSchema, ChatUpdateSchema
      SpatialConfigSchema, GlobalVolumeConfigSchema, ScheduledActionSchema

    types/WSUnicast.ts:
      NTPResponseMessageSchema, MusicSearchResponseSchema

    types/HTTPRequest.ts:
      GetUploadUrlSchema, UploadCompleteSchema, RoomSchema
      DiscoverRoomsSchema, GetActiveRoomsSchema

### Time Synchronization (NTP-inspired)

    1. Client sends NTP_REQUEST with t0
    2. Server stamps t1/t2
    3. Client receives at t3
    4. EMA smoothing (alpha=0.2) for RTT
    5. Min 10 measurements before "synced"
    6. Play/pause = scheduled actions with serverTimeToExecute

### HTTP Endpoints

    POST /upload/get-presigned-url    — Get R2 presigned upload URL
    POST /upload/complete             — Confirm upload complete
    GET  /rooms                       — List active rooms
    GET  /rooms/discover              — Discover rooms

---

## 13. sam3

Segment Anything Model 3 — image/video segmentation with visual grounding, prompt encoding, and tracking.

### Installation / Setup

    pip install -e .
    # Or use torch hub
    # Requires: PyTorch, torchvision, numpy, PIL

### File Structure

    sam3/
      __init__.py
      model_builder.py              — All model construction functions
      visualization_utils.py        — Visualization helpers
      sam/
        __init__.py
        common.py                   — MLPBlock, LayerNorm2d
        transformer.py              — TwoWayTransformer, Attention
        prompt_encoder.py           — PromptEncoder, PositionEmbeddingRandom
        mask_decoder.py             — MaskDecoder, MLP
        rope.py                     — Rotary Position Embedding
      agent/
        __init__.py
        agent_core.py               — Agent core logic
        client_llm.py               — LLM client
        client_sam3.py              — SAM3 model client
        inference.py                — Inference pipeline
        viz.py                      — Agent visualization
        helpers/
          memory.py, roi_align.py, boxes.py, rle.py, keypoints.py, masks.py
    scripts/
      measure_speed.py              — Benchmarking
      qualitative_test.py           — Qualitative evaluation
      eval/                         — Evaluation scripts

### Top-Level Builder Functions (model_builder.py)

    def build_sam3_image_model(
        checkpoint_path, device="cuda", eval_mode=True,
        compile_mode=None, use_fa3=False, ...
    ) -> SAM3Model

    def build_sam3_video_model(
        checkpoint_path, device="cuda", eval_mode=True, ...
    ) -> SAM3VideoModel

    def build_sam3_video_predictor(*args, gpus_to_use=None, **kwargs)

    def build_sam3_multiplex_video_model(
        checkpoint_path, device="cuda", ...
    ) -> SAM3MultiplexModel

    def build_sam3_multiplex_video_predictor(...)

    def build_sam3_predictor(
        checkpoint_path, device="cuda", ...
    ) -> SAM3Predictor

    def download_ckpt_from_hf(version="sam3") -> str

    def build_tracker(
        checkpoint_path, device="cuda", ...
    ) -> Tracker

### SAM Core Components

    class PromptEncoder(nn.Module):
        get_dense_pe() -> Tensor
        forward(points, boxes, masks) -> (sparse, dense)

    class MaskDecoder(nn.Module):
        forward(image_embeddings, image_pe, sparse_prompt, dense_prompt, ...) -> (masks, iou)
        predict_masks(image_embeddings, ...) -> (masks, iou)

    class TwoWayTransformer(nn.Module):
        forward(image_embedding, image_pe, point_embedding) -> (queries, keys)

    class Attention(nn.Module):
        forward(q, k, v) -> Tensor

    class PositionEmbeddingRandom(nn.Module):
        forward(size: Tuple[int, int]) -> Tensor
        forward_with_coords(coords, image_size) -> Tensor

### Visualization Utilities

    generate_colors(n_colors=256)
    show_img_tensor(img_batch, vis_img_idx=0)
    draw_box_on_image(image, box, color)
    plot_bbox(image, bboxes, labels, scores, ...)
    plot_mask(mask, color, ax)
    visualize_frame_output(frame_idx, video_frames, outputs)
    render_masklet_frame(img, outputs, frame_idx, alpha)
    save_masklet_video(video_frames, outputs, out_path, alpha, fps)
    save_masklet_image(frame, outputs, out_path, alpha)

### Usage Example

    from sam3.model_builder import build_sam3_predictor, download_ckpt_from_hf

    ckpt = download_ckpt_from_hf("sam3")
    predictor = build_sam3_predictor(ckpt, device="cuda")

    # For video
    from sam3.model_builder import build_sam3_video_predictor
    video_predictor = build_sam3_video_predictor(ckpt, device="cuda")

---

## 14. overpass-turbo

Web-based IDE for querying OpenStreetMap data via the Overpass API.

### Installation / Setup

    npm install
    npm run build
    npm run dev       # Development server

### File Structure

    js/
      index.ts                  — App entry point
      ide.ts                    — IDE class (editor, dialogs, export)
      overpass.ts               — Overpass API query engine
      query.ts                  — Query parser
      ffs.ts                    — Free-form search / Wizard
      map.ts                    — Leaflet map integration
      settings.ts               — Settings management
      i18n.ts                   — Internationalization
      autorepair.ts             — Query auto-repair
      nominatim.ts              — Nominatim geocoding
      shortcuts.ts              — Keyboard shortcuts
      configs.ts                — App configuration
      misc.ts                   — Miscellaneous utilities
      popup.ts                  — Map popups
      PopupIcon.ts              — Custom popup icons
      sync-with-osm.ts          — OSM data sync
      OSM4Leaflet.ts            — OSM-to-Leaflet conversion
      GeoJsonNoVanish.ts        — GeoJSON layer that persists
      leaflet.polylineoffset.ts — Polyline offset plugin
      ffs/free.ts               — Free-form search impl
      jsmapcss/Rule.ts          — MapCSS rule parser
      jsmapcss/Condition.ts     — MapCSS condition parser
    locales/                    — 35+ language translations

### Core Classes

    class Overpass (overpass.ts):
      // Main query engine
      type QueryLang = "xml" | "OverpassQL" | "SQL"
      handlers: { onProgress, onDone, onEmptyMap, onDataReceived,
                  onAbort, onAjaxError, onQueryError, onStyleError,
                  onQueryErrorLine, onRawDataPresent, onGeoJsonReady,
                  onPopupReady }
      rerender(userMapCSS)       — Re-render with custom MapCSS

    class IDE (ide.ts):
      codeEditor                 — CodeMirror editor instance
      waiter                     — Loading/progress indicator
      // Export functions, dialog management, run query

    class parser (query.ts):
      // Query string parser

    class i18n (i18n.ts):
      t(key)                     — Translate key
      // Supports 35+ languages

    class Settings (settings.ts):
      define_setting(name, type, default, version)
      export_image_scale: boolean
      export_image_attribution: boolean

### Free-Form Search (ffs.ts)

    export function ffs_construct_query(search, callback, ...)
        Build Overpass query from natural language search

    export function ffs_repair_search(search, callback)
        Attempt to repair invalid search query

    export function ffs_invalidateCache()
        Clear FFS cache

### Query Auto-Repair (autorepair.ts)

    export default function autorepair(q, lng)
        Automatically fix common query errors

### Usage Example

    // Programmatic query
    import overpass from './overpass';

    overpass.handlers["onDataReceived"] = (data, type) => {
        console.log('Received:', data);
    };
    overpass.handlers["onDone"] = () => { console.log('Query complete'); };

    // Run query
    overpass.run_query('[out:json];node["amenity"="cafe"]({{bbox}});out;');

---

## 15. rayneo-setup / rayneo-6dof / rayneo-mit

Unity projects for RayNeo X2 AR glasses using the RayNeo OpenXR ARDK.

### Installation / Setup

    Prerequisites: Unity 2022.3+, RayNeo OpenXR ARDK package (1.0.0 or 1.1.2)

    1. Open project in Unity
    2. Import RayNeo OpenXR ARDK via Package Manager
    3. Build for Android (RayNeo X2 target)
    4. Deploy via ADB to RayNeo X2

### rayneo-setup — File Structure

    Assets/
      Scenes/SampleScene.unity                           — Main scene
      InfographicElements_UI/Scripts/
        UITextTypeWriter.cs                              — Typewriter text effect
        NumberCOunt.cs                                   — Number counter animation
      Samples/RayNeo OpenXR ARDK/1.1.2/Hello RayNeo/
        Scenes/
          Entry.unity                                    — Entry/launcher scene
          HUD.unity, HUD 1.unity, HUD 2.unity            — HUD display scenes
          Algorithm/
            FacialRecog.unity                            — Facial recognition demo
            Slam.unity                                   — SLAM demo
            SensorTrans.unity                            — Sensor transform demo
            PlaneDetection.unity                         — Plane detection demo
          Common/
            ShareCamera.unity                            — Camera sharing demo
            RayNeoInfoDeviceName.unity                   — Device info display
            DualeyeDiffrentDisplay.unity                 — Dual-eye rendering
          Interactive/
            CustomRayPoint.unity                         — Custom ray pointer
            BaseInteraction.unity                        — Base interaction demo
            GazeActive.unity                             — Gaze activation
            IPC.unity                                    — Inter-process communication
            Lattice.unity                                — Lattice menu demo
            TouchEvent.unity                             — Touch event handling
        Scripts/
          KillSelf.cs                                    — Auto-destroy after delay
          ResetHeadTrack.cs                              — Head tracking reset
          Scene1Ctrl.cs                                  — Scene navigation controller
          Algorithm/
            PlaneDetection/TestPlaneDetection.cs         — Plane detection sample
            Facial/CreateCube.cs                         — AR cube creation
            Facial/TestRuntimeFacial.cs                  — Runtime facial recognition
            Sensor/TestSensorAlgorithm.cs                — Sensor data display
            Sensor/CompassMgr/CompassGenerate.cs         — Compass visualization
            SlamDemoCtrl.cs                              — SLAM cube placement
          SampleScene/
            SampleSceneCtrl.cs                           — Scene launcher
            SampleCubeCtrl.cs                            — Interactive cube
            RayNeoInfo/TestRayNeoInfoExtension.cs        — Device name display
          Interactive/
            TestIPC.cs                                   — IPC demo (ring, GPS)
            RingTouchCube.cs                             — Ring touch interaction
            TestTouchEvent.cs                            — Touch event testing
            ShareCameraCtrl.cs                           — Camera share control
            BaseInteraction.cs                           — Base interaction
          Tool/
            ShowFps.cs                                   — FPS counter
            GetDeviceInfo.cs                             — Device info query
            SetCanvasOverlay.cs                          — Canvas overlay setup
            CameraPermissionRequest.cs                   — Camera permission

### Key Classes (all projects share similar patterns)

    class SampleSceneCtrl : MonoBehaviour
      void OnBtnClick(string sceneName)      — Navigate to scene
      void CloseApp()                        — Exit application
      void OpenBatteryInfo()                 — Show battery
      void CloseBatteryInfo()                — Hide battery

    class Scene1Ctrl : MonoBehaviour
      void OnDoubleTapCallBack()             — Double-tap handler
      LatticeButton m_defaultSelectBtn       — Default lattice selection
      LatticeButton m_level2DefaultSelectBtn — Level 2 selection
      LatticeButton m_deleteLevel1Btn        — Delete actions
      LatticeButton m_backBtn               — Back navigation

    class TestPlaneDetection : MonoBehaviour
      // Uses RayNeo plane detection API
      // Visualizes detected planes as meshes

    class SlamDemoCtrl : MonoBehaviour
      GameObject m_Cube                      — Cube prefab
      int m_LineCount = 10                   — Grid size
      float m_CubeSpace = 0.3f              — Cube spacing
      void OnPostUpdate(Pose pose)           — SLAM pose callback

    class TestRuntimeFacial : MonoBehaviour
      Text Distance                          — Face distance display
      // Uses RayNeo facial recognition API

    class TestSensorAlgorithm : MonoBehaviour
      // Reads compass/azimuth from RayNeo sensor API
      void GetAzimuth()                      — Read azimuth value

    class TestIPC : MonoBehaviour
      RayTrackedPoseDriver m_rayDriver       — Ray input driver
      Text m_gpsInfo                         — GPS data display
      RingTouchCube m_RingCube               — Ring interaction

    class SampleCubeCtrl : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler, IPointerClickHandler
      void OnPointerEnter(PointerEventData)  — Gaze enter
      void OnPointerExit(PointerEventData)   — Gaze exit
      void OnPointerClick(PointerEventData)  — Gaze click
      void ModifyRotation()                  — Toggle rotation

    class ResetHeadTrack : MonoBehaviour
      void OnReset()                         — Reset head tracking origin

### rayneo-6dof — Additional Scenes

    Includes MetaSpace demo with portal effects:
      FantasyPortalSceneSelect.cs            — Scene selection
      FantasyPortalCameraOrbit.cs            — Camera orbit control
      FantasyPortalRotation.cs               — Object rotation
      RadomPlacment.cs                       — Random object placement
      PlanarReflection.cs                    — Planar reflection rendering
      PreviewObject.cs                       — Object preview rotation

### rayneo-mit — Same structure as rayneo-setup (ARDK 1.1.2)

    Identical sample scripts and scenes, with MIT license variant.

### RayNeo OpenXR ARDK Key APIs (from samples)

    // Head Tracking
    RayTrackedPoseDriver                     — Ray-based pose tracking
    ResetHeadTrack                           — Recenter tracking

    // Interaction
    LatticeButton                            — Grid menu button
    IPointerEnterHandler/ExitHandler/ClickHandler — Gaze interaction

    // Algorithms
    Plane Detection API                      — Detect horizontal/vertical planes
    Facial Recognition API                   — Face detection + distance
    SLAM API                                 — 6DOF tracking with pose callbacks
    Sensor API                               — Compass, azimuth, IMU data

    // Display
    DualeyeDiffrentDisplay                   — Per-eye rendering
    Canvas Overlay                           — UI overlay on AR view

---

## Cross-Reference: Protocol Compatibility

    | Glasses       | Protocol Lib     | Interface  | VID:PID       |
    |---------------|------------------|------------|---------------|
    | XREAL Air     | js_air/protocol  | WebHID     | 0x3318:0x0423 |
    | XREAL Light   | js_light/protocol| WebHID     | 0x0486:0x573C |
    | XREAL (native)| real_utilities   | hidapi     | 0x3318:0x0423 |
    | XREAL (Rust)  | headset-utils    | libusb     | auto-detect   |
    | XREAL (C)     | imu-inspector    | hidapi     | auto-detect   |
    | RayNeo X2     | OpenXR ARDK      | Unity      | N/A           |
    | Vuzix Blade 2 | Vuzix HUD SDK    | Android    | N/A           |
    | Everysight     | EvsKit           | BLE        | N/A           |
    | Frame          | BLE + Lua VM     | nRF52840   | N/A           |

---

*End of API Invocation Reference — Part 2*
