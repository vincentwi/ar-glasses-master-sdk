# AR Glasses VID/PID Registry
## USB & BLE Device Identification Quick Reference

> Extracted from MASTER_SDK_REFERENCE.md — see full doc for complete context.

---

## USB HID Devices (XRLinuxDriver / Breezy ecosystem)

| Vendor     | VID      | Device Models                                              | PID Count |
|------------|----------|------------------------------------------------------------|-----------|
| **XREAL**  | `0x3318` | Air, Air 2, Air 2 Pro, Air 2 Ultra, One Pro, One, 1S      | 10        |
| **RayNeo** | `0x35CA` | One, One Lite, Pro, Luma, Luma Pro, Luma Ultra, Luma Cyber, Beast | 14  |
| **Rokid**  | `ROKID_GLASS_VID` | 7 variants (`0x162B`–`0x2180`)                   | 7         |
| **TCL**    | `0x1BBB` / `0xAF50` | RayNeo X3 series                              | 1         |

## BLE Devices (xg-glass-sdk)

| Device       | BLE Identifier              | Transport Notes                                    |
|--------------|-----------------------------|----------------------------------------------------|
| **Frame**    | Flutter BLE scan            | MTU negotiation, Lua scripting bridge              |
| **Omi**      | Name: "Omi" / "OMI Glass"  | GATT, MTU 512, OPUS 16kHz mono audio               |
| **Meta**     | Wearables SDK registration  | Bluetooth HFP for mic (8kHz mono)                  |
| **Rokid**    | BLE scan → Wi-Fi P2P       | Hybrid: BLE for discovery, Wi-Fi for data          |

## SBS (Side-by-Side) Display Modes

| Vendor     | Non-SBS Resolution | SBS Resolution   | Notes                          |
|------------|-------------------|------------------|--------------------------------|
| **XREAL**  | 1920×1080         | 3840×1080        | Standard stereo mapping        |
| **RayNeo** | 1920×1080@60      | 3840×1080@60     | Mode codes: 0x31, 0x32, etc.  |
| **Rokid**  | 3840×1080@60 (2D) | 3840×1200@60/90 (3D) | Higher res 3D modes       |
| **RayNeo X3** | 1280×480 (total) | 640×480 per eye | Binocular rendering           |

## USB Data Structures

```c
// From XRLinuxDriver
struct device_properties_t {
    int hid_vendor_id, hid_product_id;
    uint8_t usb_bus, usb_address;
    bool sbs_mode_supported, sbs_mode_enabled;
    int imu_cycles_per_s;    // 60-1000Hz depending on device
    int imu_buffer_size;
};
```

## BLE UUIDs (Omi Glass)

| UUID Purpose         | Description                                         |
|---------------------|-----------------------------------------------------|
| AUDIO_SERVICE_UUID  | Primary scan target                                  |
| AUDIO_DATA_UUID     | OPUS stream (3-byte header: 2b index + 1b sub-index) |
| PHOTO_CONTROL_UUID  | Write 0x05 to trigger capture                       |
| PHOTO_DATA_UUID     | Receive chunks, EOF marker = 0xFFFF                 |

---

*Source: docs/MASTER_SDK_REFERENCE.md, docs/deep-reads/04-xr-drivers.md*
