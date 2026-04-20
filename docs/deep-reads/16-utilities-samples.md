# Utilities & Samples — Master SDK Reference
## IMU Sensor Fusion, Head Tracking, 3DoF Apps, and AR Glasses Samples

Generated: 2026-04-19
Sources: 9 GitHub repositories deep-crawled

---

# ============================================================================
# 1. xioTechnologies/Fusion — IMU Sensor Fusion Library (1.6K stars)
# ============================================================================

Repository: https://github.com/xioTechnologies/Fusion
License: MIT
Language: C with Python bindings (pip package: `imufusion`)
Stars: 1,600+ | Forks: 341

## Overview

Fusion is a sensor fusion library for Inertial Measurement Units (IMUs), optimised for
embedded systems. Provides AHRS (Attitude and Heading Reference System) algorithm combining
gyroscope, accelerometer, and magnetometer data into orientation relative to Earth.

Algorithm is based on the REVISED AHRS algorithm from chapter 7 of Madgwick's PhD thesis
(NOT the commonly known "Madgwick algorithm" from chapter 3).

Key features:
- Gyroscope bias correction algorithm
- Acceleration/magnetic rejection (ignores bad sensor data)
- Sensor axis remapping (24 alignment configurations)
- Calibration models for gyro/accel/magnetometer
- Tilt-compensated compass heading
- NWU, ENU, NED earth frame conventions
- Pure C, header-only math, minimal dependencies
- Python package: `pip install imufusion`

## File Structure

```
Fusion/
├── Fusion/              # Core C library
│   ├── Fusion.h         # Main include (wraps all headers)
│   ├── FusionAhrs.h     # AHRS structs + function declarations
│   ├── FusionAhrs.c     # AHRS algorithm implementation
│   ├── FusionBias.h     # Gyroscope bias structs + declarations
│   ├── FusionBias.c     # Bias estimation implementation
│   ├── FusionCompass.h   # Tilt-compensated compass
│   ├── FusionCompass.c   # Compass implementation
│   ├── FusionConvention.h # Earth axes conventions (NWU/ENU/NED)
│   ├── FusionMath.h     # Vector/Quaternion/Matrix/Euler math
│   ├── FusionModel.h    # Sensor calibration models
│   └── FusionRemap.h    # Sensor axis remapping (24 configs)
├── Python/
│   └── imufusion/       # Python C extension bindings
│       ├── imufusion.c  # Module init, class registration
│       ├── Ahrs.h       # Python AHRS wrapper
│       ├── AhrsFlags.h
│       ├── AhrsInternalStates.h
│       ├── AhrsSettings.h
│       ├── Bias.h       # Python Bias wrapper
│       ├── BiasSettings.h
│       ├── Compass.h
│       ├── Convention.h
│       ├── Convert.h
│       ├── Model.h
│       ├── NpArray.h    # NumPy array helpers
│       └── Remap.h
├── Examples/
│   └── Python/
│       ├── simple_example.py
│       └── advanced_example.py
├── CMakeLists.txt
├── setup.py
└── pyproject.toml
```

## Core Data Types (FusionMath.h)

```c
// 3D Vector (union — access via .array[3] or .axis.{x,y,z})
typedef union {
    float array[3];
    struct { float x; float y; float z; } axis;
} FusionVector;

// Quaternion (union — access via .array[4] or .element.{w,x,y,z})
typedef union {
    float array[4];
    struct { float w; float x; float y; float z; } element;
} FusionQuaternion;

// 3x3 Matrix row-major (union — .array[9] or .element.{xx,xy,xz,...})
typedef union {
    float array[9];
    struct {
        float xx, xy, xz;
        float yx, yy, yz;
        float zx, zy, zz;
    } element;
} FusionMatrix;

// Euler angles in degrees (ZYX convention)
typedef union {
    float array[3];
    struct { float roll; float pitch; float yaw; } angle;
} FusionEuler;
```

### Math Constants

```c
#define FUSION_VECTOR_ZERO       ((FusionVector){ .array = {0,0,0} })
#define FUSION_VECTOR_ONES       ((FusionVector){ .array = {1,1,1} })
#define FUSION_QUATERNION_IDENTITY ((FusionQuaternion){ .array = {1,0,0,0} })
#define FUSION_MATRIX_IDENTITY   ((FusionMatrix){ .array = {1,0,0, 0,1,0, 0,0,1} })
#define FUSION_EULER_ZERO        ((FusionEuler){ .array = {0,0,0} })
```

