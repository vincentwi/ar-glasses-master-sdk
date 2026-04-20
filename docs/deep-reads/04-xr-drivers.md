# DEEP Wave 2 — XR Drivers & Glasses Applications
## PhoenixHeadTracker, XRLinuxDriver, RayDesk, TAPLINKX3

Generated: 2026-04-20

---

## TABLE OF CONTENTS
1. PhoenixHeadTracker
2. XRLinuxDriver
3. RayDesk
4. TAPLINKX3

================================================================================
## 1. PHOENIXHEADTRACKER
================================================================================

### Overview
Windows .NET Framework 4.7.2 (C#) head-tracking app for XREAL Air glasses.
Captures IMU yaw/pitch/roll via AirAPI_Windows.dll (custom version supporting roll),
sends data to OpenTrack over UDP or controls mouse cursor directly for gaming.
License: GPL-3.0

### Architecture
- WinForms application (Form1.cs, Program.cs)
- P/Invoke into AirAPI_Windows.dll (native, via hidapi.dll) for glasses connection
- Kalman filter for smoothing rotation deltas
- UDP output to OpenTrack (6DOF packet: x, y, z, yaw, pitch, roll as doubles)
- Direct mouse control via Win32 SendInput API

### Source Files
- PhoenixHeadTracker/Program.cs — Entry point
- PhoenixHeadTracker/Form1.cs — Main form (825 lines)
- PhoenixHeadTracker/Form1.Designer.cs — WinForms designer
- PhoenixHeadTracker/Properties/AssemblyInfo.cs
- PhoenixHeadTracker/Properties/Resources.Designer.cs
- PhoenixHeadTracker/Properties/Settings.Designer.cs

### USB / Protocol
- Uses AirAPI_Windows.dll + hidapi.dll to connect to XREAL Air glasses
- No direct VID/PID in source — delegated to AirAPI_Windows.dll
- XREAL Air VID: 0x3318 (from XRLinuxDriver cross-reference)

### Classes & Functions

#### class Form1 : Form
P/Invoke declarations:
  - [DllImport("AirAPI_Windows")] static extern int StartConnection()
  - [DllImport("AirAPI_Windows")] static extern int StopConnection()
  - [DllImport("AirAPI_Windows")] static extern IntPtr GetEuler()
    Returns: float[3] — [roll, pitch, yaw] in degrees
  - [DllImport("user32.dll")] static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize)
  - [DllImport("user32.dll")] static extern IntPtr GetMessageExtraInfo()

Methods:
  - Form1() — Constructor; initializes bitmaps, graphics, center points for 3 picture boxes
  - void Form1_Load(object, EventArgs) — Gets screen dimensions, initializes INPUT struct
  - void timer1_Tick(object, EventArgs) — Main tracking loop:
      1. GetEuler() → float[3] (roll, pitch, yaw)
      2. Map to screen coordinates using speed trackbars
      3. Kalman filter on deltas
      4. If OpenTrack: pack 6 doubles (x,y,z,yaw,pitch,roll) → UDP send
      5. If MouseTrack: SendInput with filtered deltas
      6. Rotate UI indicator images
  - void timer2_Tick(object, EventArgs) — Post-connection reset (6s delay)
  - void ResetValues() — Zeros rotation, calculates distance offsets
  - void button2_Click(object, EventArgs) — "Connect Xreal Air" button handler
  - void buttonStartOpentrack_Click(object, EventArgs) — Start UDP to OpenTrack
  - void buttonStopOpentrack_Click(object, EventArgs) — Stop UDP
  - void buttonMouseTrackOn_Click(object, EventArgs) — Enable mouse tracking
  - void buttonMouseTrackOff_Click(object, EventArgs) — Disable mouse tracking
  - void buttonReset_Click(object, EventArgs) — Reset center view
  - void WndProc(ref Message m) — Intercepts WM_INPUT for mouse forwarding
  - void buttonFightDriftXPlus_Click / Minus_Click — Adjust drift compensation ±1
  - void buttonFightDriftYPlus_Click / Minus_Click
  - void buttonFightDriftRollPlus_Click / Minus_Click

Key fields:
  - isMouseTrack: bool — mouse mode active
  - isOpenTrack: bool — UDP mode active
  - FightDriftX/Y/Roll: int — drift compensation values
  - KalmanFilter instances for x, y, roll

#### class KalmanFilter
  - KalmanFilter(double q, double r, double p, double x)
      q: process noise, r: measurement noise, p: estimate error covariance, x: initial value
  - double Update(double measurement) → filtered value

### Protocol: OpenTrack UDP
  - Default endpoint: 127.0.0.1:4242
  - Packet: 6 * sizeof(double) = 48 bytes
  - Layout: [x, y, z, yaw, pitch, roll] — all doubles


================================================================================
## 2. XRLINUXDRIVER
================================================================================

### Overview
Linux C driver supporting XREAL, VITURE, Rokid, and RayNeo XR glasses.
Detects glasses via USB hotplug (libusb), reads IMU quaternions from device-specific
SDKs, translates to mouse/joystick output via libevdev uinput. Supports SBS 3D mode
toggling. Plugin architecture for Breezy Desktop, smooth follow, etc.
Architectures: x86_64 (all 4 brands), aarch64 (XREAL + VITURE only).

