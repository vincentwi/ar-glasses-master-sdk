# AR Glasses Master SDK — Complete Enriched API Reference

> **Comprehensive API reference covering every function, class, and method across 27+ repositories.**
> Generated: 2026-04-20 | Enriched: 2026-04-20 | 700+ functions documented | 12 domains | 27 repos analyzed
> Enriched from deep-reads: RayNeo Feishu docs, Fusion AHRS, StardustXR KDL protocol, Monado headers, Geo/Maps APIs

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

**Cross-references:** `DisplayOptions`, `DisplayMode`, `RokidDisplayController.showText()`, `LayoutManager.showTextWall()` (MentraOS equivalent)

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

**Cross-references:** `RokidDisplayController.close()`, `GlassesClient.display()`

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

**Returns:** `void`

**Example:**
```typescript
session.display.showTextWall("Hello from MentraOS!");
```

**Cross-references:** `showDoubleTextWall()`, `showDashboardCard()`, `showReferenceCard()`, `showBitmapView()`, `clear()`

---

### `LayoutManager.showDoubleTextWall(topText: String, bottomText: String): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Display split-screen text with top and bottom sections.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| topText | String | Text for the top section |
| bottomText | String | Text for the bottom section |

**Returns:** `void`

---

### `LayoutManager.showDashboardCard(title: String, content: String): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Display a dashboard-style card with title and content.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| title | String | Card title |
| content | String | Card body content |

**Returns:** `void`

---

### `LayoutManager.showReferenceCard(title: String, body: String): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Display a reference card layout.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| title | String | Reference card title |
| body | String | Reference card body |

**Returns:** `void`

---

### `LayoutManager.showBitmapView(data: String, width?: number, height?: number): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Display a bitmap image on the glasses.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| data | String | Base64-encoded image data |
| width | number? | Optional width in pixels |
| height | number? | Optional height in pixels |

**Returns:** `void`

---

### `LayoutManager.clear(): void`
**Repo:** MentraOS | **File:** cloud/packages/sdk/src/app/session/layouts.ts | **Language:** TypeScript

Clear all displayed content from the glasses.

**Returns:** `void`

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

**Returns:** `void`

**Example:**
```lua
frame.display.text("Hello World", 100, 100, {color=1})
frame.display.show()  -- Must call show() to commit
```

**Cross-references:** `frame.display.show()`, `frame.display.bitmap()`, `frame.display.assign_color()`

---

### `frame.display.bitmap(x, y, width, data)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Draw a bitmap image on the Frame display.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| x | number | X position in pixels |
| y | number | Y position in pixels |
| width | number | Bitmap width in pixels |
| data | string | Raw pixel data (indexed color palette) |

**Returns:** `void`

---

### `frame.display.show()`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Commit the current display buffer to the screen. Must be called after `text()` or `bitmap()` to make changes visible.

**Returns:** `void`

**Precaution:** Without calling `show()`, display changes remain in the offscreen buffer and are not visible.

---

### `frame.display.assign_color(index, r, g, b)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Assign an RGB color to a palette index for use in text/bitmap rendering.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| index | number | Color palette index (0-15) |
| r | number | Red component (0-255) |
| g | number | Green component (0-255) |
| b | number | Blue component (0-255) |

**Returns:** `void`

**Cross-references:** `frame.display.assign_color_ycbcr()`

---

### `frame.display.assign_color_ycbcr(index, y, cb, cr)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Assign a YCbCr color to a palette index.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| index | number | Color palette index (0-15) |
| y | number | Luminance component |
| cb | number | Blue-difference chroma component |
| cr | number | Red-difference chroma component |

**Returns:** `void`

---

### `frame.display.set_brightness(level)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Set the display brightness level.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| level | number | Brightness level |

**Returns:** `void`

---

### `frame.display.power_save(enable)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Enable or disable display power saving mode.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| enable | boolean | true to enable power saving, false to disable |

**Returns:** `void`

---

### `frame.display.write_register(addr, value)`
**Repo:** frame-codebase | **File:** source/application/lua_libraries/display.c | **Language:** C (Lua binding)

Write directly to a display controller register (advanced/debug).

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| addr | number | Register address |
| value | number | Value to write |

**Returns:** `void`

**Precaution:** Direct register writes can destabilize the display. Use for debugging only.

---

## 1.4 Vuzix Blade 2 HUD Display

### `ActionMenuActivity.onCreateActionMenu(Menu menu) -> boolean`
**Repo:** Blade_2_Template_App | **File:** app/src/main/java/.../center_content_template_activity.java | **Language:** Java

Create the HUD action menu. Override to inflate your menu resource.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| menu | Menu | Android Menu object to inflate into |

**Returns:** `boolean` — true if menu was created successfully

**Example:**
```java
@Override
protected boolean onCreateActionMenu(Menu menu) {
    getMenuInflater().inflate(R.menu.main_menu, menu);
    return true;
}
```

**Cross-references:** `getActionMenuGravity()`, `alwaysShowActionMenu()`

---

### `ActionMenuActivity.getActionMenuGravity() -> int`
**Repo:** Blade_2_Template_App | **File:** app/src/main/java/.../around_content_template_activity.java | **Language:** Java

Set menu position. Returns `Gravity.RIGHT` for side menu or `Gravity.CENTER` for center menu.

**Returns:** `int` — Android Gravity constant

---

### `ActionMenuActivity.alwaysShowActionMenu() -> boolean`
**Repo:** Blade_2_Template_App | **File:** app/src/main/java/.../center_content_template_activity.java | **Language:** Java

Whether the action menu is always visible on the HUD.

**Returns:** `boolean` — true for persistent menu, false for on-demand

---

## 1.5 Everysight Maverick Display

### `Text().setText(text).setResource(font).setTextAlign(align).setXY(x, y).setForegroundColor(color).addTo(screen)`
**Repo:** everysight-sdk | **File:** (SDK binary) | **Language:** Kotlin

Fluent builder API for rendering text on Everysight Maverick glasses.

**Parameters (builder chain):**
| Method | Type | Description |
|--------|------|-------------|
| setText(text) | String | Text content to display |
| setResource(font) | Font.StockFont | Font selection (e.g., Medium, Large) |
| setTextAlign(align) | Align | Text alignment (center, left, right) |
| setXY(x, y) | Int, Int | Position on display |
| setForegroundColor(color) | Int | RGBA color value |
| addTo(screen) | Screen | Target screen to add element to |

**Returns:** Text element added to screen

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
| Method | Returns | Description |
|--------|---------|-------------|
| `zoomIn()` | void | Increase zoom level |
| `zoomOut()` | void | Decrease zoom level |
| `resetZoom()` | void | Reset to default zoom |
| `setRadius(radius: Float, immediate: Boolean)` | void | Set cylinder radius |
| `updateHeadPose(yaw: Float, pitch: Float, deltaTime: Float)` | void | Update from IMU data |
| `recenter(currentYaw: Float, currentPitch: Float)` | void | Recenter view to current head position |
| `getViewMatrix() -> FloatArray` | FloatArray | Get 4x4 view matrix |
| `getMVPMatrix() -> FloatArray` | FloatArray | Get model-view-projection matrix |
| `getLeftEyeMVPMatrix() -> FloatArray` | FloatArray | Left eye MVP for stereo |
| `getRightEyeMVPMatrix() -> FloatArray` | FloatArray | Right eye MVP for stereo |

**Cross-references:** `CylinderMesh`, `FlatQuadMesh`, `StreamRenderer`, `HeadGazeCursor`

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

### `void make3DEffect()`
**Repo:** RayNeo ARDK | **File:** ARDK for Android / Unity | **Language:** C#/Java
**Source:** deep-reads/09-rayneo-docs.md

Enable stereoscopic 3D parallax effect on binocular display. Adjusts rendering to create depth perception across both eye displays.

**Returns:** `void`

**Notes:**
- Available on both X2 and X3 Pro
- Uses `BindingPair` for left/right eye synchronization
- Must be called after display initialization

**Cross-references:** `make3DEffectForSide()`, `BindingPair`, `BaseMirrorActivity`, `MirrorContainerView`

---

### `void make3DEffectForSide()`
**Repo:** RayNeo ARDK | **File:** ARDK for Android / Unity | **Language:** C#/Java
**Source:** deep-reads/09-rayneo-docs.md

Enable stereoscopic 3D effect for a specific eye side. Used for per-eye content differentiation.

**Returns:** `void`

**Cross-references:** `make3DEffect()`, `setLeft()`, `checkIsLeft()`

---

### `class BindingPair`
**Repo:** RayNeo ARDK | **Language:** Java
**Source:** deep-reads/09-rayneo-docs.md

Manages left/right eye view synchronization for binocular displays.

**Key Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `updateView()` | void | Sync view to both displays |
| `setLeft()` | void | Set as left eye view |
| `checkIsLeft()` | boolean | Check which eye this view belongs to |

---

### `class BaseMirrorActivity`
**Repo:** RayNeo ARDK | **Language:** Java
**Source:** deep-reads/09-rayneo-docs.md

Base activity for dual-display rendering. Extend this to create binocular AR activities.

**Cross-references:** `BaseMirrorFragment`, `MirrorContainerView`, `BindingPair`

---

### `class MirrorContainerView`
**Repo:** RayNeo ARDK | **Language:** Java
**Source:** deep-reads/09-rayneo-docs.md

Container view that mirrors content to both eyes automatically.

---

### `class FToast`
**Repo:** RayNeo ARDK | **Language:** Java
**Source:** deep-reads/09-rayneo-docs.md

Floating toast for binocular display. Renders toast messages visible in both eye displays simultaneously.

---

### `class FDialog`
**Repo:** RayNeo ARDK | **Language:** Java
**Source:** deep-reads/09-rayneo-docs.md

Floating dialog for binocular display. Shows dialog boxes visible in both eye displays.

---

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

### Core Types

```c
typedef union {
    float array[3];
    struct { float x; float y; float z; } axis;
} FusionVector;
// 3D vector. Used for accelerometer, gyroscope, magnetometer data.

typedef union {
    float array[4];
    struct { float w; float x; float y; float z; } element;
} FusionQuaternion;
// Quaternion representation of orientation.

typedef union {
    float array[9];
    struct { float xx, xy, xz, yx, yy, yz, zx, zy, zz; } element;
} FusionMatrix;
// 3x3 matrix in row-major order. Used for rotation matrices, calibration.

typedef union {
    float array[3];
    struct { float roll; float pitch; float yaw; } angle;
} FusionEuler;
// ZYX Euler angles in degrees. Roll=X, Pitch=Y, Yaw=Z.
```

### Constants/Macros

```c
#define FUSION_VECTOR_ZERO      ((FusionVector){ .array = {0.0f, 0.0f, 0.0f} })
#define FUSION_VECTOR_ONES      ((FusionVector){ .array = {1.0f, 1.0f, 1.0f} })
#define FUSION_QUATERNION_IDENTITY ((FusionQuaternion){ .array = {1.0f, 0.0f, 0.0f, 0.0f} })
#define FUSION_MATRIX_IDENTITY  ((FusionMatrix){ .array = {1,0,0, 0,1,0, 0,0,1} })
#define FUSION_EULER_ZERO       ((FusionEuler){ .array = {0.0f, 0.0f, 0.0f} })
```

### Earth Axes Convention

```c
typedef enum {
    FusionConventionNwu,  // North-West-Up: X=North, Y=West, Z=Up
    FusionConventionEnu,  // East-North-Up: X=East, Y=North, Z=Up
    FusionConventionNed,  // North-East-Down: X=North, Y=East, Z=Down
} FusionConvention;
```

### AHRS Settings Structure

