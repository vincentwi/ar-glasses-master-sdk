# DEEP Wave 6 Documentation & Specifications
# Comprehensive API References, Function Lists, and Capability Descriptions
# Generated: 2026-04-20

================================================================================
## TABLE OF CONTENTS
================================================================================

1. XREAL SDK Documentation
2. OpenXR 1.1 Specification Reference
3. Monado XR Runtime — Documentation & Full Source Analysis
4. Snap OS 2.0 / Spectacles SDK
5. Qualcomm RayNeo X3 Pro AR Development
6. StardustXR Documentation
7. Monado Source Code Deep Analysis (from /tmp/glasses-sdk-repos/monado/)

================================================================================
## 1. XREAL SDK DOCUMENTATION
================================================================================

### Overview
XREAL SDK enables AR application development for XREAL glasses including
Air, Air 2, Air 2 Pro, Air 2 Ultra, and Light series.

### Supported Devices
- XREAL Air (USB-C tethered, 3DoF IMU)
- XREAL Air 2 (improved display, electrochromic dimming)
- XREAL Air 2 Pro (variable electrochromic dimming)
- XREAL Air 2 Ultra (6DoF with dual cameras, SLAM tracking)
- XREAL Light (6DoF, hand tracking, plane detection)

### SDK Architecture
- **NRSDK** (primary Unity SDK): Provides AR session management, spatial tracking,
  image tracking, plane detection, hand tracking, spatial anchors
- **Nebula**: Companion app for 3DoF screen projection mode
- **Android Native**: Direct HID access via USB for IMU data

### Core API Classes (Unity/NRSDK)
- NRSessionManager — Session lifecycle management
- NRHMDPoseTracker — Head pose tracking (3DoF/6DoF)
- NRInput — Controller and hand input
- NRFrame — Per-frame data access
- NRRenderer — Stereo rendering pipeline
- NRTrackableManager — Trackable objects (planes, images)
- NRWorldAnchor — Persistent spatial anchors
- NRGlassesInitErrorTip — Error handling

### Key Functions
- NRSessionManager.CreateSession()
- NRSessionManager.DestroySession()
- NRFrame.GetHeadPose()
- NRFrame.GetDeviceType()
- NRInput.GetControllerState()
- NRInput.GetHandState()
- NRRenderer.CreateStereoRenderer()
- NRTrackableManager.GetTrackables<NRTrackablePlane>()
- NRTrackableManager.GetTrackables<NRTrackableImage>()

### Display Specs
- Air 2 Ultra: 1920x1080 per eye, 46° FoV, OLED micro-display
- Refresh Rate: 60/72/90/120 Hz (device dependent)
- Color Depth: 8-bit per channel

### Tracking Capabilities
- IMU: Accelerometer + Gyroscope (all models)
- SLAM: Visual-Inertial Odometry (Air 2 Ultra, Light only)
- Hand Tracking: 21 joint skeleton per hand (Air 2 Ultra)
- Plane Detection: Horizontal/vertical planes (6DoF models)
- Image Tracking: Marker and natural feature tracking

### USB Protocol
- Vendor ID: 0x3318
- Product IDs: 0x0424 (Air), 0x0428 (Air 2), 0x0432 (Air 2 Pro),
  0x0426 (Air 2 Ultra)
- HID interface for IMU data at 1000Hz
- Display connected as USB-C DisplayPort Alt Mode

================================================================================
## 2. OPENXR 1.1 SPECIFICATION REFERENCE
================================================================================

### Overview
OpenXR is the Khronos Group open standard for XR (VR/AR/MR) application
development. Version 1.1 is the latest ratified specification.

### Core Architecture
- Instance → System → Session → Swapchain → Frame pipeline
- Action-based input system with interaction profiles
- Reference spaces for coordinate system management
- Extension mechanism for vendor-specific features

### Core Functions (Complete List)

#### Instance Lifecycle
- xrCreateInstance(const XrInstanceCreateInfo*, XrInstance*)
- xrDestroyInstance(XrInstance)
- xrGetInstanceProperties(XrInstance, XrInstanceProperties*)
- xrPollEvent(XrInstance, XrEventDataBuffer*)
- xrResultToString(XrInstance, XrResult, char[])
- xrStructureTypeToString(XrInstance, XrStructureType, char[])

#### System Discovery
- xrGetSystem(XrInstance, const XrSystemGetInfo*, XrSystemId*)
- xrGetSystemProperties(XrInstance, XrSystemId, XrSystemProperties*)

#### Session Management
- xrCreateSession(XrInstance, const XrSessionCreateInfo*, XrSession*)
- xrDestroySession(XrSession)
- xrBeginSession(XrSession, const XrSessionBeginInfo*)
- xrEndSession(XrSession)
- xrRequestExitSession(XrSession)

#### Reference Spaces
- xrEnumerateReferenceSpaces(XrSession, uint32_t, uint32_t*, XrReferenceSpaceType*)
- xrCreateReferenceSpace(XrSession, const XrReferenceSpaceCreateInfo*, XrSpace*)
- xrGetReferenceSpaceBoundsRect(XrSession, XrReferenceSpaceType, XrExtent2Df*)
- xrCreateActionSpace(XrSession, const XrActionSpaceCreateInfo*, XrSpace*)
- xrLocateSpace(XrSpace, XrSpace, XrTime, XrSpaceLocation*)
- xrLocateSpaces(XrSession, const XrSpacesLocateInfo*, XrSpaceLocations*)
- xrDestroySpace(XrSpace)

#### View Configuration
- xrEnumerateViewConfigurations(XrInstance, XrSystemId, uint32_t, uint32_t*, XrViewConfigurationType*)
- xrGetViewConfigurationProperties(XrInstance, XrSystemId, XrViewConfigurationType, XrViewConfigurationProperties*)
- xrEnumerateViewConfigurationViews(XrInstance, XrSystemId, XrViewConfigurationType, uint32_t, uint32_t*, XrViewConfigurationView*)
- xrLocateViews(XrSession, const XrViewLocateInfo*, XrViewState*, uint32_t, uint32_t*, XrView*)

#### Swapchain Management
- xrEnumerateSwapchainFormats(XrSession, uint32_t, uint32_t*, int64_t*)
- xrCreateSwapchain(XrSession, const XrSwapchainCreateInfo*, XrSwapchain*)
- xrDestroySwapchain(XrSwapchain)
- xrEnumerateSwapchainImages(XrSwapchain, uint32_t, uint32_t*, XrSwapchainImageBaseHeader*)
- xrAcquireSwapchainImage(XrSwapchain, const XrSwapchainImageAcquireInfo*, uint32_t*)
- xrWaitSwapchainImage(XrSwapchain, const XrSwapchainImageWaitInfo*)
- xrReleaseSwapchainImage(XrSwapchain, const XrSwapchainImageReleaseInfo*)