### Architecture
```
main() → pthread threads:
  ├── monitor_usb_devices_thread    — libusb hotplug detection
  ├── block_on_device_thread        — connects, calibrates, blocks on active device
  ├── monitor_config_file_thread    — inotify on config.ini
  ├── monitor_control_flags_thread  — watches control flags file
  └── manage_state_thread           — periodic state updates

Connection flow:
  USB hotplug → devices.c finds matching driver → connection_pool manages
  → driver connects (device-specific SDK) → IMU data → driver_handle_pose()
  → reference pose subtraction → plugin pipeline → outputs (mouse/joystick/IPC)
```

### USB VID/PIDs

#### XREAL (VID: 0x3318)
| PID    | Model          | FOV  | Calibration | Look-ahead |
|--------|----------------|------|-------------|------------|
| 0x0424 | Air            | 45°  | 15s         | 10.0       |
| 0x0428 | Air 2          | 45°  | 15s         | 10.0       |
| 0x0432 | Air 2 Pro      | 45°  | 15s         | 10.0       |
| 0x0426 | Air 2 Ultra    | 52°  | 15s         | 10.0       |
| 0x0435 | One Pro        | 57°  | 5s          | 25.0       |
| 0x0436 | One Pro        | 57°  | 5s          | 25.0       |
| 0x0437 | One            | 50°  | 5s          | 25.0       |
| 0x0438 | One            | 50°  | 5s          | 25.0       |
| 0x043e | 1S             | 52°  | 5s          | 25.0       |
| 0x043d | 1S             | 52°  | 5s          | 25.0       |

Pitch adjustments: One Pro = 35°, others = 0°
Resolution: 1920x1080, IMU: 250Hz (forced from 1000Hz native)
SBS modes: 3840x1080 @ 60/72/90Hz, 1920x1080 @ 60Hz SBS

#### VITURE (VID: 0x35ca)
| PID    | Model       | FOV  | Resolution | Calibration |
|--------|-------------|------|------------|-------------|
| 0x1011 | One         | 40°  | 1080p      | 1s          |
| 0x1013 | One         | 40°  | 1080p      | 1s          |
| 0x1017 | One         | 40°  | 1080p      | 1s          |
| 0x1015 | One Lite    | 40°  | 1080p      | 1s          |
| 0x101b | One Lite    | 40°  | 1080p      | 1s          |
| 0x1019 | Pro         | 43°  | 1080p      | 1s          |
| 0x101d | Pro         | 43°  | 1080p      | 1s          |
| 0x1131 | Luma        | 50°  | 1200p      | 1s          |
| 0x1121 | Luma Pro    | 52°  | 1200p      | 5s          |
| 0x1141 | Luma Pro    | 52°  | 1200p      | 5s          |
| 0x1101 | Luma Ultra  | 52°  | 1200p      | 10s         |
| 0x1104 | Luma Ultra  | 52°  | 1200p      | 10s         |
| 0x1151 | Luma Cyber  | 52°  | 1200p      | 5s          |
| 0x1201 | Beast       | 58°  | 1200p      | 1s          |

Pitch adjustments: One=6°, Pro=3°, Luma/Beast=-8.5°
IMU frequencies: 60, 90, 120, 240, 500 Hz (legacy); 1000Hz (Carina)
Display modes: 0x31 (1920x1080@60), 0x32 (3840x1080@60 SBS), 0x35 (3840x1080@90 SBS)
               0x41 (1920x1200@60), 0x42 (3840x1200@60 SBS), 0x45 (3840x1200@90 SBS)

#### Rokid (VID: ROKID_GLASS_VID — from SDK header)
| PID    | Notes          |
|--------|----------------|
| 0x162B | Max/Air        |
| 0x162C | Max/Air        |
| 0x162D | Max/Air        |
| 0x162E | Max/Air        |
| 0x162F | Max/Air        |
| 0x2002 |                |
| 0x2180 |                |

FOV: 45°, Resolution: 1920x1080, IMU: 90Hz, Calibration: 1s
Coordinate system: East-Up-South → NWU conversion with 5° offset

#### RayNeo (VID: 0x1bbb, PID: 0xaf50)
Models: NXTWEAR S/S+, Air 2, 2s, 3s/Pro
FOV: 43°, Resolution: 1920x1080, IMU: 250Hz (forced from 500Hz), Calibration: 5s
Coordinate system: East-Up-South → NWU with 15° offset
SDK functions: EstablishUsbConnection, StartXR, OpenIMU, GetHeadTrackerPose, etc.

### Source Files (102 total)

#### Core (src/)
- driver.c — main(), threading, pose handling, config monitoring (711 lines)
- devices.c — libusb hotplug, device enumeration (141 lines)
- imu.c — quaternion math, euler conversions (258 lines)
- outputs.c — libevdev mouse/joystick output, dead zone smoothing (646 lines)
- config.c — config file parsing
- state.c — driver state management
- plugins.c — plugin dispatch
- ipc.c — inter-process communication (shared memory)
- multitap.c — double/triple tap detection
- buffer.c — IMU ring buffer
- connection_pool.c — multi-device connection management
- files.c — file utilities
- logging.c — log management
- strings.c — string utilities
- epoch.c — timestamp utilities
- curl.c — HTTP client
- system.c — system utilities
- runtime_context.c — global runtime state