```c
typedef struct {
    FusionConvention convention;          // Earth axes convention (NWU/ENU/NED)
    float gain;                           // Complementary filter gain (0.5 typical; 0=gyro only)
    float gyroscopeRange;                 // Gyroscope range in deg/s (0=disable angular rate recovery)
    float accelerationRejection;          // Accel rejection threshold in degrees (0=disable; 10 typical)
    float magneticRejection;              // Mag rejection threshold in degrees (0=disable; 10 typical)
    unsigned int recoveryTriggerPeriod;   // Recovery trigger period in samples (0=disable; 5*sampleRate typical)
} FusionAhrsSettings;

// Default settings:
extern const FusionAhrsSettings fusionAhrsDefaultSettings;
// = { .convention=NWU, .gain=0.5, .gyroscopeRange=0.0, .accelerationRejection=90.0,
//     .magneticRejection=90.0, .recoveryTriggerPeriod=0 }
```

### AHRS Internal State Structures

```c
typedef struct {
    float accelerationError;              // Angular error in degrees (accel vs algorithm output)
    bool accelerometerIgnored;            // true if accel was ignored last update
    float accelerationRecoveryTrigger;    // Recovery trigger 0.0-1.0
    float magneticError;                  // Angular error in degrees (mag vs algorithm output)
    bool magnetometerIgnored;             // true if mag was ignored last update
    float magneticRecoveryTrigger;        // Recovery trigger 0.0-1.0
} FusionAhrsInternalStates;

typedef struct {
    bool startup;                         // true during algorithm startup
    bool angularRateRecovery;             // true during angular rate recovery
    bool accelerationRecovery;            // true during acceleration recovery
    bool magneticRecovery;                // true during magnetic recovery
} FusionAhrsFlags;
```

---

### `void FusionAhrsInitialise(FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Initialize the AHRS (Attitude and Heading Reference System) structure with default settings. Resets quaternion to identity and enables startup mode with gain ramping.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | Pointer to AHRS structure to initialize |

**Returns:** `void`

**Example:**
```c
FusionAhrs ahrs;
FusionAhrsInitialise(&ahrs);
```

**Cross-references:** `FusionAhrsSetSettings()`, `FusionAhrsRestart()`, `FusionAhrsUpdate()`

---

### `void FusionAhrsRestart(FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Restarts the AHRS algorithm. Resets quaternion to identity and enables startup gain ramping. Use when sensor orientation has changed dramatically.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | Pointer to AHRS structure |

**Returns:** `void`

**Cross-references:** `FusionAhrsInitialise()`

---

### `void FusionAhrsSetSettings(FusionAhrs *ahrs, const FusionAhrsSettings *settings)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Configure the AHRS algorithm parameters. Converts rejection thresholds to internal representation. Disables rejection features if gain=0 or recoveryTriggerPeriod=0.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | AHRS structure |
| settings | const FusionAhrsSettings* | Settings structure with convention, gain, gyroscopeRange, accelerationRejection, magneticRejection, recoveryTriggerPeriod |

**Returns:** `void`

**Example:**
```c
FusionAhrsSettings settings = {
    .convention = FusionConventionNwu,
    .gain = 0.5f,
    .gyroscopeRange = 2000.0f,           // deg/s full scale
    .accelerationRejection = 10.0f,       // degrees threshold
    .magneticRejection = 10.0f,           // degrees threshold
    .recoveryTriggerPeriod = 5 * SAMPLE_RATE,  // 5 seconds of samples
};
FusionAhrsSetSettings(&ahrs, &settings);
```

**Notes:**
- `gain`: 0.5 is typical. Higher values trust accelerometer/magnetometer more. 0 = pure gyroscope integration.
- `gyroscopeRange`: Set to your gyroscope's full-scale range. 0 disables angular rate recovery.
- `accelerationRejection`: Ignores accelerometer when motion exceeds this angle threshold from expected gravity.
- `magneticRejection`: Ignores magnetometer when field deviates too much from expected direction.

**Cross-references:** `FusionAhrsInitialise()`, `FusionAhrsUpdate()`

---

### `void FusionAhrsUpdate(FusionAhrs *ahrs, FusionVector gyroscope, FusionVector accelerometer, FusionVector magnetometer, float deltaTime)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.c | **Language:** C

Core AHRS update with all three sensor inputs. Implements the revised Madgwick algorithm (PhD thesis Ch.7) with acceleration/magnetic rejection and angular rate recovery.

**Algorithm Steps:**
1. Integrate gyroscope with delta time
2. Compute accelerometer feedback (gravity direction correction)
3. Compute magnetometer feedback (heading correction)
4. Apply acceleration rejection (ignore if motion detected)
5. Apply magnetic rejection (ignore if field disturbance detected)
6. Angular rate recovery (use feedback as backup when gyro range exceeded)
7. Gain ramping during startup
8. Update and normalize quaternion

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | AHRS structure |
| gyroscope | FusionVector | Gyroscope data in degrees per second |
| accelerometer | FusionVector | Accelerometer data in g (1g = 9.81 m/s²) |
| magnetometer | FusionVector | Magnetometer data in any calibrated units |
| deltaTime | float | Time since last update in seconds |

**Returns:** `void`

**Example:**
```c
FusionVector gyro = {.axis = {0.1f, 0.2f, -0.1f}};   // deg/s
FusionVector accel = {.axis = {0.0f, 0.0f, 1.0f}};    // g
FusionVector mag = {.axis = {20.0f, 0.0f, 40.0f}};    // uT
FusionAhrsUpdate(&ahrs, gyro, accel, mag, 1.0f / SAMPLE_RATE);

// Get result
FusionEuler euler = FusionQuaternionToEuler(FusionAhrsGetQuaternion(&ahrs));
printf("Roll=%f Pitch=%f Yaw=%f\n", euler.angle.roll, euler.angle.pitch, euler.angle.yaw);
```

**Internal Static Functions:**
- `HalfGravity(ahrs)` — Returns gravity direction scaled by 0.5 from quaternion (convention-aware)
- `HalfMagnetic(ahrs)` — Returns magnetic field direction scaled by 0.5 from quaternion
- `Feedback(sensor, reference)` — Returns feedback as cross product of sensor and reference vectors

**Cross-references:** `FusionAhrsUpdateNoMagnetometer()`, `FusionAhrsUpdateExternalHeading()`, `FusionAhrsGetQuaternion()`

---

### `void FusionAhrsUpdateNoMagnetometer(FusionAhrs *ahrs, FusionVector gyroscope, FusionVector accelerometer, float deltaTime)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.c | **Language:** C

AHRS update without magnetometer. Calls `FusionAhrsUpdate` with zero magnetometer vector. Heading is zeroed during startup phase. Suitable for most AR glasses which lack magnetometer.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | AHRS structure |
| gyroscope | FusionVector | Gyroscope in degrees per second |
| accelerometer | FusionVector | Accelerometer in g |
| deltaTime | float | Delta time in seconds |

**Returns:** `void`

**Notes:** Without magnetometer, yaw will drift over time. Use `FusionAhrsSetHeading()` periodically to correct.

**Cross-references:** `FusionAhrsUpdate()`, `FusionAhrsUpdateExternalHeading()`

---

### `void FusionAhrsUpdateExternalHeading(FusionAhrs *ahrs, FusionVector gyroscope, FusionVector accelerometer, float heading, float deltaTime)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.c | **Language:** C

AHRS update using external heading (e.g., GPS compass) instead of magnetometer. Constructs equivalent magnetometer vector from heading and current roll.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | AHRS structure |
| gyroscope | FusionVector | Gyroscope in degrees per second |
| accelerometer | FusionVector | Accelerometer in g |
| heading | float | External heading in degrees (0=North, 90=East) |
| deltaTime | float | Delta time in seconds |

**Returns:** `void`

**Cross-references:** `FusionAhrsUpdate()`, `FusionCompass()`

---

### `FusionQuaternion FusionAhrsGetQuaternion(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns the current orientation quaternion describing sensor orientation relative to Earth.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | const FusionAhrs* | AHRS structure |

**Returns:** `FusionQuaternion` — {w, x, y, z} unit quaternion. w=1 when aligned with reference frame.

**Example:**
```c
FusionQuaternion q = FusionAhrsGetQuaternion(&ahrs);
printf("w=%f x=%f y=%f z=%f\n", q.element.w, q.element.x, q.element.y, q.element.z);

// Convert to Euler
FusionEuler euler = FusionQuaternionToEuler(q);
// Convert to rotation matrix
FusionMatrix matrix = FusionQuaternionToMatrix(q);
```

**Cross-references:** `FusionAhrsSetQuaternion()`, `FusionQuaternionToEuler()`, `FusionQuaternionToMatrix()`

---

### `void FusionAhrsSetQuaternion(FusionAhrs *ahrs, FusionQuaternion quaternion)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Set the orientation quaternion directly. Use to restore a previously saved orientation.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | AHRS structure |
| quaternion | FusionQuaternion | Quaternion to set |

**Returns:** `void`

---

### `FusionVector FusionAhrsGetGravity(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns direction of gravity in sensor frame as a unit vector. Useful for determining "down" direction relative to the sensor.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | const FusionAhrs* | AHRS structure |

**Returns:** `FusionVector` — Unit vector pointing in gravity direction in sensor frame

---

### `FusionVector FusionAhrsGetLinearAcceleration(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns linear acceleration (accelerometer with gravity removed) in sensor frame, in g units. Useful for detecting user motion/gestures.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | const FusionAhrs* | AHRS structure |

**Returns:** `FusionVector` — Linear acceleration in g (0 when stationary)

---

### `FusionVector FusionAhrsGetEarthAcceleration(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns acceleration in Earth frame with gravity removed. Rotates accelerometer to Earth frame then subtracts gravity vector. Useful for displacement estimation.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | const FusionAhrs* | AHRS structure |

**Returns:** `FusionVector` — Earth-frame acceleration in g

---

### `FusionAhrsInternalStates FusionAhrsGetInternalStates(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns internal algorithm states for debugging: accelerationError, accelerometerIgnored, magneticError, magnetometerIgnored, recovery triggers.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | const FusionAhrs* | AHRS structure |

**Returns:** `FusionAhrsInternalStates` — Struct with debug information

---

### `FusionAhrsFlags FusionAhrsGetFlags(const FusionAhrs *ahrs)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.h | **Language:** C

Returns algorithm flags: startup, angularRateRecovery, accelerationRecovery, magneticRecovery.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | const FusionAhrs* | AHRS structure |

**Returns:** `FusionAhrsFlags` — Boolean flags for each algorithm state

---

### `void FusionAhrsSetHeading(FusionAhrs *ahrs, float heading)`
**Repo:** Fusion | **File:** Fusion/FusionAhrs.c | **Language:** C

Sets the heading (yaw) of the current orientation by applying a Z-axis rotation. Use for compass correction or user-initiated recenter.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ahrs | FusionAhrs* | AHRS structure |
| heading | float | Heading in degrees (0-360) |

**Returns:** `void`

---

## 2.2 Fusion Math Operations

### `float FusionDegreesToRadians(float degrees)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Converts degrees to radians.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| degrees | float | Angle in degrees |

**Returns:** `float` — degrees * (PI / 180)

---

### `float FusionRadiansToDegrees(float radians)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Converts radians to degrees.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| radians | float | Angle in radians |

**Returns:** `float` — radians * (180 / PI)

---

### `float FusionArcSin(float value)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Clamped arc sine. Clamps input to [-1, 1] before computing asin to avoid NaN results from floating-point imprecision.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| value | float | Input value (will be clamped to [-1, 1]) |

