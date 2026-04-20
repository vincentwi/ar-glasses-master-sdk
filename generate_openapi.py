#!/usr/bin/env python3
"""Generate comprehensive OpenAPI 3.1.0 YAML for AR Glasses Master SDK."""

import yaml
import sys

spec = {
    "openapi": "3.1.0",
    "info": {
        "title": "AR Glasses Master SDK API",
        "description": "Comprehensive REST-like documentation API for the AR Glasses Master SDK. Covers 27+ repositories, 500+ functions across 12 domains: Display, IMU, Camera, Audio, BLE, Gesture, Spatial Computing, ML/AI, GPS, Device Management, StardustXR 3D, and Geo/Maps Intelligence.",
        "version": "1.0.0",
        "contact": {
            "name": "AR Glasses SDK Team",
            "url": "https://github.com/AugmentOS"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "servers": [
        {
            "url": "https://api.ar-glasses-sdk.dev/api/v1",
            "description": "AR Glasses SDK Documentation API"
        },
        {
            "url": "http://localhost:3000/api/v1",
            "description": "Local development server"
        }
    ],
    "tags": [
        {"name": "display", "description": "Display & Rendering APIs — text display, bitmap rendering, HUD menus, binocular stereo, curved monitors"},
        {"name": "imu", "description": "IMU & Head Tracking (Sensor Fusion) — AHRS, quaternion math, bias estimation, Kalman filtering"},
        {"name": "camera", "description": "Camera & Computer Vision — photo capture, SLAM cameras, frame processing"},
        {"name": "audio", "description": "Audio & Speech — TTS, microphone capture, transcription, audio sync"},
        {"name": "ble", "description": "BLE & Wireless Communication — Bluetooth LE, Wi-Fi P2P, WebSocket transport"},
        {"name": "gesture", "description": "Gesture & Input — tap detection, keyboard, gaze input, hand tracking, ring input"},
        {"name": "spatial", "description": "Spatial Computing (SLAM, Anchors, OpenXR) — XR sessions, reference spaces, plane detection"},
        {"name": "ml", "description": "ML/AI On-Device — TFLite Micro, SAM3 segmentation, Groq LLM, on-device inference"},
        {"name": "gps", "description": "GPS & Geolocation — location access, GPS IPC"},
        {"name": "device", "description": "Device Management & Connectivity — connection lifecycle, device drivers, config, plugins"},
        {"name": "stardust", "description": "3D Environment (StardustXR) — spatial nodes, drawables, fields, panels, Wayland integration"},
        {"name": "geo", "description": "Geo/Maps Intelligence — Overpass OSM queries, Gemini Maps grounding, health data"},
    ],
    "paths": {},
    "components": {
        "schemas": {}
    }
}

paths = spec["paths"]
schemas = spec["components"]["schemas"]

# ============================================================
# HELPER
# ============================================================
def add_path(domain, repo, func_name, summary, description, tag, parameters=None, returns=None):
    path = f"/api/v1/{domain}/{repo}/{func_name}"
    entry = {
        "get": {
            "operationId": f"{domain}_{repo}_{func_name}".replace("-", "_").replace(".", "_"),
            "summary": summary,
            "description": description,
            "tags": [tag],
            "responses": {
                "200": {
                    "description": returns or "Success",
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                }
            }
        }
    }
    if parameters:
        entry["get"]["parameters"] = parameters
    paths[path] = entry

def param(name, ptype, desc, required=False):
    return {
        "name": name,
        "in": "query",
        "description": desc,
        "required": required,
        "schema": {"type": ptype}
    }

# ============================================================
# SCHEMAS
# ============================================================
schemas["FusionVector"] = {
    "type": "object",
    "description": "3D vector used for IMU sensor data (accelerometer, gyroscope, magnetometer).",
    "properties": {
        "x": {"type": "number", "format": "float"},
        "y": {"type": "number", "format": "float"},
        "z": {"type": "number", "format": "float"},
    }
}
schemas["FusionQuaternion"] = {
    "type": "object",
    "description": "Quaternion orientation representation {w, x, y, z}.",
    "properties": {
        "w": {"type": "number", "format": "float"},
        "x": {"type": "number", "format": "float"},
        "y": {"type": "number", "format": "float"},
        "z": {"type": "number", "format": "float"},
    }
}
schemas["FusionEuler"] = {
    "type": "object",
    "description": "Euler angle orientation: roll, pitch, yaw in degrees.",
    "properties": {
        "roll": {"type": "number", "format": "float"},
        "pitch": {"type": "number", "format": "float"},
        "yaw": {"type": "number", "format": "float"},
    }
}
schemas["FusionMatrix"] = {
    "type": "object",
    "description": "3x3 rotation matrix.",
    "properties": {
        "elements": {"type": "array", "items": {"type": "number"}, "minItems": 9, "maxItems": 9}
    }
}
schemas["FusionAhrsSettings"] = {
    "type": "object",
    "description": "AHRS algorithm configuration.",
    "properties": {
        "convention": {"type": "string", "enum": ["NWU", "ENU", "NED"]},
        "gain": {"type": "number", "format": "float", "description": "Filter gain (0 = gyro only)"},
        "gyroscopeRange": {"type": "number", "format": "float", "description": "Max degrees per second"},
        "accelerationRejection": {"type": "number", "format": "float"},
        "magneticRejection": {"type": "number", "format": "float"},
        "recoveryTriggerPeriod": {"type": "integer"},
    }
}
schemas["FusionAhrs"] = {
    "type": "object",
    "description": "AHRS (Attitude and Heading Reference System) state structure.",
    "properties": {
        "quaternion": {"$ref": "#/components/schemas/FusionQuaternion"},
        "settings": {"$ref": "#/components/schemas/FusionAhrsSettings"},
    }
}
schemas["FusionBiasSettings"] = {
    "type": "object",
    "properties": {
        "sampleRate": {"type": "number"},
        "stationaryThreshold": {"type": "number"},
        "stationaryPeriod": {"type": "number"},
    }
}
schemas["FusionAhrsInternalStates"] = {
    "type": "object",
    "properties": {
        "accelerationError": {"type": "number"},
        "accelerometerIgnored": {"type": "boolean"},
        "magneticError": {"type": "number"},
        "magnetometerIgnored": {"type": "boolean"},
    }
}
schemas["FusionAhrsFlags"] = {
    "type": "object",
    "properties": {
        "startup": {"type": "boolean"},
        "angularRateRecovery": {"type": "boolean"},
        "accelerationRecovery": {"type": "boolean"},
        "magneticRecovery": {"type": "boolean"},
    }
}
schemas["XRDeviceInfo"] = {
    "type": "object",
    "description": "XR device properties from XRLinuxDriver.",
    "properties": {
        "brand": {"type": "string"},
        "model": {"type": "string"},
        "hid_vendor_id": {"type": "integer"},
        "hid_product_id": {"type": "integer"},
        "resolution_w": {"type": "integer"},
        "resolution_h": {"type": "integer"},
        "fov": {"type": "number", "description": "Diagonal FOV degrees"},
        "lens_distance_ratio": {"type": "number"},
        "calibration_wait_s": {"type": "integer"},
        "imu_cycles_per_s": {"type": "integer"},
        "imu_buffer_size": {"type": "integer"},
        "look_ahead_constant": {"type": "number"},
        "sbs_mode_supported": {"type": "boolean"},
        "provides_orientation": {"type": "boolean"},
        "provides_position": {"type": "boolean"},
    }
}
schemas["IMUData"] = {
    "type": "object",
    "description": "IMU sensor reading with orientation and acceleration.",
    "properties": {
        "orientation": {"$ref": "#/components/schemas/FusionQuaternion"},
        "euler": {"$ref": "#/components/schemas/FusionEuler"},
        "linearAcceleration": {"$ref": "#/components/schemas/FusionVector"},
        "timestamp_ms": {"type": "number"},
    }
}
schemas["SensorData"] = {
    "type": "object",
    "description": "Raw sensor reading from AR glasses IMU.",
    "properties": {
        "gyroscope": {"$ref": "#/components/schemas/FusionVector"},
        "accelerometer": {"$ref": "#/components/schemas/FusionVector"},
        "magnetometer": {"$ref": "#/components/schemas/FusionVector"},
        "timestamp": {"type": "number"},
    }
}
schemas["GlassesClient"] = {
    "type": "object",
    "description": "Universal glasses client interface (xg-glass-sdk).",
    "properties": {
        "model": {"type": "string", "enum": ["FRAME", "META", "ROKID", "RAYNEO", "SIMULATOR", "OMI"]},
        "capabilities": {"$ref": "#/components/schemas/DeviceCapabilities"},
        "state": {"type": "string", "enum": ["Disconnected", "Connecting", "Connected", "Error"]},
    }
}
schemas["DeviceCapabilities"] = {
    "type": "object",
    "description": "Device feature capabilities.",
    "properties": {
        "canCapturePhoto": {"type": "boolean", "default": True},
        "canDisplayText": {"type": "boolean", "default": True},
        "canRecordAudio": {"type": "boolean", "default": False},
        "canPlayTts": {"type": "boolean", "default": False},
        "canPlayAudioBytes": {"type": "boolean", "default": False},
        "supportsTapEvents": {"type": "boolean", "default": False},
        "supportsStreamingTextUpdates": {"type": "boolean", "default": False},
    }
}
schemas["DeviceConfig"] = {
    "type": "object",
    "description": "XR driver configuration.",
    "properties": {
        "disabled": {"type": "boolean"},
        "display_fov": {"type": "number"},
        "lens_distance_ratio": {"type": "number"},
        "display_res": {"type": "array", "items": {"type": "number"}},
    }
}
schemas["DisplayOptions"] = {
    "type": "object",
    "properties": {
        "mode": {"type": "string", "enum": ["REPLACE", "APPEND"]},
        "force": {"type": "boolean", "default": False},
    }
}
schemas["CaptureOptions"] = {
    "type": "object",
    "properties": {
        "quality": {"type": "integer", "minimum": 0, "maximum": 100},
        "targetWidth": {"type": "integer"},
        "targetHeight": {"type": "integer"},
        "timeoutMs": {"type": "integer", "default": 30000},
    }
}
schemas["CapturedImage"] = {
    "type": "object",
    "properties": {
        "jpegBytes": {"type": "string", "format": "byte"},
        "timestampMs": {"type": "integer"},
        "width": {"type": "integer"},
        "height": {"type": "integer"},
        "rotationDegrees": {"type": "integer"},
        "sourceModel": {"type": "string"},
    }
}
schemas["AudioSource"] = {
    "type": "object",
    "description": "Audio source — TTS text or raw bytes.",
    "oneOf": [
        {"type": "object", "properties": {"type": {"const": "tts"}, "text": {"type": "string"}}},
        {"type": "object", "properties": {"type": {"const": "raw"}, "data": {"type": "string", "format": "byte"}, "pcmFormat": {"$ref": "#/components/schemas/PcmFormat"}}},
    ]
}
schemas["PcmFormat"] = {
    "type": "object",
    "properties": {
        "sampleRateHz": {"type": "integer", "default": 16000},
        "channelCount": {"type": "integer", "default": 1},
        "encoding": {"type": "string", "enum": ["PCM_S16_LE", "PCM_S8", "OPUS", "MP3"]},
    }
}
schemas["AudioChunk"] = {
    "type": "object",
    "properties": {
        "bytes": {"type": "string", "format": "byte"},
        "format": {"$ref": "#/components/schemas/PcmFormat"},
        "sequence": {"type": "integer"},
        "timestampMs": {"type": "integer"},
        "endOfStream": {"type": "boolean"},
    }
}
schemas["MicrophoneOptions"] = {
    "type": "object",
    "properties": {
        "preferredEncoding": {"type": "string", "enum": ["PCM_S16_LE", "PCM_S8", "OPUS"]},
        "preferredSampleRateHz": {"type": "integer"},
        "preferredChannelCount": {"type": "integer"},
        "vendorMode": {"type": "string"},
    }
}
schemas["PlayAudioOptions"] = {
    "type": "object",
    "properties": {
        "speechRate": {"type": "number"},
        "interrupt": {"type": "boolean", "default": True},
    }
}
schemas["ConnectionState"] = {
    "type": "string",
    "enum": ["Disconnected", "Connecting", "Connected", "Error"],
}
schemas["GlassesError"] = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["NotConnected", "PermissionDenied", "Busy", "Timeout", "Transport", "Unsupported"]},
        "message": {"type": "string"},
        "detail": {"type": "string"},
    }
}
schemas["GlassesEvent"] = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["Log", "Warning", "Tap", "AccGyro", "Magnetometer", "KeyEvent", "AmbientLight", "Vsync", "ProximityNear", "ProximityFar"]},
        "data": {"type": "object"},
    }
}
schemas["SlamState"] = {
    "type": "object",
    "description": "SLAM tracking state from 6DoF devices.",
    "properties": {
        "position": {"$ref": "#/components/schemas/FusionVector"},
        "orientation": {"$ref": "#/components/schemas/FusionQuaternion"},
        "trackingConfidence": {"type": "number"},
        "timestamp_ns": {"type": "integer"},
    }
}
schemas["TempleAction"] = {
    "type": "object",
    "description": "Temple button/touchpad action from glasses.",
    "properties": {
        "action": {"type": "string", "enum": ["tap", "double_tap", "triple_tap", "swipe_forward", "swipe_back"]},
        "count": {"type": "integer"},
    }
}
schemas["RingData"] = {
    "type": "object",
    "description": "Pebble ring sensor/interaction data.",
    "properties": {
        "touchPosition": {"type": "object", "properties": {"x": {"type": "number"}, "y": {"type": "number"}}},
        "gesture": {"type": "string"},
    }
}
schemas["GPSData"] = {
    "type": "object",
    "description": "GPS/location data.",
    "properties": {
        "latitude": {"type": "number"},
        "longitude": {"type": "number"},
        "altitude": {"type": "number"},
        "accuracy": {"type": "number"},
        "timestamp": {"type": "integer"},
    }
}
schemas["XRTDevice"] = {
    "type": "object",
    "description": "Monado XR device with 30+ method pointers.",
    "properties": {
        "name": {"type": "string"},
        "tracking_origin_type": {"type": "string"},
        "provides_orientation": {"type": "boolean"},
        "provides_position": {"type": "boolean"},
    }
}
schemas["XRTCompositor"] = {
    "type": "object",
    "description": "Monado XR compositor for frame submission.",
    "properties": {
        "frame_count": {"type": "integer"},
        "predicted_display_time_ns": {"type": "integer"},
    }
}
schemas["XRTSpace"] = {
    "type": "object",
    "description": "Monado XR space for spatial tracking.",
    "properties": {
        "type": {"type": "string", "enum": ["VIEW", "LOCAL", "STAGE", "LOCAL_FLOOR", "UNBOUNDED"]},
        "pose": {"type": "object"},
    }
}
schemas["OverpassQuery"] = {
    "type": "object",
    "description": "Overpass QL query for OpenStreetMap data.",
    "properties": {
        "query": {"type": "string", "description": "Overpass QL or XML query string"},
        "bbox": {"type": "string", "description": "Bounding box (south,west,north,east)"},
        "timeout": {"type": "integer", "default": 25},
        "outputFormat": {"type": "string", "enum": ["json", "xml", "csv"], "default": "json"},
    }
}
schemas["GeminiMapsConfig"] = {
    "type": "object",
    "description": "Gemini Maps grounding configuration.",
    "properties": {
        "model": {"type": "string", "default": "gemini-3-flash-preview"},
        "latitude": {"type": "number"},
        "longitude": {"type": "number"},
        "enableWidget": {"type": "boolean", "default": True},
    }
}
schemas["StreamConfig"] = {
    "type": "object",
    "description": "RayDesk streaming configuration.",
    "properties": {
        "width": {"type": "integer", "default": 1920},
        "height": {"type": "integer", "default": 1080},
        "fps": {"type": "integer", "default": 60},
        "bitrate": {"type": "integer", "default": 20000},
        "audioEnabled": {"type": "boolean", "default": True},
    }
}
schemas["StreamState"] = {
    "type": "string",
    "enum": ["Disconnected", "Connecting", "Pairing", "Streaming", "Error"],
}
schemas["Transform"] = {
    "type": "object",
    "description": "StardustXR 3D transform (translation, rotation, scale).",
    "properties": {
        "translation": {"$ref": "#/components/schemas/FusionVector"},
        "rotation": {"$ref": "#/components/schemas/FusionQuaternion"},
        "scale": {"$ref": "#/components/schemas/FusionVector"},
    }
}
schemas["Hand"] = {
    "type": "object",
    "description": "Full hand skeleton with 26 joints from OpenXR hand tracking.",
    "properties": {
        "thumb": {"type": "object"},
        "index": {"type": "object"},
        "middle": {"type": "object"},
        "ring": {"type": "object"},
        "little": {"type": "object"},
        "palm": {"type": "object"},
        "wrist": {"type": "object"},
    }
}
schemas["AppServerConfig"] = {
    "type": "object",
    "properties": {
        "packageName": {"type": "string"},
        "apiKey": {"type": "string"},
        "port": {"type": "integer", "default": 3000},
        "cloudUrl": {"type": "string"},
    }
}
schemas["BookmarkEntry"] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "url": {"type": "string"},
        "isHome": {"type": "boolean"},
    }
}
schemas["EnvironmentTheme"] = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "skyColor": {"type": "integer"},
        "statusRingColor": {"type": "integer"},
        "dashboardColor": {"type": "integer"},
        "frameColor": {"type": "integer"},
    }
}

