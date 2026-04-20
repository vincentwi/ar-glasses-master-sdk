# DEEP REPASS WAVE 5 — Complete SDK Reference Extraction
## Generated: 2026-04-19

---

# TABLE OF CONTENTS
1. Vuzix Blade 2 Template App (complete)
2. Everysight Maverick SDK (complete)
3. XREAL WebXR Polyfill (complete)
4. Decky-XRGaming Steam Deck Plugin (complete)
5. Pebble Mobile App / CoreDevices (key files)
6. Open Wearables Platform (key files)
7. Protostar — StardustXR Launcher (all .rs files)
8. SAM3 — Segment Anything with Concepts (README)
9. Truncated File Completions (TAPLINKX3, XRLinuxDriver, Stardust Server)

---

# 1. VUZIX BLADE 2 TEMPLATE APP (Complete)

## Architecture Overview
- Android app targeting SDK 34, min SDK 22
- Uses Vuzix HUD libraries: `com.vuzix:hud-actionmenu:2.9.1`, `com.vuzix:hud-resources:2.4.0`
- DynamicThemeApplication for ambient light-based theme switching
- ActionMenuActivity for HUD-style navigation
- Widget system integrated with BladeOS Launcher

## Key Dependencies (app/build.gradle)
```
implementation 'com.vuzix:hud-actionmenu:2.9.1'
implementation 'com.vuzix:hud-resources:2.4.0'
implementation "androidx.appcompat:appcompat:1.7.0"
```

## BladeSampleApplication.java — DynamicThemeApplication
Extends `com.vuzix.hud.resources.DynamicThemeApplication`:
- `getNormalThemeResId()` -> R.style.AppTheme (dark theme)
- `getLightThemeResId()` -> R.style.AppTheme_Light
- Blade OS detects ambient light and switches themes automatically

## ActionMenuActivity Pattern (center_content_template_activity.java)
The core HUD navigation pattern for Vuzix Blade 2:

```java
public class center_content_template_activity extends ActionMenuActivity {
    // Key overrides:
    protected boolean onCreateActionMenu(Menu menu)    // NOT onCreateOptionsMenu!
    protected boolean alwaysShowActionMenu()            // true = always visible, false = popup on gesture
    protected int getDefaultAction()                    // starting menu item index
    
    // Menu items defined in XML, onClick handlers in Java:
    public void showHello(MenuItem item)
    public void showVuzix(MenuItem item)
    public void showBlade(MenuItem item)
    
    // Custom ActionView for dynamic menu items:
    private static class SwitchMenuItemView extends DefaultActionMenuItemView {
        void setSwitchState(boolean on, int times) {
            icon.setImageTintList(...)  // Access internal icon field
            setIcon(...)
            setTitle(...)
        }
    }
}
```

## Around Content Template (around_content_template_activity.java)
Bottom/around-content navigation style (like Blade Settings app):
```java
protected int getActionMenuGravity() { return Gravity.CENTER; }
protected void onActionItemFocused(MenuItem item) {
    // Update UI based on focused menu item
    // This event fires when ActionItem gains focus
}
// Commented code shows KEYCODE handling:
// KeyEvent.KEYCODE_ENTER, KEYCODE_DPAD_CENTER -> finish()
// KeyEvent.KEYCODE_DPAD_LEFT -> onLeft()
// KeyEvent.KEYCODE_DPAD_RIGHT -> onRight()
```

## Pop-Up Menu Template
Same as center content but `alwaysShowActionMenu()` returns `false`.
Menu appears on "1 Finger hold for 1 second" gesture.
Two finger tap (back gesture) hides menu.

## Widget System (Template_Widget.java)
Standard Android AppWidgetProvider with BladeOS integration:
```java
// AndroidManifest.xml integration:
<meta-data android:name="com.vuzix.launcher.widget"
    android:value="...center_content_template_activity" />
    
// Light/dark mode widget switching:
RemoteViews views = new RemoteViews(context.getPackageName(),
    isLightMode ? R.layout.template_widget_light : R.layout.template_widget_dark);
```

## BroadcastReceiver for Display Mode Changes
```java
// Receives: com.vuzix.intent.action.UI_DISPLAY_MODE
// Triggers widget update when ambient light environment changes
```