**Returns:** `float` — Arc sine in radians

---

### `float FusionFastInverseSqrt(float x)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Fast inverse square root using Pizer's implementation. Returns `1/sqrt(x)`. Disabled if `FUSION_USE_NORMAL_SQRT` is defined (falls back to `1.0f/sqrtf(x)`).

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| x | float | Input value (must be positive) |

**Returns:** `float` — Approximate 1/sqrt(x)

**Notes:** Optimized for embedded systems. Provides ~1% accuracy which is sufficient for sensor fusion.

---

### `bool FusionVectorIsZero(FusionVector v)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Returns true if all components are exactly 0.0f.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| v | FusionVector | Vector to test |

**Returns:** `bool` — true if x==0 && y==0 && z==0

---

### `FusionVector FusionVectorAdd(FusionVector a, FusionVector b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Element-wise vector addition. Returns `{a.x+b.x, a.y+b.y, a.z+b.z}`.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| a | FusionVector | First vector |
| b | FusionVector | Second vector |

**Returns:** `FusionVector` — Sum vector

---

### `FusionVector FusionVectorSubtract(FusionVector a, FusionVector b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Element-wise vector subtraction. Returns `{a.x-b.x, a.y-b.y, a.z-b.z}`.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| a | FusionVector | First vector |
| b | FusionVector | Second vector |

**Returns:** `FusionVector` — Difference vector

---

### `FusionVector FusionVectorScale(FusionVector v, float s)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Scalar multiplication of vector. Returns `{v.x*s, v.y*s, v.z*s}`.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| v | FusionVector | Vector to scale |
| s | float | Scalar multiplier |

**Returns:** `FusionVector` — Scaled vector

---

### `float FusionVectorSum(FusionVector v)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Returns sum of all components: x + y + z.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| v | FusionVector | Input vector |

**Returns:** `float` — x + y + z

---

### `FusionVector FusionVectorHadamard(FusionVector a, FusionVector b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Element-wise product (Hadamard product): `{a.x*b.x, a.y*b.y, a.z*b.z}`.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| a | FusionVector | First vector |
| b | FusionVector | Second vector |

**Returns:** `FusionVector` — Element-wise product

---

### `FusionVector FusionVectorCross(FusionVector a, FusionVector b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Cross product a × b.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| a | FusionVector | First vector |
| b | FusionVector | Second vector |

**Returns:** `FusionVector` — Cross product (perpendicular to both inputs)

---

### `float FusionVectorDot(FusionVector a, FusionVector b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Dot product a · b.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| a | FusionVector | First vector |
| b | FusionVector | Second vector |

**Returns:** `float` — a.x*b.x + a.y*b.y + a.z*b.z

---

### `float FusionVectorNormSquared(FusionVector v)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Returns magnitude squared |v|² = x² + y² + z². Avoids sqrt for performance when comparing magnitudes.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| v | FusionVector | Input vector |

**Returns:** `float` — Magnitude squared

---

### `float FusionVectorNorm(FusionVector v)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Returns magnitude |v| = sqrt(x² + y² + z²).

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| v | FusionVector | Input vector |

**Returns:** `float` — Magnitude

---

### `FusionVector FusionVectorNormalise(FusionVector v)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Returns unit vector v/|v|. Uses fast inverse sqrt for performance on embedded systems unless `FUSION_USE_NORMAL_SQRT` is defined.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| v | FusionVector | Input vector (must be non-zero) |

**Returns:** `FusionVector` — Unit vector

---

### Quaternion Operations

### `FusionQuaternion FusionQuaternionAdd(FusionQuaternion a, FusionQuaternion b)`
Element-wise quaternion addition.

### `FusionQuaternion FusionQuaternionScale(FusionQuaternion q, float s)`
Scalar multiplication of quaternion.

### `float FusionQuaternionSum(FusionQuaternion q)`
Returns w + x + y + z.

### `FusionQuaternion FusionQuaternionHadamard(FusionQuaternion a, FusionQuaternion b)`
Element-wise quaternion product.

### `FusionQuaternion FusionQuaternionProduct(FusionQuaternion a, FusionQuaternion b)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Hamilton quaternion product a * b. Non-commutative: a*b ≠ b*a.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| a | FusionQuaternion | Left quaternion |
| b | FusionQuaternion | Right quaternion |

**Returns:** `FusionQuaternion` — Hamilton product

---

### `FusionQuaternion FusionQuaternionVectorProduct(FusionQuaternion q, FusionVector v)`
Returns q * v where v is treated as quaternion with w=0.

### `float FusionQuaternionNormSquared(FusionQuaternion q)`
Returns |q|² (quaternion norm squared).

### `float FusionQuaternionNorm(FusionQuaternion q)`
Returns |q| (quaternion norm).

### `FusionQuaternion FusionQuaternionNormalise(FusionQuaternion q)`
Returns unit quaternion q/|q|.

---

### Conversion Functions

### `FusionMatrix FusionQuaternionToMatrix(FusionQuaternion q)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Converts quaternion to 3x3 rotation matrix (transpose of Kuipers convention).

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| q | FusionQuaternion | Input quaternion |

**Returns:** `FusionMatrix` — 3x3 rotation matrix

---

### `FusionEuler FusionQuaternionToEuler(FusionQuaternion q)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Converts quaternion to ZYX Euler angles in degrees (roll, pitch, yaw).

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| q | FusionQuaternion | Input quaternion |

**Returns:** `FusionEuler` — {roll, pitch, yaw} in degrees

---

### `FusionVector FusionMatrixMultiply(FusionMatrix m, FusionVector v)`
**Repo:** Fusion | **File:** Fusion/FusionMath.h | **Language:** C

Matrix-vector multiplication M * v.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| m | FusionMatrix | 3x3 matrix |
| v | FusionVector | 3D vector |

**Returns:** `FusionVector` — Transformed vector

---

## 2.3 Fusion Bias Estimation

### Bias Settings Structure

```c
typedef struct {
    float sampleRate;           // Sample rate in Hz (default: 100)
    float stationaryThreshold;  // Stationary threshold in deg/s (default: 3.0)
    float stationaryPeriod;     // Stationary detection period in seconds (default: 3.0)
} FusionBiasSettings;

extern const FusionBiasSettings fusionBiasDefaultSettings;
// = { .sampleRate=100, .stationaryThreshold=3.0, .stationaryPeriod=3.0 }
```

### `void FusionBiasInitialise(FusionBias *bias)`
**Repo:** Fusion | **File:** Fusion/FusionBias.h | **Language:** C

Initialize gyroscope bias estimation structure with default settings (100Hz, 3.0°/s threshold, 3.0s period). Zeroes offset.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| bias | FusionBias* | Bias estimation structure |

**Returns:** `void`

---

### `void FusionBiasSetSettings(FusionBias *bias, const FusionBiasSettings *settings)`
**Repo:** Fusion | **File:** Fusion/FusionBias.h | **Language:** C

Configure bias estimation: sampleRate, stationaryThreshold, stationaryPeriod. Computes filter coefficient and timeout internally.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| bias | FusionBias* | Bias structure |
| settings | const FusionBiasSettings* | Settings with sampleRate, stationaryThreshold, stationaryPeriod |

**Returns:** `void`

---

### `FusionVector FusionBiasUpdate(FusionBias *bias, FusionVector gyroscope)`
**Repo:** Fusion | **File:** Fusion/FusionBias.c | **Language:** C

Update bias estimation and return offset-corrected gyroscope. Must be called every sample. Detects stationary periods automatically to estimate and remove gyroscope drift.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| bias | FusionBias* | Bias structure |
| gyroscope | FusionVector | Raw gyroscope in degrees per second |

**Returns:** `FusionVector` — Offset-corrected gyroscope in degrees per second

**Example:**
```c
FusionBias bias;
FusionBiasInitialise(&bias);
// In sensor loop:
FusionVector correctedGyro = FusionBiasUpdate(&bias, rawGyro);
FusionAhrsUpdateNoMagnetometer(&ahrs, correctedGyro, accel, deltaTime);
```

---

### `FusionVector FusionBiasGetOffset(const FusionBias *bias)`
**Repo:** Fusion | **File:** Fusion/FusionBias.h | **Language:** C

Returns the current estimated gyroscope bias offset.

**Returns:** `FusionVector` — Gyroscope offset in degrees per second

---

### `void FusionBiasSetOffset(FusionBias *bias, FusionVector offset)`
**Repo:** Fusion | **File:** Fusion/FusionBias.h | **Language:** C

Sets gyroscope offset directly (e.g., restore from non-volatile memory).

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| bias | FusionBias* | Bias structure |
| offset | FusionVector | Gyroscope offset in degrees per second |

**Returns:** `void`

---

## 2.4 Fusion Compass & Calibration

### `float FusionCompass(FusionVector accelerometer, FusionVector magnetometer, FusionConvention convention)`
**Repo:** Fusion | **File:** Fusion/FusionCompass.h | **Language:** C

Calculates tilt-compensated magnetic heading using accelerometer for tilt and magnetometer for heading. Convention-aware: computes north/west/east vectors differently per convention.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| accelerometer | FusionVector | Accelerometer in any calibrated units |
| magnetometer | FusionVector | Magnetometer in any calibrated units |
| convention | FusionConvention | Earth axes convention (NWU/ENU/NED) |

**Returns:** `float` — Magnetic heading in degrees (0-360)

---

### `FusionVector FusionModelInertial(FusionVector uncalibrated, FusionMatrix misalignment, FusionVector sensitivity, FusionVector offset)`
**Repo:** Fusion | **File:** Fusion/FusionModel.h | **Language:** C

Apply inertial sensor calibration: `M * diag(s) * (raw - offset)`.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| uncalibrated | FusionVector | Raw gyroscope or accelerometer reading |
| misalignment | FusionMatrix | 3x3 misalignment correction matrix |
| sensitivity | FusionVector | Sensitivity diagonal (as vector: {sx, sy, sz}) |
| offset | FusionVector | Zero-rate offset vector |

**Returns:** `FusionVector` — Calibrated sensor reading

---

### `FusionVector FusionModelMagnetic(FusionVector uncalibrated, FusionMatrix softIronMatrix, FusionVector hardIronOffset)`
**Repo:** Fusion | **File:** Fusion/FusionModel.h | **Language:** C

Apply magnetometer calibration: `S * (raw - h)`.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| uncalibrated | FusionVector | Raw magnetometer reading |
| softIronMatrix | FusionMatrix | 3x3 soft-iron correction matrix |
| hardIronOffset | FusionVector | Hard-iron offset vector |

**Returns:** `FusionVector` — Calibrated magnetometer reading

---

### `FusionVector FusionRemap(FusionVector sensor, FusionRemapAlignment alignment)`
**Repo:** Fusion | **File:** Fusion/FusionRemap.h | **Language:** C

Remap sensor axes using one of 24 orthogonal permutations. Use when sensor is mounted in non-standard orientation.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sensor | FusionVector | Raw sensor vector |
| alignment | FusionRemapAlignment | One of 24 alignment enums (e.g., FusionRemapAlignmentPXPYPZ for no remap) |

**Returns:** `FusionVector` — Remapped sensor vector

**Available Alignments (24 total):**
- `FusionRemapAlignmentPXPYPZ` — +X+Y+Z (no remap)
- `FusionRemapAlignmentPXPZNY` — +X+Z-Y
- `FusionRemapAlignmentPXNZPY` — +X-Z+Y
- `FusionRemapAlignmentPXNYNZ` — +X-Y-Z
- ... (20 more orthogonal permutations)
- `FusionRemapAlignmentNXNYPZ` — -X-Y+Z

---