# ============================================================
# PATHS — DISPLAY (Domain 1)
# ============================================================
# xg-glass-sdk display
add_path("display", "xg-glass-sdk", "GlassesClient.display",
    "Display text on AR glasses",
    "Display text on the connected AR glasses. Abstracts vendor-specific display APIs behind a unified interface.\n\nRokid: CxrApi openCustomView/updateCustomView with JSON layout, throttled at 350ms.\nFrame: Sends via BLE to frame.display.text().\nMeta: UNSUPPORTED.\nSimulator: Launches SimDisplayActivity.",
    "display",
    [param("text", "string", "Text content to display", True), param("mode", "string", "REPLACE or APPEND"), param("force", "boolean", "Bypass throttling/dedup")],
    "Result<Unit> — Success or failure with GlassesError")

add_path("display", "xg-glass-sdk", "RokidDisplayController.showText",
    "Rokid-specific text display with throttling",
    "Internal display controller for Rokid glasses. Uses CxrApi openCustomView() for first display, updateCustomView() for updates. Tracks lastText to skip duplicate renders. 350ms minimum throttle interval.",
    "display",
    [param("text", "string", "Text to display", True), param("force", "boolean", "Bypass 350ms throttle")])

add_path("display", "xg-glass-sdk", "RokidDisplayController.close",
    "Close Rokid custom view",
    "Closes the custom view on Rokid glasses. Calls CxrApi.closeCustomView().",
    "display")

# MentraOS display
add_path("display", "MentraOS", "LayoutManager.showTextWall",
    "Display full-screen text wall",
    "Display full-screen text on MentraOS-compatible glasses.",
    "display",
    [param("text", "string", "Text to display as full-screen wall", True)])

add_path("display", "MentraOS", "LayoutManager.showDoubleTextWall",
    "Display split-screen text",
    "Display split-screen text with top and bottom sections.",
    "display",
    [param("topText", "string", "Text for top section", True), param("bottomText", "string", "Text for bottom section", True)])

add_path("display", "MentraOS", "LayoutManager.showDashboardCard",
    "Display dashboard card",
    "Display a dashboard-style card with title and content.",
    "display",
    [param("title", "string", "Card title", True), param("content", "string", "Card content", True)])

add_path("display", "MentraOS", "LayoutManager.showReferenceCard",
    "Display reference card",
    "Display a reference card layout with title and body.",
    "display",
    [param("title", "string", "Card title", True), param("body", "string", "Card body", True)])

add_path("display", "MentraOS", "LayoutManager.showBitmapView",
    "Display bitmap image",
    "Display a bitmap image on the glasses.",
    "display",
    [param("data", "string", "Base64-encoded image data", True), param("width", "integer", "Optional width"), param("height", "integer", "Optional height")])

add_path("display", "MentraOS", "LayoutManager.clear",
    "Clear display",
    "Clear all displayed content from the glasses.",
    "display")

# Frame display
add_path("display", "frame-codebase", "frame.display.text",
    "Render text on Frame OLED",
    "Render text on the Brilliant Labs Frame's micro-OLED display at specified position with font/color options.",
    "display",
    [param("text", "string", "Text to render", True), param("x", "number", "X position pixels", True), param("y", "number", "Y position pixels", True)])

add_path("display", "frame-codebase", "frame.display.bitmap",
    "Draw bitmap on Frame display",
    "Draw a bitmap image on the Frame display at specified position.",
    "display",
    [param("x", "number", "X position", True), param("y", "number", "Y position", True), param("width", "number", "Bitmap width", True)])

add_path("display", "frame-codebase", "frame.display.show",
    "Commit Frame display buffer",
    "Commit the current display buffer to the screen. Must be called after text() or bitmap() to make changes visible.",
    "display")

add_path("display", "frame-codebase", "frame.display.assign_color",
    "Assign RGB color to palette index",
    "Assign an RGB color to a palette index for use in text/bitmap rendering.",
    "display",
    [param("index", "integer", "Palette index", True), param("r", "integer", "Red 0-255", True), param("g", "integer", "Green 0-255", True), param("b", "integer", "Blue 0-255", True)])

add_path("display", "frame-codebase", "frame.display.assign_color_ycbcr",
    "Assign YCbCr color to palette index",
    "Assign a YCbCr color to a palette index.",
    "display",
    [param("index", "integer", "Palette index", True), param("y", "integer", "Y component", True), param("cb", "integer", "Cb component", True), param("cr", "integer", "Cr component", True)])

add_path("display", "frame-codebase", "frame.display.set_brightness",
    "Set Frame display brightness",
    "Set the display brightness level on Brilliant Labs Frame.",
    "display",
    [param("level", "integer", "Brightness level", True)])

add_path("display", "frame-codebase", "frame.display.power_save",
    "Frame display power save",
    "Enable or disable display power saving mode.",
    "display",
    [param("enable", "boolean", "Enable power save", True)])

add_path("display", "frame-codebase", "frame.display.write_register",
    "Write display register (advanced)",
    "Write directly to a display controller register (advanced/debug).",
    "display",
    [param("addr", "integer", "Register address", True), param("value", "integer", "Value to write", True)])

# Vuzix Blade 2
add_path("display", "Blade_2_Template_App", "ActionMenuActivity.onCreateActionMenu",
    "Create Vuzix HUD action menu",
    "Override to inflate your menu resource for the Vuzix Blade 2 HUD. Returns true if menu was created.",
    "display")

add_path("display", "Blade_2_Template_App", "ActionMenuActivity.getActionMenuGravity",
    "Set Vuzix HUD menu position",
    "Set menu position. Returns Gravity.RIGHT for side menu or Gravity.CENTER for center menu.",
    "display")

add_path("display", "Blade_2_Template_App", "ActionMenuActivity.alwaysShowActionMenu",
    "Persistent Vuzix HUD menu",
    "Whether the action menu is always visible on the HUD. Return true for persistent menu.",
    "display")

add_path("display", "Blade_2_Template_App", "Template_Widget.updateAppWidget",
    "Update Vuzix HUD widget",
    "Static method to update the HUD app widget content.",
    "display")

add_path("display", "Blade_2_Template_App", "Template_Widget.update",
    "Update widget with theme mode",
    "Update widget with light/dark mode preference.",
    "display",
    [param("isLightMode", "boolean", "Use light theme")])

# Everysight
add_path("display", "everysight-sdk", "Text.builder",
    "Everysight Maverick text builder",
    "Fluent builder API for rendering text on Everysight Maverick glasses. Chain setText(), setResource(), setTextAlign(), setXY(), setForegroundColor(), addTo().",
    "display")

# TAPLINKX3 display
add_path("display", "TAPLINKX3", "DualWebViewGroup",
    "Binocular WebView renderer",
    "Core binocular rendering engine. Duplicates WebView content for stereo AR display (1280x480, 640x480 per eye). Uses PixelCopy for right eye mirroring. Multi-window tab management. Refresh at 16ms (~60fps) normal, 100ms idle.",
    "display")

# RayDesk display
add_path("display", "RayDesk", "StreamRenderer",
    "OpenGL stream renderer",
    "Main OpenGL renderer supporting multiple display modes: flat quad, curved cylinder, and keyhole viewport.",
    "display")

add_path("display", "RayDesk", "CylinderController.zoomIn",
    "Zoom in curved monitor", "Zoom in on the curved virtual monitor.", "display")
add_path("display", "RayDesk", "CylinderController.zoomOut",
    "Zoom out curved monitor", "Zoom out on the curved virtual monitor.", "display")
add_path("display", "RayDesk", "CylinderController.resetZoom",
    "Reset zoom", "Reset curved monitor zoom to default.", "display")
add_path("display", "RayDesk", "CylinderController.setRadius",
    "Set cylinder radius", "Set the curved monitor cylinder radius.",
    "display",
    [param("radius", "number", "Cylinder radius", True), param("immediate", "boolean", "Apply immediately")])
add_path("display", "RayDesk", "CylinderController.getViewMatrix",
    "Get view matrix", "Get the current view matrix as a 16-float array.", "display")
add_path("display", "RayDesk", "CylinderController.getMVPMatrix",
    "Get MVP matrix", "Get model-view-projection matrix.", "display")
add_path("display", "RayDesk", "CylinderController.getLeftEyeMVPMatrix",
    "Get left eye MVP", "Get left eye model-view-projection matrix.", "display")
add_path("display", "RayDesk", "CylinderController.getRightEyeMVPMatrix",
    "Get right eye MVP", "Get right eye model-view-projection matrix.", "display")
