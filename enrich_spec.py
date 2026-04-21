#!/usr/bin/env python3
"""
Enrich OpenAPI spec with documentation from deep-read files.
Reads all 18 deep-read files, matches functions to paths, and enriches descriptions.
"""

import yaml
import os
import re
import glob
from collections import defaultdict

# ============================================================
# 1. Load the existing spec
# ============================================================
with open('/tmp/ar-glasses-old/openapi.yaml', 'r') as f:
    spec = yaml.safe_load(f)

# ============================================================
# 2. Load all deep-read files
# ============================================================
deep_read_dir = '/tmp/ar-glasses-old/docs/deep-reads'
deep_reads = {}
all_deep_text = ""
for md_file in sorted(glob.glob(os.path.join(deep_read_dir, '*.md'))):
    basename = os.path.basename(md_file)
    with open(md_file, 'r') as f:
        content = f.read()
    deep_reads[basename] = content
    all_deep_text += f"\n\n=== {basename} ===\n\n{content}"

print(f"Loaded {len(deep_reads)} deep-read files, total {len(all_deep_text)} chars")
print(f"Existing paths: {len(spec.get('paths', {}))}")

# ============================================================
# 3. Build enrichment lookup tables
# ============================================================

# Map of function/class names to their documentation snippets
enrichments = {}

def extract_context(text, search_term, context_lines=30):
    """Extract context around a search term."""
    lines = text.split('\n')
    results = []
    for i, line in enumerate(lines):
        if search_term.lower() in line.lower():
            start = max(0, i - 2)
            end = min(len(lines), i + context_lines)
            results.append('\n'.join(lines[start:end]))
    return results

# ============================================================
# 4. Define enrichment mappings
# ============================================================

