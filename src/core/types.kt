package com.arglasses.sdk.core

/**
 * Enumeration of all supported AR glasses devices.
 *
 * USB VID/PID values sourced from XRLinuxDriver devices.h:
 * - These are the actual USB identifiers used for device detection
 * - Each device has unique product IDs per model variant
 *
 * @property displayName Human-readable device name
 * @property usbVendorId USB Vendor ID (0 if BLE-only device)
 * @property hasBinocularDisplay Whether device needs dual-eye rendering
 * @property hasCamera Whether device has a camera
 * @property hasMicrophone Whether device has microphone(s)
 * @property hasSpeaker Whether device has speaker(s)
 * @property maxDoF Maximum degrees of freedom (3 or 6)
 * @property hasSLAM Whether device supports SLAM/world-locked content
 */
enum class DeviceType(
    val displayName: String,
    val usbVendorId: Int,
    val hasBinocularDisplay: Boolean,
    val hasCamera: Boolean,
    val hasMicrophone: Boolean,
    val hasSpeaker: Boolean,
    val maxDoF: Int,
    val hasSLAM: Boolean
) {
    /**
     * RayNeo X3 Pro — Snapdragon AR1, 6DoF SLAM, 6000 nits MicroLED
     * Canvas: 640x480 per eye
     * Input: Temple touchpad + shortcut button + voice + Apple Watch
     * Source: RayNeo ARDK, hermes-glasses/OpenClaw app
     */
    RAYNEO_X3(
        displayName = "RayNeo X3 Pro",
        usbVendorId = 0x35CA,  // From XRLinuxDriver rayneo.h
        hasBinocularDisplay = true,
        hasCamera = true,
        hasMicrophone = true,
        hasSpeaker = true,
        maxDoF = 6,
        hasSLAM = true
    ),

    /**
     * RayNeo X2 — Snapdragon XR2, 6DoF SLAM, binocular MicroLED
     * Canvas: 640x480 per eye
     * Source: RayNeo ARDK, XRLinuxDriver (supported device)
     */
    RAYNEO_X2(
        displayName = "RayNeo X2",
        usbVendorId = 0x35CA,
        hasBinocularDisplay = true,
        hasCamera = true,
        hasMicrophone = true,
        hasSpeaker = true,
        maxDoF = 6,
        hasSLAM = true
    ),

    /**
     * XREAL Air/One series — X1 chip, Micro-OLED, tethered display
     * VID: 0x3318 (from XRLinuxDriver/imu-inspector)
     * PIDs: 0x0424 (Air), 0x0428 (Air 2), 0x0432 (Air 2 Ultra), 0x0426 (One)
     */
    XREAL(
        displayName = "XREAL",
        usbVendorId = 0x3318,
        hasBinocularDisplay = true,
        hasCamera = false,  // Air 2 Ultra has sensing, most don't
        hasMicrophone = false,
        hasSpeaker = true,
        maxDoF = 3,  // 6DoF with Eye accessory
        hasSLAM = false
    ),

    /**
     * Meta Ray-Ban / Ray-Ban Display
     * Connection: BLE (DAT SDK)
     * Source: xg-glass-sdk meta implementation
     */
    META(
        displayName = "Meta Ray-Ban",
        usbVendorId = 0,  // BLE only
        hasBinocularDisplay = false,  // Ray-Ban Display has display, original doesn't
        hasCamera = true,
        hasMicrophone = true,
        hasSpeaker = true,
        maxDoF = 0,
        hasSLAM = false
    ),

    /**
     * Brilliant Labs Frame — nRF52840, Lua scripting, BLE, micro-OLED
     * Source: xg-glass-sdk frame implementation, frame-codebase (TFLite Micro)
     */
    FRAME(
        displayName = "Brilliant Frame",
        usbVendorId = 0,  // BLE only
        hasBinocularDisplay = false,  // Monocular micro-OLED
        hasCamera = true,  // AI-optimized low-power sensor
        hasMicrophone = false,
        hasSpeaker = false,
        maxDoF = 0,
        hasSLAM = false
    ),

    /**
     * Rokid Max/Air — Micro-OLED birdbath, tethered
     * VID: 0x04D2 (from XRLinuxDriver)
     * PIDs: 0x162F (Max), 0x1630 (Air)
     */
    ROKID(
        displayName = "Rokid",
        usbVendorId = 0x04D2,
        hasBinocularDisplay = true,
        hasCamera = false,
        hasMicrophone = false,
        hasSpeaker = true,
        maxDoF = 3,
        hasSLAM = false
    ),

    /**
     * Viture Luma Pro — Sony Micro-OLED, electrochromic dimming
     * VID: 0x35CA (from XRLinuxDriver)
     * PIDs: 0x1011 (One), 0x101A (Luma), 0x101C (Luma Pro), 0x101D (Ultra)
     */
    VITURE(
        displayName = "Viture",
        usbVendorId = 0x35CA,
        hasBinocularDisplay = true,
        hasCamera = true,  // Luma Pro has front camera
        hasMicrophone = false,
        hasSpeaker = true,
        maxDoF = 3,
        hasSLAM = false
    ),

    /**
     * Vuzix Blade 2 — DLP waveguide, monocular, enterprise
     * Source: Blade_2_Template_App, HUD ActionMenu API v2.9
     */
    VUZIX(
        displayName = "Vuzix Blade 2",
        usbVendorId = 0,  // WiFi/USB but no standard VID
        hasBinocularDisplay = false,  // Monocular
        hasCamera = true,
        hasMicrophone = true,
        hasSpeaker = true,
        maxDoF = 3,
        hasSLAM = false
    ),

    /**
     * Software simulator for development without hardware.
     * Source: xg-glass-sdk simulator implementation
     */
    SIMULATOR(
        displayName = "Simulator",
        usbVendorId = 0,
        hasBinocularDisplay = true,
        hasCamera = true,
        hasMicrophone = true,
        hasSpeaker = true,
        maxDoF = 6,
        hasSLAM = true
    )
}