add_path("display", "RayDesk", "CylinderMesh",
    "Curved screen geometry", "Generates curved screen geometry for the virtual monitor.", "display")
add_path("display", "RayDesk", "FlatQuadMesh",
    "Flat screen geometry", "Generates flat rectangular geometry for 2D display mode.", "display")
add_path("display", "RayDesk", "SkyboxRenderer",
    "Procedural skybox", "Procedural skybox renderer for the virtual environment.", "display")
add_path("display", "RayDesk", "EnvironmentRenderer",
    "Composite environment renderer", "Combines skybox, status ring, dashboard, and physical frame elements.", "display")

# RayNeo Unity display
add_path("display", "rayneo-setup", "DualeyeDiffrentDisplay",
    "RayNeo per-eye rendering", "Per-eye rendering for RayNeo X2 glasses, allowing different content on left and right eyes.", "display")
add_path("display", "rayneo-setup", "SetCanvasOverlay",
    "RayNeo canvas overlay", "Setup UI canvas as overlay on AR view for HUD elements.", "display")

# MentraOS CoreModule display
add_path("display", "MentraOS", "CoreModule.displayText",
    "WebView display text", "Display text via WebView bridge CoreModule on glasses.", "display",
    [param("text", "string", "Text to display", True)])
add_path("display", "MentraOS", "CoreModule.displayEvent",
    "Display event on glasses", "Send a display event via React Native CoreModule.", "display")
add_path("display", "MentraOS", "CoreModule.clearDisplay",
    "Clear glasses display", "Clear all content from glasses display via CoreModule.", "display")

# Frame LED
add_path("display", "frame-codebase", "frame.led.set_color",
    "Set Frame LED color", "Set the RGB LED color on Brilliant Labs Frame.",
    "display",
    [param("r", "integer", "Red 0-255", True), param("g", "integer", "Green 0-255", True), param("b", "integer", "Blue 0-255", True)])

# MentraOS LED
add_path("display", "MentraOS", "LedModule.rgbLedControl",
    "Control glasses RGB LED", "Control the RGB LED on MentraOS-compatible glasses.",
    "display")

# ============================================================
# PATHS — IMU (Domain 2)
# ============================================================
# Fusion AHRS
add_path("imu", "Fusion", "FusionAhrsInitialise",
    "Initialize AHRS", "Initialize the AHRS structure with default settings. Resets quaternion to identity and enables startup mode.",
    "imu")
add_path("imu", "Fusion", "FusionAhrsSetSettings",
    "Configure AHRS settings", "Configure AHRS algorithm parameters: convention, gain, gyroscope range, rejection thresholds, recovery period.",
    "imu")
add_path("imu", "Fusion", "FusionAhrsUpdate",
    "AHRS update (full)", "Core AHRS update with gyroscope, accelerometer, and magnetometer. Implements revised Madgwick algorithm.",
    "imu",
    [param("deltaTime", "number", "Time since last update in seconds", True)])
add_path("imu", "Fusion", "FusionAhrsUpdateNoMagnetometer",
    "AHRS update (no mag)", "AHRS update without magnetometer. Heading is zeroed during startup phase.",
    "imu")
add_path("imu", "Fusion", "FusionAhrsUpdateExternalHeading",
    "AHRS update (external heading)", "AHRS update using external heading (e.g., GPS compass) instead of magnetometer.",
    "imu",
    [param("heading", "number", "External heading in degrees", True)])
add_path("imu", "Fusion", "FusionAhrsGetQuaternion",
    "Get AHRS quaternion", "Returns the current orientation quaternion describing sensor orientation relative to Earth.",
    "imu", returns="FusionQuaternion {w, x, y, z}")
add_path("imu", "Fusion", "FusionAhrsSetQuaternion",
    "Set AHRS quaternion", "Set the orientation quaternion directly.", "imu")
add_path("imu", "Fusion", "FusionAhrsGetGravity",
    "Get gravity vector", "Returns direction of gravity in sensor frame as a unit vector.", "imu")
add_path("imu", "Fusion", "FusionAhrsGetLinearAcceleration",
    "Get linear acceleration", "Returns linear acceleration (gravity removed) in sensor frame, in g units.", "imu")
add_path("imu", "Fusion", "FusionAhrsGetEarthAcceleration",
    "Get Earth-frame acceleration", "Returns acceleration in Earth frame with gravity removed.", "imu")
add_path("imu", "Fusion", "FusionAhrsGetInternalStates",
    "Get AHRS internal states", "Returns internal algorithm states: accelerationError, magneticError, ignored flags, recovery triggers.", "imu")
add_path("imu", "Fusion", "FusionAhrsGetFlags",
    "Get AHRS flags", "Returns algorithm flags: startup, angularRateRecovery, accelerationRecovery, magneticRecovery.", "imu")
add_path("imu", "Fusion", "FusionAhrsSetHeading",
    "Set AHRS heading", "Sets the heading (yaw) by applying a Z-axis rotation.", "imu",
    [param("heading", "number", "Heading in degrees", True)])
add_path("imu", "Fusion", "FusionAhrsRestart",
    "Restart AHRS", "Restarts the AHRS algorithm. Resets quaternion to identity and enables startup gain ramping.", "imu")

# Fusion Math
add_path("imu", "Fusion", "FusionDegreesToRadians",
    "Degrees to radians", "Converts degrees to radians.", "imu",
    [param("degrees", "number", "Angle in degrees", True)])
add_path("imu", "Fusion", "FusionRadiansToDegrees",
    "Radians to degrees", "Converts radians to degrees.", "imu",
    [param("radians", "number", "Angle in radians", True)])
add_path("imu", "Fusion", "FusionArcSin",
    "Clamped arc sine", "Clamped arc sine. Clamps input to [-1, 1] before computing asin to avoid NaN.", "imu")
add_path("imu", "Fusion", "FusionFastInverseSqrt",
    "Fast inverse square root", "Fast inverse square root using Pizer's implementation. Returns 1/sqrt(x).", "imu")
add_path("imu", "Fusion", "FusionVectorAdd",
    "Vector addition", "Element-wise vector addition {a.x+b.x, a.y+b.y, a.z+b.z}.", "imu")
add_path("imu", "Fusion", "FusionVectorSubtract",
    "Vector subtraction", "Element-wise vector subtraction.", "imu")
add_path("imu", "Fusion", "FusionVectorScale",
    "Vector scalar multiply", "Scalar multiplication of vector.", "imu")
add_path("imu", "Fusion", "FusionVectorCross",
    "Vector cross product", "Cross product a × b.", "imu")
add_path("imu", "Fusion", "FusionVectorDot",
    "Vector dot product", "Dot product a · b.", "imu")
add_path("imu", "Fusion", "FusionVectorNorm",
    "Vector magnitude", "Returns magnitude |v|.", "imu")
add_path("imu", "Fusion", "FusionVectorNormalise",
    "Normalize vector", "Returns unit vector v/|v|. Uses fast inverse sqrt for embedded performance.", "imu")
add_path("imu", "Fusion", "FusionVectorIsZero",
    "Check zero vector", "Returns true if all elements are zero.", "imu")
add_path("imu", "Fusion", "FusionVectorSum",
    "Vector element sum", "Returns sum of all vector elements.", "imu")
add_path("imu", "Fusion", "FusionVectorHadamard",
    "Hadamard product", "Element-wise vector multiplication.", "imu")
add_path("imu", "Fusion", "FusionVectorNormSquared",
    "Vector norm squared", "Returns squared magnitude for efficiency.", "imu")
add_path("imu", "Fusion", "FusionQuaternionProduct",
    "Quaternion product", "Hamilton quaternion product a * b.", "imu")
add_path("imu", "Fusion", "FusionQuaternionNormalise",
    "Normalize quaternion", "Returns unit quaternion q/|q|.", "imu")
add_path("imu", "Fusion", "FusionQuaternionNorm",
    "Quaternion norm", "Returns quaternion magnitude.", "imu")
add_path("imu", "Fusion", "FusionQuaternionAdd",
    "Quaternion addition", "Element-wise quaternion addition.", "imu")
add_path("imu", "Fusion", "FusionQuaternionScale",
    "Quaternion scale", "Scalar multiplication of quaternion.", "imu")
add_path("imu", "Fusion", "FusionQuaternionToMatrix",
    "Quaternion to matrix", "Converts quaternion to 3x3 rotation matrix.", "imu")
add_path("imu", "Fusion", "FusionQuaternionToEuler",
    "Quaternion to Euler", "Converts quaternion to ZYX Euler angles in degrees (roll, pitch, yaw).", "imu")
add_path("imu", "Fusion", "FusionMatrixMultiply",
    "Matrix-vector multiply", "Matrix-vector multiplication M * v.", "imu")

# Fusion Bias
add_path("imu", "Fusion", "FusionBiasInitialise",
    "Initialize bias estimation", "Initialize gyroscope bias estimation (100Hz, 3.0°/s threshold, 3.0s period).", "imu")
add_path("imu", "Fusion", "FusionBiasSetSettings",
    "Configure bias settings", "Configure bias estimation: sampleRate, stationaryThreshold, stationaryPeriod.", "imu")
add_path("imu", "Fusion", "FusionBiasUpdate",
    "Update bias estimation", "Update bias estimation and return offset-corrected gyroscope. Detects stationary periods.", "imu")
add_path("imu", "Fusion", "FusionBiasGetOffset",
    "Get bias offset", "Returns the current estimated gyroscope bias offset.", "imu")
add_path("imu", "Fusion", "FusionBiasSetOffset",
    "Set bias offset", "Manually set gyroscope bias offset.", "imu")

# Fusion Compass & Calibration
add_path("imu", "Fusion", "FusionCompass",
    "Tilt-compensated compass", "Calculates tilt-compensated magnetic heading using accelerometer for tilt.", "imu")
add_path("imu", "Fusion", "FusionModelInertial",
    "Inertial sensor calibration", "Apply inertial sensor calibration: M * s * (raw - offset).", "imu")
add_path("imu", "Fusion", "FusionModelMagnetic",
    "Magnetometer calibration", "Apply magnetometer calibration: S * (raw - h).", "imu")
add_path("imu", "Fusion", "FusionRemap",
    "Remap sensor axes", "Remap sensor axes using one of 24 orthogonal permutations for non-standard mounting.", "imu")

# Fusion Python
add_path("imu", "Fusion", "imufusion.Ahrs",
    "Python AHRS instance", "Create an AHRS instance (Python imufusion wrapper). Use ahrs.update(gyro, accel, mag, dt).", "imu")

# XRLinuxDriver IMU
add_path("imu", "XRLinuxDriver", "normalize_quaternion",
    "Normalize quaternion", "Normalize a quaternion to unit length.", "imu")
add_path("imu", "XRLinuxDriver", "multiply_quaternions",
    "Multiply quaternions", "Hamilton product of two quaternions.", "imu")
add_path("imu", "XRLinuxDriver", "euler_to_quaternion_xyz",
    "Euler to quaternion (XYZ)", "Convert Euler angles (XYZ order) to quaternion.", "imu")
add_path("imu", "XRLinuxDriver", "quaternion_to_euler_zyx",
    "Quaternion to Euler (ZYX)", "Convert quaternion to Euler angles (ZYX order).", "imu")
add_path("imu", "XRLinuxDriver", "vector_rotate",
    "Rotate vector by quaternion", "Rotate a 3D vector by a quaternion.", "imu")
add_path("imu", "XRLinuxDriver", "quat_small_angle_rad",
    "Small angle between quaternions", "Compute the small angle between two quaternions in radians.", "imu")

# XRLinuxDriver Buffer
add_path("imu", "XRLinuxDriver", "create_buffer",
    "Create ring buffer", "Create a ring buffer for smoothing IMU data.", "imu",
    [param("size", "integer", "Buffer size", True)])
add_path("imu", "XRLinuxDriver", "push",
    "Push to ring buffer", "Push value into ring buffer and return rolling average.", "imu")
add_path("imu", "XRLinuxDriver", "create_imu_buffer",
    "Create IMU buffer", "Create a quaternion-aware IMU ring buffer with timestamp tracking.", "imu")
add_path("imu", "XRLinuxDriver", "push_to_imu_buffer",
    "Push to IMU buffer", "Push quaternion sample into IMU buffer. Returns smoothed quaternion and look-ahead prediction.", "imu")
add_path("imu", "XRLinuxDriver", "free_buffer",
    "Free ring buffer", "Free a ring buffer.", "imu")

# PhoenixHeadTracker
add_path("imu", "PhoenixHeadTracker", "StartConnection",
    "Connect to XREAL Air", "Connect to XREAL Air glasses via AirAPI_Windows.dll. Returns 1 on success.", "imu")
add_path("imu", "PhoenixHeadTracker", "StopConnection",
    "Disconnect from XREAL Air", "Disconnect from XREAL Air glasses.", "imu")
add_path("imu", "PhoenixHeadTracker", "GetEuler",
    "Get Euler angles", "Read Euler angles from glasses. Returns pointer to float[3]: [roll, pitch, yaw].", "imu")