#### Frame Loop
- xrWaitFrame(XrSession, const XrFrameWaitInfo*, XrFrameState*)
- xrBeginFrame(XrSession, const XrFrameBeginInfo*)
- xrEndFrame(XrSession, const XrFrameEndInfo*)

#### Action System
- xrCreateActionSet(XrInstance, const XrActionSetCreateInfo*, XrActionSet*)
- xrDestroyActionSet(XrActionSet)
- xrCreateAction(XrActionSet, const XrActionCreateInfo*, XrAction*)
- xrDestroyAction(XrAction)
- xrSuggestInteractionProfileBindings(XrInstance, const XrInteractionProfileSuggestedBinding*)
- xrAttachSessionActionSets(XrSession, const XrSessionActionSetsAttachInfo*)
- xrGetCurrentInteractionProfile(XrSession, XrPath, XrInteractionProfile*)
- xrGetActionStateBoolean(XrSession, const XrActionStateGetInfo*, XrActionStateBoolean*)
- xrGetActionStateFloat(XrSession, const XrActionStateGetInfo*, XrActionStateFloat*)
- xrGetActionStateVector2f(XrSession, const XrActionStateGetInfo*, XrActionStateVector2f*)
- xrGetActionStatePose(XrSession, const XrActionStateGetInfo*, XrActionStatePose*)
- xrSyncActions(XrSession, const XrActionsSyncInfo*)
- xrEnumerateBoundSourcesForAction(XrSession, const XrBoundSourcesForActionEnumerateInfo*, uint32_t, uint32_t*, XrPath*)
- xrGetInputSourceLocalizedName(XrSession, const XrInputSourceLocalizedNameGetInfo*, uint32_t, uint32_t*, char*)

#### Haptic Output
- xrApplyHapticFeedback(XrSession, const XrHapticActionInfo*, const XrHapticBaseHeader*)
- xrStopHapticFeedback(XrSession, const XrHapticActionInfo*)

#### Path System
- xrStringToPath(XrInstance, const char*, XrPath*)
- xrPathToString(XrInstance, XrPath, uint32_t, uint32_t*, char*)

### Key OpenXR 1.1 Additions
- XR_VERSION_1_1 formally ratified
- xrLocateSpaces — batch space location queries
- Improved interaction profile system
- Better error reporting

### Reference Space Types
- VIEW — Head-locked
- LOCAL — Seated/standing origin, recenterable
- STAGE — Room-scale with boundaries
- LOCAL_FLOOR — Local space at floor level
- UNBOUNDED_MSFT — Large-area tracking

### Blend Modes
- XR_ENVIRONMENT_BLEND_MODE_OPAQUE (VR)
- XR_ENVIRONMENT_BLEND_MODE_ADDITIVE (AR optical see-through)
- XR_ENVIRONMENT_BLEND_MODE_ALPHA_BLEND (AR video see-through)

### Key Extensions for AR Glasses
- XR_EXT_hand_tracking — 26-joint hand skeleton
- XR_EXT_hand_interaction — Hand-based interaction profile
- XR_EXT_eye_gaze_interaction — Eye tracking input
- XR_FB_passthrough — Passthrough camera feed
- XR_FB_face_tracking2 — Facial expression tracking
- XR_FB_body_tracking — Full body tracking
- XR_MSFT_spatial_anchor — Persistent spatial anchors
- XR_EXT_plane_detection — Plane detection
- XR_KHR_visibility_mask — Visibility mask for rendering optimization
- XR_META_body_tracking_full_body — Full body with calibration

### Interaction Profiles (Standard)
- /interaction_profiles/khr/simple_controller
- /interaction_profiles/google/daydream_controller
- /interaction_profiles/htc/vive_controller
- /interaction_profiles/htc/vive_pro
- /interaction_profiles/microsoft/motion_controller
- /interaction_profiles/microsoft/xbox_controller
- /interaction_profiles/oculus/go_controller
- /interaction_profiles/oculus/touch_controller
- /interaction_profiles/valve/index_controller
- /interaction_profiles/ext/hand_interaction_ext
- /interaction_profiles/ext/eye_gaze_interaction

================================================================================
## 3. MONADO XR RUNTIME — DOCUMENTATION & SOURCE ANALYSIS
================================================================================

### Overview
Monado is the first open-source OpenXR runtime. It implements the OpenXR
specification and provides a modular architecture for XR device support.
Licensed under BSL-1.0. Developed by Collabora and NVIDIA.

### Architecture Layers
1. **State Trackers** — OpenXR API implementation (oxr_*), SteamVR driver
2. **IPC Layer** — Client/server process separation
3. **Compositor** — Vulkan-based compositor with distortion correction
4. **Auxiliary** — Utility libraries (math, tracking, vk helpers)
5. **Drivers** — Device-specific implementations
6. **Targets** — Build targets (service, CLI, GUI, libmonado)

### Source Tree Structure (from /tmp/glasses-sdk-repos/monado/src/xrt/)
```
include/xrt/      — Core interfaces (40 headers)
state_trackers/    — OpenXR state tracker, prober, SteamVR
compositor/        — Vulkan compositor, client wrappers
auxiliary/         — Math, tracking, Vulkan helpers, utilities
drivers/           — 38+ device drivers
targets/           — Build targets (service, CLI, GUI, libmonado)
tracking/          — Computer vision tracking (hand, constellation)
```

### ===== CORE INTERFACES (xrt_iface) =====

### struct xrt_instance (xrt_instance.h)
Root object for Monado. Singleton per process.

Methods (function pointers):
- is_system_available(xinst, *out_available) → xrt_result_t
- create_system(xinst, **out_xsys, **out_xsysd, **out_xso, **out_xsysc) → xrt_result_t
- get_prober(xinst, **out_xp) → xrt_result_t
- destroy(xinst) → void

Helper functions:
- xrt_instance_is_system_available()
- xrt_instance_create_system()
- xrt_instance_get_prober()
- xrt_instance_destroy()
- xrt_instance_create() — Factory, implemented per target

Data members:
- instance_info: struct xrt_instance_info
- startup_timestamp: int64_t (CLOCK_MONOTONIC)
- android_instance: struct xrt_instance_android*

### struct xrt_instance_info
- app_info: struct xrt_application_info
- platform_info: struct xrt_platform_info

### struct xrt_application_info
- application_name[128]
- ext_hand_tracking_enabled: bool
- ext_hand_tracking_data_source_enabled: bool
- ext_eye_gaze_interaction_enabled: bool
- ext_future_enabled: bool
- ext_hand_interaction_enabled: bool
- htc_facial_tracking_enabled: bool
- fb_body_tracking_enabled: bool
- fb_face_tracking2_enabled: bool
- meta_body_tracking_full_body_enabled: bool
- meta_body_tracking_calibration_enabled: bool
- android_face_tracking_enabled: bool

---

### struct xrt_system (xrt_system.h)
Collection of devices, policies, and compositor.

