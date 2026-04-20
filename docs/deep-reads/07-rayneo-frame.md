# DEEP-wave5-rayneo-frame — Deep Analysis of 5 Repos
## RayNeo SDK, Frame TFLite Micro, Overpass Turbo

Generated: 2026-04-20

---

# TABLE OF CONTENTS

1. Metaverse-Max-RayNeo-X3-Pro-Set-Up (SDK v1.1.2)
2. Rayneo_OpenXR_ARDK_Project (SDK v1.0.0)
3. RayNeoX3Pro-MITSample (SDK v1.1.2)
4. frame-codebase (TFLite Micro on Brilliant Labs Frame)
5. overpass-turbo (Overpass API query tool)

---

# 1. METAVERSE-MAX-RAYNEO-X3-PRO-SET-UP

## Overview
Basic RayNeo X3 Pro setup guide and sample project by Max Manausa.
Unity project demonstrating core SDK features. Includes APK for direct install.
SDK Version: RayNeo OpenXR ARDK 1.1.2

## Source Files (25 C# files)

### SDK Integration Scripts
- Scripts/Algorithm/SlamDemoCtrl.cs
- Scripts/Algorithm/Sensor/TestSensorAlgorithm.cs
- Scripts/Algorithm/Sensor/CompassMgr/CompassGenerate.cs
- Scripts/Algorithm/PlaneDetection/TestPlaneDetection.cs
- Scripts/Algorithm/Facial/TestRuntimeFacial.cs
- Scripts/Algorithm/Facial/CreateCube.cs
- Scripts/Interactive/TestTouchEvent.cs
- Scripts/Interactive/TestIPC.cs
- Scripts/Interactive/ShareCameraCtrl.cs
- Scripts/Interactive/RingTouchCube.cs
- Scripts/Interactive/BaseInteraction.cs
- Scripts/SampleScene/SampleSceneCtrl.cs
- Scripts/SampleScene/SampleCubeCtrl.cs
- Scripts/SampleScene/RayNeoInfo/TestRayNeoInfoExtension.cs
- Scripts/Scene1Ctrl.cs
- Scripts/ResetHeadTrack.cs
- Scripts/KillSelf.cs
- Scripts/DoubleTabBackSceneCtrl.cs
- Scripts/Tool/ShowFps.cs
- Scripts/Tool/SetCanvasOverlay.cs
- Scripts/Tool/GetDeviceInfo.cs
- Scripts/Tool/CameraPermissionRequest.cs
- Assets/CanvasSwitcher.cs

## Key Namespaces & SDK Imports
```
using RayNeo;
using RayNeo.API;
using com.rayneo.xr.extensions;
using FfalconXR;
using static com.rayneo.xr.extensions.XRCamera;
```

## Classes & Methods Extracted

### SlamDemoCtrl : MonoBehaviour [6DOF SLAM]
- IMPORTS: RayNeo, RayNeo.API
- Start() — calls Algorithm.EnableSlamHeadTracker(), subscribes HeadTrackedPoseDriver.OnPostUpdate
- OnPostUpdate(Pose pose) — receives position + rotation from SLAM
- OnDestroy() — calls Algorithm.DisableSlamHeadTracker()
- CreateCubes() — spawns cube grid for 6DOF visualization
- KEY SDK CALLS:
  * Algorithm.EnableSlamHeadTracker()
  * Algorithm.DisableSlamHeadTracker()
  * HeadTrackedPoseDriver.OnPostUpdate += callback

### TestPlaneDetection : MonoBehaviour [6DOF Plane Detection]
- IMPORTS: RayNeo, RayNeo.API, com.rayneo.xr.extensions, FfalconXR
- Awake() — Algorithm.EnableSlamHeadTracker() + Algorithm.EnablePlaneDetection()
- Update() — Algorithm.GetPlaneInfo(m_infoArrays), Algorithm.CreatePlaneMesh(), ConvertPlanePosition/Rotation
- OnDestroy() — Algorithm.DisablePlaneDetection() + Algorithm.DisableSlamHeadTracker()
- KEY SDK CALLS:
  * Algorithm.EnablePlaneDetection()
  * Algorithm.DisablePlaneDetection()
  * Algorithm.GetPlaneInfo(XRPlaneInfo[]) — returns int (plane count)
  * Algorithm.CreatePlaneMesh(info, gameObject, bool, material)
  * Algorithm.ConvertPlanePosition(info)
  * Algorithm.ConvertPlaneRotation(info)