# Key enrichment data extracted from deep reads
FUSION_AHRS_ENRICHMENTS = {
    'FusionAhrsInitialise': 
        'C signature: void FusionAhrsInitialise(FusionAhrs *const ahrs);\n'
        'Initialises the AHRS structure with default settings (convention=NWU, gain=0.5, '
        'gyroscopeRange=0.0, accelerationRejection=90.0, magneticRejection=90.0, '
        'recoveryTriggerPeriod=0). Resets quaternion to identity {1,0,0,0} and enables startup mode '
        'with gain ramping. The FusionAhrs struct contains: settings (FusionAhrsSettings), '
        'quaternion (FusionQuaternion), accelerometer, halfGravity vectors, startup flag, '
        'rampedGain, and recovery state variables.\n'
        'Source: Fusion/FusionAhrs.h (xioTechnologies/Fusion)\n'
        'Cross-ref: Call FusionAhrsSetSettings() to customize, FusionAhrsUpdate() to process IMU data.',

    'FusionAhrsSetSettings':
        'C signature: void FusionAhrsSetSettings(FusionAhrs *const ahrs, const FusionAhrsSettings *const settings);\n'
        'FusionAhrsSettings fields:\n'
        '  - convention: FusionConventionNwu (North-West-Up), FusionConventionEnu (East-North-Up), or FusionConventionNed (North-East-Down)\n'
        '  - gain: float — Complementary filter gain (0.5 typical; 0=gyro only, higher=more accel/mag trust)\n'
        '  - gyroscopeRange: float — Gyroscope range in deg/s (0=disable angular rate recovery)\n'
        '  - accelerationRejection: float — Threshold in degrees for rejecting spurious accelerometer data (0=disable; 10 typical)\n'
        '  - magneticRejection: float — Threshold in degrees for rejecting spurious magnetometer data (0=disable; 10 typical)\n'
        '  - recoveryTriggerPeriod: unsigned int — Samples before triggering recovery (0=disable; 5*sampleRate typical)\n'
        'Internally converts rejection thresholds. Disables rejection if gain=0 or recoveryTriggerPeriod=0.\n'
        'Source: Fusion/FusionAhrs.h',

    'FusionAhrsUpdate':
        'C signature: void FusionAhrsUpdate(FusionAhrs *const ahrs, const FusionVector gyroscope, '
        'const FusionVector accelerometer, const FusionVector magnetometer, const float deltaTime);\n'
        'Core AHRS update implementing the revised Madgwick algorithm (PhD thesis Ch.7). Parameters:\n'
        '  - ahrs: FusionAhrs* — AHRS state structure\n'
        '  - gyroscope: FusionVector — Gyroscope reading in degrees per second\n'
        '  - accelerometer: FusionVector — Accelerometer reading in g (1g = 9.81 m/s²)\n'
        '  - magnetometer: FusionVector — Magnetometer in any calibrated units\n'
        '  - deltaTime: float — Time since last update in seconds (e.g., 0.01 for 100Hz)\n'
        'Algorithm: Integrates gyroscope with accelerometer/magnetometer feedback via complementary filter. '
        'Handles startup gain ramping (high initial gain for fast convergence), angular rate recovery '
        '(detects and compensates for gyroscope saturation), and acceleration/magnetic rejection '
        '(ignores spurious sensor readings using cross-product error metrics).\n'
        'Output: Updates internal quaternion. Retrieve via FusionAhrsGetQuaternion().\n'
        'Source: Fusion/FusionAhrs.c\n'
        'Cross-ref: FusionAhrsUpdateNoMagnetometer() for 6-axis, FusionAhrsUpdateExternalHeading() for GPS heading.',

    'FusionAhrsUpdateNoMagnetometer':
        'C signature: void FusionAhrsUpdateNoMagnetometer(FusionAhrs *const ahrs, '
        'const FusionVector gyroscope, const FusionVector accelerometer, const float deltaTime);\n'
        'AHRS update using only gyroscope and accelerometer (no magnetometer). Calls FusionAhrsUpdate() '
        'with zero magnetometer vector. During startup phase, heading (yaw) is zeroed to prevent drift. '
        'Use this for glasses without magnetometer or in magnetically disturbed environments.\n'
        'Parameters: Same as FusionAhrsUpdate minus magnetometer.\n'
        'Source: Fusion/FusionAhrs.c',

    'FusionAhrsUpdateExternalHeading':
        'C signature: void FusionAhrsUpdateExternalHeading(FusionAhrs *const ahrs, '
        'const FusionVector gyroscope, const FusionVector accelerometer, '
        'const float heading, const float deltaTime);\n'
        'AHRS update using external heading source (e.g., GPS compass) instead of magnetometer. '
        'Constructs an equivalent magnetometer vector from the heading angle and current roll orientation.\n'
        '  - heading: float — External heading in degrees (0=North, 90=East)\n'
        'Source: Fusion/FusionAhrs.c',

    'FusionAhrsGetQuaternion':
        'C signature: FusionQuaternion FusionAhrsGetQuaternion(const FusionAhrs *const ahrs);\n'
        'Returns the current orientation quaternion {w, x, y, z} describing sensor orientation relative to Earth. '
        'Convention-aware (NWU/ENU/NED as configured). The quaternion is a unit quaternion (|q|=1).\n'
        'Return type: FusionQuaternion — union of float array[4] and struct {w, x, y, z}.\n'
        'Usage: Convert to Euler with FusionQuaternionToEuler(), to matrix with FusionQuaternionToMatrix().\n'
        'Source: Fusion/FusionAhrs.h',

    'FusionAhrsSetQuaternion':
        'C signature: void FusionAhrsSetQuaternion(FusionAhrs *const ahrs, const FusionQuaternion quaternion);\n'
        'Directly sets the orientation quaternion. Use for initialization from known orientation or for manual correction.\n'
        'Source: Fusion/FusionAhrs.h',

    'FusionAhrsGetGravity':
        'C signature: FusionVector FusionAhrsGetGravity(const FusionAhrs *const ahrs);\n'
        'Returns direction of gravity in sensor frame as a unit vector. Computed from the '
        'current quaternion orientation. Convention-aware (NWU: {0,0,+1}, NED: {0,0,-1}).\n'
        'Source: Fusion/FusionAhrs.h',

    'FusionAhrsGetLinearAcceleration':
        'C signature: FusionVector FusionAhrsGetLinearAcceleration(const FusionAhrs *const ahrs);\n'
        'Returns linear acceleration (accelerometer with gravity removed) in sensor frame, in g units. '
        'Computed as: accelerometer - gravity_direction. Useful for detecting motion, steps, gestures.\n'
        'Source: Fusion/FusionAhrs.h',

    'FusionAhrsGetEarthAcceleration':
        'C signature: FusionVector FusionAhrsGetEarthAcceleration(const FusionAhrs *const ahrs);\n'
        'Returns acceleration in Earth frame with gravity removed. Rotates the accelerometer reading '
        'to Earth frame using the current quaternion, then subtracts gravity vector. Useful for '
        'navigation and dead-reckoning in world coordinates.\n'
        'Source: Fusion/FusionAhrs.h',

    'FusionAhrsGetInternalStates':
        'C signature: FusionAhrsInternalStates FusionAhrsGetInternalStates(const FusionAhrs *const ahrs);\n'
        'Returns internal algorithm states for debugging/monitoring:\n'
        '  - accelerationError: float — Angular error in degrees between accelerometer and algorithm output\n'
        '  - accelerometerIgnored: bool — true if accelerometer was rejected in last update\n'
        '  - accelerationRecoveryTrigger: float — Recovery trigger progress 0.0-1.0\n'
        '  - magneticError: float — Angular error in degrees between magnetometer and algorithm\n'
        '  - magnetometerIgnored: bool — true if magnetometer was rejected\n'
        '  - magneticRecoveryTrigger: float — Magnetic recovery trigger 0.0-1.0\n'
        'Source: Fusion/FusionAhrs.h',

    'FusionAhrsGetFlags':
        'C signature: FusionAhrsFlags FusionAhrsGetFlags(const FusionAhrs *const ahrs);\n'
        'Returns algorithm status flags:\n'
        '  - startup: bool — true during initial convergence period (gain ramping)\n'
        '  - angularRateRecovery: bool — true if gyroscope saturation detected and being compensated\n'
        '  - accelerationRecovery: bool — true during acceleration recovery mode\n'
        '  - magneticRecovery: bool — true during magnetic recovery mode\n'
        'Source: Fusion/FusionAhrs.h',

    'FusionAhrsSetHeading':
        'C signature: void FusionAhrsSetHeading(FusionAhrs *const ahrs, const float heading);\n'
        'Sets the heading (yaw) of the current orientation by applying a Z-axis rotation to match '
        'the desired heading in degrees. Does not affect pitch or roll.\n'
        '  - heading: float — Desired heading in degrees (0=North)\n'
        'Source: Fusion/FusionAhrs.h',

    'FusionAhrsRestart':
        'C signature: void FusionAhrsRestart(FusionAhrs *const ahrs);\n'
        'Restarts the AHRS algorithm. Resets quaternion to identity {1,0,0,0}, re-enables startup mode '
        'with high initial gain for fast re-convergence. Use after significant orientation change or sensor reset.\n'
        'Source: Fusion/FusionAhrs.h',

    'FusionBiasInitialise':
        'C signature: void FusionBiasInitialise(FusionBias *const bias);\n'
        'Initialises gyroscope bias estimation with default settings: sampleRate=100Hz, '
        'stationaryThreshold=3.0 deg/s, stationaryPeriod=3.0s. Zeroes the offset vector.\n'
        'FusionBias struct: settings, filterCoefficient, timeout, timer, offset (FusionVector).\n'
        'Source: Fusion/FusionBias.h',

    'FusionBiasSetSettings':
        'C signature: void FusionBiasSetSettings(FusionBias *const bias, const FusionBiasSettings *const settings);\n'
        'FusionBiasSettings fields:\n'
        '  - sampleRate: float — Sample rate in Hz (default: 100)\n'
        '  - stationaryThreshold: float — Max gyro magnitude in deg/s to consider stationary (default: 3.0)\n'
        '  - stationaryPeriod: float — Seconds of stationary detection before updating bias (default: 3.0)\n'
        'Computes internal filter coefficient and timeout from settings.\n'
        'Source: Fusion/FusionBias.h',

    'FusionBiasUpdate':
        'C signature: FusionVector FusionBiasUpdate(FusionBias *const bias, FusionVector gyroscope);\n'
        'Must be called every sample. Detects stationary periods (gyro magnitude < threshold for stationaryPeriod). '
        'During stationary, updates bias offset using low-pass filter. Returns offset-corrected gyroscope.\n'
        '  - gyroscope: FusionVector — Raw gyroscope in degrees per second\n'
        '  - returns: FusionVector — Bias-corrected gyroscope in degrees per second\n'
        'Source: Fusion/FusionBias.c',

    'FusionCompass':
        'C signature: float FusionCompass(const FusionVector accelerometer, const FusionVector magnetometer, '
        'const FusionConvention convention);\n'
        'Calculates tilt-compensated magnetic heading. Uses accelerometer to determine tilt (gravity direction), '
        'then projects magnetometer onto horizontal plane. Convention-aware: computes north/west/east vectors '
        'differently per NWU/ENU/NED convention.\n'
        '  - accelerometer: FusionVector — in any calibrated units\n'
        '  - magnetometer: FusionVector — in any calibrated units\n'
        '  - convention: FusionConvention — Earth axes convention\n'
        '  - returns: float — Magnetic heading in degrees (0-360)\n'
        'Source: Fusion/FusionCompass.c',

    'FusionModelInertial':
        'C signature: static inline FusionVector FusionModelInertial(const FusionVector uncalibrated, '
        'const FusionMatrix misalignment, const FusionVector sensitivity, const FusionVector offset);\n'
        'Applies gyroscope/accelerometer calibration model: result = M * diag(s) * (raw - offset)\n'
        '  - uncalibrated: Raw sensor reading\n'
        '  - misalignment: 3x3 misalignment correction matrix\n'
        '  - sensitivity: Sensitivity diagonal (as vector for element-wise multiply)\n'
        '  - offset: Zero-rate offset vector\n'
        'Source: Fusion/FusionModel.h',

    'FusionModelMagnetic':
        'C signature: static inline FusionVector FusionModelMagnetic(const FusionVector uncalibrated, '
        'const FusionMatrix softIronMatrix, const FusionVector hardIronOffset);\n'
        'Applies magnetometer calibration: result = S * (raw - h)\n'
        '  - uncalibrated: Raw magnetometer reading\n'
        '  - softIronMatrix: 3x3 soft-iron correction matrix\n'
        '  - hardIronOffset: Hard-iron offset vector\n'
        'Source: Fusion/FusionModel.h',

    'FusionRemap':
        'C signature: static inline FusionVector FusionRemap(const FusionVector sensor, '
        'const FusionRemapAlignment alignment);\n'
        'Remaps sensor axes using one of 24 orthogonal permutations for non-standard mounting.\n'
        'FusionRemapAlignment enum values: PXPYPz (+X+Y+Z, no remap), PXPZNY (+X+Z-Y), etc.\n'
        'Example: If sensor is mounted rotated 90° around X, use the appropriate alignment to remap '
        'axes to body frame before passing to AHRS.\n'
        'Source: Fusion/FusionRemap.h',
}

