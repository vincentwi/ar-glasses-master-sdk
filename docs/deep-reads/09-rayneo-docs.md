# DEEP-wave7: RayNeo Documentation (Feishu, GitBook, open.rayneo.com)

## Platform Overview
RayNeo X-Series (X2, X3 Pro) — Android 12/14 based AR glasses with dual Micro-OLED displays.
- X2: Snapdragon XR2 Gen1, 1920×1080 per eye, 33° FOV, 6DOF
- X3 Pro: Snapdragon AR1 Gen1, Micro-LED, birdbath optics, 3DOF + optional 6DOF

## SDK Architecture
Three SDK tiers:
1. **ARDK for Android** — Native Android SDK (AAR)
2. **OpenXR Unity ARDK** — Unity plugin (2021.3.6f1c1 for X2, 2022.3.36f1 for X3Pro)
3. **IPCSDK for Android** — IPC for ring/phone accessory integration

## 1. Binocular Display APIs

### Core Classes
- `BindingPair` — Manages left/right eye view synchronization
- `BaseMirrorActivity` — Base activity for dual-display rendering
- `BaseMirrorFragment` — Fragment variant for dual-display
- `MirrorContainerView` — Container view that mirrors content to both eyes
- `FToast` — Floating toast for binocular display
- `FDialog` — Floating dialog for binocular display

### Key Methods
```java
void updateView()           // Sync view to both displays
void setLeft()             // Set as left eye view
boolean checkIsLeft()      // Check which eye
void make3DEffect()        // Enable stereoscopic 3D parallax
void make3DEffectForSide() // Per-eye 3D effect
```

## 2. Focus Management

### Classes
- `FocusHolder` — Manages focus state across UI elements
- `FixPosFocusTracker` — Fixed-position focus tracking
- `RecyclerViewSlidingTracker` — Focus tracking in scrollable lists
- `RecyclerViewFocusTracker` — RecyclerView focus management
- `IFocusable` interface — Contract for focusable elements

## 3. Touch/Gesture Events

### Classes
- `TouchDispatcher` — Distributes touch events from temple touchpad
- `CommonTouchCallback` — Standard callback for touch events
- `BaseEventActivity` — Base activity with temple gesture support

### TempleAction Enum
```java
enum TempleAction {
    SlideForward,    // Swipe forward on temple
    SlideBackward,   // Swipe backward on temple
    SwipeUp,         // Vertical swipe up
    SwipeDown,       // Vertical swipe down
    TwoFingerTap,    // Two-finger simultaneous tap
    LongPress,       // Long press
    SingleTap,       // Single tap
    DoubleTap        // Double tap
}
```

## 4. 3DOF Head Tracking

### Unity API
```csharp
// Core class: HeadTrackedPoseDriver
HeadTrackedPoseParams.AwakeDriver()    // Initialize 3DOF
HeadTrackedPoseParams.DestroyDriver()  // Cleanup
void OnPostUpdate(Pose pose)           // Callback with quaternion
void ResetRotation()                   // Reset to zero heading
// Tracks: pitch, yaw, roll (no positional tracking)
```

### Android Sensor API
```java
// Use TYPE_GAME_ROTATION_VECTOR sensor
SensorManager.getDefaultSensor(Sensor.TYPE_GAME_ROTATION_VECTOR)
// Rates: SENSOR_DELAY_FASTEST, SENSOR_DELAY_GAME, SENSOR_DELAY_NORMAL, SENSOR_DELAY_UI
// Returns quaternion → convert to Euler angles
```

## 5. 6DOF SLAM

### Unity API
```csharp
Algorithm.EnableSlamHeadTracker()       // Start 6DOF SLAM
Algorithm.GetSlamStatus() → SlamState   // Poll status
Algorithm.DisableSlamHeadTracker()      // Stop SLAM

enum SlamState {
    INITIALIZING,       // SLAM warming up
    TRACKING_SUCCESS,   // Tracking active
    TRACKING_FAIL       // Lost tracking
}
// Uses VGA camera for visual-inertial SLAM
// Provides full 6DOF pose (position + rotation)
```

## 6. Gaze Interaction / Eye Tracking

