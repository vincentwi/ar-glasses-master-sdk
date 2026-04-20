package com.arglasses.sdk.core

import android.graphics.Bitmap
import android.view.View
import android.view.ViewGroup

/**
 * Display controller — unified API for rendering on glasses displays.
 *
 * Handles the complexity of binocular rendering automatically.
 * For RayNeo devices, this wraps the ARDK BindingPair pattern:
 *
 * ```
 * ┌─────────────────┬─────────────────┐
 * │   Left Eye      │   Right Eye     │
 * │   (left panel)  │   (right panel) │
 * │                 │                 │
 * │   Same content  │   Same content  │
 * │   mirrored      │   mirrored      │
 * └─────────────────┴─────────────────┘
 * ```
 *
 * Key components from RayNeo ARDK:
 * - BindingPair<T>: Manages left+right ViewBinding pair
 *   - updateView { binding -> ... }: Updates both eyes simultaneously
 *   - setLeft { binding -> ... }: Updates left eye only (for events)
 *   - checkIsLeft(binding): Returns true if binding is the left one
 *
 * - BaseMirrorActivity: Activity with automatic binocular mirroring
 * - BaseMirrorFragment: Fragment with automatic mirroring
 * - MirrorContainerView: View-level composition mirroring
 * - BaseMirrorContainerView: View-level inheritance mirroring
 * - FToast: Toast with binocular fusion
 * - FDialog: Dialog with binocular fusion
 *
 * For TapLink X3 pattern (browser):
 * - DualWebViewGroup: Single WebView → dual-eye clip rendering
 *   - Left eye: Direct WebView with clip bounds
 *   - Right eye: SurfaceView with pixel-copied preview
 *
 * Source: RayNeo ARDK, TapLink X3 DualWebViewGroup, xg-glass-sdk
 */
interface DisplayController {

    /**
     * Show text on the glasses display.
     *
     * For binocular devices: text is automatically mirrored to both eyes.
     * Uses green/cyan text on black background for waveguide visibility.
     *
     * RayNeo design rules (from Feishu docs):
     * - Canvas is always 640x480 per eye
     * - Safety margin: 16-30px black border on all edges
     * - Minimum line width: 2px (1px causes waveguide artifacts)
     * - Virtual image distance: 1.7m-5m comfort zone
     *
     * @param text Text to display (max ~50 chars for comfort)
     * @param position Where to place the text
     * @param color Text color (green/cyan recommended for waveguide)
     * @param sizeSp Font size in SP (16-24 recommended)
     */
    fun showText(
        text: String,
        position: TextPosition = TextPosition.CENTER,
        color: TextColor = TextColor.GREEN,
        sizeSp: Float = 20f
    )

    /**
     * Show a bitmap image on the glasses display.
     *
     * For binocular devices: image is mirrored to both eyes.
     * Image will be scaled to fit within the display canvas.
     *
     * @param bitmap Image to display
     * @param position Where to place the image
     */
    fun showImage(bitmap: Bitmap, position: TextPosition = TextPosition.CENTER)

    /**
     * Show a custom Android View on the glasses display.
     *
     * For binocular devices (RayNeo): wraps the view in MirrorContainerView
     * for automatic dual-eye rendering.
     *
     * @param view The Android View to display
     */
    fun showView(view: View)

    /**
     * Apply 3D parallax effect to a view.
     *
     * Creates binocular parallax pseudo-3D by offsetting the left and right
     * eye views slightly. From RayNeo ARDK:
     * - make3DEffect(view, depthPx): Applies to both sides
     * - make3DEffectForSide(view, depthPx, isLeft): Per-eye control
     *
     * @param view Target view
     * @param depthPx Parallax offset in pixels (positive = closer, negative = farther)
     */
    fun apply3DEffect(view: View, depthPx: Int)

    /**
     * Clear the display (show black/transparent).
     */
    fun clear()