Methods:
- create_session(xsys, xsi, **out_xs, **out_xcn) → xrt_result_t
- destroy(xsys) → void

Data:
- properties: struct xrt_system_properties
  - vendor_id: uint32_t
  - name[256]: char
  - form_factor: enum xrt_form_factor

### struct xrt_system_devices
All devices known in the system.

Data:
- static_xdevs[XRT_SYSTEM_MAX_DEVICES]: struct xrt_device*
- static_xdev_count: size_t
- static_roles:
  - head: struct xrt_device*
  - eyes: struct xrt_device*
  - face: struct xrt_device*
  - body: struct xrt_device*
  - hand_tracking.unobstructed.left/right: struct xrt_device*
  - hand_tracking.conforming.left/right: struct xrt_device*

Methods:
- get_roles(xsysd, *out_roles) → xrt_result_t
- feature_inc(xsysd, type) → xrt_result_t
- feature_dec(xsysd, type) → xrt_result_t
- destroy(xsysd) → void

### struct xrt_system_roles
- generation_id: uint64_t
- left: int32_t (device index, -1 if none)
- right: int32_t
- gamepad: int32_t
- left_profile: enum xrt_device_name
- right_profile: enum xrt_device_name
- gamepad_profile: enum xrt_device_name

---

### struct xrt_device (xrt_device.h)
Central device interface — HMD or input device.

Data members:
- name: enum xrt_device_name
- device_type: enum xrt_device_type
- str[256]: char (device description)
- serial[256]: char (unique ID)
- hmd: struct xrt_hmd_parts* (null if not HMD)
- tracking_origin: struct xrt_tracking_origin*
- binding_profile_count: size_t
- binding_profiles: struct xrt_binding_profile*
- input_count: size_t
- inputs: struct xrt_input*
- output_count: size_t
- outputs: struct xrt_output*
- supported: struct xrt_device_supported

Methods (function pointers):
- update_inputs(xdev) → xrt_result_t
- get_tracked_pose(xdev, name, at_timestamp_ns, *out_relation) → xrt_result_t
- get_hand_tracking(xdev, name, desired_timestamp_ns, *out_value, *out_timestamp_ns) → xrt_result_t
- get_face_tracking(xdev, facial_expression_type, at_timestamp_ns, *out_value) → xrt_result_t
- get_face_calibration_state_android(xdev, *out_face_is_calibrated) → xrt_result_t
- get_body_skeleton(xdev, body_tracking_type, *out_value) → xrt_result_t
- get_body_joints(xdev, body_tracking_type, desired_timestamp_ns, *out_value) → xrt_result_t
- reset_body_tracking_calibration_meta(xdev) → xrt_result_t
- set_body_tracking_calibration_override_meta(xdev, new_body_height) → xrt_result_t
- set_output(xdev, name, *value) → xrt_result_t
- get_output_limits(xdev, *limits) → xrt_result_t
- get_presence(xdev, *presence) → xrt_result_t
- begin_plane_detection_ext(xdev, *begin_info, plane_detection_id, *out_id) → xrt_result_t
- destroy_plane_detection_ext(xdev, plane_detection_id) → xrt_result_t
- get_plane_detection_state_ext(xdev, plane_detection_id, *out_state) → xrt_result_t
- get_plane_detections_ext(xdev, plane_detection_id, *out_detections) → xrt_result_t
- get_view_poses(xdev, *default_eye_relation, at_timestamp_ns, view_type, view_count,
    *out_head_relation, *out_fovs, *out_poses) → xrt_result_t
- compute_distortion(xdev, view, u, v, *out_result) → xrt_result_t
- get_visibility_mask(xdev, type, view_index, **out_mask) → xrt_result_t
- ref_space_usage(xdev, type, name, used) → xrt_result_t
- is_form_factor_available(xdev, form_factor, *out_available) → xrt_result_t
- get_battery_status(xdev, *out_present, *out_charging, *out_charge) → xrt_result_t
- get_brightness(xdev, *out_brightness) → xrt_result_t
- set_brightness(xdev, brightness, relative) → xrt_result_t
- get_compositor_info(xdev, *mode, *out_info) → xrt_result_t
- begin_feature(xdev, type) → xrt_result_t
- end_feature(xdev, type) → xrt_result_t
- destroy(xdev) → void

### struct xrt_device_supported (capability flags)
- orientation_tracking: bool
- position_tracking: bool
- hand_tracking: bool
- eye_gaze: bool
- presence: bool
- force_feedback: bool
- ref_space_usage: bool
- form_factor_check: bool
- stage: bool
- face_tracking: bool
- face_tracking_calibration_state: bool
- body_tracking: bool
- body_tracking_calibration: bool
- battery_status: bool
- brightness_control: bool
- compositor_info: bool
- planes: bool
- plane_capability_flags: enum xrt_plane_detection_capability_flags_ext

### enum xrt_device_feature_type
- XRT_DEVICE_FEATURE_HAND_TRACKING_LEFT
- XRT_DEVICE_FEATURE_HAND_TRACKING_RIGHT
- XRT_DEVICE_FEATURE_EYE_TRACKING
- XRT_DEVICE_FEATURE_FACE_TRACKING

---

### struct xrt_hmd_parts
- screens[1]: { w_pixels, h_pixels, nominal_frame_interval_ns }
- views[XRT_MAX_VIEWS]: struct xrt_view
- view_count: size_t
- blend_modes[XRT_MAX_DEVICE_BLEND_MODES]: enum xrt_blend_mode
- blend_mode_count: size_t
- distortion: { models, preferred, mesh: { vertices, vertex_count, stride,
    uv_channels_count, indices, index_counts[], index_offsets[], index_count_total },
    fov[XRT_MAX_VIEWS] }

### struct xrt_view
- viewport: { x_pixels, y_pixels, w_pixels, h_pixels }
- display: { w_pixels, h_pixels }
- rot: struct xrt_matrix_2x2

---

### struct xrt_session (xrt_session.h)
XRT representation of XrSession.

Methods:
- poll_events(xs, *out_xse) → xrt_result_t
- request_exit(xs) → xrt_result_t
- destroy(xs) → void

### enum xrt_session_event_type
- XRT_SESSION_EVENT_NONE
- XRT_SESSION_EVENT_STATE_CHANGE
- XRT_SESSION_EVENT_OVERLAY_CHANGE
- XRT_SESSION_EVENT_LOSS_PENDING
- XRT_SESSION_EVENT_LOST
- XRT_SESSION_EVENT_DISPLAY_REFRESH_RATE_CHANGE
- XRT_SESSION_EVENT_REFERENCE_SPACE_CHANGE_PENDING
- XRT_SESSION_EVENT_PERFORMANCE_CHANGE
- XRT_SESSION_EVENT_PASSTHRU_STATE_CHANGE
- XRT_SESSION_EVENT_VISIBILITY_MASK_CHANGE
- XRT_SESSION_EVENT_USER_PRESENCE_CHANGE
- XRT_SESSION_EVENT_REQUEST_EXIT

