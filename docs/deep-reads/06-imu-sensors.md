# DEEP Wave 4: IMU Sensors & Sensor Fusion Libraries
## Complete API Reference for Fusion, headset-utils, real_utilities, imu-inspector, spidgets-3dof

Generated from deep-read of all source files across 5 repositories.

---

# 1. FUSION (xioTechnologies/Fusion)
## C sensor fusion library for IMUs — Madgwick revised AHRS algorithm
## Source: /tmp/glasses-sdk-repos/Fusion/

### Overview
Fusion is a sensor fusion library for IMUs, optimised for embedded systems. Combines gyroscope,
accelerometer, and magnetometer data into orientation (quaternion/euler). Based on revised
Madgwick AHRS algorithm (PhD thesis Ch.7). Also available as Python package `imufusion`.

Key features:
- AHRS algorithm with acceleration/magnetic rejection
- Gyroscope bias estimation algorithm
- Sensor calibration models (inertial + magnetic)
- Axis remapping (24 orthogonal permutations)
- Fast inverse square root for embedded perf
- Supports NWU, ENU, NED conventions

---

## 1.1 FusionMath.h — Core Types & Math Operations

### Types/Unions

```c
typedef union {
    float array[3];
    struct { float x; float y; float z; } axis;
} FusionVector;
// 3D vector. Used for accelerometer, gyroscope, magnetometer data.

typedef union {
    float array[4];
    struct { float w; float x; float y; float z; } element;
} FusionQuaternion;
// Quaternion representation of orientation.

typedef union {
    float array[9];
    struct { float xx, xy, xz, yx, yy, yz, zx, zy, zz; } element;
} FusionMatrix;
// 3x3 matrix in row-major order. Used for rotation matrices, calibration.

typedef union {
    float array[3];
    struct { float roll; float pitch; float yaw; } angle;
} FusionEuler;
// ZYX Euler angles in degrees. Roll=X, Pitch=Y, Yaw=Z.
```

### Constants/Macros

```c
#define FUSION_VECTOR_ZERO      ((FusionVector){ .array = {0.0f, 0.0f, 0.0f} })
#define FUSION_VECTOR_ONES      ((FusionVector){ .array = {1.0f, 1.0f, 1.0f} })
#define FUSION_QUATERNION_IDENTITY ((FusionQuaternion){ .array = {1.0f, 0.0f, 0.0f, 0.0f} })
#define FUSION_MATRIX_IDENTITY  ((FusionMatrix){ .array = {1,0,0, 0,1,0, 0,0,1} })
#define FUSION_EULER_ZERO       ((FusionEuler){ .array = {0.0f, 0.0f, 0.0f} })
```

### Degree/Radian Conversion Functions

```c
static inline float FusionDegreesToRadians(const float degrees);
// Converts degrees to radians. Returns: degrees * (PI / 180)

static inline float FusionRadiansToDegrees(const float radians);
// Converts radians to degrees. Returns: radians * (180 / PI)
```

### Arc Sine (clamped)

```c
static inline float FusionArcSin(const float value);
// Returns arc sine clamped to [-1, 1] to avoid NaN.
```

### Fast Inverse Square Root

```c
static inline float FusionFastInverseSqrt(const float x);
// Pizer's implementation. Returns 1/sqrt(x). Disabled if FUSION_USE_NORMAL_SQRT defined.
```

### Vector Operations

```c
static inline bool FusionVectorIsZero(const FusionVector v);
// Returns true if all components are exactly 0.0f.

static inline FusionVector FusionVectorAdd(const FusionVector a, const FusionVector b);
// Returns a + b (element-wise).

static inline FusionVector FusionVectorSubtract(const FusionVector a, const FusionVector b);
// Returns a - b (element-wise).

static inline FusionVector FusionVectorScale(const FusionVector v, const float s);
// Returns v * s (scalar multiply).

static inline float FusionVectorSum(const FusionVector v);
// Returns x + y + z.

static inline FusionVector FusionVectorHadamard(const FusionVector a, const FusionVector b);
// Returns element-wise product: {a.x*b.x, a.y*b.y, a.z*b.z}.

static inline FusionVector FusionVectorCross(const FusionVector a, const FusionVector b);
// Returns cross product a × b.

static inline float FusionVectorDot(const FusionVector a, const FusionVector b);
// Returns dot product a · b.

static inline float FusionVectorNormSquared(const FusionVector v);
// Returns |v|² (magnitude squared).

static inline float FusionVectorNorm(const FusionVector v);
// Returns |v| (magnitude).

static inline FusionVector FusionVectorNormalise(const FusionVector v);
// Returns unit vector v/|v|. Uses fast inverse sqrt unless FUSION_USE_NORMAL_SQRT.
```

### Quaternion Operations

```c
static inline FusionQuaternion FusionQuaternionAdd(const FusionQuaternion a, const FusionQuaternion b);
// Returns a + b (element-wise).

static inline FusionQuaternion FusionQuaternionScale(const FusionQuaternion q, const float s);
// Returns q * s (scalar multiply).

static inline float FusionQuaternionSum(const FusionQuaternion q);
// Returns w + x + y + z.

static inline FusionQuaternion FusionQuaternionHadamard(const FusionQuaternion a, const FusionQuaternion b);
// Returns element-wise product.

static inline FusionQuaternion FusionQuaternionProduct(const FusionQuaternion a, const FusionQuaternion b);
// Returns Hamilton quaternion product a * b.

static inline FusionQuaternion FusionQuaternionVectorProduct(const FusionQuaternion q, const FusionVector v);
// Returns q * v where v is treated as quaternion with w=0.

static inline float FusionQuaternionNormSquared(const FusionQuaternion q);
// Returns |q|² (quaternion norm squared).

static inline float FusionQuaternionNorm(const FusionQuaternion q);
// Returns |q| (quaternion norm).

static inline FusionQuaternion FusionQuaternionNormalise(const FusionQuaternion q);
// Returns unit quaternion q/|q|.
```

### Matrix Operations

