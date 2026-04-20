# StardustXR Deep Analysis — All Repos

Generated from deep-reading ALL .rs files, Cargo.toml, README.md, and KDL protocol IDL files.
Version: 0.51.x across all repos.

---

## 1. OVERVIEW

StardustXR is a **3D display server for VR/AR headsets on Linux**. It provides a spatial computing
environment where 2D windows (via Wayland) and 3D applications coexist in physical space.

Architecture layers:
```
  [XR Runtime (OpenXR/Monado)] <-- hardware
        |
  [StardustXR Server]          <-- Bevy + OpenXR + Wayland compositor
        |  (Unix socket, FlatBuffers protocol)
  [StardustXR Core]            <-- wire protocol, fusion client lib, gluon D-Bus registry
        |
  [Client Apps]                <-- flatland (2D panels), protostar (launchers), custom apps
```

Communication: Unix domain sockets with FlatBuffers messages + SCM_RIGHTS for FD passing.
Service discovery: D-Bus session bus (org.stardustxr.HMD) with ObjectRegistry.

---

## 2. REPO: server (stardust-xr-server v0.51.0)

### README
"Stardust XR is a display server for VR and AR headsets on Linux-based systems."

### Architecture
- **Bevy game engine** (v0.16) as the rendering backbone with OpenXR integration
- **bevy_mod_openxr** for XR session/rendering/input
- **Wayland compositor** (waynest) for hosting traditional 2D apps
- **Vulkano** for DMA-BUF texture import/export
- **D-Bus** (zbus) for service registration and object registry
- **Tokio** async runtime for networking and client connections

### Key Dependencies
- bevy 0.16 (PBR, GLTF, audio, core pipeline)
- bevy_mod_openxr 0.3, bevy_mod_xr 0.3
- openxr 0.19
- waynest (Wayland server)
- vulkano (Vulkan interop for DMA-BUF)
- tokio (async runtime)
- zbus 5.11 (D-Bus)
- stardust-xr-wire, stardust-xr-gluon (from core repo)
- glam 0.29, mint 0.5
- cosmic-text, xkbcommon-rs

### Module Structure (87 .rs files)
```
src/
├── main.rs              -- Entry point, Bevy app setup, OpenXR config, socket listener
├── core/
│   ├── client.rs        -- Client connection management, scenegraph per client
│   ├── client_state.rs  -- Persistent client state (save/restore sessions)
│   ├── scenegraph.rs    -- Server-side scenegraph (node registry per client)
│   ├── vulkano_data.rs  -- Vulkan context for DMA-BUF
│   └── mod.rs
├── nodes/
│   ├── mod.rs           -- Node, Aspect, AspectIdentifier base types
│   ├── alias.rs         -- Node aliasing (cross-client references)
│   ├── root.rs          -- Root node (client entry point)
│   ├── spatial.rs       -- Spatial transform nodes (parent-child hierarchy)
│   ├── fields.rs        -- SDF field shapes (box, sphere, cylinder, torus, spline)
│   ├── camera.rs        -- Camera capture nodes
│   ├── audio.rs         -- Spatial audio nodes
│   ├── drawable/
│   │   ├── model.rs     -- GLTF model loading
│   │   ├── text.rs      -- 3D text rendering
│   │   ├── lines.rs     -- Polyline rendering
│   │   ├── sky.rs       -- Sky/environment maps
│   │   └── dmatex.rs    -- DMA-BUF texture handling
│   ├── input/
│   │   ├── method.rs    -- Input methods (pointer, hand, tip)
│   │   ├── handler.rs   -- Input handlers (receive input)
│   │   ├── link.rs      -- Method-handler links
│   │   ├── pointer.rs   -- Pointer input type
│   │   ├── hand.rs      -- Hand input type
│   │   └── tip.rs       -- Tip/controller input type
│   └── items/
│       ├── mod.rs       -- Item system (typed objects with UI/acceptors)
│       └── panel.rs     -- Panel items (2D windows in 3D space)
├── objects/
│   ├── mod.rs           -- D-Bus object handles (SpatialRef, FieldRef, Tracked)
│   ├── hmd.rs           -- HMD tracking object
│   ├── play_space.rs    -- Play space boundaries
│   └── input/
│       ├── oxr_hand.rs      -- OpenXR hand tracking
│       ├── oxr_controller.rs -- OpenXR controller input
│       ├── mouse_pointer.rs  -- Flatscreen mouse pointer
│       └── eye_pointer.rs    -- Eye tracking pointer
├── bevy_int/
│   ├── entity_handle.rs -- Entity handle wrapper for cross-thread use
│   ├── bevy_channel.rs  -- Channel for Bevy system communication
│   ├── spectator_cam.rs -- Spectator camera for flatscreen
│   ├── tracking_offset.rs -- XR tracking offset
│   └── color.rs         -- Color conversion utilities
├── wayland/             -- Full Wayland compositor implementation
│   ├── display.rs, registry.rs, mod.rs
│   ├── core/ (surface, seat, pointer, keyboard, touch, shm, buffer, etc.)
│   ├── xdg/ (wm_base, toplevel, surface, positioner, popup, decoration)
│   └── dmabuf/ (DMA-BUF feedback, buffer params)
└── session.rs           -- Session save/restore, startup script execution
foundation/              -- Server utility crate
├── delta.rs, error.rs, id.rs, method_response.rs, registry.rs, resource.rs, task.rs
```