# XRLinuxDriver enrichments
XRLINUX_ENRICHMENTS = {
    'normalize_quaternion':
        'C signature: imu_quat_type normalize_quaternion(imu_quat_type q);\n'
        'Normalizes quaternion {x,y,z,w} to unit length. Part of XRLinuxDriver imu.c (258 lines).\n'
        'Type: imu_quat_type { float x, y, z, w }\n'
        'Source: XRLinuxDriver/src/imu.c',

    'multiply_quaternions':
        'C signature: imu_quat_type multiply_quaternions(imu_quat_type q1, imu_quat_type q2);\n'
        'Hamilton product of two quaternions. Used in pose pipeline for reference pose subtraction.\n'
        'Source: XRLinuxDriver/src/imu.c',

    'euler_to_quaternion_xyz':
        'C signature: imu_quat_type euler_to_quaternion_xyz(imu_euler_type euler);\n'
        'Convert Euler angles (XYZ order) to quaternion. imu_euler_type { float roll, pitch, yaw }.\n'
        'Also available: euler_to_quaternion_zyx(), euler_to_quaternion_zxy().\n'
        'Source: XRLinuxDriver/src/imu.c',

    'quaternion_to_euler_zyx':
        'C signature: imu_euler_type quaternion_to_euler_zyx(imu_quat_type q);\n'
        'Convert quaternion to Euler angles (ZYX intrinsic order). Returns {roll, pitch, yaw} in radians.\n'
        'Also available: quaternion_to_euler_xyz(), quaternion_to_euler_zxy().\n'
        'Source: XRLinuxDriver/src/imu.c',

    'multitap_detection':
        'C signature: Implemented in XRLinuxDriver/src/multitap.c\n'
        'Detects double-tap (recenter screen) and triple-tap (recalibrate) from IMU acceleration spikes. '
        'Configurable via config.ini multi_tap_enabled flag. Uses acceleration magnitude threshold '
        'with timing windows to distinguish tap count.\n'
        'Source: XRLinuxDriver/src/multitap.c',

    'setup_ipc_values':
        'C signature: void setup_ipc()\n'
        'Sets up shared memory IPC for pose data communication. Creates memory-mapped files for:\n'
        '  - Quaternion orientation (x, y, z, w)\n'
        '  - Euler angles (roll, pitch, yaw)\n'
        '  - Euler velocities\n'
        '  - Look-ahead prediction values\n'
        'Used by Breezy Desktop and other consumers to read head pose without direct connection.\n'
        'Source: XRLinuxDriver/src/ipc.c',
}

# USB VID/PID enrichments for XRLinuxDriver
USB_VIDPID_INFO = """
Supported USB VID/PIDs (from XRLinuxDriver/src/devices/):

XREAL (VID: 0x3318):
  0x0424=Air, 0x0428=Air 2, 0x0432=Air 2 Pro, 0x0426=Air 2 Ultra
  0x0435/0x0436=One Pro, 0x0437/0x0438=One, 0x043e/0x043d=1S
  FOV: Air=45°, Ultra=52°, One Pro=57°, One=50°, 1S=52°
  IMU: 250Hz (forced from 1000Hz native), Resolution: 1920x1080

VITURE (VID: 0x35ca):
  0x1011/0x1013/0x1017=One(40°), 0x1015/0x101b=One Lite(40°)
  0x1019/0x101d=Pro(43°), 0x1131=Luma(50°), 0x1121/0x1141=Luma Pro(52°)
  0x1101/0x1104=Luma Ultra(52°), 0x1151=Luma Cyber(52°), 0x1201=Beast(58°)
  IMU: 60-1000Hz configurable

Rokid (VID from SDK header):
  0x162B-0x162F, 0x2002, 0x2180 = Max/Air
  FOV: 45°, IMU: 90Hz

RayNeo (VID: 0x1bbb, PID: 0xaf50):
  Models: NXTWEAR S/S+, Air 2, 2s, 3s/Pro
  FOV: 43°, IMU: 250Hz (forced from 500Hz)
"""

# RayNeo enrichments
RAYNEO_ENRICHMENTS = {
    'RegisterIMUEventCallback':
        'RayNeo SDK function for registering IMU event callbacks. Part of the ARDK for Android (AAR).\n'
        'Used with OpenIMU/CloseIMU for IMU data streaming.\n'
        'Android sensor alternative: SensorManager.getDefaultSensor(Sensor.TYPE_GAME_ROTATION_VECTOR)\n'
        'Rates: SENSOR_DELAY_FASTEST, SENSOR_DELAY_GAME, SENSOR_DELAY_NORMAL, SENSOR_DELAY_UI\n'
        'Returns quaternion data convertible to Euler angles.\n'
        'Source: RayNeo ARDK (Feishu docs)\n'
        'Cross-ref: XRLinuxDriver rayneo.c — EstablishUsbConnection, StartXR, OpenIMU, GetHeadTrackerPose',

    'GetHeadTrackerPose':
        'RayNeo SDK: Gets 6DoF pose — rotation[4] (quaternion xyzw), position[3] (meters), timestamp.\n'
        'Requires StartXR() to be called first. Uses VGA camera for visual-inertial SLAM.\n'
        'SlamState enum: INITIALIZING, TRACKING_SUCCESS, TRACKING_FAIL.\n'
        'Unity API: Algorithm.EnableSlamHeadTracker(), Algorithm.GetSlamStatus()\n'
        'XRLinuxDriver uses: VID=0x1bbb, PID=0xaf50, coordinate system East-Up-South → NWU with 15° offset.\n'
        'Source: RayNeo ARDK + XRLinuxDriver/src/devices/rayneo.c',

    'StartXR':
        'RayNeo SDK: Starts XR mode on glasses. Must be called before GetHeadTrackerPose() or OpenIMU().\n'
        'On X2: Enables 6DOF SLAM with VGA camera fusion.\n'
        'On X3 Pro: Enables 3DOF or optional 6DOF mode.\n'
        'Source: RayNeo ARDK, XRLinuxDriver/src/devices/rayneo.c',

    'StopXR':
        'RayNeo SDK: Stops XR mode. Releases camera and SLAM resources.\n'
        'Source: RayNeo ARDK, XRLinuxDriver/src/devices/rayneo.c',

    'SwitchTo2D':
        'RayNeo SDK: Switches display to 2D mode (single view, no SBS).\n'
        'Resolution: 1920x1080 per eye.\n'
        'Source: XRLinuxDriver/src/devices/rayneo.c',

    'SwitchTo3D':
        'RayNeo SDK: Switches display to 3D/SBS (side-by-side) mode.\n'
        'Resolution: 3840x1080 total (1920x1080 per eye).\n'
        'Source: XRLinuxDriver/src/devices/rayneo.c',
}

