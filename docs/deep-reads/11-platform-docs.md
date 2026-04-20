# DEEP Wave 9 - Platform Documentation Crawl
## Comprehensive AR Glasses SDK & Platform Reference
### Generated: 2026-04-20

---

# TABLE OF CONTENTS

1. [XREAL SDK Documentation (Full Site Crawl)](#1-xreal-sdk)
2. [OpenXR 1.1 Specification Index](#2-openxr-11-spec)
3. [Snap OS 2.0 Capabilities](#3-snap-os-20)
4. [Qualcomm RayNeo X3 Pro Development Guide](#4-qualcomm-rayneo-x3-pro)
5. [Japanese Setup Article - RayNeo Android Development](#5-rayneo-android-dev-japanese)

---

# 1. XREAL SDK
## Source: https://docs.xreal.com/
## SDK Version: 3.1.0

### 1.1 XREAL SDK Overview

By utilizing the XREAL SDK, innovative mixed reality experiences are developed. Using a simple development process and a high-level API, XREAL SDK offers a set of powerful MR features and enables your XREAL glasses to understand the real world.

The XREAL SDK has transitioned from the proprietary NRSDK approach into Unity's XR Plugin umbrella. This integration allows developers to utilize:
- **XR Interaction Toolkit** for handling interaction logic
- **AR Foundation** to manage AR features
- Enhanced cross-platform portability

**Supported Unity Versions:** Unity 2021.3.X and above (LTS versions)

#### Core Features

**Spatial Computing:**
- **6DoF Tracking** - Uses dual SLAM cameras + IMU sensors for position and orientation tracking. Provides real-time mapping and 3D point clouds.
- **Plane Detection** - Detects horizontal and vertical flat surfaces. Continuously updated as glasses move. Multiple planes can merge.
- **Image Tracking** - Recognizes images and builds AR experiences around them. Multiple images per session supported, including custom ones.
- **Hand Tracking** - Real-time gesture recognition and joint pose tracking. Shares coordinate system with glasses tracking.
- **Depth Mesh** - 3D environment representation using visual algorithms. Supports real-time occlusion rendering and collision detection.
- **Spatial Anchor** - Persistent anchors shared across sessions and devices. Maintains virtual objects at physical locations.

**Optimized Rendering:**
- Warping: Dynamically predicted poses for reprojection before every VSync
- Minimized latency, reduced judder
- Automatic optimization (no manual tuning needed)

**Interactions:**
- Phone Controller (3DoF): Android phone as controller with gesture/touchscreen support
- Hand gestures
- Controller + Hands combined mode

### 1.2 XREAL Devices - Full Specifications

#### Device Lineup

| Feature | Light (Discontinued) | Air | Air 2 | Air 2 Pro | Air 2 Ultra | XREAL One | XREAL One Pro | XREAL 1S |
|---------|---------------------|-----|-------|-----------|-------------|-----------|---------------|----------|
| Weight | 106g | ~77g | ~72g | ~75g | ~80g | 82g | 87g | 82g |
| Resolution/Eye | 1920x1080 | 1920x1080 | 1920x1080 | 1920x1080 | 1920x1080 | 1920x1080 | 1920x1080 | 1920x1200 |
| FOV | 52° | 46° | 46° | 46° | 52° | 50° | 57° | 52° |
| Frame Rate | 60Hz | 60/72Hz | 60/72/90/120Hz | 60/72/90/120Hz | 60/72/90/120Hz | 60/72/90/120Hz | 60/72/90/120Hz | 60/72/90/120Hz |
| RGB Camera | Yes | No | No | No | No | Yes (Detachable) | Yes (Detachable) | Yes (Detachable) |
| Grayscale Camera | Yes | No | No | No | Yes | No | No | No |
| IMU | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Connection | USB-C | USB-C | USB-C | USB-C | USB-C | USB-C | USB-C | USB-C |
| Audio | Dual Speakers+Mics | Dual Speakers+Mics | Dual Speakers+Mics | Dual Speakers+Mics | Dual Speakers+Mics | Dual Speakers, 4 Mics | Dual Speakers, 4 Mics | Dual Speakers, 4 Mics |

Key notes:
- **XREAL Air 2 Ultra**: Adds spatial computing with integrated 6DoF via dual grayscale cameras, 52° FOV
- **XREAL One Series**: Self-developed X1 chip, direct device connection, 3DoF, detachable RGB camera
- **XREAL Air 2 Pro**: First electrochromic lens in mass production

#### Feature Compatibility Matrix

| Features | XREAL One Series (with RGB Camera) | XREAL Air/Air 2/Air 2 Pro | XREAL Air 2 Ultra |
|----------|-------------------------------------|----------------------------|-------------------|
| Head Tracking | 6DoF | 3DoF | 6DoF |
| Plane Tracking | No | No | Yes |
| Image Tracking | No | No | Yes |
| Hand Tracking | No | No | Yes |
| Depth Mesh | No | No | Yes |
| Spatial Anchor | No | No | Yes |
| First Person View | Application & Reality | Application | Application |
| Controller | 3DoF | 3DoF | 3DoF |
| Customize Phone Controller UI | Yes | Yes | Yes |

#### Supported Android Phones (as of NRSDK 2.3.0+)

| Brand | Chip | Model | Android Version |
|-------|------|-------|-----------------|
| Samsung | Snapdragon 8 Gen 3 | Galaxy S24 (SM-S9210) | Android 14 |
| Samsung | Snapdragon 8 Elite (3nm) | Galaxy S25 (SM-S931U) | Android 15 |

Also supported: **Beam Pro** (XREAL's own XR spatial computing device)

### 1.3 Getting Started with XREAL SDK

#### Prerequisites

**Hardware:**
- Beam Pro or supported Android Phone (Samsung S24+ flagship series)
- XREAL glasses
- ADB (wireless recommended)

**Software:**
- Unity LTS: 2021.3.X, 2022.3.X, or 6000.0.X
- XR Plugin Management
- XREAL SDK for Unity (com.xreal.xr.tar.gz)
  - Sample: Interaction Basics (required)
  - Sample: AR Features (optional)
- XR Interaction Toolkit (2.5.x or 3.0.x supported)
  - Sample: Starter Assets
  - Sample: Hands Interaction Demo (optional)
- AR Foundation (optional - for plane detection, image tracking, spatial anchors, depth meshing)
- XR Hands (optional)
- Android SDK 12.0 (API Level 31)+

#### Setup Steps
1. Create Unity 3D project, switch to Android platform
2. Install XRI + AR Foundation from Package Manager
3. Import XREAL SDK: Window -> Package Manager -> Add package from tarball -> com.xreal.xr.tar.gz
4. Configure Project Settings via XR Plugin Validation or manually
5. Build and deploy

#### Key Project Settings

| Setting | Value |
|---------|-------|
| Default Orientation | Portrait |
| Auto Graphics API | false |
| Graphics APIs | OpenGL ES3 |
| Minimum API Level | Android 10.0+ |
| Target API Level | Automatic (highest) |
| Write Permission | External(SDCard) |
| VSync Count | Don't Sync |

#### XREAL-Specific Settings (Edit > Project Settings > XR Plug-in Management > XREAL)

**Stereo Rendering Mode:**
- Multi-view (single pass, better performance)
- Multi-pass (separate passes per eye)

**Tracking Types:**
- MODE_6DOF: Full position + rotation
- MODE_3DOF: Rotation only
- MODE_0DOF: No tracking
- MODE_0DOF-STAB: Stabilized, no tracking

**Input Sources:**
- Hands, Controller, None, Controller And Hands

**Support Multi Resume:** Enables dual-screen independent display. AR view stays active in glasses while phone runs 2D apps.

**Supported Device Categories:**
- XREAL_DEVICE_CATEGORY_REALITY: 6DoF glasses (Air 2 Ultra)
- XREAL_DEVICE_CATEGORY_VISION: 3DoF glasses (Air 2, One Series)

### 1.4 Camera System

Uses Unity XR Interaction Toolkit for camera setup. Key prefabs:
- `XR Interaction Setup` - Controllers only
- `XR Interaction Hands Setup` - Hand gestures (with or without controllers)

**Camera Settings (vs default):**
- Clear Flags: Solid Color (not Skybox)
- Background Color: Black
- Field of View: 25 (not 60)
- Clipping Planes: 0.1 (not 0.3)

**Reset Camera API:** `XREALUtility.GetInputSubsystem()?.TryRecenter()`

### 1.5 Plane Detection

Capabilities:
- Real-time horizontal and vertical plane detection
- Continuous surface tracking
- Visual feedback with custom prefabs
- Interaction support for placing/manipulating virtual objects

Requirements: Unity 2021.3+, XR Interaction Toolkit, AR Foundation

### 1.6 Spatial Anchors

Fixed reference points in AR environment providing stable position and orientation across sessions.

**Main Features:**
- Create and manage spatial anchors in Unity
- Save and load spatial anchors
- User interaction support (clicking on anchors)
- Mapping quality visualization

**Best Practices:**
- Observe environment thoroughly around anchor (5-15 seconds)
- Maintain smooth, slow movement
- Even lighting, rich texture, 0.5-3m distance
- Avoid attaching objects >3m from anchor
- Avoid: rapid viewpoint changes, quick movements, poor lighting, transparent/reflective surfaces

### 1.7 Full Documentation Site Map

All pages crawled from docs.xreal.com sidebar:
- XREAL SDK Overview
- XREAL Devices
  - Compatibility
  - XREAL Glasses
- Getting Started with XREAL SDK
- Migrating from NRSDK to XREAL SDK
- Sample Code
- Release Note (3.1.0, 3.0.0, etc.)
- Camera
  - Access RGB Camera
- Input and Interactions
- Image Tracking
- Plane Detection
- Depth Mesh
  - Normal Mesh
- Spatial Anchor
  - Anchors
- MRTK3 Integration
- Tools
- Rendering
- Frequently Asked Questions
- Design Guide

### 1.8 API Reference

Full API Reference available at: https://developer.xreal.com/reference/nrsdk/overview
SDK Download: https://developer.xreal.com/download
GitHub: https://github.com/nreal-ai

---

# 2. OpenXR 1.1 Spec
## Source: https://registry.khronos.org/OpenXR/specs/1.1/man/html/openxr.html
## Version: 1.1.58 (from git ref release-1.1.58)

### 2.1 API Categories Overview

The OpenXR 1.1 specification organizes its API into these major categories:
1. **OpenXR Commands** (Functions) - 400+ functions
2. **Object Handles** - 59 handle types
3. **Structures** - 700+ struct types
4. **Enumerations** - 200+ enum types
5. **Flags** - 54 flag types
6. **Function Pointer Types** - 5 types
7. **Scalar Types** - 18 types
8. **C Macro Definitions** - 48 macros
9. **Extensions** - 200+ extensions

### 2.2 Core Commands (Key API Groups)

#### Instance & System
- xrCreateInstance, xrDestroyInstance, xrGetInstanceProperties, xrGetInstanceProcAddr
- xrGetSystem, xrGetSystemProperties
- xrEnumerateInstanceExtensionProperties, xrEnumerateApiLayerProperties

#### Session Management
- xrCreateSession, xrDestroySession, xrBeginSession, xrEndSession
- xrRequestExitSession, xrAttachSessionActionSets

#### Frame Loop
- xrWaitFrame, xrBeginFrame, xrEndFrame
- xrLocateViews

#### Swapchain
- xrCreateSwapchain, xrDestroySwapchain
- xrEnumerateSwapchainImages, xrEnumerateSwapchainFormats
- xrAcquireSwapchainImage, xrWaitSwapchainImage, xrReleaseSwapchainImage

#### Space & Tracking
- xrCreateReferenceSpace, xrCreateActionSpace, xrDestroySpace
- xrLocateSpace, xrLocateSpaces
- xrGetReferenceSpaceBoundsRect, xrEnumerateReferenceSpaces

#### Actions & Input
- xrCreateAction, xrCreateActionSet, xrDestroyAction, xrDestroyActionSet
- xrSyncActions, xrGetActionStateBoolean, xrGetActionStateFloat
- xrGetActionStatePose, xrGetActionStateVector2f
- xrSuggestInteractionProfileBindings, xrGetCurrentInteractionProfile
- xrApplyHapticFeedback, xrStopHapticFeedback

#### Hand Tracking (EXT)
- xrCreateHandTrackerEXT, xrDestroyHandTrackerEXT
- xrLocateHandJointsEXT

#### Plane Detection (EXT)
- xrCreatePlaneDetectorEXT, xrDestroyPlaneDetectorEXT
- xrBeginPlaneDetectionEXT, xrGetPlaneDetectionStateEXT
- xrGetPlaneDetectionsEXT, xrGetPlanePolygonBufferEXT

#### Spatial Anchors
- xrCreateSpatialAnchorEXT, xrCreateSpatialAnchorFB, xrCreateSpatialAnchorMSFT
- xrCreateSpatialAnchorHTC, xrCreateSpatialAnchorSpaceANDROID
- xrPersistSpatialAnchorMSFT, xrUnpersistSpatialAnchorMSFT
- xrCreateSpatialAnchorsAsyncML, xrQuerySpatialAnchorsAsyncML

#### Passthrough
- xrCreatePassthroughFB, xrCreatePassthroughHTC
- xrCreatePassthroughLayerFB, xrCreatePassthroughLayerANDROID
- xrPassthroughStartFB, xrPassthroughPauseFB

#### Body Tracking
- xrCreateBodyTrackerFB, xrCreateBodyTrackerBD, xrCreateBodyTrackerHTC
- xrLocateBodyJointsFB, xrLocateBodyJointsBD, xrLocateBodyJointsHTC

#### Face Tracking
- xrCreateFaceTrackerFB, xrCreateFaceTracker2FB, xrCreateFaceTrackerANDROID
- xrGetFaceExpressionWeightsFB, xrGetFaceStateANDROID

#### Eye Tracking
- xrCreateEyeTrackerFB, xrGetEyeGazesFB

#### Scene Understanding (MSFT)
- xrCreateSceneObserverMSFT, xrComputeNewSceneMSFT, xrCreateSceneMSFT
- xrGetSceneComponentsMSFT, xrLocateSceneComponentsMSFT

#### Scene Meshing (ANDROID)
- xrCreateSceneMeshingTrackerANDROID, xrCreateSceneMeshSnapshotANDROID
- xrGetAllSubmeshStatesANDROID, xrGetSubmeshDataANDROID

#### Environment Depth (META)
- xrCreateEnvironmentDepthProviderMETA, xrCreateEnvironmentDepthSwapchainMETA
- xrAcquireEnvironmentDepthImageMETA

#### Trackables (ANDROID)
- xrCreateTrackableTrackerANDROID, xrGetAllTrackablesANDROID
- xrGetTrackablePlaneANDROID, xrGetTrackableImageANDROID
- xrGetTrackableMarkerANDROID, xrGetTrackableObjectANDROID

### 2.3 Object Handles (59 types)

Key handles:
- XrInstance, XrSession, XrSpace, XrSwapchain, XrAction, XrActionSet
- XrHandTrackerEXT, XrPlaneDetectorEXT, XrBodyTrackerFB/BD/HTC
- XrFaceTrackerFB/ANDROID/BD, XrEyeTrackerFB
- XrPassthroughFB/HTC, XrPassthroughLayerFB/ANDROID
- XrSpatialAnchorMSFT, XrSpatialAnchorsStorageML
- XrSceneMSFT, XrSceneObserverMSFT, XrSceneMeshingTrackerANDROID
- XrEnvironmentDepthProviderMETA, XrEnvironmentRaycasterMETA
- XrVirtualKeyboardMETA, XrWorldMeshDetectorML
- XrTrackableTrackerANDROID, XrTrackableImageDatabaseANDROID
- XrSpatialContextEXT, XrSpatialEntityEXT, XrSpatialPersistenceContextEXT

### 2.4 Key Extensions (AR Glasses Relevant)

#### Khronos (KHR) Extensions
- XR_KHR_opengl_es_enable - OpenGL ES graphics binding
- XR_KHR_vulkan_enable/enable2 - Vulkan graphics binding
- XR_KHR_android_create_instance - Android instance creation
- XR_KHR_composition_layer_cylinder/cube/equirect2 - Composition layers
- XR_KHR_visibility_mask - Visibility mask
- XR_KHR_locate_spaces - Batch space location

#### EXT Extensions
- XR_EXT_hand_tracking - Hand joint tracking
- XR_EXT_hand_interaction - Hand-based interaction
- XR_EXT_eye_gaze_interaction - Eye gaze input
- XR_EXT_plane_detection - Plane detection
- XR_EXT_spatial_anchor - Spatial anchors
- XR_EXT_spatial_entity - Spatial entities
- XR_EXT_spatial_persistence - Spatial persistence
- XR_EXT_future - Async operation futures
- XR_EXT_user_presence - User presence detection
- XR_EXT_render_model - Render models

#### Android Extensions
- XR_ANDROID_trackables - Trackable objects
- XR_ANDROID_trackables_image/marker/object/qr_code - Specific trackable types
- XR_ANDROID_scene_meshing - Scene mesh generation
- XR_ANDROID_spatial_anchor_space - Spatial anchor spaces
- XR_ANDROID_device_anchor_persistence - Device-local anchor persistence
- XR_ANDROID_composition_layer_passthrough_mesh - Passthrough mesh
- XR_ANDROID_face_tracking - Face tracking
- XR_ANDROID_raycast - Raycasting
- XR_ANDROID_performance_metrics - Performance metrics

#### META Extensions
- XR_META_environment_depth - Environment depth
- XR_META_environment_raycast - Environment raycasting
- XR_META_foveation_eye_tracked - Foveated rendering
- XR_META_passthrough_color_lut - Passthrough color manipulation
- XR_META_spatial_entity_discovery/persistence/sharing - Spatial entities
- XR_META_simultaneous_hands_and_controllers - Dual input
- XR_META_virtual_keyboard - Virtual keyboard
- XR_META_body_tracking_fidelity/calibration - Body tracking

#### Qualcomm (QCOM) Extensions
- XR_QCOM_tracking_optimization_settings - Tracking optimization
- XR_QCOM_hand_tracking_gesture - Hand gestures

#### Other Vendor Extensions
- XR_FB_* - Meta/Facebook (passthrough, body tracking, scene, spatial entities)
- XR_ML_* - Magic Leap (spatial anchors, world mesh, markers, facial expression)
- XR_MSFT_* - Microsoft (spatial anchor, scene understanding, hand mesh)
- XR_HTC_* - HTC (body tracking, facial tracking, passthrough, foveation)
- XR_BD_* - ByteDance (body tracking, spatial sensing, spatial audio)
- XR_VARJO_* - Varjo (foveated rendering, depth, markers)

### 2.5 Scalar Types

- XrBool32, XrDuration, XrTime, XrVersion, XrPath, XrSystemId
- XrFlags64, XrFutureEXT, XrMarkerML, XrRenderModelKeyFB
- XrSpaceUserIdFB, XrTrackableANDROID, XrSpatialEntityIdEXT/BD

---

# 3. Snap OS 2.0
## Source: https://newsroom.snap.com/introducing-snap-os-2.0
## Published: September 15, 2025

### 3.1 Overview

Snap OS 2.0 is the next generation operating system for Snap's fifth-generation Spectacles. It enables real-time AI-powered experiences with natural hand and voice interaction.

**Public Launch:** Specs launching publicly in 2026.

### 3.2 Announced Capabilities

#### Browser (Overhauled)
- New minimalist design for Snap OS
- Optimized page loading speed and power usage
- New home screen with widgets and bookmarks
- Updated toolbar: type or speak URLs, navigate history, refresh
- Window resizing (customizable aspect ratio like a laptop)
- **WebXR support** - immersive AR experiences directly from WebXR-enabled websites

#### Spotlight (Reimagined)
- Dedicated Spotlight Lens for phone-free content consumption
- Spatially overlays content onto the real world
- Portrait orientation matches Spectacles' field of view (perfect for vertical video)
- Can anchor content in place or have it follow the user
- Example: Watch creator videos while doing dishes

#### Snapping & Sharing
- New Gallery Lens for viewing Spectacles captures
- Interactive layout with curving carousel of videos
- Zoom in for detail
- Organize favorites, send to friends, or post to Snapchat Story

#### Travel Mode
- Stabilizes AR content and tracking while moving
- Works on planes, trains, and in cars (passenger seat)
- Ensures digital content stays anchored and stable during transit

#### Developer Ecosystem
- Hundreds of developers from 30+ countries building Lenses
- Popular Lenses: SightCraft (Enklu), NavigatAR (Utopia Labs), Pool Assist (Studio ANRK)
- Snap-made: Finger Paint, Chess, Imagine Together
- **Synth Riders** (rhythm game) coming to Spectacles - freestyle dancing in real world

### 3.3 Key Technical Capabilities
- Real-time AI-powered experiences
- Hand interaction (natural gestures)
- Voice interaction
- Spatial content anchoring
- Content stabilization during movement
- WebXR web standards support
- Lens development platform

---

# 4. Qualcomm RayNeo X3 Pro Development Guide
## Source: https://www.qualcomm.com/developer/project/get-started-with-rayneo-x3-pro-ar-development
## Published: January 15, 2026

### 4.1 Overview

The RayNeo X3 Pro smart glasses are powered by **Snapdragon AR1 Gen 1** chipset, offering high-performance on-device AI and AR experiences.

### 4.2 Equipment & Resources

**Required:**
- RayNeo X3 Pro smart glasses

**Development Resources:**
| Resource | URL |
|----------|-----|
| ADB Steps Guide | https://www.youtube.com/watch?v=l3wu7x14LKY |
| Device Introduction | https://leiniao-ibg.feishu.cn/wiki/X4nqwAsr6ioAEBklJZIcPfgyn9c |
| Qualcomm Spaces Config Tool | Snapdragon Spaces Compatibility Plugin for Android XR |
| Design Specifications | https://leiniao-ibg.feishu.cn/wiki/TnHLw4vL4iZgFtkPiMZcxWl8nkb |
| OpenXR Unity ARDK | https://leiniao-ibg.feishu.cn/wiki/Fpyjw4VOAiRnW9kwZWycvLsJnFf |
| ARDK for Android | https://leiniao-ibg.feishu.cn/wiki/FJ5ow2TCri336zkwLpuciIiJn5d |
| Debugging Tools | https://leiniao-ibg.feishu.cn/wiki/I9AIwlDciiI5IIkJDvkcX8Lwn1f |
| FAQ | https://leiniao-ibg.feishu.cn/wiki/LG8JwMt3fiL1TIkjtkzcPHJJnFc |

### 4.3 SDK Options

Two official SDKs:
1. **RayNeo OpenXR Unity ARDK** - AR capabilities (3DoF, SLAM, 6DoF, plane detection)
2. **ARDK for Android** - Native Android development

For Glass OS above 23.8.29: Use Unity SDK 1.1.2

### 4.4 Head Control Modes

| Mode | Description |
|------|-------------|
| SLAM Mode | 6DoF, face detection, plane detection |
| DOF3 | Conventional 3DoF |
| DOF_WITH_ABSOLUTE_ORIENTATION | 3DoF + magnetometer binding |

Configure via: BuildSettings -> XR Plug-in Management -> OpenXR -> RayNeoSupport -> Camera Attitude Type

### 4.5 Unity Setup

**Recommended Unity Versions:**
- X3Pro SDK: Unity Editor 2022.3.36f1c1
- Compatible: 2020.3.20LTS+, 2021.3.0LTS+, 2022.2.0+, 2023.1.0+

**Setup Steps:**
1. Install Unity Hub + Editor with Android support (SDK, NDK, OpenJDK)
2. Create 3D project
3. Import RayNeo ARDK via Package Manager (package.json)
4. Accept new input system, restart editor
5. Switch platform to Android
6. Enable OpenXR + RayNeo XR feature group in XR Plug-in Management
7. Fix All validation issues

### 4.6 Required Configuration

**AndroidManifest.xml** (Critical):
```xml
<activity android:name="com.rayneo.openxradapter.UnityOpenXrActivity"
          android:theme="@style/UnityThemeSelector">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
    <meta-data android:name="unityplayer.UnityActivity" android:value="true" />
</activity>
<meta-data android:name="com.rayneo.mercury.app" android:value="true" />
```

### 4.7 XR Plugin Prefab Elements

| Element | Description |
|---------|-------------|
| XR Plugin | Main object |
| LaserBeam | Ray control unit (camera-linked) |
| BeamGraphic | Ray renderer (can be disabled) |
| LaserBeamDot | Interaction point on collision |
| Head | Camera control for 3DoF head tracking |

**Game View Resolution:** 640x480 (adjust per device)

### 4.8 Building First App

1. Create scene, delete Main Camera and Directional Light
2. Add XR Plugin prefab from Packages/RayNeo OpenXR ARDK/SDK/Runtime/Resources/Prefab
3. Create UI with Canvas (World Space, position (0,0,1000))
4. Replace Graphic Raycaster with XRGraphicRaycaster
5. Build And Run

**Expected Results:**
- Stereoscopic rendering works (visible in scrcpy)
- 3DoF head tracking functional
- Temple click triggers button events

### 4.9 Key Notes

- Audio, camera, gyroscope: Use Android native APIs directly
- Power consumption: AR glasses have high requirements; optimize app power
- Vuforia partial support on X2 but limited by temperature/power
- Debugging: Use scrcpy for screen mirroring

---

# 5. RayNeo Android Dev (Japanese)
## Source: https://zenn.dev/satohjohn/articles/a06815e13b9f7f
## Published: 2026/04/05
## Title: RayNeoでAndroidアプリを作ってインストール (Building and Installing Android Apps on RayNeo)

### 5.1 Overview (Translation)

The RayNeo X3 Pro is a smart glass device that can run custom Android apps.

**Project Goals:**
- Create Android app for RayNeo X3 Pro
- Capture camera images and send to server
- Upload images to Google Cloud Run via HTTPS
- Install and run on AR glasses

### 5.2 Setup Milestones

1. App creation environment setup
2. RayNeo X3 Pro configuration
3. Android app development
4. Cloud Run app creation

### 5.3 Environment Setup

**Install JDK + Android Studio:**
```bash
brew install --cask zulu@17
brew install --cask android-studio
```

**Environment variable:**
```bash
export PATH=$PATH:$HOME/Library/Android/sdk/platform-tools
```

**Verify ADB:**
```bash
$ adb version
Android Debug Bridge version 1.0.41
```

### 5.4 RayNeo X3 Developer Mode

Enable developer mode on RayNeo X3:
- Go to Settings > General
- Swipe left 10 times to trigger "wall collision effect"
- This enables/disables ADB mode (for X3Pro with OS 25.8.13+)

**Verify device connection:**
```bash
$ adb devices -l
A06B4A37D5FF133  device usb:0-1 product:RayNeoX3Pro model:ARGF20 device:MercuryLiteXR
```

### 5.5 Key Development Notes

1. **Background must be black** (appears transparent on AR glasses)
2. **Smartphone apps require controller** (RayNeo companion app)
3. **For smart glasses apps**, add metadata to AndroidManifest.xml:
```xml
<meta-data android:name="com.rayneo.mercury.app" android:value="true" />
```
This bypasses the need for a controller and installs outside AppLab.

4. **WiFi connectivity** works with standard Android permissions
5. **Camera access** uses standard Android Camera APIs

### 5.6 AndroidManifest.xml Permissions

```xml
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_CAMERA"/>
<uses-feature android:name="android.hardware.camera" android:required="true"/>
```

### 5.7 Camera Image Upload Implementation

Uses OkHttp for image upload to Cloud Run, CameraX for camera capture:
- 10-second interval image capture and upload
- OkHttpClient with 10s connect timeout, 30s write timeout
- CameraX ImageAnalysis with STRATEGY_KEEP_ONLY_LATEST
- YUV_420_888 output format

### 5.8 Debugging Tools

- **scrcpy** recommended for screen mirroring (mouse/keyboard control is easier than temple taps)
- Install via `adb install` or directly from Android Studio

---

# CROSS-PLATFORM COMPARISON MATRIX

| Capability | XREAL SDK | OpenXR 1.1 | Snap OS 2.0 | RayNeo X3 Pro |
|------------|-----------|------------|-------------|---------------|
| 6DoF Tracking | Yes (Air 2 Ultra, One w/RGB) | xrLocateSpace/xrLocateSpaces | Yes (implied) | Yes (SLAM mode) |
| 3DoF Tracking | Yes (all devices) | Via reference space | Yes | Yes (DOF3 mode) |
| Hand Tracking | Yes (Air 2 Ultra) | XR_EXT_hand_tracking | Yes (natural gestures) | No (temple/ring input) |
| Plane Detection | Yes (Air 2 Ultra) | XR_EXT_plane_detection | Not announced | Yes (SLAM mode) |
| Image Tracking | Yes (Air 2 Ultra) | XR_ANDROID_trackables_image | Not announced | Via ARDK |
| Spatial Anchors | Yes (Air 2 Ultra) | Multiple extensions | Content anchoring | Not documented |
| Depth Mesh | Yes (Air 2 Ultra) | XR_ANDROID_scene_meshing | Not announced | Not documented |
| Passthrough | First Person View | XR_FB/HTC/ANDROID_passthrough | AR overlay native | AR overlay native |
| Voice Input | Not documented | Not directly | Yes | Not documented |
| WebXR | Not documented | Not directly | Yes (Browser) | Not documented |
| Body Tracking | Not documented | XR_FB/BD/HTC_body_tracking | Not announced | Not documented |
| Face Tracking | Not documented | XR_FB/ANDROID/BD_face_tracking | Not announced | Face detection (SLAM) |
| Eye Tracking | Not documented | XR_FB_eye_tracking_social | Not announced | Not documented |
| Development Engine | Unity (XR Plugin) | Any (C API) | Lens Studio | Unity (OpenXR ARDK) |
| Primary Chipset | Qualcomm (phone) / X1 (One) | Platform agnostic | Snapdragon (Spectacles) | Snapdragon AR1 Gen 1 |
| Connection | USB-C to phone/BeamPro | Platform agnostic | Standalone | Standalone |

---

# SDK DOWNLOAD & RESOURCE LINKS

## XREAL
- SDK Download: https://developer.xreal.com/download
- API Reference: https://developer.xreal.com/reference/nrsdk/overview
- GitHub: https://github.com/nreal-ai
- Template Project: https://github.com/dengxian-xreal/XREALSDKTemplate
- Documentation: https://docs.xreal.com/

## OpenXR
- Specification: https://registry.khronos.org/OpenXR/specs/1.1/man/html/openxr.html
- Full Spec PDF: https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.html

## Snap / Spectacles
- Snap OS 2.0 Announcement: https://newsroom.snap.com/introducing-snap-os-2.0
- Spectacles Support: https://support.spectacles.com/

## RayNeo / Qualcomm
- RayNeo X3 Pro Product: https://www.rayneo.com/products/x3-pro-ai-display-glasses
- ARDK Download: https://leiniao-ibg.feishu.cn/wiki/IDFfwLKR4iihBuknkVrcGiMUnic
- Developer Manual: https://leiniao-ibg.feishu.cn/wiki/IwTRwecN0ikZcjkHAhicN5lWn0g
- Snapdragon Spaces Plugin: https://www.qualcomm.com/developer/software/snapdragon-spaces-compatibility-plugin-for-android-xr
- RayNeo Companion App: https://play.google.com/store/apps/details?id=com.rayneo.mercury

---
*Document generated by DEEP Wave 9 platform documentation crawler*
*All content extracted from public documentation sources*