### Math Inline Functions (FusionMath.h)

```c
// Conversions
float FusionDegreesToRadians(float degrees);
float FusionRadiansToDegrees(float radians);

// Vector operations
FusionVector FusionVectorAdd(FusionVector a, FusionVector b);
FusionVector FusionVectorSubtract(FusionVector a, FusionVector b);
FusionVector FusionVectorScale(FusionVector v, float s);
FusionVector FusionVectorHadamard(FusionVector a, FusionVector b);  // element-wise multiply
FusionVector FusionVectorCrossProduct(FusionVector a, FusionVector b);
float        FusionVectorDotProduct(FusionVector a, FusionVector b);
float        FusionVectorNorm(FusionVector v);   // magnitude
FusionVector FusionVectorNormalise(FusionVector v);

// Quaternion operations
FusionQuaternion FusionQuaternionProduct(FusionQuaternion a, FusionQuaternion b);
FusionQuaternion FusionQuaternionConjugate(FusionQuaternion q);
FusionQuaternion FusionQuaternionNormalise(FusionQuaternion q);
FusionVector     FusionQuaternionRotate(FusionQuaternion q, FusionVector v);

// Matrix operations
FusionVector FusionMatrixMultiply(FusionMatrix M, FusionVector v);

// Conversion functions
FusionMatrix FusionQuaternionToMatrix(FusionQuaternion q);
FusionEuler  FusionQuaternionToEuler(FusionQuaternion q);  // ZYX Euler angles

// Safe asin with clamping
float FusionArcSin(float v);
```

## Earth Axes Convention (FusionConvention.h)

```c
typedef enum {
    FusionConventionNwu,  // North(X), West(Y), Up(Z)  — default
    FusionConventionEnu,  // East(X), North(Y), Up(Z)
    FusionConventionNed,  // North(X), East(Y), Down(Z)
} FusionConvention;
```

## AHRS Algorithm API (FusionAhrs.h / FusionAhrs.c)

### Settings

```c
typedef struct {
    FusionConvention convention;          // Earth axes convention
    float gain;                           // Algorithm gain (default: 0.5)
    float gyroscopeRange;                 // Max gyro deg/s (0 = unlimited)
    float accelerationRejection;          // Accel rejection angle deg (default: 90)
    float magneticRejection;              // Mag rejection angle deg (default: 90)
    unsigned int recoveryTriggerPeriod;   // Recovery period in samples (0 = disabled)
} FusionAhrsSettings;

// Default settings
const FusionAhrsSettings fusionAhrsDefaultSettings = {
    .convention = FusionConventionNwu,
    .gain = 0.5f,
    .gyroscopeRange = 0.0f,
    .accelerationRejection = 90.0f,
    .magneticRejection = 90.0f,
    .recoveryTriggerPeriod = 0,
};
```

### AHRS Structure (private members)

```c
typedef struct {
    FusionAhrsSettings settings;
    FusionQuaternion quaternion;
    FusionVector accelerometer;
    FusionVector halfGravity;
    bool startup;                          // True during startup period
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
```

### Internal States (for diagnostics)

```c
typedef struct {
    float accelerationError;           // degrees
    bool accelerometerIgnored;
    float accelerationRecoveryTrigger; // 0.0 to 1.0
    float magneticError;               // degrees
    bool magnetometerIgnored;
    float magneticRecoveryTrigger;     // 0.0 to 1.0
} FusionAhrsInternalStates;
```

### Flags

```c
typedef struct {
    bool startup;                // True during startup (first 3 seconds)
    bool angularRateRecovery;    // Gyroscope range exceeded
    bool accelerationRecovery;   // Accel rejection triggered recovery
    bool magneticRecovery;       // Mag rejection triggered recovery
} FusionAhrsFlags;
```

### AHRS Function Signatures