add_path("imu", "PhoenixHeadTracker", "KalmanFilter.Update",
    "Kalman filter update", "1D Kalman filter for smoothing IMU deltas. Returns filtered value.", "imu",
    [param("measurement", "number", "Measurement value", True)])

# headset-utils fusion
add_path("imu", "headset-utils", "Fusion.attitude_quaternion",
    "Get attitude quaternion (Rust)", "Get current orientation as unit quaternion from sensor fusion.", "imu")
add_path("imu", "headset-utils", "Fusion.update",
    "Update fusion (Rust)", "Process next IMU sample through the fusion algorithm.", "imu")
add_path("imu", "headset-utils", "NaiveCF.new",
    "Create complementary filter", "Create a naive complementary filter combining accelerometer and gyroscope.", "imu")
add_path("imu", "headset-utils", "any_fusion",
    "Auto-detect fusion", "Auto-detect glasses and create a fusion instance.", "imu")

# RayDesk spatial tracking
add_path("imu", "RayDesk", "HeadGazeCursor.updateHeadOrientation",
    "Update head orientation", "Update cursor from Euler angles.", "imu",
    [param("yaw", "number", "Yaw degrees", True), param("pitch", "number", "Pitch degrees", True)])
add_path("imu", "RayDesk", "HeadGazeCursor.updateFromQuaternion",
    "Update from quaternion", "Update cursor from raw quaternion sensor values.", "imu")
add_path("imu", "RayDesk", "HeadGazeCursor.getCursorPosition",
    "Get cursor position", "Get current cursor position mapped from head orientation.", "imu")
add_path("imu", "RayDesk", "HeadGazeCursor.recenter",
    "Recenter cursor", "Reset cursor to center.", "imu")
add_path("imu", "RayDesk", "OneEuroFilter",
    "1€ noise filter", "1€ noise filter for smooth head tracking. Combines low-pass filtering with speed-adaptive cutoff.", "imu")
add_path("imu", "RayDesk", "Quaternion.fromSensorValues",
    "Quaternion from sensor", "Create quaternion from raw sensor float array.", "imu")
add_path("imu", "RayDesk", "Quaternion.fromYawPitch",
    "Quaternion from yaw/pitch", "Create quaternion from yaw and pitch degrees.", "imu")
add_path("imu", "RayDesk", "Quaternion.multiply",
    "Quaternion multiply (Kotlin)", "Multiply two quaternions.", "imu")
add_path("imu", "RayDesk", "Quaternion.toYawPitch",
    "Quaternion to yaw/pitch", "Extract yaw and pitch from quaternion.", "imu")

# spidgets-3dof
add_path("imu", "spidgets-3dof", "broadcastCam",
    "Broadcast camera angles", "Send camera Euler angles [x,y,z] to all Socket.IO clients.", "imu")
add_path("imu", "spidgets-3dof", "calibrate",
    "Tare/calibrate IMU", "Tare/zero the IMU position (recalibrate origin).", "imu")

# RayNeo vendor IMU
add_path("imu", "XRLinuxDriver", "RegisterIMUEventCallback",
    "Register RayNeo IMU callback", "Register callback for IMU events from RayNeo glasses.", "imu")
add_path("imu", "XRLinuxDriver", "OpenIMU",
    "Open RayNeo IMU", "Start IMU streaming from RayNeo glasses.", "imu")
add_path("imu", "XRLinuxDriver", "CloseIMU",
    "Close RayNeo IMU", "Stop IMU streaming from RayNeo glasses.", "imu")
add_path("imu", "XRLinuxDriver", "GetHeadTrackerPose",
    "Get RayNeo head tracker pose", "Get 6DoF pose from RayNeo: rotation[4], position[3], timestamp.", "imu")
add_path("imu", "XRLinuxDriver", "Recenter",
    "Recenter RayNeo tracking", "Recenter the RayNeo tracking origin.", "imu")

# VITURE IMU
add_path("imu", "XRLinuxDriver", "register_raw_callback",
    "Register VITURE raw IMU", "Register raw IMU callback for VITURE glasses.", "imu")
add_path("imu", "XRLinuxDriver", "register_pose_callback",
    "Register VITURE pose callback", "Register pose callback for VITURE glasses.", "imu")
add_path("imu", "XRLinuxDriver", "open_imu",
    "Open VITURE IMU", "Start VITURE IMU streaming with specified mode and frequency.", "imu")
add_path("imu", "XRLinuxDriver", "close_imu",
    "Close VITURE IMU", "Stop VITURE IMU streaming.", "imu")

# ============================================================
# PATHS — CAMERA (Domain 3)
# ============================================================
add_path("camera", "xg-glass-sdk", "GlassesClient.capturePhoto",
    "Capture photo from glasses",
    "Capture a photo from the glasses camera. Returns JPEG bytes with metadata.\nRokid: takeGlassPhoto → syncSingleFile → readBytes\nMeta: DAT SDK StreamSession → capturePhoto\nOmi: BLE write 0x05, receive chunks, EOF=0xFFFF\nFrame: BLE via frame_msg.RxPhoto",
    "camera",
    [param("quality", "integer", "JPEG quality 0-100"), param("targetWidth", "integer", "Target width"), param("targetHeight", "integer", "Target height"), param("timeoutMs", "integer", "Capture timeout ms")])

add_path("camera", "frame-codebase", "frame.file.open",
    "Open file for camera storage", "Open a file for camera image storage on Frame's LittleFS filesystem.", "camera",
    [param("path", "string", "File path", True), param("mode", "string", "File mode", True)])

add_path("camera", "headset-utils", "NrealLightSlamCamera.new",
    "Create SLAM camera", "Access the XREAL Light's SLAM tracking cameras.", "camera")
add_path("camera", "headset-utils", "NrealLightSlamCamera.get_frame",
    "Get SLAM camera frame", "Get a frame from the SLAM camera with timeout.", "camera",
    [param("timeout_ms", "integer", "Timeout in ms", True)])

add_path("camera", "rayneo-setup", "ShareCameraCtrl",
    "RayNeo camera sharing", "Camera sharing control for RayNeo X2 glasses.", "camera")
add_path("camera", "rayneo-setup", "CameraPermissionRequest",
    "RayNeo camera permission", "Request camera permissions on RayNeo platform.", "camera")

add_path("camera", "MentraOS", "CoreModule.photoRequest",
    "Request photo capture", "Request photo capture via MentraOS CoreModule with size, compression, flash options.", "camera")
add_path("camera", "MentraOS", "CoreModule.startBufferRecording",
    "Start buffer recording", "Start buffered video recording.", "camera")
add_path("camera", "MentraOS", "CoreModule.stopBufferRecording",
    "Stop buffer recording", "Stop buffered video recording.", "camera")
add_path("camera", "MentraOS", "CoreModule.startVideoRecording",
    "Start video recording", "Start video recording on glasses.", "camera")
add_path("camera", "MentraOS", "CoreModule.stopVideoRecording",
    "Stop video recording", "Stop video recording on glasses.", "camera")

# ============================================================
# PATHS — AUDIO (Domain 4)
# ============================================================
add_path("audio", "xg-glass-sdk", "GlassesClient.playAudio",
    "Play audio on glasses",
    "Play audio on glasses (TTS or raw bytes).\nRokid: CxrApi sendGlobalTtsContent, raw PCM via AudioTrack\nMeta: PCM via AudioTrack (A2DP)\nSimulator: Android TextToSpeech",
    "audio",
    [param("source_type", "string", "tts or raw", True), param("text", "string", "TTS text"), param("speechRate", "number", "TTS rate 0.75-4.0"), param("interrupt", "boolean", "Interrupt playback")])

add_path("audio", "xg-glass-sdk", "GlassesClient.startMicrophone",
    "Start microphone capture",
    "Start microphone capture, returning a streaming audio session.\nRokid: CxrApi openAudioRecord (PCM/OPUS)\nMeta: AudioRecord via Bluetooth HFP (8kHz mono)\nOmi: OPUS 16kHz mono via BLE\nFrame: BLE audio via frame_msg",
    "audio",
    [param("preferredEncoding", "string", "PCM_S16_LE, OPUS"), param("preferredSampleRateHz", "integer", "Sample rate"), param("preferredChannelCount", "integer", "Channels")])

add_path("audio", "xg-glass-sdk", "MicrophoneSession.stop",
    "Stop microphone", "Stop the microphone capture session.", "audio")

add_path("audio", "TAPLINKX3", "GroqAudioService.startRecording",
    "Start Groq audio recording", "Start M4A recording (44.1kHz AAC 128kbps) for Groq Whisper transcription.", "audio")
add_path("audio", "TAPLINKX3", "GroqAudioService.stopRecording",
    "Stop and transcribe", "Stop recording and send to Groq for transcription.", "audio")
add_path("audio", "TAPLINKX3", "GroqAudioService.hasApiKey",
    "Check Groq API key", "Check if Groq API key is configured.", "audio")
add_path("audio", "TAPLINKX3", "GroqAudioService.setApiKey",
    "Set Groq API key", "Set Groq API key for Whisper transcription.", "audio",
    [param("key", "string", "Groq API key", True)])

add_path("audio", "beatsync", "WebSocket.PLAY",
    "BeatSync synchronized play", "Request synchronized play across all connected devices.", "audio")
add_path("audio", "beatsync", "WebSocket.PAUSE",
    "BeatSync synchronized pause", "Request synchronized pause.", "audio")
add_path("audio", "beatsync", "WebSocket.NTP_REQUEST",
    "BeatSync NTP time sync", "NTP-inspired time synchronization: client sends t0, server stamps t1/t2. EMA smoothing alpha=0.2.", "audio")
add_path("audio", "beatsync", "WebSocket.SET_GLOBAL_VOLUME",
    "BeatSync set volume", "Set master volume for all devices.", "audio")
add_path("audio", "beatsync", "WebSocket.SEARCH_MUSIC",
    "BeatSync search music", "Search external music sources.", "audio")
add_path("audio", "beatsync", "WebSocket.STREAM_MUSIC",
    "BeatSync stream music", "Start streaming music from URL.", "audio")
add_path("audio", "beatsync", "WebSocket.START_SPATIAL_AUDIO",
    "BeatSync start spatial", "Enable spatial audio mode.", "audio")
add_path("audio", "beatsync", "WebSocket.STOP_SPATIAL_AUDIO",
    "BeatSync stop spatial", "Disable spatial audio mode.", "audio")
add_path("audio", "beatsync", "WebSocket.SET_METRONOME",
    "BeatSync set metronome", "Configure metronome click (bpm, volume).", "audio")
add_path("audio", "beatsync", "HTTP.upload_presigned_url",
    "BeatSync get upload URL", "POST /upload/get-presigned-url — Get R2 presigned upload URL.", "audio")

add_path("audio", "mobileapp", "AudioRecorder.startRecording",
    "Pebble ring start recording", "Start audio recording from Pebble smart ring.", "audio")
add_path("audio", "mobileapp", "AudioRecorder.stopRecording",
    "Pebble ring stop recording", "Stop audio recording from Pebble ring.", "audio")
add_path("audio", "mobileapp", "AudioPlayer.playRaw",
    "Pebble ring play raw audio", "Play raw audio samples on Pebble ring.", "audio")
add_path("audio", "mobileapp", "AudioPlayer.playAAC",
    "Pebble ring play AAC", "Play AAC encoded audio on Pebble ring.", "audio")

add_path("audio", "MentraOS", "CoreModule.setMicState",
    "Set mic state", "Enable/disable microphone with options for PCM data, transcript, VAD bypass.", "audio")
add_path("audio", "MentraOS", "CoreModule.restartTranscriber",
    "Restart transcriber", "Restart the on-device speech-to-text transcriber.", "audio")
add_path("audio", "MentraOS", "CoreModule.setGlassesMediaVolume",
    "Set glasses volume", "Set media volume on glasses.", "audio",
    [param("level", "integer", "Volume level", True)])
add_path("audio", "MentraOS", "CoreModule.getGlassesMediaVolume",
    "Get glasses volume", "Get current media volume from glasses.", "audio")

add_path("audio", "MentraOS", "AppSession.onTranscription",
    "Subscribe to transcription", "Subscribe to real-time speech transcription events from glasses microphone.", "audio")

# ============================================================
# PATHS — BLE (Domain 5)
# ============================================================
add_path("ble", "xg-glass-sdk", "OmiGlassesClient.BLE_UUIDs",
    "Omi BLE service UUIDs", "Omi Glass BLE GATT UUIDs: AUDIO_SERVICE, AUDIO_DATA, AUDIO_CODEC, BATTERY, PHOTO_CONTROL, PHOTO_DATA, TIME_SYNC.", "ble")

add_path("ble", "frame-codebase", "bluetooth_setup",
    "Frame BLE setup", "Initialize BLE stack on the nRF52840 SoC.", "ble")
add_path("ble", "frame-codebase", "bluetooth_is_paired",
    "Check Frame BLE paired", "Check if Frame is paired with a phone.", "ble")
