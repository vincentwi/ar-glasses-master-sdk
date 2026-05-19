# Deep-Dive Research: Zello PTT & BeatSync Multi-Device Audio Sync
## For AR Glasses Walkie-Talkie Implementation

---

## 1. ZELLO CHANNEL API — Architecture & Protocol

### 1.1 Overview
Zello Channel API is a WebSocket-based protocol for push-to-talk voice communication over the internet. It uses JSON text messages for control signaling and binary WebSocket messages for audio data, all over a single persistent WSS connection.

### 1.2 WebSocket Protocol (CRITICAL for our implementation)

**Connection URLs:**
- Consumer: `wss://zello.io/ws`
- Work: `wss://zellowork.io/ws/{network}`
- Enterprise: `wss://{domain}/ws/mesh`

**Dual-Message Protocol:**
- TEXT messages (JSON): Control commands (logon, start_stream, stop_stream, events)
- BINARY messages: Audio data packets with 9-byte headers

**Binary Packet Format:**
```
{type(8), stream_id(32 big-endian), packet_id(32 big-endian), data[]}
```
- Type 0x01 = audio stream data
- Type 0x02 = image data
- Total header: 9 bytes (1 + 4 + 4)
- packet_id is server-assigned on incoming, zeroed on outgoing

### 1.3 Audio Codec & Streaming

**Codec: Opus (mandatory)**
- Sample rate: 16000 Hz (16kHz) — voice-optimized
- Frame size: 20ms (default), range 2.5-60ms
- Frames per packet: 1
- Encoder application: 2048 (OPUS_APPLICATION_VOIP)
- Channels: 1 (mono)

**Codec Header (4 bytes, base64-encoded):**
```
byte 0-1: sample_rate_hz (16-bit little-endian) = 0x3E80 = 16000
byte 2:   frames_per_packet = 1
byte 3:   frame_size_ms = 60 (or 20)
```
Example: `gD4BPA==` = {0x80, 0x3e, 0x01, 0x3c} = 16kHz, 1 frame, 60ms

### 1.4 PTT State Machine (Zello's Model)

```
IDLE ──── [user presses PTT] ────> CONNECTING
  ^                                    |
  |                          [start_stream response]
  |                                    v
  |                              TRANSMITTING
  |                                    |
  |                        [user releases PTT]
  |                                    v
  └──────────────────────────── STOP_STREAM ──> IDLE

IDLE ──── [on_stream_start event] ──> RECEIVING
  ^                                      |
  |                           [on_stream_stop event]
  └──────────────────────────────────────┘
```

**Key states from Zello Android SDK:**
- `MessageIn.isActive()` — receiving incoming voice
- `MessageOut.isActive()` — transmitting outgoing voice
- `MessageOut.isConnecting()` — stream being established
- Contact statuses: OFFLINE, AVAILABLE, CONNECTING, BUSY, STANDBY

**PTT Touch Handler (from PttActivity.java):**
```java
_pttButton.setOnTouchListener((v, event) -> {
    int action = event.getAction();
    if (action == MotionEvent.ACTION_DOWN) {
        Zello.getInstance().beginMessage();
    } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
        Zello.getInstance().endMessage();
    }
    return false;
});
```

### 1.5 Stream Lifecycle (Detailed)

**Outgoing (Transmit):**
1. `start_stream` JSON command with codec params → server returns `stream_id`
2. Recorder captures PCM → Opus encoder → binary packets with stream_id
3. Each packet: 9-byte header + opus data, sent via `ws.send(binary)`
4. `stop_stream` JSON command when done

**Incoming (Receive):**
1. `on_stream_start` event with codec_header, stream_id, from, channel
2. Binary packets arrive with matching stream_id
3. Opus decoder → PCM → audio player
4. `on_stream_stop` event signals end

### 1.6 Channel Management

- Logon specifies channel(s) as string array
- Up to 100 channels on Zello Work
- Channel status: `online` / `offline` with `users_online` count
- `on_channel_status` event for status changes
- Direct messaging via `for` parameter on any command
- Talk priority: NORMAL=100, LOW=10

### 1.7 Connection Resilience

- Server sends WebSocket Ping every 30s, expects Pong within 30s
- Client-side heartbeat via `keepalive` command
- Reconnect with exponential retry (default 1s interval, 5 attempts)
- `refresh_token` for fast re-authentication
- `session_connection_lost` event triggers auto-reconnect

### 1.8 Key Source Files (JS SDK)