```c
// Initialize AHRS with default settings
void FusionAhrsInitialise(FusionAhrs *const ahrs);

// Restart algorithm (keeps settings, resets state)
void FusionAhrsRestart(FusionAhrs *const ahrs);

// Configure settings
void FusionAhrsSetSettings(FusionAhrs *const ahrs, const FusionAhrsSettings *const settings);

// === UPDATE FUNCTIONS (call one per sensor sample) ===

// Full 9-axis update: gyro + accel + mag
void FusionAhrsUpdate(FusionAhrs *const ahrs,
    const FusionVector gyroscope,       // degrees/sec
    const FusionVector accelerometer,   // g
    const FusionVector magnetometer,    // any calibrated unit
    const float deltaTime);             // seconds

// 6-axis update: gyro + accel only (no magnetometer)
void FusionAhrsUpdateNoMagnetometer(FusionAhrs *const ahrs,
    const FusionVector gyroscope,
    const FusionVector accelerometer,
    const float deltaTime);

// External heading update: gyro + accel + GPS/compass heading
void FusionAhrsUpdateExternalHeading(FusionAhrs *const ahrs,
    const FusionVector gyroscope,
    const FusionVector accelerometer,
    const float heading,                // degrees
    const float deltaTime);

// === OUTPUT FUNCTIONS ===

// Get orientation as quaternion
FusionQuaternion FusionAhrsGetQuaternion(const FusionAhrs *const ahrs);

// Set orientation quaternion manually
void FusionAhrsSetQuaternion(FusionAhrs *const ahrs, const FusionQuaternion quaternion);

// Get gravity vector in sensor frame
FusionVector FusionAhrsGetGravity(const FusionAhrs *const ahrs);

// Get linear acceleration (accel minus gravity, sensor frame)
FusionVector FusionAhrsGetLinearAcceleration(const FusionAhrs *const ahrs);

// Get earth acceleration (accel minus gravity, earth frame)
FusionVector FusionAhrsGetEarthAcceleration(const FusionAhrs *const ahrs);

// Get internal diagnostic states
FusionAhrsInternalStates FusionAhrsGetInternalStates(const FusionAhrs *const ahrs);

// Get algorithm flags
FusionAhrsFlags FusionAhrsGetFlags(const FusionAhrs *const ahrs);

// Set heading (yaw) in degrees
void FusionAhrsSetHeading(FusionAhrs *const ahrs, const float heading);
```

### AHRS Algorithm Details

Startup behavior:
- 3-second startup period with STARTUP_GAIN = 10.0
- Gain ramps down from 10.0 to configured gain over 3 seconds
- During startup, accelerometer/magnetometer have extra weight

Update loop:
1. Check if gyroscope exceeds configured range -> restart if exceeded
2. Ramp down gain during startup period
3. Calculate half-gravity and half-magnetic reference vectors
4. Compute feedback error between measured and reference vectors
5. Apply acceleration/magnetic rejection (ignore if error too large)
6. Recovery mechanism: if sensor ignored too long, force re-inclusion
7. Integrate gyroscope + feedback corrections using quaternion integration
8. Normalize quaternion

## Gyroscope Bias Estimation API (FusionBias.h / FusionBias.c)

### Bias Settings

```c
typedef struct {
    float sampleRate;           // Hz (default: 100)
    float stationaryThreshold;  // deg/s threshold for "stationary" (default: 3.0)
    float stationaryPeriod;     // seconds device must be stationary (default: 3.0)
} FusionBiasSettings;

const FusionBiasSettings fusionBiasDefaultSettings = {
    .sampleRate = 100.0f,
    .stationaryThreshold = 3.0f,
    .stationaryPeriod = 3.0f,
};
```

### Bias Structure

```c
typedef struct {
    FusionBiasSettings settings;
    float filterCoefficient;     // High-pass filter coefficient
    unsigned int timeout;        // Stationary timeout in samples
    unsigned int timer;          // Current timer count
    FusionVector offset;         // Estimated gyroscope offset
} FusionBias;
```

### Bias Function Signatures

```c
void FusionBiasInitialise(FusionBias *const bias);
void FusionBiasSetSettings(FusionBias *const bias, const FusionBiasSettings *const settings);

// Call per sample — returns offset-corrected gyroscope
FusionVector FusionBiasUpdate(FusionBias *const bias, FusionVector gyroscope);

FusionVector FusionBiasGetOffset(const FusionBias *const bias);
void FusionBiasSetOffset(FusionBias *const bias, const FusionVector offset);
```

### Bias Algorithm

Uses a high-pass filter (cutoff: 0.02 Hz) to estimate gyroscope offset:
1. Subtract current offset from raw gyroscope
2. If any axis exceeds stationaryThreshold -> reset timer, return corrected value
3. Increment timer while stationary
4. After stationary period elapsed, update offset via high-pass filter