### Key Public Types & Functions

#### main.rs
```rust
pub type BevyMaterial = StandardMaterial;
pub struct PreFrameWait;  // ScheduleLabel
pub struct ObjectRegistryRes(Arc<ObjectRegistry>);  // Resource
pub struct DbusConnection(Connection);  // Resource
pub fn vk_device_exts() -> Vec<&'static std::ffi::CStr>;
pub fn get_time(pipelined: bool, state: &OxrFrameState) -> openxr::Time;
```

#### core/client.rs
```rust
pub fn tick_internal_client();
pub fn get_env(pid: i32) -> Result<FxHashMap<String, String>, std::io::Error>;
pub fn state(env: &FxHashMap<String, String>) -> Option<Arc<ClientStateParsed>>;
pub struct Client {
    // messenger, scenegraph, pid, state, etc.
}
impl Client {
    pub fn from_connection(connection: UnixStream) -> Result<Arc<Self>>;
    pub fn get_cmdline(&self) -> Option<Vec<String>>;
    pub fn get_cwd(&self) -> Option<PathBuf>;
    pub fn generate_id(&self) -> Id;
    pub fn get_node(&self, name: &'static str, id: Id) -> Result<Arc<Node>>;
    pub fn unresponsive(&self) -> bool;
    pub fn disconnect(&self, reason: Result<()>);
}
```

#### core/scenegraph.rs
```rust
pub struct Scenegraph {
    // DashMap<Id, Arc<Node>>, Weak<Client>
}
impl Scenegraph {
    pub fn get_client(&self) -> Option<Arc<Client>>;
    pub fn add_node(&self, node: Node) -> Arc<Node>;
    pub fn add_node_raw(&self, node: Arc<Node>);
    pub fn get_node(&self, node: Id) -> Option<Arc<Node>>;
    pub fn remove_node(&self, node: Id) -> Option<Arc<Node>>;
}
```

#### nodes/mod.rs
```rust
pub struct Message { /* method, data, fds */ }
pub struct Owned;
pub struct OwnedNode(pub Arc<Node>);
pub struct Node {
    // id, client, aspects, enabled, destroyable
}
impl Node {
    pub fn get_client(&self) -> Option<Arc<Client>>;
    pub fn get_id(&self) -> Id;
    pub fn generate(client: &Arc<Client>, destroyable: bool) -> Self;
    pub fn from_id(client: &Arc<Client>, id: Id, destroyable: bool) -> Self;
    pub fn add_to_scenegraph(self) -> Result<Arc<Node>>;
    pub fn enabled(&self) -> bool;
    pub fn set_enabled(&self, enabled: bool);
    pub fn destroy(&self);
    pub fn add_aspect<A: AspectIdentifier>(&self, aspect: A) -> Arc<A>;
    pub fn get_aspect<A: AspectIdentifier>(&self) -> Result<Arc<A>>;
    pub fn send_local_signal(...);
    pub fn execute_local_method(...);
    pub fn send_remote_signal(...);
}
pub trait AspectIdentifier: Aspect { /* ID */ }
pub trait Aspect: Any + Send + Sync + 'static { /* methods */ }
```

#### nodes/spatial.rs
```rust
pub struct SpatialNodePlugin;
pub struct SpatialNode(pub Weak<Spatial>);
pub struct Spatial {
    // node, parent, local_transform, entity, children
}
impl Spatial {
    pub fn new(node: Weak<Node>, parent: Option<Arc<Spatial>>, transform: Mat4) -> Arc<Self>;
    pub fn add_to(node: &Arc<Node>, parent: Option<Arc<Spatial>>, transform: Mat4) -> Arc<Spatial>;
    pub fn space_to_space_matrix(from: Option<&Spatial>, to: Option<&Spatial>) -> Mat4;
    pub fn local_transform(&self) -> Mat4;
    pub fn global_transform(&self) -> Mat4;
    pub fn set_local_transform(&self, transform: Mat4);
    pub fn set_spatial_parent(self: &Arc<Self>, parent: &Arc<Spatial>) -> Result<()>;
    pub fn set_spatial_parent_in_place(self: &Arc<Self>, parent: &Arc<Spatial>) -> Result<()>;
    pub fn is_ancestor_of(&self, spatial: Arc<Spatial>) -> bool;
    pub fn visible(&self) -> bool;
}
```

#### nodes/fields.rs
```rust
pub struct FieldDebugGizmoPlugin;
pub trait FieldTrait: Send + Sync + 'static { /* distance, normal, closest_point, ray_march */ }
pub struct Ray { pub origin: Vec3, pub direction: Vec3 }
pub struct Field { /* node, shape, spatial */ }
pub struct FieldRef;
impl Field {
    pub fn add_to(node: &Arc<Node>, shape: Shape) -> Result<Arc<Field>>;
}
```