### Session Event Structs
- xrt_session_event_state_change: { type, visible, focused, timestamp_ns }
- xrt_session_event_overlay: { type, primary_focused }
- xrt_session_event_loss_pending: { type, loss_time_ns }
- xrt_session_event_display_refresh_rate_change: { type, from_hz, to_hz }
- xrt_session_event_reference_space_change_pending: { event_type, ref_type, timestamp_ns, pose, pose_valid }
- xrt_session_event_perf_change: { type, domain, sub_domain, from_level, to_level }
- xrt_session_event_passthrough_state_change: { type, state }
- xrt_session_event_visibility_mask_change: { type, view_index }
- xrt_session_event_user_presence_change: { type, is_user_present }

---

### struct xrt_space_overseer (xrt_space.h)
Manages all spaces in the XR system.

Semantic spaces:
- root: always available
- view: head-tracking space
- local: recenterable local space
- local_floor: floor-level local
- stage: room-scale space
- unbounded: SLAM-based unbounded

Methods:
- create_offset_space(xso, parent, *offset, **out_space) → xrt_result_t
- create_pose_space(xso, xdev, name, **out_space) → xrt_result_t
- locate_space(xso, base_space, *base_offset, at_ns, space, *offset, *out_rel) → xrt_result_t
- locate_spaces(xso, base_space, *base_offset, at_ns, **spaces, count, *offsets, *out_rels) → xrt_result_t
- locate_device(xso, base_space, *base_offset, at_ns, xdev, *out_rel) → xrt_result_t
- ref_space_inc(xso, type) → xrt_result_t
- ref_space_dec(xso, type) → xrt_result_t
- recenter_local_spaces(xso) → xrt_result_t
- get_tracking_origin_offset(xso, xto, *out_offset) → xrt_result_t
- set_tracking_origin_offset(xso, xto, *offset) → xrt_result_t
- get_reference_space_offset(xso, type, *out_offset) → xrt_result_t
- set_reference_space_offset(xso, type, *offset) → xrt_result_t
- create_local_space(xso, **out_local, **out_local_floor) → xrt_result_t
- add_device(xso, xdev) → xrt_result_t
- attach_device(xso, xdev, space) → xrt_result_t
- destroy(xso) → void

---

### struct xrt_compositor (xrt_compositor.h)
Graphics compositor interface.

Layer types (enum xrt_layer_type):
- XRT_LAYER_PROJECTION
- XRT_LAYER_PROJECTION_DEPTH
- XRT_LAYER_QUAD
- XRT_LAYER_CUBE
- XRT_LAYER_CYLINDER
- XRT_LAYER_EQUIRECT1
- XRT_LAYER_EQUIRECT2
- XRT_LAYER_PASSTHROUGH

Swapchain interface (struct xrt_swapchain):
- acquire_image(xsc, *out_index) → xrt_result_t
- inc_image_use(xsc, index) → xrt_result_t
- dec_image_use(xsc, index) → xrt_result_t
- wait_image(xsc, timeout_ns, index) → xrt_result_t
- barrier_image(xsc, direction, index) → xrt_result_t
- release_image(xsc, index) → xrt_result_t

Compositor fence (struct xrt_compositor_fence):
- wait(xcf, timeout) → xrt_result_t
- destroy(xcf) → void

Compositor semaphore (struct xrt_compositor_semaphore):
- wait(xcsem, value, timeout_ns) → xrt_result_t
- destroy(xcsem) → void

Layer composition flags:
- CORRECT_CHROMATIC_ABERRATION_BIT
- BLEND_TEXTURE_SOURCE_ALPHA_BIT
- UNPREMULTIPLIED_ALPHA_BIT
- VIEW_SPACE_BIT
- COLOR_BIAS_SCALE
- NORMAL_SUPER_SAMPLING_BIT_FB
- QUALITY_SUPER_SAMPLING_BIT_FB
- NORMAL_SHARPENING_BIT_FB
- QUALITY_SHARPENING_BIT_FB
- ADVANCED_BLENDING_BIT
- DEPTH_TEST

---

### struct xrt_prober (xrt_prober.h)
Device discovery and enumeration.

Methods:
- probe(xp) → xrt_result_t
- lock_list(xp, ***out_devices, *out_count) → xrt_result_t
- unlock_list(xp, ***devices) → xrt_result_t
- dump(xp, use_stdout) → int
- create_system(xp, *broadcast, **out_xsysd, **out_xso) → xrt_result_t
- select(xp, **xdevs, capacity) → int
- open_hid_interface(xp, *xpdev, iface, **out_hid) → int
- open_serial_device(xp, *xpdev, *params, **out_serial) → int
- open_video_device(xp, *xpdev, *xfctx, **out_xfs) → int
- list_video_devices(xp, cb, *ptr) → int
- get_builders(xp, *out_builder_count, ***out_builders, ...) → int
- get_string_descriptor(xp, *xpdev, which, *out_buf, max_len) → int
- can_open(xp, *xpdev) → bool
- destroy(xp_ptr) → void

---

### struct xrt_tracking_origin (xrt_tracking.h)
Tracking system origin.

- name[256]: char
- type: enum xrt_tracking_type
- initial_offset: struct xrt_pose

### enum xrt_tracking_type
- XRT_TRACKING_TYPE_NONE
- XRT_TRACKING_TYPE_RGB
- XRT_TRACKING_TYPE_LIGHTHOUSE
- XRT_TRACKING_TYPE_MAGNETIC
- XRT_TRACKING_TYPE_EXTERNAL_SLAM
- XRT_TRACKING_TYPE_OTHER
- XRT_TRACKING_TYPE_ATTACHABLE

### Tracking Sinks
- struct xrt_imu_sink: push_imu(sink, *sample)
- struct xrt_pose_sink: push_pose(sink, *sample)
- struct xrt_hand_masks_sink: push_hand_masks(sink, *hand_masks)
- struct xrt_slam_sinks: { cam_count, cams[5], imu, gt, hand_masks }

### Tracked device types
- struct xrt_tracked_psmv: push_imu, get_tracked_pose, destroy
- struct xrt_tracked_psvr: push_imu, get_tracked_pose, destroy
- struct xrt_tracked_slam: get_tracked_pose

---

### Frame Pipeline (xrt_frame.h, xrt_frameserver.h)

### struct xrt_frame
- width, height, stride, size: dimensions
- data: uint8_t* (pixel data)
- format: enum xrt_format
- stereo_format: enum xrt_stereo_format
- timestamp, source_timestamp: int64_t
- source_sequence, source_id: uint64_t

### struct xrt_frame_sink
- push_frame(sink, *frame) → void