## Compass API (FusionCompass.h / FusionCompass.c)

```c
// Tilt-compensated compass heading in degrees
float FusionCompass(
    const FusionVector accelerometer,    // g
    const FusionVector magnetometer,     // calibrated
    const FusionConvention convention);  // NWU/ENU/NED
```

## Calibration Models (FusionModel.h)

```c
// Gyroscope/Accelerometer calibration model
// calibrated = misalignment * ((uncalibrated - offset) ⊙ sensitivity)
static inline FusionVector FusionModelInertial(
    const FusionVector uncalibrated,
    const FusionMatrix misalignment,
    const FusionVector sensitivity,
    const FusionVector offset);

// Magnetometer calibration model (soft-iron + hard-iron)
// calibrated = softIronMatrix * (uncalibrated - hardIronOffset)
static inline FusionVector FusionModelMagnetic(
    const FusionVector uncalibrated,
    const FusionMatrix softIronMatrix,
    const FusionVector hardIronOffset);
```

## Axis Remapping (FusionRemap.h)

24 possible alignment configurations for mounting sensors in different orientations:

```c
typedef enum {
    FusionRemapAlignmentPXPYPZ,  // +X+Y+Z (identity, no remap)
    FusionRemapAlignmentPXPZNY,  // +X+Z-Y
    FusionRemapAlignmentPXNZPY,  // +X-Z+Y
    FusionRemapAlignmentPXNYNZ,  // +X-Y-Z
    FusionRemapAlignmentPYPXNZ,  // +Y+X-Z
    FusionRemapAlignmentPYPZPX,  // +Y+Z+X
    FusionRemapAlignmentPYNZNX,  // +Y-Z-X
    FusionRemapAlignmentPYNXPZ,  // +Y-X+Z
    FusionRemapAlignmentPZPXPY,  // +Z+X+Y
    FusionRemapAlignmentPZPYNX,  // +Z+Y-X
    FusionRemapAlignmentPZNYPX,  // +Z-Y+X
    FusionRemapAlignmentPZNXNY,  // +Z-X-Y
    FusionRemapAlignmentNZPXNY,  // -Z+X-Y
    FusionRemapAlignmentNZPYPX,  // -Z+Y+X
    FusionRemapAlignmentNZNYNX,  // -Z-Y-X
    FusionRemapAlignmentNZNXPY,  // -Z-X+Y
    FusionRemapAlignmentNYPXPZ,  // -Y+X+Z
    FusionRemapAlignmentNYPZNX,  // -Y+Z-X
    FusionRemapAlignmentNYNZPX,  // -Y-Z+X
    FusionRemapAlignmentNYNXNZ,  // -Y-X-Z
    FusionRemapAlignmentNXPYNZ,  // -X+Y-Z
    FusionRemapAlignmentNXPZPY,  // -X+Z+Y
    FusionRemapAlignmentNXNZNY,  // -X-Z-Y
    FusionRemapAlignmentNXNYPZ,  // -X-Y+Z
} FusionRemapAlignment;

FusionVector FusionRemap(FusionVector sensor, FusionRemapAlignment alignment);
```

## Python API (imufusion package)

Install: `pip install imufusion`

### Python Classes

```python
import imufusion

# AHRS
ahrs = imufusion.Ahrs()
ahrs.settings = imufusion.AhrsSettings(...)  # or set individual properties
ahrs.update(gyroscope, accelerometer, magnetometer, delta_time)
ahrs.update_no_magnetometer(gyroscope, accelerometer, delta_time)
ahrs.update_external_heading(gyroscope, accelerometer, heading, delta_time)
quaternion = ahrs.quaternion         # numpy array [w,x,y,z]
euler = ahrs.euler                   # numpy array [roll,pitch,yaw] degrees
internal_states = ahrs.internal_states  # AhrsInternalStates
flags = ahrs.flags                   # AhrsFlags
ahrs.heading = 0.0                   # set heading
ahrs.quaternion = [1,0,0,0]          # set quaternion
gravity = ahrs.gravity
linear_acceleration = ahrs.linear_acceleration
earth_acceleration = ahrs.earth_acceleration

# Bias
bias = imufusion.Bias()
bias.settings = imufusion.BiasSettings(...)
corrected_gyro = bias.update(gyroscope)

# Module-level functions
heading = imufusion.compass(accelerometer, magnetometer, convention=imufusion.CONVENTION_NWU)
calibrated = imufusion.inertial_model(uncalibrated, misalignment, sensitivity, offset)
calibrated = imufusion.magnetic_model(uncalibrated, soft_iron, hard_iron)
remapped = imufusion.remap(sensor, imufusion.ALIGNMENT_PXPYPZ)

# Convention constants
imufusion.CONVENTION_NWU
imufusion.CONVENTION_ENU
imufusion.CONVENTION_NED

# Alignment constants (24 total)
imufusion.ALIGNMENT_PXPYPZ  # through ALIGNMENT_NXNYPZ
```