## 2.5 Fusion Python API

### `imufusion.Ahrs()`
**Repo:** Fusion | **File:** Python bindings | **Language:** Python

Create an AHRS instance (Python wrapper for the C library).

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
    print(f"Roll={euler[0]:.1f} Pitch={euler[1]:.1f} Yaw={euler[2]:.1f}")
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
Normalize a quaternion to unit length.

### `imu_quat_type multiply_quaternions(imu_quat_type q1, imu_quat_type q2)`
Hamilton product of two quaternions.

### `imu_quat_type euler_to_quaternion_xyz(imu_euler_type euler)`
Convert Euler angles (XYZ order) to quaternion.

### `imu_euler_type quaternion_to_euler_zyx(imu_quat_type q)`
Convert quaternion to Euler angles (ZYX order).

### `imu_vec3_type vector_rotate(imu_vec3_type v, imu_quat_type q)`
Rotate a 3D vector by a quaternion.

### `float quat_small_angle_rad(imu_quat_type q1, imu_quat_type q2)`
Compute the small angle between two quaternions in radians.

---

## 2.7 XRLinuxDriver Buffer System

### `buffer_type *create_buffer(int size)`
Create a ring buffer for smoothing IMU data.

### `float push(buffer_type *buffer, float next_value)`
Push a value into the ring buffer and return the rolling average.

### `imu_buffer_type *create_imu_buffer(int buffer_size)`
Create a quaternion-aware IMU ring buffer with timestamp tracking.

### `imu_buffer_response_type *push_to_imu_buffer(imu_buffer_type *buf, imu_quat_type quat, float timestamp_ms)`
Push a quaternion sample into the IMU buffer. Returns smoothed quaternion and look-ahead prediction.

---

## 2.8 PhoenixHeadTracker (C# / Windows)

### `int StartConnection()`
**Repo:** PhoenixHeadTracker | **Language:** C#

Connect to XREAL Air glasses. Returns 1 on success.

```csharp
[DllImport("AirAPI_Windows", CallingConvention = CallingConvention.Cdecl)]
public static extern int StartConnection();
```

### `int StopConnection()`
Disconnect from XREAL Air glasses. Returns 1 on success.

### `IntPtr GetEuler()`
Read Euler angles from glasses. Returns pointer to float[3]: [roll, pitch, yaw].

### `IntPtr GetQuaternion()`
Read quaternion from glasses. Returns pointer to float[4]: [x, y, z, w].

### `class KalmanFilter`
1D Kalman filter for smoothing IMU deltas.
- **Constructor:** `KalmanFilter(double q, double r, double p, double x)` — q=process noise, r=measurement noise, p=initial error, x=initial value.
- **Methods:** `double Update(double measurement)` — Returns filtered value.

---

## 2.9 headset-utils (Rust) — Sensor Fusion

### `trait ARGlasses: Send`
**Repo:** headset-utils | **File:** src/lib.rs | **Language:** Rust

Core trait for AR glasses device communication.

```rust
pub trait ARGlasses: Send {
    fn serial(&mut self) -> Result<String>;
    fn read_event(&mut self) -> Result<GlassesEvent>;
    fn get_display_mode(&mut self) -> Result<DisplayMode>;
    fn set_display_mode(&mut self, display_mode: DisplayMode) -> Result<()>;
    fn display_fov(&self) -> f32;                                    // FOV in radians
    fn imu_to_display_matrix(&self, side: Side, ipd: f32) -> Isometry3<f64>;
    fn name(&self) -> &'static str;
    fn cameras(&self) -> Result<Vec<CameraDescriptor>>;             // default: empty
    fn display_matrices(&self) -> Result<(DisplayMatrices, DisplayMatrices)>; // default: NotImplemented
    fn display_delay(&self) -> u64;                                  // display delay in usecs
}
```

**Implementations:** NrealAir, NrealLight, RokidAir, GrawoowG530, MadGazeGlow