## Theme System (styles.xml)
```xml
<style name="AppTheme" parent="HudTheme">
    <item name="imageHeaderTintColor">@color/hud_green</item>
    <item name="valueTextColor">@color/hud_white</item>
    <item name="backgroundColor">@color/hud_dark_gray</item>
</style>
<style name="AppTheme.Light" parent="HudTheme.Light">
    <!-- Light mode uses transparent colors for see-through display -->
</style>
```

## AndroidManifest Key Points
- `android:theme="@style/HudTheme"` — Required for Blade display
- `<meta-data android:name="com.vuzix.icon.tint" android:value="true" />` — Launcher icon tinting
- Activities, widgets, and broadcast receivers for UI_DISPLAY_MODE

## Layout Patterns
- **Center Lock**: Content in center, action menus slide underneath
- **Around Content**: Content around edges, action menu in center
- **Pop-Up**: Full real estate, menu appears on gesture

---

# 2. EVERYSIGHT MAVERICK SDK (Complete)

## Overview
- Smart glasses SDK for Everysight Maverick
- iOS (Swift/Obj-C xcframework) + Android (AAR/JAR)
- BLE-based communication with glasses
- Firmware OTA update system
- Simulator available (Windows/Mac/Linux)
- Latest: v2.6.1 (Oct 2025), Firmware 121

## SDK Architecture
```kotlin
// Kotlin example from README:
class HelloDeveloperScreen:Screen() {
    override fun onCreate() {
        Text()
          .setText("Hello Developer")
          .setResource(Font.StockFont.Medium)
          .setTextAlign(Align.center)
          .setXY(getWidth()/2, getHeight()/2)
          .setForegroundColor(EvsColor.Green.rgba)
          addTo(this)
    }
}
```

## iOS Swift Interface (EvsKit.swiftmodule)
Key classes and protocols:

### Evs (Main Entry Point)
```swift
public class Evs {
    static func instance() -> IEvsApp
    static func initOptions(options: [String: String]) throws
    static func startDefaultLogger()
    static func setLogger(logger: IEvsLogger?)
}
```

### BLE Communication
```swift
protocol IBleScanListener : IBtAdapterStateListener {
    func onScanStarted()
    func onScanStopped()
    func onScanFailed()
    func onPeripheralFound(deviceUuid: String, localName: String, rssi: NSNumber)
}

class BLEPeripheral : NSObject, IBleDevice {
    func connect() -> Bool
    func connectSecured() -> Bool
    func disconnect() -> Bool
    func getMtuSize() -> Int32
    func isConnected() -> Bool
    func requestBatteryRead(callback: (KotlinInt) -> Void) -> Bool
    func requestRssiRead(callback: (KotlinInt) -> Void) -> Bool
    func registerNotify(serviceUUID: String, charaUUID: String, listener: IEvsCommunicationChannelListener)
}
```

### Sensor Management
```swift
class EvsSensorsManager : NSObject {
    static let shared: EvsSensorsManager
    var HR_SERVICE: String
    var POWER_SERVICE: String
    var CADENCE_SPEED_SERVICE: String
    var CONTROLLER_EVS_SERVICE: String
    func scan(service: String?)
    func stopScan()
    func connectedDevice(device: BLEPeripheral) -> Bool
    func disconnectDevice(device: BLEPeripheral) -> Bool
}
```

### BT Scanner
```swift
class BtScanner : NSObject {
    static let shared: BtScanner
    func scanForGlasses(bleScanListener: IBleScanListener?)
    func stopScan()
}
```

### OTA Updates
```swift
enum OtaState {
    case none, uploading, installing, completed, failed
}
```

## API Evolution (v2.5.0 -> v2.6.0 -> v2.6.1)

### v2.6.0 Major Additions:
- **Line of Sight (LOS) API** (beta): ArScreen, ArWindow, ArModel, ArPrimitive, ArLines, ArPoints, ArTriangles
- **Auto-layout UIElements**: AutoLayout, Column, Row, Modifier
- **Viewport base class** for Screen and ArScreen
- **Sensors API**: enableInertialSensors, enableGyro, enableMagnetometer, enableAccelerometer
- **BLE 5.4 certified** firmware stack

### v2.6.1 Additions:
- ImgSrc: Generate image from text using TextParams
- ViewPort: onRenderingCenterChanged
- Android 16KB page size support
- Android API Level 36 support