### Usage Pattern (Simple)

```python
import imufusion
import numpy as np

ahrs = imufusion.Ahrs()
sample_rate = 100  # Hz

for gyro, accel, mag in sensor_data:
    ahrs.update(gyro, accel, mag, 1.0 / sample_rate)
    euler = ahrs.euler  # [roll, pitch, yaw] in degrees
```

### Usage Pattern (Advanced with Bias + Calibration)

```python
import imufusion

# Setup
ahrs = imufusion.Ahrs()
ahrs.settings = imufusion.AhrsSettings(
    convention=imufusion.CONVENTION_NWU,
    gain=0.5,
    gyroscope_range=2000,
    acceleration_rejection=10,
    magnetic_rejection=10,
    recovery_trigger_period=5 * sample_rate
)

bias = imufusion.Bias()
bias.settings = imufusion.BiasSettings(
    sample_rate=sample_rate,
    stationary_threshold=3.0,
    stationary_period=3.0
)

for gyro_raw, accel_raw, mag_raw in data:
    gyro = bias.update(gyro_raw)
    ahrs.update(gyro, accel_raw, mag_raw, 1.0 / sample_rate)
    euler = ahrs.euler
```

---

# ============================================================================
# 2. 3rl-io/spidgets-3dof — Spatial Widgets 3DoF App
# ============================================================================

Repository: https://github.com/3rl-io/spidgets-3dof
Stars: 46 | License: (included)
Language: JavaScript (Node.js) + HTML/CSS

## Overview

Example app for "spatial widgets" (spidgets) using 3DoF head tracking with AR glasses.
A Node.js server reads IMU Euler angles from a native binary (euler_60) and broadcasts
them to a web frontend via Socket.IO.

## Architecture

```
[AR Glasses USB] -> [euler_60 binary (native)] -> [ar-server.js (Node.js)]
    -> [Socket.IO] -> [Web Browser (Three.js / WebGL)]
```

## Key Files

- ar-server.js — Main server
- webroot/ — Web frontend (HTML/JS)
- bin/ — Pre-built euler_60 binaries (from headset-utils)
- package.json — Node.js dependencies (express, socket.io)

## ar-server.js — Key API

```javascript
// Server spawns native binary that outputs Euler angles
// Platform-specific binary selection:
//   Linux:  bin/euler_60
//   macOS:  bin/euler_60_apple_silicon
//   Windows: bin/euler_60 (shell: false)

// Socket.IO events:
io.emit('cam', [x, y, z, firstConnect])  // Euler angles broadcast
io.emit('status', msg)                    // Status messages
socket.on('powersaver', state => ...)     // Toggle power saver (skip frames)
socket.on('calibrate', calibrate)         // Trigger yaw drift calibration

// Yaw drift calibration:
// 1. Pause UI for 60 seconds
// 2. Measure yaw change over 55 seconds
// 3. Calculate drift rate (radians/ms)
// 4. Save to 'drift' file
// 5. Apply drift compensation: totalDrift = (Date.now() - tareTime) * drift
```

## Usage Pattern

```bash
npm install
node ar-server.js [--port 8000] [--cal] [--record]
# Open http://localhost:8000 in browser
# Plug in supported AR glasses via USB
```

---

# ============================================================================
# 3. 3rl-io/headset-utils — Headset Utilities (Rust)
# ============================================================================

Repository: https://github.com/3rl-io/headset-utils
Stars: 9 | License: MIT-derived
Language: Rust

## Overview

Rust library providing unified HID access to AR glasses IMU data.
Supports multiple headset brands. Outputs Euler angles at 60Hz.
The `euler_60` binary is the primary consumer.

## Supported Headsets

- Rokid Air (rokid.rs)
- Nreal Air (nreal_air.rs)
- Nreal Light (nreal_light.rs)
- Mad Gaze Glow (mad_gaze.rs)
- Grawoow G530 (grawoow.rs)

