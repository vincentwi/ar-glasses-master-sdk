package com.arglasses.sdk.core

import android.content.Context
import android.graphics.Bitmap

/**
 * GlassesClient — The unified interface for all AR glasses devices.
 *
 * This is the primary abstraction layer. Every glasses device (RayNeo, XREAL,
 * Meta, Rokid, Brilliant Frame, Viture, Vuzix) implements this interface.
 *
 * Architecture based on:
 * - xg-glass-sdk GlassesClient (HKUST SPARK Lab)
 * - headset-utils ARGlasses trait (Rust)
 * - MentraOS AppSession API (TypeScript)
 * - RayNeo ARDK BinocularDisplay/FocusHolder pattern
 *
 * Usage:
 * ```kotlin
 * val client = GlassesClientFactory.create(DeviceType.RAYNEO_X3)
 * client.connect(context, myCallback)
 * ```
 *
 * @see GlassesCallback for lifecycle events
 * @see GlassesInfo for device capabilities discovery
 * @see DeviceType for supported device enumeration
 */
interface GlassesClient {

    // ═══════════════════════════════════════════════════════
    // CONNECTION LIFECYCLE
    // ═══════════════════════════════════════════════════════

    /**
     * Connect to the glasses device.
     *
     * For BLE devices (Frame, Meta, Even G2): initiates BLE scan and GATT connection.
     * For USB devices (RayNeo, XREAL, Viture): opens USB accessory connection.
     * For WiFi devices (RayNeo X2): connects via WiFi Direct/P2P.
     *
     * Source patterns:
     * - xg-glass-sdk: GlassesClient.connect(context, callback)
     * - headset-utils: ARGlasses::connect() -> Result<(), Error>
     * - MentraOS: AppSession constructor with WebSocket
     *
     * @param context Android Context for system service access
     * @param callback Lifecycle event callbacks
     * @return true if connection attempt started, false if device unavailable
     */
    fun connect(context: Context, callback: GlassesCallback): Boolean

    /**
     * Disconnect from glasses and release all resources.
     * Stops all active streams (IMU, camera, audio).
     * Safe to call multiple times.
     */
    fun disconnect()

    /**
     * Check if currently connected to glasses.
     * @return true if connected and ready for commands
     */
    fun isConnected(): Boolean

    /**
     * Get device information and capabilities.
     * Only valid after onConnected callback.
     *
     * @return GlassesInfo with device capabilities, or null if not connected
     */
    fun getDeviceInfo(): GlassesInfo?

    // ═══════════════════════════════════════════════════════
    // DISPLAY
    // Based on: RayNeo ARDK BindingPair/BaseMirrorActivity,
    //           xg-glass-sdk display(), MentraOS LayoutManager
    // ═══════════════════════════════════════════════════════

    /**
     * Get the display controller for this device.
     * Returns null if device has no display (e.g., Mentra Live, Meta Ray-Ban).
     *
     * For binocular devices (RayNeo, XREAL), automatically handles
     * dual-eye rendering via the BindingPair pattern from RayNeo ARDK:
     * - BaseMirrorActivity: Activity-level sight merging
     * - BaseMirrorFragment: Fragment-level sight merging
     * - MirrorContainerView: View-level composition
     * - FToast/FDialog: Universal toast/dialog with merging
     *
     * @return DisplayController or null
     */
    fun display(): DisplayController?

    // ═══════════════════════════════════════════════════════
    // CAMERA
    // Based on: xg-glass-sdk capturePhoto(), RayNeo Camera2 API,
    //           Meta DAT SDK, Brilliant Frame camera
    // ═══════════════════════════════════════════════════════

    /**
     * Get the camera controller.
     * Returns null if device has no camera (e.g., Even G2, Viture).
     *
     * Implementations:
     * - RayNeo: Android Camera2 API (16MP RGB)
     * - Meta: DAT SDK photo capture (12MP)
     * - Frame: BLE frame.camera Lua API (low-res AI sensor)
     * - xg-glass-sdk: CaptureOptions with resolution/format/flash
     *
     * @return CameraController or null
     */
    fun camera(): CameraController?

    // ═══════════════════════════════════════════════════════
    // AUDIO (MIC + SPEAKER)
    // Based on: xg-glass-sdk playAudio/startMicrophone,
    //           MentraOS AudioManager, RayNeo ARDK audio modes
    // ═══════════════════════════════════════════════════════