## Tools
- **Simulator**: MaverickSim for Windows/Mac/Linux
- **Image Converter** (evsimgconvert.py): Converts PNG/JPG/SVG to Maverick M332 color format (3-3-2 bit RGB)
- **Font Converter** (font2sif.py): TrueType/OpenType to SIF (System Independent Font) for emWin embedded GUI

---

# 3. XREAL WEBXR POLYFILL (Complete)

## Overview
JavaScript WebHID-based communication library for XREAL (Nreal) Air and Light glasses.
Communicates via USB HID protocol directly from the browser.

## Device Identification (common.js)
```javascript
// XREAL Air: productId 0x0423 (1059) or 0x0424 (1060)
// XREAL Light: productId 0x573C (22332) or 0x5740 (22336)
// Vendor IDs: 0x0486, 0x0483, 0x0482, 0x3318 (Gleaming Reality)

export const NREAL_VENDOR_ID = 0x3318;
export const BOOT_PRODUCT_ID = 0x0423;
```

## Protocol (js_air/protocol.js)
HID packet structure:
```javascript
const HEAD = 0xfd;
const MSG_ID_OFS = 15;
const PAYLOAD_OFS = 22;
const LEN_OFS = 5;
const CRC_OFS = 1;

// Device3Packet (IMU data structure):
// signature[2], temperature[2], timestamp[8],
// angular_multiplier[2], angular_divisor[4],
// angular_velocity_x[3], angular_velocity_y[3], angular_velocity_z[3],
// acceleration_multiplier[2], acceleration_divisor[4],
// acceleration_x[3], acceleration_y[3], acceleration_z[3],
// magnetic_multiplier[2], magnetic_divisor[4],
// magnetic_x[2], magnetic_y[2], magnetic_z[2],
// checksum[4], _padding[6]
```

## Message IDs
```javascript
MESSAGES = {
    R_MCU_APP_FW_VERSION: 0x26,
    R_GLASSID: 0x15,
    R_DP7911_FW_VERSION: 0x16,
    R_ACTIVATION_TIME: 0x29,
    W_ACTIVATION_TIME: 0x2A,
    W_SLEEP_TIME: 0x1E,
    R_IMU_DATA: 0x80,
    W_TOGGLE_IMU: 0x19,
    R_DSP_VERSION: 0x18,
    // Firmware update messages:
    W_UPDATE_MCU_APP_FW_PREPARE: 0x3E,
    W_UPDATE_MCU_APP_FW_START: 0x3F,
    W_UPDATE_MCU_APP_FW_TRANSMIT: 0x40,
    W_UPDATE_MCU_APP_FW_FINISH: 0x41,
    // Button events (pushed from device):
    P_BUTTON_PRESSED: 0x6C05,  // 11-bit payload
    // Button IDs: 0001=power, 0006=brightness+, 0007=brightness-
    // Brightness levels: 0-7
}
```

## Glasses Manager (js_air/manager.js)
```javascript
// Key functions:
export async function getFirmwareVersionInMcu()
export async function getFirmwareVersionInDp()
export async function getFirmwareVersionInDsp()
export async function getSN()
export async function startIMU()    // W_TOGGLE_IMU with [0x1]
export async function stopIMU()     // W_TOGGLE_IMU with [0x0]
export async function getBrightness()
export async function setBrightness(brightness_int)  // 1-8
export async function upgradeInDsp(data)
export async function upgradeInDp()
```

## Glasses Class (js_air/glasses.js)
```javascript
class Glasses extends EventTarget {
    constructor(device) {
        // WebHID device
        this._device = device;
        device.oninputreport = this._handleInputReport.bind(this);
        // IMU polling
        this.imu_poller_instance = new RepeatingDeviceReportPoll({interval: 100});
    }
    
    sendReport(msgId, payload)              // Build and send HID report
    async sendReportTimeout(msgId, payload, timeout=1000)  // Send with response wait
    async isMcu()                           // Check if device is MCU
    startIMUPolling()                       // Begin IMU data stream
    stopIMUPolling()                        // Stop IMU data stream
}
```

---

# 4. DECKY-XRGAMING — Steam Deck XR Plugin (Complete)

## Overview
Decky Loader plugin for Steam Deck that enables XR gaming with AR glasses.
Integrates with XRLinuxDriver via IPC. Installs/manages Breezy Vulkan layer.