    /**
     * Set display brightness.
     * @param level 0-100 brightness percentage
     */
    fun setBrightness(level: Int)

    /**
     * Get the display canvas dimensions.
     * RayNeo: always 640x480 per eye.
     * XREAL: 1920x1080 per eye.
     */
    fun getCanvasSize(): Resolution
}

/**
 * Camera controller — unified photo/video capture API.
 *
 * Source implementations:
 * - RayNeo: Android Camera2 API (standard Android)
 * - Meta: DAT SDK (proprietary BLE protocol)
 * - Frame: BLE frame.camera Lua command
 * - xg-glass-sdk: CaptureOptions pattern
 */
interface CameraController {

    /**
     * Capture a single photo.
     * @param callback Called with the captured bitmap
     */
    fun capturePhoto(callback: (Bitmap) -> Unit)

    /**
     * Start continuous video frame capture.
     * Each frame is delivered to the callback.
     * @param callback Called with each video frame
     * @param fps Target frames per second (device may limit)
     */
    fun startVideoStream(callback: (Bitmap) -> Unit, fps: Int = 30)

    /** Stop video streaming. */
    fun stopVideoStream()

    /** Check if video is currently streaming. */
    fun isStreaming(): Boolean
}

/**
 * Audio controller — microphone and speaker management.
 *
 * RayNeo audio capture modes (from ARDK CapabilitiesAPI Feishu docs):
 *
 * X2 modes:
 * - MODE_2MIC_VOICE_RECOGNITION: 2-mic beamforming for ASR (best quality)
 * - MODE_2MIC_A2DP_REC: 2-mic + Bluetooth music recording
 * - MODE_1MIC_VOICE_COMMUNICATION: Single mic, AEC enabled (for calls)
 * - MODE_1MIC_MUSIC_REC: Single mic + system audio mix
 *
 * X3 modes (all X2 modes plus):
 * - MODE_THIRD_PARTY_VOICE_COMMUNICATION: For 3rd-party VoIP apps
 *
 * Source: RayNeo ARDK, xg-glass-sdk AudioSource, MentraOS AudioManager
 */
interface AudioController {

    /** Play audio through glasses speakers.
     *  @param audioData Raw PCM audio bytes
     *  @param sampleRate Sample rate in Hz (typically 16000 or 44100)
     */
    fun playAudio(audioData: ByteArray, sampleRate: Int = 16000)

    /** Speak text through TTS on glasses.
     *  Source: xg-glass-sdk AudioSource.TTS pattern
     *  @param text Text to speak
     *  @param language BCP-47 language tag (default: en-US)
     */
    fun speak(text: String, language: String = "en-US")

    /** Start microphone recording/streaming.
     *  @param callback Called with audio chunks
     *  @param mode Recording mode (device-specific)
     */
    fun startMicrophone(
        callback: (ByteArray) -> Unit,
        mode: AudioCaptureMode = AudioCaptureMode.VOICE_RECOGNITION
    )

    /** Stop microphone recording. */
    fun stopMicrophone()
}

enum class AudioCaptureMode {
    VOICE_RECOGNITION,               // Best for ASR
    VOICE_COMMUNICATION,             // Best for calls (AEC enabled)
    MUSIC_RECORDING,                 // Captures system audio mix
    TWO_MIC_BEAMFORMING,            // 2-mic directional (RayNeo X2/X3)
    THIRD_PARTY_VOICE_COMMUNICATION  // For VoIP apps (RayNeo X3 only)
}

/**
 * Sensor controller — IMU, GPS, and other sensor data.
 *
 * IMU fusion powered by xioTechnologies/Fusion library:
 * - AHRS algorithm: Madgwick-derived with adaptive gain
 * - Configurable sample rate per device
 * - Acceleration rejection with configurable threshold
 * - Magnetic rejection with configurable threshold
 * - Convention: NWU (default), ENU, NED
 *
 * Source: xioTechnologies/Fusion, XRLinuxDriver imu.c, headset-utils Fusion trait
 */