```c
static inline FusionVector FusionMatrixMultiply(const FusionMatrix m, const FusionVector v);
// Returns M * v (matrix-vector multiplication).
```

### Conversion Functions

```c
static inline FusionMatrix FusionQuaternionToMatrix(const FusionQuaternion q);
// Converts quaternion to 3x3 rotation matrix (transpose of Kuipers convention).

static inline FusionEuler FusionQuaternionToEuler(const FusionQuaternion q);
// Converts quaternion to ZYX Euler angles in degrees (roll, pitch, yaw).
```

---

## 1.2 FusionConvention.h — Earth Axes Convention

```c
typedef enum {
    FusionConventionNwu,  // North-West-Up: X=North, Y=West, Z=Up
    FusionConventionEnu,  // East-North-Up: X=East, Y=North, Z=Up
    FusionConventionNed,  // North-East-Down: X=North, Y=East, Z=Down
} FusionConvention;
```

---

## 1.3 FusionAhrs.h / FusionAhrs.c — AHRS Algorithm (CRITICAL)

### Structures

```c
typedef struct {
    FusionConvention convention;          // Earth axes convention (NWU/ENU/NED)
    float gain;                           // Complementary filter gain (0.5 typical; 0=gyro only)
    float gyroscopeRange;                 // Gyroscope range in deg/s (0=disable angular rate recovery)
    float accelerationRejection;          // Accel rejection threshold in degrees (0=disable; 10 typical)
    float magneticRejection;              // Mag rejection threshold in degrees (0=disable; 10 typical)
    unsigned int recoveryTriggerPeriod;   // Recovery trigger period in samples (0=disable; 5*sampleRate typical)
} FusionAhrsSettings;

typedef struct {
    FusionAhrsSettings settings;
    FusionQuaternion quaternion;
    FusionVector accelerometer;
    FusionVector halfGravity;
    bool startup;
    float rampedGain;
    float rampedGainStep;
    bool angularRateRecovery;
    FusionVector halfAccelerometerFeedback;
    FusionVector halfMagnetometerFeedback;
    bool accelerometerIgnored;
    int accelerationRecoveryTrigger;
    int accelerationRecoveryTimeout;
    bool magnetometerIgnored;
    int magneticRecoveryTrigger;
    int magneticRecoveryTimeout;
} FusionAhrs;
// AHRS state structure. All members are private.

typedef struct {
    float accelerationError;              // Angular error in degrees (accel vs algorithm output)
    bool accelerometerIgnored;            // true if accel was ignored last update
    float accelerationRecoveryTrigger;    // Recovery trigger 0.0-1.0
    float magneticError;                  // Angular error in degrees (mag vs algorithm output)
    bool magnetometerIgnored;             // true if mag was ignored last update
    float magneticRecoveryTrigger;        // Recovery trigger 0.0-1.0
} FusionAhrsInternalStates;

typedef struct {
    bool startup;                         // true during algorithm startup
    bool angularRateRecovery;             // true during angular rate recovery
    bool accelerationRecovery;            // true during acceleration recovery
    bool magneticRecovery;                // true during magnetic recovery
} FusionAhrsFlags;
```

### Default Settings

```c
extern const FusionAhrsSettings fusionAhrsDefaultSettings;
// = { .convention=NWU, .gain=0.5, .gyroscopeRange=0.0, .accelerationRejection=90.0,
//     .magneticRejection=90.0, .recoveryTriggerPeriod=0 }
```

### AHRS Functions (ALL FusionAhrs* functions)

```c
void FusionAhrsInitialise(FusionAhrs *const ahrs);
// @brief Initialises the AHRS structure with default settings and restarts algorithm.
// @param ahrs AHRS structure.

void FusionAhrsRestart(FusionAhrs *const ahrs);
// @brief Restarts the AHRS algorithm. Resets quaternion to identity, enables startup mode.
// @param ahrs AHRS structure.

void FusionAhrsSetSettings(FusionAhrs *const ahrs, const FusionAhrsSettings *const settings);
// @brief Sets algorithm settings. Converts rejection thresholds to internal representation.
//        Disables rejection features if gain=0 or recoveryTriggerPeriod=0.
// @param ahrs AHRS structure.
// @param settings Settings structure.

void FusionAhrsUpdate(FusionAhrs *const ahrs,
                      const FusionVector gyroscope,
                      const FusionVector accelerometer,
                      const FusionVector magnetometer,
                      const float deltaTime);
// @brief Updates AHRS algorithm with gyroscope, accelerometer, and magnetometer.
//        Core algorithm: integrates gyroscope with accelerometer/magnetometer feedback.
//        Handles startup gain ramping, angular rate recovery, accel/mag rejection.
// @param ahrs          AHRS structure.
// @param gyroscope     Gyroscope in degrees per second.
// @param accelerometer Accelerometer in g.
// @param magnetometer  Magnetometer in any calibrated units.
// @param deltaTime     Delta time in seconds.

void FusionAhrsUpdateNoMagnetometer(FusionAhrs *const ahrs,
                                     const FusionVector gyroscope,
                                     const FusionVector accelerometer,
                                     const float deltaTime);
// @brief Updates AHRS using only gyroscope and accelerometer (no magnetometer).
//        Calls FusionAhrsUpdate with zero magnetometer, zeros heading during startup.
// @param ahrs          AHRS structure.
// @param gyroscope     Gyroscope in degrees per second.
// @param accelerometer Accelerometer in g.
// @param deltaTime     Delta time in seconds.

void FusionAhrsUpdateExternalHeading(FusionAhrs *const ahrs,
                                      const FusionVector gyroscope,
                                      const FusionVector accelerometer,
                                      const float heading,
                                      const float deltaTime);
// @brief Updates AHRS using gyroscope, accelerometer, and external heading (e.g., GPS).
//        Constructs equivalent magnetometer from heading and current roll.
// @param ahrs          AHRS structure.
// @param gyroscope     Gyroscope in degrees per second.
// @param accelerometer Accelerometer in g.
// @param heading       Heading in degrees.
// @param deltaTime     Delta time in seconds.

FusionQuaternion FusionAhrsGetQuaternion(const FusionAhrs *const ahrs);
// @brief Returns the current orientation quaternion.
// @param ahrs AHRS structure.
// @return Quaternion describing sensor orientation relative to Earth.

void FusionAhrsSetQuaternion(FusionAhrs *const ahrs, const FusionQuaternion quaternion);
// @brief Sets the orientation quaternion directly.
// @param ahrs AHRS structure.
// @param quaternion Quaternion to set.

FusionVector FusionAhrsGetGravity(const FusionAhrs *const ahrs);
// @brief Returns direction of gravity in sensor frame as unit vector.
// @param ahrs AHRS structure.
// @return Gravity direction vector.

FusionVector FusionAhrsGetLinearAcceleration(const FusionAhrs *const ahrs);
// @brief Returns linear acceleration (accelerometer with gravity removed) in sensor frame.
// @param ahrs AHRS structure.
// @return Linear acceleration in g.

FusionVector FusionAhrsGetEarthAcceleration(const FusionAhrs *const ahrs);
// @brief Returns acceleration in Earth frame with gravity removed.
//        Rotates accelerometer to Earth frame then subtracts gravity.
// @param ahrs AHRS structure.
// @return Earth acceleration in g.

FusionAhrsInternalStates FusionAhrsGetInternalStates(const FusionAhrs *const ahrs);
// @brief Returns internal algorithm states for debugging/monitoring.
// @param ahrs AHRS structure.
// @return Internal states structure.

FusionAhrsFlags FusionAhrsGetFlags(const FusionAhrs *const ahrs);
// @brief Returns algorithm flags (startup, recovery states).
// @param ahrs AHRS structure.
// @return Flags structure.

void FusionAhrsSetHeading(FusionAhrs *const ahrs, const float heading);
// @brief Sets the heading (yaw) of the current orientation.
//        Applies rotation around Z axis to match desired heading.
// @param ahrs AHRS structure.
// @param heading Heading in degrees.
```