## Python Backend (main.py)
```python
from PyXRLinuxDriverIPC.xrdriveripc import XRDriverIPC

ipc = XRDriverIPC(
    config_home=os.path.join(decky.DECKY_USER_HOME, ".config"),
    supported_output_modes=['virtual_display', 'sideview']
)

class Plugin:
    async def retrieve_config(self)         # IPC config read
    async def write_config(self, config)    # IPC config write
    async def write_control_flags(self, control_flags)
    async def retrieve_driver_state(self)
    async def is_driver_running(self)
    async def force_reset_driver(self)
    async def install_breezy(self)          # Installs Breezy Vulkan layer
    async def check_breezy_installed(self)  # Verifies installation
    async def request_token(self, email)    # License management
    async def verify_token(self, token)
```

## TypeScript Frontend (index.tsx) — Key Interfaces
```typescript
interface Config {
    disabled: boolean;
    output_mode: "mouse" | "joystick" | "external_only";
    external_mode: ('virtual_display' | 'sideview' | 'none')[];
    display_size: number;
    display_distance: number;
    sbs_content: boolean;
    sideview_position: "center" | "top_left" | "top_right" | "bottom_left" | "bottom_right";
    virtual_display_smooth_follow_enabled: boolean;
    curved_display: boolean;
    smooth_follow_track_roll: boolean;
    smooth_follow_track_pitch: boolean;
    smooth_follow_track_yaw: boolean;
    look_ahead: number;
    mouse_sensitivity: number;
}

interface DriverState {
    heartbeat: number;
    connected_device_brand: string;
    connected_device_model: string;
    connected_device_full_distance_cm: number;
    connected_device_full_size_cm: number;
    connected_device_pose_has_position: boolean;
    calibration_state: "NOT_CALIBRATED" | "CALIBRATING" | "CALIBRATED" | "WAITING_ON_USER";
    sbs_mode_enabled: boolean;
    sbs_mode_supported: boolean;
    firmware_update_recommended: boolean;
    device_license: License;
}

type HeadsetModeOption = "virtual_display" | "vr_lite" | "sideview" | "disabled";
```

## Headset Mode Descriptions
- **Virtual display**: Only available in-game
- **VR-Lite**: Use head movements to look around in-game
- **Sideview**: Display follow, sizing, and positioning
- **Disabled**: Static display with no head-tracking

---

# 5. PEBBLE MOBILE APP / COREDEVICES (Key Files)

## Architecture
- Kotlin Multiplatform (KMP): commonMain, iosMain, androidMain
- Uses `libpebblecommon` for Pebble BLE communication
- Firebase Auth, Firestore, analytics
- Wispr Flow transcription integration
- Cactus/Krisp audio processing
- OAuth integrations (Google, GitHub, Apple)

## CompanionDevice Interface
```kotlin
interface CompanionDevice {
    suspend fun registerDevice(identifier: PebbleIdentifier, uiContext: PlatformUiContext)
    fun hasApprovedDevice(identifier: PebbleIdentifier): Boolean
    fun cdmPreviouslyCrashed(): Boolean
}
```

## Key Modules
- **Transcription**: WisprFlowTranscriptionService, CactusTranscriptionService, NullTranscriptionService
- **Models**: ModelManager, ModelDownloadManager (on-device AI models)
- **Database**: CoreDatabase with UserConfig, WeatherLocation, MemfaultChunks, Hearts, Heartbeats
- **API**: ApiClient, WisprFlow integration
- **UI**: PebbleWebview, SignInButton, ModelDownloadDialog, GenericWebViewScreen
- **Queue**: PersistentQueueScheduler for reliable task execution

---

# 6. OPEN WEARABLES PLATFORM (Key Files)

## Architecture
- Python/FastAPI backend + React/TypeScript frontend
- MCP (Model Context Protocol) server for AI assistants
- Aggregates data from Garmin, Whoop, Polar, Suunto, etc.
- PostgreSQL + Celery + Redis backend

## MCP Server (mcp/app/main.py)
```python
mcp = FastMCP("open-wearables", instructions="""
    Available tools:
    - get_users: Discover users
    - get_activity_summary: Steps, calories, heart rate, intensity minutes
    - get_sleep_summary: Sleep data
    - get_workout_events: Exercise data
    - get_timeseries: Granular samples (weight, SpO2, HRV, heart rate)
""")
```