add_path("ble", "frame-codebase", "bluetooth_unpair",
    "Unpair Frame BLE", "Unpair the Frame from connected device.", "ble")
add_path("ble", "frame-codebase", "bluetooth_is_connected",
    "Check Frame BLE connected", "Check if Frame BLE is currently connected.", "ble")
add_path("ble", "frame-codebase", "bluetooth_send_data",
    "Send data over Frame BLE", "Send data over BLE to the connected phone.", "ble",
    [param("length", "integer", "Data length", True)])

add_path("ble", "xg-glass-sdk", "RokidGlassesClient.BLE",
    "Rokid BLE + Wi-Fi P2P", "Rokid connection flow: BLE scan → initBluetooth → connectBluetooth → initWifiP2P. Service UUID: 00009100-0000-1000-8000-00805f9b34fb.", "ble")

add_path("ble", "mobileapp", "RingCompanionDeviceManager.openPairingPicker",
    "Pebble ring pairing picker", "Open BLE companion device pairing picker for Pebble ring.", "ble")
add_path("ble", "mobileapp", "RingCompanionDeviceManager.unregister",
    "Unregister ring device", "Unregister a paired Pebble ring satellite device.", "ble")
add_path("ble", "mobileapp", "RingCompanionDeviceManager.unregisterAll",
    "Unregister all ring devices", "Unregister all paired Pebble ring devices.", "ble")

add_path("ble", "MentraOS", "WebSocketTransport",
    "MentraOS WebSocket transport", "WebSocket-based transport for MentraOS cloud communication.", "ble")

add_path("ble", "MentraOS", "CoreModule.connectDefault",
    "Connect to default glasses", "Connect to the default/last-known glasses device.", "ble")
add_path("ble", "MentraOS", "CoreModule.connectByName",
    "Connect glasses by name", "Connect to glasses by device name.", "ble",
    [param("deviceName", "string", "Device name", True)])
add_path("ble", "MentraOS", "CoreModule.connectSimulated",
    "Connect simulated glasses", "Connect to simulated glasses for development.", "ble")
add_path("ble", "MentraOS", "CoreModule.disconnect",
    "Disconnect glasses", "Disconnect from current glasses.", "ble")
add_path("ble", "MentraOS", "CoreModule.forget",
    "Forget glasses device", "Forget the paired glasses device.", "ble")
add_path("ble", "MentraOS", "CoreModule.findCompatibleDevices",
    "Find compatible glasses", "Scan for compatible glasses devices.", "ble",
    [param("deviceModel", "string", "Device model filter", True)])
add_path("ble", "MentraOS", "CoreModule.requestWifiScan",
    "Request Wi-Fi scan", "Request glasses to scan for Wi-Fi networks.", "ble")
add_path("ble", "MentraOS", "CoreModule.sendWifiCredentials",
    "Send Wi-Fi credentials", "Send Wi-Fi SSID and password to glasses.", "ble",
    [param("ssid", "string", "Wi-Fi SSID", True), param("password", "string", "Wi-Fi password", True)])

# ============================================================
# PATHS — GESTURE (Domain 6)
# ============================================================
add_path("gesture", "XRLinuxDriver", "multitap_detection",
    "Multi-tap gesture detection", "Detects double-tap (recenter) and triple-tap (recalibrate) from IMU acceleration spikes.", "gesture")

add_path("gesture", "TAPLINKX3", "CustomKeyboardView.setOnKeyboardActionListener",
    "Set keyboard listener", "Set callback listener for AR keyboard events.", "gesture")
add_path("gesture", "TAPLINKX3", "CustomKeyboardView.updateHover",
    "Update keyboard hover", "Update hover position from head tracking.", "gesture",
    [param("x", "number", "X position", True), param("y", "number", "Y position", True)])
add_path("gesture", "TAPLINKX3", "CustomKeyboardView.clearHover",
    "Clear keyboard hover", "Clear hover highlight.", "gesture")
add_path("gesture", "TAPLINKX3", "CustomKeyboardView.handleAnchoredTap",
    "Handle anchored tap", "Process tap in anchored keyboard mode.", "gesture",
    [param("x", "number", "X position", True), param("y", "number", "Y position", True)])
add_path("gesture", "TAPLINKX3", "CustomKeyboardView.copyStateFrom",
    "Copy keyboard state", "Sync state between left/right eye keyboards.", "gesture")

add_path("gesture", "rayneo-setup", "SampleCubeCtrl.OnPointerEnter",
    "RayNeo gaze enter", "Gaze-based pointer enters object on RayNeo X2.", "gesture")
add_path("gesture", "rayneo-setup", "SampleCubeCtrl.OnPointerExit",
    "RayNeo gaze exit", "Gaze-based pointer exits object.", "gesture")
add_path("gesture", "rayneo-setup", "SampleCubeCtrl.OnPointerClick",
    "RayNeo gaze click", "Gaze-based click/tap on object.", "gesture")
add_path("gesture", "rayneo-setup", "TestTouchEvent",
    "RayNeo touch event", "Touch event handling for RayNeo ring controller.", "gesture")
add_path("gesture", "rayneo-setup", "RingTouchCube",
    "RayNeo ring touch", "Ring-based touch interaction with 3D objects.", "gesture")

add_path("gesture", "MentraOS", "AppSession.onButtonPress",
    "Subscribe to button press", "Subscribe to physical button press events on glasses.", "gesture")
add_path("gesture", "MentraOS", "AppSession.onTouchEvent",
    "Subscribe to touch events", "Subscribe to touch gesture events on glasses.", "gesture",
    [param("gesture", "string", "Gesture type", True)])

add_path("gesture", "stardust-core", "Hand",
    "Hand tracking skeleton", "Full hand skeleton with 26 joints from OpenXR hand tracking. Includes Thumb, Finger structs.", "gesture")
add_path("gesture", "stardust-core", "Finger.length",
    "Get finger length", "Total finger length from hand tracking.", "gesture")
add_path("gesture", "stardust-core", "Finger.direction",
    "Get finger direction", "Finger pointing direction vector.", "gesture")

# ============================================================
# PATHS — SPATIAL (Domain 7)
# ============================================================
add_path("spatial", "OpenXR", "xrCreateInstance",
    "Create OpenXR instance", "Create an OpenXR instance. Root object for all XR operations.", "spatial")
add_path("spatial", "OpenXR", "xrCreateSession",
    "Create XR session", "Create an XR session with graphics binding.", "spatial")
add_path("spatial", "OpenXR", "xrCreateReferenceSpace",
    "Create reference space", "Create reference space: VIEW (head-locked), LOCAL (recenterable), STAGE (room-scale), LOCAL_FLOOR, UNBOUNDED.", "spatial")
add_path("spatial", "OpenXR", "xrLocateSpace",
    "Locate space", "Locate one space relative to another at a given time. Returns pose with tracking confidence.", "spatial")
add_path("spatial", "OpenXR", "xrWaitFrame",
    "Wait for frame", "Wait for the next frame to render. Returns predicted display time.", "spatial")
add_path("spatial", "OpenXR", "xrBeginFrame",
    "Begin frame", "Signal the start of frame rendering.", "spatial")
add_path("spatial", "OpenXR", "xrEndFrame",
    "End frame", "Submit rendered layers: PROJECTION, QUAD, CYLINDER, EQUIRECT, PASSTHROUGH.", "spatial")
add_path("spatial", "OpenXR", "xrLocateViews",
    "Locate views", "Get per-eye view poses and field of view for rendering.", "spatial")
add_path("spatial", "OpenXR", "xrSyncActions",
    "Sync actions", "Synchronize action state with the runtime.", "spatial")
add_path("spatial", "OpenXR", "xrGetActionState",
    "Get action state", "Read current state of input actions (Boolean, Float, Vector2f, Pose).", "spatial")
add_path("spatial", "OpenXR", "xrApplyHapticFeedback",
    "Apply haptic feedback", "Apply haptic feedback to a controller.", "spatial")

# Monado
add_path("spatial", "Monado", "xrt_device.update_inputs",
    "Update device inputs", "Refresh input state on Monado XR device.", "spatial")
add_path("spatial", "Monado", "xrt_device.get_tracked_pose",
    "Get tracked pose", "Get 6DoF pose from Monado device.", "spatial")
add_path("spatial", "Monado", "xrt_device.get_hand_tracking",
    "Get hand tracking", "Get hand joint positions from Monado device.", "spatial")
add_path("spatial", "Monado", "xrt_device.get_face_tracking",
    "Get face tracking", "Get facial expressions from Monado device.", "spatial")
add_path("spatial", "Monado", "xrt_device.get_body_joints",
    "Get body joints", "Get full body tracking joints.", "spatial")
add_path("spatial", "Monado", "xrt_device.set_output",
    "Set haptic output", "Set haptic output on Monado device.", "spatial")
add_path("spatial", "Monado", "xrt_device.begin_plane_detection_ext",
    "Begin plane detection", "Start plane detection on Monado device.", "spatial")
add_path("spatial", "Monado", "xrt_device.get_plane_detections_ext",
    "Get detected planes", "Get detected planes from Monado device.", "spatial")
add_path("spatial", "Monado", "xrt_device.compute_distortion",
    "Compute lens distortion", "Compute lens distortion correction.", "spatial")
add_path("spatial", "Monado", "xrt_device.get_battery_status",
    "Get device battery", "Get battery level from Monado device.", "spatial")
add_path("spatial", "Monado", "xrt_device.set_brightness",
    "Set display brightness", "Set display brightness on Monado device.", "spatial")

add_path("spatial", "Monado", "xrt_space_overseer.create_offset_space",
    "Create offset space", "Create a space with offset from parent.", "spatial")
add_path("spatial", "Monado", "xrt_space_overseer.create_pose_space",
    "Create pose space", "Create a space from device pose.", "spatial")
add_path("spatial", "Monado", "xrt_space_overseer.locate_space",
    "Locate space (Monado)", "Locate one space relative to another.", "spatial")
add_path("spatial", "Monado", "xrt_space_overseer.locate_spaces",
    "Batch locate spaces", "Batch locate multiple spaces.", "spatial")
add_path("spatial", "Monado", "xrt_space_overseer.recenter_local_spaces",
    "Recenter local spaces", "Recenter all local spaces.", "spatial")

# RayNeo SLAM
add_path("spatial", "rayneo-setup", "SlamDemoCtrl.OnPostUpdate",
    "RayNeo SLAM pose callback", "SLAM pose callback — receives 6DoF position+rotation for cube placement.", "spatial")
add_path("spatial", "rayneo-setup", "TestPlaneDetection",
    "RayNeo plane detection", "Plane detection visualization using RayNeo ARDK.", "spatial")
add_path("spatial", "rayneo-setup", "ResetHeadTrack.OnReset",
    "Reset RayNeo head tracking", "Reset head tracking origin on RayNeo.", "spatial")

# XRLinuxDriver IPC
add_path("spatial", "XRLinuxDriver", "setup_ipc_values",
    "Setup IPC shared memory", "Set up shared memory IPC for pose data communication between driver and applications.", "spatial")
add_path("spatial", "XRLinuxDriver", "setup_ipc_value",
    "Setup individual IPC value", "Setup a single named shared memory value.", "spatial")

# RayNeo vendor
add_path("spatial", "XRLinuxDriver", "StartXR",
    "Start RayNeo XR", "Start XR mode on RayNeo glasses.", "spatial")
add_path("spatial", "XRLinuxDriver", "StopXR",
    "Stop RayNeo XR", "Stop XR mode on RayNeo glasses.", "spatial")
add_path("spatial", "XRLinuxDriver", "SwitchTo2D",
    "Switch RayNeo to 2D", "Switch RayNeo display to 2D mode.", "spatial")
add_path("spatial", "XRLinuxDriver", "SwitchTo3D",
    "Switch RayNeo to 3D", "Switch RayNeo display to 3D/SBS mode.", "spatial")

# ============================================================
# PATHS — ML (Domain 8)
# ============================================================
add_path("ml", "frame-codebase", "tflm_initialize",
    "Init TFLite float model", "Initialize TensorFlow Lite Micro runtime for hello world float model.", "ml")
add_path("ml", "frame-codebase", "tflm_infer",
    "TFLite float inference", "Run inference on the hello world float model.", "ml",
    [param("input", "number", "Input value", True)])
add_path("ml", "frame-codebase", "tflm_initialize_int8",
    "Init TFLite int8 model", "Initialize the quantized int8 hello world model.", "ml")
add_path("ml", "frame-codebase", "tflm_infer_int8",
    "TFLite int8 inference", "Run inference on int8 quantized model.", "ml")
add_path("ml", "frame-codebase", "fomo_initialize",
    "Init FOMO model", "Initialize FOMO (Faster Objects, More Objects) detection model.", "ml")
add_path("ml", "frame-codebase", "fomo_infer",
    "FOMO object detection", "Run FOMO object detection on a grayscale image.", "ml")
add_path("ml", "frame-codebase", "fomo_is_initialized",
    "Check FOMO initialized", "Check if FOMO model is initialized.", "ml")