### struct xrt_fs (Frameserver)
- name[512], product[32], manufacturer[32], serial[32]
- source_id: uint64_t
- enumerate_modes(xfs, **out_modes, *out_count) → bool
- configure_capture(xfs, *cp) → bool
- stream_start(xfs, *xs, capture_type, descriptor_index) → bool
- slam_stream_start(xfs, *sinks) → bool
- stream_stop(xfs) → bool
- is_running(xfs) → bool

---

### enum xrt_device_name (Supported Devices — 50+ entries)
XRT_DEVICE_INVALID, XRT_DEVICE_GENERIC_HMD,
XRT_DEVICE_VIVE_PRO, XRT_DEVICE_VIVE_WAND, XRT_DEVICE_VIVE_TRACKER,
XRT_DEVICE_VIVE_TRACKER_GEN1/GEN2/GEN3/TUNDRA,
XRT_DEVICE_SIMPLE_CONTROLLER, XRT_DEVICE_DAYDREAM,
XRT_DEVICE_WMR_CONTROLLER, XRT_DEVICE_XBOX_CONTROLLER,
XRT_DEVICE_GO_CONTROLLER, XRT_DEVICE_TOUCH_CONTROLLER,
XRT_DEVICE_INDEX_CONTROLLER, XRT_DEVICE_HP_REVERB_G2_CONTROLLER,
XRT_DEVICE_SAMSUNG_ODYSSEY_CONTROLLER, XRT_DEVICE_LOGITECH_MX_INK_CONTROLLER,
XRT_DEVICE_ML2_CONTROLLER, XRT_DEVICE_OPPO_MR_CONTROLLER,
XRT_DEVICE_HAND_INTERACTION, XRT_DEVICE_EYE_GAZE_INTERACTION,
XRT_DEVICE_PSMV, XRT_DEVICE_PSSENSE, XRT_DEVICE_HYDRA,
XRT_DEVICE_RIFT_REMOTE, XRT_DEVICE_BLUBUR_S1, XRT_DEVICE_PSVR2,
XRT_DEVICE_FLIPVR, XRT_DEVICE_CONTACTGLOVE2,
XRT_DEVICE_HAND_TRACKER, XRT_DEVICE_REALSENSE, XRT_DEVICE_DEPTHAI,
XRT_DEVICE_EXT_HAND_INTERACTION, XRT_DEVICE_ANDROID_FACE_TRACKING,
XRT_DEVICE_HTC_FACE_TRACKING, XRT_DEVICE_FB_BODY_TRACKING,
XRT_DEVICE_FB_FACE_TRACKING2, XRT_DEVICE_PICO_NEO3_CONTROLLER,
XRT_DEVICE_PICO4_CONTROLLER, XRT_DEVICE_PICO_G3_CONTROLLER,
XRT_DEVICE_VIVE_COSMOS_CONTROLLER, XRT_DEVICE_VIVE_FOCUS3_CONTROLLER,
XRT_DEVICE_TOUCH_PRO_CONTROLLER, XRT_DEVICE_TOUCH_PLUS_CONTROLLER,
XRT_DEVICE_TOUCH_CONTROLLER_RIFT_CV1, XRT_DEVICE_TOUCH_CONTROLLER_QUEST_1_RIFT_S,
XRT_DEVICE_TOUCH_CONTROLLER_QUEST_2

### enum xrt_blend_mode
- XRT_BLEND_MODE_OPAQUE = 1
- XRT_BLEND_MODE_ADDITIVE = 2
- XRT_BLEND_MODE_ALPHA_BLEND = 3

### enum xrt_format (Image Formats)
XRT_FORMAT_R8G8B8X8, R8G8B8A8, R8G8B8, R8G8, R8, BAYER_GR8, ...

---

### xrt_result_t (Error Codes — Complete)
XRT_SUCCESS = 0
XRT_TIMEOUT = 2
XRT_SPACE_BOUNDS_UNAVAILABLE = 3
XRT_OPERATION_CANCELLED = 4
XRT_ERROR_IPC_FAILURE = -1
XRT_ERROR_NO_IMAGE_AVAILABLE = -2
XRT_ERROR_VULKAN = -3
XRT_ERROR_OPENGL = -4
XRT_ERROR_FAILED_TO_SUBMIT_VULKAN_COMMANDS = -5
XRT_ERROR_SWAPCHAIN_FLAG_VALID_BUT_UNSUPPORTED = -6
XRT_ERROR_ALLOCATION = -7
XRT_ERROR_POSE_NOT_ACTIVE = -8
XRT_ERROR_FENCE_CREATE_FAILED = -9
XRT_ERROR_NATIVE_HANDLE_FENCE_ERROR = -10
XRT_ERROR_MULTI_SESSION_NOT_IMPLEMENTED = -11
XRT_ERROR_SWAPCHAIN_FORMAT_UNSUPPORTED = -12
XRT_ERROR_EGL_CONFIG_MISSING = -13
XRT_ERROR_THREADING_INIT_FAILURE = -14
XRT_ERROR_IPC_SESSION_NOT_CREATED = -15
XRT_ERROR_IPC_SESSION_ALREADY_CREATED = -16
XRT_ERROR_PROBER_NOT_SUPPORTED = -17
XRT_ERROR_PROBER_CREATION_FAILED = -18
XRT_ERROR_PROBER_LIST_LOCKED = -19
XRT_ERROR_PROBER_LIST_NOT_LOCKED = -20
XRT_ERROR_PROBING_FAILED = -21
XRT_ERROR_DEVICE_CREATION_FAILED = -22
XRT_ERROR_D3D = -23
XRT_ERROR_D3D11 = -24
XRT_ERROR_D3D12 = -25
XRT_ERROR_RECENTERING_NOT_SUPPORTED = -26
XRT_ERROR_COMPOSITOR_NOT_SUPPORTED = -27
XRT_ERROR_IPC_COMPOSITOR_NOT_CREATED = -28
XRT_ERROR_NOT_IMPLEMENTED = -29
XRT_ERROR_UNSUPPORTED_SPACE_TYPE = -30
XRT_ERROR_ANDROID = -31
XRT_ERROR_FEATURE_NOT_SUPPORTED = -32
XRT_ERROR_INPUT_UNSUPPORTED = -33
XRT_ERROR_OUTPUT_UNSUPPORTED = -34
XRT_ERROR_OUTPUT_REQUEST_FAILURE = -35
XRT_ERROR_SYNC_PRIMITIVE_CREATION_FAILED = -36
XRT_ERROR_IPC_SERVICE_ALREADY_RUNNING = -37
XRT_ERROR_IPC_MAINLOOP_FAILED_TO_INIT = -38
XRT_ERROR_INVALID_ARGUMENT = -39
XRT_ERROR_FUTURE_RESULT_NOT_READY = -40
XRT_ERROR_FUTURE_ALREADY_COMPLETE = -41
XRT_ERROR_DEVICE_NOT_ATTACHABLE = -42
XRT_ERROR_UNCAUGHT_EXCEPTION = -43
XRT_ERROR_UNSUPPORTED_VIEW_TYPE = -44