#### Device Drivers (src/devices/)
- xreal.c — XREAL Air/One driver (391 lines)
- viture.c — VITURE One/Luma/Pro driver (754 lines)
- rokid.c — Rokid Max/Air driver (249 lines)
- rayneo.c — RayNeo/TCL driver (267 lines)

#### Plugins (src/plugins/)
- breezy_desktop.c — Virtual desktop
- smooth_follow.c — Smooth follow mode
- virtual_display.c — Virtual display
- sideview.c — Side view
- opentrack_source.c — OpenTrack output
- opentrack_listener.c — OpenTrack input
- neck_saver.c — Neck saver limits
- metrics.c — Analytics
- gamescope_reshade_wayland.c — Gamescope integration
- device_license.c — License management
- custom_banner.c — Custom banner display

#### Features (src/features/)
- breezy_desktop.c — Breezy Desktop feature logic
- smooth_follow.c — Smooth follow feature
- sbs.c — Side-by-side 3D

### Key Data Types

#### imu_quat_type { float x, y, z, w }
#### imu_euler_type { float roll, pitch, yaw }
#### imu_vec3_type { float x, y, z }
#### imu_pose_type { imu_quat_type orientation, imu_vec3_type position, imu_euler_type euler, bool has_orientation, bool has_position, uint32_t timestamp_ms }

#### device_properties_type
  - char* brand, model
  - int hid_vendor_id, hid_product_id
  - uint8_t usb_bus, usb_address
  - calibration_setup_type calibration_setup
  - int resolution_w, resolution_h
  - float fov, lens_distance_ratio
  - int calibration_wait_s, imu_cycles_per_s, imu_buffer_size
  - float look_ahead_constant, look_ahead_frametime_multiplier
  - float look_ahead_scanline_adjust, look_ahead_ms_cap
  - bool sbs_mode_supported, firmware_update_recommended
  - bool provides_orientation, provides_position, can_be_supplemental

#### device_driver_type
  - char* id
  - supported_device_func → device_properties_type* (vendor_id, product_id, bus, address)
  - device_connect_func → bool
  - block_on_device_func → void
  - device_is_sbs_mode_func → bool
  - device_set_sbs_mode_func → bool (enabled)
  - is_connected_func → bool
  - disconnect_func → void (bool soft)

#### driver_config_type
  - bool disabled, mouse_mode, joystick_mode, external_mode
  - bool use_roll_axis, vr_lite_invert_x, vr_lite_invert_y
  - int mouse_sensitivity
  - char* output_mode
  - bool multi_tap_enabled, metrics_disabled
  - float dead_zone_threshold_deg
  - Debug flags: debug_threads, debug_joystick, debug_multi_tap, debug_ipc, debug_license, debug_device, debug_connections

#### driver_state_type
  - uint32_t heartbeat
  - char* connected_device_brand, connected_device_model
  - calibration_state_type calibration_state (NOT_CALIBRATED, CALIBRATING, CALIBRATED, WAITING_ON_USER)
  - bool sbs_mode_supported, sbs_mode_enabled
  - bool firmware_update_recommended
  - char** granted_features, license_features

#### control_flags_type
  - bool recenter_screen, recalibrate, force_quit
  - sbs_control_type sbs_mode (UNSET, ENABLE, DISABLE)
  - char* request_features

#### connection_pool_type
  - pthread_mutex_t mutex
  - connection_t** list, int count, capacity
  - int primary_index, supplemental_index

### Key Functions

#### driver.c
  - int main(int argc, const char** argv) — entry point, creates 5 pthreads
  - void driver_handle_pose(imu_pose_type pose) — main pose pipeline
  - bool driver_reference_pose(imu_pose_type* out_pose, bool* pose_updated)
  - bool driver_disabled() → config()->disabled
  - void reset_calibration(bool reset_device)
  - void setup_ipc()
  - void evaluate_block_on_device_ready()
  - void* block_on_device_thread_func(void* arg)
  - void update_config_from_file(FILE* fp)
  - void* monitor_config_file_thread_func(void* arg)
  - void* manage_state_thread_func(void* arg)
  - void handle_control_flags_update()
  - void* monitor_control_flags_file_thread_func(void* arg)
  - void handle_device_connection_changed(bool is_added, connected_device_type* device_info)
  - void* monitor_usb_devices_thread_func(void* arg)

#### imu.c
  - float degree_to_radian(float deg) → float
  - float radian_to_degree(float rad) → float
  - imu_quat_type normalize_quaternion(imu_quat_type q)
  - imu_quat_type conjugate(imu_quat_type q)
  - imu_quat_type multiply_quaternions(imu_quat_type q1, imu_quat_type q2)
  - imu_quat_type euler_to_quaternion_xyz/zyx/zxy(imu_euler_type euler)
  - imu_euler_type quaternion_to_euler_xyz/zyx/zxy(imu_quat_type q)
  - imu_quat_type device_pitch_adjustment(float adjustment_degrees)
  - imu_vec3_type vector_rotate(imu_vec3_type v, imu_quat_type q)
  - bool quat_equal(imu_quat_type q1, imu_quat_type q2)
  - float quat_small_angle_rad(imu_quat_type q1, imu_quat_type q2)