- DATA TYPE: XRPlaneInfo with local_polygon, local_polygon_size, pose.position, pose.rotation

### TestRuntimeFacial : MonoBehaviour [Face Tracking]
- IMPORTS: RayNeo
- Start() — FaceDetectorManager.Ins.StartFaceDectector()
- Update() — FaceDetectorManager.Ins.GetFacePosition(out bool suc) returns Vector3
- OnDestroy() — FaceDetectorManager.Ins.StopFaceDectector()
- KEY SDK CALLS:
  * FaceDetectorManager.Ins.StartFaceDectector()
  * FaceDetectorManager.Ins.StopFaceDectector()
  * FaceDetectorManager.Ins.GetFacePosition(out bool) → Vector3

### TestTouchEvent : MonoBehaviour [Touch/Gesture Input]
- IMPORTS: RayNeo
- Start() — registers gesture listeners
- KEY SDK CALLS:
  * SimpleTouchForLite.Instance.OnSwipeUp.AddListener(callback)
  * SimpleTouchForLite.Instance.OnSwipeDown.AddListener(callback)
  * SimpleTouchForLite.Instance.OnSwipeLeft.AddListener(callback)
  * SimpleTouchForLite.Instance.OnSwipeRight.AddListener(callback)
  * SimpleTouchForLite.Instance.OnTripleTap.AddListener(callback)
  * SimpleTouchForLite.Instance.OnLongPress.AddListener(callback)
  * SimpleTouchForLite.Instance.OnDoubleTap.AddListener(callback)

### TestIPC : MonoBehaviour [Ring Controller + GPS + IPC]
- IMPORTS: RayNeo, RayNeo.API
- Start() — opens ring, GPS, creates RayNeoInput
- KEY SDK CALLS:
  * RingManager.OpenRing(RingTouchType.CustomTouchEvent, false)
  * RingManager.CloseRing()
  * IPC.OpenPhoneGPS()
  * IPC.ClosePhoneGPS()
  * IPC.GpsStateChagneCallBack += callback
  * IPC.GPSPushCallBack += callback
  * PermissionUtil.TryQueryPermission(permission)
  * RayNeoInput — new input system wrapper
  * m_Input.Ring.TouchPadClick.WasPressedThisFrame()
  * m_Input.Ring.Position.ReadValue<Vector3>()
  * m_Input.Ring.HeavyClick.IsPressed()
- DATA TYPES:
  * PhoneGPSResultType enum (UNKNOW, PHONE_CONNECTED, etc.)
  * RingTouchType.CustomTouchEvent

### ShareCameraCtrl : MonoBehaviour [Camera Access]
- IMPORTS: RayNeo.API, com.rayneo.xr.extensions.XRCamera
- KEY SDK CALLS:
  * ShareCamera.OpenCamera(XRCameraType, RawImage) → XRCameraHandler
  * ShareCamera.CloseCamera(XRCameraHandler)
  * ShareCamera.getSupportResolutions(XRCameraType) → XRResolution[]
- DATA TYPES: XRCameraType.RGB, XRCameraHandler, XRResolution {width, height}

### SampleSceneCtrl : MonoBehaviour [Scene Management]
- KEY SDK CALLS:
  * RayNeoInfo.DeviceIsIntegratedType() — device check
  * PlatformAndroid.OpenSystemMonitoring()
  * PlatformAndroid.CloseSystemMonitoring()

### TestRayNeoInfoExtension : MonoBehaviour
- KEY SDK CALLS: RayNeoInfoExtension.GetDeviceName()

### ResetHeadTrack : MonoBehaviour [3DOF Reset]
- KEY SDK CALLS: HeadTrackedPoseDriver.ResetQuaternion()

### Scene1Ctrl : MonoBehaviour [UI Navigation]
- KEY SDK CALLS:
  * LatticeBrain.FocusLevel(level)
  * LatticeBrain.SelectButton(button)
  * LatticeBrain.RemoveButton(button)
  * LatticeBrain.MovingChangeItem = bool

### TestSensorAlgorithm : MonoBehaviour [Compass/Azimuth]
- KEY SDK CALLS: Algorithm.GetAzimuth() → float (yaw angle)

