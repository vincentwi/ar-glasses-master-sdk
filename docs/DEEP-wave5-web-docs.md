# DEEP Wave 5 Web Documentation Crawl
# Deep-crawled: 2026-04-19
# Sources: Snap OS 2.0, Gemini Maps Grounding, StardustXR, Everysight Maverick, XREAL SDK

================================================================================
## 1. SNAP OS 2.0 — FULL ANNOUNCEMENT
================================================================================
Source: https://newsroom.snap.com/introducing-snap-os-2.0
Date: September 15, 2025

### Overview
Snap OS 2.0 is the second major version of the operating system for Snap's 5th-gen
Spectacles AR glasses. It introduces new interfaces, utilities, and Lenses for
browsing, content, and communication on Spectacles.

### Key Features

#### Browser (Overhauled)
- New minimalist design native to Snap OS
- Optimized page loading speed and power usage
- New home screen with widgets and bookmarks ("just a pinch away")
- Updated toolbar: type or speak website URL, navigate history, refresh
- Window resizing: resize to preferred aspect ratio (like laptop)
- WebXR support: immersive AR experiences from any WebXR-enabled website

#### Spotlight (Reimagined)
- Dedicated Spotlight Lens for phone-free content viewing
- Spatially overlays favorite content onto the real world
- Portrait orientation matches Spectacles' FOV — perfect for vertical video
- Can anchor Spotlight in place or have it follow as you move
- 3D layout for comments

#### Snapping & Sharing — Gallery Lens
- View Spectacles captures in spacious, interactive layout
- Scroll through curving carousel of videos
- Zoom in for detail
- Organize favorites before sending to friend or posting Story on Snapchat

#### Travel Mode
- Stabilizes AR content and tracking systems while in motion
- Works on planes, trains, or in passenger seat of car
- Ensures digital content stays anchored and stable during movement

### Developer Ecosystem
- Hundreds of developers from 30+ countries developing Lenses for Spectacles
- Notable Lenses: SightCraft (Enklu), NavigatAR (Utopia Labs), Pool Assist (Studio ANRK)
- Snap-made Lenses: Finger Paint, Chess, Imagine Together
- Synth Riders (rhythm game) coming to Spectacles — freestyle dancing, catch notes,
  ride rails, dodge obstacles in real world

### Technical Capabilities (from Snap OS 1.0 foundation)
- Real-time AI-powered experiences
- Hand tracking for natural interaction
- Voice interaction
- World understanding (world mesh)
- Lens Studio for development
- 6DoF tracking

### Upcoming: Specs Public Launch in 2026

================================================================================
## 2. GEMINI API — GROUNDING WITH GOOGLE MAPS (Full Technical Reference)
================================================================================
Source: https://ai.google.dev/gemini-api/docs/maps-grounding

### Overview
Grounding with Google Maps connects Gemini's generative capabilities with Google
Maps' rich, factual, up-to-date geospatial data. Enables location-aware functionality
in applications. Leverages 250M+ places worldwide.

### Key Capabilities
- Accurate, location-aware responses from Google Maps data
- Enhanced personalization based on user locations
- Contextual information and interactive Google Maps widgets
- Combines with Google Search grounding for best results

### API Configuration

#### Enabling the Tool (JSON)
```json
{
  "contents": [{
    "parts": [{"text": "Restaurants near Times Square."}]
  }],
  "tools": { "googleMaps": {} }
}
```

#### With Widget Enabled
```json
{
  "tools": { "googleMaps": { "enableWidget": true } }
}
```

#### With Location Context
```json
{
  "tools": { "googleMaps": {} },
  "toolConfig": {
    "retrievalConfig": {
      "latLng": {
        "latitude": 40.758896,
        "longitude": -73.985130
      }
    }
  }
}
```