#### outputs.c
  - void init_outputs() / deinit_outputs() / reinit_outputs()
  - imu_euler_type get_euler_velocities(imu_euler_type* previous, imu_euler_type current, int imu_cycles_per_sec)
  - void handle_imu_update(imu_pose_type pose, imu_euler_type velocities, bool imu_calibrated, ipc_values_type* ipc_values)
  - void reset_pose_data(ipc_values_type* ipc_values)
  - bool wait_for_imu_start()
  - bool is_imu_alive()
  - int joystick_value(float input_velocity, float max_input_velocity)
  - static imu_quat_type quat_slerp(imu_quat_type a, imu_quat_type b, float t)
  - static float dead_zone_slerp_alpha(float angle_rad, float threshold_rad, int imu_cycles_per_s)

#### devices.c
  - void init_devices() — libusb_init, registers hotplug callback
  - void handle_device_connection_events() — libusb_handle_events_timeout
  - void deinit_devices()
  - connected_device_type* find_connected_device()
  - bool device_equal(device_properties_type*, device_properties_type*)
  - int hotplug_callback(libusb_context*, libusb_device*, libusb_hotplug_event, void*)

#### connection_pool.h
  - void connection_pool_init(pose_handler_t, reference_pose_getter_t)
  - void connection_pool_handle_device_added(const device_driver_type*, device_properties_type*)
  - bool connection_pool_is_connected()
  - bool connection_pool_connect_active()
  - void connection_pool_block_on_active()
  - void connection_pool_disconnect_all(bool soft)
  - bool connection_pool_device_is_sbs_mode()
  - bool connection_pool_device_set_sbs_mode(bool enabled)
  - void connection_pool_ingest_pose(const char* driver_id, imu_pose_type pose)
  - device_properties_type* connection_pool_primary_device()
  - device_properties_type* connection_pool_supplemental_device()

#### Plugin Interface (plugins.h)
  - start_func start
  - default_config_func / handle_config_line_func / set_config_func
  - setup_ipc_func / handle_ipc_change_func
  - modify_reference_pose_func / handle_reference_pose_updated_func
  - modify_pose_func / handle_pose_data_func / reset_pose_data_func
  - handle_state_func / handle_device_connect_func / handle_device_disconnect_func


================================================================================
## 3. RAYDESK
================================================================================

### Overview
Android Kotlin app for RayNeo X3 Pro AR glasses. Streams PC desktop via
Moonlight/Sunshine protocol. Three display modes: keyhole panning, floating
monitor (3D), curved widescreen. Uses Mercury SDK for binocular display.
License: GPL-3.0

### Architecture
```
ConnectionActivity → ServerListView → (discovery/pairing)
  → StreamingActivity
    ├── MoonlightBridge (Moonlight NvConnection)
    │   ├── MediaCodecDecoderRenderer (video decode)
    │   └── VideoSurfaceHolder → VideoTextureProvider (OES texture)
    ├── StreamRenderer (GLSurfaceView.Renderer)
    │   ├── DisplayMode: FLOATING_MONITOR | KEYHOLE_PANNING | CURVED_MONITOR
    │   ├── VirtualScreenController (floating mode)
    │   ├── KeyholeViewport (keyhole mode)
    │   ├── CylinderController (curved mode)
    │   ├── EnvironmentRenderer (skybox, status ring, frame)
    │   └── ScreenSpaceHudRenderer (FPS, signal)
    ├── HeadGazeCursor (temple gesture → cursor)
    └── StreamingMenuOverlay (radial settings)
```

### Source Files (58 Kotlin files)

#### streaming/
- StreamManager.kt — High-level stream state management
- MoonlightBridge.kt — Moonlight NvConnection integration (849 lines)
- StreamConfig.kt — Resolution/bitrate config
- StreamState.kt — Connection state enum
- ServerInfo.kt — Server metadata
- ServerDiscoveryManager.kt — mDNS discovery
- DiscoveredServer.kt — Discovered server model
- ReconnectionManager.kt — Auto-reconnect logic

#### spatial/
- VirtualScreenController.kt — 3D virtual screen positioning (484 lines)
- KeyholeViewport.kt — UV-based desktop panning
- CylinderController.kt — Curved cylinder display
- Quaternion.kt — Quaternion math
- OneEuroFilter.kt — 1€ noise filter
- TextureRect.kt — UV rectangle
- ViewportResult.kt — Viewport + cursor position
- EdgeGlint.kt — Edge indicator

#### gl/
- StreamRenderer.kt — Core OpenGL renderer (998 lines)
- ShaderUtils.kt — Shader compilation
- FlatQuadMesh.kt — Quad mesh
- CylinderMesh.kt — Cylindrical mesh