#### nodes/items/panel.rs
```rust
pub trait Backend: Send + Sync + 'static {
    // apply_surface_material, apply_cursor_material, close_toplevel, etc.
    // pointer/keyboard/touch input forwarding
}
pub trait PanelItemTrait: Send + Sync + 'static { /* node, backend operations */ }
pub struct PanelItem<B: Backend> { /* node, backend, aliases, children */ }
impl<B: Backend> PanelItem<B> {
    pub fn create(backend: Box<B>, pid: Option<i32>) -> (Arc<Node>, Arc<PanelItem<B>>);
    pub fn toplevel_parent_changed(&self, parent: Id);
    pub fn toplevel_title_changed(&self, title: &str);
    pub fn toplevel_size_changed(&self, size: Vector2<u32>);
    pub fn set_cursor(&self, geometry: Option<Geometry>);
    pub fn create_child(&self, id: Id, info: &ChildInfo);
    pub fn reposition_child(&self, id: Id, geometry: &Geometry);
    pub fn destroy_child(&self, id: Id);
}
pub struct PanelItemUi;
pub struct PanelItemAcceptor;
```

#### nodes/input/method.rs
```rust
pub struct InputMethod {
    // node, spatial, data_type, datamap, handler_order, captures
}
impl InputMethod {
    pub fn add_to(node: &Arc<Node>, ...) -> Result<Arc<InputMethod>>;
    pub fn distance(&self, to: &Field) -> f32;
    pub fn update_state(&self, input: InputDataType, datamap: Datamap);
    pub fn set_handler_capture_order(...);
}
```

#### foundation (server-foundation crate)
```rust
pub struct Delta<T> { /* change tracking */ }
pub struct Id(pub u64);
pub struct Registry<T: Send + Sync + ?Sized> { /* weak-ref registry with DashMap */ }
pub struct OwnedRegistry<T: Send + Sync + ?Sized> { /* strong-ref registry */ }
pub struct MethodResponseSender(pub(crate) MethodResponse);
pub type Result<T, E = ServerError> = std::result::Result<T, E>;
pub enum ServerError { /* InvalidPath, IgnoredSignal, NotFound, OverrideSingleton, etc. */ }
pub fn get_resource_file<'a>(...);  // Resource file resolution
```

#### CLI Arguments
```
--force-flatscreen     Force flatscreen mode with mouse pointer
--xr-only              Disable flatscreen window
--spectator            First-person spectator camera
--transparent-flatscreen  Transparent window
--disable-controllers  Disable controller input
--disable-hands        Disable hand tracking
--transparent-hands    Transparent hands for passthrough
--overlay <PRIORITY>   Run as XR overlay
--execute-startup-script <PATH>
--restore <SESSION_ID>  Restore saved session
```

---

## 3. REPO: core (stardust-xr workspace v0.51.1)

Workspace with 4 crates: `wire`, `fusion`, `protocol`, `gluon`

### 3.1 wire (stardust-xr-wire)

The low-level communication library.

#### Wire Protocol Format
Messages are FlatBuffers with a 4-byte length header:
```
[4 bytes: body_length] [body: FlatBuffer Message]
```
FDs are passed via Unix SCM_RIGHTS.

Message types (type_ field):
- 0 = Error
- 1 = Signal (fire-and-forget)
- 2 = Method call (request-response)
- 3 = Method return

#### Key Types
```rust
// messenger.rs
pub enum MessengerError { ReceiverDropped, IOError, InvalidFlatbuffer, MessageTypeOutOfBounds }
pub struct Message { data: Vec<u8>, fds: Vec<OwnedFd> }
pub struct MethodResponse { sender_handle, message_id, node_id, aspect_id, method_id }
pub struct MessageReceiver { read: OwnedReadHalf, pending_futures, ... }
pub struct MessageSender { write: OwnedWriteHalf, handle, ... }
pub struct MessageSenderHandle { message_tx, pending_future_tx, message_counter }
pub fn create(connection: UnixStream) -> (MessageSender, MessageReceiver);

// scenegraph.rs
pub enum ScenegraphError { NodeNotFound, BrokenAlias, AspectNotFound, MemberNotFound, MemberError, InternalError }
pub trait Scenegraph {
    fn send_signal(&self, node_id: u64, aspect: u64, method: u64, data: &[u8], fds: Vec<OwnedFd>) -> Result<(), ScenegraphError>;
    fn execute_method(&self, node_id: u64, aspect: u64, method: u64, data: &[u8], fds: Vec<OwnedFd>, response: MethodResponse);
}

// client.rs
pub async fn connect() -> Result<UnixStream, std::io::Error>;
// Connects via $STARDUST_INSTANCE or "stardust-0" in XDG_RUNTIME_DIR

// server.rs
pub struct LockedSocket { pub socket_path: PathBuf }
impl LockedSocket {
    pub fn get_free() -> Option<Self>;  // Finds free stardust-N socket
}

// values.rs
pub type Quaternion = mint::Quaternion<f32>;
pub type Mat4 = mint::ColumnMatrix4<f32>;
pub type Color = color::Rgba<f32, color::color_space::LinearRgb>;
pub enum ResourceID { Direct(PathBuf), Namespaced(String, PathBuf) }
impl ResourceID {
    pub fn new_direct(path: impl AsRef<Path>) -> std::io::Result<ResourceID>;
    pub fn new_namespaced(namespace: &str, path: impl AsRef<Path>) -> Self;
}

// flex/datamap.rs
pub struct Datamap(Vec<u8>);
impl Datamap {
    pub fn from_raw(raw: Vec<u8>) -> Result<Self, ReaderError>;
    pub fn with_data<F, O>(&self, f: F) -> O;
    pub fn raw(&self) -> &Vec<u8>;
    pub fn from_typed<T: Serialize>(typed: T) -> Result<Self, SerializationError>;
    pub fn deserialize<'de, T: Deserialize<'de>>(&'de self) -> Result<T, DeserializationError>;
}

// flex/mod.rs
pub fn serialize<S: Serialize>(value: S) -> Result<(Vec<u8>, Vec<OwnedFd>), FlexSerializeError>;
pub fn deserialize<'a, T: Deserialize<'a>>(data: &'a [u8], fds: Vec<OwnedFd>) -> Result<T, DeserializationError>;

// fd.rs
pub struct ProtocolFd(pub OwnedFd);
pub fn with_fd_serialization_ctx<T, E: Error>(...);
pub fn with_fd_deserialization_ctx<T>(...);
```