### Python SDK Example
```python
from google import genai
from google.genai import types

client = genai.Client()

prompt = "What are the best Italian restaurants within a 15-minute walk from here?"

response = client.models.generate_content(
    model='gemini-3-flash-preview',
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_maps=types.GoogleMaps())],
        tool_config=types.ToolConfig(retrieval_config=types.RetrievalConfig(
            lat_lng=types.LatLng(
                latitude=34.050481, longitude=-118.248526))),
    ),
)

print("Generated Response:")
print(response.text)

if grounding := response.candidates[0].grounding_metadata:
  if grounding.grounding_chunks:
    print("Sources:")
    for chunk in grounding.grounding_chunks:
      print(f'- [{chunk.maps.title}]({chunk.maps.uri})')
```

### Response Format — groundingMetadata
```json
{
  "candidates": [{
    "content": {
      "parts": [{"text": "CanteenM is an American restaurant with..."}],
      "role": "model"
    },
    "groundingMetadata": {
      "groundingChunks": [{
        "maps": {
          "uri": "https://maps.google.com/?cid=13100894621228039586",
          "title": "Heaven on 7th Marketplace",
          "placeId": "places/ChIJ0-zA1vBZwokRon0fGj-6z7U"
        }
      }],
      "groundingSupports": [{
        "segment": {
          "startIndex": 0,
          "endIndex": 79,
          "text": "CanteenM is an American restaurant..."
        },
        "groundingChunkIndices": [0]
      }],
      "webSearchQueries": ["restaurants near me"],
      "googleMapsWidgetContextToken": "widgetcontent/..."
    }
  }]
}
```

### Response Fields
- groundingChunks: Array of maps sources (uri, placeId, title)
- groundingSupports: Links text spans to source chunks via indices
- googleMapsWidgetContextToken: Token for rendering contextual Places widget

### Widget Rendering
Use `<gmp-place-contextual context-token="TOKEN">` component from Google Maps JS API.

### Use Cases
1. Place-specific questions (reviews, outdoor seating, hours)
2. Location-based personalization (family-friendly, playground reviews)
3. Itinerary planning (multi-day plans with directions)

### Combining Maps + Search
Enable both tools in same request for best results:
- Maps: structured data (addresses, hours, ratings)
- Search: descriptive context (events, news, articles)

### Pricing
- $25 / 1K grounded prompts
- Free tier: 500 requests/day
- Only counted when response contains Maps grounded result

### Supported Models
| Model                        | Support |
|------------------------------|---------|
| Gemini 3.1 Pro Preview       | ✔️      |
| Gemini 3.1 Flash-Lite Preview| ✔️      |
| Gemini 3 Flash Preview       | ✔️      |
| Gemini 2.5 Pro               | ✔️      |
| Gemini 2.5 Flash             | ✔️      |
| Gemini 2.5 Flash-Lite        | ✔️      |
| Gemini 2.0 Flash             | ✔️      |

### Service Usage Requirements
- Must display Google Maps sources immediately following generated content
- Sources viewable within one user interaction
- Generate link previews with Google Maps attribution
- Display source title, link to uri or googleMapsUri
- Follow Google Maps text attribution guidelines (Roboto font, 12-16sp, no modification)

### CSS for Attribution
```css
@import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
.GMP-attribution {
  font-family: Roboto, Sans-Serif;
  font-style: normal;
  font-weight: 400;
  font-size: 1rem;
  letter-spacing: normal;
  white-space: nowrap;
  color: #5e5e5e;
}
```

### Caching Allowed
googleMapsWidgetContextToken, placeId, and reviewId may be cached/stored/exported.

### Prohibited Territories
China, Crimea, Cuba, Donetsk/Luhansk, Iran, North Korea, Syria, Vietnam

### Limitations
- Text-only input/output (no multimodal beyond text + widgets)
- Tool is off by default — must explicitly enable
- Not for emergency response services