#### gl/environment/
- EnvironmentRenderer.kt — Skybox + frame + dashboard
- SkyboxRenderer.kt — Procedural skybox
- StatusRingRenderer.kt — Status ring around monitor
- StatusRingMesh.kt / StatusRingTextRenderer.kt
- PhysicalFrameRenderer.kt / MonitorFrameMesh.kt
- ScreenSpaceHudRenderer.kt — FPS/signal HUD
- DashboardRenderer.kt / DashboardMesh.kt
- DomeMesh.kt — Sky dome
- EnvironmentShaders.kt — Shader sources

#### video/
- VideoTextureProvider.kt — SurfaceTexture → OES texture
- VideoSurfaceHolder.kt — SurfaceHolder adapter
- GLTextureRenderer.kt — Texture rendering
- TestPatternGenerator.kt — Test pattern
- FrameSlot.kt — Frame synchronization

#### ui/
- StreamingActivity.kt — Main streaming UI (2040 lines)
- ConnectionActivity.kt — Server connection UI
- StreamingMenuOverlay.kt — Radial settings menu
- GameStyleMenuOverlay.kt — Game-style overlay
- ServerListView.kt / ServerListItem.kt / ServerItemViewModel.kt
- PinEntryDialog.kt — Pairing PIN entry
- NumberGridView.kt — Number grid
- FocusNavigator.kt — Focus navigation
- CursorSettingsActivity.kt — Cursor config
- ConnectionOverlay.kt — Connection status

#### input/
- HeadGazeCursor.kt — Head tracking → cursor

#### data/
- StreamingSettings.kt — Persistent settings
- ServerRepository.kt — Server persistence
- SavedServer.kt — Saved server model
- CursorSettings.kt — Cursor configuration
- StatusRingDataProvider.kt — Status data
- EnvironmentTheme.kt / EnvironmentThemes.kt — Theme definitions

#### test/
- RayDeskApplication.kt — Application class

### Key Classes & Signatures

#### class MoonlightBridge(activity: Activity, surfaceProvider: SurfaceProvider)
  - fun initializeDecoder(meteredConnection: Boolean = false, hdrEnabled: Boolean = false, glRenderer: String = ""): MediaCodecDecoderRenderer
  - fun setStreamConfig(config: StreamConfig)
  - fun setConnectionListener(listener: NvConnectionListener)
  - fun setResolutionListener(listener: StreamResolutionListener)
  - fun notifyActualResolution(actualWidth: Int, actualHeight: Int)
  - fun getSupportedVideoFormats(): Int
  - fun connect(hostAddress: String, port: Int, httpsPort: Int, app: NvApp, serverCert: X509Certificate, cryptoProvider: LimelightCryptoProvider, uniqueId: String)
  - suspend fun quitExistingSession(server: SavedServer, port: Int, httpsPort: Int): Boolean
  - suspend fun connectToSavedServer(server: SavedServer, appName: String, port: Int, httpsPort: Int)
  - fun disconnect()
  - fun release()
  - fun sendAbsolutePosition(x: Int, y: Int, refWidth: Int = 1920, refHeight: Int = 1080)
  - fun centerCursor(refWidth: Int = 1920, refHeight: Int = 1080)
  - fun sendMouseClick(button: Byte = MouseButtonPacket.BUTTON_LEFT)
  - fun sendMouseScroll(direction: Int)
  - fun sendKeyboardShortcut(vkCode: Int, modifiers: Byte)
  - fun switchToMonitor(monitorNumber: Int) — CTRL+ALT+SHIFT+F1-F12
  - fun generatePairingPin(): String
  - suspend fun pairWithServer(address: String, pin: String): PairingResult
  - fun createSavedServer(address: String, result: PairingResult.Success): SavedServer
  Companion: DEFAULT_WIDTH=1920, DEFAULT_HEIGHT=1080, DEFAULT_FPS=60, DEFAULT_BITRATE_KBPS=20000

#### class StreamManager
  - val currentState: StreamState
  - fun connect(host: String, config: StreamConfig): Flow<StreamState>
  - fun disconnect()
  - fun getDiscoveredServers(): Flow<List<ServerInfo>>

#### class VirtualScreenController(screenDistance: Float, screenHeight: Float, screenAspect: Float)
  Constants: FIXED_DISTANCE=2.5f, MIN_SCALE=0.5f, MAX_SCALE=3.0f, DAMPENING_COEFF=0.1f
  - fun updateHeadPose(yaw: Float, pitch: Float)
  - fun recenter(currentYaw: Float, currentPitch: Float)
  - fun updateAspectRatio(width: Int, height: Int)
  - fun updateCursorPosition(cursorX: Float, cursorY: Float)
  - fun getViewportUVRect(): TextureRect
  - fun isCursorPanningActive(): Boolean
  - fun zoomIn() / zoomOut() / resetZoom()
  - fun setScale(scale: Float)
  - fun updateZoomAnimation(deltaTime: Float)
  - fun getZoomLevel(): Float — 0-1
  - fun getCurrentScale(): Float
  - fun isZoomAnimating(): Boolean
  - fun getScreenModelMatrix(): FloatArray — 4x4 column-major
  - fun getHeadViewMatrix(): FloatArray
  - fun configureProjection(fovDegrees: Float, aspect: Float, near: Float, far: Float)
  - fun getProjectionMatrix(): FloatArray
  - fun getMVPMatrix(): FloatArray