add_path("ml", "frame-codebase", "person_detect_initialize",
    "Init person detection", "Initialize person detection (Visual Wake Words) model.", "ml")
add_path("ml", "frame-codebase", "person_detect_infer",
    "Person detection inference", "Run person detection inference on input image.", "ml")
add_path("ml", "frame-codebase", "person_detect_is_initialized",
    "Check person detect initialized", "Check if person detection model is initialized.", "ml")
add_path("ml", "frame-codebase", "tflm_get_float_model_info",
    "Get float model info", "Get input/output info for the float TFLite model.", "ml")
add_path("ml", "frame-codebase", "tflm_get_int8_model_info",
    "Get int8 model info", "Get input/output info for the int8 TFLite model.", "ml")

# SAM3
add_path("ml", "sam3", "build_sam3_predictor",
    "Build SAM3 image predictor", "Build a SAM3 image predictor for single-image segmentation.", "ml",
    [param("checkpoint_path", "string", "Model checkpoint path", True), param("device", "string", "cuda or cpu")])
add_path("ml", "sam3", "build_sam3_video_predictor",
    "Build SAM3 video predictor", "Build a SAM3 video predictor for video segmentation with tracking.", "ml")
add_path("ml", "sam3", "build_sam3_image_model",
    "Build SAM3 image model", "Build core SAM3 image model.", "ml")
add_path("ml", "sam3", "download_ckpt_from_hf",
    "Download SAM3 checkpoint", "Download SAM3 checkpoint from HuggingFace.", "ml")
add_path("ml", "sam3", "PromptEncoder.forward",
    "SAM3 prompt encoding", "Encode prompts (points, boxes, masks) into embeddings for SAM3.", "ml")
add_path("ml", "sam3", "MaskDecoder.forward",
    "SAM3 mask decoding", "Decode masks from image and prompt embeddings.", "ml")

# Groq LLM
add_path("ml", "TAPLINKX3", "GroqInterface.chatWithGroq",
    "Chat with Groq LLM", "Chat with Groq llama3-70b-8192 model via JavaScript bridge.", "ml",
    [param("message", "string", "Chat message", True), param("historyJson", "string", "Chat history JSON"), param("ttsEnabled", "boolean", "Enable TTS")])
add_path("ml", "TAPLINKX3", "GroqInterface.speakWithOrpheus",
    "TTS via Orpheus", "Text-to-speech via Orpheus engine.", "ml",
    [param("text", "string", "Text to speak", True)])
add_path("ml", "TAPLINKX3", "GroqInterface.ping",
    "Ping Groq interface", "Returns 'pong' for connectivity check.", "ml")
add_path("ml", "TAPLINKX3", "GroqInterface.getActivePageUrl",
    "Get active page URL", "Get current browser page URL.", "ml")
add_path("ml", "TAPLINKX3", "GroqInterface.openUrlInNewTab",
    "Open URL in new tab", "Open URL in a new browser tab.", "ml",
    [param("url", "string", "URL to open", True)])

# Pebble Ring AI
add_path("ml", "mobileapp", "SendBeeperMessageTool",
    "MCP: Send Beeper message", "MCP tool for sending messages via Beeper.", "ml")
add_path("ml", "mobileapp", "SearchBeeperForContactTool",
    "MCP: Search Beeper contacts", "MCP tool for searching Beeper contacts.", "ml")
add_path("ml", "mobileapp", "SetAlarmTool",
    "MCP: Set alarm", "MCP tool for setting alarms.", "ml")
add_path("ml", "mobileapp", "SetTimerTool",
    "MCP: Set timer", "MCP tool for setting timers.", "ml")
add_path("ml", "mobileapp", "CactusModelProvider",
    "On-device AI model", "On-device AI model provider using Cactus framework.", "ml")

# Frame ML experiments
add_path("ml", "frame-codebase", "experiment_get_name",
    "Get experiment name", "Get the name of the current ML experiment.", "ml")
add_path("ml", "frame-codebase", "experiment_register_lua_functions",
    "Register ML Lua functions", "Register ML experiment functions into Lua VM.", "ml")
add_path("ml", "frame-codebase", "jpeg_decode_grayscale_scaled",
    "Decode JPEG grayscale (scaled)", "Decode JPEG to grayscale with scaling for ML input.", "ml")
add_path("ml", "frame-codebase", "jpeg_decode_rgb_scaled",
    "Decode JPEG RGB (scaled)", "Decode JPEG to RGB with scaling for ML input.", "ml")
add_path("ml", "frame-codebase", "upscale_90_to_96_with_rotation",
    "Upscale 90→96 with rotation", "Upscale and rotate image from 90px to 96px for model input.", "ml")

# SAM3 visualization
add_path("ml", "sam3", "generate_colors",
    "Generate visualization colors", "Generate N distinct colors for mask visualization.", "ml")
add_path("ml", "sam3", "visualize_frame_output",
    "Visualize frame output", "Visualize segmentation output for a video frame.", "ml")
add_path("ml", "sam3", "save_masklet_video",
    "Save masklet video", "Save segmented masklet video output.", "ml")

# ============================================================
# PATHS — GPS (Domain 9)
# ============================================================
add_path("gps", "rayneo-setup", "TestIPC",
    "RayNeo GPS via IPC", "IPC demo accessing GPS data from RayNeo Mercury platform.", "gps")
add_path("gps", "TAPLINKX3", "GPS_Integration",
    "TAPLINKX3 GPS integration", "GPS via RayNeo Mercury IPC (com.ffalconxr.mercury.ipc.Launcher). Coordinates injected into Groq system prompts.", "gps")
add_path("gps", "MentraOS", "AppSession.location",
    "MentraOS location module", "Location module for accessing glasses GPS/location data.", "gps")

# ============================================================
# PATHS — DEVICE (Domain 10)
# ============================================================
add_path("device", "xg-glass-sdk", "GlassesClient.connect",
    "Connect to glasses", "Establish connection to the glasses. Transport varies by device.", "device")
add_path("device", "xg-glass-sdk", "GlassesClient.disconnect",
    "Disconnect from glasses", "Tear down connection. Safe to call multiple times.", "device")

add_path("device", "MentraOS", "AppServer.constructor",
    "Create MentraOS app server", "Create a new AppServer (extends Hono) with config: packageName, apiKey, port, cloudUrl.", "device")
add_path("device", "MentraOS", "AppServer.onSession",
    "Handle new session", "Register handler for new glasses sessions.", "device")
add_path("device", "MentraOS", "AppServer.start",
    "Start MentraOS server", "Start the MentraOS app server.", "device")
add_path("device", "MentraOS", "AppSession.connect",
    "Connect MentraOS session", "Connect app session to MentraOS cloud.", "device",
    [param("sessionId", "string", "Session ID", True)])
add_path("device", "MentraOS", "AppSession.disconnect",
    "Disconnect MentraOS session", "Disconnect app session from cloud.", "device")
add_path("device", "MentraOS", "AppSession.releaseOwnership",
    "Release session ownership", "Release ownership of the session.", "device")
add_path("device", "MentraOS", "AppSession.onHeadPosition",
    "Subscribe to head position", "Subscribe to head position events.", "device")
add_path("device", "MentraOS", "AppSession.onPhoneNotification",
    "Subscribe to phone notifications", "Subscribe to phone notification events.", "device")
add_path("device", "MentraOS", "AppSession.onGlassesBattery",
    "Subscribe to battery events", "Subscribe to glasses battery level events.", "device")
add_path("device", "MentraOS", "AppSession.onConnectionState",
    "Subscribe to connection state", "Subscribe to connection state changes.", "device")
add_path("device", "MentraOS", "AppSession.discoverAppUsers",
    "Discover app users", "Discover other users of this app.", "device",
    [param("domain", "string", "Discovery domain", True)])
add_path("device", "MentraOS", "AppSession.isUserActive",
    "Check user active", "Check if a user is currently active.", "device",
    [param("userId", "string", "User ID", True)])
add_path("device", "MentraOS", "AppSession.getUserCount",
    "Get user count", "Get count of active users in a domain.", "device")
add_path("device", "MentraOS", "AppSession.broadcastToAppUsers",
    "Broadcast to users", "Broadcast message to all app users.", "device")
add_path("device", "MentraOS", "AppSession.sendDirectMessage",
    "Send direct message", "Send direct message to a specific user.", "device",
    [param("targetUserId", "string", "Target user ID", True)])
add_path("device", "MentraOS", "AppSession.joinAppRoom",
    "Join app room", "Join a multi-user app room.", "device",
    [param("roomId", "string", "Room ID", True)])
add_path("device", "MentraOS", "AppSession.leaveAppRoom",
    "Leave app room", "Leave a multi-user app room.", "device")

# XRLinuxDriver device management
add_path("device", "XRLinuxDriver", "connection_pool_init",
    "Init connection pool", "Initialize the device connection pool with pose handling callbacks.", "device")
add_path("device", "XRLinuxDriver", "connection_pool_handle_device_added",
    "Handle device added", "Handle a new device being detected (USB hotplug).", "device")
add_path("device", "XRLinuxDriver", "connection_pool_is_connected",
    "Check device connected", "Check if any device is connected.", "device")
add_path("device", "XRLinuxDriver", "connection_pool_primary_device",
    "Get primary device", "Get the primary (active) device properties.", "device")
add_path("device", "XRLinuxDriver", "connection_pool_device_is_sbs_mode",
    "Check SBS mode", "Check if device is in side-by-side 3D mode.", "device")
add_path("device", "XRLinuxDriver", "connection_pool_device_set_sbs_mode",
    "Set SBS mode", "Enable/disable side-by-side 3D mode.", "device",
    [param("enabled", "boolean", "Enable SBS mode", True)])
add_path("device", "XRLinuxDriver", "connection_pool_disconnect_all",
    "Disconnect all devices", "Disconnect all connected devices.", "device")
add_path("device", "XRLinuxDriver", "connection_pool_connect_active",
    "Connect active device", "Connect to the active device.", "device")
add_path("device", "XRLinuxDriver", "driver_handle_pose",
    "Handle pose data", "Process incoming pose data from device.", "device")
add_path("device", "XRLinuxDriver", "driver_reference_pose",
    "Get reference pose", "Get the reference pose for calibration.", "device")
add_path("device", "XRLinuxDriver", "driver_disabled",
    "Check driver disabled", "Check if the driver is currently disabled.", "device")

# headset-utils
add_path("device", "headset-utils", "ARGlasses.serial",
    "Get glasses serial", "Get serial number from AR glasses.", "device")
add_path("device", "headset-utils", "ARGlasses.read_event",
    "Read glasses event", "Read next event from AR glasses (IMU, button, etc.).", "device")
add_path("device", "headset-utils", "ARGlasses.get_display_mode",
    "Get display mode", "Get current display mode (SameOnBoth, Stereo, HighRefreshRate).", "device")
add_path("device", "headset-utils", "ARGlasses.set_display_mode",
    "Set display mode", "Set display mode on AR glasses.", "device")
add_path("device", "headset-utils", "any_glasses",
    "Auto-detect glasses", "Auto-detect and connect to any supported AR glasses.", "device")
add_path("device", "headset-utils", "NrealAir.new",
    "Create XREAL Air instance", "Connect to XREAL Air glasses.", "device")
add_path("device", "headset-utils", "NrealLight.new",
    "Create XREAL Light instance", "Connect to XREAL Light glasses.", "device")
add_path("device", "headset-utils", "RokidAir.new",
    "Create Rokid Air instance", "Connect to Rokid Air glasses.", "device")
add_path("device", "headset-utils", "GrawoowG530.new",
    "Create Grawoow G530 instance", "Connect to Grawoow G530 glasses.", "device")
add_path("device", "headset-utils", "MadGazeGlow.new",
    "Create MadGaze Glow instance", "Connect to MadGaze Glow glasses.", "device")
add_path("device", "headset-utils", "Connection.start",
    "Start glasses connection", "Start persistent connection to glasses.", "device")
add_path("device", "headset-utils", "Connection.stop",
    "Stop glasses connection", "Stop glasses connection.", "device")

# XREAL WebHID
add_path("device", "xreal-webxr", "hidSupported",
    "Check WebHID support", "Check if WebHID API is available in the browser.", "device")
add_path("device", "xreal-webxr", "getFirmwareVersionInMcu",
    "Get MCU firmware version", "Read MCU firmware version from XREAL Air glasses.", "device")
add_path("device", "xreal-webxr", "getFirmwareVersionInDp",
    "Get DP firmware version", "Read DP firmware version.", "device")
add_path("device", "xreal-webxr", "getFirmwareVersionInDsp",
    "Get DSP firmware version", "Read DSP firmware version.", "device")
add_path("device", "xreal-webxr", "cmd_build",
    "Build HID command", "Build a HID command packet for XREAL Air glasses.", "device")
add_path("device", "xreal-webxr", "parse_rsp",
    "Parse HID response", "Parse a HID response packet.", "device")
