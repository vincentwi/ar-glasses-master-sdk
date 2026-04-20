# DEEP-wave1c-xr-tools.md
# Exhaustive Deep-Read: open-wearables, xreal-webxr, decky-XRGaming

Generated: 2026-04-20

---

## TABLE OF CONTENTS

1. [REPO 1: xreal-webxr](#repo-1-xreal-webxr)
2. [REPO 2: decky-XRGaming](#repo-2-decky-xrgaming)
3. [REPO 3: open-wearables (MCP server)](#repo-3-open-wearables)

---

# REPO 1: xreal-webxr

**Repository:** /tmp/glasses-sdk-repos/xreal-webxr/
**Author:** jakedowns
**Purpose:** WebXR bindings and test utilities for XREAL (Nreal) AR glasses via WebHID API
**License:** Provided with disclaimer of warranty (no explicit OSS license)
**Status:** Work in progress

## 1.1 README Summary

- WebXR support for XREAL devices (Air + Light models)
- Based on combined effort of the XREAL Open Source Community
- Links to companion projects: AirDesktopViewer (Windows), breezy desktop (Linux), Monado OpenXR, etc.
- Open-source community drivers for Windows, Android, Linux, Mac, Rust, Web
- Roadmap mentions OpenXR and CloudXR integration

## 1.2 Architecture

```
xreal-webxr/
├── common.js                 # Device detection, connection management (Air + Light)
├── index.html                # Modern landing page with connect button (WebUSB)
├── index_old.html            # Legacy demo page with full IMU/brightness/firmware UI
├── js_air/                   # XREAL Air glasses protocol implementation
│   ├── glasses.js            # Glasses class (extends EventTarget) - HID reports, IMU
│   ├── manager.js            # Manager functions: firmware, brightness, IMU, SN
│   ├── protocol.js           # Wire protocol: message IDs, CRC32, packet parsing
│   ├── sdkgraph.dot          # SDK dependency graph (Graphviz)
│   └── samples.csv, samples-2.csv  # Sample IMU data
├── js_light/                 # XREAL Light glasses protocol implementation
│   ├── glasses.js            # Glasses class for Light model
│   ├── manager.js            # Manager functions for Light model
│   ├── protocol.js           # Light protocol: different framing (STX/ETX), CRC32
│   └── protocolYmodem.js     # Ymodem firmware upload protocol for Light
├── tools/
│   ├── sparkline.js          # SVG sparkline renderer for IMU visualization
│   └── http.js               # Simple HTTP client wrapper for Nreal API
├── DISCLAIMER.md             # Warranty disclaimer
├── key.pem, cert.pem         # SSL certificates for local HTTPS testing
└── .github/FUNDING.yml       # GitHub sponsors config
```

**Entry Points:**
- `index.html` - Modern connect page (uses WebUSB)
- `index_old.html` - Full-featured demo (uses WebHID, IMU streaming, brightness, firmware)

**Dependencies:** None (vanilla JS, ES modules, browser WebHID/WebUSB APIs)

## 1.3 Source Files — Complete API Reference

### common.js — Device Detection & Connection Management

```
Global State:
  let curGlasses = null           — Currently connected glasses instance
  window.curGlassesArray = []     — Array of all connected glasses

Imports:
  GlassesLight from './js_light/glasses.js'
  * as managerLight from './js_light/manager.js'
  GlassesAir from './js_air/glasses.js'
  * as managerAir from './js_air/manager.js'
```

**Functions:**

```
export function isNrealDevice(device) → boolean
  Params: device (HIDDevice) — a WebHID device object
  Returns: true if device.productId matches known XREAL product IDs
  Product IDs: 0x0423 (Air MCU), 0x573C (Light), 0x0424 (Air alt)

export function addHidListener() → void
  Sets navigator.hid.onconnect and ondisconnect handlers
  Air product IDs: 1059 (0x0423), 1060 (0x0424)
  Light product IDs: 22332 (0x573C), 22336 (0x5740)
  Creates GlassesAir or GlassesLight instance on connect

export function checkConnection() → Promise<Glasses|undefined>
  Returns curGlasses if already connected, else queries navigator.hid.getDevices()
  Filters for Nreal devices, checks canCommand, returns first commandable device

export function requestDevice() → Promise<Glasses|undefined>
  Opens WebHID device picker with vendor filters:
    0x0486 (ASUS), 0x0483 (STMicroelectronics), 0x0482 (Kyocera), 0x3318 (Gleaming Reality)
  Returns GlassesAir or GlassesLight instance

export async function connectDevice() → Promise<Glasses>
  Checks existing connection, then requests new device if needed

export async function disconnectDevice() → void
  Closes and nullifies curGlasses

export function deviceIsAir(device) → boolean
  Checks productId == 1059 || 1060

export function deviceIsLight(device) → boolean
  Checks productId == 22332 || 22336

export function isAirOrLight() → 1 | 2 | null | 'not found device'
  Returns 1 for Air, 2 for Light, null/string for not found

export function hexStream2int8Array(captureString) → Uint8Array
  Converts hex string to byte array

export function parseHexString(captureString) → parsed report
  Uses glasses.protocol.parse_rsp on hex stream
```

### js_air/glasses.js — XREAL Air Glasses Class

```
export default class Glasses extends EventTarget {
  Properties:
    imu_poller_instance: RepeatingDeviceReportPoll — IMU polling timer
    _device: HIDDevice — underlying WebHID device
    _interestMsg: Array — message interest list
    _reports: Map<number, report> — received reports keyed by msgId
    _captures: Array — captured packets
    setBrightness: Function — bound from Manager

  constructor(device: HIDDevice)
    Opens device, sets input report handler, creates IMU poller (100ms interval)
    Exposes as window.glasses

  get device() → HIDDevice

  startIMUPolling() → void
    Starts the RepeatingDeviceReportPoll timer

  stopIMUPolling() → void
    Stops the polling timer

  renderSparklines() → void
    Renders sparkline SVG visualizations of IMU data in browser

  dumpCaptures() → void
    Logs captured packets to console

  connect() → Promise<void>
    Opens HID device if not already opened

  _handleInputReport({device, reportId, data}) → void
    Parses incoming HID report via Protocol.parse_rsp
    Handles msgId 0x0 (IMU data) — updates sparklines, bars
    Handles P_BUTTON_PRESSED (0x6C05) — brightness button events
    Stores report in _reports Map

  sendReport(msgId: number, payload: Array) → void
    Builds command via Protocol.cmd_build, sends via device.sendReport(0x00, cmd)

  async sendReportTimeout(msgId: number, payload=[], timeout=1000) → report|null
    Sends report and polls _reports map until response or timeout (10ms intervals)

  async isMcu() → boolean
    Sends R_ACTIVATION_TIME, returns true if response received

  toString() → string
    Format: "<Glasses deviceName=... vid=... pid=...>"
}

class RepeatingDeviceReportPoll {
  Properties:
    timer: number|null
    opts: {interval: number, callback: Function}
    ended: boolean

  constructor(opts?: {interval?: number, callback?: Function})

  start() → void
    Starts setInterval with opts.callback

  end() → void
    Sets ended flag to stop on next tick
}
```

### js_air/protocol.js — Air Protocol Constants & Functions

```
Constants:
  HEAD = 0xfd
  MSG_ID_OFS = 15, PAYLOAD_OFS = 22, LEN_OFS = 5, CRC_OFS = 1, TS_OFS = 7
  NREAL_VENDOR_ID = 0x3318
  BOOT_PRODUCT_ID = 0x0423
  IMU_TIMEOUT = 250

  ERRORS: {
    DEVICE3_ERROR_NO_ERROR: 0, ..._NO_DEVICE: 1, ..._NO_HANDLE: 2,
    ..._NO_ALLOCATION: 3, ..._WRONG_SIZE: 4, ..._FILE_NOT_OPEN: 5,
    ..._FILE_NOT_CLOSED: 6, ..._LOADING_FAILED: 7, ..._SAVING_FAILED: 8,
    ..._UNPLUGGED: 9, ..._UNEXPECTED: 10, ..._WRONG_SIGNATURE: 11,
    ..._INVALID_VALUE: 12, ..._NOT_INITIALIZED: 13, ..._PAYLOAD_FAILED: 14,
    ..._UNKNOWN: 15
  }

class Device3Packet {
  // IMU packet structure (56 bytes):
  // signature[2], temperature[2], timestamp[8],
  // angular_multiplier[2], angular_divisor[4],
  // angular_velocity_x[3], angular_velocity_y[3], angular_velocity_z[3],
  // acceleration_multiplier[2], acceleration_divisor[4],
  // acceleration_x[3], acceleration_y[3], acceleration_z[3],
  // magnetic_multiplier[2], magnetic_divisor[4],
  // magnetic_x[2], magnetic_y[2], magnetic_z[2],
  // checksum[4], _padding[6]
  constructor() — initializes all fields as Uint8Array
}

MESSAGES: {
  R_MCU_APP_FW_VERSION: 0x26,   R_GLASSID: 0x15,
  R_DP7911_FW_VERSION: 0x16,    R_ACTIVATION_TIME: 0x29,
  W_ACTIVATION_TIME: 0x2A,      W_SLEEP_TIME: 0x1E,
  R_IMU_DATA: 0x80,             UNKNOWN_40: 0x40,
  W_TOGGLE_IMU: 0x19,           W_CANCEL_ACTIVATION: 0x19,
  R_DSP_VERSION: 0x18,
  W_UPDATE_DSP_APP_FW_PREPARE: 0x45, W_UPDATE_DSP_APP_FW_START: 0x46,
  W_UPDATE_DSP_APP_FW_TRANSMIT: 0x47, W_UPDATE_DSP_APP_FW_FINISH: 0x48,
  E_DSP_ONE_PACKGE_WRITE_FINISH: 0x6C0E,
  E_DSP_UPDATE_ENDING: 0x6C11,  E_DSP_UPDATE_PROGRES: 0x6C10,
  W_UPDATE_MCU_APP_FW_PREPARE: 0x3E, W_UPDATE_MCU_APP_FW_START: 0x3F,
  W_UPDATE_MCU_APP_FW_TRANSMIT: 0x40, W_UPDATE_MCU_APP_FW_FINISH: 0x41,
  W_BOOT_JUMP_TO_APP: 0x42,     W_MCU_APP_JUMP_TO_BOOT: 0x44,
  R_DP7911_FW_IS_UPDATE: 0x3C,  W_UPDATE_DP: 0x3D,
  W_BOOT_UPDATE_MODE: 0x1100,   ...START: 0x1103, ...TRANSMIT: 0x1104,
  P_BUTTON_PRESSED: 0x6C05,     P_UKNOWN_HEARTBEAT: 0x6C02,
  W_BRIGHTNESS: (uses W_BRIGHTNESS msg for get/set)
}

Functions:
  export function keyForHex(hex: number) → string|null
  export function listKnownCommands() → void (console.table)
  export function cmd_build(msgId: number, payload: Uint8Array) → Uint8Array(64)
    Builds 64-byte HID command with HEAD, CRC32, msgId, payload
  export function parse_rsp(rsp: Uint8Array) → {msgId, status, payload}|undefined
    Parses response; returns undefined if HEAD byte doesn't match 0xfd
  export function brightInt2Bytes(brightness_int: number) → Uint8Array
  export function brightBytes2Int(bright_byte_arr: Uint8Array) → number
  export function bytes2Time(bytes: Uint8Array) → string
  export function hex2Decimal(byte: string) → number
  export function time2Bytes(timeStamp: number) → Uint8Array(8)
  export function hex8(value: number) → string
  export function bytes2String(buffer: Uint8Array) → string
```

### js_air/manager.js — Air Manager Functions

```
Imports: Glasses, Protocol, common

export function hidSupported() → boolean
export function canCommand(device: HIDDevice) → Promise<boolean>
  Creates Glasses, connects, checks isMcu()
export async function hasActivated() → boolean
export function Asc2Hex(value: string) → string
export async function getFirmwareVersionInMcu() → string
export async function getFirmwareVersionInDp() → string
export async function getFirmwareVersionInDsp() → string
export async function isNeedUpgradeInDp() → number (payload[0])
export async function upgradeInDp() → boolean
export async function upgradeInDsp(data: ArrayBuffer) → boolean
export async function getSN() → string
export async function startIMU() → string
  Starts IMU polling + sends W_TOGGLE_IMU with [0x1]
export async function stopIMU() → string
  Sends W_TOGGLE_IMU with [0x0]
export async function getBrightness() → Uint8Array
export async function setBrightness(brightness_int: number) → Uint8Array

Internal:
  function getGlasses() → Glasses
  function reportSuccess(report) → boolean (report.status === 0)
  function sleep(delay: number) → Promise<void>
  async function sendFirmwareInMcu(bootDevice, data) → boolean
  async function sendFirmwareInDsp(glasses, data) → boolean
  function isBootDevice(device) → boolean
  async function waitBootDevice() → HIDDevice
```

### js_light/glasses.js — XREAL Light Glasses Class

```
export default class Glasses extends EventTarget {
  constructor(device: HIDDevice)
    Sets _device, _interestMsg, _reports Map, input report handler

  get device() → HIDDevice
  connect() → Promise<void>
  _handleInputReport({device, reportId, data}) → void
    Parses via Light Protocol.parse_rsp
  sendReport(msgId, payload, option) → void
    Uses Light Protocol.cmd_build with option parameter
  async sendReportTimeout(msgId, payload=[], option, timeout=3000) → report|null
  async isMcu() → boolean
  toString() → string
}
```

### js_light/protocol.js — Light Protocol

```
Constants:
  HEAD = 0x02, END = 0x03, BREAK = 0x3a
  NREAL_VENDOR_ID = 0x0486, BOOT_PRODUCT_ID = 0x573C

MESSAGES: {
  W_CANCEL_ACTIVATION: 0x65,      R_MCU_APP_FW_VERSION: 0x35,
  R_AUDIO_APP_FW_VERSION: 0x35,   R_OV580_APP_FW_VERSION: 0x35,
  R_ACTIVATION_TIME: 0x66,        W_ACTIVATION_TIME: 0x66,
  R_GLASSID: 0x43,                R_ISNEED_ACTIVATION: 0x65,
  W_MCU_SUPER_B_JUMP_TO_A: 0x38,  W_UPDATE_MCU_SUPER_A_FW_START: 0x39,
  W_MCU_SUPER_A_JUMP_TO_B: 0x52,  W_UPDATE_DP: 0x58,
  W_BOOT_UPDATE_MODE: 0x1100, etc.
}

Functions:
  export function cmd_build(msgId, payload, option) → Uint8Array(64)
    Uses STX/ETX framing, dataType based on msgId
    GET = 0x33, SET = 0x31, SUPER = 0x40
  export function parse_rsp(rsp) → {msgId, payload}
    Parses STX-framed response, extracts msgId at offset 4
  export function bytes2Time(bytes) → number
  export function hex8(value) → string
  export function bytes2String(buffer) → string
```

### js_light/protocolYmodem.js — Ymodem Firmware Upload

```
Constants:
  HEAD = 0x02, NREAL_VENDOR_ID = 0x0483, BOOT_PRODUCT_ID = 0x5740

Uses CRC16 table (not CRC32)

Functions:
  export function cmd_build(payload: Uint8Array) → Uint8Array(1029)
    Builds Ymodem frame: HEAD + PN + ~PN + payload(1024) + CRC16
  export function cmd_build_EOT() → Uint8Array(133)
    End-of-transmission packet
  export function cmd_build_SOH() → Uint8Array(133)
    Start-of-header packet
  export function bytes2Time(bytes) → number
  export function hex8(value) → string
  export function bytes2String(buffer) → string
```

### js_light/manager.js — Light Manager Functions

```
export function hidSupported() → boolean
export function canCommand(device) → Promise<boolean>
export async function hasActivated(glasses) → boolean
export async function activate(timeStamp, flag) → report
export async function deactivate() → boolean
export async function getFirmwareVersionInMcu() → string
export async function getFirmwareVersionInAudio() → string
export async function getFirmwareVersionInOv580() → string
export async function selectBinFile() → File|null
export async function getSerialPort() → SerialPort
export async function upgradeInMcuForSerial(data) → boolean
export async function upgradeInMcu(data) → boolean
export async function upgradeInDp() → boolean
export async function getSN() → string

Internal:
  function getGlasses() → Glasses
  function Asc2Hex(value) → string
  function reportSuccess(report) → boolean (payload.length === 0)
  function sleep(delay) → Promise<void>
  async function sendFirmwareInMcu(port, data) → boolean
  function progress(cur, all) → void
  async function listenSerial(reader, port) → Uint8Array
  async function waitSerialPort() → SerialPort
```

### tools/sparkline.js — SVG Sparkline Renderer

```
export function sparkline(svg, entries, options) → void
  Params: svg (SVGElement), entries (number[]|{value}[]), options ({
    onmousemove?, onmouseout?, interactive?, spotRadius?, cursorWidth?, fetch?
  })
  Renders sparkline path + fill into SVG element

export default sparkline
```

### tools/http.js — HTTP Client

```
var http = {}
  http.rquest(option: {url, method, data, timeout}, callback) → void
  http.get(url: string|{url}, callback) → void
  http.post(option, callback) → void
  baseUrl = "https://app-api.nreal.ai/api"
export default http
```

## 1.4 Usage Example

```html
<script type="module">
  import * as Common from './common.js';
  import * as Manager from './js_air/manager.js';

  // Check WebHID support
  if (!Manager.hidSupported()) {
    console.error('WebHID not supported');
  }

  // Add connection listeners
  Common.addHidListener();

  // Connect to glasses
  const glasses = await Common.connectDevice();
  console.log('Connected:', glasses.toString());

  // Read firmware version
  const version = await Manager.getFirmwareVersionInMcu();
  console.log('Firmware:', version);

  // Start IMU head tracking
  await Manager.startIMU();

  // Set brightness (1-8)
  await Manager.setBrightness(5);
</script>
```

---

# REPO 2: decky-XRGaming

**Repository:** /tmp/glasses-sdk-repos/decky-XRGaming/
**Author:** Wayne Heaney (wheaney)
**Purpose:** Decky Loader plugin for Steam Deck providing virtual display and head-tracking modes for XR glasses
**License:** GPL-3.0-or-later
**Version:** 1.5.4

## 2.1 README Summary

- Provides virtual display, VR-lite (mouse/joystick), and Follow modes for XR glasses
- Installs Breezy Desktop's Vulkan implementation
- Supported devices: XREAL, VITURE, RayNeo, TCL, Rokid
- Features: automatic recentering, SBS 3D mode, display sizing/distance, smooth follow
- Supporter Tier premium features via Ko-fi donations
- Multi-tap support (double-tap recenter, triple-tap recalibrate)

## 2.2 Architecture

```
decky-XRGaming/
├── main.py                    # Python backend (Decky plugin class)
├── decky.pyi                  # Type stubs for decky module
├── src/
│   ├── index.tsx              # Main React component (~1282 lines) — full plugin UI
│   ├── stableState.ts         # useStableState hook for debounced state
│   ├── license.ts             # License/feature management types and utilities
│   ├── tutorials.tsx          # Tutorial modal components
│   ├── showQrModal.tsx        # QR code modal utility
│   ├── SupporterTierStatus.tsx    # Supporter tier status display component
│   ├── SupporterTierModal.tsx     # Supporter tier enrollment/donation modal
│   ├── SupporterTierFeatureLabel.tsx  # Feature label with lock indicator
│   ├── QrButton.tsx           # QR code + link button component
│   └── types.d.ts             # Asset type declarations (svg, png, webp)
├── plugin.json                # Decky plugin metadata
├── package.json               # npm package config
├── rollup.config.js           # Build config
├── tsconfig.json              # TypeScript config
├── bin/                       # Shell scripts for packaging/deploying
│   ├── package
│   ├── copy_and_install
│   └── update_remote_binaries
├── assets/                    # Tutorial images and store image
└── LICENSE                    # GPL-3.0
```

**Tech Stack:**
- Backend: Python (asyncio, subprocess), Decky Loader framework
- Frontend: React + TypeScript, @decky/ui components, @decky/api
- Build: Rollup
- Dependencies: qrcode.react, react-icons, @decky/api, @decky/ui
- External: Breezy Vulkan (installed at runtime), XRLinuxDriver IPC

## 2.3 Source Files — Complete API Reference

### main.py — Python Backend Plugin

```python
import asyncio, decky, os, subprocess, sys, time
from settings import SettingsManager
from PyXRLinuxDriverIPC.xrdriveripc import XRDriverIPC

Constants:
  INSTALLED_VERSION_SETTING_KEY = "installed_from_plugin_version"
  DONT_SHOW_AGAIN_SETTING_KEY = "dont_show_again"
  MANIFEST_CHECKSUM_KEY = "manifest_checksum"
  MEASUREMENT_UNITS_SETTING_KEY = "measurement_units"
  BREEZY_INSTALL_STARTED_AT_SETTING_KEY = "breezy_install_started_at"
  BREEZY_INSTALL_TIMEOUT_SECONDS = 60

Module-level:
  settings = SettingsManager(name="settings", settings_directory=decky.DECKY_PLUGIN_SETTINGS_DIR)
  ipc = XRDriverIPC(logger, config_home, supported_output_modes=['virtual_display', 'sideview'])

class Plugin:
  def __init__(self):
    self.breezy_installed = False

  async def is_breezy_install_pending(self) → bool
    Checks if install was started and hasn't timed out

  def mark_breezy_install_started(self) → None
  def clear_breezy_install_started(self) → None

  async def retrieve_config(self) → dict|None
    Gets config from IPC + measurement_units from settings

  async def write_config(self, config: dict) → dict|None
    Writes config via IPC, stores measurement_units separately

  async def write_control_flags(self, control_flags: dict) → None
    Writes control flags via IPC (recenter, recalibrate, sbs_mode, etc.)

  async def retrieve_driver_state(self) → dict
    Gets driver state from IPC

  async def retrieve_dont_show_again_keys(self) → list[str]
  async def set_dont_show_again(self, key: str) → bool
  async def reset_dont_show_again(self) → bool

  async def is_breezy_installed_and_running(self) → bool
  async def is_driver_running(self) → bool
    Calls ipc.is_driver_running(as_user=decky.DECKY_USER)

  async def force_reset_driver(self) → bool
  async def check_breezy_installed(self) → bool
    Verifies plugin version, manifest checksum, runs breezy_vulkan_verify

  async def get_breezy_manifest_checksum(self) → str|None

  async def install_breezy(self) → bool
    Creates async task for _install_breezy

  async def _install_breezy(self) → bool
    Runs breezy_vulkan_setup script, retries 3 times
    Requests features: ["sbs", "smooth_follow"]

  async def request_token(self, email: str) → result
  async def verify_token(self, token: str) → result

  async def _main(self) → None
    Stores event loop reference

  async def _unload(self) → None
  async def _migration(self) → None

  async def _uninstall(self) → None
    Runs breezy_vulkan_uninstall and xr_driver_uninstall
```

### src/index.tsx — Main UI Component (~1282 lines)

**TypeScript Interfaces:**

```typescript
interface Config {
  disabled: boolean;
  gamescope_reshade_wayland_disabled: boolean;
  output_mode: OutputMode;  // "mouse" | "joystick" | "external_only"
  external_mode: ExternalMode[];  // 'virtual_display' | 'sideview' | 'none'
  vr_lite_invert_x: boolean;
  vr_lite_invert_y: boolean;
  opentrack_listener_enabled: boolean;
  mouse_sensitivity: number;
  look_ahead: number;
  display_size: number;
  display_distance: number;
  sbs_content: boolean;
  sbs_mode_stretched: boolean;
  sideview_position: SideviewPosition;
  virtual_display_smooth_follow_enabled: boolean;
  sideview_smooth_follow_enabled: boolean;
  sideview_follow_threshold: number;
  curved_display: boolean;
  multi_tap_enabled: boolean;
  smooth_follow_track_roll: boolean;
  smooth_follow_track_pitch: boolean;
  smooth_follow_track_yaw: boolean;
  neck_saver_horizontal_multiplier: number;
  neck_saver_vertical_multiplier: number;
  dead_zone_threshold_deg: number;
  ui_view: { headset_mode: HeadsetModeOption; is_joystick_mode: boolean; };
  measurement_units?: MeasurementUnits;
}

interface DriverState {
  heartbeat: number;
  connected_device_brand: string;
  connected_device_model: string;
  connected_device_full_distance_cm: number;
  connected_device_full_size_cm: number;
  connected_device_pose_has_position: boolean;
  calibration_setup: CalibrationSetup;
  calibration_state: CalibrationState;
  sbs_mode_enabled: boolean;
  sbs_mode_supported: boolean;
  firmware_update_recommended: boolean;
  is_gamescope_reshade_ipc_connected: boolean;
  device_license: License;
}

interface ControlFlags {
  recenter_screen: boolean;
  recalibrate: boolean;
  sbs_mode: SbsModeControl;
  refresh_device_license: boolean;
}

Type aliases:
  InstallationStatus = "checking" | "inProgress" | "installed"
  OutputMode = "mouse" | "joystick" | "external_only"
  ExternalMode = 'virtual_display' | 'sideview' | 'none'
  HeadsetModeOption = "virtual_display" | "vr_lite" | "sideview" | "disabled"
  CalibrationSetup = "AUTOMATIC" | "INTERACTIVE"
  CalibrationState = "NOT_CALIBRATED" | "CALIBRATING" | "CALIBRATED" | "WAITING_ON_USER"
  SbsModeControl = "unset" | "enable" | "disable"
  SideviewPosition = "center" | "top_left" | "top_right" | "bottom_left" | "bottom_right"
  MeasurementUnits = "cm" | "in"
```

**Utility Functions:**

```typescript
const clampValue = (value: number, min: number, max: number) → number
const sliderValueFromNotch = (min, max, notchCount, notchIndex) → number
const convertMeasurement = (valueCm: number, units: MeasurementUnits) → number
const measurementToCentimeters = (value: number, units: MeasurementUnits) → number
const formatMeasurement = (valueCm: number, units: MeasurementUnits) → string
const buildMeasurementNotchLabels = (fullValueCm, units, sliderMin, sliderMax, notchCount, notchIndices) → NotchLabel[]|undefined
```

**Content Component (VFC):**

```typescript
const Content: VFC = () => {
  // State hooks: config, isJoystickMode, driverState, dirtyControlFlags,
  //   installationStatus, showAdvanced, forceResettingDriver, error,
  //   dontShowAgainKeys, dirtyHeadsetMode/stableHeadsetMode

  // Key async functions:
  async function refreshConfig() → void
  async function retrieveDriverState() → Promise<DriverState>
  async function refreshDriverState() → void (self-scheduling every 1s)
  async function refreshDontShowAgainKeys() → void
  async function waitForPendingBreezyInstall() → boolean
  async function checkInstallation() → void
  async function writeConfig(newConfig: Config) → void
  async function writeControlFlags(flags: Partial<ControlFlags>) → void
  async function setDontShowAgain(key: string) → void
  async function resetDontShowAgain() → void
  async function requestToken(email: string) → boolean
  async function verifyToken(token: string) → boolean
  async function refreshLicense() → RefreshLicenseResponse
  async function forceResetDriver() → void
  async function updateConfig(newConfig: Config) → void

  // Renders: device status, headset mode slider, mode-specific controls,
  //   SBS mode toggle, display size/distance sliders, advanced settings,
  //   supporter tier status, help/discord links
}

export default definePlugin(() => ({
  title: "XR Gaming",
  content: <Content />,
  icon: <FaGlasses/>
}))
```

### src/stableState.ts — Debounced State Hook

```typescript
export function useStableState<T>(
  initialState: T,
  delay: number
): [T, T, Dispatch<SetStateAction<T>>]
  // Returns [dirtyState, stableState, setDirtyState]
  // stableState only updates after `delay` ms without changes to dirtyState
```

### src/license.ts — License Management

```typescript
export enum FeatureStatus { Off = "off", Trial = "trial", On = "on" }
export type FeatureTierPeriodType = "monthly" | "yearly" | "lifetime"
export type TierPeriodFundsNeeded = { [type in FeatureTierPeriodType]?: number }

export interface LicenseFeature {
  status: FeatureStatus;
  endDate?: number;
}

export interface LicenseTier {
  active: boolean;
  endDate?: number;
  period?: FeatureTierPeriodType;
  fundsNeededByPeriod?: TierPeriodFundsNeeded;
  fundsToRenew?: boolean;  // deprecated
  fundsNeededUSD?: number;  // deprecated
  lifetimeFundsNeededUSD?: number;  // deprecated
}

export interface License {
  hardwareId: string;
  confirmedToken?: boolean;
  tiers?: { [key: string]: LicenseTier };
  features?: { [key: string]: LicenseFeature };
}

export interface LicenseFeatureDetails {
  enabled: boolean;
  subtext?: string;
}

export const SupporterTierFeatureNames = ["sbs", "smooth_follow"]

export function toSec(date: number) → number
export function secondsRemaining(date: number|undefined) → number
export function featureDetails(license: License|undefined, featureName: string) → LicenseFeatureDetails
export function featureEnabled(license: License|undefined, featureName: string) → boolean
export function trialTimeRemaining(license?: License) → number|undefined
export function timeRemainingText(seconds?: number) → string|undefined
export function featureSubtext(license: License|undefined, featureName: string) → string|undefined
```

### src/tutorials.tsx — Tutorial Modal Components

```typescript
type TutorialComponentProps = { deviceBrand: string, deviceModel: string }
type TutorialComponent = React.FC<TutorialComponentProps>
type tutorial = { title: string, description?: string, component: TutorialComponent }

Components:
  GamePropertiesResolutionListItem() → JSX.Element
  SteamDisplayResolutionListItem() → JSX.Element
  SteamDisplayResolutionGamescopeSBSListItem() → JSX.Element
  VirtualDisplayTutorial() → JSX.Element
  getSBSTutorialComponent(vulkanOnlyMode: boolean) → TutorialComponent

export const tutorials: { [key: string]: tutorial }
  Keys: 'headset_mode_virtual_display_vulkan_only',
        'sbs_mode_enabled_true_vulkan_only', 'sbs_mode_enabled_true'

export function onChangeTutorial(
  tutorialKey: string,
  deviceBrand: string,
  deviceModel: string,
  onConfirm: () => void,
  dontShowAgainKeys: string[],
  setDontShowAgain: (key: string) => Promise<void>
) → void
```

### src/showQrModal.tsx

```typescript
const showQrModal = (url: string) → void
  Shows modal with QRCodeSVG (256px) and URL text
export default showQrModal
```

### src/SupporterTierStatus.tsx

```typescript
export interface SupporterTierDetails {
  licensePresent: boolean; active: boolean; confirmedToken: boolean;
  fundsNeeded?: number; lifetimeFundsNeeded?: number;
  lifetimeAccess: boolean; timeRemainingText?: string;
  trialTimeRemaining?: number; trialTimeRemainingText?: string;
}

export function supporterTierDetails(license?: License) → SupporterTierDetails
export function useShowSupporterTierDetails() → Function
  React hook that returns function to show SupporterTierModal
export function SupporterTierStatus({details, requestTokenFn, verifyTokenFn, refreshLicenseFn}: Props) → JSX.Element
```

### src/SupporterTierModal.tsx

```typescript
enum SupporterTierView {
  NoLicense, Enroll, Renew, Donate, VerifyToken, RequestToken, Done
}

export interface RefreshLicenseResponse {
  licensePresent: boolean; confirmedToken?: boolean;
  timeRemainingText?: string; fundsNeeded?: number;
  lifetimeFundsNeeded?: number; isRenewed: boolean;
}

Components:
  SupporterTierFeaturesList() → JSX.Element
  SupporterTierAboutRenewBlurb(props) → JSX.Element
  SupporterTierAboutEnrollBlurb(props) → JSX.Element
  SupporterTierNoLicense(props: SupporterTierStepProps) → JSX.Element
  SupporterTierAbout(props: SupporterTierAboutProps) → JSX.Element
  SupporterTierEnroll(props) → JSX.Element
  SupporterTierRenew(props) → JSX.Element
  SupporterTierDonate(props) → JSX.Element (DonationURL = 'https://ko-fi.com/wheaney')
  SupporterTierVerifyToken(props) → JSX.Element
  SupporterTierRequestToken(props) → JSX.Element

export function SupporterTierModal(props: SupporterTierModalProps) → JSX.Element
  State machine for enrollment/donation/token verification flow
```

### src/SupporterTierFeatureLabel.tsx

```typescript
export interface Props { label: string; feature: LicenseFeatureDetails; }
export function SupporterTierFeatureLabel({label, feature}: Props) → JSX.Element
  Renders label with optional lock icon and subtext
```

### src/QrButton.tsx

```typescript
const QrButton: FC<{ icon: ReactNode; url: string; followLink?: boolean; children: ReactNode }>
  Renders PanelSectionRow with text and button that either navigates to URL or shows QR modal
export default QrButton
```

## 2.4 Usage

1. Install Decky Loader on Steam Deck
2. Install "XR Gaming" from Decky store
3. Plug in supported XR glasses
4. Use sidebar controls to select mode (Virtual Display, VR-Lite, Follow, Disabled)
5. Adjust settings per mode (display size, distance, sensitivity, SBS, etc.)

---

# REPO 3: open-wearables

**Repository:** /tmp/glasses-sdk-repos/open-wearables/
**Author:** the-momentum
**Purpose:** Open-source health/wearable data aggregation platform with MCP server for AI assistants
**License:** MIT

## 3.1 Overview

Open Wearables is a full-stack platform:
- **Backend:** Python 3.13+, FastAPI, SQLAlchemy 2.0, PostgreSQL, Celery + Redis
- **Frontend:** React 19, TypeScript, TanStack Router/Query, Tailwind + shadcn/ui
- **MCP Server:** Python 3.13+, FastMCP, httpx (REST API client)
- **Docs:** Mintlify documentation site

Supported wearable providers: Garmin, Whoop, Polar, Suunto, Fitbit, Strava, Ultrahuman, Apple Health

**NOTE:** For this analysis, we focus on the **MCP server** component as the most relevant
to XR/glasses SDK integration (the backend and frontend are a large full-stack web app).

## 3.2 MCP Server Architecture

```
mcp/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastMCP server entry point, mounts all routers
│   ├── config.py          # Pydantic settings (API URL, API key, log level)
│   ├── utils.py           # normalize_datetime utility
│   ├── prompts.py         # present_health_data prompt
│   ├── services/
│   │   ├── __init__.py
│   │   └── api_client.py  # OpenWearablesClient — async HTTP client
│   └── tools/
│       ├── __init__.py
│       ├── users.py       # get_users tool
│       ├── activity.py    # get_activity_summary tool
│       ├── sleep.py       # get_sleep_summary tool
│       ├── workouts.py    # get_workout_events tool
│       └── timeseries.py  # get_timeseries tool
├── config/
│   └── .env.example
├── pyproject.toml
├── .python-version
├── uv.lock
└── README.md
```

**Dependencies (pyproject.toml):**
- fastmcp >= 2.0.0
- httpx >= 0.27.0
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0
- Python >= 3.13

**Entry Point:** `uv run start` → `app.main:main()`

## 3.3 Complete API Reference

### app/config.py — Settings

```python
class Settings(BaseSettings):
    """MCP server configuration loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file="config/.env", env_file_encoding="utf-8", extra="ignore"
    )
    open_wearables_api_url: str = "http://localhost:8000"
    open_wearables_api_key: SecretStr = SecretStr("")
    log_level: str = "INFO"
    request_timeout: int = 30

    def is_configured(self) → bool:
        """Check if the API key is configured."""

settings = Settings()  # Module-level singleton
```

### app/main.py — FastMCP Server

```python
mcp = FastMCP("open-wearables", instructions="...")
  # Mounts: users_router, activity_router, sleep_router, workouts_router,
  #         timeseries_router, prompts_router

def main() → None:
    """Entry point for the MCP server."""
    mcp.run()
```

### app/services/api_client.py — HTTP Client

```python
class OpenWearablesClient:
    """Client for interacting with Open Wearables REST API."""

    def __init__(self) → None:
        self.base_url: str
        self.timeout: int
        self._api_key: str

    def _ensure_configured(self) → None:
        """Raise ValueError if API key not configured."""

    @property
    def headers(self) → dict[str, str]:
        """Returns {'X-Open-Wearables-API-Key': key, 'Content-Type': 'application/json'}"""

    async def _request(self, method: str, path: str, **kwargs) → dict[str, Any]:
        """Make HTTP request. Handles 401, 404 errors."""

    async def get_users(self, search: str|None = None, limit: int = 100) → dict[str, Any]:
        """GET /api/v1/users — List users"""

    async def get_user(self, user_id: str) → dict[str, Any]:
        """GET /api/v1/users/{user_id} — Get specific user"""

    async def get_sleep_summaries(self, user_id: str, start_date: str, end_date: str, limit: int = 100) → dict[str, Any]:
        """GET /api/v1/users/{user_id}/summaries/sleep"""

    async def get_workouts(self, user_id: str, start_date: str, end_date: str, record_type: str|None = None, limit: int = 100) → dict[str, Any]:
        """GET /api/v1/users/{user_id}/events/workouts"""

    async def get_activity_summaries(self, user_id: str, start_date: str, end_date: str, limit: int = 100) → dict[str, Any]:
        """GET /api/v1/users/{user_id}/summaries/activity"""

    async def get_timeseries(self, user_id: str, start_time: str, end_time: str, types: list[str], resolution: str = "raw", limit: int = 100, cursor: str|None = None) → dict[str, Any]:
        """GET /api/v1/users/{user_id}/timeseries"""

client = OpenWearablesClient()  # Singleton
```

### app/tools/users.py

```python
users_router = FastMCP(name="Users Tools")

@users_router.tool
async def get_users(search: str|None = None, limit: int = 10) → dict:
    """Get users accessible via the configured API key.
    Args:
        search: Filter by first name, last name, or email
        limit: Max users to return (default: 10)
    Returns:
        {"users": [{id, first_name, last_name, email}], "total": int}
    """
```

### app/tools/activity.py

```python
activity_router = FastMCP(name="Activity Tools")

@activity_router.tool
async def get_activity_summary(user_id: str, start_date: str, end_date: str) → dict:
    """Get daily activity summaries.
    Returns: {user, period, records: [{date, steps, distance_meters,
      active_calories_kcal, total_calories_kcal, active_minutes,
      heart_rate, intensity_minutes, floors_climbed, source}],
      summary: {total_days, days_with_data, total_steps, avg_steps, ...}}
    """
```

### app/tools/sleep.py

```python
sleep_router = FastMCP(name="Sleep Tools")

@sleep_router.tool
async def get_sleep_summary(user_id: str, start_date: str, end_date: str) → dict:
    """Get daily sleep summaries.
    Returns: {user, period, records: [{date, start_datetime, end_datetime,
      duration_minutes, source}],
      summary: {total_nights, nights_with_data, avg/min/max_duration_minutes}}
    """
```

### app/tools/workouts.py

```python
workouts_router = FastMCP(name="Workout Tools")

@workouts_router.tool
async def get_workout_events(user_id: str, start_date: str, end_date: str, workout_type: str|None = None) → dict:
    """Get workout events.
    Returns: {user, period, records: [{id, type, start_datetime, end_datetime,
      duration_seconds, distance_meters, calories_kcal, avg/max_heart_rate_bpm,
      avg_pace_sec_per_km, elevation_gain_meters, source}],
      summary: {total_workouts, total_duration_seconds, total_distance_meters,
      total_calories_kcal, workout_types}}
    """
```

### app/tools/timeseries.py

```python
timeseries_router = FastMCP(name="Timeseries Tools")
_MAX_PAGES = 100  # Safety ceiling: 100 pages * 100 samples = 10k max

@timeseries_router.tool
async def get_timeseries(user_id: str, start_time: str, end_time: str, types: list[str], resolution: str = "raw") → dict:
    """Get granular time-series samples.
    types: heart_rate, resting_heart_rate, heart_rate_variability_sdnn/rmssd,
           oxygen_saturation, respiratory_rate, blood_glucose,
           blood_pressure_systolic/diastolic, weight, body_fat_percentage,
           body_mass_index, steps, active_energy, basal_energy, distance
    resolution: "raw", "1min", "5min", "15min", "1hour"
    Returns: {user, period, records: [{timestamp, type, value, unit, source}],
      summary: {total_samples, by_type: {count, avg, min, max}}, truncated}
    Auto-paginates up to _MAX_PAGES.
    """
```

### app/prompts.py

```python
prompts_router = FastMCP(name="Health Data Prompts")

@prompts_router.prompt
def present_health_data() → list[PromptMessage]:
    """Guidelines for presenting health data:
    - Steps: readable format
    - Distance: meters to km
    - Calories: whole numbers
    - Duration: hours/minutes if >= 60
    - Heart rate: always include "bpm"
    - Lead with insights, highlight patterns
    """
```

### app/utils.py

```python
def normalize_datetime(dt_str: str|None) → str|None:
    """Normalize datetime string to ISO 8601 format.
    Replaces 'Z' with '+00:00', returns isoformat()."""
```

## 3.4 Usage

```bash
# Install
cd mcp && uv sync

# Configure
cp config/.env.example config/.env
# Edit config/.env: OPEN_WEARABLES_API_URL, OPEN_WEARABLES_API_KEY

# Run
uv run start

# Claude Desktop config:
{
  "mcpServers": {
    "open-wearables": {
      "command": "uv",
      "args": ["run", "--frozen", "--directory", "/path/to/mcp", "start"]
    }
  }
}
```

---

# CROSS-REPO ANALYSIS

## Relevance to Smart Glasses SDK

| Repo | Relevance | Key Takeaways |
|------|-----------|---------------|
| xreal-webxr | **HIGH** — Direct XREAL glasses HID protocol | Wire protocol for Air (0xfd framing, CRC32) and Light (STX/ETX framing). IMU data structure (Device3Packet). Product IDs, vendor IDs. WebHID connection patterns. |
| decky-XRGaming | **HIGH** — Display/tracking modes for XR glasses on Linux | Config schema for virtual display, VR-lite, follow modes. XRDriverIPC interface. Breezy Vulkan integration. Calibration states, SBS mode. Multi-brand support (XREAL, VITURE, RayNeo, TCL, Rokid). |
| open-wearables | **MEDIUM** — Health data platform, MCP server pattern | MCP server architecture pattern (FastMCP + routers). Health data aggregation from wearables. Not directly glasses-related but shows unified wearable data model. |

## Key Protocol Details (xreal-webxr)

**XREAL Air HID Protocol:**
- 64-byte packets, HEAD=0xfd
- CRC32 checksum
- msgId at offset 15 (2 bytes, little-endian)
- Payload at offset 22
- Status byte at offset 22

**XREAL Light HID Protocol:**
- Variable-length packets, HEAD=0x02, END=0x03, separator=0x3a
- CRC32 checksum (different encoding — hex ASCII)
- DataType: GET=0x33, SET=0x31, SUPER=0x40
- Firmware upload via Ymodem (CRC16, 1024-byte blocks)

**Device Identification:**
- Air: vendorId=0x3318, productIds=0x0423/0x0424
- Light: vendorId=0x0486, productIds=0x573C/0x5740
- Light Boot: vendorId=0x0483, productId=0x5740

## Key Config Schema (decky-XRGaming)

The Config interface defines the complete XR display configuration:
- Headset modes: virtual_display, vr_lite, sideview, disabled
- Display: size (0.1-2.5), distance (0.1-2.5), curved_display
- VR-Lite: mouse_sensitivity (5-100), joystick mode, invert X/Y
- Follow: sideview_position, smooth_follow, follow_threshold
- SBS: sbs_content, sbs_mode_stretched
- Advanced: look_ahead (0-45), neck_saver multipliers, dead_zone_threshold_deg, multi_tap, opentrack

---

*END OF DEEP READ — All source files have been read and documented exhaustively.*