================================================================================
## 3. GOOGLE BLOG — GROUNDING WITH GOOGLE MAPS (Supplemental)
================================================================================
Source: https://blog.google/technology/developers/grounding-google-maps-gemini-api/
Date: Oct 17, 2025
Authors: James Harrison (GPM, Geo Developer), Alisa Fortin (PM, Google DeepMind)

### Key Highlights
- GA launch of Google Maps tool in Gemini API
- Connects Gemini reasoning with 250M+ places
- Demo app available in Google AI Studio (Chat with Maps, uses Gemini Live API)
- Context token returns interactive widget with photos, reviews, details

### Use Case Examples
- Detailed itinerary planning with distance, travel time, business hours
- Hyper-local personalized recommendations (kid-friendly, playgrounds, schools)
- Local place-based answers from user reviews and Maps data

### Combined Tools
Internal evaluations show significant improvement in response quality when using
both Maps + Search together vs either alone.

================================================================================
## 4. STARDUST XR — COMPLETE DEVELOPER DOCUMENTATION
================================================================================
Source: https://stardustxr.org/docs/

### What is Stardust XR?
A display server for VR and AR headsets on Linux-based systems. Provides a 3D
environment where 2D windows (existing apps) and 3D apps can coexist in physical space.

### Architecture
- Server: Renders meshes, handles input via SUIS (Spatial Universal Interaction System)
- Built-in Wayland compositor for 2D applications
- Reference server uses Bevy (Rust game engine)
- IPC: Unix domain sockets with flatbuffers/flexbuffers protocol
- Protocol: Object-oriented scenegraph-based
- Requires working OpenXR setup

### Components

#### Server
- GitHub: https://github.com/StardustXR/server
- Root space that all clients connect to
- Must run before any clients
- Can autostart clients via startup script
- Run: `cargo run` (dev: `cargo run -F bevy/dynamic_linking`)

#### Clients
- armillary: 3D model viewer (rotate, move, display models)
- atmosphere: 3D environment viewer
- black-hole: Universal minimization of objects
- comet: 3D annotation tool
- flatland: 2D apps as Panels in 3D space
- gravity: Launch programs with 3D space offset
- non-spatial-input: Raw keyboard/mouse input utilities
- protostar: App launcher library (includes hexagon-launcher)

#### Rust Crates
- core lib: Rust crates and schemas for server/client connection
- stardust-xr-fusion: High-level library for creating clients (structs for all objects, trait-based + async events)
- stardust-xr-molecules: Widget library built on Fusion (similar to MRTK)
- stardust-xr-asteroids: Declarative UI library (like Iced + SwiftUI)
- protostar: App launcher library

### Installation

#### Fedora/Derivatives
```bash
sudo dnf group install stardust-xr
```

#### Fedora Atomic/Universal Blue
```bash
sudo rpm-ostree install stardust-xr-armillary stardust-xr-atmosphere stardust-xr-black-hole stardust-xr-comet stardust-xr-flatland stardust-xr-gravity stardust-xr-non-spatial-input stardust-xr-protostar stardust-xr-server
```

#### Arch Linux
```bash
paru -S stardust-xr-armillary stardust-xr-atmosphere stardust-xr-black-hole stardust-xr-comet stardust-xr-flatland stardust-xr-gravity stardust-xr-non-spatial-input stardust-xr-protostar stardust-xr-server
```

### Developer Build
- Clone repos on main branch for protocol compatibility
- Clients: `cargo run` or `cargo run -p {crate_name}`
- Minimal setup: hexagon-launcher (from protostar) + flatland
- 2D apps: set WAYLAND_DISPLAY=wayland-1
- X11 apps: use xwayland-satellite

### Startup Script
Location: ~/.config/stardust/startup (executable)

Environment Variables:
- STARDUST_INSTANCE: Socket name/path for Stardust connection
- WAYLAND_DISPLAY: Wayland display socket for server's compositor
- FLAT_WAYLAND_DISPLAY: Points to underlying Wayland compositor
- XDG_SESSION_TYPE: Set to "wayland"