add_path("device", "xreal-webxr", "Glasses",
    "XREAL Glasses controller", "XREAL Air glasses EventTarget controller. Emits: imu, button, brightness, display_mode.", "device")
add_path("device", "xreal-webxr", "hasActivated",
    "Check activation status", "Check if XREAL glasses are activated.", "device")
add_path("device", "xreal-webxr", "upgradeInDsp",
    "DSP firmware upgrade", "Upgrade DSP firmware on XREAL glasses.", "device")
add_path("device", "xreal-webxr", "upgradeInDp",
    "DP firmware upgrade", "Upgrade DP firmware on XREAL glasses.", "device")

# XREAL Light WebHID
add_path("device", "xreal-webxr", "light.activate",
    "Activate XREAL Light", "Activate XREAL Light glasses.", "device")
add_path("device", "xreal-webxr", "light.deactivate",
    "Deactivate XREAL Light", "Deactivate XREAL Light glasses.", "device")
add_path("device", "xreal-webxr", "light.getSN",
    "Get XREAL Light serial", "Get serial number from XREAL Light.", "device")
add_path("device", "xreal-webxr", "light.upgradeInMcu",
    "XREAL Light MCU upgrade", "Upgrade MCU firmware on XREAL Light.", "device")

# Decky XRGaming
add_path("device", "decky-XRGaming", "Plugin.retrieve_config",
    "Get XR driver config", "Retrieve Breezy XR driver configuration.", "device")
add_path("device", "decky-XRGaming", "Plugin.write_config",
    "Write XR driver config", "Write Breezy XR driver configuration.", "device")
add_path("device", "decky-XRGaming", "Plugin.write_control_flags",
    "Set control flags", "Set XR driver control flags.", "device")
add_path("device", "decky-XRGaming", "Plugin.retrieve_driver_state",
    "Get driver state", "Get current XR driver state.", "device")
add_path("device", "decky-XRGaming", "Plugin.check_installation",
    "Check Breezy installed", "Verify Breezy XR driver is installed.", "device")
add_path("device", "decky-XRGaming", "Plugin.request_token",
    "Request license token", "Request a license token via email.", "device",
    [param("email", "string", "Email address", True)])
add_path("device", "decky-XRGaming", "Plugin.verify_token",
    "Verify license token", "Verify a license token.", "device",
    [param("token", "string", "License token", True)])
add_path("device", "decky-XRGaming", "Plugin.force_reset_driver",
    "Force reset driver", "Hard reset the XR driver.", "device")

# RayNeo installer
add_path("device", "xg-glass-sdk", "RayNeoInstallerGlassesClient.connect",
    "RayNeo install APK", "Phone-side client that pushes APK to RayNeo glasses via ADB-over-TCP.", "device")
add_path("device", "xg-glass-sdk", "RayNeoInstallerGlassesClient.pushUserSettings",
    "Push user settings to RayNeo", "Push user settings map to RayNeo glasses.", "device")

# App contract
add_path("device", "xg-glass-sdk", "UniversalAppEntry",
    "Universal app entry", "App registration interface: id, displayName, commands, userSettings.", "device")
add_path("device", "xg-glass-sdk", "UniversalCommand.run",
    "Run universal command", "Execute a universal command in the app context.", "device")
add_path("device", "xg-glass-sdk", "AIApiSettings.fields",
    "AI API settings fields", "Helper for AI API configuration fields (baseUrl, model, apiKey).", "device")

# MentraOS tokens
add_path("device", "MentraOS", "createToken",
    "Create auth token", "Create a JWT authentication token.", "device")
add_path("device", "MentraOS", "validateToken",
    "Validate auth token", "Validate a JWT authentication token.", "device")
add_path("device", "MentraOS", "generateWebviewUrl",
    "Generate webview URL", "Generate a URL with embedded auth token for webview.", "device")

# MentraOS streaming
add_path("device", "MentraOS", "CoreModule.startStream",
    "Start video stream", "Start RTMP video streaming from glasses.", "device")
add_path("device", "MentraOS", "CoreModule.stopStream",
    "Stop video stream", "Stop RTMP video streaming.", "device")
add_path("device", "MentraOS", "CoreModule.keepStreamAlive",
    "Keep stream alive", "Send keepalive for active stream.", "device")
add_path("device", "MentraOS", "CoreModule.ping",
    "Ping glasses", "Send ping/heartbeat to glasses.", "device")
add_path("device", "MentraOS", "CoreModule.getGlassesStatus",
    "Get glasses status", "Get current glasses connection status.", "device")
add_path("device", "MentraOS", "CoreModule.getCoreStatus",
    "Get core status", "Get MentraOS core service status.", "device")

# RayDesk streaming
add_path("device", "RayDesk", "MoonlightBridge.connect",
    "Connect Moonlight stream", "Connect to Moonlight/Sunshine streaming server.", "device",
    [param("address", "string", "Server address", True), param("port", "integer", "Server port", True)])
add_path("device", "RayDesk", "MoonlightBridge.disconnect",
    "Disconnect stream", "End Moonlight streaming session.", "device")
add_path("device", "RayDesk", "MoonlightBridge.initializeDecoder",
    "Init hardware decoder", "Initialize hardware video decoder.", "device")
add_path("device", "RayDesk", "MoonlightBridge.isStreaming",
    "Check streaming", "Check if currently streaming.", "device")
add_path("device", "RayDesk", "MoonlightBridge.sendAbsolutePosition",
    "Send cursor position", "Send absolute cursor position to remote PC.", "device")
add_path("device", "RayDesk", "MoonlightBridge.sendMouseMove",
    "Send mouse move", "Send relative mouse movement.", "device")
add_path("device", "RayDesk", "MoonlightBridge.sendMouseClick",
    "Send mouse click", "Send mouse click to remote PC.", "device")
add_path("device", "RayDesk", "MoonlightBridge.sendKeyboard",
    "Send keyboard event", "Send keyboard event to remote PC.", "device")
add_path("device", "RayDesk", "MoonlightBridge.sendScroll",
    "Send scroll event", "Send scroll event to remote PC.", "device")
add_path("device", "RayDesk", "ServerDiscoveryManager",
    "Discover streaming servers", "mDNS-based discovery of Moonlight/Sunshine servers.", "device")
add_path("device", "RayDesk", "ReconnectionManager",
    "Auto-reconnect manager", "Auto-reconnect with exponential backoff.", "device")

# real_utilities C++
add_path("device", "real_utilities", "open_device",
    "Open XREAL HID device", "Open XREAL HID device by interface number.", "device",
    [param("interface_num", "integer", "HID interface number", True)])
add_path("device", "real_utilities", "write_control",
    "Write HID control", "Write command to XREAL control interface.", "device")
add_path("device", "real_utilities", "read_control",
    "Read HID control", "Read response from XREAL control interface.", "device")
add_path("device", "real_utilities", "write_imu",
    "Write HID IMU", "Write command to XREAL IMU interface.", "device")
add_path("device", "real_utilities", "read_imu",
    "Read HID IMU", "Read IMU data from XREAL IMU interface.", "device")
add_path("device", "real_utilities", "protocol.cmd_build",
    "Build v1 HID command", "Build Protocol v1 HID command packet.", "device")
add_path("device", "real_utilities", "protocol.parse_rsp",
    "Parse v1 HID response", "Parse Protocol v1 HID response packet.", "device")
add_path("device", "real_utilities", "protocol3.cmd_build",
    "Build v3 IMU command", "Build Protocol v3 IMU command packet.", "device")
add_path("device", "real_utilities", "protocol3.parse_rsp",
    "Parse v3 IMU response", "Parse Protocol v3 IMU response packet.", "device")

# imu-inspector
add_path("device", "imu-inspector", "open_device",
    "Open XREAL for inspection", "Open XREAL HID device for IMU inspection.", "device")
add_path("device", "imu-inspector", "fix_report",
    "Fix/normalize HID report", "Fix/normalize raw HID IMU report data.", "device")
add_path("device", "imu-inspector", "print_report",
    "Print parsed IMU data", "Pretty-print parsed IMU data from HID report.", "device")

# VITURE device
add_path("device", "XRLinuxDriver", "xr_device_provider_create",
    "Create VITURE device", "Create VITURE XR device provider handle.", "device")
add_path("device", "XRLinuxDriver", "xr_device_provider_initialize",
    "Init VITURE device", "Initialize VITURE device with configuration.", "device")
add_path("device", "XRLinuxDriver", "xr_device_provider_start",
    "Start VITURE device", "Start VITURE device streaming.", "device")
add_path("device", "XRLinuxDriver", "xr_device_provider_stop",
    "Stop VITURE device", "Stop VITURE device streaming.", "device")
add_path("device", "XRLinuxDriver", "xr_device_provider_shutdown",
    "Shutdown VITURE device", "Shutdown VITURE device provider.", "device")
add_path("device", "XRLinuxDriver", "xr_device_provider_destroy",
    "Destroy VITURE device", "Destroy VITURE device provider handle.", "device")

# Frame firmware low-level
add_path("device", "frame-codebase", "flash_erase_page",
    "Erase flash page", "Erase a flash memory page on Frame.", "device")
add_path("device", "frame-codebase", "flash_write",
    "Write flash memory", "Write data to flash memory on Frame.", "device")
add_path("device", "frame-codebase", "flash_get_info",
    "Get flash info", "Get flash page size and total size.", "device")
add_path("device", "frame-codebase", "spi_configure",
    "Configure SPI bus", "Configure SPI bus on Frame.", "device")
add_path("device", "frame-codebase", "spi_read",
    "SPI read", "Read data from SPI device.", "device")
add_path("device", "frame-codebase", "spi_write",
    "SPI write", "Write data to SPI device.", "device")

# Frame system Lua
add_path("device", "frame-codebase", "frame.update",
    "Frame process events", "Process pending system events on Frame.", "device")
add_path("device", "frame-codebase", "frame.sleep",
    "Frame sleep", "Sleep for specified duration.", "device",
    [param("seconds", "number", "Sleep duration", True)])
add_path("device", "frame-codebase", "frame.stay_awake",
    "Frame stay awake", "Prevent auto-sleep on Frame.", "device",
    [param("enable", "boolean", "Enable stay awake", True)])
add_path("device", "frame-codebase", "frame.battery_level",
    "Frame battery level", "Read battery percentage on Frame.", "device")
add_path("device", "frame-codebase", "frame.fpga_read",
    "Frame FPGA read", "Read FPGA register on Frame.", "device")
add_path("device", "frame-codebase", "frame.fpga_write",
    "Frame FPGA write", "Write FPGA register on Frame.", "device")
add_path("device", "frame-codebase", "frame.time.utc",
    "Frame UTC time", "Get UTC timestamp on Frame.", "device")
add_path("device", "frame-codebase", "frame.time.zone",
    "Frame timezone", "Get timezone offset on Frame.", "device")
add_path("device", "frame-codebase", "frame.file.read",
    "Frame file read", "Read bytes from file on Frame LittleFS.", "device")
add_path("device", "frame-codebase", "frame.file.write",
    "Frame file write", "Write data to file on Frame LittleFS.", "device")
add_path("device", "frame-codebase", "frame.file.close",
    "Frame file close", "Close file on Frame.", "device")
add_path("device", "frame-codebase", "frame.file.remove",
    "Frame file remove", "Delete file on Frame.", "device")
add_path("device", "frame-codebase", "frame.file.rename",
    "Frame file rename", "Rename file on Frame.", "device")
add_path("device", "frame-codebase", "frame.file.mkdir",
    "Frame mkdir", "Create directory on Frame.", "device")
add_path("device", "frame-codebase", "frame.file.listdir",
    "Frame list directory", "List directory contents on Frame.", "device")

# Encryption (Pebble Ring)
add_path("device", "mobileapp", "AesGcmCrypto.encrypt",
    "AES-GCM encrypt", "Encrypt data with AES-GCM.", "device")
add_path("device", "mobileapp", "AesGcmCrypto.decrypt",
    "AES-GCM decrypt", "Decrypt AES-GCM encrypted data.", "device")
add_path("device", "mobileapp", "EncryptionKeyManager.generateKey",
    "Generate encryption key", "Generate a new AES-GCM encryption key.", "device")
add_path("device", "mobileapp", "EncryptionKeyManager.saveKeyLocally",
    "Save key locally", "Save encryption key to local storage.", "device")
add_path("device", "mobileapp", "EncryptionKeyManager.saveToCloudKeychain",
    "Save key to cloud", "Save encryption key to iCloud Keychain.", "device")

# xg-glass CLI
add_path("device", "xg-glass-cli", "cmd_init",
    "CLI: Initialize project", "Initialize new xg-glass project from template.", "device")
add_path("device", "xg-glass-cli", "cmd_build",
    "CLI: Build project", "Build the xg-glass project (assembleDebug).", "device")
add_path("device", "xg-glass-cli", "cmd_install",
    "CLI: Install APK", "Install APK to connected device.", "device")
add_path("device", "xg-glass-cli", "cmd_run",
    "CLI: Run app", "Run app on device (optionally single Kotlin file).", "device")