---

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
impl dyn Fusion {
    pub fn attitude_frd_rad(&self) -> Vector3<f32>;  // (roll, pitch, yaw) in radians
    pub fn attitude_frd_deg(&self) -> Vector3<f32>;  // (roll, pitch, yaw) in degrees
}
```

---

### `enum GlassesEvent`
```rust
pub enum GlassesEvent {
    AccGyro {
        accelerometer: Vector3<f32>,  // m²/s. Upright normal = (0, 9.81, 0)
        gyroscope: Vector3<f32>,      // rad/sec right-hand rotation. RUB frame.
        timestamp: u64,               // device time in microseconds
    },
    Magnetometer { magnetometer: Vector3<f32>, timestamp: u64 },
    KeyPress(u8),
    ProximityNear,
    ProximityFar,
    AmbientLight(u16),
    VSync,
}
```

---

### `pub fn any_glasses() -> Result<Box<dyn ARGlasses>>`
Auto-detect and connect to any supported AR glasses. Tries Rokid, NrealAir, NrealLight, Grawoow, MadGaze in order.

### `pub fn any_fusion() -> Result<Box<dyn Fusion>>`
Auto-detect glasses and create a NaiveCF fusion instance.

---

### `struct NaiveCF`
**Repo:** headset-utils | **File:** src/naive_cf.rs | **Language:** Rust

Naive complementary filter implementation. Constants:
- `BASE_GRAV_RATIO = 0.005` (accelerometer trust ratio)
- `GYRO_SPEED_IN_TIMESTAMP_FACTOR = 1_000_000.0` (microseconds)
- `INCONSISTENCY_DECAY = 0.90`
- `UP_FRD = (0.0, 0.0, -9.81)`

```rust
impl NaiveCF {
    pub fn new(glasses: Box<dyn ARGlasses>) -> Result<Self>;
    pub fn get_correction(acc, rotation, scale) -> Option<UnitQuaternion<f32>>;
    pub fn get_rotation(acc, rotation) -> Option<UnitQuaternion<f32>>;
}
```

---

## 2.10 RayNeo 3DOF Head Tracking (HeadTrackedPoseDriver)
**Source:** deep-reads/09-rayneo-docs.md

### `HeadTrackedPoseParams.AwakeDriver()`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

Initialize 3DOF head tracking driver. Must be called before receiving pose updates.

**Returns:** `void`

**Notes:**
- Tracks pitch, yaw, roll (no positional tracking)
- Uses TYPE_GAME_ROTATION_VECTOR sensor internally
- Available sensor rates: SENSOR_DELAY_FASTEST, SENSOR_DELAY_GAME, SENSOR_DELAY_NORMAL, SENSOR_DELAY_UI

**Cross-references:** `DestroyDriver()`, `OnPostUpdate()`, `ResetRotation()`

---

### `HeadTrackedPoseParams.DestroyDriver()`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

Cleanup and destroy the 3DOF tracking driver. Release all sensor resources.

**Returns:** `void`

---

### `void OnPostUpdate(Pose pose)`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

Callback invoked after each pose update with quaternion orientation data.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| pose | Pose | Unity Pose containing rotation quaternion (no position in 3DOF mode) |

**Returns:** `void`

---

### `void ResetRotation()`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

Reset head tracking to zero heading. Recenters the forward direction to current head orientation.

**Returns:** `void`

---

## 2.11 RayDesk Spatial Tracking

### `class HeadGazeCursor(screenWidth: Int, screenHeight: Int, ...)`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/input/HeadGazeCursor.kt | **Language:** Kotlin

Maps IMU head orientation to cursor position on the virtual screen.

**Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `updateHeadOrientation(yaw, pitch, timestamp)` | void | Update from Euler angles |
| `updateFromQuaternion(sensorValues, timestamp)` | void | Update from raw quaternion |
| `getCursorPosition()` | CursorPosition | Get current cursor position |
| `recenter()` | void | Reset cursor to center |
| `reset()` | void | Full state reset |

---

### `class OneEuroFilter`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/spatial/OneEuroFilter.kt | **Language:** Kotlin

1€ noise filter for smooth head tracking. Combines low-pass filtering with speed-adaptive cutoff frequency.

---

### `data class Quaternion(val w: Float, val x: Float, val y: Float, val z: Float)`
**Repo:** RayDesk | **File:** app/src/main/java/com/raydesk/spatial/Quaternion.kt | **Language:** Kotlin

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
| Name | Type | Description |
|------|------|-------------|
| jpegBytes | ByteArray | Raw JPEG image data |
| timestampMs | Long | Capture timestamp in milliseconds |
| width | Int? | Image width (if available) |
| height | Int? | Image height (if available) |
| rotationDegrees | Int? | EXIF rotation |
| sourceModel | GlassesModel | Which device captured it |

---

## 3.2 RayNeo Camera Sharing (ShareCamera)
**Source:** deep-reads/09-rayneo-docs.md

### `ShareCamera.OpenCamera(XRCameraType type, XRResolution resolution, RawImage display, int frameRate)`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

Open camera for shared access on RayNeo glasses.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| type | XRCameraType | Camera type: VGA (for SLAM) or Main (for capture) |
| resolution | XRResolution | Target resolution |
| display | RawImage | Unity RawImage output target |
| frameRate | int | Target frames per second |

**Returns:** `void`

**Notes:**
- Uses Android Camera2 API internally
- VGA camera is shared with SLAM pipeline
- Main camera provides higher resolution for photo/video capture

**Cross-references:** `ShareCameraCtrl`, `CameraPermissionRequest`, `Algorithm.EnableSlamHeadTracker()`

---

## 3.3 RayNeo Face Detection Pipeline
**Source:** deep-reads/09-rayneo-docs.md

Single face recognition/tracking using computer vision + deep learning pipeline.

**Capabilities:**
- Face presence detection
- Face tracking (bounding box)
- Face bounding rectangle output
- Green-lined bounding box visualization

---

# 4. Audio & Speech

## 4.1 Universal Audio API (xg-glass-sdk)

### `GlassesClient.playAudio(source: AudioSource, options: PlayAudioOptions) -> Result<Unit>`
**Repo:** xg-glass-sdk | **Language:** Kotlin

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
**Repo:** xg-glass-sdk | **Language:** Kotlin

Start microphone capture, returning a streaming audio session.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| options | MicrophoneOptions | preferredEncoding (PCM_S16_LE/OPUS), sampleRate (16kHz), channelCount (1), vendorMode |

**Returns:** `Result<MicrophoneSession>` — Session with format info and audio Flow

---

## 4.2 RayNeo Audio Capture Modes
**Source:** deep-reads/09-rayneo-docs.md

### `AudioManager.setParameters(String mode)`
**Repo:** RayNeo ARDK | **Language:** Java

Set audio capture mode on RayNeo glasses via Android AudioManager.

**Available Modes:**
| Mode | Description |
|------|-------------|
| `"recording"` | Standard recording mode |
| `"camera"` | Camera audio capture (optimized for video) |
| `"translation"` | Translation pipeline (noise reduction for speech) |
| `"voice_assistant"` | Voice assistant mode (wake-word optimized) |

**Example:**
```java
AudioManager am = (AudioManager) getSystemService(Context.AUDIO_SERVICE);
am.setParameters("recording");
```

---

# 5. BLE & Wireless Communication

## 5.1 Omi Glass BLE UUIDs

```kotlin
AUDIO_SERVICE_UUID     = "19B10000-E8F2-537E-4F6C-D104768A1214"
AUDIO_DATA_UUID        = "19B10001-E8F2-537E-4F6C-D104768A1214"
AUDIO_CODEC_UUID       = "19B10002-E8F2-537E-4F6C-D104768A1214"
BATTERY_SERVICE_UUID   = "0000180F-0000-1000-8000-00805F9B34FB"
BATTERY_LEVEL_UUID     = "00002A19-0000-1000-8000-00805F9B34FB"
PHOTO_CONTROL_UUID     = "19B10006-E8F2-537E-4F6C-D104768A1214"
PHOTO_DATA_UUID        = "19B10005-E8F2-537E-4F6C-D104768A1214"
TIME_SYNC_SERVICE_UUID = "19B10030-E8F2-537E-4F6C-D104768A1214"
TIME_SYNC_WRITE_UUID   = "19B10031-E8F2-537E-4F6C-D104768A1214"
```

---

# 6. Gesture & Input

## 6.1 RayNeo Touch & Gaze Input
**Source:** deep-reads/09-rayneo-docs.md

### `class TouchDispatcher`
**Repo:** RayNeo ARDK | **Language:** Java

Distributes touch events from temple touchpad to registered callbacks.

**Cross-references:** `CommonTouchCallback`, `BaseEventActivity`, `TempleAction`

---

### `enum TempleAction`
**Repo:** RayNeo ARDK | **Language:** Java

```java
enum TempleAction {
    SlideForward,    // Swipe forward on temple
    SlideBackward,   // Swipe backward on temple
    SwipeUp,         // Vertical swipe up
    SwipeDown,       // Vertical swipe down
    TwoFingerTap,    // Two-finger simultaneous tap
    LongPress,       // Long press (>1s)
    SingleTap,       // Single tap
    DoubleTap        // Double tap (<300ms between taps)
}
```

---

### `class FocusHolder`
**Repo:** RayNeo ARDK | **Language:** Java

Manages focus state across UI elements in the RayNeo binocular display.

**Related Classes:**
- `FixPosFocusTracker` — Fixed-position focus tracking
- `RecyclerViewSlidingTracker` — Focus tracking in scrollable lists
- `RecyclerViewFocusTracker` — RecyclerView focus management
- `IFocusable` interface — Contract for focusable elements

---

## 6.2 RayNeo Gaze Interaction (Unity)
**Source:** deep-reads/09-rayneo-docs.md

### `class GazeLaserBeam`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

Renders gaze direction ray. Part of the XR Plugin Gaze prefab system.

**Selection Modes:**
1. Gaze-for-seconds: dwell time → select
2. Temple-click: gaze + tap to select

**Configurable Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| ProgressOuterDiameterOffset | float | Loading ring outer radius offset |
| ProgressInnerDiameterOffset | float | Loading ring inner radius offset |
| ProgressSpeed | float | Dwell timer speed (seconds to fill) |

**Cross-references:** `LaserBeam`, `XRGraphicRaycaster`

---

### `class XRGraphicRaycaster`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

Raycasts from gaze direction against UI elements. Extends Unity's GraphicRaycaster for XR gaze-based interaction.

---

## 6.3 RayNeo Ring Control (IPCSDK)
**Source:** deep-reads/09-rayneo-docs.md

### `RingIPCHelper.registerRingInfo(callback)`
**Repo:** RayNeo IPCSDK | **Language:** Java

Start receiving ring controller data via IPC.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| callback | RingInfoCallback | Callback invoked with ring data JSON |

**Returns:** `void`

**Ring Data JSON Fields:**
```json
{
    "ring_connected": true,
    "ring_imu_status": "active",
    "quaternion": {
        "w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0
    }
}
```

**Cross-references:** `unRegisterRingInfo()`, `setRingIMU()`, `setRingLongClick()`, `setRingSeparateButton()`

---

### `RingIPCHelper.unRegisterRingInfo()`
Stop receiving ring data.

### `void setRingIMU(boolean enabled)`
Toggle IMU stream from the ring controller.

### `void setRingLongClick()`
Register for long-click events from the ring.

### `void setRingSeparateButton()`
Enable separate button event reporting from the ring.

---

# 7. Spatial Computing (SLAM, Anchors, OpenXR)

## 7.1 RayNeo 6DOF SLAM
**Source:** deep-reads/09-rayneo-docs.md

### `Algorithm.EnableSlamHeadTracker()`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

Start 6DOF SLAM tracking using the VGA camera for visual-inertial SLAM. Provides full 6DOF pose (position + rotation).

**Returns:** `void`

**Precautions:**
- Uses VGA camera; may conflict with ShareCamera if both use VGA simultaneously
- Requires well-lit environment for visual feature tracking
- CPU-intensive; monitor thermal state

**Cross-references:** `GetSlamStatus()`, `DisableSlamHeadTracker()`, `SlamState`

---

### `Algorithm.GetSlamStatus() -> SlamState`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

Poll the current SLAM tracking status.

**Returns:** `SlamState` enum value

---

### `Algorithm.DisableSlamHeadTracker()`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

Stop SLAM tracking and release camera/computation resources.

**Returns:** `void`

---

### `enum SlamState`
**Repo:** RayNeo ARDK | **Language:** C# (Unity)

```csharp
enum SlamState {
    INITIALIZING,       // SLAM warming up, collecting initial features
    TRACKING_SUCCESS,   // Tracking active and reliable
    TRACKING_FAIL       // Lost tracking (e.g., rapid motion, occlusion)
}
```

---

## 7.2 OpenXR Core Functions

### `xrCreateInstance(const XrInstanceCreateInfo*, XrInstance*) -> XrResult`
Create an OpenXR instance. Root object for all XR operations.

### `xrDestroyInstance(XrInstance) -> XrResult`
Destroy an OpenXR instance.

### `xrGetSystem(XrInstance, const XrSystemGetInfo*, XrSystemId*) -> XrResult`
Discover the XR system (HMD + controllers).

### `xrCreateSession(XrInstance, const XrSessionCreateInfo*, XrSession*) -> XrResult`
Create an XR session with graphics binding.

### `xrBeginSession(XrSession, const XrSessionBeginInfo*) -> XrResult`
Begin the session with view configuration.

### `xrEndSession(XrSession) -> XrResult`
End the active session.

### `xrCreateReferenceSpace(XrSession, const XrReferenceSpaceCreateInfo*, XrSpace*) -> XrResult`
Create a reference space. Types: VIEW (head-locked), LOCAL (recenterable), STAGE (room-scale), LOCAL_FLOOR, UNBOUNDED_MSFT.

### `xrLocateSpace(XrSpace, XrSpace, XrTime, XrSpaceLocation*) -> XrResult`
Locate one space relative to another at a given time. Returns pose with tracking confidence flags.

### `xrLocateSpaces(XrSession, const XrSpacesLocateInfo*, XrSpaceLocations*) -> XrResult`
Batch space location queries (OpenXR 1.1).

### `xrWaitFrame(XrSession, const XrFrameWaitInfo*, XrFrameState*) -> XrResult`
Wait for the next frame. Returns predicted display time.

### `xrBeginFrame(XrSession, const XrFrameBeginInfo*) -> XrResult`
Signal start of frame rendering.

### `xrEndFrame(XrSession, const XrFrameEndInfo*) -> XrResult`
Submit rendered layers. Supports: PROJECTION, QUAD, CYLINDER, EQUIRECT, PASSTHROUGH layers.

### `xrLocateViews(XrSession, const XrViewLocateInfo*, XrViewState*, uint32_t, uint32_t*, XrView*) -> XrResult`
Get per-eye view poses and field of view.

### `xrSyncActions(XrSession, const XrActionsSyncInfo*) -> XrResult`
Synchronize action state with the runtime.

### `xrApplyHapticFeedback(XrSession, const XrHapticActionInfo*, const XrHapticBaseHeader*) -> XrResult`
Apply haptic feedback to a controller.

---

## 7.3 Monado XR Runtime
**Source:** deep-reads/08-monado-specs.md

### `struct xrt_device`
**Repo:** Monado | **File:** src/xrt/include/xrt/xrt_device.h | **Language:** C

Central device interface with 25+ method pointers. Represents both HMDs and input devices.

**Data Members:**
| Field | Type | Description |
|-------|------|-------------|
| name | enum xrt_device_name | Device identifier (50+ entries) |
| device_type | enum xrt_device_type | HMD, controller, tracker, etc. |
| str[256] | char | Human-readable description |
| serial[256] | char | Unique serial number |
| hmd | xrt_hmd_parts* | HMD-specific data (null for controllers) |
| tracking_origin | xrt_tracking_origin* | Tracking system origin |
| inputs | xrt_input* | Array of input bindings |
| outputs | xrt_output* | Array of output bindings |
| supported | xrt_device_supported | Capability flags |

**Methods (function pointers):**
| Method | Description |
|--------|-------------|
| `update_inputs(xdev)` | Refresh all input state |
| `get_tracked_pose(xdev, name, timestamp, *out)` | Get 6DoF pose at timestamp |
| `get_hand_tracking(xdev, name, timestamp, *out_value, *out_ts)` | Get 26-joint hand skeleton |
| `get_face_tracking(xdev, type, timestamp, *out)` | Get facial expressions |
| `get_body_joints(xdev, type, timestamp, *out)` | Get full body tracking |
| `set_output(xdev, name, *value)` | Set haptic output |
| `begin_plane_detection_ext(xdev, ...)` | Start plane detection |
| `get_plane_detections_ext(xdev, id, *out)` | Get detected planes |
| `compute_distortion(xdev, view, u, v, *out)` | Compute lens distortion |
| `get_battery_status(xdev, *present, *charging, *charge)` | Battery level query |
| `set_brightness(xdev, brightness, relative)` | Set display brightness |
| `get_view_poses(xdev, ...)` | Get per-eye view poses |
| `get_visibility_mask(xdev, type, view_index, **out)` | Get visibility mask |
| `get_presence(xdev, *presence)` | Check if user is present |

**Capability Flags (xrt_device_supported):**
orientation_tracking, position_tracking, hand_tracking, eye_gaze, presence, force_feedback, ref_space_usage, form_factor_check, stage, face_tracking, body_tracking, battery_status, brightness_control, planes

---

### `struct xrt_space_overseer`
**Repo:** Monado | **File:** src/xrt/include/xrt/xrt_space.h | **Language:** C

Manages all XR spaces in the system.

**Semantic Spaces:**
- `root` — Always available base space
- `view` — Head-tracking space
- `local` — Recenterable local space
- `local_floor` — Floor-level local space
- `stage` — Room-scale space with boundaries
- `unbounded` — SLAM-based unbounded tracking

**Methods (15+):**
| Method | Description |
|--------|-------------|
| `create_offset_space(parent, *offset, **out)` | Create space at offset from parent |
| `create_pose_space(xdev, name, **out)` | Create space tracking device pose |
| `locate_space(base, *offset, at_ns, space, *offset, *out)` | Locate one space relative to another |
| `locate_spaces(base, *offset, at_ns, **spaces, count, *offsets, *out)` | Batch locate multiple spaces |
| `locate_device(base, *offset, at_ns, xdev, *out)` | Locate device in a space |
| `recenter_local_spaces()` | Recenter all local spaces to current head position |
| `ref_space_inc/dec(type)` | Reference counting for space types |
| `get_tracking_origin_offset(xto, *out)` | Get tracking origin offset |
| `set_tracking_origin_offset(xto, *offset)` | Set tracking origin offset |
| `get_reference_space_offset(type, *out)` | Get reference space offset |
| `set_reference_space_offset(type, *offset)` | Set reference space offset |
| `create_local_space(**out_local, **out_local_floor)` | Create local + local_floor pair |
| `add_device(xdev)` | Add device to space system |
| `attach_device(xdev, space)` | Attach device to specific space |

---

### `struct xrt_compositor`
**Repo:** Monado | **File:** src/xrt/include/xrt/xrt_compositor.h | **Language:** C

Graphics compositor interface for submitting rendered frames.

**Layer Types (8):**
| Layer | Description |
|-------|-------------|
| XRT_LAYER_PROJECTION | Standard stereo projection |
| XRT_LAYER_PROJECTION_DEPTH | Projection with depth buffer |
| XRT_LAYER_QUAD | Flat quad in 3D space |
| XRT_LAYER_CUBE | Cubemap (skybox) |
| XRT_LAYER_CYLINDER | Curved cylinder surface |
| XRT_LAYER_EQUIRECT1 | Equirectangular (v1) |
| XRT_LAYER_EQUIRECT2 | Equirectangular (v2) |
| XRT_LAYER_PASSTHROUGH | Camera passthrough |

---

### libmonado API v1.7.0
**Source:** deep-reads/08-monado-specs.md

Control interface for managing Monado service externally (30+ functions).

**Key Functions:**
| Function | Description |
|----------|-------------|
| `mnd_api_get_version(*major, *minor, *patch)` | Get API version |
| `mnd_root_create(**out_root)` | Create root handle |
| `mnd_root_destroy(**root_ptr)` | Destroy root handle |
| `mnd_root_update_client_list(root)` | Refresh client list |
| `mnd_root_get_number_clients(root, *out)` | Get client count |
| `mnd_root_get_client_id_at_index(root, idx, *out)` | Get client ID |
| `mnd_root_get_client_name(root, id, **out)` | Get client name |
| `mnd_root_get_client_state(root, id, *out)` | Get client state flags |
| `mnd_root_set_client_primary(root, id)` | Set primary client |
| `mnd_root_set_client_focused(root, id)` | Set focused client |
| `mnd_root_get_device_count(root, *out)` | Get device count |
| `mnd_root_get_device_info_*(root, idx, prop, *out)` | Get device properties (bool/i32/u32/float/string) |
| `mnd_root_get_device_from_role(root, role, *out)` | Get device by role name |
| `mnd_root_recenter_local_spaces(root)` | Recenter all local spaces |
| `mnd_root_get/set_reference_space_offset(root, type, *offset)` | Reference space offset |
| `mnd_root_get/set_tracking_origin_offset(root, idx, *offset)` | Tracking origin offset |
| `mnd_root_get_device_battery_status(root, idx, ...)` | Battery status |
| `mnd_root_get/set_device_brightness(root, idx, ...)` | Display brightness |

**Role Names:** "head", "left", "right", "gamepad", "eyes", "hand-tracking-unobstructed-left/right", "hand-tracking-conforming-left/right"

---

# 8. ML/AI On-Device

## 8.1 Frame TFLite Micro

### `tflm_status_t tflm_initialize(void)`
Initialize TFLite Micro runtime for hello world float model.

### `tflm_status_t tflm_infer(float input, float* output)`
Run inference on hello world float model.

### `tflm_status_t fomo_initialize(void)`
Initialize FOMO (Faster Objects, More Objects) detection model.

### `tflm_status_t fomo_infer(const uint8_t* input_grayscale, int8_t* output_grid)`
Run FOMO object detection on grayscale image.

### `tflm_status_t person_detect_initialize(void)`
Initialize person detection (Visual Wake Words) model.

### `tflm_status_t person_detect_infer(const uint8_t* input_image, int8_t* output_scores)`
Run person detection inference.

---

# 9. GPS & Geolocation

## 9.1 RayNeo GPS via IPCSDK
**Source:** deep-reads/09-rayneo-docs.md

### `GPSIPCHelper.registerGPSInfo(callback)`
**Repo:** RayNeo IPCSDK | **Language:** Java

Start receiving GPS data stream from tethered phone via IPC.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| callback | GPSInfoCallback | Callback invoked with GPS JSON data |

**Returns:** `void`

**GPS JSON Fields:**
```json
{
    "mLatitude": 37.7749,
    "mLongitude": -122.4194,
    "mAltitude": 10.5,
    "mSpeed": 1.2,
    "mBearing": 180.0,
    "mProvider": "gps",
    "mTime": 1713636000000,
    "mHorizontalAccuracyMeters": 3.5
}
```

**Precautions:**
- Requires phone tethered connection (check `MobileState.isMobileConnected()` first)
- GPS data comes from phone, not glasses (glasses have no GPS hardware)
- Update frequency depends on phone's GPS settings

**Cross-references:** `unRegisterGPSInfo()`, `MobileState.isMobileConnected()`

---

### `GPSIPCHelper.unRegisterGPSInfo()`
Stop GPS data stream.

### `MobileState.isMobileConnected() -> boolean`
Check if phone is tethered to glasses.

---

## 9.2 Mercury SDK (Dev Setup)
**Source:** deep-reads/09-rayneo-docs.md

### `mercury_install_allowed`
**Repo:** RayNeo Platform | **Language:** ADB Shell

Enable developer mode on RayNeo glasses for sideloading custom APKs.

**Command:**
```bash
adb shell settings put global mercury_install_allowed 1
```

**Notes:** Mercury is RayNeo's Android runtime/launcher system. This setting is required for sideloading during development.

---

# 10. Device Management & Connectivity

## 10.1 Universal Connection API

### `GlassesClient.connect() -> Result<Unit>`
Establish connection to the glasses. Transport varies by device (BLE, USB, Wi-Fi).

### `GlassesClient.disconnect()`
Tear down connection. Safe to call multiple times.

### `sealed class ConnectionState`
- `Disconnected` — Not connected
- `Connecting` — Connection in progress
- `Connected` — Active connection
- `Error(error: GlassesError)` — Connection error

### `sealed class GlassesError`
- `NotConnected` — Not connected to device
- `PermissionDenied` — Required permissions not granted
- `Busy` — Device is busy
- `Timeout(operation: String)` — Operation timed out
- `Transport(detail: String, raw: Throwable?)` — Transport-layer error
- `Unsupported(detail: String)` — Feature not supported

---

## 10.2 Device Capability Matrix

| Field | Rokid | Meta | Omi | Frame | RayNeo | Simulator |
|-------|-------|------|-----|-------|--------|-----------|
| canCapturePhoto | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| canDisplayText | ✔ | ✘ | ✘ | ✔ | ✔ | ✔ |
| canRecordAudio | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| canPlayTts | ✔ | ✘ | ✘ | ✘ | ✘ | ✔ |
| canPlayAudioBytes | ✔ | ✔ | ✘ | ✘ | ✔ | ✘ |
| supportsTapEvents | ✘ | ✘ | ✘ | ✔ | ✘ | ✘ |

---

# 11. 3D Environment (StardustXR)
**Source:** deep-reads/05-stardustxr.md

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
pub async fn sync_event_loop<F: FnMut(&Arc<ClientHandle>, &mut ControlFlow)>(mut self, f: F);
pub fn async_event_loop(mut self) -> AsyncEventLoop;
```