### Internal Static Functions (FusionAhrs.c)

```c
static inline FusionVector HalfGravity(const FusionAhrs *const ahrs);
// Returns direction of gravity scaled by 0.5 from quaternion. Convention-aware (NWU/ENU/NED).

static inline FusionVector HalfMagnetic(const FusionAhrs *const ahrs);
// Returns direction of magnetic field scaled by 0.5 from quaternion. Convention-aware.

static inline FusionVector Feedback(const FusionVector sensor, const FusionVector reference);
// Returns feedback as cross product of sensor and reference vectors.
// If error >90°, normalises the cross product.

static inline int Clamp(const int value, const int min, const int max);
// Clamps integer value to [min, max] range.
```

---

## 1.4 FusionBias.h / FusionBias.c — Gyroscope Bias Estimation

### Structures

```c
typedef struct {
    float sampleRate;           // Sample rate in Hz (default: 100)
    float stationaryThreshold;  // Stationary threshold in deg/s (default: 3.0)
    float stationaryPeriod;     // Stationary detection period in seconds (default: 3.0)
} FusionBiasSettings;

typedef struct {
    FusionBiasSettings settings;
    float filterCoefficient;
    unsigned int timeout;
    unsigned int timer;
    FusionVector offset;
} FusionBias;
// Bias estimation state. All members private.
```

### Bias Functions

```c
extern const FusionBiasSettings fusionBiasDefaultSettings;
// = { .sampleRate=100, .stationaryThreshold=3.0, .stationaryPeriod=3.0 }

void FusionBiasInitialise(FusionBias *const bias);
// @brief Initialises bias structure with default settings. Zeroes offset.
// @param bias Bias structure.

void FusionBiasSetSettings(FusionBias *const bias, const FusionBiasSettings *const settings);
// @brief Sets bias algorithm settings. Computes filter coefficient and timeout.
// @param bias Bias structure.
// @param settings Settings.

FusionVector FusionBiasUpdate(FusionBias *const bias, FusionVector gyroscope);
// @brief Updates bias algorithm and returns offset-corrected gyroscope.
//        Must be called every sample. Detects stationary periods to estimate offset.
// @param bias Bias structure.
// @param gyroscope Gyroscope in degrees per second.
// @return Offset-corrected gyroscope in degrees per second.

FusionVector FusionBiasGetOffset(const FusionBias *const bias);
// @brief Returns current gyroscope offset estimate.
// @param bias Bias structure.
// @return Gyroscope offset in degrees per second.

void FusionBiasSetOffset(FusionBias *const bias, const FusionVector offset);
// @brief Sets gyroscope offset (e.g. restore from non-volatile memory).
// @param bias Bias structure.
// @param offset Gyroscope offset in degrees per second.
```

---

## 1.5 FusionCompass.h / FusionCompass.c — Tilt-Compensated Compass

```c
float FusionCompass(const FusionVector accelerometer,
                    const FusionVector magnetometer,
                    const FusionConvention convention);
// @brief Calculates tilt-compensated magnetic heading.
//        Uses accelerometer to determine tilt, magnetometer for heading.
//        Convention-aware: computes north/west/east vectors differently per convention.
// @param accelerometer Accelerometer in any calibrated units.
// @param magnetometer  Magnetometer in any calibrated units.
// @param convention    Earth axes convention.
// @return Magnetic heading in degrees.
```

---

## 1.6 FusionModel.h — Sensor Calibration Models

```c
static inline FusionVector FusionModelInertial(
    const FusionVector uncalibrated,
    const FusionMatrix misalignment,
    const FusionVector sensitivity,
    const FusionVector offset);
// @brief Applies gyroscope/accelerometer calibration: M * s * (raw - offset)
// @param uncalibrated  Raw gyroscope or accelerometer.
// @param misalignment  Misalignment matrix.
// @param sensitivity   Sensitivity diagonal (as vector).
// @param offset        Offset vector.
// @return Calibrated gyroscope or accelerometer.

static inline FusionVector FusionModelMagnetic(
    const FusionVector uncalibrated,
    const FusionMatrix softIronMatrix,
    const FusionVector hardIronOffset);
// @brief Applies magnetometer calibration: S * (raw - h)
// @param uncalibrated   Raw magnetometer.
// @param softIronMatrix Soft-iron matrix.
// @param hardIronOffset Hard-iron offset vector.
// @return Calibrated magnetometer.
```