---

### MONADO DRIVERS (38 drivers found in src/xrt/drivers/)

| Driver | Interface Header | Description |
|--------|-----------------|-------------|
| xreal_air | xreal_air_interface.h | XREAL Air/Air2/Air2Pro/Air2Ultra |
| wmr | wmr_interface.h | Windows Mixed Reality |
| survive | survive_interface.h | Valve Lighthouse (libsurvive) |
| steamvr_lh | steamvr_lh_interface.h | SteamVR Lighthouse |
| rift_s | rift_s_interface.h | Oculus Rift S |
| rift | rift_interface.h | Oculus Rift CV1 |
| rift_sensor | rift_sensor_interface.h | Rift Constellation cameras |
| psvr | psvr_interface.h | PlayStation VR |
| psvr2 | psvr2_interface.h | PlayStation VR2 |
| psmv | psmv_interface.h | PlayStation Move |
| pssense | pssense_interface.h | PS5 DualSense |
| hydra | hydra_interface.h | Razer Hydra |
| hdk | hdk_interface.h | OSVR HDK |
| ohmd | oh_interface.h | OpenHMD bridge |
| realsense | rs_interface.h | Intel RealSense |
| depthai | depthai_interface.h | Luxonis DepthAI |
| remote | r_interface.h | Remote debugging |
| simulated | simulated_interface.h | Simulated HMD |
| sample | sample_interface.h | Sample/template driver |
| qwerty | qwerty_interface.h | Keyboard-driven testing |
| north_star | ns_interface.h | Leap Motion North Star |
| euroc | euroc_interface.h | EuRoC dataset player |
| vf | vf_interface.h | Video file source |
| v4l2 | v4l2_interface.h | V4L2 camera |
| uvc | uvc_interface.h | USB Video Class |
| ultraleap_v2 | ulv2_interface.h | Leap Motion v2 |
| ultraleap_v5 | ulv5_interface.h | Leap Motion v5 |
| opengloves | opengloves_interface.h | OpenGloves |
| ht | ht_interface.h | Hand tracking |
| ht_ctrl_emu | ht_ctrl_emu_interface.h | Hand-to-controller emulation |
| daydream | daydream_interface.h | Google Daydream |
| arduino | arduino_interface.h | Arduino sensor |
| illixr | illixr_interface.h | ILLIXR integration |
| rokid | rokid_interface.h | Rokid glasses |
| simula | svr_interface.h | SimulaVR |
| solarxr | solarxr_interface.h | SlimeVR/SolarXR |
| twrap | twrap_interface.h | Tracking wrapper |
| blubur_s1 | blubur_s1_interface.h | Blubur S1 |

### XREAL Air Driver Details (xreal_air_interface.h)
- XREAL_AIR_VID = 0x3318
- XREAL_AIR_PID = 0x0424
- XREAL_AIR_2_PID = 0x0428
- XREAL_AIR_2_PRO_PID = 0x0432
- XREAL_AIR_2_ULTRA_PID = 0x0426
- Factory: xreal_air_builder_create() → struct xrt_builder*

---

### libmonado API (monado.h) — v1.7.0

Control interface for managing Monado service externally.

#### Functions
- mnd_api_get_version(*major, *minor, *patch)
- mnd_root_create(**out_root) → mnd_result_t
- mnd_root_destroy(**root_ptr)
- mnd_root_update_client_list(root) → mnd_result_t
- mnd_root_get_number_clients(root, *out_num) → mnd_result_t
- mnd_root_get_client_id_at_index(root, index, *out_id) → mnd_result_t
- mnd_root_get_client_name(root, client_id, **out_name) → mnd_result_t
- mnd_root_get_client_state(root, client_id, *out_flags) → mnd_result_t
- mnd_root_set_client_primary(root, client_id) → mnd_result_t
- mnd_root_set_client_focused(root, client_id) → mnd_result_t
- mnd_root_toggle_client_io_active(root, client_id) → mnd_result_t [DEPRECATED]
- mnd_root_set_client_io_blocks(root, client_id, block_flags) → mnd_result_t
- mnd_root_get_device_count(root, *out_count) → mnd_result_t
- mnd_root_get_device_info_bool(root, idx, prop, *out) → mnd_result_t
- mnd_root_get_device_info_i32(root, idx, prop, *out) → mnd_result_t
- mnd_root_get_device_info_u32(root, idx, prop, *out) → mnd_result_t
- mnd_root_get_device_info_float(root, idx, prop, *out) → mnd_result_t
- mnd_root_get_device_info_string(root, idx, prop, **out) → mnd_result_t
- mnd_root_get_device_info(root, idx, *out_id, **out_name) → mnd_result_t [DEPRECATED]
- mnd_root_get_device_from_role(root, role_name, *out_index) → mnd_result_t
- mnd_root_recenter_local_spaces(root) → mnd_result_t
- mnd_root_get_reference_space_offset(root, type, *out_offset) → mnd_result_t
- mnd_root_set_reference_space_offset(root, type, *offset) → mnd_result_t
- mnd_root_get_tracking_origin_offset(root, origin_idx, *out_offset) → mnd_result_t
- mnd_root_set_tracking_origin_offset(root, origin_idx, *offset) → mnd_result_t
- mnd_root_get_tracking_origin_count(root, *out_count) → mnd_result_t
- mnd_root_get_tracking_origin_name(root, origin_idx, **out_string) → mnd_result_t
- mnd_root_get_device_battery_status(root, idx, *present, *charging, *charge) → mnd_result_t
- mnd_root_get_device_brightness(root, idx, *out_brightness) → mnd_result_t
- mnd_root_set_device_brightness(root, idx, brightness, relative) → mnd_result_t

#### Role Names for mnd_root_get_device_from_role
- "head", "left", "right", "gamepad", "eyes"
- "hand-tracking-unobstructed-left", "hand-tracking-unobstructed-right"
- "hand-tracking-conforming-left", "hand-tracking-conforming-right"

================================================================================
## 4. SNAP OS 2.0 / SPECTACLES SDK
================================================================================

### Overview
Snap OS 2.0 is the operating system for Snap's 5th generation Spectacles
AR glasses. It is a standalone AR computing platform.

### Hardware Specs
- Qualcomm Snapdragon AR2 Gen 1 processor
- 4 environment cameras for spatial tracking
- Two LCoS waveguide displays, ~26.3° diagonal FoV
- 45-minute battery life
- Wi-Fi 6E, Bluetooth 5.3
- 6DoF inside-out tracking
- Hand tracking (skeleton-based)
- Voice input via dual microphones

### Development Platform
- **Lens Studio** — Primary development IDE (desktop)
- **SnapOS Extensions** — Native API extensions
- **SpectaclesInteractionKit** — Interaction framework