**Connection:** Via Unix socket at `$STARDUST_INSTANCE` or `stardust-0` in XDG_RUNTIME_DIR.

---

### `struct Transform`
```rust
pub struct Transform {
    pub translation: Option<Vector3<f32>>,
    pub rotation: Option<Quaternion>,
    pub scale: Option<Vector3<f32>>,
}
impl Transform {
    pub const fn none() -> Self;
    pub const fn identity() -> Self;
    pub fn from_translation(t: impl Into<Vector3<f32>>) -> Self;
    pub fn from_rotation(r: impl Into<Quaternion>) -> Self;
    pub fn from_scale(s: impl Into<Vector3<f32>>) -> Self;
    pub fn from_translation_rotation(t, r) -> Self;
    pub fn from_rotation_scale(r, s) -> Self;
    pub fn from_translation_rotation_scale(t, r, s) -> Self;
}
```

---

## 11.2 Spatial Hierarchy (KDL Protocol)

### Aspect Hierarchy
```
Owned
├── set_enabled(bool)
└── destroy()

SpatialRef
├── get_local_bounding_box() -> BoundingBox
├── get_relative_bounding_box(relative_to) -> BoundingBox
└── get_transform(relative_to) -> Transform

Spatial : Owned + SpatialRef
├── set_local_transform(Transform)
├── set_relative_transform(relative_to, Transform)
├── set_spatial_parent(parent)
├── set_spatial_parent_in_place(parent)
└── export_spatial() -> u64

FieldRef : SpatialRef
├── distance(space, point) -> f32
├── normal(space, point) -> Vec3
├── closest_point(space, point) -> Vec3
└── ray_march(space, origin, direction) -> RayMarchResult

Field : Spatial + FieldRef
├── set_shape(Shape)
└── export_field() -> u64
```

---

## 11.3 Drawables

### `impl Lines`
```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              lines: &[Line]) -> NodeResult<Self>;
pub fn set_lines(&self, lines: &[Line]) -> NodeResult<()>;
```

### `impl Model`
```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              model_resource: &ResourceID) -> NodeResult<Self>;
pub fn part(&self, relative_path: &str) -> NodeResult<ModelPart>;
```

### `impl Text`
```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              text: &str, style: TextStyle) -> NodeResult<Self>;
pub fn set_text(&self, text: &str) -> NodeResult<()>;
pub fn set_character_height(&self, height: f32) -> NodeResult<()>;
```

### `impl Sound`
```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              resource: &ResourceID) -> NodeResult<Self>;
pub fn play(&self) -> NodeResult<()>;
pub fn stop(&self) -> NodeResult<()>;
```

---

## 11.4 Fields (Signed Distance Fields)

### `impl Field`
```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              shape: Shape) -> NodeResult<Self>;
```

**Shape Union:**
- `Box(Vec3)` — Box with half-extents
- `Sphere(f32)` — Sphere with radius
- `Cylinder(CylinderShape)` — Cylinder
- `Torus(TorusShape)` — Torus
- `Spline(CubicSplineShape)` — Cubic spline tube

**Field Operations:**
- `distance(space, point) -> f32` — SDF evaluation
- `normal(space, point) -> Vec3` — Surface normal
- `closest_point(space, point) -> Vec3` — Nearest surface point
- `ray_march(space, origin, direction) -> RayMarchResult`

---

## 11.5 Input System

### `impl InputMethod`
```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              input_type: InputDataType, datamap: &Datamap) -> NodeResult<Self>;
pub fn update_state(&self, input: InputDataType, datamap: Datamap);
```

**InputDataType Union:** Pointer, Hand (26 joints), Tip

### Hand Heuristic Methods
```rust
impl Hand {
    pub fn palm_normal(&self) -> Vector3<f32>;
    pub fn radial_axis(&self) -> Vector3<f32>;
    pub fn distal_axis(&self) -> Vector3<f32>;
    pub fn finger_curl(&self, finger: &Finger) -> f32;
    pub fn thumb_curl(&self) -> f32;
    pub fn pinch_distance(&self, finger: &Finger) -> f32;
    pub fn pinch_position(&self) -> Vector3<f32>;
    pub fn stable_pinch_position(&self) -> Vector3<f32>;
    pub fn predicted_pinch_position(&self) -> Vector3<f32>;
    pub fn pinch_strength(&self) -> f32;
    pub fn fist_strength(&self) -> f32;
}
```

### `impl InputHandler`
```rust
pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform,
              field: &impl FieldAspect) -> NodeResult<Self>;
```
Events: `input_sent`, `input_updated`, `input_left`

---

## 11.6 Flatland — Wayland Panel Shell

### `struct PanelWrapper<State>`
```rust
pub fn new(panel_item: PanelItem) -> Self;
pub fn on_toplevel_title_changed(self, f: impl Fn(&mut State, String)) -> Self;
pub fn on_toplevel_size_changed(self, f: impl Fn(&mut State, Vector2<u32>)) -> Self;
pub fn on_toplevel_move_request(self, f: impl Fn(&mut State)) -> Self;
pub fn on_set_cursor(self, f: impl Fn(&mut State, Geometry)) -> Self;
pub fn on_create_child(self, f: impl Fn(&mut State, u64, ChildInfo)) -> Self;
```