| File | Purpose |
|------|---------|
| `session.js` | WebSocket connection, auth, message routing, heartbeat |
| `outgoingMessage.js` | PTT transmit: recorder → encoder → binary packets |
| `recorder.js` | AudioWorklet/ScriptProcessor mic capture (PCM) |
| `encoder.js` | Opus encoding via Web Worker (WASM) |
| `decoder.js` | Opus decoding |
| `player.js` | Audio playback via Web Audio API |
| `incomingMessage.js` | Incoming stream handling |
| `constants.js` | All event names, error codes, message types |
| `utils.js` | Binary packet builder, codec header builder/parser |

### 1.9 Key Source Files (Android SDK)

| File | Purpose |
|------|---------|
| `Zello.java` | Singleton entry point, configure/unconfigure, beginMessage/endMessage |
| `Events.java` | Callback interface: onMessageStateChanged, onAppStateChanged |
| `MessageIn.java` | Incoming message state (isActive, getFrom, getAuthor) |
| `MessageOut.java` | Outgoing message state (isActive, isConnecting) |
| `Contact.java` | Contact model (type, status, muted) |
| `AppState.java` | App state (isSignedIn, isSigningIn) |
| `Audio.java` | Audio mode management (SPEAKER, EARPIECE, BLUETOOTH) |
| `PttActivity.java` | Sample PTT app with touch handler |
| `headset/*.kt` | Bluetooth headset/media button PTT handling |

---

## 2. BEATSYNC — Multi-Device Audio Synchronization

### 2.1 Architecture Overview

BeatSync is a Turborepo monorepo achieving millisecond-accurate synchronized audio playback across multiple devices. Architecture:

```
Client (Next.js) <──WebSocket──> Server (Bun) <──WebSocket──> Client N
                                    |
                                 R2 Storage (audio files)
```

### 2.2 NTP-Inspired Time Synchronization (CRITICAL PATTERN)

**Protocol (4-timestamp NTP):**
```
Client                     Server
  |                           |
  |── t0 (client send) ──>   |
  |                     t1 (server recv)
  |                     t2 (server send)
  |   <── t0,t1,t2 ─────    |
  t3 (client recv)            |
  
  RTT = (t3 - t0) - (t2 - t1)
  Clock offset = ((t1 - t0) + (t2 - t3)) / 2
```

**Key Parameters:**
- Initial probe interval: 50ms (rapid measurement)
- Steady-state interval: 2500ms (heartbeat)
- Minimum measurements before "synced": 10+ (MAX_MEASUREMENTS = 16)
- RTT smoothing: Exponential Moving Average (alpha = 0.2)
- Stale timeout: 3750ms (1.5 × steady interval)
- High-precision time: `performance.timeOrigin + performance.now()`

**Coded Probes (Huygens algorithm):**
- Probe gap: 25ms between pairs
- Gap tolerance: ±5ms
- Avoids TCP coalescing of small packets

### 2.3 Scheduled Action Execution (KEY PATTERN)

BeatSync doesn't send "play now" — it sends "play at server_time X":

```
Server: Calculate serverTimeToExecute = epochNow() + scheduleDelayMs
        scheduleDelayMs = max(400ms, maxClientRTT × 1.5 + 200ms)
        Cap: 3000ms maximum

Client: Receive SCHEDULED_ACTION with serverTimeToExecute
        Calculate: localExecutionTime = serverTimeToExecute + clockOffset
        Wait until: performance.now() reaches localExecutionTime
        Execute action at exact moment
```

**Dynamic Delay Calculation:**
```typescript
function calculateScheduleTimeMs(maxRTT: number): number {
    const dynamicDelay = Math.max(400, maxRTT * 1.5 + 200);
    return Math.min(dynamicDelay, 3000);
}
```

### 2.4 Audio Loading Coordination (before play)

1. Server broadcasts `LOAD_AUDIO_SOURCE` to all clients
2. Each client loads/decodes audio → responds `AUDIO_SOURCE_LOADED`
3. Server waits for ALL clients (or 3s timeout)
4. THEN schedules synchronized play via `SCHEDULED_ACTION`

### 2.5 Late-Joiner Sync

When a client joins during playback:
```typescript
// Calculate where in the track the new client should start
const timeElapsedAtExecution = serverTimeToExecute - serverTimeWhenPlaybackStarted;
const resumePosition = startPosition + timeElapsedAtExecution / 1000;
// Send unicast PLAY to late client only
```

### 2.6 Room Management

- Room IDs: 6-digit codes
- In-memory state (no database)
- Manager hierarchy: GlobalManager → RoomManager → ChatManager
- Room cleanup: 60s after last client disconnects
- Client data cached for rejoin scenarios
- Periodic backup to R2 every 60s