    /**
     * Get the audio controller (microphone + speaker).
     *
     * RayNeo X2 audio capture modes (from ARDK):
     * - MODE_2MIC_VOICE_RECOGNITION: 2-mic beamforming for ASR
     * - MODE_2MIC_A2DP_REC: 2-mic + Bluetooth audio
     * - MODE_1MIC_VOICE_COMMUNICATION: single mic for calls
     * - MODE_1MIC_MUSIC_REC: single mic + music mix
     *
     * RayNeo X3 adds:
     * - MODE_THIRD_PARTY_VOICE_COMMUNICATION: for 3rd-party calls
     *
     * @return AudioController or null
     */
    fun audio(): AudioController?

    // ═══════════════════════════════════════════════════════
    // SENSORS (IMU, GPS, etc.)
    // Based on: xioTechnologies/Fusion AHRS algorithm,
    //           XRLinuxDriver imu.h, headset-utils Fusion trait,
    //           RayNeo ARDK SensorManager
    // ═══════════════════════════════════════════════════════

    /**
     * Get the sensor controller (IMU, GPS, etc.).
     *
     * IMU fusion uses xioTechnologies/Fusion library internally:
     * - AHRS algorithm with adaptive gain
     * - Acceleration rejection (filters out linear acceleration)
     * - Magnetic rejection (filters out magnetic distortion)
     * - Configurable conventions: NWU, ENU, NED
     *
     * Sensor rates (from XRLinuxDriver):
     * - XREAL: 1000 Hz native
     * - RayNeo: 400 Hz native
     * - Rokid: 400 Hz native
     * - Viture: 60 Hz (lower due to USB report rate)
     *
     * @return SensorController (always available — all glasses have IMU)
     */
    fun sensors(): SensorController

    // ═══════════════════════════════════════════════════════
    // INPUT (Touch, Gesture, Voice)
    // Based on: RayNeo ARDK TouchDispatcher/TempleAction,
    //           xg-glass-sdk TouchCallback, MentraOS EventManager
    // ═══════════════════════════════════════════════════════

    /**
     * Get the input controller (touch, gesture, voice commands).
     *
     * Input sources vary by device:
     * - RayNeo: Temple touchpad (tap/double-tap/long-press/swipe 4-dir)
     *           + shortcut button (right temple)
     *           + voice (ASR)
     *           + Apple Watch gestures (pinch-to-confirm, twist-to-select)
     * - XREAL: Ring controller, phone controller
     * - Meta: Temple button, voice ("Hey Meta")
     * - Frame: Tap gesture on frame
     * - Vuzix: Touchpad (TrackballEvent), voice (Speech SDK)
     * - Rokid: Touch ring on temple
     *
     * RayNeo TempleAction types (from ARDK BaseEventActivity):
     * - TempleAction.SlideForward / SlideBackward
     * - TempleAction.SlideUp / SlideDown (X3 only)
     * - TempleAction.SingleTap / DoubleTap / LongClick
     * - TempleAction.TwoFingerTap (X3 only)
     *
     * @return InputController
     */
    fun input(): InputController
}

/**
 * Factory for creating device-specific GlassesClient implementations.
 *
 * Source: xg-glass-sdk pattern with GlassesClientFactory
 */
object GlassesClientFactory {

    /**
     * Create a GlassesClient for the specified device type.
     *
     * @param deviceType Target device
     * @return GlassesClient implementation for that device
     */
    fun create(deviceType: DeviceType): GlassesClient {
        return when (deviceType) {
            DeviceType.RAYNEO_X3 -> TODO("RayNeoX3Client()")
            DeviceType.RAYNEO_X2 -> TODO("RayNeoX2Client()")
            DeviceType.XREAL -> TODO("XrealClient()")
            DeviceType.META -> TODO("MetaClient()")
            DeviceType.FRAME -> TODO("FrameClient()")
            DeviceType.ROKID -> TODO("RokidClient()")
            DeviceType.VITURE -> TODO("VitureClient()")
            DeviceType.VUZIX -> TODO("VuzixClient()")
            DeviceType.SIMULATOR -> TODO("SimulatorClient()")
        }
    }

    /**
     * Auto-detect connected glasses device.
     * Scans USB, BLE, and WiFi for known device signatures.
     *
     * Device detection methods:
     * - USB: VID/PID matching (from XRLinuxDriver devices.h):
     *   - XREAL: VID 0x3318, PIDs 0x0424/0x0428/0x0432/0x0426
     *   - Viture: VID 0x35CA, PIDs 0x1011-0x101D
     *   - Rokid: VID 0x04D2, PIDs 0x162F/0x1630
     *   - RayNeo: VID 0x35CA, PIDs 0x2011-0x2022
     * - BLE: Service UUID matching
     * - WiFi: mDNS/DNS-SD discovery
     *
     * @param context Android Context
     * @return Detected DeviceType or null
     */
    fun autoDetect(context: Context): DeviceType? {
        TODO("Auto-detection via USB VID/PID + BLE scan")
    }
}