### Key APIs & Capabilities
- **Spatial Understanding**: Plane detection, mesh reconstruction
- **Hand Tracking**: Full skeleton tracking, pinch gestures, hand rays
- **World Mesh**: Real-time environment mesh
- **Spatial Anchors**: Persistent anchors for content placement
- **Connected Lenses**: Multi-user shared AR experiences
- **Snap ML**: On-device ML model execution
- **Location Service**: GPS + visual positioning
- **Voice Commands**: Wake word + speech recognition

### Lens Studio API Surface
- ScriptComponent — Script lifecycle
- Transform — 3D transform manipulation
- Camera — Camera access
- MeshBuilder — Procedural mesh creation
- MaterialMeshVisual — Rendering
- HandTracking — Hand input
- DeviceTracking — Head pose
- WorldTracking — Environmental understanding
- PersistentStorage — Data persistence
- RemoteServiceModule — Network communication

### Interaction Kit Components
- HandInteractor — Pinch, grab, poke interactions
- ContainerFrame — UI container
- ScrollView — Scrollable content
- ToggleButton / Slider — UI elements
- InteractableManipulation — Object manipulation

### Display Modes
- Immersive — Full AR overlay
- Snap — Quick glanceable info
- Home — Launcher/OS UI

================================================================================
## 5. QUALCOMM RAYNEO X3 PRO AR DEVELOPMENT
================================================================================

### Overview
RayNeo X3 Pro is an AR glasses platform powered by Qualcomm Snapdragon
AR1 Gen1 chipset. Features binocular full-color waveguide displays.

### Hardware Specifications
- Qualcomm Snapdragon AR1 Gen1
- Binocular waveguide display (micro-OLED + diffractive waveguide)
- 1920x1080 per eye, up to 120Hz
- 6DoF tracking (V-SLAM with IMU fusion)
- Dual RGB cameras + IR camera
- Hand tracking support
- Microphone array + speakers
- Wi-Fi 6 + Bluetooth 5.2
- USB-C for power/data
- Android-based OS

### Development Options
1. **Qualcomm Spaces SDK** — OpenXR-based development
   - Full OpenXR 1.0 conformance
   - Hand tracking extension
   - Plane detection
   - Spatial anchors
   - Hit testing
   - Image tracking

2. **RayNeo SDK** — Native Android SDK
   - Display management
   - Sensor data access
   - Camera streaming
   - Custom rendering pipeline

3. **Unity/Unreal** — Via Qualcomm Spaces plugin

### Qualcomm Spaces Key APIs
- SpatialAnchorsFeature — Create/load/save spatial anchors
- PlaneDetectionFeature — Detect horizontal/vertical planes
- HandTrackingFeature — 26-joint hand tracking
- ImageTrackingFeature — Track reference images
- HitTestingFeature — Ray-surface intersection
- CameraAccessFeature — RGB camera frame access
- QrCodeTrackingFeature — QR code detection

### Supported OpenXR Extensions
- XR_MSFT_spatial_anchor
- XR_EXT_hand_tracking
- XR_QCOM_tracking_optimization_settings
- XR_FB_passthrough (video see-through on supported models)
- XR_EXT_plane_detection

================================================================================
## 6. STARDUSTXR DOCUMENTATION
================================================================================

### Overview
StardustXR is a modular 3D UI server protocol for Linux XR. It provides a
Wayland-like protocol for spatial computing, allowing multiple applications
to share a 3D space.

### Architecture
- **Stardust Server** — Central 3D compositor (runs on Monado or other OpenXR runtime)
- **Stardust Clients** — Applications that connect to the server
- **Flatland** — 2D panel client for running existing desktop apps in 3D
- **Gravity** — Physics-based interaction system
- **Magnetar** — Default hand interaction handler
- **Protostar** — Application launcher

### Protocol
- Based on **Flexbuffers** over Unix sockets
- Node-based scene graph
- Each client gets a namespace in the scene graph
- Server manages spatial relationships

### Core Concepts
- **Spatial**: Base 3D object with position/rotation/scale
- **Zone**: Capture volume for interaction
- **Field**: Spatial distance field for interaction detection
- **PulseReceiver/PulseSender**: Event messaging system
- **Item/ItemAcceptor**: Data transfer between clients

### Development Setup
1. Install Monado (OpenXR runtime)
2. Install StardustXR server (stardust-xr-server)
3. Set XR_RUNTIME_JSON to Monado's manifest
4. Run server, then connect clients

### Client Libraries
- **stardust-xr-fusion** (Rust) — Primary client library
- **libstardustxr** (C) — Low-level protocol library

### Fusion API (Rust)
Key types:
- client::Client — Connection to server
- node::NodeType — Base trait for all nodes
- spatial::Spatial — 3D positioned object
- drawable::Model — 3D model loading (glTF)
- drawable::Lines — Line rendering
- drawable::Text — 3D text rendering
- input::InputHandler — Input event handling
- input::InputMethod — Input source (hand/pointer)
- fields::BoxField / SphereField / CylinderField — Interaction volumes
- items::panel::PanelItem — 2D panel embedding

### Fusion Client Lifecycle
```rust
let (client, event_loop) = Client::connect_with_async_loop().await?;
let root = client.get_root();
// Create spatial nodes, register input handlers, etc.
// event_loop processes messages
```

### Key Functions (Rust Fusion)
- Client::connect_with_async_loop() — Connect to server
- Spatial::create(client, parent, transform) — Create spatial node
- Model::create(client, parent, transform, model_path) — Load 3D model
- InputHandler::create(client, parent, transform, field) — Register input
- BoxField::create(client, parent, transform, size) — Create box field
- PanelItem::create(client, parent, transform, size) — Create 2D panel

================================================================================
## 7. MONADO SOURCE CODE DEEP ANALYSIS
================================================================================

### Repository Stats
- Path: /tmp/glasses-sdk-repos/monado/
- Size: ~35MB
- Core headers in src/xrt/include/xrt/: 40 files
- Total struct xrt_* definitions: 219+ across all headers
- Driver count: 38 device drivers

### Complete Header File List (src/xrt/include/xrt/)
xrt_android.h, xrt_byte_order.h, xrt_compiler.h, xrt_compositor.h,
xrt_config.h, xrt_config_arch.h, xrt_config_os.h, xrt_defines.h,
xrt_device.h, xrt_documentation.h, xrt_frame.h, xrt_frameserver.h,
xrt_future.h, xrt_future_value.h, xrt_gfx_d3d11.h, xrt_gfx_d3d12.h,
xrt_gfx_egl.h, xrt_gfx_gl.h, xrt_gfx_gles.h, xrt_gfx_vk.h,
xrt_gfx_win32.h, xrt_gfx_xlib.h, xrt_handles.h, xrt_instance.h,
xrt_limits.h, xrt_macro_lists.h, xrt_openxr_includes.h,
xrt_plane_detector.h, xrt_prober.h, xrt_results.h, xrt_session.h,
xrt_settings.h, xrt_space.h, xrt_system.h, xrt_tracking.h,
xrt_visibility_mask.h, xrt_vulkan_includes.h, xrt_windows.h