## Source Files

```
src/
├── lib.rs           # Core traits, error types, glass detection
├── grawoow.rs       # Grawoow G530 driver
├── mad_gaze.rs      # Mad Gaze Glow driver
├── naive_cf.rs      # Naive complementary filter implementation
├── nreal_air.rs     # Nreal Air HID driver
├── nreal_light.rs   # Nreal Light driver
├── rokid.rs         # Rokid Air HID driver
└── util.rs          # Utilities
```

## Key API (lib.rs)

```rust
// Core event types from glasses
enum GlassesEvent {
    AccGyro { accelerometer, gyroscope },
    Magnetometer(data),
    KeyPress(data),
    // ...
}

// Error types
enum Error {
    IoError(std::io::Error),
    UsbError(rusb::Error),
    HidError(hidapi::HidError),
    SerialPortError(serialport::Error),
    NotFound,
    NotImplemented,
    PacketTimeout,
    Other(&'static str),
    ConcurrencyError,
}

// Trait for glasses
trait ARGlasses {
    fn read_event(&mut self) -> Result<GlassesEvent>;
}

// Trait for sensor fusion
trait Fusion: Send {
    fn glasses(&mut self) -> &mut Box<dyn ARGlasses>;
    fn attitude_quaternion(&self) -> UnitQuaternion<f32>;
    fn inconsistency_frd(&self) -> f32;
    fn update(&mut self) -> ();
}

// Convenience methods on Fusion trait
impl dyn Fusion {
    fn attitude_frd_rad(&self) -> Vector3<f32>;
    fn attitude_frd_deg(&self) -> Vector3<f32>;
}

// Auto-detect any connected glasses
fn any_glasses() -> Result<Box<dyn ARGlasses>>;
// Detection order: RokidAir, NrealAir, NrealLight, GrawoowG530, MadGazeGlow
```

## Sensor Fusion Pipeline (documented in comments)

```
Roll/Pitch  ← accel + gyro (complementary filter)
Gyro-Yaw    ← gyro integration
Mag-Yaw     ← mag + roll/pitch (arctan)
Yaw         ← mag-yaw + gyro-yaw (complementary filter)

Reference frame: FRD (Forward, Right, Down)
- Standard aerospace frame
- Default for nalgebra
```

## Feature Flags (Cargo.toml)

```toml
[features]
default = ["mad_gaze", "nreal", "rokid", "grawoow"]
mad_gaze = ["hidapi"]
nreal = ["hidapi"]
rokid = ["hidapi"]
grawoow = ["hidapi"]
```

## udev Rules (Linux)

```
# udev/70-ar-headsets.rules
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="3318", MODE="0666"  # Nreal
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="04d2", MODE="0666"  # Rokid
```

---

# ============================================================================
# 4. edwatt/real_utilities — Nreal Air Utilities (C++)
# ============================================================================

Repository: https://github.com/edwatt/real_utilities
Stars: 24 | License: GPL-2.0
Language: C++ (Visual Studio project)

## Overview

Windows tools for interfacing with Nreal Air glasses. Provides low-level USB/HID
protocol implementation for reading IMU data.

## Key Files

- protocol.cpp — Nreal Air HID protocol implementation
- protocol.h — Protocol declarations
- Real_Utilities.sln — Visual Studio solution
- Real_Utilities.vcxproj — Project file

## Architecture

Direct HID communication with Nreal Air glasses on Windows using the Windows HID API.
Parses proprietary binary protocol for:
- Accelerometer data
- Gyroscope data
- Magnetometer data
- Device status/control

---

# ============================================================================
# 5. abls/imu-inspector — IMU Inspector Tool
# ============================================================================

Repository: https://github.com/abls/imu-inspector
Stars: 8 | Language: C
Description: "smol program to figure out the format of raw IMU data from nreal air"

## Overview

Minimal C program that connects to Nreal Air glasses via HID and displays raw
IMU data in an ncurses terminal UI. Critical for understanding the binary protocol.

## Key Files

- inspector.c — Single-file C program
- Makefile — Build instructions

## Nreal Air HID Protocol (reverse-engineered)