### 3.2 protocol (stardust-xr-protocol)

KDL-based Interface Definition Language for the StardustXR protocol.

#### Protocol Files (10 .kdl IDL files)
- **root.kdl** — Client root, frame events, ping, state save/restore
- **node.kdl** — Owned aspect (enable/disable/destroy)
- **spatial.kdl** — SpatialRef, Spatial, Transform, BoundingBox
- **field.kdl** — FieldRef, Field, Shape union (Box/Sphere/Cylinder/Torus/Spline)
- **drawable.kdl** — Lines, Model, ModelPart, Text, DMA-BUF textures, Sky
- **input.kdl** — InputMethod, InputHandler, Hand/Pointer/Tip structs
- **item.kdl** — Generic item/acceptor system
- **item_panel.kdl** — PanelItem (2D windows), pointer/keyboard/touch forwarding
- **audio.kdl** — Sound nodes (WAV/MP3)
- **camera.kdl** — Camera capture nodes

#### Protocol Parser Types
```rust
pub struct Protocol { version, description, interface, custom_enums, custom_structs, custom_unions, aspects }
pub struct Interface { node_id: u64, members: Vec<Member> }
pub struct Aspect { name, id: u64 (FNV hash), description, inherits, members, inherited_aspects }
pub struct Member { name, opcode: u64 (FNV hash), description, side: Side, _type: MemberType, arguments, return_type }
pub enum MemberType { Signal, Method }
pub enum Side { Client, Server }
pub enum ArgumentType { Empty, Bool, Int, UInt, Float, Vec2, Vec3, Quat, Mat4, Color, String, Bytes, Vec, Map, NodeID, Datamap, ResourceID, Enum, Union, Struct, Node, Fd }
pub fn resolve_inherits(protocols: &mut [&mut Protocol]) -> Result<(), String>;
```

### 3.3 fusion (stardust-xr-fusion)

High-level client library for building StardustXR applications.

#### Client Connection
```rust
pub struct Client { internal: Arc<ClientHandle>, message_rx, message_tx }
impl Client {
    pub async fn connect() -> Result<Self, ClientError>;
    pub fn from_connection(connection: UnixStream) -> Self;
    pub fn handle(&self) -> Arc<ClientHandle>;
    pub fn get_root(&self) -> &Root;
    pub fn setup_resources(&self, paths: &[&Path]) -> NodeResult<()>;
    pub async fn dispatch(&mut self) -> Result<(), MessengerError>;
    pub async fn flush(&mut self) -> Result<(), MessengerError>;
    pub async fn sync_event_loop<F>(&mut self, f: F) -> Result<(), MessengerError>;
    pub fn async_event_loop(mut self) -> AsyncEventLoop;
}
pub struct ClientHandle { pub message_sender_handle, registry, id_counter, root }
impl ClientHandle {
    pub fn get_root(&self) -> &Root;
    pub fn generate_id(&self) -> u64;
}
pub struct AsyncEventLoop { pub client_handle: Arc<ClientHandle>, ... }
pub enum ControlFlow { Poll, Wait, WaitUntil(Instant), Stop }
pub struct AsyncEventHandle(Arc<Notify>);
```

#### Node System
```rust
pub type NodeResult<O> = Result<O, NodeError>;
pub enum NodeError { ClientDropped, MessengerError, DoesNotExist, NotAliased, InvalidPath, Serialization, Deserialization, ReturnedError, OverrideSingleton, MapInvalid }
pub trait NodeType: Sized + Send + Sync + 'static {
    fn node(&self) -> &NodeCore;
    fn id(&self) -> u64;
    fn client(&self) -> &Arc<ClientHandle>;
    fn set_enabled(&self, enabled: bool) -> Result<(), NodeError>;
}
pub struct NodeCore { pub client: Arc<ClientHandle>, pub id: u64, pub(crate) owned: bool }
pub struct TypedMethodResponse<T: Serialize>(...);
```