interface SensorController {

    /**
     * Start IMU data streaming.
     *
     * Internally runs the Fusion AHRS algorithm:
     * ```
     * FusionAhrsSettings settings = {
     *     .convention = FusionConventionNwu,
     *     .gain = 0.5f,
     *     .gyroscopeRange = 2000.0f,  // dps
     *     .accelerationRejection = 10.0f,  // degrees
     *     .magneticRejection = 10.0f,       // degrees
     *     .recoveryTriggerPeriod = 5 * sampleRate  // 5 seconds
     * };
     * FusionAhrsSetSettings(&ahrs, &settings);
     * // Per sample:
     * FusionAhrsUpdate(&ahrs, gyroscope, accelerometer, magnetometer, deltaTime);
     * FusionQuaternion q = FusionAhrsGetQuaternion(&ahrs);
     * FusionEuler euler = FusionQuaternionToEuler(q);
     * ```
     *
     * @param callback Called with each IMU sample
     * @param rateHz Desired sample rate (capped by device max)
     */
    fun startIMU(callback: (IMUData) -> Unit, rateHz: Int = 60)

    /** Stop IMU streaming. */
    fun stopIMU()

    /**
     * Get current head orientation (one-shot).
     * Uses the most recent fused IMU data.
     * @return Current orientation as Euler angles
     */
    fun getOrientation(): EulerAngles?

    /**
     * Start GPS location updates via connected phone.
     *
     * For RayNeo: Uses IPCSDK to relay GPS from phone's RayNeo AR companion app.
     * For other devices: Uses phone's location via companion app BLE relay.
     *
     * Requires:
     * - Phone companion app installed and running
     * - Location permission granted on phone
     * - RayNeo: MobileState.isMobileConnected() == true
     *
     * @param callback Called with location updates
     * @param intervalMs Update interval in milliseconds
     */
    fun startGPS(callback: (lat: Double, lon: Double, accuracy: Float) -> Unit, intervalMs: Long = 1000)

    /** Stop GPS streaming. */
    fun stopGPS()
}

/**
 * Input controller — touch, gesture, and voice input.
 *
 * Source: RayNeo ARDK TouchDispatcher/CommonTouchCallback/BaseEventActivity,
 *         xg-glass-sdk TouchCallback, MentraOS EventManager
 */
interface InputController {

    /**
     * Register for gesture events from the temple touchpad/buttons.
     *
     * RayNeo gesture detection pipeline (from ARDK):
     * 1. MotionEvent received from temple touchpad
     * 2. TouchDispatcher converts to gestures via CommonTouchCallback
     * 3. BaseEventActivity maps to TempleAction subclasses
     * 4. Actions delivered via Kotlin Flow (reactive stream)
     *
     * Gesture direction modes (RayNeo X3):
     * - Natural Mode (default): swipe forward on temple = navigate forward
     * - Non-Natural Mode: inverted (settable in system settings)
     *
     * @param callback Called with each gesture event
     */
    fun setGestureCallback(callback: (GestureEvent) -> Unit)

    /**
     * Register for voice commands.
     * Starts ASR on the glasses microphone.
     *
     * @param callback Called with recognized text
     * @param language BCP-47 language tag
     */
    fun setVoiceCallback(callback: (text: String, confidence: Float) -> Unit, language: String = "en-US")

    /**
     * Set up focus management for scrollable lists.
     *
     * RayNeo ARDK focus components:
     * - FocusHolder: Base focus switching logic
     * - FixPosFocusTracker: Fixed focus position (item scrolls to focus point)
     * - RecyclerViewSlidingTracker: Fixed focus, sliding list
     * - RecyclerViewFocusTracker: Moving focus, fixed list
     * - IFocusable interface: For custom focusable views
     *
     * Source: RayNeo ARDK Focus Management (Feishu Capabilities & API)
     */
    fun enableFocusManagement(recyclerView: android.view.View)
}