---

## 1.7 FusionRemap.h — Sensor Axis Remapping

```c
typedef enum {
    FusionRemapAlignmentPXPYPZ,  // +X+Y+Z (no remap)
    FusionRemapAlignmentPXPZNY,  // +X+Z-Y
    FusionRemapAlignmentPXNZPY,  // +X-Z+Y
    FusionRemapAlignmentPXNYNZ,  // +X-Y-Z
    // ... 24 total orthogonal permutations ...
    FusionRemapAlignmentNXNYPZ,  // -X-Y+Z
} FusionRemapAlignment;

static inline FusionVector FusionRemap(const FusionVector sensor, const FusionRemapAlignment alignment);
// @brief Remaps sensor axes to body frame using one of 24 orthogonal permutations.
// @param sensor    Sensor vector.
// @param alignment Alignment enum value.
// @return Sensor remapped to body frame.
```

---

# 2. HEADSET-UTILS (3rl-io/headset-utils)
## Rust AR glasses driver library with IMU fusion
## Source: /tmp/glasses-sdk-repos/headset-utils/

### Overview
Rust library for communicating with AR headsets. Supports:
- Rokid Air, Max
- XREAL Air, Air 2, Air 2 Pro, Light
- MGrawoow G530 (MetaVision M53)
- Mad Gaze Glow

Outputs raw IMU data (accel, gyro, mag) + built-in naive complementary filter fusion.
Coordinate system: RUB (Right-Up-Back), same as Android sensors.

### Dependencies: rusb, hidapi, serialport, nalgebra, bytemuck, tinyjson, byteorder

---

## 2.1 lib.rs — Core Types, Traits, FFI Interface

### Error Enum
```rust
pub enum Error {
    IoError(std::io::Error),
    UsbError(rusb::Error),       // #[cfg(feature = "rusb")]
    HidError(hidapi::HidError),  // #[cfg(feature = "hidapi")]
    SerialPortError(serialport::Error), // #[cfg(feature = "serialport")]
    NotFound,
    NotImplemented,
    PacketTimeout,
    Other(&'static str),
    ConcurrencyError,
}
```

### GlassesEvent Enum
```rust
pub enum GlassesEvent {
    AccGyro {
        accelerometer: Vector3<f32>,  // m²/s. Upright normal = (0, 9.81, 0)
        gyroscope: Vector3<f32>,      // rad/sec right-hand rotation. RUB frame.
        timestamp: u64,               // device time in microseconds
    },
    Magnetometer {
        magnetometer: Vector3<f32>,   // direction of magnetic north, in uT
        timestamp: u64,
    },
    KeyPress(u8),
    ProximityNear,
    ProximityFar,
    AmbientLight(u16),
    VSync,
}
```

### DisplayMode Enum
```rust
pub enum DisplayMode {
    SameOnBoth,          // Mirror 1920x1080
    Stereo,              // SBS 3840x1080
    HalfSBS,             // Half-SBS 960x540 upscaled
    HighRefreshRate,     // 120Hz mirror
    HighRefreshRateSBS,  // 90Hz SBS
}
```

### Side Enum
```rust
pub enum Side { Left, Right }
```

### ARGlasses Trait
```rust
pub trait ARGlasses: Send {
    fn serial(&mut self) -> Result<String>;
    fn read_event(&mut self) -> Result<GlassesEvent>;
    fn get_display_mode(&mut self) -> Result<DisplayMode>;
    fn set_display_mode(&mut self, display_mode: DisplayMode) -> Result<()>;
    fn display_fov(&self) -> f32;                                    // FOV in radians
    fn imu_to_display_matrix(&self, side: Side, ipd: f32) -> Isometry3<f64>;
    fn name(&self) -> &'static str;
    fn cameras(&self) -> Result<Vec<CameraDescriptor>>;             // default: empty
    fn display_matrices(&self) -> Result<(DisplayMatrices, DisplayMatrices)>; // default: NotImplemented
    fn display_delay(&self) -> u64;                                  // display delay in usecs
}
```

### Fusion Trait
```rust
pub trait Fusion: Send {
    fn glasses(&mut self) -> &mut Box<dyn ARGlasses>;
    fn attitude_quaternion(&self) -> UnitQuaternion<f32>;
    fn inconsistency_frd(&self) -> f32;
    fn update(&mut self) -> ();
}

impl dyn Fusion {
    pub fn attitude_frd_rad(&self) -> Vector3<f32>;  // (roll, pitch, yaw) in radians
    pub fn attitude_frd_deg(&self) -> Vector3<f32>;  // (roll, pitch, yaw) in degrees
}
```

### CameraDescriptor Struct
```rust
pub struct CameraDescriptor {
    pub name: &'static str,
    pub resolution: Vector2<f64>,
    pub intrinsic_matrix: Matrix3<f64>,
    pub distortion: [f64; 5],              // k1, k2, p1, p2, k3
    pub stereo_rotation: UnitQuaternion<f64>,
    pub imu_to_camera: Isometry3<f64>,
}
```

### DisplayMatrices Struct
```rust
pub struct DisplayMatrices {
    pub intrinsic_matrix: Matrix3<f64>,
    pub resolution: (u32, u32),
    pub isometry: Isometry3<f64>,
}
```

### Connection Struct (Global Singleton)
```rust
pub struct Connection {
    pub fusion: Arc<Mutex<Box<dyn Fusion>>>,
    pub terminating: Arc<AtomicBool>,
    pub interrupting: Arc<AtomicBool>,
    pub thread: Option<JoinHandle<()>>,
}

impl Connection {
    fn new() -> Self;
    fn get() -> Result<&'static mut Connection>;
    pub fn start() -> Result<&'static Connection>;
    pub fn stop() -> Result<()>;
    pub fn read_fusion<T>(f: &dyn Fn(&mut Box<dyn Fusion>) -> T) -> Result<T>;
}
```