### GetDeviceInfo : MonoBehaviour [System Info]
- Uses FfalconXR.Log.Debug() for logging
- Uses UnityEngine.SystemInfo for device info

### CanvasSwitcher : MonoBehaviour [Custom — not SDK]
- Auto-cycles through UI canvases on timer

---

# 2. RAYNEO_OPENXR_ARDK_PROJECT (6DOF Art Gallery)

## Overview
6DOF art gallery project using RayNeo OpenXR ARDK v1.0.0 (earlier SDK version).
Similar structure to repo #1 but v1.0.0 SDK. Includes MetaSpace portal effects.

## Source Files (25 C# files)
Same SDK sample scripts as repo #1 but at v1.0.0 path, PLUS:
- Res/Algorithm/Sensor/MetaSpace/Scripts/Effect/RadomPlacment.cs
- Res/Algorithm/Sensor/MetaSpace/Scripts/Effect/QuikeController.cs
- Res/Algorithm/Sensor/MetaSpace/Scripts/Effect/PreviewObject.cs
- Res/Algorithm/Sensor/MetaSpace/Scripts/Effect/PlanarReflection.cs
- Fantasy Portal FX/Demo/Scripts/FantasyPortalSceneSelect.cs
- Fantasy Portal FX/Demo/Scripts/FantasyPortalRotation.cs
- Fantasy Portal FX/Demo/Scripts/FantasyPortalCameraOrbit.cs

## Key Differences from Repo #1 (v1.0.0 vs v1.1.2)
- SlamDemoCtrl v1.0.0 does NOT have HeadTrackedPoseDriver.OnPostUpdate callback
- v1.0.0 missing: TestTouchEvent, ShareCameraCtrl, CameraPermissionRequest, TestRayNeoInfoExtension
- v1.0.0 has MetaSpace environment effects (portals, reflections, random placement)

### Additional Classes

#### RadomPlacment : MonoBehaviour
- Start() — random placement of prefabs in radius circle

#### QuikeController : MonoBehaviour
- OnGUI() — simple switch button

#### PreviewObject : MonoBehaviour
- Update() — mouse-drag rotation or auto-rotation

---

# 3. RAYNEX3PRO-MITSAMPLE (MIT Reality Hack 2026)