# Monado enrichments
MONADO_ENRICHMENTS = {
    'xrt_device.update_inputs':
        'C signature: xrt_result_t (*update_inputs)(struct xrt_device *xdev);\n'
        'Refreshes all input state on a Monado XR device. Must be called before reading input values. '
        'Part of the xrt_device function pointer table (25+ methods). Supports 50+ device types '
        'including XREAL Air (VID=0x3318), Rokid, simulated HMD, hand trackers, etc.\n'
        'Return: XRT_SUCCESS (0) on success, or XRT_ERROR_* codes.\n'
        'Source: monado/src/xrt/include/xrt/xrt_device.h',

    'xrt_device.get_tracked_pose':
        'C signature: xrt_result_t (*get_tracked_pose)(struct xrt_device *xdev, '
        'enum xrt_input_name name, int64_t at_timestamp_ns, struct xrt_space_relation *out_relation);\n'
        'Gets 6DoF pose from device at a specific timestamp. Returns xrt_space_relation containing:\n'
        '  - pose: xrt_pose {orientation: xrt_quat, position: xrt_vec3}\n'
        '  - linear_velocity, angular_velocity: xrt_vec3\n'
        '  - relation_flags: bitmask of valid components\n'
        'Supported by devices with orientation_tracking or position_tracking capability.\n'
        'Source: monado/src/xrt/include/xrt/xrt_device.h',

    'xrt_device.get_hand_tracking':
        'C signature: xrt_result_t (*get_hand_tracking)(struct xrt_device *xdev, '
        'enum xrt_input_name name, int64_t desired_timestamp_ns, '
        'struct xrt_hand_joint_set *out_value, int64_t *out_timestamp_ns);\n'
        'Gets hand joint positions (26 joints per OpenXR XR_EXT_hand_tracking). '
        'Returns xrt_hand_joint_set with joint poses and radii. '
        'Supported by Leap Motion (ultraleap_v2/v5), hand tracking driver (ht), and controller emulation.\n'
        'Source: monado/src/xrt/include/xrt/xrt_device.h',

    'xrt_device.get_face_tracking':
        'C signature: xrt_result_t (*get_face_tracking)(struct xrt_device *xdev, '
        'enum xrt_input_name facial_expression_type, int64_t at_timestamp_ns, '
        'struct xrt_facial_expression_set *out_value);\n'
        'Gets facial expressions. Supports XR_FB_face_tracking2 and XR_HTC_facial_tracking extensions. '
        'Device types: XRT_DEVICE_FB_FACE_TRACKING2, XRT_DEVICE_HTC_FACE_TRACKING, XRT_DEVICE_ANDROID_FACE_TRACKING.\n'
        'Source: monado/src/xrt/include/xrt/xrt_device.h',

    'xrt_device.get_body_joints':
        'C signature: xrt_result_t (*get_body_joints)(struct xrt_device *xdev, '
        'enum xrt_input_name body_tracking_type, int64_t desired_timestamp_ns, '
        'struct xrt_body_joint_set *out_value);\n'
        'Gets full body tracking joints. Supports XR_FB_body_tracking and XR_META_body_tracking_full_body. '
        'Device type: XRT_DEVICE_FB_BODY_TRACKING. Includes calibration via reset/set_calibration_override_meta.\n'
        'Source: monado/src/xrt/include/xrt/xrt_device.h',

    'xrt_device.set_output':
        'C signature: xrt_result_t (*set_output)(struct xrt_device *xdev, '
        'enum xrt_output_name name, const union xrt_output_value *value);\n'
        'Sets haptic/vibration output on device. Maps to OpenXR xrApplyHapticFeedback.\n'
        'Supported by controllers with force_feedback capability.\n'
        'Source: monado/src/xrt/include/xrt/xrt_device.h',

    'xrt_device.compute_distortion':
        'C signature: xrt_result_t (*compute_distortion)(struct xrt_device *xdev, '
        'uint32_t view, float u, float v, struct xrt_uv_triplet *out_result);\n'
        'Computes lens distortion correction for a given UV coordinate. Used by the Vulkan compositor '
        'for rendering. Distortion models: NONE, COMPUTE (this function), MESHUV (pre-computed mesh).\n'
        'Source: monado/src/xrt/include/xrt/xrt_device.h',

    'xrt_device.get_battery_status':
        'C signature: xrt_result_t (*get_battery_status)(struct xrt_device *xdev, '
        'bool *out_present, bool *out_charging, float *out_charge);\n'
        'Gets battery level. out_charge is 0.0-1.0. Requires battery_status capability.\n'
        'Source: monado/src/xrt/include/xrt/xrt_device.h',

    'xrt_device.set_brightness':
        'C signature: xrt_result_t (*set_brightness)(struct xrt_device *xdev, '
        'float brightness, bool relative);\n'
        'Sets display brightness. If relative=true, adjusts by brightness delta. '
        'Requires brightness_control capability.\n'
        'Source: monado/src/xrt/include/xrt/xrt_device.h',

    'xrt_space_overseer.create_offset_space':
        'C signature: xrt_result_t (*create_offset_space)(struct xrt_space_overseer *xso, '
        'struct xrt_space *parent, const struct xrt_pose *offset, struct xrt_space **out_space);\n'
        'Creates a space with a fixed offset from parent. Used for creating reference spaces '
        '(VIEW, LOCAL, STAGE, LOCAL_FLOOR, UNBOUNDED) from the root tracking space.\n'
        'Source: monado/src/xrt/include/xrt/xrt_space.h',

    'xrt_space_overseer.locate_space':
        'C signature: xrt_result_t (*locate_space)(struct xrt_space_overseer *xso, '
        'struct xrt_space *base_space, const struct xrt_pose *base_offset, int64_t at_ns, '
        'struct xrt_space *space, const struct xrt_pose *offset, struct xrt_space_relation *out_rel);\n'
        'Locates one space relative to another at a given timestamp. Returns xrt_space_relation '
        'with pose, velocities, and validity flags. Core operation for OpenXR xrLocateSpace.\n'
        'Source: monado/src/xrt/include/xrt/xrt_space.h',

    'xrt_space_overseer.recenter_local_spaces':
        'C signature: xrt_result_t (*recenter_local_spaces)(struct xrt_space_overseer *xso);\n'
        'Recenters all local reference spaces to current head position. Called when user requests recenter.\n'
        'Source: monado/src/xrt/include/xrt/xrt_space.h',
}

# Overpass/Geo enrichments
GEO_ENRICHMENTS = {
    'overpass_query':
        'Overpass API query endpoint: POST https://overpass-api.de/api/interpreter\n'
        'Public instances: overpass-api.de, maps.mail.ru/osm/tools/overpass, overpass.private.coffee\n\n'
        'Query Language: OverpassQL (primary), XML, SQL (via Postpass)\n\n'
        'Template variables:\n'
        '  {{bbox}} — Current map bounding box (s,w,n,e)\n'
        '  {{center}} — Map center (lat,lng)\n'
        '  {{geocodeArea:name}} — Nominatim area lookup\n'
        '  {{geocodeCoords:name}} — Nominatim coordinate lookup\n\n'
        'Example — nearby restaurants:\n'
        '  [out:json][timeout:25];\n'
        '  nwr["amenity"="restaurant"](around:500,{lat},{lng});\n'
        '  out geom;\n\n'
        'Example — all POIs in view:\n'
        '  [out:json][timeout:25];\n'
        '  (node["amenity"]({{bbox}});node["shop"]({{bbox}});node["tourism"]({{bbox}}););\n'
        '  out geom;\n\n'
        'Rate limits: ~10K/day fair use, free. Response: JSON elements[] with nodes/ways/relations.\n'
        'Source: overpass-turbo source code analysis (deep-read 10-geo-maps.md)',

    'gemini_maps':
        'Gemini API Maps Grounding — connects Gemini AI with 250M+ Google Maps places.\n\n'
        'API Config (JSON):\n'
        '  {"tools": {"googleMaps": {}},\n'
        '   "toolConfig": {"retrievalConfig": {"latLng": {"latitude": N, "longitude": N}}}}\n\n'
        'Python SDK:\n'
        '  from google import genai\n'
        '  client = genai.Client()\n'
        '  response = client.models.generate_content(\n'
        '    model="gemini-3-flash-preview",\n'
        '    contents="Find coffee near here",\n'
        '    config=types.GenerateContentConfig(\n'
        '      tools=[types.Tool(google_maps=types.GoogleMaps())],\n'
        '      tool_config=types.ToolConfig(retrieval_config=types.RetrievalConfig(\n'
        '        lat_lng=types.LatLng(latitude=LAT, longitude=LNG)))))\n\n'
        'Response fields:\n'
        '  groundingChunks[].maps: {uri, title, placeId}\n'
        '  groundingSupports[]: {segment: {startIndex, endIndex, text}, groundingChunkIndices}\n'
        '  googleMapsWidgetContextToken: for rendering Places widget\n\n'
        'Pricing: $25/1K grounded prompts, free tier 500/day.\n'
        'Supported models: Gemini 3.1 Pro/Flash-Lite, 3 Flash, 2.5 Pro/Flash/Flash-Lite, 2.0 Flash.\n'
        'Source: Google Gemini API docs (deep-read 10-geo-maps.md)',
}

# ============================================================
# 5. Apply enrichments to existing paths
# ============================================================