### C FFI Exports
```rust
#[no_mangle] pub extern "C" fn StartConnection() -> i32;
// Starts sensor fusion connection. Returns 1 on success.

#[no_mangle] pub extern "C" fn StopConnection() -> i32;
// Stops connection. Returns 1 on success.

#[no_mangle] pub extern "C" fn GetEuler() -> *const f32;
// Returns pointer to [roll, pitch, yaw] in degrees (FRD frame).

#[no_mangle] pub extern "C" fn GetQuaternion() -> *const f32;
// Returns pointer to [x, y, z, w] quaternion.
```

### Factory Functions
```rust
pub fn any_fusion() -> Result<Box<dyn Fusion>>;
// Detects glasses and creates NaiveCF fusion instance.

pub fn any_glasses() -> Result<Box<dyn ARGlasses>>;
// Tries each supported glasses type in order: Rokid, NrealAir, NrealLight, Grawoow, MadGaze.

pub fn any_glasses_or_fail() -> Result<Box<dyn ARGlasses>>;
// Same but exits process on failure.
```

---

## 2.2 naive_cf.rs — Complementary Filter Fusion

### NaiveCF Struct
```rust
pub struct NaiveCF {
    pub glasses: Box<dyn ARGlasses>,
    pub attitude: UnitQuaternion<f32>,
    pub prev_gyro: (Vector3<f32>, u64),  // FRD frame
    pub inconsistency: f32,
}
```

### NaiveCF Functions
```rust
impl NaiveCF {
    pub fn new(glasses: Box<dyn ARGlasses>) -> Result<Self>;
    // Creates new CF. Waits for first non-zero gyro reading.

    fn next_event(&mut self) -> GlassesEvent;
    // Reads next valid event. Blocks. Exits process on error.

    fn rub_to_frd(v: &Vector3<f32>) -> Vector3<f32>;
    // Converts RUB (Right-Up-Back) to FRD (Forward-Right-Down): (-z, x, -y)

    fn update_gyro_rub(&mut self, gyro_rub: &Vector3<f32>, t: u64);
    // Integrates gyroscope reading (RUB frame) into attitude quaternion.

    fn update_acc(&mut self, acc_rub: &Vector3<f32>, _t: u64);
    // Applies gravity-based correction from accelerometer.
    // Skips if norm < 1.0 (free fall). Uses BASE_GRAV_RATIO=0.005.

    pub fn get_correction(acc, rotation, scale) -> Option<UnitQuaternion<f32>>;
    // Computes scaled rotation correction from accelerometer vs expected gravity.

    pub fn get_rotation(acc, rotation) -> Option<UnitQuaternion<f32>>;
    // Full rotation between expected gravity and accelerometer reading.
}

// Constants:
// BASE_GRAV_RATIO = 0.005 (accelerometer trust ratio)
// GYRO_SPEED_IN_TIMESTAMP_FACTOR = 1_000_000.0 (microseconds)
// INCONSISTENCY_DECAY = 0.90
// UP_FRD = (0.0, 0.0, -9.81)
```

---

## 2.3 rokid.rs — Rokid Air/Max Driver

### RokidAir Struct
```rust
pub struct RokidAir {
    device_handle: DeviceHandle<GlobalContext>,
    last_accelerometer: Option<(Vector3<f32>, u64)>,
    last_gyroscope: Option<(Vector3<f32>, u64)>,
    previous_key_states: u8,
    proxy_sensor_was_far: bool,
    pending_events: VecDeque<GlassesEvent>,
    model: RokidModel, // Air or Max
}
// VID=0x04d2, PID=0x162f, Endpoint=0x82
```

### Packet Structures (repr C, packed)
```rust
struct MiscPacket { packet_type, seq, _unknown, keys_pressed, proxy_sensor, ... }
struct SensorPacket { packet_type, sensor_type, seq, timestamp(u64), vector([f32;3]), ... }
// sensor_type: 1=accel, 2=gyro, 3=mag
struct CombinedPacket { packet_type, timestamp(u64), accelerometer, gyroscope, magnetometer, keys, proxy, vsync_timestamp, ... }
// packet_type=17 for combined packets (Rokid Max)
```

### Key Methods
```rust
impl RokidAir {
    pub fn new() -> Result<Self>;           // Connect to Rokid via USB
    fn handle_key_press(&mut self, keys_pressed: u8);
    fn handle_proxy_sensor(&mut self, value: u8);
}
// display_fov: Air=20°, Max=23°
// display_delay: Air=15000us, Max=13000us
```

---

## 2.4 nreal_air.rs — XREAL Air/Air2/Air2Pro Driver

### NrealAir Struct
```rust
pub struct NrealAir {
    model: AirModel,  // Air, Air2, Air2Pro
    device: HidDevice,
    pending_packets: VecDeque<McuPacket>,
    pending_events: VecDeque<GlassesEvent>,
    imu_device: ImuDevice,
}
// VID=0x3318, AIR_PID=0x0424, AIR2_PID=0x0428, AIR2PRO_PID=0x0432
```

### ImuDevice (internal)
```rust
struct ImuDevice {
    device: HidDevice,
    config_json: JsonValue,
    displays: Option<(DisplayMatrices, DisplayMatrices)>,
    gyro_bias: Vector3<f32>,
    accelerometer_bias: Vector3<f32>,
}
```

### IMU Packet Parsing
- Reads 0x80-byte packets, expects header [1, 2]
- Gyro: mul/div encoded, 24-bit signed integers, converted to rad/s with axis swap
- Accel: mul/div encoded, 24-bit signed integers, multiplied by 9.81 for m/s²
- Magnetometer: 16-bit signed integers
- Axis remapping: X=-gyro_x, Y=gyro_z, Z=gyro_y (with bias subtraction)