#### class StreamRenderer(context: Context) : GLSurfaceView.Renderer, GLTextureRenderer.Renderer
  Properties:
    @Volatile displayMode: DisplayMode (FLOATING_MONITOR, KEYHOLE_PANNING, CURVED_MONITOR)
    videoProvider: VideoTextureProvider?
    keyholeViewport: KeyholeViewport?
    virtualScreenController: VirtualScreenController?
    @Volatile headYawDegrees/headPitchDegrees: Float
    @Volatile cursorX/cursorY: Float
    testPatternEnabled: Boolean
    casSharpening: Float (0-1)
    stereoEnabled: Boolean
  Methods:
    onSurfaceCreated / onSurfaceChanged / onDrawFrame — GLSurfaceView lifecycle
    fun updateStreamResolution(width: Int, height: Int)
    fun recenterVirtualScreen() / recenterCurvedMonitor() / recenterKeyhole()
    fun setVirtualScreenScale(scale: Float)
    fun setCursorTrackingEnabled(enabled: Boolean)
    fun setCurvedMonitorRadius(radius: Float)
    fun setEnvironmentEnabled(enabled: Boolean)
    fun setEnvironmentTheme(theme: EnvironmentTheme)
    fun setHudConnectionQuality(quality: Int)
    fun setHudInputMode(mode: String)

#### enum DisplayMode { FLOATING_MONITOR, KEYHOLE_PANNING, CURVED_MONITOR }

#### sealed class PairingResult
  - data class Success(serverCert, clientCert, clientKey, serverUuid, serverName)
  - object WrongPin
  - data class Failed(reason: String)

#### interface StreamResolutionListener
  - fun onStreamResolutionChanged(actualWidth: Int, actualHeight: Int)

### Protocol: Moonlight/Sunshine
- Discovery: mDNS on local network
- Pairing: PIN-based (4-digit), uses X.509 certificates + RSA keys
- Streaming port: 47989 (HTTP), auto-discover HTTPS
- Video: H.264 / H.265 / AV1, configurable resolution/bitrate
- Audio: Stereo, AndroidAudioRenderer
- Input: Absolute mouse position, keyboard shortcuts, mouse scroll
- Unique ID: "0123456789ABCDEF" (fixed for compatibility)


================================================================================
## 4. TAPLINKX3
================================================================================

### Overview
Android Kotlin browser shell for RayNeo X3 Pro AR glasses. Dual-eye rendering
mirrors a WebView into left + right eye viewports with a precision cursor.
Custom radial keyboard. Voice control via Groq API. Bookmarks management.
TapLink AI chat via Groq. Uses Mercury SDK (com.ffalconxr.mercury) for IPC.
License: Apache 2.0

### Architecture
```
MainActivity : AppCompatActivity
  ├── DualWebViewGroup — Dual-eye rendering container
  │   ├── WebView (left eye) — main web content
  │   ├── SurfaceView (right eye) — mirrored preview via PixelCopy
  │   ├── CustomKeyboardView × 2 — custom radial keyboard (mirrored)
  │   ├── BookmarksView — bookmark management
  │   └── ChatView — TapLink AI chat
  ├── SensorManager — TYPE_GAME_ROTATION_VECTOR for head tracking
  │   ├── Anchored mode (3DoF) — quaternion-based, configurable smoothness
  │   └── Cursor mode — relative motion with gain control
  ├── GestureDetector — temple gesture detection
  │   ├── Single tap → click/focus
  │   ├── Double tap → back navigation
  │   └── Triple tap → re-center (anchored mode)
  ├── GroqInterface — Groq API bridge (chat + TTS)
  ├── GroqAudioService — Speech-to-text via Groq
  └── Mercury SDK IPC — GPS from companion phone app
```

### Source Files (18 Kotlin files)

#### Main
- MainActivity.kt — 6339 lines, main activity with all gesture/sensor/UI logic
- DualWebViewGroup.kt — Dual-eye WebView container with cursor, mirroring
- MyApplication.kt — Application class

#### Input
- CustomKeyboardView.kt — Custom keyboard (1020 lines)
  Layouts: LETTERS (QWERTY + symbols), SYMBOLS (numbers + special chars)
  Modes: anchored (cursor hover-click), focus-driven (swipe navigation)
- WebAppInterface.kt — JavaScript interface bridge

#### AI / Voice
- GroqInterface.kt — Groq chat API integration (372 lines)
  Model: "groq/compound", TTS: "canopylabs/orpheus-v1-english"
- GroqAudioService.kt — Groq audio transcription
- ChatView.kt — TapLink AI chat WebView (409 lines)

#### Data
- BookmarksView.kt — Bookmark management UI (1214 lines)
- Constants.kt — App constants
- DebugLog.kt — Debug logging

#### UI
- SystemInfoView.kt — System information display
- FontIconView.kt — Font Awesome icon view
- ColorWheelView.kt — Color picker
- NotificationService.kt — Notification listener