#### Spatial API (code-generated from spatial.kdl)
```rust
// Transform helper constructors
impl Transform {
    pub const fn none() -> Self;
    pub const fn identity() -> Self;
    pub fn from_translation(translation: impl Into<Vector3<f32>>) -> Self;
    pub fn from_rotation(rotation: impl Into<Quaternion>) -> Self;
    pub fn from_scale(scale: impl Into<Vector3<f32>>) -> Self;
    pub fn from_translation_rotation(...) -> Self;
    pub fn from_rotation_scale(...) -> Self;
    pub fn from_translation_scale(...) -> Self;
    pub fn from_translation_rotation_scale(...) -> Self;
}
impl Spatial {
    pub fn create(spatial_parent: &impl SpatialRefAspect, transform: Transform) -> NodeResult<Self>;
}
impl SpatialRef {
    pub async fn import(client: &Arc<ClientHandle>, uid: u64) -> NodeResult<Self>;
}
// Code-generated aspects: SpatialRefAspect, SpatialAspect
// Methods: get_transform, get_local_bounding_box, get_relative_bounding_box
// Signals: set_local_transform, set_relative_transform, set_spatial_parent, set_spatial_parent_in_place
// Method: export_spatial -> u64 (for cross-client sharing)
```

#### Input API (code-generated from input.kdl)
```rust
impl InputMethod {
    pub fn create(spatial_parent, transform, input_type: InputDataType, datamap: &Datamap) -> NodeResult<Self>;
}
impl InputHandler {
    pub fn create(spatial_parent, transform, field: &impl FieldAspect) -> NodeResult<Self>;
}
// InputDataType union: Pointer | Hand | Tip
// Hand has full articulation: thumb, index, middle, ring, little fingers
// Each finger: tip, distal, intermediate, proximal, metacarpal joints
// Heuristic methods on Hand:
impl Hand {
    pub fn palm_normal(&self) -> Vector3<f32>;
    pub fn radial_axis(&self) -> Vector3<f32>;
    pub fn distal_axis(&self) -> Vector3<f32>;
    pub fn finger_curl(&self, finger: &Finger) -> f32;
    pub fn thumb_curl(&self) -> f32;
    pub fn pinch_distance(&self, finger: &Finger) -> f32;
    pub fn pinch_position(&self) -> Vector3<f32>;
    pub fn stable_pinch_position(&self) -> Vector3<f32>;
    pub fn predicted_pinch_position(&self) -> Vector3<f32>;
    pub fn pinch_strength(&self) -> f32;
    pub fn fist_strength(&self) -> f32;
}
// InputHandler events: InputSent, InputUpdated, InputLeft
```

#### Field API (code-generated from field.kdl)
```rust
impl Field {
    pub fn create(spatial_parent, transform, shape: Shape) -> NodeResult<Self>;
    // Methods: distance, normal, closest_point, ray_march, set_shape, export_field
}
// Shape union: Box(Vec3) | Sphere(f32) | Cylinder(CylinderShape) | Torus(TorusShape) | Spline(CubicSplineShape)
```

#### Drawable API (code-generated from drawable.kdl)
```rust
impl Lines {
    pub fn create(spatial_parent, transform, lines: &[Line]) -> NodeResult<Self>;
}
impl Model {
    pub fn create(spatial_parent, transform, model: &ResourceID) -> NodeResult<Self>;
    pub fn part(&self, relative_path: &str) -> NodeResult<ModelPart>;
}
impl Text {
    pub fn create(spatial_parent, transform, text: &str, style: TextStyle) -> NodeResult<Self>;
}
// Model parts can have material parameters set, holdout materials applied
// DMA-BUF texture import/export for zero-copy GPU sharing
```

#### Scenegraph / Event System
```rust
pub trait EventParser: Sized + Send + Sync + 'static { /* parse signal/method from wire */ }
pub struct NodeRegistry { /* maps node IDs to event parsers */ }
impl NodeRegistry {
    pub fn new(client: Weak<ClientHandle>) -> Self;
    pub fn add_aspect<E: EventParser>(...);
    pub fn remove_node(&self, node_id: u64);
}
```

### 3.4 gluon (stardust-xr-gluon)

D-Bus integration layer for object discovery between clients.

```rust
pub async fn connect_client() -> zbus::Result<zbus::Connection>;
pub fn random_object_name() -> OwnedObjectPath;

pub struct ObjectInfo { pub bus_name: OwnedBusName, pub object_path: OwnedObjectPath }
impl ObjectInfo {
    pub async fn to_proxy(&self, conn, interface) -> Result<Proxy>;
    pub async fn to_typed_proxy<P>(&self, conn) -> Result<P>;
}

pub struct ObjectRegistry { /* watches D-Bus for object additions/removals */ }
impl ObjectRegistry {
    pub fn get_objects(&self, interface: &str) -> HashSet<ObjectInfo>;
    pub fn get_watch(&self) -> watch::Receiver<Objects>;
    pub fn get_object_events_receiver(&self) -> broadcast::Receiver<ObjectEvent>;
    pub fn get_connection(&self) -> &zbus::Connection;
}

// Query system for tracking objects
pub trait Queryable<Ctx: QueryContext>: Sized + 'static + Send + Sync { /* match criteria */ }
pub trait QueryContext: Sized + 'static + Send + Sync {}
pub struct ObjectQuery<Q, Ctx> { /* tracks matching objects */ }
pub struct ObjectListQuery<T> { /* maintains a map of matching objects */ }
pub struct QueryStream<Q, Ctx> { /* async stream of object events */ }

// D-Bus interfaces for StardustXR objects
pub trait SpatialRef { /* D-Bus interface for spatial references */ }
pub trait FieldRef { /* D-Bus interface for field references */ }
pub trait PlaySpace { /* D-Bus interface for play space */ }
pub trait Reparentable { /* D-Bus interface */ }
pub trait ReparentLock { /* D-Bus interface */ }
pub trait Destroy { /* D-Bus interface */ }
```