```c
// USB identifiers
#define AIR_VID 0x3318
#define AIR_PID 0x0424

// Interface number for IMU data: 3

// Magic payload to enable IMU streaming:
uint8_t magic_payload[] = { 0xaa, 0xc5, 0xd1, 0x21, 0x42, 0x04, 0x00, 0x19, 0x01 };
hid_write(device, magic_payload, sizeof(magic_payload));

// HID report structure (little-endian, packed):
struct {
    uint16_t unknown1;       // Always 0x0201
    uint16_t unknown2;
    uint8_t  unknown3;
    uint32_t some_counter1;
    uint8_t  unknown4;
    uint64_t unknown5;       // 00 00 a0 0f 00 00 00 01
    uint8_t  unknown6;
    int16_t  rate_pitch;     // Gyroscope pitch rate
    uint8_t  unknown7;
    int16_t  rate_roll;      // Gyroscope roll rate
    uint8_t  unknown8;
    int16_t  rate_yaw;       // Gyroscope yaw rate
    uint16_t unknown9;       // 0x2000
    uint32_t unknown10;      // 00 00 00 01
    uint8_t  unknown11;
    int16_t  rot_roll;       // Rotation roll
    uint8_t  unknown13;
    int16_t  rot_pitch1;     // Rotation pitch
    uint8_t  unknown14;
    int16_t  rot_pitch2;     // Second pitch (purpose unclear)
    uint16_t unknown15;      // 0x0080
    uint32_t unknown16;      // 00 04 00 00
    int16_t  mag1;           // Magnetometer axis 1
    int16_t  mag2;           // Magnetometer axis 2
    int16_t  mag3;           // Magnetometer axis 3
    uint32_t some_counter2;
    uint32_t unknown17;      // 0x00000000
    uint8_t  unknown18;
    uint8_t  unknown19;
} __attribute__((__packed__));
```

## Usage

```bash
make
./inspector
# Requires: libhidapi-dev libncurses-dev
# Plug in Nreal Air glasses via USB
# Displays angular rate, rotation, and magnetometer in real-time
```

---

# ============================================================================
# 6. MaxManausa/Metaverse-Max-RayNeo-X3-Pro-Set-Up
# ============================================================================

Repository: https://github.com/MaxManausa/Metaverse-Max-RayNeo-X3-Pro-Set-Up
Stars: 1
Language: Unity/C#

## Overview

RayNeo X3 Pro sample project setup guide. Unity project with initial configuration
for developing AR applications on RayNeo X3 Pro glasses.

## Structure

```
├── Assets/           # Unity assets (scenes, scripts, etc.)
├── Packages/         # Unity package manifest
├── ProjectSettings/  # Unity project settings
├── .gitattributes    # Git LFS configuration
├── .gitignore
└── README.md         # Setup guide
```

## Key Setup Notes

- Unity project with LFS for large assets
- RayNeo X3 Pro SDK integration
- December 2025 — January 2026 timeframe
- Contains sample project configurations for AR development

---

# ============================================================================
# 7. MaxManausa/Rayneo_OpenXR_ARDK_Project — 6DoF Art Gallery
# ============================================================================

Repository: https://github.com/MaxManausa/Rayneo_OpenXR_ARDK_Project
Language: Unity/C#

## Overview

6DoF art gallery sample project using RayNeo OpenXR ARDK.
Demonstrates full 6 degrees of freedom tracking with the RayNeo X3 Pro.

## Key Details

- Uses OpenXR standard for XR interaction
- ARDK (AR Development Kit) from RayNeo
- Art gallery demo showing spatial placement of virtual art
- Full 6DoF: position (x,y,z) + rotation (roll,pitch,yaw)

---

# ============================================================================
# 8. MaxManausa/RayNeoX3Pro-MITSample — Unity SDK Sample
# ============================================================================

Repository: https://github.com/MaxManausa/RayNeoX3Pro-MITSample
Language: Unity/C#

## Overview

MIT-licensed sample project for the RayNeo X3 Pro Unity SDK.
Provides boilerplate code for getting started with RayNeo development.

---

# ============================================================================
# 9. pkrumpl/frame-codebase — TFLite Micro on Brilliant Frame
# ============================================================================

Repository: https://github.com/pkrumpl/frame-codebase
Stars: 2 | Forked from: brilliantlabsAR/frame-codebase
Language: C/C++, Python

## Overview

Integration of TensorFlow Lite Micro into the Brilliant Labs Frame codebase.
The Brilliant Frame is smart glasses with a camera, display, and nRF52840 MCU.

