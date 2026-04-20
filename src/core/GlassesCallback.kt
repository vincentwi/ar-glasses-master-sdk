package com.arglasses.sdk.core

/**
 * Callback interface for glasses lifecycle and data events.
 *
 * Implement this to receive connection state changes, input events,
 * sensor data, and media captures from the glasses.
 *
 * Source patterns:
 * - xg-glass-sdk: GlassesCallback
 * - MentraOS: EventManager stream subscriptions
 * - RayNeo ARDK: BaseEventActivity + TempleAction flow
 */
interface GlassesCallback {

    // ── Connection Lifecycle ──────────────────────────────

    /** Called when successfully connected to glasses. */
    fun onConnected(info: GlassesInfo)

    /** Called when disconnected from glasses.
     *  @param reason Why the disconnection occurred */
    fun onDisconnected(reason: DisconnectReason)

    /** Called on connection or runtime errors.
     *  @param error The error that occurred */
    fun onError(error: GlassesError)

    // ── Device State ─────────────────────────────────────

    /** Battery level changed.
     *  @param level Battery percentage 0-100 */
    fun onBatteryChanged(level: Int) {}

    // ── Input Events ─────────────────────────────────────

    /** Gesture detected on temple touchpad or button.
     *  See GestureType for full mapping to RayNeo TempleAction.
     *  @param gesture The detected gesture */
    fun onGesture(gesture: GestureEvent) {}

    /** Voice command recognized (if ASR is active).
     *  @param text Recognized text
     *  @param confidence Confidence score 0.0-1.0 */
    fun onVoiceCommand(text: String, confidence: Float) {}

    // ── Sensor Data ──────────────────────────────────────

    /** New IMU sample available.
     *  Rate depends on device: XREAL=1000Hz, RayNeo=400Hz, Rokid=400Hz, Viture=60Hz
     *  @param data Fused IMU data (raw + orientation) */
    fun onIMUData(data: IMUData) {}

    /** GPS location update (from connected phone via IPC).
     *  Requires: RayNeo AR companion app with Location permission.
     *  Source: RayNeo IPCSDK GPS streaming.
     *  @param lat Latitude
     *  @param lon Longitude
     *  @param accuracy Accuracy in meters */
    fun onLocationUpdate(lat: Double, lon: Double, accuracy: Float) {}

    // ── Media Captures ───────────────────────────────────

    /** Photo captured from glasses camera.
     *  @param photo The captured image */
    fun onPhotoCaptured(photo: android.graphics.Bitmap) {}

    /** Audio transcription available (from MentraOS-style ASR).
     *  @param text Transcribed text
     *  @param isFinal Whether this is a final or interim result */
    fun onTranscription(text: String, isFinal: Boolean) {}
}

/**
 * Reasons for disconnection.
 */
enum class DisconnectReason {
    USER_REQUESTED,    // Client called disconnect()
    DEVICE_POWERED_OFF,
    OUT_OF_RANGE,      // BLE device went out of range
    USB_DISCONNECTED,  // USB cable unplugged
    ERROR,             // Unexpected error
    TIMEOUT            // Connection timeout
}

/**
 * Error types that can occur during glasses operations.
 */
sealed class GlassesError(val message: String) {
    class ConnectionFailed(msg: String) : GlassesError(msg)
    class DeviceNotFound(msg: String) : GlassesError(msg)
    class PermissionDenied(msg: String) : GlassesError(msg)
    class DisplayError(msg: String) : GlassesError(msg)
    class CameraError(msg: String) : GlassesError(msg)
    class SensorError(msg: String) : GlassesError(msg)
    class Timeout(msg: String) : GlassesError(msg)
    class Unknown(msg: String) : GlassesError(msg)
}
