# AR Glasses Master SDK — Complete API Reference

> **Comprehensive API reference covering every function, class, and method across 27+ repositories.**
> Generated: 2026-04-20 | 500+ functions documented | 12 domains | 27 repos analyzed

---

## Table of Contents

1. [Display & Rendering](#1-display--rendering)
2. [IMU & Head Tracking (Sensor Fusion)](#2-imu--head-tracking-sensor-fusion)
3. [Camera & Computer Vision](#3-camera--computer-vision)
4. [Audio & Speech](#4-audio--speech)
5. [BLE & Wireless Communication](#5-ble--wireless-communication)
6. [Gesture & Input](#6-gesture--input)
7. [Spatial Computing (SLAM, Anchors, OpenXR)](#7-spatial-computing-slam-anchors-openxr)
8. [ML/AI On-Device](#8-mlai-on-device)
9. [GPS & Geolocation](#9-gps--geolocation)
10. [Device Management & Connectivity](#10-device-management--connectivity)
11. [3D Environment (StardustXR)](#11-3d-environment-stardustxr)
12. [Geo/Maps Intelligence (Overpass, Gemini)](#12-geomaps-intelligence-overpass-gemini)

---

# 1. Display & Rendering

## 1.1 Universal Display API (xg-glass-sdk)

### `GlassesClient.display(text: String, options: DisplayOptions) -> Result<Unit>`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/GlassesClient.kt | **Language:** Kotlin

Display text on the connected AR glasses. Abstracts vendor-specific display APIs behind a unified interface.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| text | String | The text content to display on glasses |
| options | DisplayOptions | Display mode and force options (default: REPLACE, force=false) |

**Returns:** `Result<Unit>` — Success or failure with GlassesError

**Example:**
```kotlin
val client: GlassesClient = RokidGlassesClient(activity)
client.connect()
client.display("Hello World", DisplayOptions(mode = DisplayMode.REPLACE))
client.display("More text", DisplayOptions(mode = DisplayMode.APPEND))
```

**Notes:** 
- Rokid: Uses CxrApi openCustomView/updateCustomView with JSON layout, throttled at 350ms minimum interval
- Frame: Sends via BLE to Lua `frame.display.text()` on device
- Meta: UNSUPPORTED — returns `GlassesError.Unsupported`
- Omi: UNSUPPORTED
- Simulator: Launches `SimDisplayActivity` with text content

---

### `data class DisplayOptions`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/Models.kt | **Language:** Kotlin

Configuration for text display behavior.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| mode | DisplayMode | REPLACE (overwrite) or APPEND (add to existing) |
| force | Boolean | Bypass throttling/deduplication (default: false) |

---

### `enum class DisplayMode`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/Models.kt | **Language:** Kotlin

- `REPLACE` — Replace current display content entirely
- `APPEND` — Append to existing display content

---

### `RokidDisplayController.showText(text: String, force: Boolean)`
**Repo:** xg-glass-sdk | **File:** devices/device-rokid/RokidDisplayController.kt | **Language:** Kotlin

Internal display controller for Rokid glasses with throttling.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| text | String | Text to display |
| force | Boolean | Bypass 350ms throttle interval |

**Notes:** Uses CxrApi `openCustomView()` for first display, `updateCustomView()` for updates. Tracks `lastText` to skip duplicate renders.

---

### `RokidDisplayController.close()`
**Repo:** xg-glass-sdk | **File:** devices/device-rokid/RokidDisplayController.kt | **Language:** Kotlin

Closes the custom view on Rokid glasses. Calls `CxrApi.closeCustomView()`.

---

## 1.2 MentraOS Display API

### `LayoutManager.showTextWall(text: String): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Display full-screen text on MentraOS-compatible glasses.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| text | String | Text to display as a full-screen wall |

**Example:**
```typescript
session.display.showTextWall("Hello from MentraOS!");
```

---

### `LayoutManager.showDoubleTextWall(topText: String, bottomText: String): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Display split-screen text with top and bottom sections.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| topText | String | Text for the top section |
| bottomText | String | Text for the bottom section |

---

### `LayoutManager.showDashboardCard(title: String, content: String): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Display a dashboard-style card with title and content.

---

### `LayoutManager.showReferenceCard(title: String, body: String): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Display a reference card layout.

---

### `LayoutManager.showBitmapView(data: String, width?: number, height?: number): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Display a bitmap image on the glasses.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| data | String | Base64-encoded image data |
| width | number? | Optional width |
| height | number? | Optional height |

---

### `LayoutManager.clear(): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Clear all displayed content from the glasses.

---

## 1.3 Brilliant Labs Frame Display (Lua API)

### `frame.display.text(text, x, y, options)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Render text on the Frame's micro-OLED display.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| text | string | Text to render |
| x | number | X position in pixels |
| y | number | Y position in pixels |
| options | table | Font, color index, alignment options |

---

### `frame.display.bitmap(x, y, width, data)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Draw a bitmap image on the Frame display.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| x | number | X position |
| y | number | Y position |
| width | number | Bitmap width in pixels |
| data | string | Raw pixel data |

---

### `frame.display.show()`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Commit the current display buffer to the screen. Must be called after `text()` or `bitmap()` to make changes visible.

---

### `frame.display.assign_color(index, r, g, b)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Assign an RGB color to a palette index for use in text/bitmap rendering.

---

### `frame.display.assign_color_ycbcr(index, y, cb, cr)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Assign a YCbCr color to a palette index.

---

### `frame.display.set_brightness(level)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Set the display brightness level.

---

### `frame.display.power_save(enable)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Enable or disable display power saving mode.

---

### `frame.display.write_register(addr, value)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Write directly to a display controller register (advanced/debug).

---

## 1.4 Vuzix Blade 2 HUD Display

### `ActionMenuActivity.onCreateActionMenu(Menu menu) -> boolean`
**Repo:** Blade_2_Template_App | **File:** app/src/main/java/.../center_content_template_activity.java | **Language:** Java

Create the HUD action menu. Override to inflate your menu resource.

**Example:**
```java
@Override
protected boolean onCreateActionMenu(Menu menu) {
    getMenuInflater().inflate(R.menu.main_menu, menu);
    return true;
}
```

---

### `ActionMenuActivity.getActionMenuGravity() -> int`
**Repo:** Blade_2_Template_App | **File:** app/src/main/java/.../around_content_template_activity.java | **Language:** Java

Set menu position. Returns `Gravity.RIGHT` for side menu or `Gravity.CENTER` for center menu.

---

### `ActionMenuActivity.alwaysShowActionMenu() -> boolean`
**Repo:** Blade_2_Template_App | **File:** app/src/main/java/.../center_content_template_activity.java | **Language:** Java

Whether the action menu is always visible on the HUD. Return `true` for persistent menu.

---

## 1.5 Everysight Maverick Display

### `Text().setText(text).setResource(font).setTextAlign(align).setXY(x, y).setForegroundColor(color).addTo(screen)`
**Repo:** everysight-sdk | **File:** (SDK binary) | **Language:** Kotlin

Fluent builder API for rendering text on Everysight Maverick glasses.

**Example:**
```kotlin
class HelloScreen : Screen() {
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

## 1.6 DualWebViewGroup — Binocular Browser Rendering (TAPLINKX3)

### `class DualWebViewGroup(context: Context, attrs: AttributeSet?, defStyleAttr: Int) : ViewGroup`
**Repo:** TAPLINKX3 | **File:** app/src/main/java/com/TapLink/app/DualWebViewGroup.kt | **Language:** Kotlin

Core binocular rendering engine. Duplicates WebView content for stereo AR display (1280x480, 640x480 per eye). Uses PixelCopy for right eye mirroring.

**Key Features:**
- Multi-window tab management with `BrowserWindow` data class
- Refresh at 16ms (~60fps) normal, 100ms in idle mode
- Idle detection after 5 seconds → drops to ~10fps
- UI scale: 0.5-1.0 with pivot at (320, 240)

**Interfaces:**
```kotlin
interface DualWebViewGroupListener {
    fun onCursorPositionChanged(x: Float, y: Float, isVisible: Boolean)
}
interface MaskToggleListener { fun onMaskTogglePressed() }
interface AnchorToggleListener { fun onAnchorTogglePressed() }
interface FullscreenListener { fun onEnterFullscreen(); fun onExitFullscreen() }
interface KeyboardListener { fun onShowKeyboard(); fun onHideKeyboard() }
interface WindowCallback { fun onWindowCreated(webView: WebView); fun onWindowSwitched(webView: WebView) }
```

---

## 1.7 RayDesk — Spatial Desktop Rendering

### `class StreamRenderer`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/gl/StreamRenderer.kt | **Language:** Kotlin

Main OpenGL renderer supporting multiple display modes: flat quad, curved cylinder, and keyhole viewport.

---

### `class CylinderController`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/spatial/CylinderController.kt | **Language:** Kotlin

Curved virtual monitor projection controller.

**Methods:**
| Method | Description |
|--------|-------------|
| `zoomIn()` / `zoomOut()` / `resetZoom()` | Zoom controls |
| `setRadius(radius: Float, immediate: Boolean)` | Set cylinder radius |
| `updateHeadPose(yaw: Float, pitch: Float, deltaTime: Float)` | Update from IMU |
| `recenter(currentYaw: Float, currentPitch: Float)` | Recenter view |
| `getViewMatrix() -> FloatArray` | Get view matrix |
| `getMVPMatrix() -> FloatArray` | Get model-view-projection matrix |
| `getLeftEyeMVPMatrix() -> FloatArray` | Left eye MVP |
| `getRightEyeMVPMatrix() -> FloatArray` | Right eye MVP |

---

### `class CylinderMesh`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/gl/CylinderMesh.kt | **Language:** Kotlin

Generates curved screen geometry for the virtual monitor.

---

### `class FlatQuadMesh`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/gl/FlatQuadMesh.kt | **Language:** Kotlin

Generates flat rectangular geometry for 2D display mode.

---

### `class SkyboxRenderer`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/gl/environment/SkyboxRenderer.kt | **Language:** Kotlin

Procedural skybox renderer for the virtual environment.

---

### `class EnvironmentRenderer`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/gl/environment/EnvironmentRenderer.kt | **Language:** Kotlin

Composite renderer combining skybox, status ring, dashboard, and physical frame elements.

---

## 1.8 RayNeo Unity Display

### `class DualeyeDiffrentDisplay : MonoBehaviour`
**Repo:** rayneo-setup | **File:** Assets/Samples/.../DualeyeDiffrentDisplay.unity | **Language:** C# (Unity)

Per-eye rendering for RayNeo X2 glasses, allowing different content on left and right eyes.

---

### `class SetCanvasOverlay : MonoBehaviour`
**Repo:** rayneo-setup | **File:** Assets/.../Tool/SetCanvasOverlay.cs | **Language:** C# (Unity)

Setup UI canvas as overlay on AR view for HUD elements.

---

# 2. IMU & Head Tracking (Sensor Fusion)

## 2.1 Fusion Library (imufusion) — AHRS Algorithm

### `void FusionAhrsInitialise(FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Initialize the AHRS (Attitude and Heading Reference System) structure with default settings. Resets quaternion to identity and enables startup mode.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | Pointer to AHRS structure to initialize |

**Example:**
```c
FusionAhrs ahrs;
FusionAhrsInitialise(&ahrs);
```

---

### `void FusionAhrsSetSettings(FusionAhrs *ahrs, const FusionAhrsSettings *settings)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Configure the AHRS algorithm parameters. Converts rejection thresholds to internal representation.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | AHRS structure |
| settings | const FusionAhrsSettings* | Settings: convention, gain, gyroscopeRange, accelerationRejection, magneticRejection, recoveryTriggerPeriod |

**Example:**
```c
FusionAhrsSettings settings = {
    .convention = FusionConventionNwu,
    .gain = 0.5f,
    .gyroscopeRange = 2000.0f,
    .accelerationRejection = 10.0f,
    .magneticRejection = 10.0f,
    .recoveryTriggerPeriod = 5 * SAMPLE_RATE,
};
FusionAhrsSetSettings(&ahrs, &settings);
```

---

### `void FusionAhrsUpdate(FusionAhrs *ahrs, FusionVector gyroscope, FusionVector accelerometer, FusionVector magnetometer, float deltaTime)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.c | **Language:** C

Core AHRS update with all three sensor inputs. Implements the revised Madgwick algorithm with acceleration/magnetic rejection and angular rate recovery.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | AHRS structure |
| gyroscope | FusionVector | Gyroscope data in degrees per second |
| accelerometer | FusionVector | Accelerometer data in g |
| magnetometer | FusionVector | Magnetometer data in any calibrated units |
| deltaTime | float | Time since last update in seconds |

**Example:**
```c
FusionVector gyro = {.axis = {0.1f, 0.2f, -0.1f}};
FusionVector accel = {.axis = {0.0f, 0.0f, 1.0f}};
FusionVector mag = {.axis = {20.0f, 0.0f, 40.0f}};
FusionAhrsUpdate(&ahrs, gyro, accel, mag, 1.0f / SAMPLE_RATE);
```

---

### `void FusionAhrsUpdateNoMagnetometer(FusionAhrs *ahrs, FusionVector gyroscope, FusionVector accelerometer, float deltaTime)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.c | **Language:** C

AHRS update without magnetometer. Calls `FusionAhrsUpdate` with zero magnetometer vector. Heading is zeroed during startup phase.

---

### `void FusionAhrsUpdateExternalHeading(FusionAhrs *ahrs, FusionVector gyroscope, FusionVector accelerometer, float heading, float deltaTime)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.c | **Language:** C

AHRS update using external heading (e.g., GPS compass) instead of magnetometer. Constructs equivalent magnetometer vector from heading and current roll.

---

### `FusionQuaternion FusionAhrsGetQuaternion(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns the current orientation quaternion describing sensor orientation relative to Earth.

**Returns:** `FusionQuaternion` — {w, x, y, z} quaternion

---

### `void FusionAhrsSetQuaternion(FusionAhrs *ahrs, FusionQuaternion quaternion)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Set the orientation quaternion directly.

---

### `FusionVector FusionAhrsGetGravity(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns direction of gravity in sensor frame as a unit vector.

---

### `FusionVector FusionAhrsGetLinearAcceleration(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns linear acceleration (accelerometer with gravity removed) in sensor frame, in g units.

---

### `FusionVector FusionAhrsGetEarthAcceleration(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns acceleration in Earth frame with gravity removed. Rotates accelerometer to Earth frame then subtracts gravity vector.

---

### `FusionAhrsInternalStates FusionAhrsGetInternalStates(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns internal algorithm states for debugging: accelerationError, accelerometerIgnored, magneticError, magnetometerIgnored, recovery triggers.

---

### `FusionAhrsFlags FusionAhrsGetFlags(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns algorithm flags: startup, angularRateRecovery, accelerationRecovery, magneticRecovery.

---

### `void FusionAhrsSetHeading(FusionAhrs *ahrs, float heading)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.c | **Language:** C

Sets the heading (yaw) of the current orientation by applying a Z-axis rotation.

---

### `void FusionAhrsRestart(FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Restarts the AHRS algorithm. Resets quaternion to identity and enables startup gain ramping.

---

## 2.2 Fusion Math Operations

### `float FusionDegreesToRadians(float degrees)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Converts degrees to radians. Returns `degrees * (PI / 180)`.

---

### `float FusionRadiansToDegrees(float radians)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Converts radians to degrees. Returns `radians * (180 / PI)`.

---

### `float FusionArcSin(float value)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Clamped arc sine. Clamps input to [-1, 1] before computing asin to avoid NaN results.

---

### `float FusionFastInverseSqrt(float x)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Fast inverse square root using Pizer's implementation. Returns `1/sqrt(x)`. Disabled if `FUSION_USE_NORMAL_SQRT` is defined.

---

### `FusionVector FusionVectorAdd(FusionVector a, FusionVector b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Element-wise vector addition. Returns `{a.x+b.x, a.y+b.y, a.z+b.z}`.

---

### `FusionVector FusionVectorSubtract(FusionVector a, FusionVector b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Element-wise vector subtraction.

---

### `FusionVector FusionVectorScale(FusionVector v, float s)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Scalar multiplication of vector.

---

### `FusionVector FusionVectorCross(FusionVector a, FusionVector b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Cross product a × b.

---

### `float FusionVectorDot(FusionVector a, FusionVector b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Dot product a · b.

---

### `float FusionVectorNorm(FusionVector v)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Returns magnitude |v|.

---

### `FusionVector FusionVectorNormalise(FusionVector v)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Returns unit vector v/|v|. Uses fast inverse sqrt for performance on embedded systems.

---

### `FusionQuaternion FusionQuaternionProduct(FusionQuaternion a, FusionQuaternion b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Hamilton quaternion product a * b.

---

### `FusionQuaternion FusionQuaternionNormalise(FusionQuaternion q)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Returns unit quaternion q/|q|.

---

### `FusionMatrix FusionQuaternionToMatrix(FusionQuaternion q)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Converts quaternion to 3x3 rotation matrix (transpose of Kuipers convention).

---

### `FusionEuler FusionQuaternionToEuler(FusionQuaternion q)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Converts quaternion to ZYX Euler angles in degrees (roll, pitch, yaw).

---

### `FusionVector FusionMatrixMultiply(FusionMatrix m, FusionVector v)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Matrix-vector multiplication M * v.

---

## 2.3 Fusion Bias Estimation

### `void FusionBiasInitialise(FusionBias *bias)`
**Repo:** Fusion | **File:** Fusion/FusionBias.h | **Language:** C

Initialize gyroscope bias estimation structure with default settings (100Hz, 3.0°/s threshold, 3.0s period).

---

### `void FusionBiasSetSettings(FusionBias *bias, const FusionBiasSettings *settings)`
**Repo:** Fusion | **File:** Fusion/FusionBias.h | **Language:** C

Configure bias estimation: sampleRate, stationaryThreshold, stationaryPeriod.

---

### `FusionVector FusionBiasUpdate(FusionBias *bias, FusionVector gyroscope)`
**Repo:** Fusion | **File:** Fusion/FusionBias.c | **Language:** C

Update bias estimation and return offset-corrected gyroscope. Must be called every sample. Detects stationary periods automatically.

**Returns:** `FusionVector` — Offset-corrected gyroscope in degrees per second

---

### `FusionVector FusionBiasGetOffset(const FusionBias *bias)`
**Repo:** Fusion | **File:** Fusion/FusionBias.h | **Language:** C

Returns the current estimated gyroscope bias offset.

---

## 2.4 Fusion Compass & Calibration

### `float FusionCompass(FusionVector accelerometer, FusionVector magnetometer, FusionConvention convention)`
**Repo:** Fusion | **File:** Fusion/FusionCompass.h | **Language:** C

Calculates tilt-compensated magnetic heading using accelerometer for tilt and magnetometer for heading.

**Returns:** `float` — Magnetic heading in degrees

---

### `FusionVector FusionModelInertial(FusionVector uncalibrated, FusionMatrix misalignment, FusionVector sensitivity, FusionVector offset)`
**Repo:** Fusion | **File:** Fusion/FusionModel.h | **Language:** C

Apply inertial sensor calibration: `M * s * (raw - offset)`.

---

### `FusionVector FusionModelMagnetic(FusionVector uncalibrated, FusionMatrix softIronMatrix, FusionVector hardIronOffset)`
**Repo:** Fusion | **File:** Fusion/FusionModel.h | **Language:** C

Apply magnetometer calibration: `S * (raw - h)`.

---

### `FusionVector FusionRemap(FusionVector sensor, FusionRemapAlignment alignment)`
**Repo:** Fusion | **File:** Fusion/FusionRemap.h | **Language:** C

Remap sensor axes using one of 24 orthogonal permutations. Use when sensor is mounted in non-standard orientation.

---

## 2.5 Fusion Python API

### `imufusion.Ahrs()`
**Repo:** Fusion | **File:** Python bindings | **Language:** Python

Create an AHRS instance (Python wrapper).

**Example:**
```python
import imufusion
ahrs = imufusion.Ahrs()
ahrs.settings = imufusion.Settings(
    imufusion.CONVENTION_NWU, gain=0.5, gyroscope_range=2000,
    acceleration_rejection=10, magnetic_rejection=10,
    recovery_trigger_period=5 * sample_rate,
)
for gyro, accel, mag, dt in sensor_data:
    ahrs.update(gyro, accel, mag, dt)
    euler = ahrs.quaternion.to_euler()
```

---

## 2.6 XRLinuxDriver IMU Types & Functions

### `struct imu_euler_t { float roll, pitch, yaw; }`
**Repo:** XRLinuxDriver | **File:** include/imu.h | **Language:** C

Euler angle representation for head orientation.

---

### `struct imu_quat_t { float x, y, z, w; }`
**Repo:** XRLinuxDriver | **File:** include/imu.h | **Language:** C

Quaternion orientation representation.

---

### `struct imu_pose_t`
**Repo:** XRLinuxDriver | **File:** include/imu.h | **Language:** C

Complete 6DoF pose: orientation (quaternion + euler), position (vec3), validity flags, timestamp.

---

### `imu_quat_type normalize_quaternion(imu_quat_type q)`
**Repo:** XRLinuxDriver | **File:** src/imu.c | **Language:** C

Normalize a quaternion to unit length.

---

### `imu_quat_type multiply_quaternions(imu_quat_type q1, imu_quat_type q2)`
**Repo:** XRLinuxDriver | **File:** src/imu.c | **Language:** C

Hamilton product of two quaternions.

---

### `imu_quat_type euler_to_quaternion_xyz(imu_euler_type euler)`
**Repo:** XRLinuxDriver | **File:** src/imu.c | **Language:** C

Convert Euler angles (XYZ order) to quaternion.

---

### `imu_euler_type quaternion_to_euler_zyx(imu_quat_type q)`
**Repo:** XRLinuxDriver | **File:** src/imu.c | **Language:** C

Convert quaternion to Euler angles (ZYX order).

---

### `imu_vec3_type vector_rotate(imu_vec3_type v, imu_quat_type q)`
**Repo:** XRLinuxDriver | **File:** src/imu.c | **Language:** C

Rotate a 3D vector by a quaternion.

---

### `float quat_small_angle_rad(imu_quat_type q1, imu_quat_type q2)`
**Repo:** XRLinuxDriver | **File:** src/imu.c | **Language:** C

Compute the small angle between two quaternions in radians.

---

## 2.7 XRLinuxDriver Buffer System

### `buffer_type *create_buffer(int size)`
**Repo:** XRLinuxDriver | **File:** include/buffer.h | **Language:** C

Create a ring buffer for smoothing IMU data.

---

### `float push(buffer_type *buffer, float next_value)`
**Repo:** XRLinuxDriver | **File:** src/buffer.c | **Language:** C

Push a value into the ring buffer and return the rolling average.

---

### `imu_buffer_type *create_imu_buffer(int buffer_size)`
**Repo:** XRLinuxDriver | **File:** include/buffer.h | **Language:** C

Create a quaternion-aware IMU ring buffer with timestamp tracking.

---

### `imu_buffer_response_type *push_to_imu_buffer(imu_buffer_type *buf, imu_quat_type quat, float timestamp_ms)`
**Repo:** XRLinuxDriver | **File:** src/buffer.c | **Language:** C

Push a quaternion sample into the IMU buffer. Returns smoothed quaternion and look-ahead prediction.

---

## 2.8 PhoenixHeadTracker (C# / Windows)

### `int StartConnection()`
**Repo:** PhoenixHeadTracker | **File:** (AirAPI_Windows.dll P/Invoke) | **Language:** C#

Connect to XREAL Air glasses. Returns 1 on success.

```csharp
[DllImport("AirAPI_Windows", CallingConvention = CallingConvention.Cdecl)]
public static extern int StartConnection();
```

---

### `int StopConnection()`
**Repo:** PhoenixHeadTracker | **File:** (AirAPI_Windows.dll P/Invoke) | **Language:** C#

Disconnect from XREAL Air glasses.

---

### `IntPtr GetEuler()`
**Repo:** PhoenixHeadTracker | **File:** (AirAPI_Windows.dll P/Invoke) | **Language:** C#

Read Euler angles from glasses. Returns pointer to float[3]: [roll, pitch, yaw].

---

### `class KalmanFilter`
**Repo:** PhoenixHeadTracker | **File:** KalmanFilter.cs | **Language:** C#

1D Kalman filter for smoothing IMU deltas.

**Constructor:** `KalmanFilter(double q, double r, double p, double x)` — q=process noise, r=measurement noise, p=initial error, x=initial value.

**Methods:** `double Update(double measurement)` — Returns filtered value.

---

## 2.9 headset-utils (Rust) — Sensor Fusion

### `trait Fusion: Send`
**Repo:** headset-utils | **File:** src/lib.rs | **Language:** Rust

Trait for sensor fusion implementations.

```rust
pub trait Fusion: Send {
    fn glasses(&mut self) -> &mut Box<dyn ARGlasses>;
    fn attitude_quaternion(&self) -> UnitQuaternion<f32>;
    fn inconsistency_frd(&self) -> f32;
    fn update(&mut self);
}
```

---

### `struct NaiveCF`
**Repo:** headset-utils | **File:** src/naive_cf.rs | **Language:** Rust

Naive complementary filter implementation combining accelerometer and gyroscope data.

**Methods:**
- `pub fn new(glasses: Box<dyn ARGlasses>) -> Result<Self>`
- Roll/pitch from accelerometer + gyroscope
- Yaw from gyroscope integration + magnetometer correction

---

### `pub fn any_glasses() -> Result<Box<dyn ARGlasses>>`
**Repo:** headset-utils | **File:** src/lib.rs | **Language:** Rust

Auto-detect and connect to any supported AR glasses.

---

### `pub fn any_fusion() -> Result<Box<dyn Fusion>>`
**Repo:** headset-utils | **File:** src/lib.rs | **Language:** Rust

Auto-detect glasses and create a fusion instance.

---

## 2.10 RayDesk Spatial Tracking

### `class HeadGazeCursor(screenWidth: Int, screenHeight: Int, ...)`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/input/HeadGazeCursor.kt | **Language:** Kotlin

Maps IMU head orientation to cursor position on the virtual screen.

**Methods:**
| Method | Description |
|--------|-------------|
| `updateHeadOrientation(yaw, pitch, timestamp)` | Update from Euler angles |
| `updateFromQuaternion(sensorValues, timestamp)` | Update from raw quaternion |
| `getCursorPosition() -> CursorPosition` | Get current cursor position |
| `recenter()` | Reset cursor to center |
| `reset()` | Full state reset |

---

### `class OneEuroFilter`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/spatial/OneEuroFilter.kt | **Language:** Kotlin

1€ noise filter for smooth head tracking. Combines low-pass filtering with speed-adaptive cutoff.

---

### `data class Quaternion(val w: Float, val x: Float, val y: Float, val z: Float)`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/spatial/Quaternion.kt | **Language:** Kotlin

Quaternion math utilities for spatial tracking.

**Companion Methods:**
- `identity() -> Quaternion`
- `fromSensorValues(values: FloatArray) -> Quaternion`
- `fromYawPitch(yawDegrees: Float, pitchDegrees: Float) -> Quaternion`

**Instance Methods:**
- `multiply(other: Quaternion) -> Quaternion`
- `inverse() -> Quaternion`
- `normalized() -> Quaternion`
- `toYawPitch() -> Pair<Float, Float>`

---

# 3. Camera & Computer Vision

## 3.1 Universal Camera API (xg-glass-sdk)

### `GlassesClient.capturePhoto(options: CaptureOptions) -> Result<CapturedImage>`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/GlassesClient.kt | **Language:** Kotlin

Capture a photo from the glasses camera. Returns JPEG bytes with metadata.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| options | CaptureOptions | Quality (0-100), target width/height, timeout (default 30s) |

**Returns:** `Result<CapturedImage>` — JPEG bytes, timestamp, dimensions, rotation, source model

**Per-Device Behavior:**
- **Rokid:** `takeGlassPhoto(w,h,quality)` → `syncSingleFile()` → `readBytes()`
- **Meta:** DAT SDK `StreamSession` → `capturePhoto()` (starts short-lived stream)
- **Omi:** BLE: write 0x05 to PHOTO_CONTROL_UUID, receive chunks on PHOTO_DATA_UUID, EOF=0xFFFF
- **Frame:** BLE via `frame_msg.RxPhoto` + `TxCaptureSettings`
- **Simulator:** CameraX or MediaMetadataRetriever (video looping)

---

### `data class CapturedImage`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/Models.kt | **Language:** Kotlin

**Fields:**
| Name | Type | Description |
|------|------|-------------|
| jpegBytes | ByteArray | Raw JPEG image data |
| timestampMs | Long | Capture timestamp |
| width | Int? | Image width (if available) |
| height | Int? | Image height (if available) |
| rotationDegrees | Int? | EXIF rotation |
| sourceModel | GlassesModel | Which device captured it |

---

### `data class CaptureOptions`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/Models.kt | **Language:** Kotlin

| Name | Type | Description |
|------|------|-------------|
| quality | Int? | JPEG quality 0-100 (Rokid). Null = device default |
| targetWidth | Int? | Target width for resize |
| targetHeight | Int? | Target height for resize |
| timeoutMs | Long | Capture timeout (default 30,000ms) |

---

## 3.2 MentraOS Camera

### `CameraModule`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/modules/camera.ts | **Language:** TypeScript

Camera control module for MentraOS glasses.

---

## 3.3 Frame Camera (nRF52840 + FPGA)

### `frame.file.open(path, mode)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/file.c | **Language:** C (Lua binding)

Open a file for camera image storage on the Frame's LittleFS filesystem.

---

## 3.4 XREAL SLAM Camera

### `struct NrealLightSlamCamera`
**Repo:** headset-utils | **File:** src/nreal_light.rs | **Language:** Rust

Access the XREAL Light's SLAM tracking cameras.

**Methods:**
- `pub fn new() -> Result<Self>`
- `pub fn new(fd: isize) -> Result<Self>` — From file descriptor
- `pub fn get_frame(timeout: Duration) -> Result<NrealLightSlamCameraFrame>`

---

## 3.5 RayNeo Camera Sharing

### `class ShareCameraCtrl : MonoBehaviour`
**Repo:** rayneo-setup | **File:** Assets/.../Interactive/ShareCameraCtrl.cs | **Language:** C# (Unity)

Camera sharing control for RayNeo X2 glasses.

---

### `class CameraPermissionRequest : MonoBehaviour`
**Repo:** rayneo-setup | **File:** Assets/.../Tool/CameraPermissionRequest.cs | **Language:** C# (Unity)

Request camera permissions on RayNeo platform.

---

# 4. Audio & Speech

## 4.1 Universal Audio API (xg-glass-sdk)

### `GlassesClient.playAudio(source: AudioSource, options: PlayAudioOptions) -> Result<Unit>`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/GlassesClient.kt | **Language:** Kotlin

Play audio on the glasses (TTS or raw audio bytes).

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| source | AudioSource | Tts(text) or RawBytes(data, pcmFormat) |
| options | PlayAudioOptions | speechRate (0.75-4.0), interrupt (default true) |

**Per-Device Behavior:**
- **Rokid:** TTS via `CxrApi.sendGlobalTtsContent()`, raw PCM via AudioTrack
- **Meta:** PCM via AudioTrack (A2DP), encoded via MediaPlayer + temp file
- **Omi:** UNSUPPORTED
- **Frame:** UNSUPPORTED
- **Simulator:** Android TextToSpeech

---

### `GlassesClient.startMicrophone(options: MicrophoneOptions) -> Result<MicrophoneSession>`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/GlassesClient.kt | **Language:** Kotlin

Start microphone capture, returning a streaming audio session.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| options | MicrophoneOptions | preferredEncoding (PCM_S16_LE/OPUS), sampleRate (16kHz), channelCount (1), vendorMode |

**Returns:** `Result<MicrophoneSession>` — Session with format info and audio Flow

**Per-Device Behavior:**
- **Rokid:** CxrApi `openAudioRecord()` (PCM/OPUS streams)
- **Meta:** AudioRecord via Bluetooth HFP (8kHz mono)
- **Omi:** OPUS 16kHz mono via BLE notifications
- **Frame:** BLE audio via `frame_msg`
- **Simulator:** Android AudioRecord

---

### `interface MicrophoneSession`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/Audio.kt | **Language:** Kotlin

```kotlin
interface MicrophoneSession {
    val format: AudioFormat
    val audio: Flow<AudioChunk>  // Hot stream of audio chunks
    suspend fun stop()
}
```

---

### `data class AudioChunk`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/Audio.kt | **Language:** Kotlin

| Name | Type | Description |
|------|------|-------------|
| bytes | ByteArray | Raw audio data |
| format | AudioFormat | Encoding, sample rate, channels |
| sequence | Long | Sequence number |
| timestampMs | Long | Timestamp |
| endOfStream | Boolean | True if this is the last chunk |

---

## 4.2 MentraOS Audio

### `AudioManager`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/modules/audio.ts | **Language:** TypeScript

Audio manager for MentraOS glasses sessions.

---

## 4.3 Groq Audio Transcription (TAPLINKX3)

### `class GroqAudioService(context: Context)`
**Repo:** TAPLINKX3 | **File:** app/src/main/java/com/TapLink/app/GroqAudioService.kt | **Language:** Kotlin

Voice-to-text service using Groq's Whisper API (whisper-large-v3).

**Methods:**
| Method | Description |
|--------|-------------|
| `setListener(listener: TranscriptionListener)` | Set callback listener |
| `hasApiKey() -> Boolean` | Check if API key is configured |
| `setApiKey(key: String)` | Set Groq API key |
| `startRecording()` | Start M4A recording (44.1kHz AAC 128kbps) |
| `stopRecording()` | Stop and send to Groq for transcription |
| `isRecording() -> Boolean` | Check recording state |

**Interface: `TranscriptionListener`**
- `onTranscriptionResult(text: String)`
- `onError(message: String)`
- `onRecordingStart()`
- `onRecordingStop()`

---

## 4.4 BeatSync Audio Synchronization

### `WebSocket Protocol — PLAY`
**Repo:** beatsync | **File:** packages/shared/types/WSRequest.ts | **Language:** TypeScript

Request synchronized play across all connected devices.

### `WebSocket Protocol — NTP_REQUEST / NTP_RESPONSE`
**Repo:** beatsync | **File:** packages/shared/types/ | **Language:** TypeScript

NTP-inspired time synchronization: client sends t0, server stamps t1/t2, client receives at t3. EMA smoothing (alpha=0.2) for RTT. Min 10 measurements before "synced".

---

## 4.5 Pebble Ring Audio

### `actual class AudioRecorder : AutoCloseable`
**Repo:** mobileapp | **File:** ring/audio/ | **Language:** Kotlin (KMP)

Platform-specific audio recorder for Pebble smart ring.

**Methods:**
- `actual suspend fun startRecording(): RawSource`
- `actual suspend fun stopRecording()`
- `actual override fun close()`

---

### `actual class AudioPlayer : AutoCloseable`
**Repo:** mobileapp | **File:** ring/audio/ | **Language:** Kotlin (KMP)

**Methods:**
- `actual fun playRaw(samples, sampleRate, encoding, channels)`
- `actual fun playAAC(samples: Source, sampleRate: Long)`
- `actual fun stop()`

---

# 5. BLE & Wireless Communication

## 5.1 Omi Glass BLE UUIDs

**Repo:** xg-glass-sdk | **File:** devices/device-omi/OmiGlassesClient.kt | **Language:** Kotlin

```kotlin
AUDIO_SERVICE_UUID     = "19B10000-E8F2-537E-4F6C-D104768A1214"
AUDIO_DATA_UUID        = "19B10001-E8F2-537E-4F6C-D104768A1214"
AUDIO_CODEC_UUID       = "19B10002-E8F2-537E-4F6C-D104768A1214"
BATTERY_SERVICE_UUID   = "0000180F-0000-1000-8000-00805F9B34FB"
BATTERY_LEVEL_UUID     = "00002A19-0000-1000-8000-00805F9B34FB"
DEVICE_INFO_SERVICE    = "0000180A-0000-1000-8000-00805F9B34FB"
PHOTO_CONTROL_UUID     = "19B10006-E8F2-537E-4F6C-D104768A1214"
PHOTO_DATA_UUID        = "19B10005-E8F2-537E-4F6C-D104768A1214"
TIME_SYNC_SERVICE_UUID = "19B10030-E8F2-537E-4F6C-D104768A1214"
TIME_SYNC_WRITE_UUID   = "19B10031-E8F2-537E-4F6C-D104768A1214"
```

---

## 5.2 Frame BLE (nRF52840)

### `void bluetooth_setup(void)`
**Repo:** frame-codebase | **File:** source/application/bluetooth.h | **Language:** C

Initialize BLE stack on the nRF52840 SoC.

### `bool bluetooth_is_paired(void)`
**Repo:** frame-codebase | **File:** source/application/bluetooth.h | **Language:** C

### `void bluetooth_unpair(void)`
**Repo:** frame-codebase | **File:** source/application/bluetooth.h | **Language:** C

### `bool bluetooth_is_connected(void)`
**Repo:** frame-codebase | **File:** source/application/bluetooth.h | **Language:** C

### `bool bluetooth_send_data(const uint8_t* data, size_t length)`
**Repo:** frame-codebase | **File:** source/application/bluetooth.h | **Language:** C

Send data over BLE to the connected phone.

---

## 5.3 Rokid BLE + Wi-Fi P2P

**Repo:** xg-glass-sdk | **File:** devices/device-rokid/RokidGlassesClient.kt | **Language:** Kotlin

Connection flow: BLE scan → `initBluetooth()` → `connectBluetooth()` → `initWifiP2P()`

**Constants:**
- `ROKID_SERVICE_UUID = "00009100-0000-1000-8000-00805f9b34fb"`
- SharedPrefs: `"universal_glasses_rokid_bt_reconnect"`, keys: `"socket_uuid"`, `"mac_address"`

---

## 5.4 Pebble Ring BLE

### `actual class RingCompanionDeviceManager(scope)`
**Repo:** mobileapp | **File:** ring/ | **Language:** Kotlin (KMP)

BLE companion device manager for Pebble smart ring.

**Methods:**
- `actual suspend fun unregister(satellite)`
- `actual suspend fun unregisterAll()`
- `actual suspend fun openPairingPicker() -> CompanionRegisterResult`

---

## 5.5 MentraOS WebSocket Transport

### `class WebSocketTransport`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/transport/WebSocketTransport.ts | **Language:** TypeScript

WebSocket-based transport for MentraOS cloud communication.

### `interface Transport`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/transport/Transport.ts | **Language:** TypeScript

Transport abstraction with `TransportState` tracking.

---

# 6. Gesture & Input

## 6.1 XRLinuxDriver Multi-Tap Detection

### `multitap.h — Multi-Tap Gesture Detection`
**Repo:** XRLinuxDriver | **File:** include/multitap.h | **Language:** C

Detects double-tap (recenter) and triple-tap (recalibrate) gestures from IMU acceleration spikes.

---

## 6.2 TAPLINKX3 Keyboard & Cursor

### `class CustomKeyboardView(context: Context, attrs: AttributeSet?) : ViewGroup`
**Repo:** TAPLINKX3 | **File:** app/src/main/java/com/TapLink/app/CustomKeyboardView.kt | **Language:** Kotlin

Full on-screen keyboard for AR glasses with LETTERS and SYMBOLS modes, caps lock, and head-tracking hover support.

**Methods:**
- `setOnKeyboardActionListener(listener: OnKeyboardActionListener)`
- `updateHover(x: Float, y: Float)` — Update hover position from head tracking
- `clearHover()`
- `handleAnchoredTap(x: Float, y: Float)` — Process tap in anchored mode
- `copyStateFrom(source: CustomKeyboardView)` — Sync state between left/right eye keyboards

**Interface:**
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

---

## 6.3 RayNeo Touch & Gaze Input

### `class SampleCubeCtrl : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler, IPointerClickHandler`
**Repo:** rayneo-setup | **File:** Assets/.../SampleCubeCtrl.cs | **Language:** C# (Unity)

Interactive cube responding to gaze-based input on RayNeo X2.

**Methods:**
- `OnPointerEnter(PointerEventData)` — Gaze enters object
- `OnPointerExit(PointerEventData)` — Gaze exits object
- `OnPointerClick(PointerEventData)` — Gaze click/tap
- `ModifyRotation()` — Toggle object rotation

---

### `class TestTouchEvent : MonoBehaviour`
**Repo:** rayneo-setup | **File:** Assets/.../Interactive/TestTouchEvent.cs | **Language:** C# (Unity)

Touch event handling for RayNeo ring controller.

---

### `class RingTouchCube : MonoBehaviour`
**Repo:** rayneo-setup | **File:** Assets/.../Interactive/RingTouchCube.cs | **Language:** C# (Unity)

Ring-based touch interaction with 3D objects.

---

## 6.4 MentraOS Events

### `AppSession.onButtonPress(handler: (data) => void): () => void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/index.ts | **Language:** TypeScript

Subscribe to physical button press events on glasses.

### `AppSession.onTouchEvent(gesture: string, handler: (data) => void): () => void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/index.ts | **Language:** TypeScript

Subscribe to touch gesture events.

---

## 6.5 StardustXR Hand Tracking

### `struct Hand { pub thumb: Thumb, pub index: Finger, ... }`
**Repo:** stardust-core | **File:** fusion/src/input.rs | **Language:** Rust

Full hand skeleton with 26 joints from OpenXR hand tracking.

### `impl Finger`
**Repo:** stardust-core | **File:** fusion/src/input.rs | **Language:** Rust

- `pub fn length(&self) -> f32` — Total finger length
- `pub fn direction(&self) -> Vector3<f32>` — Finger pointing direction

---

# 7. Spatial Computing (SLAM, Anchors, OpenXR)

## 7.1 OpenXR Core Functions

### `xrCreateInstance(const XrInstanceCreateInfo*, XrInstance*) -> XrResult`
**Repo:** OpenXR Spec | **Language:** C

Create an OpenXR instance. Root object for all XR operations.

---

### `xrCreateSession(XrInstance, const XrSessionCreateInfo*, XrSession*) -> XrResult`
**Repo:** OpenXR Spec | **Language:** C

Create an XR session with graphics binding.

---

### `xrCreateReferenceSpace(XrSession, const XrReferenceSpaceCreateInfo*, XrSpace*) -> XrResult`
**Repo:** OpenXR Spec | **Language:** C

Create a reference space. Types: VIEW (head-locked), LOCAL (recenterable), STAGE (room-scale), LOCAL_FLOOR, UNBOUNDED_MSFT.

---

### `xrLocateSpace(XrSpace, XrSpace, XrTime, XrSpaceLocation*) -> XrResult`
**Repo:** OpenXR Spec | **Language:** C

Locate one space relative to another at a given time. Returns pose (position + orientation) with tracking confidence flags.

---

### `xrWaitFrame(XrSession, const XrFrameWaitInfo*, XrFrameState*) -> XrResult`
**Repo:** OpenXR Spec | **Language:** C

Wait for the next frame to render. Returns predicted display time.

---

### `xrBeginFrame(XrSession, const XrFrameBeginInfo*) -> XrResult`
**Repo:** OpenXR Spec | **Language:** C

Signal the start of frame rendering.

---

### `xrEndFrame(XrSession, const XrFrameEndInfo*) -> XrResult`
**Repo:** OpenXR Spec | **Language:** C

Submit rendered layers for display. Supports: PROJECTION, QUAD, CYLINDER, EQUIRECT, PASSTHROUGH layers.

---

### `xrLocateViews(XrSession, const XrViewLocateInfo*, XrViewState*, uint32_t, uint32_t*, XrView*) -> XrResult`
**Repo:** OpenXR Spec | **Language:** C

Get per-eye view poses and field of view for rendering.

---

### `xrSyncActions(XrSession, const XrActionsSyncInfo*) -> XrResult`
**Repo:** OpenXR Spec | **Language:** C

Synchronize action state with the runtime.

---

### `xrGetActionStateBoolean / Float / Vector2f / Pose`
**Repo:** OpenXR Spec | **Language:** C

Read current state of input actions (buttons, triggers, thumbsticks, poses).

---

### `xrApplyHapticFeedback(XrSession, const XrHapticActionInfo*, const XrHapticBaseHeader*) -> XrResult`
**Repo:** OpenXR Spec | **Language:** C

Apply haptic feedback to a controller.

---

## 7.2 Monado XR Runtime

### `struct xrt_device`
**Repo:** Monado | **File:** src/xrt/include/xrt/xrt_device.h | **Language:** C

Central device interface with 30+ method pointers.

**Key Methods:**
| Method | Description |
|--------|-------------|
| `update_inputs(xdev)` | Refresh input state |
| `get_tracked_pose(xdev, name, timestamp, *out)` | Get 6DoF pose |
| `get_hand_tracking(xdev, name, timestamp, *out_value, *out_ts)` | Get hand joints |
| `get_face_tracking(xdev, type, timestamp, *out)` | Facial expressions |
| `get_body_joints(xdev, type, timestamp, *out)` | Full body tracking |
| `set_output(xdev, name, *value)` | Haptic output |
| `begin_plane_detection_ext(xdev, ...)` | Start plane detection |
| `get_plane_detections_ext(xdev, id, *out)` | Get detected planes |
| `compute_distortion(xdev, view, u, v, *out)` | Lens distortion |
| `get_battery_status(xdev, ...)` | Battery level |
| `set_brightness(xdev, brightness, relative)` | Display brightness |

---

### `struct xrt_space_overseer`
**Repo:** Monado | **File:** src/xrt/include/xrt/xrt_space.h | **Language:** C

Manages all XR spaces in the system.

**Key Methods:**
- `create_offset_space(parent, *offset, **out_space)`
- `create_pose_space(xdev, name, **out_space)`
- `locate_space(base_space, *offset, at_ns, space, *offset, *out_rel)`
- `locate_spaces(base, *offset, at_ns, **spaces, count, *offsets, *out_rels)` — Batch locate
- `recenter_local_spaces()` — Recenter all local spaces

---

## 7.3 RayNeo SLAM

### `class SlamDemoCtrl : MonoBehaviour`
**Repo:** rayneo-setup | **File:** Assets/.../Algorithm/SlamDemoCtrl.cs | **Language:** C# (Unity)

SLAM cube placement demo using RayNeo 6DoF tracking.

**Fields:**
- `m_Cube: GameObject` — Cube prefab
- `m_LineCount: int = 10` — Grid dimensions
- `m_CubeSpace: float = 0.3f` — Spacing between cubes

**Methods:**
- `OnPostUpdate(Pose pose)` — SLAM pose callback, receives 6DoF position+rotation

---

### `class TestPlaneDetection : MonoBehaviour`
**Repo:** rayneo-setup | **File:** Assets/.../Algorithm/PlaneDetection/TestPlaneDetection.cs | **Language:** C# (Unity)

Plane detection visualization using RayNeo ARDK.

---

### `class ResetHeadTrack : MonoBehaviour`
**Repo:** rayneo-setup | **File:** Assets/.../ResetHeadTrack.cs | **Language:** C# (Unity)

**Methods:** `void OnReset()` — Reset head tracking origin.

---

## 7.4 XRLinuxDriver IPC

### `bool setup_ipc_values(ipc_values_type *ipc_values, bool debug)`
**Repo:** XRLinuxDriver | **File:** include/ipc.h | **Language:** C

Set up shared memory IPC for pose data communication between driver and applications.

### `struct ipc_values_t`
**Repo:** XRLinuxDriver | **File:** include/ipc.h | **Language:** C

```c
struct ipc_values_t {
    float *display_res;           // [w, h]
    bool  *disabled;
    float *date;                  // [4] keepalive
    float *pose_orientation;      // [16] quaternion data
    float *pose_position;         // [3] xyz position
    pthread_mutex_t *pose_orientation_mutex;
    float *display_fov;
    float *lens_distance_ratio;
};
```

---

# 8. ML/AI On-Device

## 8.1 Frame TFLite Micro

### `tflm_status_t tflm_initialize(void)`
**Repo:** frame-codebase | **File:** source/application/tflm_wrapper.h | **Language:** C

Initialize TensorFlow Lite Micro runtime for the hello world float model.

---

### `tflm_status_t tflm_infer(float input, float* output)`
**Repo:** frame-codebase | **File:** source/application/tflm_wrapper.h | **Language:** C

Run inference on the hello world float model.

---

### `tflm_status_t tflm_initialize_int8(void)`
**Repo:** frame-codebase | **File:** source/application/tflm_wrapper.h | **Language:** C

Initialize the quantized int8 hello world model.

---

### `tflm_status_t fomo_initialize(void)`
**Repo:** frame-codebase | **File:** source/application/tflm_wrapper.h | **Language:** C

Initialize the FOMO (Faster Objects, More Objects) detection model.

---

### `tflm_status_t fomo_infer(const uint8_t* input_grayscale, int8_t* output_grid)`
**Repo:** frame-codebase | **File:** source/application/tflm_wrapper.h | **Language:** C

Run FOMO object detection on a grayscale image.

---

### `tflm_status_t person_detect_initialize(void)`
**Repo:** frame-codebase | **File:** source/application/tflm_wrapper.h | **Language:** C

Initialize person detection (Visual Wake Words) model.

---

### `tflm_status_t person_detect_infer(const uint8_t* input_image, int8_t* output_scores)`
**Repo:** frame-codebase | **File:** source/application/tflm_wrapper.h | **Language:** C

Run person detection inference.

---

## 8.2 SAM3 (Segment Anything Model 3)

### `build_sam3_predictor(checkpoint_path, device="cuda", ...) -> SAM3Predictor`
**Repo:** sam3 | **File:** sam3/model_builder.py | **Language:** Python

Build a SAM3 image predictor for single-image segmentation.

---

### `build_sam3_video_predictor(*args, gpus_to_use=None, **kwargs)`
**Repo:** sam3 | **File:** sam3/model_builder.py | **Language:** Python

Build a SAM3 video predictor for video segmentation with tracking.

---

### `build_sam3_image_model(checkpoint_path, device="cuda", eval_mode=True, ...) -> SAM3Model`
**Repo:** sam3 | **File:** sam3/model_builder.py | **Language:** Python

Build core SAM3 image model.

---

### `download_ckpt_from_hf(version="sam3") -> str`
**Repo:** sam3 | **File:** sam3/model_builder.py | **Language:** Python

Download SAM3 checkpoint from HuggingFace.

---

### `class PromptEncoder(nn.Module)`
**Repo:** sam3 | **File:** sam3/sam/prompt_encoder.py | **Language:** Python

Encode prompts (points, boxes, masks) into embeddings for SAM3.

**Methods:**
- `get_dense_pe() -> Tensor` — Get dense positional encoding
- `forward(points, boxes, masks) -> (sparse_embeddings, dense_embeddings)`

---

### `class MaskDecoder(nn.Module)`
**Repo:** sam3 | **File:** sam3/sam/mask_decoder.py | **Language:** Python

Decode masks from image and prompt embeddings.

**Methods:**
- `forward(image_embeddings, image_pe, sparse_prompt, dense_prompt, ...) -> (masks, iou_predictions)`
- `predict_masks(...) -> (masks, iou_predictions)`

---

## 8.3 Groq LLM Integration (TAPLINKX3)

### `class GroqInterface(context: Context, webView: WebView)`
**Repo:** TAPLINKX3 | **File:** app/src/main/java/com/TapLink/app/GroqInterface.kt | **Language:** Kotlin

JavaScript bridge for Groq AI chat.

**Methods (all @JavascriptInterface):**
- `ping() -> String` — Returns "pong"
- `getActivePageUrl() -> String` — Get current page URL
- `chatWithGroq(message: String, historyJson: String, ttsEnabled: Boolean)` — Chat with llama3-70b-8192
- `speakWithOrpheus(text: String)` — TTS via Orpheus
- `openUrlInNewTab(url: String)` — Open URL

---

## 8.4 Pebble Ring AI Agent

### `class SendBeeperMessageTool`
**Repo:** mobileapp | **File:** ring/agent/builtin_servlets/messaging/ | **Language:** Kotlin

MCP tool for sending messages via Beeper.

### `class SearchBeeperForContactTool`
**Repo:** mobileapp | **File:** ring/agent/builtin_servlets/messaging/ | **Language:** Kotlin

MCP tool for searching Beeper contacts.

### `class SetAlarmTool` / `class SetTimerTool`
**Repo:** mobileapp | **File:** ring/agent/builtin_servlets/clock/ | **Language:** Kotlin

MCP tools for setting alarms and timers.

### `class CactusModelProvider`
**Repo:** mobileapp | **File:** ring/model/ | **Language:** Kotlin

On-device AI model provider (Cactus framework).

---

# 9. GPS & Geolocation

## 9.1 RayNeo GPS via IPC

### `class TestIPC : MonoBehaviour`
**Repo:** rayneo-setup | **File:** Assets/.../Interactive/TestIPC.cs | **Language:** C# (Unity)

IPC demo accessing GPS data from RayNeo Mercury platform.

**Fields:**
- `m_gpsInfo: Text` — GPS data display
- `m_RingCube: RingTouchCube` — Ring interaction

---

### TAPLINKX3 GPS Integration

Uses RayNeo Mercury IPC (`com.ffalconxr.mercury.ipc.Launcher`) for location access. GPS coordinates are injected into Groq chat system prompts for location-aware responses.

---

## 9.2 MentraOS Location

### `AppSession.location: LocationModule`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/index.ts | **Language:** TypeScript

Location module for accessing glasses GPS/location data.

---

# 10. Device Management & Connectivity

## 10.1 Universal Connection API

### `GlassesClient.connect() -> Result<Unit>`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/GlassesClient.kt | **Language:** Kotlin

Establish connection to the glasses. Transport varies by device.

---

### `GlassesClient.disconnect()`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/GlassesClient.kt | **Language:** Kotlin

Tear down connection. Safe to call multiple times.

---

### `sealed class ConnectionState`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/StateAndEvents.kt | **Language:** Kotlin

- `Disconnected` — Not connected
- `Connecting` — Connection in progress
- `Connected` — Active connection
- `Error(error: GlassesError)` — Connection error

---

### `sealed class GlassesError`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/Errors.kt | **Language:** Kotlin

- `NotConnected` — Not connected to device
- `PermissionDenied` — Required permissions not granted
- `Busy` — Device is busy with another operation
- `Timeout(operation: String)` — Operation timed out
- `Transport(detail: String, raw: Throwable?)` — Transport-layer error
- `Unsupported(detail: String)` — Feature not supported on this device

---

## 10.2 Device Capability Matrix

### `data class DeviceCapabilities`
**Repo:** xg-glass-sdk | **File:** core/src/main/java/com/universalglasses/core/Models.kt | **Language:** Kotlin

| Field | Rokid | Meta | Omi | Frame | RayNeo | Simulator |
|-------|-------|------|-----|-------|--------|-----------|
| canCapturePhoto | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| canDisplayText | ✔ | ✘ | ✘ | ✔ | ✔ | ✔ |
| canRecordAudio | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| canPlayTts | ✔ | ✘ | ✘ | ✘ | ✘ | ✔ |
| canPlayAudioBytes | ✔ | ✔ | ✘ | ✘ | ✔ | ✘ |
| supportsTapEvents | ✘ | ✘ | ✘ | ✔ | ✘ | ✘ |
| supportsStreamingText | ✔ | ✘ | ✘ | ✔ | ✘ | ✘ |

---

## 10.3 MentraOS Session Management

### `class AppServer extends Hono`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/server/index.ts | **Language:** TypeScript

```typescript
class AppServer extends Hono {
    constructor(config: AppServerConfig);
    onSession(handler: (session: AppSession) => void): void;
    async start(): Promise<void>;
}

interface AppServerConfig {
    packageName: string;
    apiKey: string;
    port?: number;       // default: 3000
    cloudUrl?: string;
}
```

---

### `class AppSession`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/index.ts | **Language:** TypeScript

**Sub-managers:** events, display, settings, dashboard, location, camera, led, audio, storage

**Connection Methods:**
- `async connect(sessionId: string): Promise<void>`
- `async disconnect(options?: { reason?: string }): Promise<void>`
- `async releaseOwnership(reason: string): Promise<void>`

**Event Subscriptions:**
- `onTranscription(handler) -> () => void`
- `onHeadPosition(handler) -> () => void`
- `onButtonPress(handler) -> () => void`
- `onTouchEvent(gesture, handler) -> () => void`
- `onPhoneNotification(handler) -> () => void`
- `onGlassesBattery(handler) -> () => void`
- `onConnectionState(handler) -> () => void`

**Multi-user:**
- `async discoverAppUsers(domain, includeProfiles?) -> any`
- `async isUserActive(userId) -> boolean`
- `async getUserCount(domain) -> number`
- `async broadcastToAppUsers(payload) -> void`
- `async sendDirectMessage(targetUserId, payload) -> boolean`
- `async joinAppRoom(roomId, options?) -> void`
- `async leaveAppRoom(roomId) -> void`

---

## 10.4 XRLinuxDriver Device Management

### `void connection_pool_init(pose_handler_t callback, reference_pose_getter_t getter)`
**Repo:** XRLinuxDriver | **File:** include/connection_pool.h | **Language:** C

Initialize the device connection pool with pose handling callbacks.

---

### `void connection_pool_handle_device_added(const device_driver_type* driver, device_properties_type* device)`
**Repo:** XRLinuxDriver | **File:** include/connection_pool.h | **Language:** C

Handle a new device being detected (USB hotplug).

---

### `bool connection_pool_is_connected()`
**Repo:** XRLinuxDriver | **File:** include/connection_pool.h | **Language:** C

Check if any device is connected.

---

### `device_properties_type* connection_pool_primary_device()`
**Repo:** XRLinuxDriver | **File:** include/connection_pool.h | **Language:** C

Get the primary (active) device properties.

---

### `struct device_properties_t`
**Repo:** XRLinuxDriver | **File:** include/devices.h | **Language:** C

```c
struct device_properties_t {
    char *brand, *model;
    int hid_vendor_id, hid_product_id;
    int resolution_w, resolution_h;
    float fov;                    // diagonal FOV degrees
    float lens_distance_ratio;
    int calibration_wait_s;
    int imu_cycles_per_s;
    int imu_buffer_size;
    float look_ahead_constant;
    bool sbs_mode_supported;
    bool provides_orientation;    // 3DoF
    bool provides_position;       // 6DoF
};
```

---

### `struct device_driver_t`
**Repo:** XRLinuxDriver | **File:** include/devices.h | **Language:** C

Device driver interface with function pointers:
- `supported_device_func(vendor, product, bus, addr)` → device_properties
- `device_connect_func()`
- `block_on_device_func()`
- `device_is_sbs_mode_func()` / `device_set_sbs_mode_func(enabled)`
- `is_connected_func()`
- `disconnect_func(soft)`

---

## 10.5 headset-utils Device Abstraction (Rust)

### `trait ARGlasses: Send`
**Repo:** headset-utils | **File:** src/lib.rs | **Language:** Rust

```rust
pub trait ARGlasses: Send {
    fn serial(&mut self) -> Result<String>;
    fn read_event(&mut self) -> Result<GlassesEvent>;
    fn get_display_mode(&mut self) -> Result<DisplayMode>;
    fn set_display_mode(&mut self, mode: DisplayMode) -> Result<()>;
    fn display_fov(&self) -> f32;
    fn imu_to_display_matrix(&self, side: Side, ipd: f32) -> Isometry3<f64>;
    fn name(&self) -> &'static str;
    fn cameras(&self) -> Result<Vec<CameraDescriptor>>;
    fn display_matrices(&self) -> Result<(DisplayMatrices, DisplayMatrices)>;
    fn display_delay(&self) -> u64;
}
```

**Implementations:**
- `NrealAir::new() -> Result<Self>`
- `NrealLight::new() -> Result<Self>`
- `RokidAir::new() -> Result<Self>`
- `GrawoowG530::new() -> Result<Self>`
- `MadGazeGlow::new() -> Result<Self>`

---

## 10.6 XREAL WebHID Protocol

### `function hidSupported() -> boolean`
**Repo:** xreal-webxr | **File:** js_air/manager.js | **Language:** JavaScript

Check if WebHID API is available in the browser.

---

### `async function getFirmwareVersionInMcu() -> string`
**Repo:** xreal-webxr | **File:** js_air/manager.js | **Language:** JavaScript

Read MCU firmware version from XREAL Air glasses.

---

### `function cmd_build(msgId, payload) -> Uint8Array`
**Repo:** xreal-webxr | **File:** js_air/protocol.js | **Language:** JavaScript

Build a HID command packet for XREAL Air glasses.

**Constants:**
- `NREAL_VENDOR_ID = 0x3318`
- `BOOT_PRODUCT_ID = 0x0423`
- `IMU_TIMEOUT = 250`

---

### `class Glasses extends EventTarget`
**Repo:** xreal-webxr | **File:** js_air/glasses.js | **Language:** JavaScript

XREAL Air glasses controller. Emits events: 'imu', 'button', 'brightness', 'display_mode'.

---

## 10.7 Decky XRGaming Plugin

### `class Plugin (Python backend)`
**Repo:** decky-XRGaming | **File:** main.py | **Language:** Python

Steam Deck plugin for managing Breezy XR driver.

**Methods:**
- `async def retrieve_config()` — Get driver config
- `async def write_config(config)` — Write driver config
- `async def write_control_flags(flags)` — Set control flags
- `async def retrieve_driver_state()` — Get current state
- `async def check_installation()` — Verify Breezy installed
- `async def request_token(email)` — Request license
- `async def verify_token(token)` — Verify license
- `async def force_reset_driver()` — Hard reset

---

## 10.8 RayNeo Installer (ADB-over-TCP)

### `class RayNeoInstallerGlassesClient(context, config) : GlassesClient`
**Repo:** xg-glass-sdk | **File:** devices/device-rayneo-installer/ | **Language:** Kotlin

Phone-side client that pushes APK to RayNeo glasses via ADB-over-TCP.

- `connect()` = install APK to glasses
- `suspend fun pushUserSettings(settings: Map<String, String>): Result<Unit>`
- Nested: `class AdbRemoteInstaller`, `object SyncProtocol`, `object ShellProtocol`

---

## 10.9 App Contract System

### `interface UniversalAppEntry`
**Repo:** xg-glass-sdk | **File:** app-contract/src/main/java/com/universalglasses/appcontract/UniversalAppEntry.kt | **Language:** Kotlin

```kotlin
interface UniversalAppEntry {
    val id: String
    val displayName: String
    fun commands(env: HostEnvironment): List<UniversalCommand>
    fun userSettings(): List<UserSettingField> = emptyList()
}
```

---

### `interface UniversalCommand`
**Repo:** xg-glass-sdk | **File:** app-contract/ | **Language:** Kotlin

```kotlin
interface UniversalCommand {
    val id: String
    val title: String
    suspend fun run(ctx: UniversalAppContext): Result<Unit>
}
```

---

### `object AIApiSettings`
**Repo:** xg-glass-sdk | **File:** app-contract/ | **Language:** Kotlin

Helper for AI API configuration fields.

- `fun fields(defaultBaseUrl, defaultModel, defaultApiKey) -> List<UserSettingField>`
- `fun baseUrl(settings) -> String`
- `fun model(settings) -> String`
- `fun apiKey(settings) -> String`

---

## 10.10 Token Utilities (MentraOS)

### `function createToken(payload: AppTokenPayload, secret: string, expiresIn?: string): string`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/token/ | **Language:** TypeScript

### `function validateToken(token: string, secret: string): TokenValidationResult`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/token/ | **Language:** TypeScript

### `function generateWebviewUrl(baseUrl: string, token: string): string`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/token/ | **Language:** TypeScript

---

# 11. 3D Environment (StardustXR)

## 11.1 StardustXR Client SDK (Rust — fusion crate)

### `impl Client`
**Repo:** stardust-core | **File:** fusion/src/client.rs | **Language:** Rust

```rust
pub async fn connect() -> Result<Self, ClientError>;
pub fn from_connection(connection: UnixStream) -> Self;
pub fn handle(&self) -> Arc<ClientHandle>;
pub fn get_root(&self) -> &Root;
pub fn setup_resources(&self, paths: &[&Path]) -> NodeResult<()>;
pub async fn dispatch(&mut self) -> Result<(), MessengerError>;
pub async fn flush(&mut self) -> Result<(), MessengerError>;
pub async fn await_method<O, F: Future<Output = O>>(&mut self, method: F) -> O;
pub async fn sync_event_loop<F: FnMut(&Arc<ClientHandle>, &mut ControlFlow)>(mut self, f: F);
pub fn async_event_loop(mut self) -> AsyncEventLoop;
```

---

### `struct Transform`
**Repo:** stardust-core | **File:** fusion/src/spatial.rs | **Language:** Rust

```rust
pub struct Transform {
    pub translation: Option<Vector3<f32>>,
    pub rotation: Option<Quaternion>,
    pub scale: Option<Vector3<f32>>,
}

impl Transform {
    pub fn from_translation(t) -> Self;
    pub fn from_rotation(r) -> Self;
    pub fn from_scale(s) -> Self;
    pub fn from_translation_rotation(t, r) -> Self;
    pub fn from_rotation_scale(r, s) -> Self;
    pub fn from_translation_rotation_scale(t, r, s) -> Self;
}
```

---

## 11.2 Drawables

### `impl Lines`
**Repo:** stardust-core | **File:** fusion/src/drawable.rs | **Language:** Rust

```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              lines: &[Line]) -> NodeResult<Self>;
```

3D line drawing with per-vertex color and thickness.

---

### `impl Model`
**Repo:** stardust-core | **File:** fusion/src/drawable.rs | **Language:** Rust

```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              model_resource: &ResourceID) -> NodeResult<Self>;
pub fn part(&self, relative_path: &str) -> NodeResult<ModelPart>;
```

Load GLTF 3D models. Access individual mesh parts for material overrides.

---

### `impl Text`
**Repo:** stardust-core | **File:** fusion/src/drawable.rs | **Language:** Rust

```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              text: &str, style: TextStyle, bounds: TextBounds) -> NodeResult<Self>;
```

3D text rendering with font, size, bounds, and alignment.

---

### `impl Sound`
**Repo:** stardust-core | **File:** fusion/src/drawable.rs | **Language:** Rust

```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              resource: &ResourceID) -> NodeResult<Self>;
```

Spatial audio source positioned in 3D space.

---

## 11.3 Fields (Signed Distance Fields)

### `impl Field`
**Repo:** stardust-core | **File:** fusion/src/fields.rs | **Language:** Rust

```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              shape: FieldShape) -> NodeResult<Self>;
```

Shapes: Sphere, Box, Cylinder, Torus, CubicSpline.

**Operations:**
- `distance(point) -> f32` — SDF evaluation
- `normal(point) -> Vec3` — Surface normal
- `closest_point(point) -> Vec3` — Nearest surface point
- `ray_march(origin, direction) -> (f32, Vec3)` — Ray marching

---

## 11.4 Input System

### `impl InputMethod`
**Repo:** stardust-core | **File:** fusion/src/input.rs | **Language:** Rust

```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              datamap: Datamap) -> NodeResult<Self>;
```

Input source (pointer, hand, tip). Data types: `Pointer`, `Hand` (26 joints), `Tip`.

---

### `impl InputHandler`
**Repo:** stardust-core | **File:** fusion/src/input.rs | **Language:** Rust

```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              field: &impl FieldAspect, handler: impl Fn(...)) -> NodeResult<Self>;
```

Receives input events when an InputMethod intersects the handler's Field.

---

## 11.5 Panel Items (2D in 3D)

### `impl PanelItemUi`
**Repo:** stardust-core | **File:** fusion/src/items.rs | **Language:** Rust

Register as a panel item UI provider.

```rust
pub fn register(client: &Arc<ClientHandle>) -> NodeResult<Self>;
```

---

### `impl PanelItemAcceptor`
**Repo:** stardust-core | **File:** fusion/src/items.rs | **Language:** Rust

Accept panel items (Wayland windows) into your 3D space.

```rust
pub fn create(client: &Arc<ClientHandle>, parent: &impl SpatialRefAspect,
              field: &impl FieldAspect) -> NodeResult<Self>;
```

---

## 11.6 Flatland — Wayland Panel Shell

### `struct PanelWrapper<State>`
**Repo:** stardust-flatland | **File:** src/panel_wrapper.rs | **Language:** Rust

**Event Hooks:**
- `on_toplevel_title_changed(f)` — Window title changed
- `on_toplevel_size_changed(f)` — Window resized
- `on_toplevel_move_request(f)` — Window wants to move
- `on_set_cursor(f)` — Cursor appearance changed
- `on_create_child(f)` — Child surface (popup) created

---

### `struct PointerPlane<State>`
**Repo:** stardust-flatland | **File:** src/pointer_plane.rs | **Language:** Rust

- `on_mouse_button(f: Fn(&mut State, u32, bool))` — Mouse button events
- `on_pointer_motion(f: Fn(&mut State, Vector3<f32>))` — Pointer movement
- `on_scroll(f: Fn(&mut State, MouseEvent))` — Scroll events

---

### `struct TouchPlane<State>`
**Repo:** stardust-flatland | **File:** src/touch_plane.rs | **Language:** Rust

- `on_touch_down(f: Fn(&mut State, u32, Vector3<f32>))` — Touch start
- `on_touch_move(f: Fn(&mut State, u32, Vector3<f32>))` — Touch move
- `on_touch_up(f: Fn(&mut State, u32))` — Touch end

---

### `struct GrabBall<H: GrabBallHead>`
**Repo:** stardust-flatland | **File:** src/grab_ball.rs | **Language:** Rust

3D handle for repositioning panels in space.

- `create(head, offset, ...) -> Self`
- `update(&mut self)` — Process input
- `pos(&self) -> &Vec3` — Current position
- `set_enabled(&mut self, enabled: bool)`

---

## 11.7 Protostar — App Launchers

### `struct Application`
**Repo:** stardust-protostar | **File:** src/application.rs | **Language:** Rust

```rust
pub fn create(desktop_file: DesktopFile) -> Result<Self>;
pub fn name(&self) -> Option<&str>;
pub fn categories(&self) -> &[String];
pub fn icon(&self, preferred_px_size: u16, prefer_3d: bool) -> Option<Icon>;
pub fn launch<T: SpatialRefAspect + Clone>(&self, launch_space: &T) -> NodeResult<()>;
```

---

### `struct DesktopFile`
**Repo:** stardust-protostar | **File:** src/desktop_file.rs | **Language:** Rust

```rust
pub fn parse(path: PathBuf) -> Result<Self, String>;
pub fn get_icon(&self, preferred_px_size: u16) -> Option<Icon>;
```

---

### `pub fn get_desktop_files() -> impl Iterator<Item = PathBuf>`
**Repo:** stardust-protostar | **File:** src/desktop_file.rs | **Language:** Rust

Scan XDG data directories for .desktop files.

---

### `struct Hex { q: isize, r: isize, s: isize }`
**Repo:** stardust-protostar | **File:** src/hex.rs | **Language:** Rust

Hexagonal coordinate system for the hex-grid app launcher.

- `pub fn new(q, r, s) -> Self`
- `pub fn get_coords(&self) -> [f32; 3]` — 3D position
- `pub fn neighbor(self, direction: usize) -> Self`
- `pub fn spiral(i: usize) -> Self` — i-th position in spiral layout

---

## 11.8 StardustXR Wire Protocol

### `pub async fn connect() -> Result<UnixStream, std::io::Error>`
**Repo:** stardust-core | **File:** wire/src/lib.rs | **Language:** Rust

Connect to the StardustXR server via Unix domain socket.

### `pub fn serialize<S: Serialize>(value: &S) -> Result<(Vec<u8>, Vec<OwnedFd>), FlexSerializeError>`
**Repo:** stardust-core | **File:** wire/src/flex/mod.rs | **Language:** Rust

Serialize data with FlexBuffers, supporting file descriptor passing.

### `pub fn deserialize<'a, T: Deserialize<'a>>(data: &'a [u8], fds: impl IntoIterator<Item=OwnedFd>) -> Result<T>`
**Repo:** stardust-core | **File:** wire/src/flex/mod.rs | **Language:** Rust

Deserialize FlexBuffer data with file descriptor reconstruction.

---

## 11.9 Gluon D-Bus Registry

### `impl ObjectRegistry`
**Repo:** stardust-core | **File:** gluon/src/lib.rs | **Language:** Rust

```rust
pub async fn new(connection: &Connection) -> Arc<Self>;
pub fn get_objects(&self, interface: &str) -> HashSet<ObjectInfo>;
pub fn get_watch(&self) -> watch::Receiver<Objects>;
pub fn query<Q, Ctx>(self: &Arc<Self>, context: impl Into<Arc<Ctx>>) -> QueryStream<Q, Ctx>;
```

**D-Bus Traits:**
- `SpatialRef { fn node() -> u64; fn get_transform(); fn set_transform(); }`
- `FieldRef { fn node() -> u64; fn distance(); fn normal(); fn closest_point(); }`
- `PlaySpace { fn bounds() -> Vec<(f64,f64)>; fn center() -> (f64,f64,f64); }`

---

# 12. Geo/Maps Intelligence (Overpass, Gemini)

## 12.1 Overpass API (OpenStreetMap)

### `class Overpass`
**Repo:** overpass-turbo | **File:** js/overpass.ts | **Language:** TypeScript

Main query engine for OpenStreetMap data.

**Query Languages:** OverpassQL, XML, SQL (PostGIS-compatible)

**Handlers:**
```typescript
handlers: {
    onProgress, onDone, onEmptyMap, onDataReceived,
    onAbort, onAjaxError, onQueryError, onStyleError,
    onQueryErrorLine, onRawDataPresent, onGeoJsonReady, onPopupReady
}
```

**API Endpoints:**
- `{server}interpreter` — Main query endpoint (POST)
- `{server}kill_my_queries` — Abort running queries
- `{server}status` — Server status

**Example:**
```typescript
overpass.handlers["onDataReceived"] = (data, type) => {
    console.log('Received:', data);
};
overpass.run_query('[out:json];node["amenity"="cafe"]({{bbox}});out;');
```

---

### `function ffs_construct_query(search, callback, ...)`
**Repo:** overpass-turbo | **File:** js/ffs.ts | **Language:** TypeScript

Build an Overpass query from natural language search using OSM tag presets.

---

### `function ffs_repair_search(search, callback)`
**Repo:** overpass-turbo | **File:** js/ffs.ts | **Language:** TypeScript

Attempt to repair an invalid search query.

---

### `function autorepair(q, lng)`
**Repo:** overpass-turbo | **File:** js/autorepair.ts | **Language:** TypeScript

Automatically fix common Overpass query errors (missing recurse statements, output format, geometry modes).

---

### Template Shortcuts
**Repo:** overpass-turbo | **File:** js/shortcuts.ts | **Language:** TypeScript

Mustache-style templates for dynamic queries:
- `{{bbox}}` — Map bounding box
- `{{center}}` — Map center coordinates
- `{{date:offset}}` — Relative date (e.g., `{{date:-1day}}`)
- `{{geocodeArea:name}}` — Area from Nominatim geocoding
- `{{geocodeCoords:name}}` — Coordinates from Nominatim

---

## 12.2 Gemini Maps Grounding

### Python SDK
**Language:** Python

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model='gemini-3-flash-preview',
    contents="Find Italian restaurants nearby",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_maps=types.GoogleMaps())],
        tool_config=types.ToolConfig(
            retrieval_config=types.RetrievalConfig(
                lat_lng=types.LatLng(latitude=34.05, longitude=-118.25)
            )
        ),
    ),
)

# Access grounding metadata
for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
    print(f'{chunk.maps.title}: {chunk.maps.uri}')
```

**Response Fields:**
- `groundingChunks[].maps.uri` — Google Maps link
- `groundingChunks[].maps.title` — Place name
- `groundingChunks[].maps.placeId` — Google Place ID
- `groundingSupports[].segment` — Text spans linked to sources
- `googleMapsWidgetContextToken` — For rendering interactive widget

---

## 12.3 AR Glasses Geo Integration Patterns

### Overpass API for POI Overlay
```typescript
async function getArPois(lat: number, lng: number, radius: number = 200) {
    const query = `
        [out:json][timeout:10];
        (node["amenity"](around:${radius},${lat},${lng});
         node["shop"](around:${radius},${lat},${lng});
         node["tourism"](around:${radius},${lat},${lng}););
        out body;
    `;
    const response = await fetch('https://overpass-api.de/api/interpreter', {
        method: 'POST', body: `data=${encodeURIComponent(query)}`
    });
    return response.json();
}
```

### Gemini Maps for Contextual Questions
```typescript
async function askAboutLocation(question: string, lat: number, lng: number) {
    const response = await fetch(
        'https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent',
        {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'x-goog-api-key': API_KEY},
            body: JSON.stringify({
                contents: [{parts: [{text: question}]}],
                tools: {googleMaps: {enableWidget: true}},
                toolConfig: {retrievalConfig: {latLng: {latitude: lat, longitude: lng}}}
            })
        }
    );
    return response.json();
}
```

---

## 12.4 Open Wearables MCP Server

### `get_users(search?, limit=10) -> dict`
**Repo:** open-wearables | **File:** mcp/app/tools/users.py | **Language:** Python

Discover users accessible via API key.

---

### `get_activity_summary(user_id, start_date, end_date) -> dict`
**Repo:** open-wearables | **File:** mcp/app/tools/activity.py | **Language:** Python

Daily activity data: steps, calories, heart rate, intensity minutes.

---

### `get_sleep_summary(user_id, start_date, end_date) -> dict`
**Repo:** open-wearables | **File:** mcp/app/tools/sleep.py | **Language:** Python

Sleep data for a date range.

---

### `get_workout_events(user_id, start_date, end_date) -> dict`
**Repo:** open-wearables | **File:** mcp/app/tools/workouts.py | **Language:** Python

Workout/exercise session data.

---

### `get_timeseries(user_id, series_type, start_date, end_date) -> dict`
**Repo:** open-wearables | **File:** mcp/app/tools/timeseries.py | **Language:** Python

Granular time-series: weight, SpO2, HRV, intraday heart rate, etc.

---

### Sleep Scoring Algorithms
**Repo:** open-wearables | **File:** backend/algorithms/sleep.py | **Language:** Python

- `calculate_duration_score(start, end, awake_minutes) -> int`
- `calculate_total_stages_score(deep_minutes, rem_minutes) -> int`
- `calculate_bedtime_consistency_score(...) -> int`
- `calculate_interruptions_score(...) -> int`
- `calculate_overall_sleep_score(duration, stages, bedtime, interruptions) -> int`

### HRV Algorithms
**Repo:** open-wearables | **File:** backend/algorithms/resilience.py | **Language:** Python

- `hr_to_rr_intervals_ms(hr_series) -> ndarray`
- `calculate_rmssd(hr_series) -> float` — Root Mean Square of Successive Differences
- `calculate_sdnn(hr_series) -> float` — Standard Deviation of NN intervals
- `calculate_hrv_cv(hrv_series) -> float` — HRV Coefficient of Variation

---

# Appendix A: Vendor SDK Reference (Native APIs)

## A.1 RayNeo Native SDK
```c
void RegisterIMUEventCallback(IMUEventCallback callback);
int EstablishUsbConnection(int32_t vid, int32_t pid);
void StartXR(); void StopXR();
void SwitchTo2D(); void SwitchTo3D();
void OpenIMU(); void CloseIMU();
void Recenter();
void GetHeadTrackerPose(float rotation[4], float position[3], uint64_t* timeNsInDevice);
bool GetSideBySideStatus();
```

## A.2 VITURE Native SDK
```c
XRDeviceProviderHandle xr_device_provider_create(int product_id, int fd, int bus, int dev);
int xr_device_provider_initialize(XRDeviceProviderHandle handle, const char* config);
int xr_device_provider_start(XRDeviceProviderHandle handle);
int xr_device_provider_stop(XRDeviceProviderHandle handle);
int xr_device_provider_shutdown(XRDeviceProviderHandle handle);
void xr_device_provider_destroy(XRDeviceProviderHandle handle);
int register_raw_callback(XRDeviceProviderHandle handle, VitureImuRawCallback cb);
int register_pose_callback(XRDeviceProviderHandle handle, VitureImuPoseCallback cb);
int open_imu(XRDeviceProviderHandle handle, uint8_t mode, uint8_t freq);
int close_imu(XRDeviceProviderHandle handle, uint8_t mode);
```

## A.3 Rokid Native SDK
```c
GlassWaitEvent(); // 90Hz IMU with GAME_ROTATION_EVENT
```

## A.4 XREAL HID Protocol
```
Vendor ID: 0x3318
Product IDs: 0x0424 (Air), 0x0428 (Air 2), 0x0432 (Air 2 Pro), 0x0426 (Air 2 Ultra)
IMU: 1000Hz native via HID reports
Display: USB-C DisplayPort Alt Mode
```

---

# Appendix B: XRLinuxDriver Plugin System

## B.1 Plugin Interface
```c
struct plugin_t {
    char* id;
    start_func start;
    default_config_func default_config;
    handle_config_line_func handle_config_line;
    set_config_func set_config;
    setup_ipc_func setup_ipc;
    modify_reference_pose_func modify_reference_pose;
    modify_pose_func modify_pose;
    handle_pose_data_func handle_pose_data;
    handle_device_connect_func handle_device_connect;
    handle_device_disconnect_func handle_device_disconnect;
};
```

## B.2 Registered Plugins (11 total)
1. **device_license** — License key management
2. **virtual_display** — Head-locked virtual screen + IPC
3. **sideview** — Follow-mode display
4. **metrics** — Usage telemetry
5. **custom_banner** — Overlay banner
6. **smooth_follow** — Slerp-based screen follow (configurable thresholds)
7. **breezy_desktop** — Wayland compositor integration via /dev/shm
8. **gamescope_reshade_wayland** — SteamOS shader injection
9. **neck_saver** — Ergonomic posture alerts
10. **opentrack_source** — Sends UDP: 6 doubles (x,y,z,yaw,pitch,roll) + frame#
11. **opentrack_listener** — Receives OpenTrack UDP as synthetic IMU device

---

# Appendix C: Protocol Reference

## C.1 OpenTrack UDP Protocol
```
Target: configurable IP:port (default 127.0.0.1:4242)
Payload: 48 bytes = 6 × double (little-endian)
  [0] x, [1] y, [2] z, [3] yaw, [4] pitch, [5] roll
```

## C.2 XREAL Air HID Protocol (v3)
```
NREAL_VENDOR_ID = 0x3318
BOOT_PRODUCT_ID = 0x0423
Commands: cmd_build(msgId, payload) -> HID packet
Response: parse_rsp(rsp) -> parsed packet
```

## C.3 XREAL Light HID Protocol
```
NREAL_VENDOR_ID = 0x0486
BOOT_PRODUCT_ID = 0x573C
```

## C.4 Breezy Desktop IPC Binary Protocol
```
File: /dev/shm/breezy_desktop_imu
Layout version 5: config header + IMU record with parity byte
Config: version, enabled, look_ahead[4], display_res[2], fov, lens_ratio, sbs, banner
IMU: smooth_follow_enabled, orientation[16], position[3], epoch_ms, parity
```

## C.5 StardustXR Wire Protocol
```
Transport: Unix domain sockets with FD passing (SCM_RIGHTS)
Header: 4 bytes (u32 body_length)
Body: FlatBuffers message
Message types: Error(0), Signal(1), MethodCall(2), MethodReturn(3)
Fields: type_, message_id, node_id, aspect, method, error, data
```

## C.6 BeatSync NTP-inspired Sync Protocol
```
1. Client sends NTP_REQUEST with t0
2. Server stamps t1 (receive), t2 (send)
3. Client receives at t3
4. RTT = (t3-t0) - (t2-t1)
5. Offset = ((t1-t0) + (t2-t3)) / 2
6. EMA smoothing (alpha=0.2) for RTT
7. Min 10 measurements before "synced"
8. Play/pause = scheduled actions with serverTimeToExecute
```

---

# Appendix D: Cross-Reference Tables

## D.1 SDK-to-Use-Case Matrix

| Use Case | SDK/Repo | Language | Platform |
|----------|----------|----------|----------|
| Universal glasses app | xg-glass-sdk | Kotlin | Android |
| Cloud-connected glasses app | MentraOS SDK | TypeScript | Server |
| Linux head tracking | XRLinuxDriver | C | Linux |
| IMU sensor fusion | Fusion | C/Python | Any |
| AR web browser | TAPLINKX3 | Kotlin | RayNeo |
| PC desktop streaming | RayDesk | Kotlin | RayNeo |
| Windows head tracking | PhoenixHeadTracker | C# | Windows |
| Spatial XR compositor | StardustXR | Rust | Linux |
| Rust glasses abstraction | headset-utils | Rust | Linux |
| 3DOF streaming server | spidgets-3dof | JavaScript | Node.js |
| Video segmentation | SAM3 | Python | GPU |
| OSM geospatial queries | overpass-turbo | TypeScript | Web |
| Health data access | open-wearables | Python | Server |
| Smart ring companion | mobileapp | Kotlin KMP | iOS/Android |
| Steam Deck XR | decky-XRGaming | TS/Python | SteamOS |

## D.2 Glasses Protocol Compatibility

| Glasses | Protocol | Interface | VID:PID |
|---------|----------|-----------|---------|
| XREAL Air | HID v3 | USB/WebHID | 0x3318:0x0424 |
| XREAL Air 2 | HID v3 | USB | 0x3318:0x0428 |
| XREAL Air 2 Ultra | HID v3 + SLAM | USB | 0x3318:0x0426 |
| XREAL Light | HID | USB/WebHID | 0x0486:0x573C |
| RayNeo X2/X3 | OpenXR ARDK | Unity/Android | 0x1BBB:0xAF50 |
| Rokid Max/Air | CXR-M SDK | BLE+Wi-Fi | ROKID_GLASS_VID |
| VITURE One/Pro | Native SDK | USB | 0x35CA:various |
| Brilliant Frame | BLE + Lua | nRF52840 | N/A |
| Meta Ray-Ban | DAT SDK | Bluetooth | N/A |
| Omi Glass | BLE GATT | nRF52 | N/A |
| Vuzix Blade 2 | Vuzix HUD SDK | Android | N/A |
| Everysight Maverick | EvsKit | BLE | N/A |

## D.3 Supported Device Features per XRLinuxDriver

| Device | IMU Hz | FOV | SBS | 6DoF | Pitch Adj |
|--------|--------|-----|-----|------|-----------|
| XREAL Air | 1000→250 | 46° | ✔ | ✘ | 0° |
| XREAL One Pro | 1000→250 | 57° | ✔ | ✘ | 35° |
| VITURE One | 60-500 | 43° | ✔ | ✘ | 6° |
| VITURE Pro | 60-500 | 43° | ✔ | ✘ | 3° |
| VITURE Luma | 1000 | 44° | ✔ | ✔ | -8.5° |
| Rokid | 90 | 50° | ✔ | ✘ | 5° |
| RayNeo | 500→250 | 46° | ✔ | ✘ | 15° |

---

# Appendix E: MentraOS Glasses-Side Client API

## E.1 AsgClientService (Android Foreground Service)

### `class AsgClientService extends Service implements NetworkStateListener, BluetoothStateListener`
**Repo:** MentraOS | **File:** asg_client/app/src/main/java/com/mentra/asg_client/AsgClientService.java | **Language:** Java

Core foreground service (1593 lines). Uses SOLID architecture with ServiceContainer DI.

**Manager Interfaces:**
- `IServiceLifecycle` — Service lifecycle management
- `ICommunicationManager` — BLE/WiFi communication
- `IConfigurationManager` — Device configuration
- `IStateManager` — State tracking
- `IMediaManager` — Camera, video, audio

**Command Handlers (20+ types):**
- `AuthTokenCommandHandler` — Authentication
- `BatteryCommandHandler` — Battery status
- `BleConfigCommandHandler` — BLE configuration
- `GalleryCommandHandler` — Gallery management
- `I2SAudioCommandHandler` — I2S audio protocol
- `ImuCommandHandler` — IMU data streaming
- `K900CommandHandler` — K900 chip control
- `MicrophoneCommandHandler` — Mic enable/disable
- `OtaCommandHandler` — OTA firmware updates
- `PhotoCommandHandler` — Photo capture
- `PingCommandHandler` — Heartbeat

---

## E.2 MentraOS Mobile Module API (React Native)

### `CoreModule` — TypeScript Interface
**Repo:** MentraOS | **File:** mobile/modules/core/src/CoreModule.ts | **Language:** TypeScript

```typescript
// Connection
getGlassesStatus(): GlassesStatus
getCoreStatus(): CoreStatus
connectDefault(): void
connectByName(deviceName: string): void
connectSimulated(): void
disconnect(): void
forget(): void
findCompatibleDevices(deviceModel: string): void
ping(): void

// Display
displayEvent(params: DisplayEventParams): void
displayText(params: DisplayTextParams): void
clearDisplay(): void

// Network
requestWifiScan(): void
sendWifiCredentials(ssid: string, password: string): void
setHotspotState(enabled: boolean): void

// Camera & Media
photoRequest(requestId, appId, size, webhookUrl, authToken, compress, flash, sound): void
startBufferRecording(): void
stopBufferRecording(): void
saveBufferVideo(requestId, durationSeconds): void
startVideoRecording(requestId, save, flash, sound): void
stopVideoRecording(requestId): void

// Streaming
startStream(params: StreamParams): void
stopStream(): void
keepStreamAlive(params: KeepAliveParams): void

// Audio
setMicState(sendPcmData, sendTranscript, bypassVad): void
restartTranscriber(): void
getGlassesMediaVolume(): void
setGlassesMediaVolume(level: number): void

// LED
rgbLedControl(requestId, packageName, action, color, ...): void
```

---

## E.3 MentraOS iOS Swift Drivers

### Device Drivers
**Repo:** MentraOS | **File:** mobile/modules/core/ios/Source/ | **Language:** Swift

- `G1.swift` — Even Realities G1 driver
- `G2.swift` — Even Realities G2 driver
- `Mach1.swift` — Mentra Mach 1 driver
- `MentraLive.swift` — Mentra Live driver
- `MentraNex.swift` — Mentra Nex driver
- `Frame.swift` — Brilliant Labs Frame driver
- `Simulated.swift` — Simulated glasses driver

### `CoreManager.swift` — Main Bridge Manager
- Manages device lifecycle, BLE scanning, connection state
- Bridges to React Native via NativeModule

### `SherpaOnnxTranscriber.swift` — On-Device STT
- On-device speech-to-text using Sherpa-ONNX
- No cloud dependency for transcription

### `SileroVAD.swift` — Voice Activity Detection
- Silero VAD model for detecting speech vs silence
- Used to filter microphone input

---

## E.4 MentraOS WebView Bridge SDK

### `class Bridge`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/webview/index.ts | **Language:** TypeScript

Communication bridge between on-glasses WebView and React Native host.

```typescript
class Bridge {
    send(message: OutgoingMessage): void;
    subscribe(type: SubscriptionType, handler: SubscriptionHandler): () => void;
}
```

### `class CoreModule`
```typescript
class CoreModule {
    displayText(args: DisplayTextArgs): void;
    setMicState(enabled: boolean): void;
}
```

### `class Events`
```typescript
class Events {
    onTranscription(handler: (text: string) => void): () => void;
    onMovement(handler: (data: MovementPayload) => void): () => void;
}
```

### `class SocketBridge`
```typescript
class SocketBridge {
    connect(url: string): void;
    disconnect(): void;
    onAudio(handler: (audio: ArrayBuffer) => void): () => void;
    onConnection(handler: (connected: boolean) => void): () => void;
}
```

---

## E.5 MentraOS Device Capabilities

Capabilities differ per glasses model:

| Feature | G1 | G2 | Mach 1 | Mentra Live | Vuzix Z100 |
|---------|----|----|--------|-------------|------------|
| Display | ✔ | ✔ | ✔ | ✔ | ✔ |
| Camera | ✘ | ✔ | ✔ | ✔ | ✔ |
| Microphone | ✔ | ✔ | ✔ | ✔ | ✔ |
| Speaker | ✔ | ✔ | ✔ | ✔ | ✔ |
| Touch | ✔ | ✔ | ✘ | ✘ | ✘ |
| IMU | ✔ | ✔ | ✔ | ✔ | ✘ |
| LED | ✘ | ✔ | ✘ | ✔ | ✘ |

---

## E.6 MentraOS Stream Types

```typescript
enum StreamType {
    TRANSCRIPTION, TRANSLATION, HEAD_POSITION, BUTTON_PRESS,
    PHONE_NOTIFICATION, GLASSES_BATTERY, PHONE_BATTERY,
    GLASSES_CONNECTION_STATE, LOCATION, AUDIO, VAD,
    CALENDAR_EVENT, TOUCH_EVENT, PHOTO
}

enum LayoutType {
    TEXT_WALL, DOUBLE_TEXT_WALL, DASHBOARD_CARD,
    REFERENCE_CARD, BITMAP_VIEW
}

enum DashboardMode { SYSTEM, CONTENT }

enum PermissionType { MICROPHONE, LOCATION, CAMERA, NOTIFICATIONS }

enum AppType { /* app classification */ }
enum AppSettingType { /* setting types */ }
```

---

# Appendix F: RayDesk Streaming API Details

## F.1 MoonlightBridge

### `class MoonlightBridge(context: Context, decoderSurface: SurfaceProvider)`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/streaming/MoonlightBridge.kt | **Language:** Kotlin

Core integration with Moonlight streaming protocol.

**Methods:**
| Method | Description |
|--------|-------------|
| `initializeDecoder(width, height, format) -> Boolean` | Init hardware decoder |
| `setStreamConfig(config: StreamConfig)` | Configure stream parameters |
| `connect(address, port, uniqueId, ...) -> Boolean` | Connect to server |
| `disconnect()` | End stream |
| `release()` | Free resources |
| `isStreaming() -> Boolean` | Check stream state |
| `isHevcSupported() -> Boolean` | HEVC decoder available |
| `isAv1Supported() -> Boolean` | AV1 decoder available |
| `sendAbsolutePosition(x, y, refW, refH)` | Send cursor position |
| `centerCursor(refW, refH)` | Center cursor on screen |
| `sendMouseMove(dx, dy)` | Send relative mouse move |
| `sendMouseClick(button)` | Send mouse click |
| `sendKeyboard(keyCode, pressed)` | Send keyboard event |
| `sendScroll(dx, dy)` | Send scroll event |
| `quitExistingSession(address, port, ...) -> Boolean` | Kill stale sessions |
| `connectToSavedServer(server: SavedServer) -> Boolean` | Auto-connect |

---

## F.2 StreamConfig

```kotlin
data class StreamConfig(
    val width: Int = 1920,
    val height: Int = 1080,
    val fps: Int = 60,
    val bitrate: Int = 20000,   // kbps
    val audioEnabled: Boolean = true
)
```

---

## F.3 StreamState

```kotlin
sealed class StreamState {
    object Disconnected : StreamState()
    object Connecting : StreamState()
    object Pairing : StreamState()
    data class Streaming(val width: Int, val height: Int) : StreamState()
    data class Error(val message: String) : StreamState()
}
```

---

## F.4 Server Discovery

### `class ServerDiscoveryManager`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/streaming/ServerDiscoveryManager.kt | **Language:** Kotlin

mDNS-based discovery of Moonlight/Sunshine streaming servers on local network.

### `class ReconnectionManager`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/streaming/ReconnectionManager.kt | **Language:** Kotlin

Auto-reconnect with exponential backoff.

---

## F.5 GL Rendering Pipeline

### `class GLTextureRenderer`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/video/GLTextureRenderer.kt | **Language:** Kotlin

GL render loop on TextureView, compositing decoded video with environment.

### `class VideoTextureProvider`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/video/VideoTextureProvider.kt | **Language:** Kotlin

Provides OES texture from hardware video decoder.

### `class FrameSlot`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/video/FrameSlot.kt | **Language:** Kotlin

Lock-free frame exchange between decoder and renderer threads.

### `class TestPatternGenerator`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/video/TestPatternGenerator.kt | **Language:** Kotlin

Generates test patterns for debugging display pipeline.

---

## F.6 Environment Themes

```kotlin
data class EnvironmentTheme(
    val name: String,
    val skyColor: Int,
    val statusRingColor: Int,
    val dashboardColor: Int,
    val frameColor: Int
)
```

Built-in themes defined in `EnvironmentThemes.kt`.

---

# Appendix G: Encryption & Security (Pebble Ring)

## G.1 AES-GCM Cryptography

### `actual object AesGcmCrypto`
**Repo:** mobileapp | **File:** ring/encryption/AesGcmCrypto.kt | **Language:** Kotlin (KMP)

Platform-specific AES-GCM encrypt/decrypt.

```kotlin
actual fun encrypt(plaintext: ByteArray, keyBase64: String): ByteArray
actual fun decrypt(ivAndCiphertext: ByteArray, keyBase64: String): ByteArray
actual fun keyFingerprint(keyBase64: String): String
```

---

### `actual class EncryptionKeyManager`
**Repo:** mobileapp | **File:** ring/encryption/EncryptionKeyManager.kt | **Language:** Kotlin (KMP)

Key generation and storage with iCloud Keychain support.

```kotlin
actual fun generateKey(): KeyResult
actual suspend fun saveKeyLocally(key: String, email: String)
actual suspend fun getLocalKey(email: String): String?
actual suspend fun saveToCloudKeychain(uiContext: Any, key: String)
actual suspend fun readFromCloudKeychain(uiContext: Any): String?
```

---

### `class DocumentEncryptor`
**Repo:** mobileapp | **File:** ring/encryption/DocumentEncryptor.kt | **Language:** Kotlin

Wrapper for encrypting/decrypting recording documents using AES-GCM.

---

# Appendix H: Frame Firmware Low-Level APIs

## H.1 Flash Storage

```c
void flash_erase_page(uint32_t address);
void flash_write(uint32_t address, const uint32_t* data, size_t length);
void flash_wait_until_complete(void);
void flash_get_info(size_t* page_size, size_t* total_size);
uint32_t flash_base_address(void);
```

## H.2 SPI Bus

```c
void spi_configure(void);
void spi_read(spi_device_t device, uint8_t* tx, uint8_t* rx, size_t len);
void spi_write(spi_device_t device, uint8_t* tx, size_t len);
```

## H.3 Compression

```c
int compression_decompress(size_t dst_size, const uint8_t* src, ...);
```

## H.4 Experiment Utilities (ML on Frame)

```c
int jpeg_decode_grayscale_scaled(const uint8_t* data, size_t size, ...);
int jpeg_decode_grayscale(const uint8_t* data, size_t size, ...);
void upscale_90_to_96_with_rotation(const uint8_t* src, uint8_t* dst);
int jpeg_decode_rgb_scaled(const uint8_t* data, size_t size, ...);
void upscale_90_to_96_rgb_with_rotation(const uint8_t* src, uint8_t* dst);
const char* experiment_get_name(void);
void experiment_register_lua_functions(lua_State* L, int table);
void lua_open_experiment_library(lua_State* L);
```

## H.5 System Lua API

```lua
frame.update()              -- Process pending events
frame.sleep(seconds)        -- Sleep for duration
frame.stay_awake(enable)    -- Prevent auto-sleep
frame.battery_level()       -- Read battery percentage
frame.fpga_read(addr, len)  -- Read FPGA register
frame.fpga_write(addr, data)-- Write FPGA register

-- Time
frame.time.utc()            -- UTC timestamp
frame.time.zone()           -- Timezone offset
frame.time.date()           -- Date string

-- File (LittleFS)
frame.file.open(path, mode)     -- Open file
frame.file.read(handle, bytes)  -- Read bytes
frame.file.write(handle, data)  -- Write data
frame.file.close(handle)        -- Close file
frame.file.remove(path)         -- Delete file
frame.file.rename(old, new)     -- Rename file
frame.file.mkdir(path)          -- Create directory
frame.file.listdir(path)        -- List directory
frame.file.require(module)      -- Load Lua module

-- LED
frame.led.set_color(r, g, b)   -- Set LED color

-- IMU
frame.imu                       -- Callback-based sensor data

-- ML Experiment
frame.experiment.run_person_detection()  -- Run VWW model
```

## H.6 FPGA Camera Pipeline

```c
// fpga_application.h
// Camera pipeline running on FPGA fabric
// Handles image capture, processing, and transfer to MCU
```

## H.7 Radio Test Suite

```c
// radio_test.c / radio_test.h
// RF test suite for nRF52840
// Used in manufacturing for BLE radio verification
```

---

# Appendix I: spidgets-3dof Server API

## I.1 Server (ar-server.js)

### Socket.IO Events (server → client)
- `'cam'` — Camera Euler angles [x, y, z]
- `'camstart'` — Initial camera position on connect

### Socket.IO Events (client → server)
- `'tare'` — Recalibrate zero position

### Functions
```javascript
emit(event, data)                   // Broadcast to all clients
broadcastCam(x, y, z, first)       // Send camera update
calibrate()                         // Tare/zero position
```

### CLI Options
```
--port <number>     Server port (default 3000)
--drift <float>     Drift compensation rate
```

## I.2 Client (webroot/app.js)

### Alpine.js Store 'app'
- `x, y, z` — Current rotation in degrees

### Functions
```javascript
initCamera(yaw, firstConnect)      // Set initial camera
setCamera(vecArr)                  // Update camera from socket
```

## I.3 Widget API
```javascript
class ChartWidget extends window.spidgets.SDiv { ... }
class WeatherWidget extends window.spidgets.SDiv { ... }
```

---

# Appendix J: C++ XREAL HID Protocol (real_utilities)

## J.1 Protocol v1 — Control Interface

```cpp
class protocol {
    struct parsed_rsp {
        uint16_t msgId;
        uint8_t status;
        uint8_t payload[200];
        uint16_t payload_size;
    };

    static void listKnownCommands();
    static std::string keyForHex(uint16_t hex);
    static uint16_t hexForKey(std::string key);
    static void parse_rsp(const uint8_t* buffer, int size, parsed_rsp* result);
    static int cmd_build(uint16_t msgId, const uint8_t* p, int p_size,
                         uint8_t* cmd_buf, int cb_size);
    static int cmd_build(std::string msg_id, const uint8_t* p, int p_size,
                         uint8_t* cmd_buf, int cb_size);
    static void print_summary_rsp(parsed_rsp* result);
};
```

## J.2 Protocol v3 — IMU Interface

```cpp
class protocol3 {
    struct parsed_rsp {
        uint8_t msgId;
        uint8_t payload[200];
        uint16_t payload_size;
    };

    static void listKnownCommands();
    static std::string keyForHex(uint8_t hex);
    static uint8_t hexForKey(std::string key);
    static void parse_rsp(const uint8_t* buffer, int size, parsed_rsp* result);
    static int cmd_build(uint8_t msgId, const uint8_t* p, int p_size,
                         uint8_t* cmd_buf, int cb_size);
};
```

## J.3 Main Program Functions

```cpp
hid_device* open_device(int interface_num);       // Open HID by interface
void print_bytes(const uint8_t* buf, int size);   // Hex dump

int write_control(hid_device*, uint16_t msgId, const uint8_t* p, int p_size);
int write_control(hid_device*, std::string msg_id, const uint8_t* p, int p_size);
protocol::parsed_rsp read_control(hid_device*, int timeout_ms);

int write_imu(hid_device*, uint8_t msgId, const uint8_t* p, int p_size);
protocol3::parsed_rsp read_imu(hid_device*, int timeout_ms);
void read_imu_get_rsp(hid_device*, int timeout_ms, protocol3::parsed_rsp* out);
```

---

# Appendix K: imu-inspector (C)

```c
void fix_report();                                // Fix/normalize raw HID report
void print_report();                              // Pretty-print parsed IMU data
void print_bytes(const uint8_t* buf, size_t len); // Hex dump
void print_line(const char* s);                   // Formatted output
hid_device* open_device();                        // Open XREAL HID device
int main(void);                                   // Entry: open device, read loop
```

---

# Appendix L: SAM3 Visualization Utilities

```python
generate_colors(n_colors=256)
show_img_tensor(img_batch, vis_img_idx=0)
draw_box_on_image(image, box, color)
plot_bbox(image, bboxes, labels, scores, ...)
plot_mask(mask, color, ax)
visualize_frame_output(frame_idx, video_frames, outputs)
render_masklet_frame(img, outputs, frame_idx, alpha)
save_masklet_video(video_frames, outputs, out_path, alpha, fps)
save_masklet_image(frame, outputs, out_path, alpha)
```

---

# Appendix M: BeatSync WebSocket Protocol (Complete)

## M.1 Client → Server (WSRequest)

| Type | Description | Key Fields |
|------|-------------|------------|
| PLAY | Request synced play | serverTimeToExecute |
| PAUSE | Request pause | serverTimeToExecute |
| NTP_REQUEST | Time sync | t0 |
| MOVE_CLIENT | Move position (spatial) | position: {x, y} |
| SYNC | Request state sync | — |
| SET_PLAYBACK_CONTROLS | Admin permissions | adminOnly: boolean |
| SEARCH_MUSIC | Search external | query: string |
| STREAM_MUSIC | Start stream | url: string |
| SET_GLOBAL_VOLUME | Master volume | volume: number |
| SEND_CHAT_MESSAGE | Chat | message: string |
| AUDIO_SOURCE_LOADED | Confirm ready | sourceId: string |
| REORDER_AUDIO_SOURCES | Reorder playlist | order: string[] |
| SET_METRONOME | Configure click | bpm, volume |
| SET_LOW_PASS_FREQ | Filter | frequency: number |
| SET_LISTENING_SOURCE | Spatial position | sourceId: string |
| START_SPATIAL_AUDIO | Enable spatial | — |
| STOP_SPATIAL_AUDIO | Disable spatial | — |
| LOAD_DEFAULT_TRACKS | Preset tracks | — |
| REORDER_CLIENT | Reorder position | order: string[] |
| SET_ADMIN | Promote/demote | userId, isAdmin |
| DELETE_AUDIO_SOURCES | Remove sources | sourceIds: string[] |
| SEND_IP | Client IP | ip: string |

## M.2 Server → Client (WSBroadcast)

| Type | Description |
|------|-------------|
| ROOM_STATE | Full room state snapshot |
| SET_AUDIO_SOURCES | Audio source list |
| CHAT_UPDATE | New messages |
| LOAD_AUDIO_SOURCE | Load audio request |
| SPATIAL_CONFIG | Spatial gain config |
| STOP_SPATIAL_AUDIO | Spatial stopped |
| GLOBAL_VOLUME_CONFIG | Volume update |
| METRONOME_CONFIG | Metronome update |
| LOW_PASS_CONFIG | Filter update |
| STREAM_JOB_UPDATE | Stream progress |
| SCHEDULED_ACTION | Synced play/pause |
| DEMO_USER_COUNT | Demo mode users |
| DEMO_AUDIO_READY_COUNT | Ready count |

## M.3 Server → Single Client (WSUnicast)

| Type | Description |
|------|-------------|
| NTP_RESPONSE | Time sync response (t0, t1, t2) |
| MUSIC_SEARCH_RESPONSE | Search results |

## M.4 HTTP Endpoints

```
POST /upload/get-presigned-url    — Get R2 presigned upload URL
POST /upload/complete             — Confirm upload complete
GET  /rooms                       — List active rooms
GET  /rooms/discover              — Discover rooms
```

---

# Appendix N: Open Wearables Backend API

## N.1 REST API Routes

```
Auth:
  POST /auth/login           — Login → JWT
  POST /auth/logout          — Logout
  POST /auth/change-password — Change password
  GET  /auth/me              — Current developer
  PUT  /auth/me              — Update developer

Users:
  GET    /users              — List (paginated)
  GET    /users/{id}         — Get user
  POST   /users              — Create
  DELETE /users/{id}         — Delete
  PUT    /users/{id}         — Update

Health Data:
  GET /events/workouts       — List workouts
  GET /events/sleep          — List sleep sessions
  GET /health-scores         — List health scores
  GET /data-sources/{user_id}— User data sources

Webhooks:
  POST /webhooks/{provider}  — Provider push
  GET  /webhooks/{provider}/verify — Verify

Applications:
  GET/POST/DELETE /applications — CRUD
  POST /applications/{id}/rotate — Rotate secret

API Keys:
  GET/POST/DELETE/PUT /api-keys — CRUD
  POST /api-keys/{id}/rotate   — Rotate key
```

## N.2 Backend Models

```
User, Developer, Application, ApiKey, RefreshToken
DataSource, DataPointSeries, DataPointSeriesArchive
EventRecord, EventRecordDetail, WorkoutDetails, SleepDetails
HealthScore, PersonalRecord, SeriesTypeDefinition
UserConnection, ProviderSetting, ProviderPriority
DeviceTypePriority, ArchivalSetting
Invitation, UserInvitationCode
```

---

# Appendix O: xg-glass CLI Tool

## O.1 Commands

```bash
xg-glass init <path>     # Initialize new project from template
xg-glass build            # Build the project (assembleDebug)
xg-glass install          # Install APK to device
xg-glass run [file]       # Run app (optionally single Kotlin file)
```

## O.2 CLI Options

```
--sim                    # Use simulator device
--video_url <url>        # Download video for sim mode (via yt-dlp)
--variant <name>         # Build variant
--module <name>          # Gradle module to build
```

## O.3 Internal Functions

```python
def main(argv) -> int                  # argparse entry
def cmd_init(args)                     # Initialize project
def cmd_build(args)                    # Build project
def cmd_install(args)                  # Install to device
def cmd_run(args)                      # Run on device

# Auto-bootstrap
def _ensure_java_runtime()
def _auto_download_jdk()
def _auto_download_flutter()
def _auto_download_android_sdk()
def _resolve_android_sdk()
def _ensure_emulator_running()

# Video support
def _download_video_from_url()
def _push_video_to_device()
def _resolve_sim_video()

# Env persistence
def _persist_env_macos_zshrc()
def _persist_env_windows()

@dataclass
class XgConfig:
    sdk_path: str
    entry_class: str
    rayneo_mercury_aar_dir: str
    variant: str
    module: str
    application_id: str
```

---

*End of AR Glasses Master SDK — Complete API Reference*
*Generated from source analysis of 27+ repositories. Last updated: 2026-04-20.*
*Total documented: 500+ functions/classes/methods across 12 domains.*