## Key Modification

"Rework build process for C/C++ libraries and integrate TensorFlow Lite Micro"
- 1 commit ahead of brilliantlabsAR/frame-codebase
- Targets nRF52840 (ARM Cortex-M4F)

## Structure

```
├── .vscode/        # VS Code configuration
├── docs/           # Documentation
├── libraries/      # C/C++ libraries (including TFLite Micro)
├── scripts/        # Build scripts
├── source/         # Main firmware source
├── Makefile
├── nrfx_config.h   # nRF SDK configuration
├── nrfx_log.h      # Logging config
└── README.md
```

## Key Technical Details

- Platform: Brilliant Frame (nRF52840 SoC)
- Adds TensorFlow Lite Micro for on-device ML inference
- Build system rework for C/C++ library integration
- Targets ARM Cortex-M4F with hardware FPU
- Enables edge ML on smart glasses (gesture recognition, etc.)

---

# ============================================================================
# CROSS-REFERENCE: Common Patterns for AR Glasses Development
# ============================================================================

## IMU Data Pipeline Pattern

```
[Raw HID Bytes] → [Protocol Parser] → [Bias Correction] → [Sensor Fusion] → [Quaternion/Euler]

Implementation choices:
1. Fusion library (C) — Best for embedded
2. headset-utils (Rust) — Best for desktop apps
3. eskf crate (Rust) — Error-state Kalman filter alternative
4. Custom complementary filter — Simplest approach
```

## Supported AR Glasses Summary

| Glasses          | VID:PID     | Driver Source                    |
|-----------------|-------------|----------------------------------|
| Nreal Air       | 3318:0424   | headset-utils, imu-inspector     |
| Nreal Light     | 3318:xxxx   | headset-utils                    |
| Rokid Air       | 04d2:xxxx   | headset-utils                    |
| Mad Gaze Glow   | xxxx:xxxx   | headset-utils                    |
| Grawoow G530    | xxxx:xxxx   | headset-utils                    |
| RayNeo X3 Pro   | N/A (Android)| Unity SDK + OpenXR              |
| Brilliant Frame | N/A (BLE)   | frame-codebase (nRF52840)        |

## Sensor Fusion Quick Reference

For head tracking on AR glasses:

```
Minimum (3DoF):
  FusionBias bias;
  FusionAhrs ahrs;
  FusionBiasInitialise(&bias);
  FusionAhrsInitialise(&ahrs);
  
  // Per sample:
  gyro = FusionBiasUpdate(&bias, raw_gyro);
  FusionAhrsUpdateNoMagnetometer(&ahrs, gyro, accel, dt);
  euler = FusionQuaternionToEuler(FusionAhrsGetQuaternion(&ahrs));

Full (9DoF with calibration):
  FusionBias bias;
  FusionAhrs ahrs;
  FusionBiasInitialise(&bias);
  FusionAhrsInitialise(&ahrs);
  
  settings.gain = 0.5f;
  settings.accelerationRejection = 10.0f;
  settings.magneticRejection = 10.0f;
  settings.recoveryTriggerPeriod = sample_rate * 5;
  FusionAhrsSetSettings(&ahrs, &settings);
  
  // Per sample:
  gyro = FusionBiasUpdate(&bias, raw_gyro);
  gyro_cal = FusionModelInertial(gyro, misalignment, sensitivity, offset);
  accel_cal = FusionModelInertial(accel, ...);
  mag_cal = FusionModelMagnetic(mag, soft_iron, hard_iron);
  FusionAhrsUpdate(&ahrs, gyro_cal, accel_cal, mag_cal, dt);
  euler = FusionQuaternionToEuler(FusionAhrsGetQuaternion(&ahrs));
```

## Yaw Drift Compensation (from spidgets-3dof)

```javascript
// Measure drift over 55 seconds while stationary
// drift = (endYaw - startYaw) / 55000  // radians per millisecond
// Apply: correctedYaw = rawYaw - (Date.now() - tareTime) * drift
```

## Reference Frame Conventions

```
NWU (default for Fusion):  X=North, Y=West,  Z=Up    — gravity = +Z
ENU:                       X=East,  Y=North, Z=Up    — gravity = +Z
NED:                       X=North, Y=East,  Z=Down  — gravity = -Z
FRD (headset-utils):       X=Forward, Y=Right, Z=Down — aerospace standard
```