paths = spec.get('paths', {})
enriched_count = 0

for path_key, path_val in paths.items():
    for method_key, method_val in path_val.items():
        if not isinstance(method_val, dict):
            continue
        
        op_id = method_val.get('operationId', '')
        summary = method_val.get('summary', '')
        desc = method_val.get('description', '')
        
        # Extract the function name from the path
        func_name = path_key.split('/')[-1] if '/' in path_key else ''
        # Also try the last two segments for class.method
        path_parts = path_key.rstrip('/').split('/')
        if len(path_parts) >= 2:
            class_method = path_parts[-1]
            parent = path_parts[-2] if len(path_parts) > 2 else ''
        
        enrichment = None
        
        # Match Fusion AHRS functions
        for fname, enrich_text in FUSION_AHRS_ENRICHMENTS.items():
            if fname in func_name or fname in op_id:
                enrichment = enrich_text
                break
        
        # Match XRLinuxDriver functions
        if not enrichment:
            for fname, enrich_text in XRLINUX_ENRICHMENTS.items():
                if fname in func_name or fname in op_id:
                    enrichment = enrich_text
                    break
        
        # Match RayNeo functions
        if not enrichment:
            for fname, enrich_text in RAYNEO_ENRICHMENTS.items():
                if fname in func_name or fname in op_id:
                    enrichment = enrich_text
                    break
        
        # Match Monado functions
        if not enrichment:
            for fname, enrich_text in MONADO_ENRICHMENTS.items():
                if fname.replace('.', '_') in op_id or fname in path_key:
                    enrichment = enrich_text
                    break
        
        # Add USB VID/PID info to XRLinuxDriver device-related paths
        if not enrichment and 'XRLinuxDriver' in path_key:
            if any(kw in func_name for kw in ['open_imu', 'close_imu', 'register_raw', 'register_pose', 
                                                'OpenIMU', 'CloseIMU', 'Recenter']):
                enrichment = USB_VIDPID_INFO.strip()
        
        # Enrich Overpass paths
        if not enrichment and 'overpass' in path_key.lower():
            enrichment = GEO_ENRICHMENTS.get('overpass_query')
        
        # Enrich Gemini Maps paths
        if not enrichment and 'gemini' in path_key.lower() and 'maps' in path_key.lower():
            enrichment = GEO_ENRICHMENTS.get('gemini_maps')
        
        # Enrich StardustXR paths with protocol info
        if not enrichment and 'stardust' in path_key.lower():
            if 'Hand' in func_name:
                enrichment = (
                    'StardustXR Hand struct — Full hand articulation from OpenXR hand tracking:\n'
                    '  right: bool, thumb: Thumb (tip/distal/proximal/metacarpal joints),\n'
                    '  index/middle/ring/little: Finger (tip/distal/intermediate/proximal/metacarpal),\n'
                    '  palm/wrist/elbow: Joint {position: Vec3, rotation: Quat, radius: f32, distance: f32}\n'
                    'Heuristic methods: palm_normal(), radial_axis(), distal_axis(),\n'
                    '  finger_curl(finger) -> f32, thumb_curl() -> f32,\n'
                    '  pinch_distance(finger) -> f32, pinch_position() -> Vec3,\n'
                    '  stable_pinch_position() -> Vec3, predicted_pinch_position() -> Vec3,\n'
                    '  pinch_strength() -> f32, fist_strength() -> f32.\n'
                    'Input system: InputMethod + InputHandler matched via SDF field distance.\n'
                    'Protocol: FlatBuffers over Unix domain sockets with SCM_RIGHTS FD passing.\n'
                    'Source: stardust-xr-fusion (Rust), protocol/input.kdl'
                )
            elif 'Spatial' in func_name or 'spatial' in path_key:
                enrichment = (
                    'StardustXR Spatial node — Base 3D positioned object in the scenegraph.\n'
                    'Transform: {translation: Vec3?, rotation: Quat?, scale: Vec3?}\n'
                    'Methods: create(parent, transform), set_local_transform(Transform),\n'
                    '  set_relative_transform(relative_to, Transform), set_spatial_parent(parent),\n'
                    '  export_spatial() -> u64 (for cross-client sharing).\n'
                    'BoundingBox: {center: Vec3, size: Vec3}\n'
                    'Parent-child hierarchy with local/global transform computation.\n'
                    'Source: stardust-xr-fusion/spatial.rs, protocol/spatial.kdl'
                )
            elif 'Field' in func_name or 'field' in path_key:
                enrichment = (
                    'StardustXR Field — Signed Distance Field shapes for spatial interaction.\n'
                    'Shape union: Box(Vec3) | Sphere(f32) | Cylinder(CylinderShape) | Torus(TorusShape) | Spline(CubicSplineShape)\n'
                    'Methods: distance(space, point)->f32, normal(space, point)->Vec3,\n'
                    '  closest_point(space, point)->Vec3, ray_march(space, origin, direction)->RayMarchResult,\n'
                    '  set_shape(Shape), export_field()->u64.\n'
                    'Fields are used by the SUIS (Spatial Universal Interaction System) to match\n'
                    'InputMethods with InputHandlers via distance ordering.\n'
                    'Source: stardust-xr-fusion/fields.rs, protocol/field.kdl'
                )
        
        # Enrich PhoenixHeadTracker paths
        if not enrichment and 'PhoenixHeadTracker' in path_key:
            if 'StartConnection' in func_name:
                enrichment = (
                    'C FFI: #[no_mangle] pub extern "C" fn StartConnection() -> i32;\n'
                    'Windows .NET: [DllImport("AirAPI_Windows")] static extern int StartConnection();\n'
                    'Connects to XREAL Air glasses via AirAPI_Windows.dll + hidapi.dll.\n'
                    'Returns 1 on success, 0 on failure. XREAL Air VID: 0x3318.\n'
                    'Also available in headset-utils Rust: Connection::start() -> Result<&Connection>.\n'
                    'Source: PhoenixHeadTracker/Form1.cs, headset-utils/lib.rs'
                )
            elif 'GetEuler' in func_name:
                enrichment = (
                    'C FFI: #[no_mangle] pub extern "C" fn GetEuler() -> *const f32;\n'
                    'Windows .NET: [DllImport("AirAPI_Windows")] static extern IntPtr GetEuler();\n'
                    'Returns pointer to float[3]: [roll, pitch, yaw] in degrees (FRD frame - Forward-Right-Down).\n'
                    'The headset-utils Rust backend uses NaiveCF complementary filter with:\n'
                    '  BASE_GRAV_RATIO=0.005, INCONSISTENCY_DECAY=0.90\n'
                    'Coordinate conversion: RUB (sensor) -> FRD (output): (-z, x, -y).\n'
                    'PhoenixHeadTracker applies Kalman filter (q=process noise, r=measurement noise) on deltas,\n'
                    'then outputs to OpenTrack UDP (127.0.0.1:4242, 48 bytes: 6 doubles [x,y,z,yaw,pitch,roll]).\n'
                    'Source: PhoenixHeadTracker/Form1.cs, headset-utils/lib.rs + naive_cf.rs'
                )
            elif 'KalmanFilter' in func_name:
                enrichment = (
                    'class KalmanFilter:\n'
                    '  KalmanFilter(double q, double r, double p, double x)\n'
                    '    q: process noise covariance\n'
                    '    r: measurement noise covariance\n'
                    '    p: initial estimate error covariance\n'
                    '    x: initial state estimate\n'
                    '  double Update(double measurement) -> filtered value\n'
                    '1D Kalman filter used for smoothing IMU rotation deltas before sending to OpenTrack.\n'
                    'Three instances: one each for yaw (x), pitch (y), and roll.\n'
                    'Source: PhoenixHeadTracker/Form1.cs'
                )
        
        # Enrich RayDesk paths
        if not enrichment and 'RayDesk' in path_key:
            if 'StreamRenderer' in func_name:
                enrichment = (
                    'Kotlin class StreamRenderer(context: Context) : GLSurfaceView.Renderer\n'
                    'Core OpenGL renderer for RayDesk (Moonlight/Sunshine streaming on RayNeo X3 Pro).\n'
                    'Display modes: FLOATING_MONITOR (3D virtual screen), KEYHOLE_PANNING (UV-based panning), '
                    'CURVED_MONITOR (cylindrical projection).\n'
                    'Properties: @Volatile displayMode, videoProvider, headYawDegrees/headPitchDegrees,\n'
                    '  cursorX/cursorY, casSharpening (0-1), stereoEnabled.\n'
                    'Methods: updateStreamResolution(w,h), recenterVirtualScreen/CurvedMonitor/Keyhole(),\n'
                    '  setVirtualScreenScale(s), setCurvedMonitorRadius(r), setEnvironmentEnabled/Theme().\n'
                    'Video: Moonlight NvConnection -> MediaCodecDecoder -> OES texture -> GL render.\n'
                    'Source: RayDesk/app/src/main/java/...gl/StreamRenderer.kt (998 lines)'
                )
            elif 'CylinderController' in path_key:
                enrichment = (
                    'Kotlin class CylinderController — Curved cylindrical display controller.\n'
                    'Uses OpenGL cylinder mesh for widescreen virtual monitor.\n'
                    'Methods: zoomIn/Out/resetZoom(), setRadius(r, immediate),\n'
                    '  getViewMatrix/getMVPMatrix/getLeftEyeMVPMatrix/getRightEyeMVPMatrix() -> FloatArray (4x4).\n'
                    'Returns 16-float column-major matrices for stereo rendering.\n'
                    'Source: RayDesk/app/src/main/java/.../spatial/CylinderController.kt'
                )
            elif 'OneEuroFilter' in func_name:
                enrichment = (
                    '1€ (One Euro) noise filter for smooth head tracking with low latency.\n'
                    'Combines low-pass filtering with speed-adaptive cutoff frequency.\n'
                    'At low speed: aggressive smoothing (low cutoff). At high speed: responsive (high cutoff).\n'
                    'Parameters: minCutoff (Hz), beta (speed coefficient), dCutoff (derivative cutoff).\n'
                    'Source: RayDesk/app/src/main/java/.../spatial/OneEuroFilter.kt'
                )
        
        # Enrich Everysight paths
        if not enrichment and 'everysight' in path_key.lower():
            enrichment = (
                'Everysight Maverick SDK — Fluent builder API for AR glasses HUD rendering.\n'
                'Hello World example (Kotlin):\n'
                '  Text().setText("Hello Developer")\n'
                '    .setResource(Font.StockFont.Medium)\n'
                '    .setTextAlign(Align.center)\n'
                '    .setXY(getWidth()/2, getHeight()/2)\n'
                '    .setForegroundColor(EvsColor.Green.rgba)\n'
                '    .addTo(this)\n'
                'UI classes: Screen, ArScreen, Viewport, UIElement, Text, TextBlock, ImgSrc, AutoLayout, Column, Row.\n'
                'AR classes (beta): ArWindow, ArModel, ArPrimitive, ArLines, ArPoints, ArTriangles, ArFactory.\n'
                'Sensors: enableInertialSensors(), enableGyro/Magnetometer/Accelerometer(),\n'
                '  registerYprSensorsEvents(), registerQuaternionSensorsEvents().\n'
                'BLE: Uses serviceCBUUID, charNotifyCBUUID, charControlCBUUID, charPairingCBUUID.\n'
                'Distribution: Maven (Android), SPM (iOS). Requires sdk.key for authentication.\n'
                'Source: Everysight Maverick SDK v2.5.0-2.6.1 (deep-read 02-everysight-coredevices.md)'
            )
        
        # Enrich headset-utils paths
        if not enrichment and 'headset-utils' in path_key:
            if 'any_fusion' in func_name:
                enrichment = (
                    'Rust: pub fn any_fusion() -> Result<Box<dyn Fusion>>;\n'
                    'Auto-detects connected glasses and creates NaiveCF complementary filter fusion instance.\n'
                    'Tries each supported type in order: Rokid (VID=0x04d2), NrealAir (VID=0x3318),\n'
                    'NrealLight (VID=0x0486), Grawoow G530 (VID=0x1ff7), MadGaze Glow (serial).\n'
                    'The Fusion trait provides: attitude_quaternion() -> UnitQuaternion<f32>,\n'
                    '  inconsistency_frd() -> f32, update() -> (), attitude_frd_rad/deg() -> Vector3<f32>.\n'
                    'Source: headset-utils/src/lib.rs'
                )
            elif 'NaiveCF' in func_name:
                enrichment = (
                    'Rust: pub struct NaiveCF { glasses, attitude, prev_gyro, inconsistency }\n'
                    'Naive complementary filter combining accelerometer and gyroscope.\n'
                    'Constants: BASE_GRAV_RATIO=0.005 (accel trust), INCONSISTENCY_DECAY=0.90.\n'
                    'Coordinate frame: RUB (Right-Up-Back) input, FRD (Forward-Right-Down) output.\n'
                    'RUB to FRD conversion: (-z, x, -y).\n'
                    'Methods: new(glasses) -> NaiveCF, update() integrates gyro + accel correction.\n'
                    'get_correction(acc, rotation, scale) -> gravity-based rotation correction.\n'
                    'Source: headset-utils/src/naive_cf.rs'
                )
        
        # Apply enrichment
        if enrichment:
            # Append enrichment to existing description
            existing_desc = method_val.get('description', '')
            if existing_desc:
                method_val['description'] = existing_desc + '\n\n--- Deep-Read Documentation ---\n\n' + enrichment
            else:
                method_val['description'] = enrichment
            enriched_count += 1