#### Template Script
```bash
#!/usr/bin/env bash
xwayland-satellite :32 &
export DISPLAY=:32
flatland &
gravity 0 0 -0.3 hexagon_launcher &
black-hole &
WAYLAND_DISPLAY=$FLAT_WAYLAND_DISPLAY manifold | simular &
```

### Making Clients (Rust)
1. Install cargo via rustup
2. `cargo new` your project
3. Add crates to Cargo.toml:
   - stardust-xr: Low-level connection library
   - stardust-xr-fusion: High-level client library
   - stardust-xr-molecules: Widget toolkit (like MRTK)
   - stardust-xr-asteroids: Declarative UI framework

Client connects to: $XDG_RUNTIME_DIR/stardust-[0-32]

### Priorities
- 3D Environment Focus (with Wayland 2D support)
- Standard Interfaces (Wayland protocol)
- Stardust Protocol (virtual objects, 3D UIs around 2D apps)
- Personal device interaction (individual users)
- Flexible object interaction

================================================================================
## 5. EVERYSIGHT MAVERICK SDK — COMPLETE DOCUMENTATION
================================================================================
Source: https://everysight.github.io/maverick_docs/
Version: v2.6.1

### Overview
SDK for developing applications for Everysight Maverick Smart Glasses.
Wirelessly tethered to smartphone/watch via Bluetooth.
Runs as part of your mobile application — no separate app needed.

### Platform Support
| Platform     | From Version |
|-------------|-------------|
| iOS          | iOS 15.6    |
| Android      | Android 8.1 |
| Apple Watch* | 9.6         |
| WearOS       | 2.0         |
*Apple Watch: must be in foreground due to Bluetooth background limitation

### Architecture
- SDK runs inside your mobile app
- Handles Bluetooth communication, rendering, sensor data
- Communication via BLE 4.2+ (BLE 5 recommended)
- Glasses act as BLE peripheral (GATT over BLE)

### Libraries
| Name          | iOS                    | Android          |
|---------------|------------------------|------------------|
| EvsKit        | EvsKit.xcframework     | EvsKit.aar       |
| NativeEvsKit  | NativeEvsKit.xcframework | NativeEvsKit.jar |

- EvsKit: Main entry point, platform-specific (BT comm, resources)
- NativeEvsKit: Common Kotlin Native codebase for iOS/Android

### API Structure — IEvsApp Interfaces
| Method      | Interface                | Description                    |
|-------------|--------------------------|--------------------------------|
| glasses()   | IEvsGlassesStateService  | Battery %, serial number       |
| display()   | IEvsDisplayService       | Brightness, display on/off     |
| screens()   | IEvsScreenService        | Add/remove screens             |
| sensors()   | IEvsSensorsService       | Enable/disable sensors         |
| auth()      | IEvsAuthService          | Set API Key                    |
| comm()      | IEvsCommunicationService | BT device, connect/disconnect  |
| ota()       | IEvsOtaService           | Firmware updates               |

### SDK Engine

#### Initialization
```kotlin
// Android
Evs.init(context)
Evs.instance().start()
// Fluent: Evs.init(context).start()
```

#### Termination
```kotlin
Evs.instance().stop()
```

#### Logging
```kotlin
Evs.startDefaultLogger()  // os_log (iOS) or logcat (Android)
Evs.setLogger(logger)     // Custom logger
```

### Communication
- Scanning: CBCentralManager::scanForPeripherals (iOS) / BluetoothLeScanner::startScan (Android)
- Service UUID: BTConstants.serviceUUID
- Device name format: EV[NUMBER] (e.g., EV0080)
- Connect: Evs.comm().setDeviceInfo(deviceId, name) then Evs.comm().connect()
- Secure: Evs.comm().connectSecured() (triggers pairing dialog with numeric code)
- Persistent: SDK remembers configured address