### Graphics Backend Support
- Vulkan (primary): xrt_gfx_vk.h
- OpenGL: xrt_gfx_gl.h
- OpenGL ES: xrt_gfx_gles.h
- EGL: xrt_gfx_egl.h
- Direct3D 11: xrt_gfx_d3d11.h
- Direct3D 12: xrt_gfx_d3d12.h
- X11/Xlib: xrt_gfx_xlib.h
- Win32: xrt_gfx_win32.h

### Key Struct Summary (All xrt_* from headers)

#### Core Objects
- xrt_instance, xrt_system, xrt_session
- xrt_device, xrt_hmd_parts, xrt_view
- xrt_system_devices, xrt_system_roles
- xrt_space, xrt_space_overseer

#### Compositor
- xrt_compositor, xrt_compositor_native, xrt_compositor_fence
- xrt_compositor_semaphore, xrt_swapchain
- xrt_layer_data, xrt_layer_frame_data
- xrt_layer_projection_data, xrt_layer_projection_depth_data
- xrt_layer_quad_data, xrt_layer_cube_data
- xrt_layer_cylinder_data, xrt_layer_equirect1_data
- xrt_layer_equirect2_data, xrt_layer_passthrough_data
- xrt_sub_image, xrt_passthrough, xrt_passthrough_layer

#### Input/Output
- xrt_input, xrt_output, xrt_input_value (union)
- xrt_binding_profile, xrt_binding_input_pair, xrt_binding_output_pair
- xrt_output_value, xrt_output_limits

#### Tracking
- xrt_tracking_origin, xrt_tracking_factory
- xrt_tracked_psmv, xrt_tracked_psvr, xrt_tracked_slam
- xrt_imu_sink, xrt_pose_sink, xrt_hand_masks_sink
- xrt_slam_sinks, xrt_tracking_sample, xrt_imu_sample
- xrt_pose_sample, xrt_hand_masks_sample

#### Frames
- xrt_frame, xrt_frame_sink, xrt_frame_node, xrt_frame_context
- xrt_fs (frameserver), xrt_fs_mode, xrt_fs_capture_parameters

#### Math/Geometry
- xrt_vec2, xrt_vec3, xrt_vec3_f64
- xrt_pose, xrt_fov, xrt_quat
- xrt_matrix_2x2, xrt_matrix_3x3, xrt_matrix_4x4
- xrt_space_relation (pose + velocity + angular_velocity)
- xrt_rect, xrt_normalized_rect, xrt_rect_f32
- xrt_colour_rgb_f32, xrt_colour_rgba_f32, xrt_colour_hsv_f32
- xrt_uuid, xrt_luid, xrt_limited_unique_id, xrt_reference

#### Prober
- xrt_prober, xrt_prober_device, xrt_prober_entry
- xrt_auto_prober, xrt_builder

#### Hand/Body/Face Tracking
- xrt_hand_joint_set, xrt_facial_expression_set
- xrt_body_skeleton, xrt_body_joint_set

#### Plane Detection
- xrt_plane_detector_begin_info_ext
- xrt_plane_detections_ext

#### Device Info
- xrt_device_compositor_info, xrt_device_compositor_mode
- xrt_device_supported, xrt_system_properties
- xrt_application_info, xrt_instance_info, xrt_platform_info

### Passthrough Support
- enum xrt_passthrough_create_flags:
  XRT_PASSTHROUGH_IS_RUNNING_AT_CREATION, XRT_PASSTHROUGH_LAYER_DEPTH
- enum xrt_passthrough_state:
  REINIT_REQUIRED, NON_RECOVERABLE_ERROR, RECOVERABLE_ERROR, RESTORED_ERROR
- enum xrt_passthrough_purpose_flags:
  RECONSTRUCTION, PROJECTED, TRACKED_KEYBOARD_HANDS, TRACKED_KEYBOARD_MASKED_HANDS

### Distortion Models
- XRT_DISTORTION_MODEL_NONE
- XRT_DISTORTION_MODEL_COMPUTE
- XRT_DISTORTION_MODEL_MESHUV

### OpenXR State Tracker (oxr_*)
Located in src/xrt/state_trackers/oxr/:
- oxr_objects.h — Main OpenXR object definitions
- oxr_api_funcs.h — OpenXR API function declarations
- oxr_logger.h — Logging infrastructure
- oxr_conversions.h — Type conversions
- oxr_chain.h — Extension chain handling
- oxr_handle.h — Handle management
- oxr_two_call.h — Two-call idiom helpers
- oxr_frame_sync.h — Frame synchronization
- oxr_hand_tracking.h — Hand tracking state
- oxr_roles.h — Device role management
- oxr_pretty_print.h — Debug printing
- oxr_swapchain_common.h — Swapchain helpers
- oxr_api_verify.h — API parameter validation

================================================================================
## CROSS-REFERENCE: CAPABILITY MATRIX
================================================================================

| Capability           | OpenXR | Monado | XREAL SDK | Snap OS | RayNeo | StardustXR |
|---------------------|--------|--------|-----------|---------|--------|------------|
| 6DoF Head Tracking  | Yes    | Yes    | Ultra/Light| Yes    | Yes    | Via runtime|
| 3DoF Head Tracking  | Yes    | Yes    | All       | N/A     | N/A    | Via runtime|
| Hand Tracking       | Ext    | Yes    | Ultra     | Yes     | Yes    | Via runtime|
| Eye Tracking        | Ext    | Yes    | No        | No      | No     | Via runtime|
| Plane Detection     | Ext    | Yes    | Light     | Yes     | Yes    | No         |
| Spatial Anchors     | Ext    | Partial| Light     | Yes     | Yes    | No         |
| Passthrough         | Ext    | Yes    | N/A(AR)   | N/A(AR) | N/A    | No         |
| Body Tracking       | Ext    | Yes    | No        | No      | No     | No         |
| Face Tracking       | Ext    | Yes    | No        | No      | No     | No         |
| Multi-user          | No     | No     | No        | Yes     | No     | Partial    |
| Vulkan Compositor   | Yes    | Yes    | No        | N/A     | No     | Via runtime|
| OpenGL Support      | Yes    | Yes    | Yes       | N/A     | Yes    | Via runtime|
| IPC/Multi-process   | Impl   | Yes    | No        | Yes     | No     | Yes        |
| Linux Support       | Yes    | Yes    | No        | No      | No     | Yes        |
| Android Support     | Yes    | Yes    | Yes       | No      | Yes    | No         |

================================================================================
## END OF DOCUMENT
================================================================================