---

## 4. REPO: flatland (v0.51.0)

### README
"Virtual displays for desktop apps" — Required for 2D apps to display correctly in StardustXR.

### Dependencies
- stardust-xr-fusion 0.51.0
- stardust-xr-molecules 0.51.0 (higher-level interaction primitives)
- stardust-xr-asteroids 0.51.0 (additional utilities)
- glam 0.28, tokio, input-event-codes

### Architecture (11 .rs files)
Flatland is a StardustXR *client* that registers as a PanelItemUI handler. When 2D Wayland apps
create windows, the server creates PanelItems, and Flatland receives them to render as
interactive 3D panels.

### Key Types

#### main.rs
```rust
pub struct State {
    // panel_item, toplevel, resize_handles, close_button, grab_balls
    // pointer_input, touch_input, panel_shell_transfer, children
}
pub struct ChildState { id: u64, geometry: Geometry }
pub struct ToplevelState {
    // parent, title, app_id, size, min_size, max_size, logical_rectangle
    pub fn size_meters(&self) -> Vector2<f32>;
}
pub fn add_child(children: &mut Vec<ChildState>, child_info: ChildInfo);
pub fn update_child_geometry(children: &mut [ChildState], id: u64, geometry: Geometry);
pub fn remove_child(children: &mut Vec<ChildState>, id: u64);
pub fn process_initial_children(children: Vec<ChildInfo>) -> Vec<ChildState>;
```

#### panel_wrapper.rs — Builder for panel event handling
```rust
pub struct PanelWrapper<State: ValidState> {
    // Wraps PanelItem with callback-based event handling
}
impl PanelWrapper<State> {
    pub fn new(panel_item: PanelItem) -> Self;
    pub fn on_toplevel_parent_changed(self, f: impl Fn(&mut State, u64)) -> Self;
    pub fn on_toplevel_title_changed(self, f: impl Fn(&mut State, String)) -> Self;
    pub fn on_toplevel_app_id_changed(self, f: impl Fn(&mut State, String)) -> Self;
    pub fn on_toplevel_fullscreen_active(self, f: impl Fn(&mut State, bool)) -> Self;
    pub fn on_toplevel_move_request(self, f: impl Fn(&mut State)) -> Self;
    pub fn on_toplevel_resize_request(self, f: impl Fn(&mut State, bool, bool, bool, bool)) -> Self;
    pub fn on_toplevel_size_changed(self, f: impl Fn(&mut State, Vector2<u32>)) -> Self;
    pub fn on_set_cursor(self, f: impl Fn(&mut State, Geometry)) -> Self;
    pub fn on_hide_cursor(self, f: impl Fn(&mut State)) -> Self;
    pub fn on_create_child(self, f: impl Fn(&mut State, u64, ChildInfo)) -> Self;
    pub fn on_reposition_child(self, f: impl Fn(&mut State, u64, Geometry)) -> Self;
    pub fn on_destroy_child(self, f: impl Fn(&mut State, u64)) -> Self;
}
```

#### pointer_input.rs — Mouse/pointer interaction
```rust
pub struct MouseEvent { button: u32, pressed: bool }
pub struct PointerPlane<State: ValidState> {
    // Configurable callbacks for pointer events
}
impl PointerPlane<State> {
    pub fn on_mouse_button(self, f: impl Fn(&mut State, MouseEvent)) -> Self;
    pub fn on_pointer_motion(self, f: impl Fn(&mut State, Vec2)) -> Self;
    pub fn on_scroll(self, f: impl Fn(&mut State, MouseEvent)) -> Self;
}
pub struct PointerSurfaceInputInner { /* tracks pointer state per surface */ }
```

#### touch_input.rs — Multi-touch interaction
```rust
pub struct TouchPlane<State: ValidState> {
    // Configurable callbacks for touch events
}
impl TouchPlane<State> {
    pub fn on_touch_down(self, f: impl Fn(&mut State, u32, Vec2)) -> Self;
    pub fn on_touch_move(self, f: impl Fn(&mut State, u32, Vec2)) -> Self;
    pub fn on_touch_up(self, f: impl Fn(&mut State, u32)) -> Self;
}
pub struct TouchSurfaceInputInner { /* tracks touch state */ }
```

#### grab_ball.rs — Draggable interaction points
```rust
pub trait GrabBallHead { /* visual head of grab ball */ }
pub struct GrabBallSettings { radius, min_distance, max_distance, color_gradient }
pub struct GrabBall<H: GrabBallHead> {
    // spatial, field, input_handler, grab_action, position, head
}
impl GrabBall<H> {
    pub fn create(client, parent, settings, offset, head) -> NodeResult<Self>;
    pub fn update(&mut self);
    pub fn pos(&self) -> &Vec3;
    pub fn set_offset(&mut self, offset: impl Into<Vec3>);
    pub fn set_enabled(&mut self, enabled: bool);
    pub fn connect_root(&self) -> &Spatial;
    pub fn grab_action(&self) -> &SingleAction;
}
```