## Time Series API (mcp/app/tools/timeseries.py)
```python
@timeseries_router.tool
async def get_timeseries(
    user_id: str,
    start_time: str,      # ISO-8601
    end_time: str,
    types: list[str],      # "heart_rate", "oxygen_saturation", "weight", etc.
    resolution: str = "raw" # "raw", "1min", "5min", "15min", "1hour"
) -> dict:
    # Returns: user, period, records[], summary (per-type avg/min/max), truncated
```

## Available Series Types
- heart_rate, resting_heart_rate, walking_heart_rate_average
- heart_rate_variability_sdnn, heart_rate_variability_rmssd
- oxygen_saturation, respiratory_rate
- blood_glucose, blood_pressure_systolic, blood_pressure_diastolic
- weight, body_fat_percentage, body_mass_index
- steps, active_energy, basal_energy, distance

---

# 7. PROTOSTAR — StardustXR Launcher (All .rs Files)

## Architecture
Multiple launcher variants for StardustXR spatial computing:
- **protostar/**: Core library (Application, XDG desktop file parsing, icon management)
- **single/**: Single app launcher
- **hexagon_launcher/**: Hexagonal grid launcher
- **app_grid/**: Grid-based launcher
- **sirius/**: Directory-based launcher

## Core Library (protostar/src/application.rs)
```rust
pub struct Application {
    desktop_file: DesktopFile,
}
impl Application {
    pub fn create(desktop_file: DesktopFile) -> Result<Self, NodeError>
    pub fn name(&self) -> Option<&str>
    pub fn categories(&self) -> &[String]
    pub fn icon(&self, preferred_px_size: u16, prefer_3d: bool) -> Option<Icon>
    pub fn launch<T: SpatialRefAspect + Clone>(&self, launch_space: &T) -> NodeResult<()>
    // Launch flow:
    // 1. Generate startup token via client.get_root().generate_state_token()
    // 2. Get connection environment
    // 3. Set STARDUST_STARTUP_TOKEN env var
    // 4. Fork + exec via sh -c with field code stripping
}
```

## XDG Desktop File Parser (protostar/src/xdg.rs)
```rust
pub struct DesktopFile {
    path: PathBuf,
    pub name: Option<String>,
    pub command: Option<String>,
    pub categories: Vec<String>,
    pub icon: Option<String>,
    pub no_display: bool,
    pub only_show_in: Vec<String>,
}

pub struct Icon {
    pub icon_type: IconType,  // Png, Svg, Gltf
    pub path: PathBuf,
    pub size: u16,
}

// Functions:
pub fn get_desktop_files() -> impl Iterator<Item = PathBuf>
// Searches XDG_DATA_DIRS, ~/.local/share, /usr/share, /usr/local/share
```

## Hexagon Launcher (hexagon_launcher/src/main.rs)
```rust
pub struct HexagonLauncher {
    open: bool,
    pos: Vector3<f32>,
    rot: Quaternion<f32>,
    apps: Vec<App>,
}
impl ClientState for HexagonLauncher {
    const APP_ID: &'static str = "org.protostar.hexagon_launcher";
    fn initial_state_update(&mut self) {
        // Load desktop files, filter by no_display and only_show_in
        // Sort by name, load icons in parallel
    }
}
// Uses hex spiral layout: Hex::spiral(i + 1).get_coords()
// Grabbable hexagon with toggle open/close button
```

## Hex Grid Math (hexagon_launcher/src/hex.rs)
```rust
// Cube coordinate system: q + r + s = 0
pub struct Hex { q: isize, r: isize, s: isize }
pub const HEX_DIRECTION_VECTORS: [Hex; 6] = [...]
impl Hex {
    pub fn spiral(i: usize) -> Self    // Outward spiral positioning
    pub fn get_coords(&self) -> [f32; 3]  // Convert to 3D coordinates
}
```

## App Grid (app_grid/src/main.rs)
```rust
const APP_LIMIT: usize = 300;
const APP_SIZE: f32 = 0.05;
const GRID_PADDING: f32 = 0.01;
const ACTIVATION_DISTANCE: f32 = 0.5;
// Positions apps in a 10-column grid
// Drag beyond ACTIVATION_DISTANCE to launch
```

---

# 8. SAM3 — SEGMENT ANYTHING WITH CONCEPTS

## Overview
Meta's SAM 3 is a unified foundation model for promptable segmentation in images/videos.
- 848M parameters, DETR-based detector + SAM 2-based tracker sharing a vision encoder
- Detects/segments/tracks via text, points, boxes, masks
- SA-CO benchmark: 270K unique concepts (50x more than existing benchmarks)
- Achieves 75-80% of human performance

## Key Usage
```python
# Image
from sam3.model_builder import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor
model = build_sam3_image_model()
processor = Sam3Processor(model)
inference_state = processor.set_image(image)
output = processor.set_text_prompt(state=inference_state, prompt="text")
masks, boxes, scores = output["masks"], output["boxes"], output["scores"]

# Video
from sam3.model_builder import build_sam3_video_predictor
video_predictor = build_sam3_video_predictor()
response = video_predictor.handle_request(dict(type="start_session", resource_path=path))
response = video_predictor.handle_request(dict(
    type="add_prompt", session_id=..., frame_index=0, text="prompt"))
```

## SmartGlasses Video Benchmark
SAM3 includes a SmartGlasses test dataset in SA-Co video evaluations:
- cgF1: 36.4 (vs 58.5 human)
- pHOTA: 63.6 (vs 72.3 human)

---

# 9. TRUNCATED FILE COMPLETIONS

## XRLinuxDriver — VITURE Device Driver (lines 501-754)

### VITURE IMU & Connection Management
```c
// Carina (new) vs Legacy (gen1) device paths:
if (viture_device_type == XR_DEVICE_TYPE_VITURE_CARINA) {
    register_callbacks_carina(viture_provider, NULL, NULL, viture_carina_imu_callback, NULL);
    // Carina: 6DoF (provides_position = true)
    // cycles_per_s = VITURE_CARINA_CYCLES_PER_S
} else {
    register_pose_callback(viture_provider, viture_legacy_pose_callback);
    // Legacy: 3DoF only
}

// IMU modes: VITURE_IMU_MODE_POSE
// Connection flow: initialize_provider -> start_stream -> open_imu
// SBS mode: xr_device_provider_switch_dimension(provider, enabled)
// Display mode: xr_device_provider_get_display_mode(provider)
```

### VITURE Driver Interface
```c
const device_driver_type viture_driver = {
    .id                      = VITURE_DRIVER_ID,
    .supported_device_func   = viture_supported_device,
    .device_connect_func     = viture_device_connect,
    .block_on_device_func    = viture_block_on_device,
    .device_is_sbs_mode_func = viture_device_is_sbs_mode,
    .device_set_sbs_mode_func = viture_device_set_sbs_mode,
    .is_connected_func       = viture_is_connected,
    .disconnect_func         = viture_disconnect
};
```

### Device Properties
```c
device->imu_cycles_per_s = cycles_per_s;
device->imu_buffer_size = cycles_per_s / 60;
device->provides_position = provides_position;  // true for Carina
device->sbs_mode_supported = true;
device->firmware_update_recommended = false;
```

## Stardust Server — Model System (lines 501-836)

### Material Parameter Handling
```rust
// Supported material parameters:
// Float: "metallic", "roughness"
// Color: "color" (base_color), "emission_factor" (emissive)
// Texture: "diffuse", "emission", "metal", "occlusion"
// Dmatex: Direct memory-mapped textures with timeline synchronization

struct PartTextures {
    diffuse: Option<(Handle<Image>, Option<SignalOnDrop>)>,
    emission: Option<(Handle<Image>, Option<SignalOnDrop>)>,
    metal: Option<(Handle<Image>, Option<SignalOnDrop>)>,
    occlusion: Option<(Handle<Image>, Option<SignalOnDrop>)>,
}
```

### Model Loading & Part Binding
```rust
pub struct Model {
    spatial: Arc<Spatial>,
    bevy_scene_entity: OnceLock<EntityHandle>,
    parts: OnceLock<Vec<Arc<ModelPart>>>,
    pre_bound_parts: Mutex<Vec<Arc<ModelPart>>>,
}

impl ModelAspect for Model {
    fn bind_model_part(node, calling_client, id, part_path) -> Result<()>
    // Creates aliases for model parts accessible by client
}
```

## Stardust Server — Fields System (lines 501-873)

### Cubic Spline SDF (Signed Distance Field)
```rust
// CubicSplineShape: True cubic Bezier closest-point via Newton iteration
pub fn sd_tube(&self, p: Vec3) -> f32
// Per-segment: find closest t, evaluate cubic, interpolate radius

pub trait FieldTrait: Send + Sync + 'static {
    fn local_distance(&self, p: Vec3A) -> f32;
    fn local_normal(&self, p: Vec3A, r: f32) -> Vec3A;
    fn local_closest_point(&self, p: Vec3A, r: f32) -> Vec3A;
    fn distance(&self, reference_space: &Spatial, p: Vec3A) -> f32;
    fn ray_march(&self, ray: Ray) -> RayMarchResult;
}
```

### Field Shapes (SDF implementations)
```rust
Shape::Box(size) => {
    // Standard box SDF with exact distance
}
Shape::Cylinder(CylinderShape { length, radius }) => {
    // Cylinder SDF
}
Shape::Sphere(radius) => p.length() - radius,
Shape::Spline(spline) => spline.sd_tube(p.into()),
Shape::Torus(TorusShape { radius_a, radius_b }) => {
    // Torus SDF
}
```

### Ray Marching
```rust
const MAX_RAY_STEPS: u32 = 1000;
const MIN_RAY_MARCH: f32 = 0.001;
const MAX_RAY_LENGTH: f32 = 1000.0;

fn ray_march(&self, ray: Ray) -> RayMarchResult {
    // Sphere-tracing with clamped step size
    // Returns: min_distance, deepest_point_distance, ray_length, ray_steps
}
```

## TAPLINKX3 — DualWebViewGroup.kt (lines 501-2000)

### Dual-Display WebView Architecture
TAPLINKX3 is an AR glasses browser with:
- **Dual-eye rendering**: Left eye UI container mirrored to right eye
- **Scroll system**: WebView content scrolling with JS bridge for nested scrollers
- **Scrollbar UI**: Custom horizontal/vertical scrollbars with thumb tracking
- **Media detection**: Freezes scrollbar updates during media playback
- **Windows/Tabs system**: Multi-window browser with tab overview (3-column grid)
- **Window state persistence**: JSON serialization to SharedPreferences with Base64 WebView state bundles
- **Screen masking**: Black overlay with media controls for video viewing
- **Fullscreen controls**: Media playback controls (prev track, 10s back, play/pause, 10s forward, next track)
- **Desktop/Mobile mode**: Switches viewport width and user agent
- **URL editing**: Custom keyboard integration with link editing
- **JS scroll bridge**: Detects and scrolls nested scrollable elements via `window.__taplinkScrollTarget`

### Key Methods
```kotlin
fun updateScrollBarsVisibility()  // Manages scrollbar show/hide based on content size
fun updateExternalScrollMetrics(rangeX, extentX, offsetX, rangeY, extentY, offsetY)
fun createNewWindow(loadDefaultUrl: Boolean = true): WebView
fun switchToWindow(id: String)
fun closeWindow(id: String)
fun saveAllWindowsState()   // JSON + Base64 WebView bundle persistence
fun restoreState()
fun toggleWindowMode()      // Shows/hides tab overview with thumbnails
fun showWindowsOverview()   // 3-column grid of window thumbnails
```

## TAPLINKX3 — MainActivity.kt (lines 501-2000)

### Input System
- **Triple tap**: Screen re-center (anchored) or toggle scroll mode (non-anchored)
- **Double tap**: Back navigation with triple-tap guard delay
- **Single tap**: Cursor click dispatch or cursor toggle
- **Scroll gestures**: Maps horizontal drag to vertical scroll in anchored/scroll mode
- **Mouse simulation**: Desktop mode uses AXIS_VSCROLL, mobile mode uses touch swipe with gesture looping

### Anchored Mode (Head-Tracking)
```kotlin
// Quaternion math for head tracking:
fun quaternionMultiply(q1: FloatArray, q2: FloatArray): FloatArray
fun quaternionInverse(q: FloatArray): FloatArray
fun quaternionSlerp(qa: FloatArray, qb: FloatArray, t: Float): FloatArray
// Uses TYPE_ROTATION_VECTOR sensor
// Smoothness factor controls interpolation
```

### Key Features
- Gesture detection with configurable cursor sensitivity
- Camera integration for image search (base64 capture)
- Speech recognition (SpeechRecognizer API)
- Geolocation via IPC (GPSIPCHelper)
- Notification service integration
- Custom keyboard with URL editing
- Bookmark management
- QR code scanning
- Desktop/mobile viewport switching

---

# END OF WAVE 5 REPASS
