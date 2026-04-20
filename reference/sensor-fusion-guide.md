# Sensor Fusion & IMU Reference Guide
## Orientation Tracking for AR Glasses

> Extracted from MASTER_SDK_REFERENCE.md and deep-read 06 (IMU sensors).

---

## Core Data Types (XRLinuxDriver — imu.h)

```c
struct imu_euler_t { float roll, pitch, yaw; };
struct imu_quat_t  { float x, y, z, w; };
struct imu_vec3_t  { float x, y, z; };

struct imu_pose_t {
    imu_quat_t orientation;   // Primary rotation representation
    imu_vec3_t position;      // 6DoF position (when available)
    imu_euler_t euler;        // Derived Euler angles
};
```

## Quaternion Math Functions

| Function                              | Description                          |
|---------------------------------------|--------------------------------------|
| `normalize_quaternion(q)`             | Unit quaternion normalization        |
| `conjugate(q)`                        | Quaternion conjugate (inverse for unit q) |
| `multiply_quaternions(q1, q2)`        | Hamilton product                     |
| `euler_to_quaternion_xyz(euler)`       | Euler → Quat (XYZ rotation order)   |
| `euler_to_quaternion_zyx(euler)`       | Euler → Quat (ZYX rotation order)   |
| `euler_to_quaternion_zxy(euler)`       | Euler → Quat (ZXY rotation order)   |
| `quaternion_to_euler_xyz(q)`           | Quat → Euler (XYZ)                  |
| `quaternion_to_euler_zyx(q)`           | Quat → Euler (ZYX)                  |
| `quaternion_to_euler_zxy(q)`           | Quat → Euler (ZXY)                  |
| `device_pitch_adjustment(degrees)`     | Create pitch correction quaternion   |
| `vector_rotate(v, q)`                 | Rotate vector by quaternion          |
| `quat_equal(q1, q2)`                  | Equality check                       |
| `quat_small_angle_rad(q1, q2)`        | Angular distance between orientations|

## Pose Sync Utilities

```c
void imu_pose_sync_euler_from_orientation(imu_pose_t *p);
// Derives euler angles from quaternion orientation

void imu_pose_sync_orientation_from_euler(imu_pose_t *p);
// Derives quaternion from euler angles
```

## IMU Sampling Rates by Device

| Device Family | IMU Rate       | Notes                              |
|---------------|----------------|------------------------------------|
| XREAL         | 60–500 Hz      | Configurable via `imu_cycles_per_s`|
| RayNeo Carina | 1000 Hz        | Highest rate in ecosystem          |
| RayNeo X3     | ~60 Hz         | Android sensor API                 |
| Rokid         | ~100 Hz        | Via BLE/Wi-Fi transport            |
| Generic USB   | Configurable   | Set via `imu_buffer_size`          |

## Sensor Fusion Libraries

### Fusion (xioTechnologies) — Deep-Read 06
- **Language**: C (portable)
- **Algorithm**: AHRS (Attitude and Heading Reference System)
- **Input**: Raw accelerometer + gyroscope + magnetometer
- **Output**: Quaternion orientation
- **Features**: Configurable gain, rejection filters, offset compensation

### XRLinuxDriver Built-in
- **Smooth follow**: Slerp-based interpolation with configurable thresholds
- **Virtual screen positioning**: Head-tracked 3D position via quaternion math
- **Multi-tap detection**: Accelerometer peak detection

### headset-utils / real_utilities
- **Purpose**: Device-specific IMU calibration and testing
- **Features**: Raw sensor dump, calibration routines, drift analysis

## Coordinate Systems

```
AR Glasses Standard (right-handed):
  X → Right
  Y → Up  
  Z → Toward user (out of screen)

Euler Convention:
  Roll  → rotation around Z (tilt head left/right)
  Pitch → rotation around X (look up/down)
  Yaw   → rotation around Y (look left/right)
```

## Virtual Screen Positioning (Breezy Desktop)

```
1. Read IMU quaternion at display refresh rate
2. Apply device_pitch_adjustment for mounting angle
3. Slerp between current and target orientation (smooth_follow)
4. Project virtual screen plane using rotated forward vector
5. Map screen coordinates to SBS stereo pair
```

## Common Pitfalls

1. **Gimbal lock**: Use quaternions, not Euler angles, for interpolation
2. **Drift**: Magnetometer fusion helps; Fusion library handles this
3. **Coordinate mismatch**: Each device may use different axis conventions
4. **Latency**: Higher IMU rate = lower motion-to-photon latency
5. **Calibration**: Some devices need static calibration on startup

---

*Source: docs/MASTER_SDK_REFERENCE.md, docs/deep-reads/06-imu-sensors.md, docs/deep-reads/13-drivers-tools.md*
