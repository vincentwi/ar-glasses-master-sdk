# DEEP Driver & Tools Reference
## Comprehensive Source-Level Documentation

Generated from full source reading of:
- XRLinuxDriver (C, Linux head-tracking driver)
- TapLink X3 (Kotlin, Android browser for RayNeo)
- RayDesk (Kotlin, Android remote desktop streaming)
- PhoenixHeadTracker (C#, Windows head tracker)
- Fusion (C, xioTechnologies sensor fusion library)

---

# 1. XRLinuxDriver — Linux AR Glasses Head-Tracking Driver

## 1.1 Architecture Overview

Multi-threaded C driver that:
1. Detects USB AR glasses via libusb hotplug
2. Reads IMU data (quaternion orientation + optional 6DoF position)
3. Applies calibration, reference pose, and plugin transformations
4. Outputs pose data via IPC (shared memory), mouse, joystick, or OpenTrack UDP

### Thread Model (5 pthreads + main)
- `block_on_device_thread` — waits for device, connects, blocks while connected
- `monitor_config_file_thread` — inotify watcher on config.ini
- `manage_state_thread` — periodic state write to /dev/shm/xr_driver_state
- `monitor_control_flags_file_thread` — watches /dev/shm/xr_driver_control
- `monitor_usb_devices_thread` — libusb hotplug event loop

### Main Entry Point (driver.c:main)
```c
int main(int argc, const char** argv)
```
- Sets SIGSEGV handler, acquires file lock (single instance)
- Initializes: config, state, connection_pool
- Creates 5 pthreads, joins all on exit

---

## 1.2 Core Data Types

### IMU Types (imu.h)
```c
struct imu_euler_t { float roll, pitch, yaw; };
struct imu_quat_t  { float x, y, z, w; };
struct imu_vec3_t  { float x, y, z; };
struct imu_pose_t  {
    imu_quat_t orientation;
    imu_vec3_t position;
    imu_euler_t euler;
    bool has_orientation, has_position;
    uint32_t timestamp_ms;
};
```

### IMU Math Functions (imu.h / imu.c)
```c
float degree_to_radian(float deg);
float radian_to_degree(float rad);
imu_quat_type normalize_quaternion(imu_quat_type q);
imu_quat_type conjugate(imu_quat_type q);
imu_quat_type multiply_quaternions(imu_quat_type q1, imu_quat_type q2);
imu_quat_type euler_to_quaternion_xyz(imu_euler_type euler);
imu_quat_type euler_to_quaternion_zyx(imu_euler_type euler);
imu_quat_type euler_to_quaternion_zxy(imu_euler_type euler);
imu_euler_type quaternion_to_euler_xyz(imu_quat_type q);
imu_euler_type quaternion_to_euler_zyx(imu_quat_type q);
imu_euler_type quaternion_to_euler_zxy(imu_quat_type q);
imu_quat_type device_pitch_adjustment(float adjustment_degrees);
imu_vec3_type vector_rotate(imu_vec3_type v, imu_quat_type q);
bool quat_equal(imu_quat_type q1, imu_quat_type q2);
float quat_small_angle_rad(imu_quat_type q1, imu_quat_type q2);
// Inline helpers:
void imu_pose_sync_euler_from_orientation(imu_pose_type *p);
void imu_pose_sync_orientation_from_euler(imu_pose_type *p);
```

### Device Properties (devices.h)
```c
struct device_properties_t {
    char* brand, *model;
    int hid_vendor_id, hid_product_id;
    uint8_t usb_bus, usb_address;
    calibration_setup_type calibration_setup;  // AUTOMATIC or INTERACTIVE
    int resolution_w, resolution_h;
    float fov;                    // diagonal FOV in degrees
    float lens_distance_ratio;    // lens_dist / perceived_display_dist
    int calibration_wait_s;
    int imu_cycles_per_s;
    int imu_buffer_size;
    float look_ahead_constant, look_ahead_frametime_multiplier;
    float look_ahead_scanline_adjust, look_ahead_ms_cap;
    bool sbs_mode_supported, firmware_update_recommended;
    bool provides_orientation, provides_position;
    bool can_be_supplemental;
};
```
Constants: `LENS_TO_PIVOT_CM = 5.0 * 2.54` (~12.7cm neck-to-lens)

### Device Driver Interface (devices.h)
```c
struct device_driver_t {
    char* id;
    device_properties_type* (*supported_device_func)(uint16_t vendor, uint16_t product, uint8_t bus, uint8_t addr);
    bool (*device_connect_func)();
    void (*block_on_device_func)();
    bool (*device_is_sbs_mode_func)();
    bool (*device_set_sbs_mode_func)(bool enabled);
    bool (*is_connected_func)();
    void (*disconnect_func)(bool soft);
};
```

### Driver Config (config.h)
```c
struct driver_config_t {
    bool disabled, mouse_mode, joystick_mode, external_mode;
    bool use_roll_axis, vr_lite_invert_x, vr_lite_invert_y;
    int mouse_sensitivity;
    char *output_mode;
    bool multi_tap_enabled, metrics_disabled;
    float dead_zone_threshold_deg;
    bool debug_threads, debug_joystick, debug_multi_tap;
    bool debug_ipc, debug_license, debug_device, debug_connections;
};
```

### Driver State (state.h)
```c
enum calibration_state_t { NOT_CALIBRATED, CALIBRATED, CALIBRATING, WAITING_ON_USER };
struct driver_state_t {
    uint32_t heartbeat;
    char *connected_device_brand, *connected_device_model;
    float connected_device_full_distance_cm, connected_device_full_size_cm;
    bool connected_device_pose_has_position;
    calibration_setup_type calibration_setup;
    calibration_state_type calibration_state;
    bool sbs_mode_supported, sbs_mode_enabled;
    bool breezy_desktop_smooth_follow_enabled;
    float breezy_desktop_follow_threshold, breezy_desktop_display_distance;
    bool firmware_update_recommended, is_gamescope_reshade_ipc_connected;
    int granted_features_count; char** granted_features;
    int license_features_count; char** license_features;
    char* device_license;
    float *smooth_follow_origin; bool smooth_follow_origin_ready;
};
struct control_flags_t {
    bool recenter_screen, recalibrate, force_quit;
    sbs_control_type sbs_mode;  // UNSET, ENABLE, DISABLE
    char* request_features;
};
```
State files: `/dev/shm/xr_driver_state`, `/dev/shm/xr_driver_control`

### Connection Pool (connection_pool.h)
```c
typedef struct connection_t {
    const device_driver_type* driver;
    device_properties_type* device;
    bool supplemental, active;
    pthread_t thread; bool thread_running;
} connection_t;

void connection_pool_init(pose_handler_t, reference_pose_getter_t);
void connection_pool_handle_device_added(const device_driver_type*, device_properties_type*);
void connection_pool_handle_device_removed(const char* driver_id);
bool connection_pool_is_connected();
bool connection_pool_connect_active();
void connection_pool_block_on_active();
void connection_pool_disconnect_all(bool soft);
device_properties_type* connection_pool_primary_device();
device_properties_type* connection_pool_supplemental_device();
const device_driver_type* connection_pool_primary_driver();
void connection_pool_ingest_pose(const char* driver_id, imu_pose_type pose);
```

### IPC Shared Memory (ipc.h)
```c
struct ipc_values_t {
    float *display_res;       // [w, h]
    bool *disabled;
    float *date;              // [4] keepalive
    float *pose_orientation;  // [16] 4 rows of quaternion data
    float *pose_position;     // [3]
    pthread_mutex_t *pose_orientation_mutex;
    float *display_fov, *lens_distance_ratio;  // deprecated
};
```

### Buffer System (buffer.h)
```c
buffer_type *create_buffer(int size);
float push(buffer_type *buffer, float next_value);
imu_buffer_type *create_imu_buffer(int buffer_size);
imu_buffer_response_type *push_to_imu_buffer(imu_buffer_type*, imu_quat_type, float timestamp_ms);
```

### Runtime Context (runtime_context.h)
```c
struct runtime_context_t {
    driver_config_type *config;
    device_properties_type *device;
    driver_state_type *state;
    connection_pool_type *conn_pool;
};
// Inline accessors: state(), config(), device_checkout(), device_checkin()
```

---

## 1.3 Device Drivers

### XREAL Driver (devices/xreal.c)
- **Driver ID**: `"xreal"`
- **Vendor**: 0x3318
- **Supported models** (10 PIDs): Air, Air 2, Air 2 Pro, Air 2 Ultra, One Pro, One, 1S
- **FOVs**: 45°–57° depending on model
- **IMU**: 1000Hz native, forced to 250Hz; buffer ~10ms smoothing
- **Pitch adjustments**: 0° for Air series, 35° for One Pro
- **SBS modes**: Maps between non-SBS (1920x1080) and SBS (3840x1080) display modes
- **Coordinate conversion**: NWU via `nwu_conversion_quat = {x=1, y=0, z=0, w=0}`
- Uses `device_imu_*` and `device_mcu_*` SDK for HID communication

### Viture Driver (devices/viture.c)
- **Driver ID**: `"viture"`
- **Vendor**: 0x35CA
- **Supported models** (14 PIDs): One, One Lite, Pro, Luma, Luma Pro, Luma Ultra, Luma Cyber, Beast
- **FOVs**: 40°–58° depending on model
- **IMU frequency**: 60-500Hz configurable, Carina devices at 1000Hz
- **6DoF**: Carina-based devices provide position via `get_gl_pose_carina()`
- **SBS modes**: 0x31 (1920x1080@60), 0x32 (3840x1080@60), etc.
- **Coordinate conversion**: EUS (GL) → NWU for Carina; direct NWU for legacy
- **Pitch adjustments**: One=6°, Pro=3°, Luma=-8.5°, Beast=-8.5°

### Rokid Driver (devices/rokid.c)
- **Driver ID**: `"rokid"`
- **Vendor**: ROKID_GLASS_VID (from SDK header)
- **Supported PIDs**: 7 variants (0x162B-0x2180)
- **IMU**: 90Hz via `GlassWaitEvent()` with GAME_ROTATION_EVENT
- **Coordinate conversion**: EUS → NWU with 5° factory offset
- **SBS modes**: 2D (3840x1080@60), 3D (3840x1200@60/90)

### RayNeo Driver (devices/rayneo.c)
- **Driver ID**: `"rayneo"`
- **Vendor/Product**: 0x1BBB / 0xAF50
- **IMU**: 500Hz native, forced to 250Hz
- **Coordinate conversion**: EUS → NWU with 15° factory offset
- **SDK functions**: `RegisterIMUEventCallback`, `StartXR`, `OpenIMU`, `GetHeadTrackerPose`
- **SBS**: `SwitchTo3D()` / `SwitchTo2D()` / `GetSideBySideStatus()`

---

## 1.4 Plugin System

### Plugin Interface (plugins.h)
```c
struct plugin_t {
    char* id;
    start_func start;
    default_config_func default_config;
    handle_config_line_func handle_config_line;
    handle_control_flag_line_func handle_control_flag_line;
    set_config_func set_config;
    setup_ipc_func setup_ipc;
    handle_ipc_change_func handle_ipc_change;
    modify_reference_pose_func modify_reference_pose;
    handle_reference_pose_updated_func handle_reference_pose_updated;
    modify_pose_func modify_pose;
    handle_pose_data_func handle_pose_data;
    reset_pose_data_func reset_pose_data;
    handle_state_func handle_state;
    handle_device_connect_func handle_device_connect;
    handle_device_disconnect_func handle_device_disconnect;
};
```

### Registered Plugins (11 total, plugins.c)
1. **device_license** — license key management
2. **virtual_display** — head-locked virtual screen with IPC to shader
3. **sideview** — follow-mode display
4. **metrics** — usage telemetry
5. **custom_banner** — overlay banner display
6. **smooth_follow** — slerp-based screen follow with configurable thresholds
7. **breezy_desktop** — Wayland compositor integration via /dev/shm binary protocol
8. **gamescope_reshade_wayland** — SteamOS/gamescope shader injection
9. **neck_saver** — ergonomic posture alerts
10. **opentrack_source** — sends pose data as OpenTrack UDP (6 doubles: x,y,z,yaw,pitch,roll + frame#)
11. **opentrack_listener** — receives OpenTrack UDP packets as a synthetic IMU device (supplemental)

### Virtual Display Plugin (plugins/virtual_display.c)
```c
struct virtual_display_config_t {
    bool enabled;
    float look_ahead_override, display_size, display_distance;
    bool sbs_content, sbs_mode_stretched;
    bool follow_mode_enabled, passthrough_smooth_follow_enabled;
    bool curved_display;
};
```
IPC values: enabled, show_banner, look_ahead_cfg[4], display_size, display_north_offset,
sbs_enabled, sbs_content, sbs_mode_stretched, curved_display, half_fov_z_rads, half_fov_y_rads,
fov_half_widths[2], fov_widths[2], texcoord_x_limits[2], texcoord_x_limits_r[2],
lens_vector[3], lens_vector_r[3]

### Smooth Follow Plugin (plugins/smooth_follow.c)
- States: NONE → INIT → WAITING → SLERPING
- 3 parameter presets: init_params, sticky_params, loose_follow_params
- Implements quaternion slerp with return-to-angle margin
- Tracks origin pose for snap-back when disabled
- Supports per-axis tracking: roll, pitch, yaw independently
- 6DoF: allows half-meter freedom in forward/back direction

### Breezy Desktop Plugin (plugins/breezy_desktop.c)
- Writes binary data to `/dev/shm/breezy_desktop_imu`
- Layout version 5: config header + IMU record with parity byte
- Config: version, enabled, look_ahead[4], display_res[2], fov, lens_ratio, sbs, banner
- IMU record: smooth_follow_enabled, orientation[16], position[3], epoch_ms, orientation[16], parity

### OpenTrack Source Plugin (plugins/opentrack_source.c)
- Sends UDP packets: 6 doubles (x,y,z,yaw,pitch,roll) + uint32 frame number
- Coordinate conversion: NWU → EUS (x=-pos.y, y=pos.z, z=-pos.x)
- Configurable: `opentrack_app_ip`, `opentrack_app_port` (default 127.0.0.1:4242)

### OpenTrack Listener Plugin (plugins/opentrack_listener.c)
- Binds UDP socket, receives OpenTrack 6-double payloads
- Creates synthetic device (brand="OpenTrack", model="UDP")
- Converts EUS yaw/pitch/roll → NWU quaternion via euler_to_quaternion_zyx
- Feedback loop detection: ignores packets when source plugin targets same localhost:port
- Timeout: disconnects if no packets for 500ms

---

## 1.5 Pose Processing Pipeline (driver.c:driver_handle_pose)

1. **Calibration wait** (device-specific seconds, typically 1-15s)
2. **Reference pose capture** (first valid pose after calibration)
3. **Plugin modify_reference_pose** hooks (smooth follow slerp)
4. **Relative orientation**: `multiply_quaternions(reference_conj, pose.orientation)`
5. **Relative position**: vector subtraction + rotation by reference_conj
6. **Multi-tap detection** (double=recenter, triple=recalibrate)
7. **Plugin modify_pose** hooks (neck saver, etc.)
8. **Euler velocity computation**
9. **handle_imu_update** → output to mouse/joystick/IPC

---

# 2. TapLink X3 — Android AR Browser for RayNeo

## 2.1 Architecture Overview

Kotlin Android app implementing a binocular web browser for RayNeo X3 AR glasses (1280x480 display, 640x480 per eye). Uses SurfaceView pixel-copying for right eye mirroring.

### Package: `com.TapLinkX3.app`

## 2.2 Key Classes

### MainActivity (6339 lines)
Implements: AppCompatActivity, DualWebViewGroup.DualWebViewGroupListener, NavigationListener,
CustomKeyboardView.OnKeyboardActionListener, BookmarkListener, LinkEditingListener,
DualWebViewGroup.MaskToggleListener, DualWebViewGroup.AnchorToggleListener, DualWebViewGroup.WindowCallback

**Key features:**
- **Sensor-based head tracking**: Uses `SensorManager` with rotation vector for anchored mode
- **Cursor system**: Virtual cursor (320x240 coordinate space) with IMU-based movement
- **Mouse tap mode**: Direct mouse input from Mudra ring controller
- **Triple-tap detection**: Re-centering in anchored mode (400ms tap interval, 800ms sequence)
- **GPS integration**: RayNeo Mercury IPC (`com.ffalconxr.mercury.ipc.Launcher`) for location
- **QR scanning**: ZXing barcode scanner with camera integration
- **Notification relay**: BroadcastReceiver for system notifications

**Cursor parameters:**
- `TRANSLATION_SCALE = 2000f` (anchored mode)
- `cursorSensitivity` 0-100, mapped to `cursorGain` 0.0-0.9
- Smoothing: double-exponential with configurable `smoothnessLevel` (0-100)
- Frame timing: `MIN_FRAME_INTERVAL_MS = 8` (~120fps cap)

### DualWebViewGroup (8439 lines)
Core binocular rendering component.

**Structure:**
- `webViewsContainer` (FrameLayout) — holds the primary WebView
- `rightEyeView` (SurfaceView) — receives pixel-copied left eye content
- `leftEyeUIContainer` — overlay for navigation, keyboard, bookmarks
- `fullScreenOverlayContainer` — fullscreen video container
- `leftEyeClipParent` — 640px wide clipping parent

**Multi-window support:**
```kotlin
data class BrowserWindow(
    val id: String = UUID.randomUUID().toString(),
    val webView: InternalWebView,
    var thumbnail: Bitmap? = null,
    var title: String = "New Tab"
)
```

**Rendering pipeline:**
- Refresh interval: 16ms (~60fps normal), 100ms (idle/masked)
- Idle detection: 5s threshold → drops to ~10fps
- PixelCopy for right eye mirroring
- UI scale: 0.5-1.0 with pivot at (320, 240)
- Progress bar for page loading

**Navigation bar buttons:** Back, Forward, Home, Refresh, Quit, Settings, Hyperlink/URL, Bookmarks, Mode toggle, Anchor toggle, Zoom in/out, Windows manager

**Interfaces:**
```kotlin
interface DualWebViewGroupListener { fun onCursorPositionChanged(x, y, isVisible) }
interface MaskToggleListener { fun onMaskTogglePressed() }
interface AnchorToggleListener { fun onAnchorTogglePressed() }
interface FullscreenListener { fun onEnterFullscreen(); fun onExitFullscreen() }
interface KeyboardListener { fun onShowKeyboard(); fun onHideKeyboard() }
interface WindowCallback { fun onWindowCreated(webView); fun onWindowSwitched(webView) }
```

### CustomKeyboardView (1020 lines)
Full custom on-screen keyboard with:
- Two modes: LETTERS and SYMBOLS
- Caps lock (double-tap shift)
- Dynamic keys (@ in letters, ← arrow in symbols)
- Cursor-aware hover system (for head-tracking input)
- Auto-lowercase after key press (unless caps locked)
- Anchored mode tap support

```kotlin
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
```

### GroqAudioService
Voice-to-text using Groq's Whisper API:
- Records M4A audio via MediaRecorder (VOICE_RECOGNITION source, 44.1kHz AAC 128kbps)
- Sends to `https://api.groq.com/openai/v1/audio/transcriptions`
- Model: `whisper-large-v3`
- API key stored in SharedPreferences

### WebAppInterface
JavaScript bridge (`@JavascriptInterface`):
- `ping()` → "pong"
- `chatWithGroq(message, historyJson)` — Groq chat completions API
  - Model: `llama3-70b-8192`
  - System prompt includes location context
  - Response via `evaluateJavascript("receiveGroqResponse('...')")`

### Constants
```kotlin
DEFAULT_URL = "file:///android_asset/AR_Dashboard_Landscape_Sidebar.html"
PREFS_NAME = "TapLinkPrefs"
BROWSER_PREFS_NAME = "BrowserPrefs"
```

### Other Components
- **BookmarksView** — bookmark management UI
- **ChatView** — AI chat interface with mic input
- **ColorWheelView** — color picker for text customization
- **SystemInfoView** — battery, time, connectivity status
- **FontIconView** — icon font rendering
- **NotificationService** — system notification listener
- **GroqInterface** — Groq API interface
- **DebugLog** — conditional logging wrapper
- **MyApplication** — Application subclass

---

# 3. RayDesk — Android Remote Desktop Streaming

## 3.1 Architecture Overview

Kotlin Android app for streaming a remote PC desktop to RayNeo X3 Pro AR glasses. Built on Moonlight (open-source NVIDIA GameStream/Sunshine client). Renders video in OpenGL with head-tracked virtual screen positioning.

### Package: `com.raydesk`

## 3.2 Streaming Layer (com.raydesk.streaming)

### MoonlightBridge
Core integration with Moonlight's `NvConnection`:
- `initializeDecoder()` — creates `MediaCodecDecoderRenderer`, wires `VideoSurfaceHolder`
- `connect()` — builds `StreamConfiguration`, creates `NvConnection`, starts streaming
- `connectToSavedServer()` — suspend function, looks up app by name, handles certificates
- `quitExistingSession()` — kills stale sessions before reconnecting
- `disconnect()` — stops connection
- Supports H.264, H.265 (HEVC), AV1
- Input methods: `sendMouseMove()`, `sendMouseClick()`, `sendKeyboard()`, `sendScroll()`

### StreamConfig
```kotlin
data class StreamConfig(
    val width: Int = 1920,
    val height: Int = 1080,
    val fps: Int = 60,
    val bitrate: Int = 20000  // kbps
)
```

### StreamManager
State machine: `Disconnected → Connecting → Connected`
Wraps Moonlight NvConnection for a cleaner API with Kotlin Flow.

### ServerDiscoveryManager / DiscoveredServer / SavedServer
mDNS-based server discovery and persistent server storage with Base64-encoded certificates.

### ReconnectionManager
Handles automatic reconnection with backoff.

## 3.3 Rendering Layer (com.raydesk.gl)

### StreamRenderer (998 lines)
OpenGL ES 3.0 renderer implementing `GLSurfaceView.Renderer`:

**Display modes:**
```kotlin
enum class DisplayMode {
    FLOATING_MONITOR,  // Screen in 3D space, head rotation moves camera
    KEYHOLE_PANNING,   // UV panning across desktop texture
    CURVED_MONITOR     // Cylindrical display
}
```

**Pipeline (per frame):**
1. Update video texture from SurfaceTexture
2. Apply pending theme change (thread-safe)
3. Video stall detection (5s timeout)
4. Decoupled rendering: FrameSlot check → texture update → render
5. Auto-disable test pattern after 3 video frames
6. Environment background (skybox/dome)
7. Video quad with shader uniforms (MVP, keyhole rect, cursor, CAS sharpening)
8. Stereo rendering for curved monitor (left/right eye viewports)
9. HUD overlay

**Shader uniforms:** uMVPMatrix, uKeyholeRect, uSTMatrix, uVideoTexture, uTestPatternEnabled, uTime, uCursorPos, uCursorEnabled, uZoomLevel, uDisplayMode, uCasSharpening, uTexelSize, uBezelEnabled/Color/Width, uAspectRatio

### FlatQuadMesh / CylinderMesh
Geometry primitives for flat and curved monitor rendering. Dynamic aspect ratio from stream resolution.

### ShaderUtils
GLSL shader compilation and program linking utilities.

### Environment Rendering
- **EnvironmentRenderer** — manages skybox + dome + dashboard + status rings
- **DomeMesh / DashboardMesh / MonitorFrameMesh / StatusRingMesh** — environment geometry
- **SkyboxRenderer** — procedural sky
- **PhysicalFrameRenderer** — monitor bezel
- **ScreenSpaceHudRenderer** — fixed-to-viewport HUD
- **StatusRingRenderer / StatusRingTextRenderer** — circular status indicators

## 3.4 Spatial Layer (com.raydesk.spatial)

### VirtualScreenController (484 lines)
Head-tracked virtual screen positioning:
- **Dampened follow**: coefficient 0.1 (not 100% world-locked, hides micro-jitter)
- **Stick-to-View**: lazy follow at 20° yaw / 12° pitch thresholds
- **Fixed distance**: 2.5m (waveguide focal plane sweet spot, avoids VAC conflict)
- **Scale-based zoom**: 0.5x–3.0x, multiplicative (1.25x in, 0.8x out)
- **Smooth animation**: 0.2s Lerp for zoom transitions
- **Cursor-centered panning**: when zoomed in, viewport follows cursor
- **Recenter**: corrects 3DoF yaw drift

### CylinderController
Curved monitor positioning with stereo left/right eye matrices, IPD offset.

### KeyholeViewport
Maps head rotation to UV coordinates for keyhole panning mode.

### Quaternion
Utility quaternion class for sensor fusion.

### OneEuroFilter
1€ filter for jitter reduction in head tracking data.

### EdgeGlint
Visual effect for screen edge indicators.

## 3.5 Video Pipeline (com.raydesk.video)

- **VideoTextureProvider** — OES texture from SurfaceTexture
- **VideoSurfaceHolder** — adapts SurfaceProvider to Moonlight's SurfaceHolder interface
- **FrameSlot** — lock-free frame buffer for decoupled rendering
- **GLTextureRenderer** — alternative renderer for binocular display
- **TestPatternGenerator** — procedural test pattern when no video

## 3.6 UI Layer (com.raydesk.ui)

- **ConnectionActivity** — server list, pairing, settings
- **StreamingActivity** — active streaming with GL view
- **CursorSettingsActivity** — cursor sensitivity configuration
- **PinEntryDialog** — pairing PIN entry
- **ServerListView / ServerListItem** — server browser
- **GameStyleMenuOverlay / StreamingMenuOverlay** — in-stream menus
- **FocusNavigator** — D-pad navigation support

## 3.7 Data Layer (com.raydesk.data)

- **SavedServer** — persisted server credentials with Base64 certs
- **ServerRepository** — SharedPreferences-based server storage
- **StreamingSettings** — streaming configuration persistence
- **CursorSettings** — cursor sensitivity/visibility
- **EnvironmentTheme / EnvironmentThemes** — visual theme definitions
- **StatusRingDataProvider** — provides data for status ring display

---

# 4. PhoenixHeadTracker — Windows C# Head Tracker

## 4.1 Architecture Overview

Windows Forms application (.NET Framework 4.7.2) that reads IMU euler angles from XREAL glasses via `AirAPI_Windows.dll` and outputs either mouse movement or OpenTrack UDP.

## 4.2 Native Interop (Form1.cs)
```csharp
[DllImport("AirAPI_Windows")] public static extern int StartConnection();
[DllImport("AirAPI_Windows")] public static extern int StopConnection();
[DllImport("AirAPI_Windows")] public static extern IntPtr GetEuler();
[DllImport("user32.dll")] static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
[DllImport("user32.dll")] static extern uint SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
```

## 4.3 Input Structs
```csharp
struct INPUT { uint type; InputUnion inputUnion; }
struct InputUnion { MOUSEINPUT mouseInput; }
struct MOUSEINPUT { int dx, dy; uint mouseData, dwFlags, time; IntPtr dwExtraInfo; }
```

## 4.4 Processing Pipeline (timer1_Tick, ~60Hz)

1. **Read Euler**: `GetEuler()` → float[3] (arr[0]=roll, arr[1]=pitch, arr[2]=yaw)
2. **Scale by screen**: `x = arr[2] * (screenWidthScale² / yawSpeed)`
3. **Delta computation**: `deltaX = xMapped - previousX` (clamped to <6000)
4. **Kalman filtering**: Per-axis filter with configurable q=0.01, r=0.002
5. **Drift compensation**: Low-pass filter + manual fight-drift buttons
6. **Output**:
   - **Mouse mode**: `SendInput()` with `MOUSEEVENTF_MOVE`, smoothing loop
   - **OpenTrack mode**: UDP 6-doubles (x,y,z,yaw,pitch,roll) to configurable IP:port

## 4.5 Kalman Filter
```csharp
class KalmanFilter {
    KalmanFilter(double q, double r, double p, double x);
    double Update(double measurement);  // prediction + measurement update
}
```
- q = process noise (0.01)
- r = measurement noise (0.002)
- p = estimate error covariance (1.0)

## 4.6 Key UI Controls
- Yaw/Pitch/Roll speed sliders
- Mouse smooth filter, Mouse delay filter
- Drift adjustment buttons (+/- per axis)
- IP address + port for OpenTrack
- Yaw/Pitch/Roll track value fields (screen scale)
- Invert checkboxes per axis
- Enable/disable checkboxes per axis

---

# 5. Fusion Library — xioTechnologies Sensor Fusion (C)

## 5.1 Overview

Lightweight AHRS (Attitude and Heading Reference System) library by Seb Madgwick. Used for fusing gyroscope, accelerometer, and magnetometer data into orientation quaternions.

**Header**: `Fusion.h` includes all sub-headers.

## 5.2 Data Types (FusionMath.h)

```c
typedef union { float array[3]; struct { float x, y, z; } axis; } FusionVector;
typedef union { float array[4]; struct { float w, x, y, z; } element; } FusionQuaternion;
typedef union { float array[9]; struct { float xx,xy,xz, yx,yy,yz, zx,zy,zz; } element; } FusionMatrix;
typedef union { float array[3]; struct { float roll, pitch, yaw; } angle; } FusionEuler;
```

**Constants:**
```c
#define FUSION_VECTOR_ZERO       ((FusionVector){0,0,0})
#define FUSION_VECTOR_ONES       ((FusionVector){1,1,1})
#define FUSION_QUATERNION_IDENTITY ((FusionQuaternion){1,0,0,0})
#define FUSION_MATRIX_IDENTITY   ((FusionMatrix){1,0,0, 0,1,0, 0,0,1})
#define FUSION_EULER_ZERO        ((FusionEuler){0,0,0})
```

## 5.3 Math Functions (FusionMath.h — all inline)

### Conversion
```c
float FusionDegreesToRadians(float degrees);    // degrees * PI / 180
float FusionRadiansToDegrees(float radians);    // radians * 180 / PI
float FusionArcSin(float value);                // asinf with clamping to avoid NaN
```

### Fast Math
```c
float FusionFastInverseSqrt(float x);  // Quake-style fast inverse sqrt
```

### Vector Operations
```c
bool FusionVectorIsZero(FusionVector v);
FusionVector FusionVectorAdd(FusionVector a, FusionVector b);
FusionVector FusionVectorSubtract(FusionVector a, FusionVector b);
FusionVector FusionVectorScale(FusionVector v, float s);
float FusionVectorSum(FusionVector v);                    // x+y+z
FusionVector FusionVectorHadamard(FusionVector a, FusionVector b);  // element-wise
FusionVector FusionVectorCross(FusionVector a, FusionVector b);
float FusionVectorDot(FusionVector a, FusionVector b);
float FusionVectorNormSquared(FusionVector v);
float FusionVectorNorm(FusionVector v);
FusionVector FusionVectorNormalise(FusionVector v);  // uses fast inverse sqrt
```

### Quaternion Operations
```c
FusionQuaternion FusionQuaternionAdd(FusionQuaternion a, FusionQuaternion b);
FusionQuaternion FusionQuaternionScale(FusionQuaternion q, float s);
float FusionQuaternionSum(FusionQuaternion q);
FusionQuaternion FusionQuaternionHadamard(FusionQuaternion a, FusionQuaternion b);
FusionQuaternion FusionQuaternionProduct(FusionQuaternion a, FusionQuaternion b);
FusionQuaternion FusionQuaternionVectorProduct(FusionQuaternion q, FusionVector v);
float FusionQuaternionNormSquared(FusionQuaternion q);
float FusionQuaternionNorm(FusionQuaternion q);
FusionQuaternion FusionQuaternionNormalise(FusionQuaternion q);
```

### Matrix Operations
```c
FusionVector FusionMatrixMultiply(FusionMatrix m, FusionVector v);
```

### Conversions (FusionMath.h lines 500+)
- Quaternion ↔ Rotation Matrix ↔ Euler Angles (ZYX convention)

## 5.4 Convention (FusionConvention.h)
```c
typedef enum {
    FusionConventionNwu,  // North-West-Up (X-Y-Z)
    FusionConventionEnu,  // East-North-Up (X-Y-Z)
    FusionConventionNed,  // North-East-Down (X-Y-Z)
} FusionConvention;
```

## 5.5 AHRS Algorithm (FusionAhrs.h / FusionAhrs.c)

### Settings
```c
typedef struct {
    FusionConvention convention;           // NWU, ENU, or NED
    float gain;                            // Filter gain (0.5 default)
    float gyroscopeRange;                  // deg/s, 0 = unlimited
    float accelerationRejection;           // degrees (90 default)
    float magneticRejection;               // degrees (90 default)
    unsigned int recoveryTriggerPeriod;    // samples before recovery
} FusionAhrsSettings;
```

### AHRS State
```c
typedef struct {
    FusionAhrsSettings settings;
    FusionQuaternion quaternion;
    FusionVector accelerometer, halfGravity;
    bool startup; float rampedGain, rampedGainStep;
    bool angularRateRecovery;
    FusionVector halfAccelerometerFeedback, halfMagnetometerFeedback;
    bool accelerometerIgnored, magnetometerIgnored;
    int accelerationRecoveryTrigger, accelerationRecoveryTimeout;
    int magneticRecoveryTrigger, magneticRecoveryTimeout;
} FusionAhrs;
```

### Functions
```c
void FusionAhrsInitialise(FusionAhrs *ahrs);
    // Sets default settings and restarts algorithm.

void FusionAhrsRestart(FusionAhrs *ahrs);
    // Resets quaternion to identity, enables startup mode (3s ramp at 10x gain).

void FusionAhrsSetSettings(FusionAhrs *ahrs, const FusionAhrsSettings *settings);
    // Applies settings with precomputed rejection thresholds.

void FusionAhrsUpdate(FusionAhrs *ahrs, FusionVector gyroscope, FusionVector accelerometer,
                       FusionVector magnetometer, float deltaTime);
    // Full 9-axis update. gyroscope in deg/s, accelerometer in g, magnetometer in calibrated units.
    // Algorithm: complementary filter with accelerometer/magnetometer feedback.
    // Restarts if gyroscope exceeds range. Ramps gain from 10x → target over 3s.
    // Applies acceleration/magnetic rejection with recovery triggers.

void FusionAhrsUpdateNoMagnetometer(FusionAhrs *ahrs, FusionVector gyroscope,
                                     FusionVector accelerometer, float deltaTime);
    // 6-axis update (no magnetometer). Zeros heading during startup.

void FusionAhrsUpdateExternalHeading(FusionAhrs *ahrs, FusionVector gyroscope,
                                      FusionVector accelerometer, float heading, float deltaTime);
    // Uses external heading (degrees) to synthesize equivalent magnetometer vector.

FusionQuaternion FusionAhrsGetQuaternion(const FusionAhrs *ahrs);
void FusionAhrsSetQuaternion(FusionAhrs *ahrs, FusionQuaternion quaternion);
FusionVector FusionAhrsGetGravity(const FusionAhrs *ahrs);
    // Returns direction of gravity as unit vector (halfGravity * 2).
FusionVector FusionAhrsGetLinearAcceleration(const FusionAhrs *ahrs);
    // Returns accelerometer minus gravity.
FusionVector FusionAhrsGetEarthAcceleration(const FusionAhrs *ahrs);
    // Returns acceleration in Earth frame (rotated by quaternion, gravity removed).
FusionAhrsInternalStates FusionAhrsGetInternalStates(const FusionAhrs *ahrs);
FusionAhrsFlags FusionAhrsGetFlags(const FusionAhrs *ahrs);
void FusionAhrsSetHeading(FusionAhrs *ahrs, float heading);
    // Rotates quaternion to match given heading (degrees).
```

### Internal States
```c
typedef struct {
    float accelerationError;           // degrees
    bool accelerometerIgnored;
    float accelerationRecoveryTrigger; // 0-1 normalized
    float magneticError;               // degrees
    bool magnetometerIgnored;
    float magneticRecoveryTrigger;     // 0-1 normalized
} FusionAhrsInternalStates;
```

### Flags
```c
typedef struct {
    bool startup;                // True during 3s startup ramp
    bool angularRateRecovery;    // True if gyro range exceeded
    bool accelerationRecovery;   // True if accel rejection triggered recovery
    bool magneticRecovery;       // True if mag rejection triggered recovery
} FusionAhrsFlags;
```

## 5.6 Gyroscope Bias Estimation (FusionBias.h / FusionBias.c)

Run-time gyroscope offset estimation and compensation.

### Settings
```c
typedef struct {
    float sampleRate;           // Hz (default 100)
    float stationaryThreshold;  // deg/s (default 3.0)
    float stationaryPeriod;     // seconds (default 3.0)
} FusionBiasSettings;
```

### Functions
```c
void FusionBiasInitialise(FusionBias *bias);
    // Initializes with default settings, zero offset.

void FusionBiasSetSettings(FusionBias *bias, const FusionBiasSettings *settings);
    // Computes filter coefficient: 2π * 0.02Hz * (1/sampleRate).
    // Computes timeout: stationaryPeriod * sampleRate.

FusionVector FusionBiasUpdate(FusionBias *bias, FusionVector gyroscope);
    // Must be called every sample at configured rate.
    // 1. Subtracts current offset from gyroscope.
    // 2. If any axis > threshold → reset timer, return corrected.
    // 3. If timer < timeout → increment timer, return corrected.
    // 4. If timer elapsed → update offset via high-pass filter, return corrected.

FusionVector FusionBiasGetOffset(const FusionBias *bias);
void FusionBiasSetOffset(FusionBias *bias, FusionVector offset);
```

## 5.7 Compass (FusionCompass.h / FusionCompass.c)

```c
float FusionCompass(FusionVector accelerometer, FusionVector magnetometer, FusionConvention convention);
    // Returns tilt-compensated magnetic heading in degrees.
    // For NWU: heading = atan2(west.x, north.x)
    // For ENU: heading = atan2(north.x, east.x)
    // For NED: heading = atan2(west.x, north.x) with inverted gravity
```

## 5.8 Sensor Models (FusionModel.h — inline)

```c
FusionVector FusionModelInertial(FusionVector uncalibrated, FusionMatrix misalignment,
                                  FusionVector sensitivity, FusionVector offset);
    // Calibration: misalignment * ((uncalibrated - offset) ⊙ sensitivity)

FusionVector FusionModelMagnetic(FusionVector uncalibrated, FusionMatrix softIronMatrix,
                                  FusionVector hardIronOffset);
    // Calibration: softIronMatrix * (uncalibrated - hardIronOffset)
```

## 5.9 Axis Remapping (FusionRemap.h — inline)

```c
FusionVector FusionRemap(FusionVector sensor, FusionRemapAlignment alignment);
```
24 alignment options: every permutation of ±X±Y±Z mapping, e.g.:
- `FusionRemapAlignmentPXPYPZ` — no remap (identity)
- `FusionRemapAlignmentPYNXPZ` — body X=sensor Y, body Y=-sensor X, body Z=sensor Z

---

# 6. Cross-Project Integration Notes

## Coordinate Systems
- **XRLinuxDriver internal**: North-West-Up (NWU)
- **XREAL SDK**: Uses NWU conversion quaternion {x=1,y=0,z=0,w=0}
- **Rokid SDK**: East-Up-South → NWU with fixed adjustment quaternion
- **RayNeo SDK**: East-Up-South → NWU with 15° offset
- **Viture Legacy**: NWU direct
- **Viture Carina**: EUS (GL) → NWU conversion
- **OpenTrack protocol**: EUS (x=-pos.y, y=pos.z, z=-pos.x from NWU)
- **Fusion library**: Configurable (NWU, ENU, NED)
- **Android TYPE_GAME_ROTATION_VECTOR**: EUS-based

## Shared Protocols
- **OpenTrack UDP**: 6 doubles (x,y,z,yaw,pitch,roll) + optional uint32 frame#
  - Used by: XRLinuxDriver (source + listener plugins), PhoenixHeadTracker
- **IPC shared memory**: `/dev/shm/` files for cross-process pose data
  - Used by: XRLinuxDriver ↔ gamescope ReShade, breezy_desktop
- **Moonlight/GameStream**: NvConnection-based streaming
  - Used by: RayDesk

## Per-Device FOV Reference
| Device | FOV (diagonal°) | Lens Ratio | Resolution |
|--------|-----------------|------------|------------|
| XREAL Air | 45 | 0.03125 | 1920x1080 |
| XREAL Air 2 Ultra | 52 | 0.03125 | 1920x1080 |
| XREAL One Pro | 57 | 0.03125 | 1920x1080 |
| Viture One | 40 | 0.05 | 1920x1080 |
| Viture Pro | 43 | 0.05 | 1920x1080 |
| Viture Luma | 50 | 0.05 | 1920x1200 |
| Viture Beast | 58 | 0.05 | 1920x1200 |
| Rokid | 45 | 0.03125 | 1920x1080 |
| RayNeo | 43 | 0.05 | 1920x1080 |
| RayNeo X3 Pro (RayDesk) | ~30 | N/A | 1280x480 (640x480/eye) |

## IMU Sample Rates
| Device | Native Hz | Used Hz |
|--------|----------|---------|
| XREAL | 1000 | 250 (forced) |
| RayNeo | 500 | 250 (forced) |
| Rokid | 90 | 90 |
| Viture (legacy) | 60-500 | configurable |
| Viture (Carina) | 1000 | 1000 |
| OpenTrack Listener | varies | up to 120 |