#### resize_handles.rs — Corner resize interaction
```rust
pub struct ResizeHandle { /* spatial, field, input, grab action */ }
pub struct ResizeHandlesInner { /* top-left, bottom-right handles */ }
pub struct ResizeHandles<State: ValidState> { /* configurable resize behavior */ }
```

#### close_button.rs — Close button with heat-up animation
```rust
pub struct ExposureButton<State: ValidState> { /* close/action button */ }
pub struct ExposureButtonInner { /* model, field, exposure tracking */ }
```

#### toplevel.rs — Top-level window management
```rust
pub struct ToplevelInner {
    // panel_item, model, resize_handles, close_button, grab_balls, title text
}
impl ToplevelInner {
    pub fn create(client, panel_item, initial_data, ...) -> NodeResult<Self>;
    pub fn frame(&mut self, info: &FrameInfo);
    pub fn handle_events(&mut self, acceptors);
    pub fn handle_item_events(&mut self);
    pub fn set_enabled(&mut self, enabled: bool);
}
```

#### panel_shell_transfer.rs — Transfer panels between shells
```rust
pub struct PanelShellTransfer {
    // model, field, input_handler for drag-drop transfer
}
```

---

## 5. REPO: protostar (workspace)

### README
"A collection of application launchers for Stardust XR"

### Sub-crates
- **protostar** (library) — Core launcher utilities
- **hexagon_launcher** — Hexagonal grid app launcher
- **single** — Single-app launcher
- **sirius** — Alternative launcher
- **app_grid** — Grid-based app launcher

### Dependencies
- stardust-xr-fusion 0.51.0
- stardust-xr-molecules 0.51.0
- stardust-xr-asteroids 0.51.0
- tokio, serde

### Key Types

#### protostar/src/xdg.rs — XDG Desktop File Parsing
```rust
pub fn get_desktop_files() -> impl Iterator<Item = PathBuf>;
pub struct DesktopFile {
    // path, name, generic_name, comment, icon, exec, categories, etc.
}
impl DesktopFile {
    pub fn parse(path: PathBuf) -> Result<Self, String>;
    pub fn get_icon(&self, preferred_px_size: u16) -> Option<Icon>;
}
pub struct Icon { path: PathBuf, size: u16, icon_type: IconType }
pub enum IconType { Png, Svg }
impl Icon {
    pub fn from_path(path: PathBuf, size: u16) -> Option<Icon>;
    pub fn cached_process(self, size: u16) -> Result<Icon, std::io::Error>;
}
pub fn get_image_cache_dir() -> PathBuf;
pub fn get_png_from_svg(svg_path, size) -> Result<PathBuf, std::io::Error>;
```

#### protostar/src/application.rs — Application launching
```rust
pub struct Application {
    // desktop_file, model (3D icon)
}
impl Application {
    pub fn create(desktop_file: DesktopFile) -> Result<Self, NodeError>;
    pub fn name(&self) -> Option<&str>;
    pub fn categories(&self) -> &[String];
    pub fn icon(&self, preferred_px_size: u16, prefer_3d: bool) -> Option<Icon>;
    pub fn launch<T: SpatialRefAspect + Clone>(&self, launch_space: &T) -> NodeResult<()>;
}
```

#### hexagon_launcher/src/hex.rs — Hexagonal grid math
```rust
pub struct Hex { q: isize, r: isize, s: isize }
impl Hex {
    pub fn new(q: isize, r: isize, s: isize) -> Self;
    pub fn get_coords(&self) -> [f32; 3];
    pub fn neighbor(self, direction: usize) -> Self;
    pub fn scale(self, factor: isize) -> Self;
    pub fn spiral(i: usize) -> Self;
}
```

#### hexagon_launcher/src/main.rs
```rust
pub struct HexagonLauncher {
    // apps arranged in hexagonal grid pattern
}
```

#### single/src/app.rs — Single application display
```rust
pub struct App {
    // application, spatial, model for icon display
}
impl App {
    pub fn new(desktop_entry: DesktopFile) -> Result<Self, NodeError>;
    pub fn load_icon(&self);
}
```

#### single/src/app_launcher.rs
```rust
pub struct AppLauncher<State: ValidState>(Application, Box<dyn Fn(&mut State) + Send + Sync>);
impl AppLauncher<State> {
    pub fn new(app: &Application) -> Self;
    pub fn done<F: Fn(&mut State) + Send + Sync + 'static>(mut self, f: F) -> Self;
}
```

---

## 6. PROTOCOL SPECIFICATION (KDL IDL)