/**
 * Device information and runtime capabilities.
 *
 * Populated after successful connection. Contains both static device
 * info and dynamic state (battery level, firmware version).
 *
 * Source patterns:
 * - xg-glass-sdk: GlassesInfo data class
 * - XRLinuxDriver: device_properties_type struct
 * - headset-utils: GlassesInfo struct (Rust)
 */
data class GlassesInfo(
    /** Human-readable device name */
    val deviceName: String,

    /** Device type enum */
    val deviceType: DeviceType,

    /** Firmware/OS version string */
    val firmwareVersion: String,

    /** Battery level 0-100, or -1 if not available */
    val batteryLevel: Int,

    /** Display resolution per eye (width x height) */
    val displayResolution: Resolution?,

    /** Display field of view in degrees
     *  Source: XRLinuxDriver device_properties_type.fov
     *  Values: XREAL=46°, Viture=43°, Rokid=50°, RayNeo=30° */
    val displayFovDegrees: Float?,

    /** Connection type used */
    val connectionType: ConnectionType,

    /** Detailed capability flags */
    val capabilities: DeviceCapabilities
)

/**
 * Display resolution.
 * Canvas resolution for RayNeo is always 640x480 per eye.
 */
data class Resolution(val width: Int, val height: Int)

/** Connection transport type */
enum class ConnectionType { BLE, USB, WIFI, SIMULATOR }

/**
 * Detailed device capability flags.
 * Queried after connection to determine what APIs are available.
 */
data class DeviceCapabilities(
    val hasDisplay: Boolean,
    val hasCamera: Boolean,
    val hasMicrophone: Boolean,
    val hasSpeaker: Boolean,
    val hasIMU: Boolean,
    val hasGPS: Boolean,       // Usually via phone relay (RayNeo IPCSDK)
    val hasSLAM: Boolean,
    val hasHandTracking: Boolean,
    val hasEyeTracking: Boolean,
    val hasFaceDetection: Boolean,
    val hasPlaneDetection: Boolean,
    val maxDoF: Int,           // 0, 3, or 6
    val imuSampleRateHz: Int,  // Native IMU rate
    val supportsBinocular: Boolean,
    val supportsElectrochromic: Boolean
)

// ═══════════════════════════════════════════════════════
// IMU DATA TYPES
// Based on: xioTechnologies/Fusion structs, XRLinuxDriver imu_pose_type
// ═══════════════════════════════════════════════════════