### `struct PointerPlane<State>`
```rust
pub fn on_mouse_button(self, f: impl Fn(&mut State, MouseEvent)) -> Self;
pub fn on_pointer_motion(self, f: impl Fn(&mut State, Vec2)) -> Self;
pub fn on_scroll(self, f: impl Fn(&mut State, MouseEvent)) -> Self;
```

### `struct TouchPlane<State>`
```rust
pub fn on_touch_down(self, f: impl Fn(&mut State, u32, Vec2)) -> Self;
pub fn on_touch_move(self, f: impl Fn(&mut State, u32, Vec2)) -> Self;
pub fn on_touch_up(self, f: impl Fn(&mut State, u32)) -> Self;
```

### `struct GrabBall<H: GrabBallHead>`
```rust
pub fn create(client, parent, settings, offset, head) -> NodeResult<Self>;
pub fn update(&mut self);
pub fn pos(&self) -> &Vec3;
pub fn set_enabled(&mut self, enabled: bool);
```

---

## 11.7 Protostar — App Launchers

### `struct Application`
```rust
pub fn create(desktop_file: DesktopFile) -> Result<Self>;
pub fn name(&self) -> Option<&str>;
pub fn categories(&self) -> &[String];
pub fn icon(&self, preferred_px_size: u16, prefer_3d: bool) -> Option<Icon>;
pub fn launch<T: SpatialRefAspect + Clone>(&self, launch_space: &T) -> NodeResult<()>;
```

### `struct DesktopFile`
```rust
pub fn parse(path: PathBuf) -> Result<Self, String>;
pub fn get_icon(&self, preferred_px_size: u16) -> Option<Icon>;
```

### `pub fn get_desktop_files() -> impl Iterator<Item = PathBuf>`
Scan XDG data directories for .desktop files.

### `struct Hex { q: isize, r: isize, s: isize }`
```rust
pub fn new(q, r, s) -> Self;
pub fn get_coords(&self) -> [f32; 3];
pub fn neighbor(self, direction: usize) -> Self;
pub fn spiral(i: usize) -> Self;
```

---

## 11.8 StardustXR Wire Protocol

**Transport:** Unix domain sockets with FD passing (SCM_RIGHTS)
**Header:** 4 bytes (u32 body_length)
**Body:** FlatBuffers message
**Message types:** Error(0), Signal(1), MethodCall(2), MethodReturn(3)
**Fields:** type_, message_id, node_id, aspect, method, error, data

### `pub async fn connect() -> Result<UnixStream, std::io::Error>`
Connect to StardustXR server via `$STARDUST_INSTANCE` or `stardust-0`.

### `pub fn serialize<S: Serialize>(value: &S) -> Result<(Vec<u8>, Vec<OwnedFd>), FlexSerializeError>`
Serialize data with FlexBuffers + file descriptor passing.

### `pub fn deserialize<'a, T: Deserialize<'a>>(data: &'a [u8], fds: impl IntoIterator<Item=OwnedFd>) -> Result<T>`
Deserialize FlexBuffer data with file descriptor reconstruction.

---

## 11.9 Gluon D-Bus Registry

### `impl ObjectRegistry`
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
**Source:** deep-reads/10-geo-maps.md

## 12.1 Overpass API (OpenStreetMap)

### API Endpoints
- **Main query:** `https://overpass-api.de/api/interpreter` (POST or GET)
- **Abort:** `https://overpass-api.de/api/kill_my_queries`
- **Status:** `https://overpass-api.de/api/status`
- **Nominatim geocoding:** `https://nominatim.openstreetmap.org/search?format=json&q={search}`

### Query Template Shortcuts
| Template | Description |
|----------|-------------|
| `{{bbox}}` | Current map bounding box (s,w,n,e) |
| `{{center}}` | Map center coordinates (lat,lng) |
| `{{date:offset}}` | Relative date (e.g., `{{date:-1day}}`, `{{date:-6months}}`) |
| `{{geocodeId:name}}` | Nominatim lookup → type(id) |
| `{{geocodeArea:name}}` | Area ID (+2400000000 for ways, +3600000000 for relations) |
| `{{geocodeBbox:name}}` | Bounding box from Nominatim |
| `{{geocodeCoords:name}}` | Lat/lon from Nominatim |
| `{{radius=1000}}` | User-defined constant (default 1000m) |

### Query Clause Types
| Type | Syntax | Description |
|------|--------|-------------|
| `key` | `["key"]` | Has tag |
| `nokey` | `["key"!~".*"]` | Does not have tag |
| `eq` | `["key"="value"]` | Exact match |
| `neq` | `["key"!="value"]` | Not equal |
| `like` | `["key"~"regex"]` | Regex match |
| `notlike` | `["key"!~"regex"]` | Negative regex |
| `meta/id` | `(id_number)` | Filter by OSM ID |
| `meta/newer` | `(newer:"date")` | Filter by timestamp |

### Example Queries for AR Glasses

**Nearby restaurants:**
```
[out:json][timeout:25];
nwr["amenity"="restaurant"](around:500,{user_lat},{user_lng});
out geom;
```

**All POIs in view:**
```
[out:json][timeout:25];
(node["amenity"]({{bbox}});
 node["shop"]({{bbox}});
 node["tourism"]({{bbox}}););
out geom;
```

**Walking paths:**
```
[out:json][timeout:15];
way["highway"~"footway|pedestrian|path|steps"](around:500,{LAT},{LNG});
out geom;
```

**Emergency services:**
```
[out:json][timeout:10];
(node["amenity"="hospital"](around:2000,{LAT},{LNG});
 node["amenity"="pharmacy"](around:1000,{LAT},{LNG});
 node["amenity"="police"](around:2000,{LAT},{LNG}););
out body;
```

---

## 12.2 Gemini Maps Grounding

### Configuration JSON
```json
{
  "contents": [{"parts": [{"text": "Restaurants near Times Square."}]}],
  "tools": {"googleMaps": {}},
  "toolConfig": {
    "retrievalConfig": {
      "latLng": {"latitude": 40.758896, "longitude": -73.985130}
    }
  }
}
```

### Python SDK Usage
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

### Response Fields
| Field | Description |
|-------|-------------|
| `groundingChunks[].maps.uri` | Google Maps link |
| `groundingChunks[].maps.title` | Place name |
| `groundingChunks[].maps.placeId` | Google Place ID |
| `groundingSupports[].segment` | Text spans linked to sources |
| `googleMapsWidgetContextToken` | Token for interactive widget |

### Supported Models
Gemini 3.1 Pro/Flash-Lite Preview, Gemini 3 Flash Preview, Gemini 2.5 Pro/Flash/Flash-Lite, Gemini 2.0 Flash

### Pricing
- **$25 per 1,000 grounded prompts**
- **Free tier: 500 requests/day**
- Only counted when prompt successfully returns grounded results

### Widget Rendering
```html
<gmp-place-contextual context-token="{widget_token}"></gmp-place-contextual>
```

---

## 12.3 Niantic Spatial VPS

Visual Positioning System for centimeter-level AR anchoring.

**Capabilities:**
- Visual Positioning System (VPS) for cm-level accuracy
- Gaussian Splat rendering for photorealistic 3D
- Semantic understanding of scanned environments
- SPZ format — Open-source, 90% file size reduction
- On-demand data capture service for large areas
- SDK: `nianticspatial.com/docs/`

---

## 12.4 AR Glasses Integration Patterns

### Pattern 1: Overpass API for POI Overlay
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
    return response.json(); // {elements: [{type, id, lat, lon, tags}...]}
}
```

### Pattern 2: Gemini Maps for Contextual Questions
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

### Rate Limits
| Service | Rate Limit | Cost | Best For |
|---------|-----------|------|----------|
| Overpass API | ~10K/day (fair use) | Free | Structural map data, bulk POI |
| Gemini Maps | 500/day free | $25/1K | AI place questions |
| Nominatim | 1 req/sec | Free | Geocoding |
| Niantic Spatial | SDK-based | Varies | 3D positioning |

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
int register_raw_callback(XRDeviceProviderHandle handle, VitureImuRawCallback cb);
int register_pose_callback(XRDeviceProviderHandle handle, VitureImuPoseCallback cb);
int open_imu(XRDeviceProviderHandle handle, uint8_t mode, uint8_t freq);
int close_imu(XRDeviceProviderHandle handle, uint8_t mode);
```

## A.3 XREAL HID Protocol
```
Vendor ID: 0x3318
Product IDs: 0x0424 (Air), 0x0428 (Air 2), 0x0432 (Air 2 Pro), 0x0426 (Air 2 Ultra)
IMU: 1000Hz native via HID reports
Display: USB-C DisplayPort Alt Mode
```

---

# Appendix B: Monado Error Codes (Complete)
**Source:** deep-reads/08-monado-specs.md

| Code | Name |
|------|------|
| 0 | XRT_SUCCESS |
| 2 | XRT_TIMEOUT |
| 3 | XRT_SPACE_BOUNDS_UNAVAILABLE |
| -1 | XRT_ERROR_IPC_FAILURE |
| -2 | XRT_ERROR_NO_IMAGE_AVAILABLE |
| -3 | XRT_ERROR_VULKAN |
| -7 | XRT_ERROR_ALLOCATION |
| -8 | XRT_ERROR_POSE_NOT_ACTIVE |
| -22 | XRT_ERROR_DEVICE_CREATION_FAILED |
| -26 | XRT_ERROR_RECENTERING_NOT_SUPPORTED |
| -29 | XRT_ERROR_NOT_IMPLEMENTED |
| -32 | XRT_ERROR_FEATURE_NOT_SUPPORTED |
| -39 | XRT_ERROR_INVALID_ARGUMENT |
| -44 | XRT_ERROR_UNSUPPORTED_VIEW_TYPE |

(44 total error codes — see deep-reads/08-monado-specs.md for complete list)

---

# Appendix C: Monado Driver List (38 drivers)
**Source:** deep-reads/08-monado-specs.md

| Driver | Description |
|--------|-------------|
| xreal_air | XREAL Air/Air2/Air2Pro/Air2Ultra |
| wmr | Windows Mixed Reality |
| survive | Valve Lighthouse (libsurvive) |
| rift_s | Oculus Rift S |
| psvr / psvr2 | PlayStation VR 1/2 |
| hydra | Razer Hydra |
| realsense | Intel RealSense |
| depthai | Luxonis DepthAI |
| north_star | Leap Motion North Star |
| rokid | Rokid glasses |
| ultraleap_v2/v5 | Leap Motion hand tracking |
| qwerty | Keyboard-driven testing |
| simulated | Simulated HMD |
| v4l2 | V4L2 camera |

---

# Appendix D: RayNeo Capabilities Matrix
**Source:** deep-reads/09-rayneo-docs.md

| Capability | X2 | X3 Pro | API Layer |
|------------|-----|--------|-----------|
| 3DOF | ✓ | ✓ | HeadTrackedPoseDriver |
| 6DOF SLAM | ✓ | - | Algorithm.EnableSlamHeadTracker |
| Gaze Ray | ✓ | ✓ | XRGraphicRaycaster |
| Face Detection | ✓ | ✓ | CV + DL pipeline |
| GPS (via phone) | ✓ | ✓ | GPSIPCHelper |
| Ring Control | - | ✓ | RingIPCHelper |
| Temple Touch | ✓ | ✓ | TouchDispatcher |
| Camera | ✓ | ✓ | ShareCamera |
| Audio Capture | ✓ | ✓ | AudioManager |
| Binocular 3D | ✓ | ✓ | make3DEffect() |