print(f"Enriched {enriched_count} existing paths")

# ============================================================
# 6. Add missing functions from deep-reads
# ============================================================

new_paths = {}

# Missing Fusion functions
fusion_missing = {
    'FusionVectorHadamard': {
        'summary': 'Hadamard (element-wise) vector product',
        'description': 'C signature: static inline FusionVector FusionVectorHadamard(const FusionVector a, const FusionVector b);\n'
                      'Returns element-wise product: {a.x*b.x, a.y*b.y, a.z*b.z}.\n'
                      'Source: Fusion/FusionMath.h',
        'tag': 'imu',
    },
    'FusionQuaternionVectorProduct': {
        'summary': 'Quaternion-vector product',
        'description': 'C signature: static inline FusionQuaternion FusionQuaternionVectorProduct(const FusionQuaternion q, const FusionVector v);\n'
                      'Returns q * v where v is treated as quaternion with w=0.\n'
                      'Source: Fusion/FusionMath.h',
        'tag': 'imu',
    },
    'FusionQuaternionNormSquared': {
        'summary': 'Quaternion norm squared',
        'description': 'C signature: static inline float FusionQuaternionNormSquared(const FusionQuaternion q);\n'
                      'Returns |q|² (w²+x²+y²+z²). More efficient than computing norm when only comparison needed.\n'
                      'Source: Fusion/FusionMath.h',
        'tag': 'imu',
    },
    'FusionBiasGetOffset': {
        'summary': 'Get current gyroscope bias offset',
        'description': 'C signature: FusionVector FusionBiasGetOffset(const FusionBias *const bias);\n'
                      'Returns the current estimated gyroscope bias offset in degrees per second.\n'
                      'Can be saved to non-volatile memory for faster startup.\n'
                      'Source: Fusion/FusionBias.h',
        'tag': 'imu',
    },
    'FusionBiasSetOffset': {
        'summary': 'Set gyroscope bias offset',
        'description': 'C signature: void FusionBiasSetOffset(FusionBias *const bias, const FusionVector offset);\n'
                      'Manually set gyroscope bias offset (e.g., restore from non-volatile memory on startup).\n'
                      'Source: Fusion/FusionBias.h',
        'tag': 'imu',
    },
}