### Protocol Packets
```rust
struct McuPacket { cmd_id: u16, data: Vec<u8> }
struct McuRawPacket { head(0xfd), checksum(CRC32), length, request_id, timestamp, cmd_id, reserved, data }
struct ImuPacket { cmd_id: u8, data: Vec<u8> }
struct ImuRawPacket { head(0xaa), checksum(CRC32), length, cmd_id, data }
```

---

## 2.5 nreal_light.rs — XREAL Light Driver

### NrealLight Struct
```rust
pub struct NrealLight {
    device: HidDevice,
    pending_packets: VecDeque<Packet>,
    last_heartbeat: std::time::Instant,
    ov580: Ov580,
}
// MCU: VID=0x0486, PID=0x573c
// OV580: VID=0x05a9, PID=0x0680
```

### Special Features
- Requires heartbeat every 250ms in SBS mode
- Has SLAM camera interface (NrealLightSlamCamera)
- Left/right SLAM cameras: 640x480 grayscale
- Config JSON with calibration data

### NrealLightSlamCamera
```rust
pub struct NrealLightSlamCamera { device_handle: DeviceHandle<GlobalContext> }
pub struct NrealLightSlamCameraFrame {
    pub left: Vec<u8>,     // 640x480 grayscale
    pub right: Vec<u8>,    // 640x480 grayscale
    pub timestamp: u64,
}
impl NrealLightSlamCamera {
    pub fn new() -> Result<Self>;
    pub fn get_frame(&mut self, timeout: Duration) -> Result<NrealLightSlamCameraFrame>;
}
```

---

## 2.6 mad_gaze.rs — Mad Gaze Glow Driver

### MadGazeGlow Struct
```rust
pub struct MadGazeGlow {
    serial: SerialFraming,  // 921600 baud serial over USB (VID=1204, PID=2)
    timestamp: u64,
    last_magnetometer_timestamp: u64,
    pending_events: VecDeque<GlassesEvent>,
}
```

### I2C Sensor Communication
- AK09911 magnetometer (addr=12): 100Hz continuous mode, LSB_TO_UT = 4912/8190
- BMI160 accel/gyro (addr=104): FIFO mode, ACC_UNIT = 2*9.80665/32768, GYRO_UNIT = 2000*PI/180/32768
- Communication via I2R/I2W serial commands

---

## 2.7 grawoow.rs — Grawoow G530 Driver

### GrawoowG530 Struct
```rust
pub struct GrawoowG530 {
    mcu_handle: DeviceHandle<GlobalContext>,  // VID=0x1ff7, PID=0x0ff4
    ov580_handle: DeviceHandle<GlobalContext>, // VID=0x05a9, PID=0x0f87
    config_json: JsonValue,
    gyro_bias: Vector3<f32>,
    accelerometer_bias: Vector3<f32>,
    start: Instant,
}
```

### IMU Packet
- Gyro at offset 0x3c: 3x i32, GYRO_MUL = PI/180/16.4
- Accel at offset 0x58: 3x i32, ACC_MUL = 9.81/16384
- Axis remapping: X=-gyro_y, Y=-gyro_z, Z=gyro_x (with bias)

---

## 2.8 util.rs — USB Utilities

```rust
pub fn get_device_vid_pid(vid: u16, pid: u16) -> Result<Device<GlobalContext>>;
// Finds USB device by VID/PID.

pub fn get_interface_for_endpoint(device: &Device, endpoint_address: u8) -> Option<u8>;
// Returns USB interface number containing the given endpoint.

pub(crate) fn crc32_adler(buf: &[u8]) -> u32;
// CRC32 (standard polynomial) used by XREAL protocol.
```

---

## 2.9 Examples

### euler_60.rs
```rust
fn main() {
    let mut fusion = any_fusion().unwrap();
    let interval = Duration::from_millis(16);  // ~60Hz
    loop {
        fusion.update();
        // Print roll, pitch, yaw in radians at 60Hz
        let frd = fusion.attitude_frd_rad();
        println!("{:10.5}{:10.5}{:10.5}", frd[0], frd[1], frd[2]);
    }
}
```

### set_to_3d.rs
- CLI tool using clap to set display mode (2d/3d/halfsbs/120hz)

---

# 3. REAL_UTILITIES
## C++ XREAL Air protocol utility (Windows)
## Source: /tmp/glasses-sdk-repos/real_utilities/

### Overview
Windows C++ tool for low-level communication with XREAL Air glasses.
Uses hidapi for USB HID communication. Implements two protocol layers:
- protocol (MCU control, interface 4) — 0xFD header
- protocol3 (IMU control, interface 3) — 0xAA header

No README beyond: "Tools for interfacing with Nreal airs. Dependencies: zlib, hidapi"

---

## 3.1 protocol.h / protocol.cpp — MCU Control Protocol

### Class: protocol
```cpp
class protocol {
public:
    typedef struct {
        uint16_t msgId;
        uint8_t status;
        uint8_t payload[200];
        uint16_t payload_size;
    } parsed_rsp;

    static void listKnownCommands();
    static std::string keyForHex(uint16_t hex);
    static uint16_t hexForKey(std::string key);
    static void parse_rsp(const uint8_t* buffer_in, int size, parsed_rsp* result);
    static int cmd_build(uint16_t msgId, const uint8_t* p_buf, int p_size, uint8_t* cmd_buf, int cb_size);
    static int cmd_build(std::string msg_id, const uint8_t* p_buf, int p_size, uint8_t* cmd_buf, int cb_size);
    static void print_summary_rsp(parsed_rsp* result);
};
```