```kotlin
Evs.init(context).start()
if(Evs.instance().comm().hasConfiguredDevice()){
    Evs.instance().comm().connect()
}
```

#### Stock UI for Scanning
```kotlin
Evs.instance().showUI("configure")
```

### Display
- Physical resolution: 640x400 pixels
- Virtual rendering area (smaller than physical, adjustable)
- Adjust position: setRenderingCenterX(dx), setRenderingCenterY(dy)

```kotlin
Evs.instance().showUI("adjust")  // Stock adjustment UI
```

#### Auto Display Off triggers:
- Charger plugged in
- Glasses disconnected
- Glasses off face
- Power button pressed when display on
- After 2 min with app+charger connected
- After 2 min when app not connected

#### Brightness
```kotlin
Evs.instance().display().desecrateBrightness().setBrightnessLevel(level) // Discrete
Evs.instance().display().setBrightness(value)  // Continuous 1-255
```

#### Auto Brightness
```kotlin
Evs.instance().display().autoBrightness().setProvider(AutoBrightnessGainProvider())
Evs.instance().display().autoBrightness().enable(true)
```

### UI Kit

#### UI Elements Hierarchy
- Base: UIElement, UIElementsGroup
- Types:
  - Vector Elements: Arc, Arc2, Arrow, Ellipse, Line, Path, Polygon, Polyline, Rect
  - Binary Resources: Image, Text, TextBlock
  - Containers: UIElementsGroup, Frame

#### Screen Classes
| Class      | Size(WxH) | Use-case                                    |
|------------|-----------|---------------------------------------------|
| Screen     | 420x150   | Normal HUD information display              |
| FullScreen | 640x400   | Full display usage, multi-view experiences  |

#### Using Screens
```kotlin
val screen = Screen("my_screen")
screen.add(Text("Hello World"))
Evs.instance().screens().addScreen(screen)
```

### Line of Sight (Beta) — AR API
Since Maverick has no GPU, SDK emulates 3D graphics using 2D rendering.
Limited vertices and elements — handle carefully for performance.

#### AR Elements
| Name     | Description                                          |
|----------|------------------------------------------------------|
| ArWindow | UIElementsGroup pinned in 3D space with 2D elements  |
| ArModel  | Simplified Mesh with limited vertex count            |

#### ArScreen
- Root for AR elements (like Screen but for 3D)
- Each render cycle generates compressed data stream sent to glasses

#### Coordinate Systems
- Supports 3D positioning with ArWindow and ArModel
- AR elements added to ArScreen for rendering

### MCP Server Support
- Maverick SDK includes MCP (Model Context Protocol) server integration
- Libraries for Android and iOS

### Development Resources
- GitHub: https://github.com/everysight-maverick/sdk
- Samples: https://github.com/everysight-maverick/samples
- iOS samples and Android samples available

================================================================================
## 6. XREAL SDK — DEEP TECHNICAL REFERENCE (v3.1.0)
================================================================================
Source: https://docs.xreal.com/

### Overview
XREAL SDK enables mixed reality development for XREAL glasses. Built on Unity XR
Plugin framework with XR Interaction Toolkit and AR Foundation integration.
Supports Unity 2021.3.X and above.

### Core Features
1. Spatial Computing: 6DoF tracking, plane detection, image anchoring, hand tracking
2. Optimized Rendering: Auto-applied latency minimization, judder reduction
3. Intuitive Interactions: Controller, hand, gaze input

### API Reference: https://developer.xreal.com/reference/nrsdk/overview
### SDK Download: https://developer.xreal.com/download
### GitHub: https://github.com/nreal-ai

---

### Camera System
- Uses Unity XRI for camera setup
- Prefabs: XR Interaction Setup, XR Interaction Hands Setup
- Location: Assets/Samples/XREAL XR Plugin/3.0.0/Interaction Basics/Prefabs

#### Camera Settings (vs default)
- Clear Flags: Solid Color (not Skybox)
- Background Color: Black
- Field of View: 25 (not 60)
- Clipping Planes: 0.1 (not 0.3)