### Aspect Hierarchy
```
Owned
├── set_enabled(bool)
└── destroy()

SpatialRef
├── get_local_bounding_box() -> BoundingBox
├── get_relative_bounding_box(relative_to) -> BoundingBox
└── get_transform(relative_to) -> Transform

Spatial : Owned + SpatialRef
├── set_local_transform(Transform)
├── set_relative_transform(relative_to, Transform)
├── set_spatial_parent(parent)
├── set_spatial_parent_in_place(parent)
└── export_spatial() -> u64

FieldRef : SpatialRef
├── distance(space, point) -> f32
├── normal(space, point) -> Vec3
├── closest_point(space, point) -> Vec3
└── ray_march(space, origin, direction) -> RayMarchResult

Field : Spatial + FieldRef
├── set_shape(Shape)
└── export_field() -> u64

Lines : Spatial
└── set_lines(lines)

Model : Spatial
└── bind_model_part(id, path) -> ModelPart

ModelPart : Spatial
├── apply_holdout_material()
└── set_material_parameter(name, value)

Text : Spatial
├── set_character_height(f32)
└── set_text(string)

Sound : Spatial
├── play()
└── stop()

InputMethodRef : SpatialRef
├── try_capture(handler)
└── release(handler)

InputMethod : Spatial + InputMethodRef
├── update_state(input, datamap)
├── set_handler_order(handlers)
├── set_captures(handlers)
├── [client] create_handler, request_capture_handler, release_handler, destroy_handler

InputHandler : Spatial
├── [client] input_sent(method, data)
├── [client] input_updated(data)
└── [client] input_left(method)

Root : SpatialRef
├── [client] ping() -> ()
├── [client] frame(FrameInfo)
├── [server] get_state() -> ClientState
├── [client] save_state() -> ClientState
├── [server] generate_state_token(ClientState) -> String
├── [server] get_connection_environment() -> Map<String>
├── [server] set_base_prefixes(Vec<String>)
└── [server] disconnect()

Item : Spatial
ItemUi
ItemAcceptor

PanelItem : Item
├── apply_cursor_material(model_part)
├── apply_surface_material(surface, model_part)
├── close_toplevel()
├── auto_size_toplevel()
├── set_toplevel_size(size)
├── set_toplevel_focused_visuals(focused)
├── [client] toplevel_parent_changed, title_changed, app_id_changed, fullscreen_active
├── [client] toplevel_move_request, resize_request, size_changed
├── [client] set_cursor, hide_cursor, create_child, reposition_child, destroy_child
├── absolute_pointer_motion, relative_pointer_motion, pointer_button, pointer_scroll
├── keyboard_key
└── touch_down, touch_move, touch_up, reset_input
```

### Data Types in Protocol
```
Struct Transform { translation: Vec3?, rotation: Quat?, scale: Vec3? }
Struct BoundingBox { center: Vec3, size: Vec3 }
Struct FrameInfo { delta: f32, elapsed: f32 }
Struct ClientState { data: bytes?, root: id, spatial_anchors: Map<id> }
Union Shape { Box(Vec3), Cylinder(CylinderShape), Sphere(f32), Spline(CubicSplineShape), Torus(TorusShape) }
Union InputDataType { Pointer, Hand, Tip }
Struct Joint { position: Vec3, rotation: Quat, radius: f32, distance: f32 }
Struct Hand { right: bool, thumb: Thumb, index/middle/ring/little: Finger, palm/wrist/elbow: Joint }
Struct Pointer { origin: Vec3, orientation: Quat, deepest_point: Vec3 }
Struct Tip { origin: Vec3, orientation: Quat }
Struct InputData { id, input: InputDataType, distance: f32, datamap: Datamap, order: uint, captured: bool }
```

---

## 7. KEY ARCHITECTURAL PATTERNS

### 1. Scenegraph-Based Protocol
Every client has a tree of nodes addressed by u64 IDs. Nodes have aspects (traits) that define
their capabilities. Messages target (node_id, aspect_id, method_id) tuples.

### 2. Aspect System (ECS-like composition)
Nodes can have multiple aspects attached. Aspects are identified by FNV-hashed names. The aspect
hierarchy supports inheritance (e.g., Spatial inherits Owned + SpatialRef).

### 3. Code Generation from KDL IDL
The fusion crate's build.rs reads KDL protocol files and generates Rust types, trait definitions,
and client-side method stubs. This ensures wire-compatible types across client and server.

### 4. Spatial Universal Interaction System (SUIS)
Input methods (pointer/hand/tip) are matched with input handlers through signed distance fields.
The system uses field distance for prioritization and supports capture semantics for exclusive
interaction (e.g., grabbing prevents other interactions).

### 5. DMA-BUF Texture Sharing
Zero-copy GPU texture sharing between Wayland clients and the 3D compositor via Linux DMA-BUF,
using explicit sync with timeline sync objects.

### 6. D-Bus Object Registry
Objects (HMD, play space, spatials, fields) are registered on D-Bus for cross-client discovery.
The gluon crate provides a query system to watch for object lifecycle events.

### 7. Session Persistence
Clients can save state (positions, custom data) that survives server restarts. State tokens
are passed via environment variables for spawned processes.

---

## 8. RELEVANCE TO GLASSES SDK

StardustXR provides the reference architecture for:
1. **Spatial computing on Linux** — positions 2D and 3D content in physical space
2. **Hand/controller/pointer input** — full hand tracking with gesture detection heuristics
3. **Wayland integration** — compositing traditional apps into XR
4. **Client-server protocol** — FlatBuffers over Unix sockets with FD passing
5. **Field-based interaction** — SDF shapes for spatial input targeting
6. **Panel system** — 2D window management in 3D space

Key integration points for a Glasses SDK:
- Use fusion crate to build StardustXR clients
- Input system (Hand struct with pinch/fist detection) for gesture recognition
- Spatial hierarchy for positioning content relative to user
- Field system for interaction boundaries
- PanelItem system for embedding 2D apps
- D-Bus object registry for service discovery