### 2.7 Key Source Files (BeatSync)

| File | Purpose |
|------|---------|
| `RoomManager.ts` | Per-room state, scheduled actions, audio load coordination |
| `GlobalManager.ts` | All rooms, active user count |
| `ntpRequest.ts` | NTP 4-timestamp response handler |
| `sync.ts` | Late-joiner sync handler |
| `play.ts` | Play initiation with audio loading |
| `config.ts` | Schedule delay calculation |
| `constants.ts` | NTP intervals, probe params |
| `utils.ts` | `epochNow()` high-precision time |
| `registry.ts` | Type-safe WebSocket handler dispatch |
| `websocketHandlers.ts` | Connection lifecycle |

---

## 3. PATTERNS FOR AR GLASSES WALKIE-TALKIE

### 3.1 Recommended Architecture

```
Glass A                     Relay Server                   Glass B
(Android)                   (lightweight)                  (Android)
  |                              |                            |
  |──WSS JSON: logon ──────>    |                            |
  |                              | <──── WSS JSON: logon ─── |
  |                              |                            |
  |──JSON: start_stream ──>     |                            |
  |                              |── JSON: on_stream_start ──>|
  |──Binary: opus packets──>    |                            |
  |                              |── Binary: opus packets ──> |
  |──JSON: stop_stream ───>     |                            |
  |                              |── JSON: on_stream_stop ──> |
```

### 3.2 Codec Configuration for Glasses

**Optimal Opus Settings for Low Latency Voice:**
```
Sample rate: 16000 Hz (sufficient for voice)
Frame size: 20ms (good balance of latency vs efficiency)
Frames per packet: 1 (lowest latency)
Application: VOIP (2048)
Bitrate: 16-24 kbps (voice)
Complexity: 5-7 (balanced CPU)
```

**Expected Latency Budget:**
```
Mic capture: ~20ms (one frame)
Opus encode: ~2ms
Network (local WiFi): ~5-20ms RTT
Opus decode: ~2ms
Audio output: ~20ms (one buffer)
Total one-way: ~50-65ms (excellent for conversation)
```

### 3.3 Android Implementation with AudioRecord/AudioTrack

**Recording (AudioRecord):**
```java
int sampleRate = 16000;
int channelConfig = AudioFormat.CHANNEL_IN_MONO;
int audioFormat = AudioFormat.ENCODING_PCM_16BIT;
int bufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat);
// Use 20ms frames = 320 samples at 16kHz
int frameSize = 320; // 16000 * 0.020
```

**Playback (AudioTrack):**
```java
AudioTrack track = new AudioTrack.Builder()
    .setAudioAttributes(new AudioAttributes.Builder()
        .setUsage(AudioAttributes.USAGE_VOICE_COMMUNICATION)
        .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
        .build())
    .setAudioFormat(new AudioFormat.Builder()
        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
        .setSampleRate(16000)
        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
        .build())
    .setBufferSizeInBytes(bufferSize)
    .setPerformanceMode(AudioTrack.PERFORMANCE_MODE_LOW_LATENCY)
    .build();
```

### 3.4 PTT State Machine for Glasses

```
enum PTTState {
    IDLE,           // No voice activity
    CONNECTING,     // start_stream sent, waiting for stream_id
    TRANSMITTING,   // Recording mic, encoding, sending
    RECEIVING,      // Playing incoming audio
    ERROR           // Connection lost
}

Transitions:
    IDLE → CONNECTING:      User activates PTT (button/gesture/voice)
    CONNECTING → TRANSMITTING: Server returns stream_id
    CONNECTING → IDLE:      Server error / timeout (3s)
    TRANSMITTING → IDLE:    User releases PTT
    IDLE → RECEIVING:       on_stream_start from other glass
    RECEIVING → IDLE:       on_stream_stop from other glass
    ANY → ERROR:            WebSocket disconnected
    ERROR → IDLE:           Reconnection successful
```

### 3.5 BeatSync-Inspired Time Sync for Glasses

For two glasses that need synchronized audio (e.g., group call with position-aware audio):

1. **NTP Clock Sync**: Both glasses sync clocks with relay server
   - Initial burst: 16 probes at 50ms intervals
   - Steady-state: probe every 2.5s (also serves as heartbeat)
   - EMA smoothing (alpha=0.2) for RTT estimation

2. **Scheduled Actions**: Server sends `serverTimeToExecute`
   - Each glass converts to local time using clock offset
   - Both execute at same real-world moment
   - Scheduling delay: max(400ms, maxRTT × 1.5 + 200ms)