# Missing RayNeo functions from Feishu docs
rayneo_missing = {
    'GPSIPCHelper.registerGPSInfo': {
        'summary': 'Register RayNeo GPS data stream',
        'description': 'Java: GPSIPCHelper.registerGPSInfo(callback);\n'
                      'Starts GPS data stream from tethered phone to RayNeo glasses via IPCSDK.\n'
                      'Requires: MobileState.isMobileConnected() == true.\n'
                      'GPS JSON fields: mLatitude (double), mLongitude (double), mAltitude (double),\n'
                      '  mSpeed (float), mBearing (float), mProvider (String: "gps"/"network"),\n'
                      '  mTime (long), mHorizontalAccuracyMeters (float).\n'
                      'Source: RayNeo IPCSDK (Feishu docs)',
        'tag': 'gps',
    },
    'GPSIPCHelper.unRegisterGPSInfo': {
        'summary': 'Unregister RayNeo GPS stream',
        'description': 'Java: GPSIPCHelper.unRegisterGPSInfo();\n'
                      'Stops GPS data stream from phone.\n'
                      'Source: RayNeo IPCSDK (Feishu docs)',
        'tag': 'gps',
    },
    'RingIPCHelper.registerRingInfo': {
        'summary': 'Register RayNeo ring data stream',
        'description': 'Java: RingIPCHelper.registerRingInfo(callback);\n'
                      'Starts ring controller data from RayNeo smart ring via IPCSDK.\n'
                      'Ring data JSON: ring_connected (boolean), ring_imu_status (String),\n'
                      '  quaternion: {w: float, x: float, y: float, z: float}.\n'
                      'Control: setRingIMU(boolean), setRingLongClick(), setRingSeparateButton().\n'
                      'Source: RayNeo IPCSDK (Feishu docs)',
        'tag': 'gesture',
    },
    'Algorithm.EnableSlamHeadTracker': {
        'summary': 'Enable RayNeo 6DOF SLAM',
        'description': 'Unity/C#: Algorithm.EnableSlamHeadTracker();\n'
                      'Starts 6DOF SLAM head tracking on RayNeo X2 using VGA camera + IMU fusion.\n'
                      'Poll status with Algorithm.GetSlamStatus() -> SlamState:\n'
                      '  INITIALIZING (warming up), TRACKING_SUCCESS (active), TRACKING_FAIL (lost).\n'
                      'Stop with Algorithm.DisableSlamHeadTracker().\n'
                      'Provides full 6DOF pose (position + rotation) for spatial computing.\n'
                      'Source: RayNeo ARDK for Unity (Feishu docs)',
        'tag': 'spatial',
    },
    'HeadTrackedPoseParams.AwakeDriver': {
        'summary': 'Initialize RayNeo 3DOF driver',
        'description': 'Unity/C#: HeadTrackedPoseParams.AwakeDriver();\n'
                      'Initializes 3DOF head tracking on RayNeo glasses.\n'
                      'Callback: void OnPostUpdate(Pose pose) — receives quaternion orientation.\n'
                      'Reset: void ResetRotation() — resets heading to zero.\n'
                      'Tracks pitch, yaw, roll (no positional tracking).\n'
                      'Android equivalent: SensorManager.getDefaultSensor(TYPE_GAME_ROTATION_VECTOR).\n'
                      'Source: RayNeo ARDK for Unity (Feishu docs)',
        'tag': 'imu',
    },
    'ShareCamera.OpenCamera': {
        'summary': 'Open RayNeo shared camera',
        'description': 'Unity/C#: ShareCamera.OpenCamera(XRCameraType type, XRResolution resolution, '
                      'RawImage display, int frameRate);\n'
                      'Opens camera on RayNeo glasses. Types: VGA (for SLAM), main (for capture).\n'
                      'Uses Android Camera2 API internally. Output to Unity RawImage.\n'
                      'Source: RayNeo ARDK for Unity (Feishu docs)',
        'tag': 'camera',
    },
    'TouchDispatcher': {
        'summary': 'RayNeo temple touch dispatcher',
        'description': 'RayNeo ARDK class that distributes touch events from the temple touchpad.\n'
                      'TempleAction enum: SlideForward, SlideBackward, SwipeUp, SwipeDown,\n'
                      '  TwoFingerTap, LongPress, SingleTap, DoubleTap.\n'
                      'Used with CommonTouchCallback and BaseEventActivity.\n'
                      'Source: RayNeo ARDK (Feishu docs)',
        'tag': 'gesture',
    },
    'BindingPair.updateView': {
        'summary': 'RayNeo binocular view sync',
        'description': 'Java: void updateView();\n'
                      'Syncs view content to both left and right eye displays on RayNeo.\n'
                      'Related: setLeft(), checkIsLeft(), make3DEffect(), make3DEffectForSide().\n'
                      'Classes: BaseMirrorActivity, BaseMirrorFragment, MirrorContainerView.\n'
                      'Source: RayNeo ARDK (Feishu docs)',
        'tag': 'display',
    },
}

# Missing Overpass/Geo functions
geo_missing = {
    'overpass.query': {
        'summary': 'Execute Overpass QL query',
        'description': GEO_ENRICHMENTS['overpass_query'],
        'tag': 'geo',
    },
    'gemini.maps.grounding': {
        'summary': 'Gemini Maps grounding query',
        'description': GEO_ENRICHMENTS['gemini_maps'],
        'tag': 'geo',
    },
    'nominatim.search': {
        'summary': 'Nominatim geocoding search',
        'description': 'Nominatim OSM geocoding: GET https://nominatim.openstreetmap.org/search?format=json&q={search}\n'
                      'Returns JSON array with: lat, lon, boundingbox, osm_type, osm_id, display_name.\n'
                      'Rate limit: 1 request/second. Free to use with attribution.\n'
                      'Usage in AR: Convert place names or addresses to lat/lng coordinates for map overlay.\n'
                      'Source: overpass-turbo nominatim.ts (deep-read 10-geo-maps.md)',
        'tag': 'geo',
    },
}

# Missing headset-utils functions
headset_missing = {
    'ARGlasses.serial': {
        'summary': 'Get glasses serial number (Rust)',
        'description': 'Rust trait: fn serial(&mut self) -> Result<String>;\n'
                      'Part of the ARGlasses trait. Returns device serial number string.\n'
                      'Implementations: RokidAir, NrealAir, NrealLight, MadGazeGlow, GrawoowG530.\n'
                      'Source: headset-utils/src/lib.rs',
        'tag': 'device',
    },
    'ARGlasses.read_event': {
        'summary': 'Read next glasses event (Rust)',
        'description': 'Rust trait: fn read_event(&mut self) -> Result<GlassesEvent>;\n'
                      'Blocks until next event from glasses. GlassesEvent variants:\n'
                      '  AccGyro { accelerometer: Vector3<f32> (m/s²), gyroscope: Vector3<f32> (rad/s), timestamp: u64 (usec) }\n'
                      '  Magnetometer { magnetometer: Vector3<f32> (uT), timestamp: u64 }\n'
                      '  KeyPress(u8), ProximityNear, ProximityFar, AmbientLight(u16), VSync\n'
                      'Coordinate frame: RUB (Right-Up-Back), same as Android sensors.\n'
                      'Source: headset-utils/src/lib.rs',
        'tag': 'imu',
    },
    'ARGlasses.set_display_mode': {
        'summary': 'Set glasses display mode (Rust)',
        'description': 'Rust trait: fn set_display_mode(&mut self, display_mode: DisplayMode) -> Result<()>;\n'
                      'DisplayMode enum: SameOnBoth (1920x1080 mirror), Stereo (3840x1080 SBS),\n'
                      '  HalfSBS (960x540 upscaled), HighRefreshRate (120Hz mirror),\n'
                      '  HighRefreshRateSBS (90Hz SBS).\n'
                      'Source: headset-utils/src/lib.rs',
        'tag': 'display',
    },
    'Connection.start': {
        'summary': 'Start headset-utils connection',
        'description': 'Rust: pub fn start() -> Result<&\'static Connection>;\n'
                      'Global singleton. Detects glasses, creates fusion thread, begins IMU processing.\n'
                      'Connection struct: fusion (Arc<Mutex<Box<dyn Fusion>>>), terminating, thread.\n'
                      'C FFI: extern "C" fn StartConnection() -> i32 (returns 1 on success).\n'
                      'Source: headset-utils/src/lib.rs',
        'tag': 'device',
    },
}

