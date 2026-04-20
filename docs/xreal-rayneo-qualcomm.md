# Master AR Glasses SDK Reference
# XREAL SDK + RayNeo SDK + Qualcomm XR Development Guide

> Comprehensive reference compiled from official documentation sites.
> Last updated: April 19, 2026

---

## Table of Contents

1. [XREAL SDK (v3.1.0)](#1-xreal-sdk-v310)
2. [RayNeo X-Series Android SDK](#2-rayneo-x-series-android-sdk)
3. [RayNeo X-Series Unity SDK](#3-rayneo-x-series-unity-sdk)
4. [Qualcomm RayNeo X3 Pro Development Guide](#4-qualcomm-rayneo-x3-pro-development-guide)
5. [RayNeo Setup from Zenn (Japanese Community)](#5-rayneo-setup-from-zenn-japanese-community)
6. [RayNeo Open Platform](#6-rayneo-open-platform)
7. [Cross-Platform API Comparison](#7-cross-platform-api-comparison)

---

## 1. XREAL SDK (v3.1.0)

**Source:** https://docs.xreal.com/
**API Reference:** https://developer.xreal.com/reference/nrsdk/overview
**GitHub:** https://github.com/nreal-ai
**SDK Download:** https://developer.xreal.com/download

### 1.1 Overview

XREAL SDK (formerly NRSDK) is a Unity XR Plugin for XREAL AR glasses. It integrates with Unity's XR subsystem, using standard XR Interaction Toolkit for interaction logic and AR Foundation for AR features. This provides cross-platform portability and high-level APIs.

**Core Features:**
- Spatial Computing (6DoF tracking, plane detection, image tracking, hand tracking, depth mesh, spatial anchors)
- Optimized Rendering (automatic latency minimization, warping/reprojection)
- Intuitive Interactions (controller, hand gestures, gaze)

**Supported Unity Versions:**
- Unity 2021.3.X LTS
- Unity 2022.3.X LTS
- Unity 6000.0.X LTS

### 1.2 Supported Devices

**Glasses Categories:**
- `XREAL_DEVICE_CATEGORY_REALITY` — 6DoF tracking (XREAL Air 2 Ultra)
- `XREAL_DEVICE_CATEGORY_VISION` — 3DoF tracking (XREAL Air 2, XREAL One Series)

**Compatible Computing Units:**
- Beam Pro
- Samsung S24 and subsequent flagship series

### 1.3 Getting Started — Setup Steps

#### Prerequisites

**Hardware:**
- Beam Pro or supported Android phone (Samsung S24+)
- XREAL glasses
- ADB (wireless ADB strongly recommended)

**Software:**
- Unity LTS with Android Build Support
- XR Plugin Management
- XREAL SDK for Unity (tarball: com.xreal.xr.tar.gz)
- XR Interaction Toolkit (2.5.x or 3.0.x)
- AR Foundation (optional — for plane detection, image tracking, spatial anchors, depth meshing)
- XR Hands (optional)
- Android SDK 12.0 (API Level 31)+

#### Step-by-Step Setup

1. **Create Unity Project** — Open Unity Hub, create new 3D project, switch to Android platform.

2. **Import XRI and AR Foundation** — Install XR Interaction Toolkit from Unity Registry Package Manager. Import `Starter Assets` sample. Optionally import `Hands Interaction Demo`. Optionally install AR Foundation.

3. **Import XREAL SDK** — Window > Package Manager > Add package from tarball > select `com.xreal.xr.tar.gz`.

   SDK Samples:
   - `Interaction Basics` (essential) — prefabs, demo scenes for basic rendering & interactions
   - `AR Features` (optional) — plane detection, image tracking, spatial anchors, depth meshing demos

4. **Configure Project Settings** — Two methods:

   **Method A: Project Validation (Recommended)**
   - Edit > Project Settings > XR Plug-in Management > Android tab > Check XREAL plug-in
   - Go to Project Validation window > Fix All

   **Method B: Manual Configuration**

   | Setting | Value |
   |---------|-------|
   | Default Orientation | Portrait |
   | Auto Graphics API | false |
   | Graphics APIs | OpenGL ES3 |
   | Minimum API Level | Android 10.0+ |
   | Target API Level | Automatic (highest installed) |
   | Write Permission | External (SDCard) |
   | Quality > VSync Count | Don't Sync |

5. **XREAL-Specific Settings** (Edit > Project Settings > XR Plug-in Management > XREAL):

   - **Stereo Rendering Mode:** Multi-view (single pass, better perf) or Multi-pass
   - **Initial Tracking Type:** MODE_6DOF | MODE_3DOF | MODE_0DOF | MODE_0DOF-STAB
   - **Initial Input Source:** Hands | Controller | None | Controller And Hands
   - **Virtual Controller:** On-screen button layout for BeamPro/phone controllers
   - **Support Multi Resume:** Dual-screen independent display mode
   - **Enable Auto Logcat:** Auto-save logcat on app start
   - **Android Permissions:** CAMERA, VIBRATION, AUDIO
   - **License Assets:** Unlock advanced SDK features

6. **Find HelloMR Sample Scene** — Assets/Samples/XREAL XR Plugin/3.0.0/Interaction Basics/HelloMR.unity

7. **Build** — File > Build Settings > Add Open Scene > Build

8. **Deploy** — Connect phone/Beam Pro via USB or WiFi ADB, install APK, connect glasses, open via ControlGlasses/MyGlasses.

### 1.4 Camera System

The XREAL XR Plugin uses Unity's XR Interaction Toolkit (XRI) for camera setup.

**Prefabs:**
- `XR Interaction Setup` — controllers only
- `XR Interaction Hands Setup` — hand gestures (with or without controllers)

Location: Assets > Samples > XREAL XR Plugin > 3.0.0 > Interaction Basics > Prefabs

**Camera Component Settings (vs default):**
- Clear Flags: Solid Color (not Skybox)
- Background Color: Black
- Field of View: 25 (not 60)
- Clipping Planes Near: 0.1 (not 0.3)

**Reset Camera API:**
```csharp
XREALUtility.GetInputSubsystem()?.TryRecenter()
```

### 1.5 Input and Interactions

#### Controller
- Phone/BeamPro serves as 3DoF controller
- Touch gestures and touchscreen actions
- Virtual controller with configurable on-screen buttons

#### Hand Tracking
- Based on XRI (XR Interaction Toolkit) and XR Hands
- Real-time joint pose tracking
- Shares coordinate system with glasses tracking

#### Gaze
- Standard Unity XRI gaze interaction
- Supported out of the box in XRI demo scenes

#### Notification Popup
- System-level notification display

### 1.6 Spatial Computing Features

#### 6DoF Tracking
- Dual SLAM cameras + IMU sensors
- Real-time position and orientation tracking
- 3D point cloud generation and mapping

#### Plane Detection
- Horizontal and vertical surface detection
- Continuous plane transformation updates
- Plane extension and merging

#### Image Tracking
- Recognizes images from database
- Multiple simultaneous image detection
- Custom image support

#### Depth Mesh
- 3D environment representation using tracking cameras
- Real-time occlusion rendering
- Collision detection between virtual and physical content
- Dynamic mesh updates

#### Spatial Anchors
- Persistent anchors across sessions and devices
- Physical location placement of virtual objects

### 1.7 Rendering

**Stereo Rendering Modes:**
- Multi-view (single pass — recommended for performance)
- Multi-pass (separate left/right eye passes)

**Warping:** SDK uses dynamically predicted poses to warp rendered images, reprojecting frames before every VSync.

**Key Notes:**
- For Composition Layers with Layer Order < 0 in URP: Disable HDR
- For URP without single pass: Disable Multithreaded Rendering
- For Overlay content scenes: Disable Multithreaded Rendering
- Scripting Backend: Must use IL2CPP for ARM64

### 1.8 Additional Features

- **MRTK3 Integration** — Mixed Reality Toolkit 3 support
- **Dual Screen Display** — AR view active in glasses while phone shows other apps
- **Device Simulator** — XR Device Simulator from XRI samples

### 1.9 XREAL SDK Sidebar (All Doc Pages)

- XREAL SDK Overview
- XREAL Devices
- Getting Started with XREAL SDK
- Migrating from NRSDK to XREAL SDK
- Sample Code
- Release Note (v3.0.0, v3.1.0)
- Camera (Camera, Access RGB Camera)
- Input and Interactions (Controller, Hand Tracking, Gaze, Notification Popup)
- Image Tracking
- Plane Detection
- Depth Mesh (Normal Mesh, ...)
- Spatial Anchor
- MRTK3 Integration
- Tools
- Rendering
- Frequently Asked Questions
- Design Guide

---

## 2. RayNeo X-Series Android SDK

**Source:** https://rayneo-en.gitbook.io/rayneo-devdoc/x-series/android-sdk
**SDK Name:** RayNeo ARSDK (MercurySDK)

### 2.1 Device Specifications

#### RayNeo X3 Pro (2025 Flagship)
| Spec | Value |
|------|-------|
| Chip | Qualcomm Snapdragon AR1 Gen1 |
| RAM/Storage | 4GB RAM + 32GB ROM |
| Display | 0.36cc full-color MicroLED + diffractive waveguide |
| Resolution | 640×480 |
| Refresh Rate | Up to 60Hz |
| FOV | 30° |
| PPD | 27 |
| Brightness | Peak 6000nits, Average 3500nits |
| Camera | 12MP main (RGB) + spatial camera (VGA) |
| Sensors | Gyroscope, accelerometer, magnetometer, removal sensor |
| Speakers | 2 stereo, reverse noise cancellation |
| Microphones | 3 (one each temple, one front) |
| Interaction | Temple touch, voice, watch/phone |
| Weight | 76g |
| Connectivity | Wi-Fi 6 (2.4G/5G), Bluetooth 5.2 |
| USB | USB 2.0, Type-C |
| Battery | 245mAh, 3-5 hours |
| OS | RayNeo AI OS 2.0 (Android 12) |

#### RayNeo X2
| Spec | Value |
|------|-------|
| Chip | Qualcomm Snapdragon XR2 |
| RAM/Storage | 6GB RAM + 128GB ROM |
| Display | Diffractive waveguide + full-color MicroLED |
| Resolution | 640×480 |
| FOV | 25° |
| PPD | 32 |
| Brightness | Peak >1500nits |
| Camera | 16MP, 1080p video |
| Sensors | Gyroscope, accelerometer, magnetometer, GPS |
| Interaction | Temple touch, smart ring, voice |
| Weight | 119g |
| Connectivity | Wi-Fi 5, Bluetooth 5.2 |
| Battery | 590mAh, 2-3 hours |
| OS | RayNeo OS |

### 2.2 Architecture Overview

The X-Series glasses run a full **Android 12** stack with two key architectural differences from phones:

1. **Dual Displays** — Left panel projects to left eye, right to right eye. Android gives one "logical screen" so vanilla UI tears in half. Must render each UI piece twice (once per eye). The SDK provides drop-in base components that handle binocular fusion automatically.

2. **Input & Focus** — Temple touchpad provides 1D touch events (X changes, Y fixed). Ring accessories also generate TP events. Explicit focus management system required.

### 2.3 Quick Start (Android)

1. **Create New Project** — Android Studio (recommended: Otter 2 Feature Drop 2025.2.2+), select "No Activity", Kotlin language.

2. **Enable ViewBinding:**
   ```gradle
   buildFeatures {
       viewBinding = true
   }
   ```

3. **Create Application Class & Configure meta-data:**
   ```xml
   <application android:name=".MyApplication" ...>
       <meta-data android:name="com.rayneo.mercury.app" android:value="true" />
   </application>
   ```
   **IMPORTANT:** This meta-data tag makes the app visible in the glasses launcher. Without it, the app icon won't appear.

4. **Import Dependencies** — Copy AAR to libs directory:
   ```gradle
   implementation(fileTree("libs"))
   implementation(libs.androidx.lifecycle.viewmodel.ktx)
   ```

5. **Initialize SDK:**
   ```kotlin
   import com.ffalcon.mercury.android.sdk.MercurySDK
   import android.app.Application

   class MyApplication: Application() {
       override fun onCreate() {
           super.onCreate()
           MercurySDK.init(this)
       }
   }
   ```

6. **Create Activity** — Extend `BaseMirrorActivity`:
   ```kotlin
   class MainActivity : BaseMirrorActivity<ActivityMainBinding>()
   ```

### 2.4 Capabilities & API — Complete Reference

#### 2.4.1 Binocular Display

**Core Utility:** `BindingPair` — based on ViewBinding, maps left and right layouts.

**Key Methods:**
- `mBindingPair.updateView { }` — Operate on both left and right layouts simultaneously
- `mBindingPair.setLeft { }` — Operate only on left layout (for event binding, external data)
- `mBindingPair.checkIsLeft(this)` — Determine if current operation is left or right

**Component Hierarchy:**

| Level | Class | Description |
|-------|-------|-------------|
| Activity | `BaseMirrorActivity` | Auto-mirrors layout views |
| Fragment | `BaseMirrorFragment` | Fragment-level binocular (don't add to BaseMirrorActivity) |
| View (composition) | `MirrorContainerView` | Must call `mirrorContainer.bindTo` |
| View (inheritance) | `BaseMirrorContainerView` | Don't add to BaseMirrorActivity |
| Toast | `FToast` | Universal Toast with binocular support |
| Dialog | `FDialog` | Universal Dialog with binocular support |

**Video Binocular Fusion:**
- Use `MirroringView` component for SurfaceView scenarios
- `binding.mirrorView.setSource(leftTexture)`
- `binding.mirrorView.startMirroring()`
- `binding.mirrorView.stopMirroring()` in onDestroy

#### 2.4.2 Focus Management

Since glasses screen cannot be touched directly, focus switching must be manually managed:
- Swipe forward/backward → switches focus
- Single tap → triggers focused view event
- Double tap → exits focus / returns to previous level

**Key Classes:**

| Class | Purpose |
|-------|---------|
| `FocusHolder` | Maintains focus targets and switching logic |
| `FocusInfo` | Describes a focusable view with event/focus handlers |
| `FixPosFocusTracker` | Fixed position focus tracking |
| `RecyclerViewSlidingTracker` | RecyclerView with fixed focus positions |
| `RecyclerViewFocusTracker` | RecyclerView with moving focus positions |
| `IFocusable` | Interface for custom view focus switching |

**Focus Setup Pattern:**
```kotlin
val focusHolder = FocusHolder(true)
mBindingPair.setLeft {
    val btn1Info = FocusInfo(
        btn1,
        eventHandler = { action ->
            when (action) {
                is TempleAction.Click -> FToast.show("click")
                else -> Unit
            }
        },
        focusChangeHandler = { hasFocus ->
            mBindingPair.updateView {
                btn1.setBackgroundColor(getColor(if(hasFocus) R.color.purple_200 else R.color.black))
            }
        }
    )
    focusHolder.addFocusTarget(btn1Info, ...)
    focusHolder.currentFocus(mBindingPair.left.btn1)
}
fixPosFocusTracker = FixPosFocusTracker(focusHolder).apply {
    focusObj.hasFocus = true
}
```

**Dynamic Focus:**
- `mBindingPair.addFocusView(...)` — Dynamically add focus views
- `handle.clearFocusView()` — Remove dynamic focus view

#### 2.4.3 Touch Events & Event Response

Temple arms generate 1D MotionEvent TP events (X dynamic, Y fixed). Ring accessories also generate TP events.

**Event Processing Chain:**
`MotionEvent` → `TouchDispatcher` → `CommonTouchCallback` → gesture recognition → `TempleAction` subclasses

**Activity Hierarchy:**
- `BaseTouchActivity` — Automatically registers gesture listeners
- `BaseEventActivity` — Converts gestures to Kotlin Flow event streams
- `BaseMirrorActivity` — Inherits from BaseEventActivity (adds binocular display)

**TempleAction Types:**
| Action | Description |
|--------|-------------|
| `TempleAction.Click` | Single tap |
| `TempleAction.DoubleClick` | Double tap |
| `TempleAction.TripleClick` | Triple tap |
| `TempleAction.LongClick` | Long press |
| `TempleAction.SlideForward` | Swipe forward |
| `TempleAction.SlideBackward` | Swipe backward |
| `TempleAction.SlideUpwards` | Swipe up (X3 only) |
| `TempleAction.SlideDownwards` | Swipe down (X3 only) |
| `TempleAction.TpSlideContinuous` | Continuous swipe with direction |

**X3-Only New Gestures (CommonTouchCallback):**
- `onTPSlideUpwards(args: FlingArgs): Boolean`
- `onTPSlideDownwards(args: FlingArgs): Boolean`
- `onTPDoubleFingerClick()`
- `onTPDoubleFingerLongClick()`
- `onTPSlideContinuous(delta, longClick, vertical)` — Added `vertical` parameter
- `filterMode` property: `OnlyX` or `OnlyY` for axis filtering

**Swipe Direction Modes (configurable in settings):**
- **Natural Mode (default):** temple→lens = SlideBackward, lens→temple = SlideForward
- **Non-Natural Mode:** temple→lens = SlideForward, lens→temple = SlideBackward

**Device Detection:**
```kotlin
if (DeviceUtil.isX3Device()) { /* X3 */ } else { /* X2 */ }
```

#### 2.4.4 Following Hand Effect (Smooth Scrolling)

| Class | Mode |
|-------|------|
| `RecyclerViewSlidingTracker` | Fixed focus position list follow-up |
| `RecyclerViewFocusTracker` | Moving focus position list follow-up |
| `FixPosFocusTracker` | Fixed view follow-up effect |

#### 2.4.5 3D Effect Implementation

Binocular parallax pseudo-3D through left-right view offset:
- `make3DEffect(view, hasFocus)` — Apply 3D effect
- `make3DEffectForSide(view, isLeft, hasFocus)` — Apply per-side 3D effect

#### 2.4.6 Audio Capture Modes

**X2 Recording Modes:**

| Mode | Description | setParameters |
|------|-------------|---------------|
| audio record | Not yet configured | `audio_source_record=sound` |
| camera record | 2 temple mics, full sound, no noise cancellation | `audio_source_record=camcorder` |
| translation | 3 mics, ignores wearer, captures external | `audio_source_record=translation` |
| voice assistant | 2 temple mics, prioritizes wearer's voice | `audio_source_record=voiceassistant` |

**Best practice:** Reset to `audio_source_record=off` when done.

**X3 Recording Modes:**

| Mode | Description |
|------|-------------|
| OFF | Release microphone, call `audio_source_record=off` |
| RECORD_TRANSLATION | Surrounding voices, meeting minutes/translation |
| CAMCORDER | Stereo recording, omnidirectional, video recording |
| VOICE_RECOGNITION | Wearer's voice only, voice assistant/navigation |
| VOICE_COMMUNICATION | Front + right mic, wearer's voice, calls/meetings |

#### 2.4.7 Camera Development

Based on Android Camera2 API. Supports resolution enumeration and preview.
- `CameraManager`, `Camera2 API`

#### 2.4.8 IMU Data Acquisition

Gyroscope, accelerometer, magnetometer data via standard Android sensor APIs.

#### 2.4.9 Mobile Connection & GPS Streaming

- `MobileState.isMobileConnected()` — Real-time Bluetooth connection status
- IPC SDK integration for mobile phone GPS data
- Asynchronous callback handling via `OnResponseListener`

#### 2.4.10 IPCSDK for Android

Inter-process communication SDK for glasses-to-phone data streaming.

---

## 3. RayNeo X-Series Unity SDK

**Source:** https://rayneo-en.gitbook.io/rayneo-devdoc/x-series/unity-sdk
**SDK Name:** RayNeo OpenXR Unity ARDK

### 3.1 Supported Unity Versions

- X2 SDK: Unity Editor 2021.3.6f1c1
- X3 Pro SDK: Unity Editor 2022.3.36f1
- Other compatible: 2020.3.20 LTS+, 2021.3.0 LTS+, 2022.2.0+, 2023.1.0+

### 3.2 SDK Architecture

The Unity ARDK is based on OpenXR and provides:
- SDK Constitutes System Architecture
- Basic Capabilities & API
- AR Capabilities & API
- X2 API (legacy SDK support)

### 3.3 Basic Capabilities & API

| Capability | Page |
|-----------|------|
| Touch Pad | Temple touchpad input in Unity |
| ShareCamera | Camera sharing/access |
| Audio Focus | Audio focus management |
| Audio Capture Modes | Recording mode configuration |
| GPS Streaming | Mobile GPS data access |
| Device System Access | System-level device APIs |

### 3.4 AR Capabilities & API

- 3DoF head tracking
- 6DoF (SLAM mode)
- 3DoF + magnetometer binding
- Face detection
- Plane detection

### 3.5 Quick Start (Unity)

1. Create empty Unity project
2. Windows > Package Manager > select package.json from RayNeo ARDK
3. Accept new input system prompt, restart
4. File > Build Settings > Switch to Android platform
5. Edit > Project Settings > Player > Other Settings > Override Default Package Name
6. Project Settings > XR Plug-in Management > Check OpenXR + RayNeo XR feature group
7. Fix All in OpenXR parameter settings

### 3.6 AndroidManifest.xml Configuration (CRITICAL)

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.unity3d.player"
    xmlns:tools="http://schemas.android.com/tools">
    <application>
       <activity android:name="com.rayneo.openxradapter.UnityOpenXrActivity"
                  android:theme="@style/UnityThemeSelector">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
            <meta-data android:name="unityplayer.UnityActivity" android:value="true" />
        </activity>
     <meta-data android:name="com.rayneo.mercury.app" android:value="true" />
    </application>
</manifest>
```

### 3.7 Head Control Modes

| Mode | Description |
|------|-------------|
| SLAM | 6DoF, face detection, plane detection |
| DOF3 | Conventional 3DoF |
| DOF_WITH_ABSOLUTE_ORIENTATION | 3DoF + magnetometer binding |

Configure at: BuildSettings > XR Plug-in Management > OpenXR > RayNeoSupport > Camera Attitude Type

### 3.8 XR Plugin Prefab Structure

| Element | Description |
|---------|-------------|
| XR Plugin | Main object |
| LaserBeam | Ray control unit (camera-based) |
| BeamGraphic | Ray renderer (can be disabled) |
| LaserBeamDot | Interaction point (ray collision) |
| Head | Camera control unit for 3DoF head tracking |

### 3.9 Building First XR App

1. Create new scene, delete Main Camera and Directional Light
2. Drag `XR Plugin` prefab from Packages/RayNeo OpenXR ARDK/SDK/Runtime/Resources/Prefab
3. Set Game view resolution: 640x480
4. Create UI > Legacy > Button
5. Set Canvas Render Mode to World Space, Pos (0, 0, 1000)
6. Replace Graphic Raycaster with `XRGraphicRaycaster`
7. Build And Run

**Expected Results:**
- Stereoscopic rendering works correctly
- 3DoF head tracking functions
- Temple click triggers button events

---

## 4. Qualcomm RayNeo X3 Pro Development Guide

**Source:** https://www.qualcomm.com/developer/project/get-started-with-rayneo-x3-pro-ar-development

### 4.1 Hardware

- **Device:** RayNeo X3 Pro AI-Powered Smart Glasses
- **Chipset:** Snapdragon® AR1 Gen 1
- **Capabilities:** High-performance on-device AI and AR experiences

### 4.2 Pre-Development Checklist

1. Update Glasses OS: Settings > General > About Device
2. For Glass OS above 23.8.29, use Unity SDK 1.1.2+
3. Download ARDK from official sources
4. Enable ADB on glasses
5. Screen mirror via AnLink (Windows) or Scrcpy

### 4.3 ADB Connection

The glasses support standard Android ADB commands. Enable ADB mode:
- Go to Glasses Settings > General
- Swipe to far left and trigger "wall collision" effect 10 times

### 4.4 SDK Options

| SDK | Use Case |
|-----|----------|
| RayNeo ARDK for Android | Native Android development with binocular display, touchpad, sensors |
| RayNeo OpenXR Unity ARDK | AR capabilities: 3DoF, SLAM/6DoF, plane detection, spatial effects |

**Key Notes from Qualcomm:**
- Unity provides AR capabilities (3DoF, SLAM, plane detection)
- For audio, camera, gyroscope: use Android native APIs directly
- All-in-one glasses have high power consumption — control app running power
- Vuforia partial low-power capabilities work on X2 but limited by temperature/power

### 4.5 Additional Qualcomm Resources

- Snapdragon Spaces Compatibility Plugin for Android XR
- Design Specifications for AR glasses
- Debugging Tools documentation

---

## 5. RayNeo Setup from Zenn (Japanese Community)

**Source:** https://zenn.dev/satohjohn/articles/a06815e13b9f7f
**Title (translated):** "Building and Installing an Android App for RayNeo"
**Published:** April 5, 2026

### 5.1 Project Overview (Translated)

The article demonstrates creating a RayNeo X3 Pro Android app that:
- Captures camera images
- Uploads them via HTTPS to Google Cloud Run
- Installs and runs as a native glasses app

### 5.2 Milestones

1. Set up app development environment
2. Configure RayNeo X3 Pro
3. Create Android app
4. Create Cloud Run server app

### 5.3 Step 1: Install JDK + Android Studio

```bash
brew install --cask zulu@17
brew install --cask android-studio
```

Configure environment:
```bash
export PATH=$PATH:$HOME/Library/Android/sdk/platform-tools
```

Verify ADB:
```bash
adb version
```

### 5.4 Step 2: Enable Developer Mode on RayNeo X3

1. Go to Glasses Settings > General
2. While on the settings screen, swipe left 10 times (trigger "wall collision effect")
3. This enables/disables ADB mode

Verify device connection:
```bash
$ adb devices -l
List of devices attached
A06B4A37D5FF133  device usb:0-1 product:RayNeoX3Pro model:ARGF20 device:MercuryLiteXR
```

Test with APK install:
```bash
adb install /path/to/F-Droid.apk
```

**TIP:** Install `scrcpy` for screen mirroring (debugging via glasses touchpad is difficult):
```bash
# https://github.com/genymobile/scrcpy
```

### 5.5 Step 3: Build Android App

**Key Notes (translated):**
- App background MUST be black (appears transparent through glasses)
- For smartphone-style apps, need RayNeo controller app
- Add meta-data to register as glasses-native app (bypasses AppLab):

```xml
<application ...>
    <meta-data android:name="com.rayneo.mercury.app" android:value="true" />
</application>
```

**Permissions for camera + network:**
```xml
<manifest ...>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_CAMERA"/>
    <uses-feature android:name="android.hardware.camera" android:required="true"/>
    <application ...>
        <service android:name=".CameraService"
            android:foregroundServiceType="camera"
            android:exported="false"/>
    </application>
</manifest>
```

**Camera Capture Pattern (CameraX):**
```kotlin
private fun bindImage(provider: ProcessCameraProvider) {
    val analysis = ImageAnalysis.Builder()
        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
        .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_YUV_420_888)
        .build()
        .also { it.setAnalyzer(executor, ::analyzeImage) }
    provider.bindToLifecycle(this, CameraSelector.DEFAULT_BACK_CAMERA, analysis)
}
```

**Image Upload (OkHttp):**
```kotlin
val request = Request.Builder()
    .url(serverUrl)
    .post(jpegBytes.toRequestBody("image/jpeg".toMediaType()))
    .build()
client.newCall(request).execute()
```

### 5.6 Step 4: Cloud Run Server (Go)

Simple Go server receiving JPEG uploads and saving to GCS:
```go
http.HandleFunc("/upload", func(w http.ResponseWriter, r *http.Request) {
    body, _ := io.ReadAll(r.Body)
    // Validate JPEG magic bytes (0xFF 0xD8)
    filename := fmt.Sprintf("%s_%s.jpg", time.Now().Format("20060102-150405"), uuid.New().String())
    obj := client.Bucket(bucket).Object(filename)
    writer := obj.NewWriter(ctx)
    writer.ContentType = "image/jpeg"
    writer.Write(body)
    writer.Close()
})
```

Deploy:
```bash
gcloud run deploy image-saver \
  --source . \
  --region asia-northeast1 \
  --set-env-vars BUCKET_NAME={BUCKET_NAME} \
  --allow-unauthenticated \
  --project={PROJECT_ID}
```

---

## 6. RayNeo Open Platform

**Source:** https://open.rayneo.com/#/docs

### 6.1 Platform Overview

RayNeo Open Platform is the official developer platform for RayNeo wearable XR applications. Developers can:
- Develop Android apps and mini-program applications
- Use RayNeo Glasses with the open SDK
- Upload applications for approval and distribution

### 6.2 Air SDK

The Air SDK provides XR functions (rendering, input) for **Thunderbird AR Glass + Android phones**. It is separate from the X-Series SDK.

### 6.3 SDK Documentation Structure

| Section | Content |
|---------|---------|
| Overview | Platform introduction |
| Develop Environment | Setup requirements |
| Equipment | Hardware requirements |
| Import SDK | SDK integration steps |
| Configuration Setting | Project configuration |
| Build Your First XR | First app tutorial |
| Developer Tools | Debugging & tools |
| Update Description | Changelog |
| SDK FAQ | Troubleshooting |

### 6.4 Developer Registration Process

1. Register a developer account
2. Complete developer information and identity authentication
3. Download SDK and complete application development
4. Create an application and upload the version installation package
5. Wait for approval and experience the online XR application

### 6.5 Platform Links

- X SDK documentation
- Air SDK documentation
- Morpheus Plan
- AI Challenge
- Discord community

---

## 7. Cross-Platform API Comparison

### Tracking Capabilities

| Feature | XREAL SDK | RayNeo X3 Pro | RayNeo X2 |
|---------|-----------|---------------|-----------|
| 3DoF | ✅ (MODE_3DOF) | ✅ (DOF3) | ✅ |
| 6DoF | ✅ (MODE_6DOF) | ✅ (SLAM mode) | ❌ |
| 3DoF + Magnetometer | ❌ | ✅ (DOF_WITH_ABSOLUTE_ORIENTATION) | ❌ |
| Hand Tracking | ✅ (XR Hands) | ❌ | ❌ |
| Plane Detection | ✅ (AR Foundation) | ✅ (SLAM mode) | ❌ |
| Image Tracking | ✅ (AR Foundation) | ❌ | ❌ |
| Depth Mesh | ✅ | ❌ | ❌ |
| Spatial Anchors | ✅ | ❌ | ❌ |

### Input Methods

| Feature | XREAL SDK | RayNeo X3 Pro | RayNeo X2 |
|---------|-----------|---------------|-----------|
| Controller (phone) | ✅ | ✅ (phone/watch) | ✅ (ring/phone) |
| Temple Touch | ❌ | ✅ (2D touch) | ✅ (1D touch) |
| Hand Gestures | ✅ | ❌ | ❌ |
| Gaze | ✅ | ❌ | ❌ |
| Voice | ❌ | ✅ | ✅ |

### Display

| Feature | XREAL SDK | RayNeo X3 Pro | RayNeo X2 |
|---------|-----------|---------------|-----------|
| Binocular Rendering | Auto (Unity XR) | SDK components (BindingPair) | SDK components |
| Stereo Rendering | Multi-view/Multi-pass | Dual-screen mirroring | Dual-screen mirroring |
| 3D Parallax Effects | ❌ | ✅ (make3DEffect) | ✅ |

### Development Framework

| Aspect | XREAL SDK | RayNeo SDK |
|--------|-----------|------------|
| Primary Engine | Unity | Unity (OpenXR) + Android Native |
| XR Framework | Unity XR Plugin | OpenXR ARDK |
| Interaction Toolkit | Unity XRI | Custom (TempleAction, FocusHolder) |
| AR Foundation | ✅ Supported | ❌ Not used |
| Language (Native) | C# | Kotlin |
| Min Android API | 31 (Android 12) | Android 12 |

### Critical Meta-Data Tag (Both Platforms)

For RayNeo glasses apps to appear in the launcher:
```xml
<meta-data android:name="com.rayneo.mercury.app" android:value="true" />
```

### Key SDK Initialization

**XREAL:** Import via Unity Package Manager tarball, configure XR Plug-in Management.

**RayNeo Android:**
```kotlin
MercurySDK.init(this) // In Application.onCreate()
```

**RayNeo Unity:** Import via Package Manager (package.json), configure OpenXR + RayNeo XR feature group.

---

## Appendix A: Useful Links

### XREAL
- Docs: https://docs.xreal.com/
- API Reference: https://developer.xreal.com/reference/nrsdk/overview
- SDK Download: https://developer.xreal.com/download
- GitHub: https://github.com/nreal-ai
- Template Project: https://github.com/dengxian-xreal/XREALSDKTemplate

### RayNeo
- English Docs: https://rayneo-en.gitbook.io/rayneo-devdoc
- Open Platform: https://open.rayneo.com/#/docs
- Product Page: https://www.rayneo.com/pages/x3-pro-launch
- Controller App: https://play.google.com/store/apps/details?id=com.rayneo.mercury

### Qualcomm
- X3 Pro Guide: https://www.qualcomm.com/developer/project/get-started-with-rayneo-x3-pro-ar-development
- Snapdragon Spaces: https://www.qualcomm.com/developer/software/snapdragon-spaces-compatibility-plugin-for-android-xr

### Tools
- Scrcpy (screen mirror): https://github.com/Genymobile/scrcpy
- AnLink (Windows mirror): https://cn.anlinksoft.com/
- ADB: https://developer.android.com/studio/command-line/adb

---

## Appendix B: Common AndroidManifest.xml for RayNeo

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">

    <!-- Permissions -->
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_CAMERA"/>
    <uses-feature android:name="android.hardware.camera" android:required="true"/>

    <application
        android:name=".MyApplication"
        android:theme="@style/Theme.MyApp">

        <!-- REQUIRED: Register as RayNeo glasses app -->
        <meta-data android:name="com.rayneo.mercury.app" android:value="true" />

        <!-- Main Activity -->
        <activity android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Camera Foreground Service -->
        <service android:name=".CameraService"
            android:foregroundServiceType="camera"
            android:exported="false"/>
    </application>
</manifest>
```

---

*This document was compiled from deep crawls of official documentation. For the most up-to-date information, always refer to the original sources linked above.*