#### Reset Camera (Recenter)
```csharp
XREALUtility.GetInputSubsystem()?.TryRecenter()
```

---

### Plane Detection
- Real-time horizontal and vertical plane detection
- Continuous surface tracking as device moves
- Visual feedback with custom prefabs
- Interaction support for placing/manipulating virtual objects
- Requires: Unity 2021.3+, XR Interaction Toolkit, AR Foundation

#### Setup
1. Add XR Origin(XR Rig) + AR Session to scene
2. Add AR Plane Manager component to XR Origin
3. Set Plane Prefab for visualization

#### Scripting
```csharp
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

public class PlaneDetection : MonoBehaviour
{
    private ARPlaneManager arPlaneManager;

    void Start()
    {
        arPlaneManager = GetComponent<ARPlaneManager>();
    }

    void Update()
    {
        foreach (ARPlane plane in arPlaneManager.trackables)
        {
            Debug.Log($"Detected plane: {plane.trackableId}");
        }
    }
}
```

---

### Image Tracking
- Detects and tracks stationary + moving images
- Up to 5 reference images in library
- Real-time tracking of 1 image simultaneously
- Provides continuous pose estimation (position + orientation)
- Physical size in Unity must match actual printed dimensions precisely

#### Requirements
- Supported formats: JPEG, PNG, TGA, BMP, GIF, PSD, TIFF
- Resolution: 150 DPI+ recommended
- Physical size: < 1 sq meter
- Quality score: 65+ recommended (0-100 scale)
- Distance: ≤ 1.5x image physical size
- Dull surfaces > glossy (less reflections)

#### Setup
1. Create Reference Image Library: Assets > Create > XR > Reference Image Library
2. Add images with Name, Size, Keep Texture at Runtime = true
3. Add ARTrackedImageManager to XR Origin
4. Set Serialized Library, Tracked Image Prefab

#### Event Handling
```csharp
[SerializeField]
ARTrackedImageManager m_TrackedImageManager;

void OnEnable() => m_TrackedImageManager.trackedImagesChanged += OnChanged;
void OnDisable() => m_TrackedImageManager.trackedImagesChanged -= OnChanged;

void OnChanged(ARTrackedImagesChangedEventArgs eventArgs)
{
    foreach (var newImage in eventArgs.added) { /* Handle added */ }
    foreach (var updatedImage in eventArgs.updated) { /* Handle updated */ }
    foreach (var removedImage in eventArgs.removed) { /* Handle removed */ }
}
```

---

### Depth Mesh / Meshing
- Creates 3D meshes of real-world environment
- Requires: XR Interaction Toolkit, AR Foundation, AR Subsystems

#### Capabilities
- Visualization: Visual feedback during environment scanning
- Occlusion: Hides virtual objects behind real ones
- Physics: MeshColliders for realistic interaction
- Flexible Object Placement: More flexible than plane detection
- Semantics: Classifies mesh blocks into categories:
  BACKGROUND, WALL, BUILDING, FLOOR, CEILING, HIGHWAY, SIDEWALK, GRASS, DOOR, TABLE

#### Setup
1. Add XR Origin + AR Session to scene
2. Add AR Mesh Manager component
3. Set Mesh Prefab for visualization
4. Build and run on device

---

### Spatial Anchor
- Fixed reference points for stable virtual object positioning
- Persist across sessions — content restored to exact real-world locations
- 6DoF pose (position + orientation)

#### Features
- Create and manage spatial anchors in Unity
- Save and load anchors
- User interaction support (clicking)
- Mapping quality display during creation

#### Best Practices
- After adding anchor: observe surroundings for 5-15 seconds
- Move slowly in various directions (forward, back, left, right)
- Don't save immediately — observe first
- Objects within 3 meters of anchor
- Good environment: even lighting, rich texture, 0.5-3m distance
- Bad: poor lighting, transparent/reflective surfaces, no texture