/**
 * 3D vector for accelerometer, gyroscope, magnetometer data.
 * Source: Fusion FusionVector struct
 */
data class Vector3(val x: Float, val y: Float, val z: Float)

/**
 * Quaternion for orientation representation.
 * Source: Fusion FusionQuaternion, XRLinuxDriver imu_quat_type
 * Convention: Hamilton (w, x, y, z)
 */
data class Quaternion(val w: Float, val x: Float, val y: Float, val z: Float)

/**
 * Euler angles in degrees.
 * Source: Fusion FusionEuler
 * Convention: configurable (NWU, ENU, NED) via FusionConvention
 *
 * @property roll Rotation around forward axis (degrees)
 * @property pitch Rotation around right axis (degrees)
 * @property yaw Rotation around up axis (degrees)
 */
data class EulerAngles(val roll: Float, val pitch: Float, val yaw: Float)

/**
 * Complete IMU data sample with raw + fused values.
 *
 * Raw values come directly from device.
 * Fused values computed by Fusion AHRS algorithm:
 * - Startup gain ramping (initial high gain decreases to steady-state)
 * - Acceleration rejection (filters linear acceleration from gravity)
 * - Magnetic rejection (filters magnetic distortion from true north)
 *
 * @property timestamp Sample timestamp in nanoseconds
 * @property accelerometer Raw accelerometer (m/s²)
 * @property gyroscope Raw gyroscope (rad/s)
 * @property magnetometer Raw magnetometer (µT), null if 6-axis only
 * @property quaternion Fused orientation quaternion
 * @property euler Fused Euler angles (degrees)
 */
data class IMUData(
    val timestamp: Long,
    val accelerometer: Vector3,
    val gyroscope: Vector3,
    val magnetometer: Vector3?,
    val quaternion: Quaternion,
    val euler: EulerAngles
)

// ═══════════════════════════════════════════════════════
// INPUT TYPES
// Based on: RayNeo ARDK TempleAction, xg-glass-sdk TouchEvent
// ═══════════════════════════════════════════════════════

/**
 * Touch/gesture event from glasses input surface.
 *
 * RayNeo TempleAction mapping:
 * - TAP → TempleAction.SingleTap
 * - DOUBLE_TAP → TempleAction.DoubleTap
 * - LONG_PRESS → TempleAction.LongClick
 * - SWIPE_FORWARD → TempleAction.SlideForward
 * - SWIPE_BACKWARD → TempleAction.SlideBackward
 * - SWIPE_UP → TempleAction.SlideUp (X3 only)
 * - SWIPE_DOWN → TempleAction.SlideDown (X3 only)
 * - TWO_FINGER_TAP → TempleAction.TwoFingerTap (X3 only)
 */
enum class GestureType {
    TAP, DOUBLE_TAP, LONG_PRESS,
    SWIPE_FORWARD, SWIPE_BACKWARD, SWIPE_UP, SWIPE_DOWN,
    TWO_FINGER_TAP,
    BUTTON_SHORT_PRESS, BUTTON_LONG_PRESS
}

data class GestureEvent(
    val type: GestureType,
    val timestamp: Long,
    val x: Float = 0f,
    val y: Float = 0f
)

// ═══════════════════════════════════════════════════════
// DISPLAY TYPES
// Based on: RayNeo ARDK BaseMirrorActivity/BindingPair,
//           MentraOS LayoutManager, xg-glass-sdk DisplayOptions
// ═══════════════════════════════════════════════════════

enum class TextPosition { TOP_LEFT, TOP_CENTER, TOP_RIGHT, CENTER, BOTTOM_LEFT, BOTTOM_CENTER, BOTTOM_RIGHT }
enum class TextColor { WHITE, GREEN, CYAN, YELLOW, RED }

/**
 * MentraOS Layout Types (from LayoutManager):
 * - TextWall: Full-screen text display
 * - ReferenceCard: Card with optional image
 * - ColumnsCard: Multi-column layout
 * - DoubleTextWall: Two text areas
 * - BitmapView: Full-screen image
 * - Split: Side-by-side panels
 * - Empty: Clear display
 */
enum class LayoutType {
    TEXT_WALL, REFERENCE_CARD, COLUMNS_CARD,
    DOUBLE_TEXT_WALL, BITMAP_VIEW, SPLIT, EMPTY
}