### Known MCU Commands (protocol)
| Command | Hex | Description |
|---------|-----|-------------|
| W_CANCEL_ACTIVATION | 0x19 | Cancel activation |
| R_MCU_APP_FW_VERSION | 0x26 | MCU APP FW version |
| R_GLASSID | 0x15 | Glass HW ID |
| R_DSP_APP_FW_VERSION | 0x21 | DSP APP FW version |
| R_DP7911_FW_VERSION | 0x16 | DP APP FW version |
| R_ACTIVATION_TIME | 0x29 | Read activation time |
| W_ACTIVATION_TIME | 0x2A | Write activation time |
| W_SLEEP_TIME | 0x1E | Write unsleep time |
| W_DISP_MODE | 0x08 | Set display mode |
| HEARTBEAT | 0x1A | Keep-alive heartbeat |
| P_BUTTON_PRESSED | 0x6C05 | Button event (pushed) |
| ASYNC_TEXT_LOG | 0x6C09 | Async text log |
| W_BOOT_UPDATE_* | 0x1100-0x1105 | Firmware update sequence |

### Packet Format (MCU protocol — 0xFD header)
```
Offset 0:  HEAD (0xFD)
Offset 1:  CRC32 (4 bytes)
Offset 5:  Length (2 bytes LE)
Offset 7:  Timestamp (8 bytes)
Offset 15: MsgID (2 bytes LE)
Offset 17: Reserved (5 bytes)
Offset 22: Payload / Status byte
```

---

## 3.2 protocol3.h / protocol3.cpp — IMU Protocol

### Class: protocol3
```cpp
class protocol3 {
public:
    typedef struct {
        uint8_t msgId;
        uint8_t payload[200];
        uint16_t payload_size;
    } parsed_rsp;

    static void listKnownCommands();
    static std::string keyForHex(uint8_t hex);
    static uint8_t hexForKey(std::string key);
    static void parse_rsp(const uint8_t* buffer_in, int size, parsed_rsp* result);
    static int cmd_build(uint8_t msgId, const uint8_t* p_buf, int p_size, uint8_t* cmd_buf, int cb_size);
    static int cmd_build(std::string msg_id, const uint8_t* p_buf, int p_size, uint8_t* cmd_buf, int cb_size);
    static void print_summary_rsp(parsed_rsp* result);
};
```

### Known IMU Commands (protocol3)
| Command | Hex | Description |
|---------|-----|-------------|
| GET_CAL_DATA_LENGTH | 0x14 | Get calibration data length |
| CAL_DATA_GET_NEXT_SEGMENT | 0x15 | Get next calibration data segment |
| ALLOCATE_CAL_DATA_BUFFER | 0x16 | Allocate calibration buffer |
| WRITE_CAL_DATA_SEGMENT | 0x17 | Write calibration data segment |
| FREE_CAL_BUFFER | 0x18 | Free calibration buffer |
| START_IMU_DATA | 0x19 | Start/stop IMU stream (0x01=start) |
| GET_STATIC_ID | 0x1A | Get static ID (returns 0x01012220) |

### Packet Format (IMU protocol — 0xAA header)
```
Offset 0:  HEAD (0xAA)
Offset 1:  CRC32 (4 bytes)
Offset 5:  Length (2 bytes LE)
Offset 7:  MsgID (1 byte)
Offset 8:  Payload
```

---

## 3.3 real_utilities.cpp — Main Program

### Functions
```cpp
static hid_device* open_device(int interface_num);
// Opens XREAL Air HID device (VID=0x3318, PID=0x0424) on specified interface.

static void print_bytes(const uint8_t* buffer, int size);
static void print_chars(const uint8_t* buffer, int size);

static int write_control(hid_device* device, uint16_t msgId, const uint8_t* p_buf, int p_size);
static int write_control(hid_device* device, std::string msg_id, const uint8_t* p_buf, int p_size);
// Sends MCU command via protocol class.

static int read_control(hid_device* device, int timeout_ms);
// Reads and parses MCU response.

static int write_imu(hid_device* device, uint8_t msgId, const uint8_t* p_buf, int p_size);
static int write_imu(hid_device* device, std::string msg_id, const uint8_t* p_buf, int p_size);
// Sends IMU command via protocol3 class.

static int read_imu(hid_device* device, int timeout_ms);
static int read_imu_get_rsp(hid_device* device, int timeout_ms, protocol3::parsed_rsp* out);
// Reads and parses IMU response.
```

### Main Program Flow
1. Opens IMU device (interface 3) and control device (interface 4)
2. Sends GET_STATIC_ID to IMU
3. Sends GET_CAL_DATA_LENGTH to IMU
4. Reads calibration data segments until complete
5. Prints calibration JSON to stdout

---

# 4. IMU-INSPECTOR
## C ncurses IMU data viewer for XREAL Air
## Source: /tmp/glasses-sdk-repos/imu-inspector/

### Overview
Single-file C program using hidapi + ncurses to display live IMU data from XREAL Air glasses.
No README found.

### Report Structure (packed)
```c
static struct {
    uint16_t unknown1;       // Expected: 0x0201
    uint16_t unknown2;
    uint8_t unknown3;
    uint32_t some_counter1;
    uint8_t unknown4;
    uint64_t unknown5;       // 00 00 a0 0f 00 00 00 01
    uint8_t unknown6;
    int16_t rate_pitch;      // Angular rate pitch
    uint8_t unknown7;
    int16_t rate_roll;       // Angular rate roll
    uint8_t unknown8;
    int16_t rate_yaw;        // Angular rate yaw
    uint16_t unknown9;       // 20 00
    uint32_t unknown10;      // 00 00 00 01
    uint8_t unknown11;
    int16_t rot_roll;        // Rotation roll
    uint8_t unknown13;
    int16_t rot_pitch1;      // Rotation pitch
    uint8_t unknown14;
    int16_t rot_pitch2;      // Rotation pitch2 (unclear)
    uint16_t unknown15;      // 00 80
    uint32_t unknown16;      // 00 04 00 00
    int16_t mag1, mag2, mag3; // Magnetometer
    uint32_t some_counter2;
    uint32_t unknown17;
    uint8_t unknown18, unknown19;
} __attribute__((__packed__)) report;
```