---

### Hand Tracking
- Based on XRI (XR Interaction Toolkit) and XR Hands
- XREAL provides custom subsystem for hand tracking data

#### Interaction Types
- Poke: Index finger tip driven
- Near-Far: Seamless near/far transitions (replaces Direct + Ray interactors)
- Teleport: Far field UI, teleporting, summoning

#### Setup
1. Install XR Hands, XRI, XR Plugin Management
2. In XR Origin -> Camera Offset -> Left Controller -> find Input Actions
3. Click "Setup Hand Tracking" in menu
4. Test with HandsDemoScene sample

#### Configuration
- Edit > Project Settings > XR Plug-in Management > XREAL
- Set Input source: "Hands" (default, changeable at runtime via API)

---

### Input: Controller
- Standard controller input via XRI
- Configurable input actions

### Input: Gaze
- Standard XRI gaze interaction
- Demo scenes support gaze out of the box

### Input: Notification Popup
- System notification UI component

---

### Additional Sections
- MRTK3 Integration: Mixed Reality Toolkit 3 support
- Tools: Development utilities
- Rendering: Optimized rendering pipeline
- Design Guide: UX/UI guidelines for AR
- Migration: Guide from NRSDK to XREAL SDK
- Sample Code: Comprehensive examples
- XREAL Devices: Hardware specs and compatibility

---

### XREAL SDK Categories & Sub-pages Index
- XREAL SDK Overview
- XREAL Devices (category)
- Getting Started with XREAL SDK
- Migrating from NRSDK to XREAL SDK
  - intro
- Sample Code
- Release Note (category)
  - XREAL SDK 3.1.0
  - XREAL SDK 3.0.0
- Camera
  - Camera setup
  - Access RGB Camera
- Input and Interactions
  - Controller
  - Hand Tracking
  - Gaze
  - Notification Popup
- Image Tracking
  - intro
  - XREAL Markers
- Plane Detection
- Depth Mesh
  - Meshing (NormalMesh)
  - Mesh Classification
  - Use Meshes in Editor
- Spatial Anchor
  - intro
  - Anchors
- MRTK3 Integration
- Tools (category)
- Rendering (category)
- Frequently Asked Questions
- Design Guide (category)

================================================================================
## CROSS-REFERENCE: AR GLASSES SDK FEATURE MATRIX
================================================================================

| Feature              | Snap Spectacles | XREAL         | Everysight Maverick | StardustXR    |
|----------------------|-----------------|---------------|---------------------|---------------|
| 6DoF Tracking        | ✅              | ✅            | ❌ (IMU only)       | ✅ (OpenXR)   |
| Hand Tracking        | ✅              | ✅ (XR Hands) | ❌                  | ✅            |
| Plane Detection      | ✅              | ✅ (AR Found) | ❌                  | ❌            |
| Image Tracking       | ✅              | ✅ (up to 5)  | ❌                  | ❌            |
| Depth/Mesh           | ✅ (world mesh) | ✅ (semantic) | ❌                  | ❌            |
| Spatial Anchors      | ✅              | ✅            | ❌                  | ❌            |
| 2D App Support       | ❌              | ❌            | ✅ (HUD)            | ✅ (Wayland)  |
| WebXR                | ✅ (OS 2.0)     | ❌            | ❌                  | ❌            |
| Voice Input          | ✅              | ❌            | ❌                  | ❌            |
| Dev Language          | Lens Studio     | Unity/C#      | Kotlin/Swift        | Rust          |
| Platform             | Snap OS         | Android       | iOS/Android         | Linux         |
| Display Resolution   | N/A             | Varies        | 640x400             | N/A           |
| Connectivity         | Standalone      | USB-C/Phone   | BLE 4.2+            | Desktop XR    |

================================================================================
## END OF DEEP-WAVE5-WEB-DOCS.md
================================================================================