# Missing xreal-webxr functions
webxr_missing = {
    'xreal-webxr.requestDevice': {
        'summary': 'Request XREAL glasses via WebHID',
        'description': 'JavaScript: export async function requestDevice() -> Promise<Glasses|undefined>;\n'
                      'Opens WebHID device picker with vendor filters:\n'
                      '  0x0486 (ASUS/Light), 0x0483 (STMicro/Light Boot), 0x3318 (XREAL Air).\n'
                      'Product IDs: Air=0x0423/0x0424, Light=0x573C/0x5740.\n'
                      'Returns GlassesAir or GlassesLight instance based on productId.\n'
                      'Source: xreal-webxr/common.js',
        'tag': 'device',
    },
    'xreal-webxr.startIMU': {
        'summary': 'Start XREAL IMU via WebHID',
        'description': 'JavaScript: export async function startIMU() -> string;\n'
                      'Starts IMU data polling (100ms interval) and sends W_TOGGLE_IMU [0x01] command.\n'
                      'IMU packet (Device3Packet, 56 bytes): signature[2], temperature[2], timestamp[8],\n'
                      '  angular_multiplier[2], angular_divisor[4], angular_velocity_xyz[3x3bytes],\n'
                      '  acceleration_multiplier[2], acceleration_divisor[4], acceleration_xyz[3x3bytes],\n'
                      '  magnetic_multiplier[2], magnetic_divisor[4], magnetic_xyz[3x2bytes], checksum[4].\n'
                      'Protocol: HEAD=0xfd, 64-byte HID reports, CRC32 checksum, msgId at offset 15.\n'
                      'Source: xreal-webxr/js_air/manager.js + protocol.js',
        'tag': 'imu',
    },
    'xreal-webxr.setBrightness': {
        'summary': 'Set XREAL brightness via WebHID',
        'description': 'JavaScript: export async function setBrightness(brightness_int: number) -> Uint8Array;\n'
                      'Sets display brightness on XREAL Air glasses. Uses brightInt2Bytes() conversion.\n'
                      'Protocol: Sends W_BRIGHTNESS message via 64-byte HID report.\n'
                      'Source: xreal-webxr/js_air/manager.js',
        'tag': 'display',
    },
}

# Monado missing functions
monado_missing = {
    'xrt_device.get_view_poses': {
        'summary': 'Get per-eye view poses',
        'description': 'C signature: xrt_result_t (*get_view_poses)(struct xrt_device *xdev, '
                      'const struct xrt_vec3 *default_eye_relation, int64_t at_timestamp_ns, '
                      'enum xrt_view_type view_type, uint32_t view_count, '
                      'struct xrt_space_relation *out_head_relation, struct xrt_fov *out_fovs, '
                      'struct xrt_pose *out_poses);\n'
                      'Gets per-eye view poses for stereo rendering. Returns head relation + per-eye FOV + poses.\n'
                      'Maps to OpenXR xrLocateViews. view_type: STEREO, MONO, etc.\n'
                      'Source: monado/src/xrt/include/xrt/xrt_device.h',
        'tag': 'spatial',
    },
    'xrt_device.get_visibility_mask': {
        'summary': 'Get lens visibility mask',
        'description': 'C signature: xrt_result_t (*get_visibility_mask)(struct xrt_device *xdev, '
                      'enum xrt_visibility_mask_type type, uint32_t view_index, '
                      'struct xrt_visibility_mask **out_mask);\n'
                      'Gets visibility mask for rendering optimization. Mask types define hidden/visible areas '
                      'of the lens to avoid rendering pixels not visible to user.\n'
                      'Maps to OpenXR XR_KHR_visibility_mask extension.\n'
                      'Source: monado/src/xrt/include/xrt/xrt_device.h',
        'tag': 'spatial',
    },
    'xrt_prober.probe': {
        'summary': 'Monado device probe/discovery',
        'description': 'C signature: xrt_result_t (*probe)(struct xrt_prober *xp);\n'
                      'Probes for XR devices. Monado supports 38+ device drivers including:\n'
                      'xreal_air (VID=0x3318), rokid, wmr, survive, rift_s, psvr, psvr2, realsense, depthai,\n'
                      'ultraleap_v2/v5, north_star, opengloves, simulated, qwerty, and more.\n'
                      'After probing, use lock_list/create_system to access discovered devices.\n'
                      'Source: monado/src/xrt/include/xrt/xrt_prober.h',
        'tag': 'device',
    },
}

# Build new path entries
all_missing = {}
all_missing.update({f'Fusion/{k}': v for k, v in fusion_missing.items()})
all_missing.update({f'rayneo-sdk/{k}': v for k, v in rayneo_missing.items()})
all_missing.update({f'geo/{k}': v for k, v in geo_missing.items()})
all_missing.update({f'headset-utils/{k}': v for k, v in headset_missing.items()})
all_missing.update({f'xreal-webxr/{k}': v for k, v in webxr_missing.items()})
all_missing.update({f'Monado/{k}': v for k, v in monado_missing.items()})

added_count = 0
for func_path, info in all_missing.items():
    tag = info['tag']
    path_key = f'/api/v1/{tag}/{func_path}'
    
    # Check if path already exists
    if path_key not in paths:
        op_id = f"{tag}_{func_path.replace('/', '_').replace('.', '_').replace('-', '_')}"
        paths[path_key] = {
            'get': {
                'operationId': op_id,
                'summary': info['summary'],
                'description': info['description'],
                'tags': [tag],
                'responses': {
                    '200': {
                        'description': 'Success',
                        'content': {
                            'application/json': {
                                'schema': {'type': 'object'}
                            }
                        }
                    }
                }
            }
        }
        added_count += 1

print(f"Added {added_count} new paths")
print(f"Total paths: {len(paths)}")

# ============================================================
# 7. Write enriched spec
# ============================================================

spec['paths'] = paths
spec['info']['description'] = (
    'Comprehensive REST-like documentation API for the AR Glasses Master SDK. '
    'Covers 27+ repositories, 500+ functions across 12 domains: Display, IMU, Camera, Audio, BLE, '
    'Gesture, Spatial Computing, ML/AI, GPS, Device Management, StardustXR 3D, and Geo/Maps Intelligence. '
    'ENRICHED with deep-read documentation from all source repositories including: '
    'Fusion AHRS C function signatures, XRLinuxDriver USB VID/PIDs, StardustXR KDL protocol, '
    'Monado xrt_device methods, RayNeo Feishu SDK docs, Overpass QL query templates, '
    'Gemini Maps grounding API, headset-utils Rust traits, and xreal-webxr WebHID protocol.'
)

# Custom YAML representer for multiline strings
def str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_representer)

output_path = '/tmp/ar-glasses-old/openapi-enriched.yaml'
with open(output_path, 'w') as f:
    yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, width=120, sort_keys=False)

print(f"\nWritten enriched spec to {output_path}")

# Count stats
import subprocess
result = subprocess.run(['wc', '-l', output_path], capture_output=True, text=True)
print(f"Output file: {result.stdout.strip()}")