### Functions
```c
static void fix_report();
// Converts report fields from little-endian to host byte order.

static void print_report();
// Displays Rate (roll/pitch/yaw) and Rot and Mag values in ncurses window.

static void print_bytes(const uint8_t* buf, size_t len);
// Hex dump of raw bytes.

static void print_line(const char* s);
// Center-prints a string.

static hid_device* open_device();
// Opens XREAL Air (VID=0x3318, PID=0x0424) on interface 3.

int main(void);
// Main loop: opens device, sends magic payload to start IMU stream,
// reads reports continuously in ncurses display.
// Magic payload: { 0xaa, 0xc5, 0xd1, 0x21, 0x42, 0x04, 0x00, 0x19, 0x01 }
```

---

# 5. SPIDGETS-3DOF (3rl-io/spidgets-3dof)
## 3DOF AR web app with Euler angle streaming
## Source: /tmp/glasses-sdk-repos/spidgets-3dof/

### Overview
Example web app for AR in a browser with 3 degrees of freedom.
Architecture:
1. Rust driver `euler_60` (from headset-utils) outputs Euler angles at 60Hz to stdout
2. Node.js `ar-server.js` manages connection, corrects yaw drift, serves via socket.io
3. Browser frontend uses spidgets-core for 3D matrix transforms

Supports: Rokid (Win/Mac/Linux/Android), XREAL (Mac/Linux/Android), Viture/RayNeo (Android only)

---

## 5.1 ar-server.js — Server-Side IMU Bridge

### Key Functions
```javascript
function emit(event, data)
// Emits socket.io event if clients connected.

function log(msg)
// Console log + emit 'status' to clients.

function broadcastCam(x, y, z, firstConnect)
// Broadcasts euler angles via 'cam' socket event (unless calibrating).
// Also records test data if --record flag.

function _runCmd()
// Spawns euler_60 binary (or euler_60_apple_silicon on macOS).

function calibrate()
// 60-second yaw drift calibration:
// - 5s delay, then 55s measurement
// - Computes drift = deltaYaw / 55000 (radians per millisecond)
// - Saves to ./drift file
```

### Data Flow
```
euler_60 stdout → parse "pitch yaw roll" → apply drift correction → socket.io 'cam' event
Format: "{whitespace}{pitch rad}{ws}{yaw rad}{ws}{roll rad}"
```

### CLI Options
- `--port N` — Change HTTP port (default 8000)
- `--cal` — Force calibration
- `--record` — Record 10s of motion data to webroot/compat/data.json

---

## 5.2 webroot/app.js — Frontend 3DOF Renderer

### Key Functions
```javascript
function initCamera(yaw, firstConnect)
// Initializes THREE.js camera rotation with YXZ euler order.
// Sets initial yaw tare on first connect.

function setCamera(vecArr)
// Sets camera rotation from [pitch, yaw, roll] array.
// Applies tare offset to yaw. Respects roll/pitch toggle.
```

### Alpine.js Store
```javascript
Alpine.store('app', {
    roll: true,          // Enable/disable roll
    pitch: true,         // Enable/disable pitch
    toggleRoll(),        // Toggle roll lock
    togglePitch(),       // Toggle pitch lock
    center(),            // Re-center yaw
});
```

### Android Fallback
- Uses browser `deviceorientation` events instead of headset IMU
- Converts event.beta/alpha to pitch/yaw radians

---

## 5.3 webroot/compat/app.js — Compatibility Demo

- Plays back recorded data from data.json at 60fps
- FPS counter with color coding (green>50, yellow>30, red<30)
- Platform detection: Android, Windows, Linux, MacOS
- Compatible headset detection per platform

---

## 5.4 webroot/widgets/

### WeatherWidget (weather-widget.js)
```javascript
class WeatherWidget extends window.spidgets.SDiv {
    connectedCallback() // Sets 380x230 dimensions, loads weatherwidget.org
}
customElements.define('weather-widget', WeatherWidget);
```

### ChartWidget (chart-widget.js)
```javascript
class ChartWidget extends window.spidgets.SDiv {
    connectedCallback() // Sets 640x360 dimensions, loads TradingView chart
    // Attributes: interval (default '15'), symbol (default 'SPY')
}
customElements.define('chart-widget', ChartWidget);
```

---

# Cross-Reference: IMU Data Flow

```
Physical Sensors (BMI160 / ICM / etc.)
    ↓
USB HID / Serial Protocol
    ↓
headset-utils (Rust) / imu-inspector (C) / real_utilities (C++)
    ├── Raw: accelerometer (m/s²), gyroscope (rad/s), magnetometer (uT)
    ├── Coordinate frame: RUB (Right-Up-Back)
    ↓
Sensor Fusion
    ├── headset-utils: NaiveCF complementary filter (Rust)
    ├── Fusion library: Madgwick AHRS (C) — more sophisticated
    │   ├── FusionBiasUpdate() — gyro bias compensation
    │   ├── FusionModelInertial() — sensor calibration
    │   ├── FusionAhrsUpdate() — quaternion output
    │   └── FusionQuaternionToEuler() — euler output
    ↓
Output: Quaternion or Euler angles (roll, pitch, yaw)
    ↓
Application Layer
    ├── euler_60 example (stdout at 60Hz)
    ├── spidgets-3dof (web browser via socket.io)
    └── C FFI: GetEuler(), GetQuaternion()
```

---

# Summary Statistics

| Repository | Language | Source Files | Key Structs/Classes | Key Functions |
|-----------|----------|-------------|-------------------|--------------|
| Fusion | C | 10 .c/.h | 7 (FusionVector, FusionQuaternion, FusionMatrix, FusionEuler, FusionAhrs, FusionBias, FusionAhrsSettings) | 40+ (inline + exported) |
| headset-utils | Rust | 10 .rs | 15+ (RokidAir, NrealAir, NrealLight, MadGazeGlow, GrawoowG530, NaiveCF, Connection, etc.) | 50+ |
| real_utilities | C++ | 5 .cpp/.h | 2 (protocol, protocol3) | 15 |
| imu-inspector | C | 1 .c | 1 (report struct) | 6 |
| spidgets-3dof | JS | 5 .js | 2 (WeatherWidget, ChartWidget) | 10 |