#### Tests
- BookmarksLogicTest.kt — Bookmark unit tests
- ExampleUnitTest.kt / ExampleInstrumentedTest.kt

### Key Classes & Signatures

#### class MainActivity : AppCompatActivity, DualWebViewGroup.DualWebViewGroupListener, NavigationListener, CustomKeyboardView.OnKeyboardActionListener, BookmarkListener, BookmarkKeyboardListener, LinkEditingListener, DualWebViewGroup.MaskToggleListener, DualWebViewGroup.AnchorToggleListener, DualWebViewGroup.WindowCallback
  Key fields:
    - dualWebViewGroup: DualWebViewGroup
    - sensorManager: SensorManager
    - rotationSensor: Sensor? (TYPE_GAME_ROTATION_VECTOR)
    - isAnchored: Boolean — anchored/3DoF mode
    - smoothnessLevel: Int (0-100, default 40)
    - cursorSensitivity: Int (0-100, default 50)
    - cursorGain: Float (0-0.9)
    - TRANSLATION_SCALE = 2000f
    - TAP_INTERVAL = 400L, TRIPLE_TAP_DURATION = 800L
  Key methods:
    - fun updateCursorSensitivity(progress: Int)
    - fun refreshCursor() / refreshCursor(visible: Boolean)
    - fun centerCursor(visible: Boolean)
    - fun isMousePointerEvent(event: MotionEvent): Boolean
    - fun toggleMouseTapMode()
    - fun cancelActiveTouchScrollGesture()
  Interfaces implemented:
    NavigationListener: onNavigationBackPressed/ForwardPressed, onQuitPressed, onSettingsPressed, onRefreshPressed, onHomePressed, onHyperlinkPressed
    LinkEditingListener: onShowLinkEditing, onHideLinkEditing, onSendCharacterToLink, etc.

#### class DualWebViewGroup — Dual-eye rendering container
  Interfaces:
    - DualWebViewGroupListener
    - KeyboardListener { onShowKeyboard(), onHideKeyboard() }
    - MaskToggleListener
    - AnchorToggleListener
    - WindowCallback

#### class CustomKeyboardView(context: Context, attrs: AttributeSet?) : LinearLayout
  Interface OnKeyboardActionListener:
    - fun onKeyPressed(key: String)
    - fun onBackspacePressed()
    - fun onEnterPressed()
    - fun onHideKeyboard()
    - fun onClearPressed()
    - fun onMoveCursorLeft() / onMoveCursorRight()
    - fun onMicrophonePressed()
  Methods:
    - fun setOnKeyboardActionListener(listener: OnKeyboardActionListener)
    - fun setCustomTextColor(color: Int)
    - fun getCustomTextColor(): Int
    - fun copyStateFrom(source: CustomKeyboardView)
    - fun updateHover(x: Float, y: Float) / updateHoverScreen(screenX, screenY, uiScale)
    - fun clearHover()
    - fun handleAnchoredTap(x: Float, y: Float)
    - fun setAnchoredMode(anchored: Boolean)
    - fun performFocusedTap()
    - fun handleFlingEvent(velocityX: Float)
    - fun handleDrag(x: Float, action: Int)
    - fun setMicActive(active: Boolean)

#### class GroqInterface(context: Context, webView: WebView)
  @JavascriptInterface methods:
    - fun ping(): String → "pong"
    - fun getActivePageUrl(): String
    - fun chatWithGroq(message: String, historyJson: String, ttsEnabled: Boolean)
    - fun speakWithOrpheus(text: String)
    - fun openUrlInNewTab(url: String)
  Internal:
    - API: https://api.groq.com/openai/v1/chat/completions
    - TTS: https://api.groq.com/openai/v1/audio/speech
    - Model: "groq/compound"
    - TTS Model: "canopylabs/orpheus-v1-english", voice: "hannah"

#### class ChatView(context: Context, attrs: AttributeSet?) : LinearLayout
  Properties:
    - keyboardListener: DualWebViewGroup.KeyboardListener?
    - micListener: MicListener?
    - val webView: WebView — loads clean_chat.html
  Interface MicListener { fun onMicrophonePressed() }
  Methods:
    - fun disableSystemKeyboard()
    - fun closeMenu()
    - fun handleAnchoredTap(localX: Float, localY: Float): Boolean
    - fun updateHover(screenX: Float, screenY: Float): Boolean
    - fun updateHoverLocal(localX: Float, localY: Float): Boolean
    - fun clearHover()
    - fun sendTextToFocusedInput(text: String)
    - fun sendBackspaceToFocusedInput()
    - fun sendEnterToFocusedInput()
    - fun setMicActive(active: Boolean)
    - fun insertVoiceText(text: String)

#### data class BookmarkEntry(id: String, url: String, isHome: Boolean)

#### interface BookmarkListener
  - fun onBookmarkSelected(url: String)
  - fun getCurrentUrl(): String

#### class BookmarkManager(context: Context)
  - fun getBookmarks(): List<BookmarkEntry>
  - fun addBookmark(url: String): BookmarkEntry
  - fun updateBookmark(id: String, newUrl: String)
  - fun deleteBookmark(id: String)
  - fun setAsHome(id: String)