---

# Appendix E: Cross-Reference Tables

## E.1 SDK-to-Use-Case Matrix

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

## E.2 Glasses Protocol Compatibility

| Glasses | Protocol | Interface | VID:PID |
|---------|----------|-----------|---------|
| XREAL Air | HID v3 | USB/WebHID | 0x3318:0x0424 |
| XREAL Air 2 | HID v3 | USB | 0x3318:0x0428 |
| XREAL Air 2 Ultra | HID v3 + SLAM | USB | 0x3318:0x0426 |
| XREAL Light | HID | USB/WebHID | 0x0486:0x573C |
| RayNeo X2/X3 | OpenXR ARDK | Unity/Android | 0x1BBB:0xAF50 |
| Rokid Max/Air | CXR-M SDK | BLE+Wi-Fi | — |
| VITURE One/Pro | Native SDK | USB | 0x35CA:various |
| Brilliant Frame | BLE + Lua | nRF52840 | N/A |
| Meta Ray-Ban | DAT SDK | Bluetooth | N/A |
| Omi Glass | BLE GATT | nRF52 | N/A |

---

# Appendix F: Protocol Reference

## F.1 StardustXR Wire Protocol
```
Transport: Unix domain sockets with FD passing (SCM_RIGHTS)
Header: 4 bytes (u32 body_length)
Body: FlatBuffers message
Message types: Error(0), Signal(1), MethodCall(2), MethodReturn(3)
```

## F.2 OpenTrack UDP Protocol
```
Target: configurable IP:port (default 127.0.0.1:4242)
Payload: 48 bytes = 6 × double (little-endian)
  [0] x, [1] y, [2] z, [3] yaw, [4] pitch, [5] roll
```

## F.3 XREAL Air HID Protocol
```
MCU (interface 4): 0xFD header, CRC32, 2-byte length, 8-byte timestamp, 2-byte msgId
IMU (interface 3): 0xAA header, CRC32, 2-byte length, 1-byte msgId
IMU magic start payload: { 0xaa, 0xc5, 0xd1, 0x21, 0x42, 0x04, 0x00, 0x19, 0x01 }
```

## F.4 Breezy Desktop IPC Binary Protocol
```
File: /dev/shm/breezy_desktop_imu
Layout version 5: config header + IMU record with parity byte
Config: version, enabled, look_ahead[4], display_res[2], fov, lens_ratio, sbs, banner
IMU: smooth_follow_enabled, orientation[16], position[3], epoch_ms, parity
```

---

# Appendix G: MentraOS Complete API

## G.1 AppServer & AppSession

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

### `class AppSession`
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

## G.2 CoreModule (React Native Bridge)
```typescript
getGlassesStatus(): GlassesStatus
getCoreStatus(): CoreStatus
connectDefault(): void
connectByName(deviceName: string): void
connectSimulated(): void
disconnect(): void
displayEvent(params: DisplayEventParams): void
displayText(params: DisplayTextParams): void
clearDisplay(): void
requestWifiScan(): void
sendWifiCredentials(ssid: string, password: string): void
photoRequest(requestId, appId, size, webhookUrl, authToken, compress, flash, sound): void
startVideoRecording(requestId, save, flash, sound): void
stopVideoRecording(requestId): void
setMicState(sendPcmData, sendTranscript, bypassVad): void
rgbLedControl(requestId, packageName, action, color, ...): void
```

## G.3 Stream Types
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
```

---

# Appendix H: RayDesk Streaming API

## H.1 MoonlightBridge
```kotlin
class MoonlightBridge(context: Context, decoderSurface: SurfaceProvider)
```
**Methods:**
| Method | Description |
|--------|-------------|
| `initializeDecoder(width, height, format)` | Init hardware decoder |
| `setStreamConfig(config: StreamConfig)` | Configure stream |
| `connect(address, port, uniqueId, ...)` | Connect to server |
| `disconnect()` | End stream |
| `sendAbsolutePosition(x, y, refW, refH)` | Send cursor |
| `sendMouseMove(dx, dy)` | Relative mouse |
| `sendKeyboard(keyCode, pressed)` | Keyboard event |
| `sendScroll(dx, dy)` | Scroll event |

## H.2 StreamConfig
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

# Appendix I: Frame Firmware Low-Level APIs

## I.1 System Lua API
```lua
frame.update()              -- Process pending events
frame.sleep(seconds)        -- Sleep for duration
frame.stay_awake(enable)    -- Prevent auto-sleep
frame.battery_level()       -- Read battery percentage
frame.fpga_read(addr, len)  -- Read FPGA register
frame.fpga_write(addr, data)-- Write FPGA register
frame.time.utc()            -- UTC timestamp
frame.time.zone()           -- Timezone offset
frame.time.date()           -- Date string
frame.file.open(path, mode) -- Open file (LittleFS)
frame.file.read(handle, bytes)  -- Read bytes
frame.file.write(handle, data)  -- Write data
frame.file.close(handle)        -- Close file
frame.file.remove(path)         -- Delete file
frame.file.mkdir(path)          -- Create directory
frame.file.listdir(path)        -- List directory
frame.led.set_color(r, g, b)   -- Set LED color
frame.imu                       -- Callback-based sensor data
```

## I.2 Flash & SPI
```c
void flash_erase_page(uint32_t address);
void flash_write(uint32_t address, const uint32_t* data, size_t length);
void flash_wait_until_complete(void);
void flash_get_info(size_t* page_size, size_t* total_size);
void spi_configure(void);
void spi_read(spi_device_t device, uint8_t* tx, uint8_t* rx, size_t len);
void spi_write(spi_device_t device, uint8_t* tx, size_t len);
```

---

# Appendix J: XRLinuxDriver Plugin System

## J.1 Plugin Interface
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

## J.2 Registered Plugins (11 total)
1. **device_license** — License key management
2. **virtual_display** — Head-locked virtual screen + IPC
3. **sideview** — Follow-mode display
4. **smooth_follow** — Slerp-based screen follow
5. **breezy_desktop** — Wayland compositor integration via /dev/shm
6. **gamescope_reshade_wayland** — SteamOS shader injection
7. **neck_saver** — Ergonomic posture alerts
8. **opentrack_source** — Sends UDP: 6 doubles (x,y,z,yaw,pitch,roll)
9. **opentrack_listener** — Receives OpenTrack UDP as synthetic IMU

---

# Appendix K: Encryption & Security (Pebble Ring)

```kotlin
actual object AesGcmCrypto {
    actual fun encrypt(plaintext: ByteArray, keyBase64: String): ByteArray
    actual fun decrypt(ivAndCiphertext: ByteArray, keyBase64: String): ByteArray
    actual fun keyFingerprint(keyBase64: String): String
}

actual class EncryptionKeyManager {
    actual fun generateKey(): KeyResult
    actual suspend fun saveKeyLocally(key: String, email: String)
    actual suspend fun getLocalKey(email: String): String?
    actual suspend fun saveToCloudKeychain(uiContext: Any, key: String)
    actual suspend fun readFromCloudKeychain(uiContext: Any): String?
}
```

---

# Appendix L: Open Wearables MCP & Health Algorithms

## L.1 MCP Tools
- `get_users(search?, limit=10) -> dict`
- `get_activity_summary(user_id, start_date, end_date) -> dict`
- `get_sleep_summary(user_id, start_date, end_date) -> dict`
- `get_workout_events(user_id, start_date, end_date) -> dict`
- `get_timeseries(user_id, series_type, start_date, end_date) -> dict`

## L.2 Sleep Scoring
- `calculate_duration_score(start, end, awake_minutes) -> int`
- `calculate_total_stages_score(deep_minutes, rem_minutes) -> int`
- `calculate_bedtime_consistency_score(...) -> int`
- `calculate_overall_sleep_score(duration, stages, bedtime, interruptions) -> int`

## L.3 HRV Algorithms
- `hr_to_rr_intervals_ms(hr_series) -> ndarray`
- `calculate_rmssd(hr_series) -> float`
- `calculate_sdnn(hr_series) -> float`
- `calculate_hrv_cv(hrv_series) -> float`

---

# Appendix M: headset-utils Device Drivers

## M.1 NrealAir (XREAL Air/Air2/Air2Pro)
```rust
pub struct NrealAir { model: AirModel, device: HidDevice, ... }
// VID=0x3318, AIR_PID=0x0424, AIR2_PID=0x0428, AIR2PRO_PID=0x0432
// IMU: 0x80-byte packets, header [1,2], 24-bit signed gyro/accel
// Axis remap: X=-gyro_x, Y=gyro_z, Z=gyro_y
// MCU protocol: 0xFD header, CRC32, cmd_id
// IMU protocol: 0xAA header, CRC32, cmd_id
```

## M.2 RokidAir (Rokid Air/Max)
```rust
pub struct RokidAir { device_handle: DeviceHandle, model: RokidModel, ... }
// VID=0x04d2, PID=0x162f, Endpoint=0x82
// Combined packets (type=17) for Max: accel+gyro+mag+keys
// display_fov: Air=20°, Max=23°
```

## M.3 NrealLight (XREAL Light)
```rust
pub struct NrealLight { device: HidDevice, ov580: Ov580, ... }
// MCU: VID=0x0486, PID=0x573c
// OV580: VID=0x05a9, PID=0x0680
// Heartbeat required every 250ms in SBS mode
// SLAM cameras: 640x480 grayscale left+right
```

## M.4 GrawoowG530 / MadGazeGlow
```rust
// GrawoowG530: VID=0x1ff7, PID=0x0ff4
// MadGazeGlow: Serial 921600 baud, VID=1204, PID=2
//   AK09911 magnetometer, BMI160 accel/gyro
```

---

# Appendix N: XREAL HID Commands (real_utilities)

## N.1 MCU Commands (protocol v1)
| Command | Hex | Description |
|---------|-----|-------------|
| W_CANCEL_ACTIVATION | 0x19 | Cancel activation |
| R_MCU_APP_FW_VERSION | 0x26 | MCU firmware version |
| R_GLASSID | 0x15 | Glass hardware ID |
| W_DISP_MODE | 0x08 | Set display mode |
| HEARTBEAT | 0x1A | Keep-alive heartbeat |
| P_BUTTON_PRESSED | 0x6C05 | Button event |

## N.2 IMU Commands (protocol v3)
| Command | Hex | Description |
|---------|-----|-------------|
| GET_CAL_DATA_LENGTH | 0x14 | Get calibration data length |
| CAL_DATA_GET_NEXT_SEGMENT | 0x15 | Get next calibration segment |
| START_IMU_DATA | 0x19 | Start/stop IMU stream (0x01=start) |
| GET_STATIC_ID | 0x1A | Get static ID (returns 0x01012220) |

---

# Appendix O: xg-glass CLI Tool

```bash
xg-glass init <path>     # Initialize new project from template
xg-glass build            # Build the project (assembleDebug)
xg-glass install          # Install APK to device
xg-glass run [file]       # Run app (optionally single Kotlin file)
```

Options: `--sim`, `--video_url <url>`, `--variant <name>`, `--module <name>`

---

*End of AR Glasses Master SDK — Complete Enriched API Reference*
*Generated from source analysis of 27+ repositories and 6 deep-read documents.*
*Enriched: 2026-04-20 | 700+ functions/classes/methods across 12 domains.*
*Deep-read sources: RayNeo Feishu/GitBook, Fusion AHRS, StardustXR KDL, Monado headers, Geo/Maps APIs*
