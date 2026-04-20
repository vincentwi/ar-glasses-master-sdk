# AR Glasses Protocol Cheatsheet
## Transport & Communication Quick Reference

> Extracted from MASTER_SDK_REFERENCE.md and deep-read analyses.

---

## Transport Layer by Device

| Device        | Primary Transport | Secondary       | SDK Layer                     |
|---------------|-------------------|-----------------|-------------------------------|
| XREAL         | USB HID           | —               | XRLinuxDriver (C)             |
| RayNeo X3     | USB HID           | Android Intent  | XRLinuxDriver + Android SDK   |
| RayNeo Luma   | USB HID           | —               | XRLinuxDriver (C)             |
| Rokid         | Wi-Fi P2P         | BLE (discovery) | xg-glass-sdk (Kotlin)         |
| Frame         | BLE GATT          | —               | xg-glass-sdk / Flutter bridge |
| Meta          | Bluetooth HFP     | Wearables SDK   | xg-glass-sdk (Kotlin)         |
| Omi           | BLE GATT          | —               | xg-glass-sdk (Kotlin)         |
| Vuzix         | Android Intent    | —               | Native Android APIs            |
| Everysight    | BLE + Companion   | —               | Proprietary SDK                |

## Connection Flows

### USB HID (XRLinuxDriver)
```
libusb_hotplug_register → device_connect(vid, pid)
  → open HID interface
  → start IMU read thread (imu_cycles_per_s Hz)
  → register feature reports for SBS/brightness control
```

### BLE (xg-glass-sdk — Omi example)
```
BLE scan("Omi"/"OMI Glass" or AUDIO_SERVICE_UUID)
  → GATT connect
  → MTU negotiate (512)
  → discover services
  → enable notifications on AUDIO_DATA_UUID
```

### BLE → Wi-Fi P2P (Rokid)
```
BLE scan → initBluetooth() → connectBluetooth()
  → initWifiP2P() → data channel over Wi-Fi Direct
```

### Meta Wearables
```
Wearables.initialize()
  → startRegistration()
  → awaitActiveDevice()
  → AudioRecord via VOICE_COMMUNICATION (Bluetooth HFP, 8kHz mono)
```

## HID Feature Reports (XRLinuxDriver)

| Function                        | Description                        |
|---------------------------------|------------------------------------|
| `device_set_sbs_mode_func`      | Enable/disable side-by-side mode   |
| `device_imu_*`                  | IMU data read interface            |
| `device_mcu_*`                  | MCU control commands               |

## Control Modes (XRLinuxDriver)

| Mode            | Field              | Description                           |
|-----------------|--------------------|---------------------------------------|
| Mouse mode      | `mouse_mode`       | IMU drives system cursor              |
| Joystick mode   | `joystick_mode`    | IMU maps to gamepad axes              |
| External mode   | `external_mode`    | Raw IMU data for external consumers   |
| Smooth follow   | `smooth_follow`    | Slerp-based screen follow             |
| Multi-tap       | `multi_tap_enabled`| Tap gesture recognition               |

## Stardust XR (Wayland Compositor Protocol)

```
Client::from_connection(UnixStream)
  → reads PID, exe path from peer creds
  → Flatbuffers IPC (zero-copy serialization)
  → scenegraph node system (spatial items, panels, fields)
```

## MentraOS IPC

```
AppServer (Unix socket server)
  → AppSession per connected client
  → LayoutManager for spatial UI
  → EventManager for input dispatch
```

## Audio Encoding Summary

| Device | Format          | Sample Rate | Channels | Transport           |
|--------|-----------------|-------------|----------|---------------------|
| Omi    | OPUS            | 16 kHz      | Mono     | BLE notifications   |
| Meta   | PCM (raw)       | 8 kHz       | Mono     | Bluetooth HFP       |
| Frame  | Device-specific | Varies      | Mono     | BLE GATT            |

---

*Source: docs/MASTER_SDK_REFERENCE.md, docs/deep-reads/*