#### interface BookmarkKeyboardListener
  - fun onShowKeyboardForEdit(text: String)
  - fun onShowKeyboardForNew()
  - fun onHideKeyboard()

#### class BookmarksView(context: Context, attrs: AttributeSet?) : LinearLayout
  Methods:
    - fun setAnchoredMode(anchored: Boolean)
    - fun refreshBookmarks()
    - fun getHomeUrl(): String
    - fun getCurrentEditField(): EditText?
    - fun getBookmarkManager(): BookmarkManager
    - fun handleFling(isForward: Boolean)
    - fun updateHover(localX: Float, localY: Float): Boolean
    - fun handleAnchoredTap(localX: Float, localY: Float): Boolean
    - fun handleDrag(x: Float, action: Int)
    - fun performFocusedTap()
    - fun handleTap(): Boolean
    - fun toggle()
    - fun isEditing(): Boolean
    - fun handleDoubleTap(): Boolean
    - fun startEditWithId(bookmarkId: String?, currentUrl: String)
    - fun endEdit()
    - fun onEnterPressed()
    - fun handleKeyboardInput(text: String)
    - fun setBookmarkListener(listener: BookmarkListener)
    - fun setKeyboardListener(listener: BookmarkKeyboardListener)

#### interface NavigationListener
  - fun onNavigationBackPressed()
  - fun onNavigationForwardPressed()
  - fun onQuitPressed()
  - fun onSettingsPressed()
  - fun onRefreshPressed()
  - fun onHomePressed()
  - fun onHyperlinkPressed()

#### interface LinkEditingListener
  - fun onShowLinkEditing()
  - fun onHideLinkEditing()
  - fun onSendCharacterToLink(character: String)
  - fun onSendBackspaceInLink()
  - fun onSendEnterInLink()
  - fun onSendClearInLink()
  - fun isLinkEditing(): Boolean

### Mercury SDK Integration
- Package: com.ffalconxr.mercury.ipc
- Launcher class for IPC with RayNeo companion app
- GPSIPCHelper for GPS data from phone
- Used for: GPS location injection into WebView, system IPC

### Gesture Handling
| Gesture | Anchored Mode | Cursor Mode |
|---------|---------------|-------------|
| Single Tap | Click at cursor | Click at cursor |
| Double Tap (temple) | Go back | Go back |
| Triple Tap (temple) | Re-center | N/A |
| Swipe fwd/back | Keyboard navigation | Scroll |
| Long-press | Right-click | Right-click |

### Head Tracking
- Sensor: TYPE_GAME_ROTATION_VECTOR (no magnetometer — drifts over 5-10 min)
- Anchored mode: quaternion → yaw/pitch with double-exponential smoothing
- Cursor mode: relative delta with configurable gain (0-0.9)
- Frame rate: ~120 FPS max (MIN_FRAME_INTERVAL_MS = 8L)
- Smoothness controlled by user pref (0-100 → smoothing factor)


================================================================================
## CROSS-REFERENCE: SHARED CONCEPTS
================================================================================

### Quaternion Conventions
- All repos use NWU (North-West-Up) coordinate system for final orientation
- XREAL: device → NWU via conversion quat {1,0,0,0}
- Rokid: East-Up-South → NWU with 5° pitch offset
- RayNeo: East-Up-South → NWU with 15° pitch offset
- VITURE: Legacy=NWU direct; Carina=EUS(GL) → NWU conversion

### XREAL Air VID/PID Cross-Reference
- PhoenixHeadTracker: Uses AirAPI_Windows.dll (VID 0x3318 + hidapi)
- XRLinuxDriver: VID 0x3318, PIDs 0x0424-0x043e (10 products)
- Both use nrealAirLinuxDriver / AirAPI_Windows for low-level HID

### Display Resolutions
- Standard: 1920x1080 (XREAL, Rokid, RayNeo, VITURE Gen1)
- Extended: 1920x1200 (VITURE Luma/Pro/Ultra/Cyber/Beast)
- SBS: 3840x1080 or 3840x1200

### IMU Rates
- XREAL: 250Hz (forced from 1000Hz native)
- VITURE Gen1: 60-500Hz (configurable); Carina: 1000Hz
- Rokid: 90Hz
- RayNeo: 250Hz (forced from 500Hz)

### Key Technologies by Repo
| Feature | Phoenix | XRLinux | RayDesk | TapLink |
|---------|---------|--------|---------|---------|
| Language | C# | C | Kotlin | Kotlin |
| Platform | Windows | Linux | Android (X3 Pro) | Android (X3 Pro) |
| Glasses | XREAL Air | XREAL/VITURE/Rokid/RayNeo | RayNeo X3 Pro | RayNeo X3 Pro |
| Input | Mouse/UDP | Mouse/Joystick/IPC | Moonlight | WebView |
| Head tracking | 3DoF | 3DoF (+6DoF VITURE) | 3DoF | 3DoF |
| Display | N/A | SBS toggle | OpenGL stereo | Dual WebView |
| AI | No | No | No | Groq API |