## Overview
Official MIT Reality Hack 2026 sample project. Unity 2022.3.36f1.
SDK Version: RayNeo OpenXR ARDK 1.1.2 (same as repo #1).

## Key Features Demonstrated
- Dual Display Rendering (priority focus rendering)
- 6DoF & 3DoF Tracking
- Face Tracking
- Scene Detection (plane detection)
- Gaze Interaction
- Gesture controls, spatial audio

## Source Files (22 C# files)
Identical SDK sample scripts as repo #1 (v1.1.2).
Same classes, same methods, same SDK calls.

## Complete SDK API Surface (consolidated from all 3 RayNeo repos)

### RayNeo.API.Algorithm (Static Class)
| Method | Category |
|--------|----------|
| Algorithm.EnableSlamHeadTracker() | 6DOF SLAM |
| Algorithm.DisableSlamHeadTracker() | 6DOF SLAM |
| Algorithm.EnablePlaneDetection() | 6DOF Planes |
| Algorithm.DisablePlaneDetection() | 6DOF Planes |
| Algorithm.GetPlaneInfo(XRPlaneInfo[]) → int | 6DOF Planes |
| Algorithm.CreatePlaneMesh(info, go, bool, mat) | 6DOF Planes |
| Algorithm.ConvertPlanePosition(info) → Vector3 | 6DOF Planes |
| Algorithm.ConvertPlaneRotation(info) → Quaternion | 6DOF Planes |
| Algorithm.GetAzimuth() → float | Sensors |

### RayNeo.HeadTrackedPoseDriver (Static)
| Method/Event | Category |
|--------------|----------|
| HeadTrackedPoseDriver.OnPostUpdate += Action<Pose> | 6DOF callback |
| HeadTrackedPoseDriver.ResetQuaternion() | 3DOF reset |

### RayNeo.FaceDetectorManager (Singleton)
| Method | Category |
|--------|----------|
| .Ins.StartFaceDectector() | Face Tracking |
| .Ins.StopFaceDectector() | Face Tracking |
| .Ins.GetFacePosition(out bool) → Vector3 | Face Tracking |

### RayNeo.SimpleTouchForLite (Singleton)
| Event | Category |
|-------|----------|
| .Instance.OnSwipeUp | Gesture |
| .Instance.OnSwipeDown | Gesture |
| .Instance.OnSwipeLeft | Gesture |
| .Instance.OnSwipeRight | Gesture |
| .Instance.OnDoubleTap | Gesture |
| .Instance.OnTripleTap | Gesture |
| .Instance.OnLongPress | Gesture |

### RayNeo.RingManager (Static)
| Method | Category |
|--------|----------|
| RingManager.OpenRing(RingTouchType, bool) | Ring Controller |
| RingManager.CloseRing() | Ring Controller |

### RayNeo.API.IPC (Static)
| Method/Event | Category |
|--------------|----------|
| IPC.OpenPhoneGPS() | GPS |
| IPC.ClosePhoneGPS() | GPS |
| IPC.GpsStateChagneCallBack += callback | GPS |
| IPC.GPSPushCallBack += callback | GPS |

### RayNeo.API.ShareCamera (Static)
| Method | Category |
|--------|----------|
| ShareCamera.OpenCamera(XRCameraType, RawImage) → XRCameraHandler | Camera |
| ShareCamera.CloseCamera(XRCameraHandler) | Camera |
| ShareCamera.getSupportResolutions(type) → XRResolution[] | Camera |

### RayNeo.API.PlatformAndroid (Static)
| Method | Category |
|--------|----------|
| PlatformAndroid.OpenSystemMonitoring() | System |
| PlatformAndroid.CloseSystemMonitoring() | System |

### RayNeo.API.RayNeoInfo / RayNeoInfoExtension
| Method | Category |
|--------|----------|
| RayNeoInfo.DeviceIsIntegratedType() → bool | Device |
| RayNeoInfoExtension.GetDeviceName() → string | Device |

### Other SDK Types
| Type | Purpose |
|------|---------|
| RayNeoInput | New Input System wrapper |
| RayTrackedPoseDriver | Ray-based pose driver |
| LatticeButton / LatticeBrain | Grid-based UI navigation |
| PermissionUtil | Android permission helper |
| XRPlaneInfo | Plane detection data |
| XRCameraType | Camera type enum (RGB) |
| XRCameraHandler | Camera handle |
| XRResolution | Resolution struct {width, height} |
| PhoneGPSResultType | GPS state enum |
| RingTouchType | Ring input type enum |

### 3DOF vs 6DOF Pattern Summary
- **3DOF (rotation only)**: Use HeadTrackedPoseDriver with ResetQuaternion(). No SLAM needed. HUD-style.
- **6DOF (full spatial)**: Call Algorithm.EnableSlamHeadTracker() + subscribe to HeadTrackedPoseDriver.OnPostUpdate for position+rotation. World-anchored content.
- **6DOF + Planes**: Add Algorithm.EnablePlaneDetection() + GetPlaneInfo() in Update loop.

---

# 4. FRAME-CODEBASE (TFLite Micro on Brilliant Labs Frame)

## Overview
Fork of Brilliant Labs Frame smart glasses firmware. Embeds TensorFlow Lite for
Microcontrollers (TFLM) directly into nRF52840 firmware for on-device ML inference.
Master's thesis at TU Graz, ELSS group.

Hardware: nRF52840 (Cortex-M4F), 256 KB RAM, ~824 KB flash.

## Architecture
- nRF52 Application (Lua runtime + BLE + AI + power management)
- nRF52 Bootloader (DFU support)
- FPGA RTL (graphics + camera pipelines, prebuilt)

## Source Files

### Application Core (C)
- source/application/main.c — main entry, TFLM init, hardware init
- source/application/bluetooth.c — BLE communication
- source/application/boot_safety.c — watchdog reset detection, DFU recovery
- source/application/compression.c — data compression
- source/application/flash.c — flash storage
- source/application/luaport.c — Lua runtime port
- source/application/spi.c — SPI bus (FPGA communication)
- source/application/watchdog.c — watchdog timer

### TFLM Integration (C++)
- source/application/tflm_wrapper.cc — C-compatible TFLM wrapper (601 lines)
- source/application/tflm_wrapper.h — public API header

### ML Experiment Modules (C, Lua-callable)
- source/application/lua_libraries/experiment_common.c — shared JPEG decode + image processing
- source/application/lua_libraries/experiment_common.h — shared types/declarations
- source/application/lua_libraries/experiment_vww.c — Visual Wake Words (grayscale)
- source/application/lua_libraries/experiment_vww_rgb.c — Visual Wake Words (RGB)
- source/application/lua_libraries/experiment_fomo.c — FOMO object detection (beer can)
- source/application/lua_libraries/experiment_hello_world.c — sine prediction demo

### Lua Libraries (C)
- lua_libraries/bluetooth.c
- lua_libraries/camera.c
- lua_libraries/compression.c
- lua_libraries/display.c
- lua_libraries/file.c
- lua_libraries/imu.c
- lua_libraries/led.c
- lua_libraries/microphone.c (disabled via FRAME_DISABLE_MICROPHONE)
- lua_libraries/system.c
- lua_libraries/time.c
- lua_libraries/version.c

### Model Data (Header files)
- models/person_detect.h — VWW grayscale model
- models/person_detect_rgb.h — VWW RGB model
- models/fomo_beer_can.h — FOMO beer can model
- models/hello_world_int8.h — Hello World quantized model

### Build Configuration
- source/application/config.mk — ML_EXPERIMENT selector (VWW, VWW_RGB, FOMO_BEER_CAN, HELLO_WORLD)

## Key Types & Enums

### tflm_status_t
```c
typedef enum { TFLM_OK = 0, TFLM_ERROR = 1 } tflm_status_t;
```

### tflm_model_info_t
```c
typedef struct {
    tflm_model_type_t type;     // TFLM_MODEL_FLOAT or TFLM_MODEL_INT8
    uint32_t model_size_bytes;
    uint32_t arena_size_bytes;
    bool initialized;
} tflm_model_info_t;
```

### jpeg_ctx_t
```c
typedef struct {
    const uint8_t *data;     // JPEG input data
    size_t size;             // Total JPEG size
    size_t offset;           // Read position
    uint8_t *buffer;         // Output pixel buffer
    uint16_t width, height;  // Image dimensions
    uint16_t buf_width;      // Buffer row stride
} jpeg_ctx_t;
```

## TFLM Wrapper API (tflm_wrapper.h)

### FOMO Object Detection (ML_EXPERIMENT_FOMO_BEER_CAN)
| Function | Signature |
|----------|-----------|
| fomo_initialize() | → tflm_status_t |
| fomo_infer(uint8_t* gray_64x64, int8_t* grid_8x8x3) | → tflm_status_t |
| fomo_is_initialized() | → bool |
| Constants: FOMO_INPUT_SIZE=4096, FOMO_OUTPUT_SIZE=192, FOMO_GRID_SIZE=8, FOMO_NUM_CLASSES=3 |
| Tensor arena: 135 KB |
| Ops: Conv2D, DepthwiseConv2D, Add, Reshape, Pad, MaxPool2D, Relu6, Mean, Softmax |

### Person Detection / VWW (ML_EXPERIMENT_VWW)
| Function | Signature |
|----------|-----------|
| person_detect_initialize() | → tflm_status_t |
| person_detect_infer(uint8_t* gray_96x96, int8_t* scores_2) | → tflm_status_t |
| person_detect_is_initialized() | → bool |
| Constants: PERSON_INPUT_SIZE=9216 (96x96x1), PERSON_OUTPUT_SIZE=2 |
| Tensor arena: 78 KB (grayscale), 100 KB (RGB) |
| Ops: AveragePool2D, Conv2D, DepthwiseConv2D, Reshape, Softmax, Mean, FullyConnected |

### Person Detection RGB (ML_EXPERIMENT_VWW_RGB)
| Same API as VWW but PERSON_INPUT_SIZE=27648 (96x96x3) |

### Hello World (ML_EXPERIMENT_HELLO_WORLD)
| Function | Signature |
|----------|-----------|
| tflm_initialize() | → tflm_status_t (float model) |
| tflm_infer(float input, float* output) | → tflm_status_t |
| tflm_initialize_int8() | → tflm_status_t (int8 model) |
| tflm_infer_int8(float input, float* output) | → tflm_status_t |
| tflm_get_float_model_info(tflm_model_info_t*) | → tflm_status_t |
| tflm_get_int8_model_info(tflm_model_info_t*) | → tflm_status_t |
| Float arena: 3000 bytes, Int8 arena: 2500 bytes |
| Ops: FullyConnected only |

## Image Processing Pipeline

### Grayscale Path (VWW / FOMO)
```
Camera JPEG (720x720) → TJpgDec scale=3 (90x90 gray) → bilinear upscale + 90° CCW rotation (96x96) → TFLM inference
```

### RGB Path (VWW_RGB)
```
Camera JPEG (720x720) → TJpgDec scale=3 (90x90 RGB) → bilinear upscale + 90° CCW rotation (96x96x3) → TFLM inference
```

### FOMO Path
```
Camera JPEG (720x720) → TJpgDec scale=3 (90x90 gray) → upscale + rotation (96x96) → crop/resize to 64x64 → FOMO inference → 8x8x3 detection grid
```

## Shared Image Functions (experiment_common.c)
| Function | Purpose |
|----------|---------|
| jpeg_decode_grayscale_scaled() | JPEG → grayscale with optional scale + rotation |
| jpeg_decode_grayscale() | Legacy 1:1 wrapper |
| jpeg_decode_rgb_scaled() | JPEG → RGB888 with optional scale + rotation |
| upscale_90_to_96_with_rotation() | Bilinear upscale gray 90→96 + 90° CW rotation |
| upscale_90_to_96_rgb_with_rotation() | Bilinear upscale RGB 90→96 + 90° CCW rotation |
| lua_open_experiment_library() | Registers frame.experiment.* Lua functions |

## Lua-Callable Experiment Functions

### VWW / VWW_RGB Experiments
| Lua API | C Function |
|---------|------------|
| frame.experiment.run_person_detection() | lua_experiment_run_person_detection |
| frame.experiment.run_person_detection_benchmark(n) | lua_experiment_run_person_detection_benchmark |
| frame.experiment.init_model() | lua_experiment_init_model |
| frame.experiment.get_name() | lua_experiment_get_name |

### FOMO Experiment
| Lua API | C Function |
|---------|------------|
| frame.experiment.run_detection() | lua_experiment_run_detection |
| frame.experiment.send_grayscale() | lua_experiment_send_grayscale |
| frame.experiment.init_model() | lua_experiment_init_model |

### Hello World Experiment
| Lua API | C Function |
|---------|------------|
| frame.experiment.infer(angle) | lua_experiment_infer |
| frame.experiment.infer_int8(angle) | lua_experiment_infer_int8 |
| frame.experiment.run_test() | lua_experiment_run_test |
| frame.experiment.get_model_info() | lua_experiment_get_model_info |

## Frame Camera Lua API (used by experiments)
```lua
frame.camera.power_save(false)    -- wake camera
frame.camera.auto({})             -- auto-adjust exposure
frame.camera.capture({resolution=720, quality="MEDIUM"})
frame.camera.image_ready()        -- poll for completion
frame.camera.read(512)            -- read JPEG chunks
```

## Frame Display Lua API (used by hello_world)
```lua
frame.display.text(str, x, y, {color='GREEN'})
frame.display.show()
frame.sleep(seconds)
```

## Boot Safety (boot_safety.c)
| Function | Purpose |
|----------|---------|
| boot_safety_init() | Check watchdog resets, increment boot counter, enter DFU after 5 fails |
| enter_dfu_mode() | Set GPREGRET flag + NVIC_SystemReset() |
| MAX_BOOT_ATTEMPTS = 5 |

## Bluetooth Data Protocol (VWW output)
```
[0x01][IMAGE_DATA...]     — 96x96 grayscale (9216 bytes in 200-byte chunks)
[0x01][0xFE][0xFE]        — separator
[0x01][SCORES...]          — 2 bytes (not_person, person)
[0x01][0xFF][0xFF][0x00][0x00] — end marker
```

## Build System Key Flags
- CMSIS-NN: ARM Cortex-M4 optimized kernels for NN ops
- -fno-rtti -fno-exceptions -DTF_LITE_STATIC_MEMORY
- FRAME_DISABLE_MICROPHONE: frees RAM for ML tensor arenas
- ML_EXPERIMENT=VWW|VWW_RGB|FOMO_BEER_CAN|HELLO_WORLD (config.mk)

## Frame Lua Library Registration (frame_lua_libraries.h)
```c
lua_open_bluetooth_library(L);
lua_open_camera_library(L);
lua_open_compression_library(L);
lua_open_display_library(L);
lua_open_imu_library(L);
lua_open_led_library(L);
lua_open_microphone_library(L);  // conditional
lua_open_system_library(L);
lua_open_time_library(L);
lua_open_version_library(L);
lua_open_experiment_library(L);  // NEW — ML experiments
lua_open_file_library(L, reformat);
```

---

# 5. OVERPASS-TURBO

## Overview
GUI for testing/developing Overpass API queries for OpenStreetMap data.
TypeScript + Leaflet web application. Supports OverpassQL, XML, and SQL query languages.

## Source Files (37 TypeScript files)

### Core Application
- js/ide.ts — Main IDE class (2834 lines)
- js/overpass.ts — Overpass API client (855 lines)
- js/query.ts — Query parser with mustache templates
- js/map.ts — Leaflet map management
- js/settings.ts — User settings
- js/configs.ts — App configuration
- js/index.ts — Entry point
- js/i18n.ts — Internationalization

### Query Processing
- js/ffs.ts — Free-form search / wizard query builder
- js/ffs/free.ts — Free-form query module
- js/autorepair.ts — Query auto-repair (recurse, editors fix)
- js/shortcuts.ts — Query shortcuts/templates
- js/nominatim.ts — Nominatim geocoding client

### Data Visualization
- js/OSM4Leaflet.ts — OSM to Leaflet conversion
- js/GeoJsonNoVanish.ts — GeoJSON layer with persistence
- js/popup.ts — Feature popup content
- js/PopupIcon.ts — Popup icon component
- js/leaflet.polylineoffset.ts — Polyline offset rendering
- js/urlParameters.ts — URL parameter handling
- js/sync-with-osm.ts — OSM sync
- js/misc.ts — Utilities (Base64, htmlentities, lzw)

### MapCSS Styling
- js/jsmapcss/index.ts
- js/jsmapcss/RuleSet.ts
- js/jsmapcss/RuleChain.ts
- js/jsmapcss/Rule.ts
- js/jsmapcss/StyleList.ts
- js/jsmapcss/StyleChooser.ts
- js/jsmapcss/Style.ts
- js/jsmapcss/Condition.ts

### Tests
- tests/test.query.ts
- tests/test.ffs.ts
- tests/test.autorepair.recurse.ts
- tests/test.autorepair.josm.ts
- tests/test.popup.ts
- tests/test.permalink.ts
- tests/test.mapcss.eval.ts
- tests/test.urlParameters.ts

## Key Classes & Functions

### class Overpass (overpass.ts)
Core Overpass API client.
| Member | Purpose |
|--------|---------|
| run_query(query, query_lang, cache, shouldCacheOnly, server, options, user_mapcss) | Execute Overpass query |
| init() | Register MapCSS extensions |
| handlers {} | Event handler registry |
| fire(name, ...args) | Fire event handlers |
| QueryLang type | "xml" | "OverpassQL" | "SQL" |

Key patterns:
- Sends query via jQuery $.ajax to Overpass API server
- Supports XML and OverpassQL formats
- Handles kill_my_queries for abort
- Parses JSON/XML responses
- Creates GeoJSON via L_OSM4Leaflet
- Applies MapCSS styling

### class parser (query.ts)
Mustache template parser for queries.
| Method | Purpose |
|--------|---------|
| parse(query, shortcuts, found_statements) | Replace {{...}} templates |
| hasStatement(name) | Check if statement exists |
| getStatement(name) | Get statement value |

Template patterns:
- {{constant=value}} — user-defined constants
- {{shortcut}} — predefined shortcuts
- {{shortcut:instruction}} — shortcuts with parameters
- {{bbox}} — current map bounding box
- {{center}} — current map center
- {{date:offset}} — date calculation
- {{geocodeArea:name}} — area geocoding
- {{geocodeCoords:name}} — coordinate geocoding

### ffs_construct_query() (ffs.ts)
Free-form search to Overpass query conversion.
| Parameter | Purpose |
|-----------|---------|
| search | Natural language search string |
| comment | Optional comment for generated query |
| callback | (error, query_string) callback |

Query clause types:
- key: `["key"]`
- nokey: `["key"!~".*"]`
- eq: `["key"="val"]`
- neq: `["key"!="val"]`
- like: `["key"~"regex"]`
- likelike: `[~"key"~"regex"]`
- notlike: `["key"!~"regex"]`
- meta/id: `(id_value)`
- meta/newer: `(newer:"date")`
- meta/user: `(user:"name")`
- meta/uid: `(uid:number)`
- free form: delegated to freeFormQuery module

Bounds modes:
- area: `{{geocodeArea:name}}->.searchArea;` + `(area.searchArea)`
- around: `(around:{{radius}},{{geocodeCoords:name}})`
- bbox: `({{bbox}})`
- global: no bounds

Output: `[out:json][timeout:25];` + union of nwr queries + `out geom;`

### class nominatim (nominatim.ts)
Geocoding via OpenStreetMap Nominatim.
| Method | Purpose |
|--------|---------|
| static request(search, callback) | Raw Nominatim API call |
| static get(search, callback) | Cached Nominatim lookup |
| static getBest(search, filter, callback) | Best result with optional filter |

### autorepair() (autorepair.ts)
Query auto-repair for JOSM compatibility.
| Method | Purpose |
|--------|---------|
| repair.recurse() | Add `>;` recurse statements for complete geometry |
| repair.editors() | Fix output format, add meta mode, fix geometry |
| repair.getQuery() | Return repaired query |
| autorepair.detect.editors(q, lng) | Detect if repair needed |

### class IDE (ide.ts)
Main IDE controller (2834 lines).
| Key Members | Purpose |
|-------------|---------|
| codeEditor | CodeMirror editor instance |
| dataViewer | Data viewer panel |
| map | Leaflet map |
| queryParser | Query template parser |
| waiter | Loading/progress indicator |
| init() | Initialize IDE |

## Overpass API Query Patterns

### Basic OverpassQL Pattern
```
[out:json][timeout:25];
nwr["key"="value"]({{bbox}});
out geom;
```

### Area Search Pattern
```
[out:json][timeout:25];
{{geocodeArea:CityName}}->.searchArea;
nwr["amenity"="restaurant"](area.searchArea);
out geom;
```

### Around Search Pattern
```
[out:json][timeout:25];
nwr["shop"="supermarket"](around:1000,{{geocodeCoords:PlaceName}});
out geom;
```

### Union Query Pattern
```
[out:json][timeout:25];
(
  node["amenity"="cafe"]({{bbox}});
  way["amenity"="cafe"]({{bbox}});
  relation["amenity"="cafe"]({{bbox}});
);
out geom;
```

---

# CROSS-REPO INTEGRATION PATTERNS

## Pattern: AR Glasses + Overpass API Location Query
1. RayNeo IPC.OpenPhoneGPS() → get GPS coordinates
2. Build Overpass query: `nwr["amenity"](around:500,{lat},{lon}); out geom;`
3. Send query to Overpass API server
4. Parse GeoJSON response
5. Place 3D markers using Algorithm.EnableSlamHeadTracker() for 6DOF

## Pattern: Frame Glasses + On-Device ML
1. frame.camera.capture() → JPEG image
2. JPEG decode → grayscale/RGB buffer
3. Bilinear upscale + rotation to model input size
4. TFLM inference (person_detect_infer / fomo_infer)
5. Display overlay via FPGA SPI (spi_write 0x12/0x14)
6. Send results via Bluetooth (bluetooth_send_data)

## Pattern: 3DOF HUD vs 6DOF World-Anchored
- 3DOF: HeadTrackedPoseDriver only (rotation). Canvas follows head. Reset with double-tap.
- 6DOF: Algorithm.EnableSlamHeadTracker() + OnPostUpdate for full pose. Objects anchored in world space.

---

# SUMMARY STATISTICS

| Repo | Language | Files | Key Classes | SDK Calls |
|------|----------|-------|-------------|-----------|
| Metaverse-Max-RayNeo | C# | 25 | 13 MonoBehaviour | 35+ SDK methods |
| Rayneo_OpenXR_ARDK | C# | 25 | 13+7 additional | Same SDK v1.0.0 |
| RayNeoX3Pro-MITSample | C# | 22 | 13 MonoBehaviour | Same SDK v1.1.2 |
| frame-codebase | C/C++ | 33+1 cc | 4 experiment modules | 12 TFLM APIs |
| overpass-turbo | TypeScript | 37 | 5 key classes | Overpass REST API |