# ============================================================
# PATHS — STARDUST (Domain 11)
# ============================================================
add_path("stardust", "stardust-core", "Client.connect",
    "Connect to StardustXR", "Connect to the StardustXR server via Unix domain socket.", "stardust")
add_path("stardust", "stardust-core", "Client.dispatch",
    "Dispatch messages", "Dispatch pending messages in the event loop.", "stardust")
add_path("stardust", "stardust-core", "Client.flush",
    "Flush messages", "Flush pending outgoing messages.", "stardust")
add_path("stardust", "stardust-core", "Client.get_root",
    "Get root spatial", "Get the root spatial node.", "stardust")
add_path("stardust", "stardust-core", "Client.setup_resources",
    "Setup resources", "Register resource paths for model/texture loading.", "stardust")
add_path("stardust", "stardust-core", "Client.sync_event_loop",
    "Synchronous event loop", "Run synchronous event loop with callback.", "stardust")
add_path("stardust", "stardust-core", "Client.async_event_loop",
    "Async event loop", "Create async event loop for StardustXR.", "stardust")

add_path("stardust", "stardust-core", "Transform.from_translation",
    "Transform from translation", "Create transform from translation vector.", "stardust")
add_path("stardust", "stardust-core", "Transform.from_rotation",
    "Transform from rotation", "Create transform from rotation quaternion.", "stardust")
add_path("stardust", "stardust-core", "Transform.from_translation_rotation_scale",
    "Transform from TRS", "Create transform from translation, rotation, and scale.", "stardust")

# Drawables
add_path("stardust", "stardust-core", "Lines.create",
    "Create 3D lines", "Create 3D line drawing with per-vertex color and thickness.", "stardust")
add_path("stardust", "stardust-core", "Model.create",
    "Create 3D model", "Load GLTF 3D model into the scene.", "stardust")
add_path("stardust", "stardust-core", "Model.part",
    "Access model part", "Access individual mesh part for material overrides.", "stardust")
add_path("stardust", "stardust-core", "Text.create",
    "Create 3D text", "Create 3D text with font, size, bounds, and alignment.", "stardust")
add_path("stardust", "stardust-core", "Sound.create",
    "Create spatial audio", "Create spatial audio source positioned in 3D space.", "stardust")

# Fields
add_path("stardust", "stardust-core", "Field.create",
    "Create SDF field", "Create a signed distance field: Sphere, Box, Cylinder, Torus, CubicSpline.", "stardust")
add_path("stardust", "stardust-core", "Field.distance",
    "SDF distance query", "Evaluate signed distance function at a point.", "stardust")
add_path("stardust", "stardust-core", "Field.normal",
    "SDF surface normal", "Get surface normal at a point.", "stardust")
add_path("stardust", "stardust-core", "Field.closest_point",
    "SDF closest point", "Get nearest surface point.", "stardust")
add_path("stardust", "stardust-core", "Field.ray_march",
    "SDF ray marching", "Ray march through the field.", "stardust")

# Input
add_path("stardust", "stardust-core", "InputMethod.create",
    "Create input method", "Create an input source (pointer, hand, tip) with datamap.", "stardust")
add_path("stardust", "stardust-core", "InputHandler.create",
    "Create input handler", "Create input handler that receives events when InputMethod intersects Field.", "stardust")

# Panel items
add_path("stardust", "stardust-core", "PanelItemUi.register",
    "Register panel UI", "Register as a panel item UI provider.", "stardust")
add_path("stardust", "stardust-core", "PanelItemAcceptor.create",
    "Create panel acceptor", "Accept Wayland windows into 3D space.", "stardust")

# Flatland
add_path("stardust", "stardust-flatland", "PanelWrapper.on_toplevel_title_changed",
    "Panel title changed", "Hook for Wayland window title changes.", "stardust")
add_path("stardust", "stardust-flatland", "PanelWrapper.on_toplevel_size_changed",
    "Panel size changed", "Hook for Wayland window resize.", "stardust")
add_path("stardust", "stardust-flatland", "PointerPlane.on_mouse_button",
    "Pointer mouse button", "Hook for mouse button events on pointer plane.", "stardust")
add_path("stardust", "stardust-flatland", "PointerPlane.on_pointer_motion",
    "Pointer motion", "Hook for pointer movement on plane.", "stardust")
add_path("stardust", "stardust-flatland", "PointerPlane.on_scroll",
    "Pointer scroll", "Hook for scroll events.", "stardust")
add_path("stardust", "stardust-flatland", "TouchPlane.on_touch_down",
    "Touch down", "Hook for touch start events.", "stardust")
add_path("stardust", "stardust-flatland", "TouchPlane.on_touch_move",
    "Touch move", "Hook for touch move events.", "stardust")
add_path("stardust", "stardust-flatland", "TouchPlane.on_touch_up",
    "Touch up", "Hook for touch end events.", "stardust")
add_path("stardust", "stardust-flatland", "GrabBall.create",
    "Create grab ball", "Create 3D handle for repositioning panels.", "stardust")

# Protostar
add_path("stardust", "stardust-protostar", "Application.create",
    "Create app from desktop file", "Create application from .desktop file for hex launcher.", "stardust")
add_path("stardust", "stardust-protostar", "Application.launch",
    "Launch application", "Launch application in spatial XR environment.", "stardust")
add_path("stardust", "stardust-protostar", "DesktopFile.parse",
    "Parse desktop file", "Parse a .desktop file for application metadata.", "stardust")
add_path("stardust", "stardust-protostar", "get_desktop_files",
    "Scan desktop files", "Scan XDG data directories for .desktop files.", "stardust")
add_path("stardust", "stardust-protostar", "Hex.spiral",
    "Hex spiral layout", "Get i-th position in hexagonal spiral layout for app launcher.", "stardust")

# Wire protocol
add_path("stardust", "stardust-core", "wire.connect",
    "Wire protocol connect", "Connect to StardustXR server via Unix socket.", "stardust")
add_path("stardust", "stardust-core", "wire.serialize",
    "Wire serialize", "Serialize data with FlexBuffers, supporting FD passing.", "stardust")
add_path("stardust", "stardust-core", "wire.deserialize",
    "Wire deserialize", "Deserialize FlexBuffer data with FD reconstruction.", "stardust")

# Gluon D-Bus
add_path("stardust", "stardust-core", "ObjectRegistry.new",
    "Create D-Bus registry", "Create object registry for D-Bus service discovery.", "stardust")
add_path("stardust", "stardust-core", "ObjectRegistry.get_objects",
    "Get D-Bus objects", "Get objects implementing a specific interface.", "stardust")
add_path("stardust", "stardust-core", "ObjectRegistry.query",
    "Query D-Bus objects", "Query stream of D-Bus objects.", "stardust")

# ============================================================
# PATHS — GEO (Domain 12)
# ============================================================
add_path("geo", "overpass-turbo", "Overpass.run_query",
    "Run Overpass query", "Run an OpenStreetMap Overpass query (OverpassQL, XML, or SQL).", "geo",
    [param("query", "string", "Overpass QL query string", True)])
add_path("geo", "overpass-turbo", "Overpass.kill_my_queries",
    "Abort running queries", "Abort all running Overpass queries.", "geo")
add_path("geo", "overpass-turbo", "Overpass.status",
    "Overpass server status", "Check Overpass API server status.", "geo")
add_path("geo", "overpass-turbo", "ffs_construct_query",
    "Natural language to Overpass", "Build an Overpass query from natural language search using OSM tag presets.", "geo",
    [param("search", "string", "Natural language search", True)])
add_path("geo", "overpass-turbo", "ffs_repair_search",
    "Repair search query", "Attempt to repair an invalid Overpass search query.", "geo")
add_path("geo", "overpass-turbo", "autorepair",
    "Auto-fix Overpass query", "Automatically fix common Overpass query errors (missing recurse, output format, geometry).", "geo")
add_path("geo", "overpass-turbo", "template_shortcuts",
    "Template shortcuts", "Mustache-style templates: {{bbox}}, {{center}}, {{date:offset}}, {{geocodeArea:name}}, {{geocodeCoords:name}}.", "geo")

add_path("geo", "gemini-maps", "generate_content",
    "Gemini Maps grounding", "Query Gemini with Google Maps grounding for location-aware AI responses.", "geo",
    [param("question", "string", "Question about location", True), param("latitude", "number", "Latitude", True), param("longitude", "number", "Longitude", True)])

add_path("geo", "ar-integration", "getArPois",
    "Get AR POIs", "Get points of interest for AR overlay using Overpass API.", "geo",
    [param("lat", "number", "Latitude", True), param("lng", "number", "Longitude", True), param("radius", "number", "Radius in meters")])

add_path("geo", "ar-integration", "askAboutLocation",
    "Ask about location", "Ask contextual questions about a location using Gemini Maps.", "geo",
    [param("question", "string", "Question", True), param("lat", "number", "Latitude", True), param("lng", "number", "Longitude", True)])

# Open Wearables
add_path("geo", "open-wearables", "get_users",
    "Get wearable users", "Discover users accessible via API key.", "geo",
    [param("search", "string", "Search filter"), param("limit", "integer", "Max results")])
add_path("geo", "open-wearables", "get_activity_summary",
    "Get activity summary", "Daily activity data: steps, calories, heart rate, intensity minutes.", "geo",
    [param("user_id", "string", "User ID", True), param("start_date", "string", "Start date", True), param("end_date", "string", "End date", True)])
add_path("geo", "open-wearables", "get_sleep_summary",
    "Get sleep summary", "Sleep data for a date range.", "geo",
    [param("user_id", "string", "User ID", True), param("start_date", "string", "Start date", True), param("end_date", "string", "End date", True)])
add_path("geo", "open-wearables", "get_workout_events",
    "Get workout events", "Workout/exercise session data.", "geo",
    [param("user_id", "string", "User ID", True), param("start_date", "string", "Start date", True), param("end_date", "string", "End date", True)])
add_path("geo", "open-wearables", "get_timeseries",
    "Get health timeseries", "Granular time-series: weight, SpO2, HRV, intraday heart rate.", "geo",
    [param("user_id", "string", "User ID", True), param("series_type", "string", "Series type", True), param("start_date", "string", "Start date", True), param("end_date", "string", "End date", True)])

# Open Wearables algorithms
add_path("geo", "open-wearables", "calculate_duration_score",
    "Sleep duration score", "Calculate sleep duration score.", "geo")
add_path("geo", "open-wearables", "calculate_total_stages_score",
    "Sleep stages score", "Calculate sleep stages score from deep/REM minutes.", "geo")
add_path("geo", "open-wearables", "calculate_overall_sleep_score",
    "Overall sleep score", "Calculate overall sleep quality score.", "geo")
add_path("geo", "open-wearables", "calculate_rmssd",
    "HRV RMSSD", "Calculate Root Mean Square of Successive Differences for HRV.", "geo")
add_path("geo", "open-wearables", "calculate_sdnn",
    "HRV SDNN", "Calculate Standard Deviation of NN intervals for HRV.", "geo")
add_path("geo", "open-wearables", "calculate_hrv_cv",
    "HRV coefficient of variation", "Calculate HRV Coefficient of Variation.", "geo")

# Open Wearables REST API
add_path("geo", "open-wearables", "auth.login",
    "Login", "POST /auth/login — Authenticate and get JWT.", "geo")
add_path("geo", "open-wearables", "auth.me",
    "Get current developer", "GET /auth/me — Get current developer info.", "geo")
add_path("geo", "open-wearables", "users.list",
    "List users", "GET /users — List users (paginated).", "geo")
add_path("geo", "open-wearables", "users.get",
    "Get user", "GET /users/{id} — Get user details.", "geo")
add_path("geo", "open-wearables", "users.create",
    "Create user", "POST /users — Create a new user.", "geo")
add_path("geo", "open-wearables", "events.workouts",
    "List workouts", "GET /events/workouts — List workout events.", "geo")
add_path("geo", "open-wearables", "events.sleep",
    "List sleep sessions", "GET /events/sleep — List sleep sessions.", "geo")
add_path("geo", "open-wearables", "health-scores",
    "List health scores", "GET /health-scores — List computed health scores.", "geo")
add_path("geo", "open-wearables", "applications.crud",
    "Manage applications", "GET/POST/DELETE /applications — CRUD for applications.", "geo")
add_path("geo", "open-wearables", "api-keys.crud",
    "Manage API keys", "GET/POST/DELETE/PUT /api-keys — CRUD for API keys.", "geo")

# ============================================================
# WRITE OUTPUT
# ============================================================
# Custom YAML representer to handle special characters
class CustomDumper(yaml.SafeDumper):
    pass

def str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

CustomDumper.add_representer(str, str_representer)

output = yaml.dump(spec, Dumper=CustomDumper, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)

with open("/tmp/ar-glasses-old/openapi.yaml", "w") as f:
    f.write(output)

print(f"Generated OpenAPI spec with {len(paths)} paths and {len(schemas)} schemas")
print(f"Tags: {len(spec['tags'])}")