3. **For PTT (simpler than BeatSync):**
   - Don't need pre-loading coordination (voice is real-time)
   - Don't need track position sync
   - DO need clock sync for accurate voice-activity-detection timestamps
   - DO need RTT measurement for latency display

### 3.6 Connection Resilience for AR Glasses

From Zello's patterns:
- WebSocket with 30s keepalive ping/pong
- Auto-reconnect with exponential backoff (1s, 2s, 4s...)
- Max 5 reconnect attempts before giving up
- Refresh token for fast re-auth after brief disconnection
- Power saving mode when glass screen off

### 3.7 Binary Protocol Design (Adapted from Zello)

**Minimal packet header for glasses (9 bytes, same as Zello):**
```
Byte 0:     Message type (0x01 = audio)
Bytes 1-4:  Stream ID (uint32, big-endian)
Bytes 5-8:  Packet ID (uint32, big-endian)
Bytes 9+:   Opus-encoded audio data
```

**JSON Control Messages (simplified):**
```json
// Join
{"cmd":"join", "seq":1, "user":"glass_A", "room":"pair_123"}

// Start talking
{"cmd":"start", "seq":2, "room":"pair_123", "codec":"opus",
 "rate":16000, "frame":20}

// Stop talking  
{"cmd":"stop", "seq":3, "stream_id":42}

// Events from server
{"cmd":"talking", "stream_id":42, "from":"glass_B"}
{"cmd":"stopped", "stream_id":42}
{"cmd":"status", "room":"pair_123", "users":2}
```

---

## 4. IMPLEMENTATION RECOMMENDATIONS

### 4.1 For Minimum Viable Walkie-Talkie

1. **Protocol**: WebSocket (WSS) with JSON control + binary audio
2. **Codec**: Opus at 16kHz/20ms/mono via Android's native Opus or libopus
3. **Server**: Lightweight relay (Node.js/Bun) — just routes packets between paired glasses
4. **PTT**: Touch event (ACTION_DOWN/UP) or physical button on glasses
5. **State machine**: 5 states (IDLE, CONNECTING, TX, RX, ERROR)
6. **Heartbeat**: 30s ping/pong + NTP probes every 2.5s
7. **Audio**: AudioRecord (VOICE_COMMUNICATION) + AudioTrack (LOW_LATENCY)

### 4.2 From BeatSync We Should Adopt

- NTP 4-timestamp clock sync protocol (for latency measurement)
- EMA RTT smoothing (alpha=0.2)
- High-precision timing via `SystemClock.elapsedRealtimeNanos()`
- Scheduled action pattern (execute at agreed server time)
- Room-based architecture with 6-digit codes
- Client data caching for reconnection

### 4.3 From Zello We Should Adopt

- Opus codec at 16kHz with 20ms frames
- 9-byte binary packet header format
- Stream ID based multiplexing
- JSON+Binary dual WebSocket protocol
- PTT touch handler pattern (ACTION_DOWN/UP)
- Channel status events
- Talk priority system
- Audio mode switching (speaker/earpiece/bluetooth)
- `for` parameter for direct messaging within a channel

### 4.4 What NOT to Copy

- Zello Android SDK is a wrapper around the Zello app (IPC via ContentProvider) — NOT standalone. We need direct WebSocket implementation.
- BeatSync's audio loading coordination (we're streaming real-time, not playing pre-loaded tracks)
- BeatSync's spatial audio grid (overkill for 2 glasses)
- Zello's JWT auth complexity (simple shared room codes suffice)

---

## 5. SUMMARY OF KEY FINDINGS

| Aspect | Zello Pattern | BeatSync Pattern | Our Glasses Approach |
|--------|--------------|------------------|---------------------|
| Transport | WSS JSON+Binary | WSS JSON only | WSS JSON+Binary |
| Codec | Opus 16kHz/20ms | Web Audio API (pre-loaded) | Opus 16kHz/20ms |
| Latency | ~100-200ms (via cloud) | ~400ms+ (scheduled) | ~50-65ms (direct relay) |
| Time Sync | Server ping/pong | NTP 4-timestamp | NTP 4-timestamp |
| PTT Trigger | Touch ACTION_DOWN/UP | N/A (music player) | Touch/Button/Voice |
| Room Model | Named channels | 6-digit room codes | 6-digit pair codes |
| Reconnect | 5 attempts, 1s retry | NTP heartbeat | 5 attempts + NTP |
| Audio API | WebAudio/native | Web Audio API | AudioRecord/AudioTrack |