### Unity Components
```csharp
// Prefab-based setup: XR Plugin Gaze
GazeLaserBeam           // Renders gaze direction ray
LaserBeam               // Visual beam component
XRGraphicRaycaster      // Raycasts against UI
// Selection modes:
// 1. Gaze-for-seconds: dwell time → select
// 2. Temple-click: gaze + tap to select
// Parameters:
float ProgressOuterDiameterOffset  // Loading ring outer radius
float ProgressInnerDiameterOffset  // Loading ring inner radius
float ProgressSpeed                // Dwell timer speed
```

## 7. Face Detection

```csharp
// Single face recognition/tracking
// Uses computer vision + deep learning pipeline
// Output: green-lined bounding box
// Capabilities: face presence, face tracking, face bounding rect
```

## 8. GPS Streaming (via IPCSDK)

```java
// Requires phone tethered connection
GPSIPCHelper.registerGPSInfo(callback)   // Start GPS stream
GPSIPCHelper.unRegisterGPSInfo()         // Stop GPS stream
MobileState.isMobileConnected()          // Check phone connection

// GPS JSON fields:
{
    "mLatitude": double,
    "mLongitude": double,
    "mAltitude": double,
    "mSpeed": float,
    "mBearing": float,
    "mProvider": String,      // "gps" or "network"
    "mTime": long,
    "mHorizontalAccuracyMeters": float
}
```

## 9. Camera/SharedCamera

```csharp
// Unity API
ShareCamera.OpenCamera(
    XRCameraType type,       // VGA or main
    XRResolution resolution, // Target resolution
    RawImage display,        // Output target
    int frameRate            // Target FPS
)
// Uses Android Camera2 API internally
// VGA camera for SLAM, main camera for capture
```

## 10. IPCSDK Ring Control

```java
RingIPCHelper.registerRingInfo(callback)    // Start ring data
RingIPCHelper.unRegisterRingInfo()          // Stop ring data
void setRingIMU(boolean enabled)             // Toggle IMU stream
void setRingLongClick()                      // Register long-click
void setRingSeparateButton()                 // Separate button events

// Ring data fields:
{
    "ring_connected": boolean,
    "ring_imu_status": String,
    "quaternion": {
        "w": float, "x": float, "y": float, "z": float
    }
}
```

## 11. Audio Capture Modes

```java
// Via AudioManager.setParameters()
"recording"           // Standard recording mode
"camera"              // Camera audio capture
"translation"         // Translation pipeline
"voice_assistant"     // Voice assistant mode
```

## 12. Mercury SDK (Dev Setup)

```bash
# Enable dev mode on RayNeo glasses
adb shell settings put global mercury_install_allowed 1
# Required for sideloading custom APKs
# Mercury = RayNeo's Android runtime/launcher system
```

## 13. INMO Open API

INMO glasses run Android 14 with n8n workflow automation.
- Open API for third-party integration
- n8n nodes for glasses control
- Notification routing, display control, camera access

## 14. Google Drive Resources

Available at: https://drive.google.com/drive/folders/1gMcDKkeOS65FrhcdUntnYNhGguOkC8Jl
- SDK packages, sample APKs, documentation PDFs
- X3_3DOFHUD V4.apk — 3DOF / 0DOF HUD prototype
- SED_SatelliteEarthDefender.apk — Game demo

## 15. Cross-Reference: Capabilities Matrix

| Capability | X2 | X3 Pro | API Layer |
|------------|-----|--------|-----------|
| 3DOF | ✓ | ✓ | HeadTrackedPoseDriver |
| 6DOF SLAM | ✓ | - | Algorithm.EnableSlamHeadTracker |
| Gaze Ray | ✓ | ✓ | XRGraphicRaycaster |
| Face Detection | ✓ | ✓ | CV + DL pipeline |
| GPS (via phone) | ✓ | ✓ | GPSIPCHelper |
| Image Recognition | ✓ | ✓ | CV pipeline |
| Eye Closed Rendering | ✓ | ✓ | Proximity sensor |
| Ring Control | - | ✓ | RingIPCHelper |
| Temple Touch | ✓ | ✓ | TouchDispatcher |
| Camera | ✓ | ✓ | ShareCamera |
| Audio Capture | ✓ | ✓ | AudioManager |
| Binocular 3D | ✓ | ✓ | make3DEffect() |

## Data Sources
- Feishu wikis: 8 pages crawled via browser
- GitBook: 10+ pages from rayneo-en.gitbook.io
- open.rayneo.com: SPA, partially accessible
- zenn.dev article: basic setup guide (Japanese)
- Qualcomm developer guide: specs and Unity 3DOF demo
