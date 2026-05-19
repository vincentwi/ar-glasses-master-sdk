# P2P Walkie-Talkie Implementation Research
## Comprehensive Analysis of 6 Open-Source Repos
### Target: AR Glasses Walkie-Talkie (RayNeo X3 Pro, Android 12, Snapdragon XR2)

---

## REPO 1: fajf/P2P-WalkieTalkie (Android/Java)
**Status: SKELETON ONLY - Abandoned WIP**

### Architecture
- WiFi Direct (P2P) based Android app
- Uses Android's WifiP2pManager for discovery
- Activity/Fragment/ViewModel pattern

### Key Files
- `EstablishConnection.java` - Main activity, loads fragment
- `EstablishConnectionFragment.java` - UI stub
- `EstablishConnectionViewModel.java` - Empty ViewModel with TODO comments

### What We Learn
- WiFi Direct is the intended transport (requires both devices on same WiFi OR WiFi Direct pairing)
- Project was abandoned before audio/PTT implementation

### Verdict: NOT USEFUL - Only a scaffold. Skip.

---

## REPO 2: devapro/LANwalkieTalkie (Android/Kotlin)
**Status: FULLY IMPLEMENTED - Excellent reference for our use case**

### Architecture Overview
- **Multi-module Android app** with clean MVI architecture
- Modules: `app`, `core`, `core-ui`, `feature-ptt`, `feature-chat`, `feature-settings`, `service-voice`, `serivce-network` (sic)
- **LAN-based** using NSD (Network Service Discovery) for auto-discovery
- **TCP sockets** for audio streaming (NOT UDP!)
- Foreground Service keeps connection alive

### Audio Capture (VoiceRecorder.kt)
```kotlin
// Key parameters:
AudioSource = MediaRecorder.AudioSource.MIC
Format = AudioFormat.ENCODING_PCM_16BIT
Channel = AudioFormat.CHANNEL_IN_MONO
Sample rates tried: [8000, 11025, 16000, 22050, 44100] // picks lowest supported
readBufferSize = 8192 bytes

// Recording loop:
while (recordingState == RECORDSTATE_RECORDING) {
    val bytes = ByteArray(readBufferSize)
    val readCount = audioRecord.read(bytes, 0, readBufferSize)
    if (readCount > 0) {
        chanelController.sendMessage(ByteBuffer.wrap(bytes))
    }
}
```

### Audio Playback (VoicePlayer.kt)
```kotlin
// Playback setup:
AudioManager.STREAM_MUSIC
AudioFormat.CHANNEL_OUT_MONO
AudioFormat.ENCODING_PCM_16BIT
AudioTrack.MODE_STREAM
AudioTrack.WRITE_NON_BLOCKING  // KEY: non-blocking writes for low latency

// Buffer size formula:
bufferSize = sampleRate * (Short.SIZE / Byte.SIZE) * 4
// Then divided by 4 for AudioTrack constructor (quarter buffer for responsiveness)

// Data listener pattern:
socketServer.dataListener = { bytes -> play(bytes) }
```

### PTT Mechanism (PTTButton.kt - Compose)
```kotlin
// Uses Compose gesture detection:
detectTapGestures(
    onPress = {
        isPressed.value = true
        onPress()  // -> dispatches PttAction.StartRecording
        awaitRelease()  // BLOCKS until finger lifted
        isPressed.value = false
        onRelease()  // -> dispatches PttAction.StopRecording
    }
)

// State machine via MVI:
PttAction.StartRecording -> voiceRecorder.startRecord()
PttAction.StopRecording -> voiceRecorder.stopRecord()
```

### Network Protocol
- **Discovery**: Android NSD (mDNS/DNS-SD) with service type `_wfwt._tcp`
- **Transport**: TCP sockets (both server and client per device)
- **Server**: ServerSocket on random port (8111-9999), accepts multiple connections
- **Client**: Connects to discovered services, auto-reconnects on failure
- **Message discrimination**: `if (data.size > 20)` -> audio; else -> text/ping/pong
- **Keepalive**: "ping"/"pong" messages every 5 seconds
- **Socket config**:
  ```kotlin
  sendBufferSize = 8192
  receiveBufferSize = 8192 * 2
  tcpNoDelay = true  // Nagle disabled for low latency
  ```

### Key Design Patterns
1. **Dual socket model**: Each device runs BOTH a server AND a client
2. **ConcurrentHashMap<String, LinkedBlockingDeque<ByteBuffer>>** for per-peer output queues
3. **Coroutine-based** with `limitedParallelism(1)` for recording thread
4. **Koin DI** for dependency injection
5. **WakeLock** for keeping CPU alive during PTT

### Adaptable for AR Glasses
- **PTT pattern**: `onPress/awaitRelease/onRelease` can map to temple tap gesture
- **VoiceRecorder**: Almost directly usable, change AudioSource to VOICE_RECOGNITION
- **VoicePlayer**: Good pattern for bone conduction output
- **NSD discovery**: Perfect for WiFi LAN discovery between two glasses
- **TCP with tcpNoDelay**: Simple and reliable for two-device scenario

### Limitations
- **No codec/compression**: Sends raw PCM16 over TCP (wastes bandwidth)
- **TCP not ideal**: Head-of-line blocking can cause latency spikes
- **Sample rate autodetect**: May pick 8kHz instead of 16kHz on some devices
- **No echo cancellation**: Would need AEC for bone conduction speakers
- **readBufferSize=8192**: At 16kHz mono 16-bit, that's ~256ms chunks - too much latency

---

## REPO 3: bschwind/walkie-talkie (ESP32/C with ESP-NOW)
**Status: CLEAN, MINIMAL, EXCELLENT ARCHITECTURE**

### Architecture Overview
- ESP32 firmware using ESP-NOW (WiFi layer 2 broadcast, no TCP/IP stack)
- **3-task model**: audio_capture_task, audio_playback_task, sender_task
- **FreeRTOS StreamBuffers** connect tasks (zero-copy pipe)
- Always-on duplex audio (no PTT needed)

### Audio Config
```c
#define SAMPLE_RATE (16000)           // 16 kHz - matches our target
#define BITS_PER_SAMPLE (I2S_BITS_PER_SAMPLE_16BIT)
#define READ_BUF_SIZE_BYTES (250)     // ~7.8ms per chunk at 16kHz mono 16-bit
// I2S MEMS mic (INMP441) + I2S DAC (PCM5102A)
// DMA: 4 buffers x 256 samples
```

### Data Flow Architecture (BRILLIANT SIMPLICITY)
```
[I2S Mic] -> audio_capture_task -> mic_stream_buf(512B) -> sender_task -> [ESP-NOW broadcast]
[ESP-NOW recv_callback] -> network_stream_buf(512B) -> audio_playback_task -> [I2S Speaker]
```

### Transport (ESP-NOW)
```c
// ESP-NOW: Layer 2 WiFi, no TCP/IP, <1ms latency
// Broadcast to all peers on channel 12
broadcast_mac = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}
// High-speed mode enabled:
esp_wifi_internal_set_fix_rate(ESP_IF_WIFI_STA, 1, WIFI_PHY_RATE_MCS7_SGI)
// Packet size: 250 bytes = ~7.8ms of audio at 16kHz/16-bit
// ESP-NOW max payload: 250 bytes (perfect fit!)
```

### Latency Optimization
1. **Tiny buffers**: 250 bytes = ~7.8ms per packet
2. **StreamBuffer with trigger=1**: Task wakes on any byte arrival
3. **No codec overhead**: Raw PCM16 direct from I2S
4. **ESP-NOW**: No TCP/IP stack, no handshake, ~1ms transport
5. **DMA double buffering**: Hardware handles I2S without CPU
6. **Total theoretical latency**: ~15-25ms end-to-end

### Adaptable for AR Glasses
- **StreamBuffer pattern**: Map to Android's BlockingQueue or Channel
- **250-byte chunks**: Perfect packet size concept (small = low latency)
- **Loopback testing**: `init_audio(mic_stream_buf, mic_stream_buf)` - great debug trick
- **Architecture**: 3-task model maps perfectly to 3 Android coroutines

### Limitations
- **No PTT**: Always-on duplex (fine for ESP, but we need PTT)
- **No codec**: Raw PCM wastes bandwidth
- **ESP-NOW broadcast**: Not directly applicable to Android (needs UDP equivalent)
- **No peer management**: Just broadcasts to everyone on channel

---

## REPO 4: meshenger-app/meshenger-android (Android/Kotlin + WebRTC)
**Status: PRODUCTION-GRADE P2P VOICE/VIDEO - Most sophisticated**

### Architecture Overview
- **WebRTC-based** P2P voice/video calling for Android
- **No server required**: Direct device-to-device over LAN
- **TCP signaling** (port 10001) for call setup, then WebRTC takes over
- **Encrypted**: NaCl/libsodium public key crypto for signaling
- **Contact exchange**: QR codes for sharing public keys

### Audio System (via WebRTC)
```kotlin
// WebRTC handles all audio with hardware acceleration:
JavaAudioDeviceModule.builder(context)
    .setUseHardwareAcousticEchoCanceler(true)   // KEY: HW AEC
    .setUseHardwareNoiseSuppressor(true)        // KEY: HW NS
    .createAudioDeviceModule()

// Audio constraints:
googEchoCancellation = true
googAutoGainControl = true
googHighpassFilter = true
googNoiseSuppression = true
```

### Signaling Protocol
```
Caller                              Callee
  |                                   |
  |-- TCP connect to port 10001 ---->|
  |-- Encrypted JSON {offer} ------->|
  |<-- Encrypted JSON {answer} ------|
  |                                   |
  |<====== WebRTC P2P audio ========>|
```

### Packet Format (PacketReader/PacketWriter)
```kotlin
// Simple length-prefixed framing:
// [4 bytes: message length][N bytes: encrypted JSON payload]
// Header: big-endian int32
fun writeMessageHeader(packet: ByteArray, value: Int) {
    packet[0] = (value shr 24 and 0xff).toByte()
    packet[1] = (value shr 16 and 0xff).toByte()
    packet[2] = (value shr 8 and 0xff).toByte()
    packet[3] = (value shr 0 and 0xff).toByte()
}
```

### Peer Discovery (Connector.kt)
- No mDNS/NSD! Uses stored contact addresses (IPv4/IPv6)
- Tries last working address first, then all stored addresses
- **EUI-64 MAC extraction** from IPv6 for address discovery
- **Neighbor table lookup** via `ip n l` command
- Link-local addresses tried with all network interfaces
- Retry logic with configurable timeout/retries

### WebRTC Configuration
```kotlin
rtcConfig.sdpSemantics = SdpSemantics.UNIFIED_PLAN
rtcConfig.continualGatheringPolicy = ContinualGatheringPolicy.GATHER_ONCE
rtcConfig.enableCpuOveruseDetection = true
// No STUN/TURN servers - direct LAN connection only
// DataChannel for in-call signaling (camera toggle, hangup)
```

### Adaptable for AR Glasses
- **WebRTC approach**: Handles AEC, AGC, noise suppression automatically
- **JavaAudioDeviceModule**: Best audio quality with hardware acceleration
- **DataChannel**: Could carry PTT state ("talking"/"idle") messages
- **Length-prefixed packets**: Clean framing for signaling
- **Network monitor disabled**: `options.disableNetworkMonitor = true` needed for hotspot

### Limitations
- **Overkill for walkie-talkie**: WebRTC adds complexity and library size (~10MB)
- **No PTT mechanism**: Designed for phone calls, not walkie-talkie
- **Connection setup time**: WebRTC ICE gathering takes 1-3 seconds
- **Battery intensive**: WebRTC keeps full duplex audio running
- **Large dependency**: org.webrtc native library

---

## REPO 5: PetteriAimonen/esp-walkie-talkie (ESP8266/C)
**Status: MOST TECHNICALLY IMPRESSIVE - Deep DSP knowledge**

### Architecture Overview
- ESP8266 firmware with custom audio DSP pipeline
- **UDP broadcast** on port 18294 for audio
- **A-law compression** (8:1 ratio) for bandwidth efficiency
- **Echo cancellation** in ISR! (interrupt service routine)
- **Multi-peer** support (up to 4 simultaneous peers)
- **Sigma-delta DAC** for audio output via I2S

### Audio Config
```c
#define AUDIO_SAMPLERATE 12500    // 12.5 kHz
#define AUDIO_BLOCKSIZE 500       // 500 samples = 40ms per packet
#define AUDIO_HDRLEN 8            // 8-byte packet header
#define UDP_PORT 18294
```

### Packet Format
```c
// Total packet: 508 bytes (8 header + 500 A-law samples)
// Header:
//   byte[0]: message counter (sequence number)
//   byte[1-3]: reserved (0)
//   byte[4-7]: sample counter (uint32, for sync)
// Payload: 500 bytes of A-law encoded audio
```

### A-Law Codec (alaw.c)
```c
// Compresses 13-bit signed PCM to 8-bit A-law
// 2:1 compression ratio on wire
uint8_t alaw_encode(int sample);  // PCM -> A-law
int alaw_decode(uint8_t sample);  // A-law -> PCM
// With dithering (quantization error accumulation):
companded = alaw_encode(to_encode + quant_acc);
quant_acc += to_encode - alaw_decode(companded);
```

### Echo Cancellation (IN ISR!)
```c
// 12-tap adaptive filter running at 12.5 kHz in interrupt
int echo_estimated = 0;
for (int i = 0; i < ECHO_CANCEL_LEN; i++) {
    echo_estimated += (dac_history[i] * echo_cancel[i] / 1024 + 2048) / 4096;
}
// LMS-style adaptation:
for (int i = 0; i < ECHO_CANCEL_LEN; i++) {
    echo_cancel[i] += (echo_delta * dac_history[i] + 2048) / 4096;
}
ac_value -= echo_estimated;
```

### Click Removal Filter
```c
// Detects transients >3500 and replaces with interpolated values
// Sliding window of 32 samples for detection
// Prevents button click artifacts from entering audio stream
```

### Peer Discovery
```c
// Broadcast empty UDP packet every 1 second
udp_sendto(pcb, p, IP_ADDR_BROADCAST, UDP_PORT);

// On receive, auto-register peer by IP:port
// Peers timeout after 10 seconds of silence
// Up to 4 peers with round-robin mixing
```

### Multi-peer Audio Mixing
```c
// Mix all active peers in ISR:
int dac_val = 0;
for (int i = 0; i < MAX_PEERS; i++) {
    if (g_peers[i].current_buf) {
        uint8_t sample = payload[AUDIO_HDRLEN + current_pos];
        dac_val += alaw_decode(sample);
    }
}
dac_val = (dac_val * get_volume()) / 16;  // volume control
```

### Volume Control (user_main.c)
```c
// Two hardware buttons: volume up/down
// Volume range: 1-16 (multiplier in audio mixing)
// Debounced with frame-based edge detection
```

### Adaptable for AR Glasses
- **A-Law codec**: Simple, low-CPU, reduces bandwidth by 50%
- **Echo cancellation algorithm**: Adaptable for bone conduction speakers
- **Click removal**: Useful for filtering temple tap gestures from audio
- **Packet format**: 8-byte header + audio payload is clean and simple
- **UDP broadcast discovery**: Map to Android UDP multicast
- **Peer timeout**: Auto-cleanup after 10 seconds of silence
- **Audio mixing**: Multi-peer mixing is bonus for group chat

### Limitations
- **ESP8266 specific**: Lots of hardware-specific code
- **Audio noise issues**: Author calls it "a somewhat failed attempt" due to RF noise
- **Low sample rate**: 12.5 kHz (we want 16 kHz)
- **No encryption**: All audio broadcast in clear

---

## REPO 6: Xinyuan-LilyGO/T-TWR (ESP32-S3/Arduino)
**Status: HARDWARE PLATFORM - LoRa radio walkie-talkie**

### Architecture Overview
- ESP32-S3 + SA868 UHF/VHF radio module
- Hardware walkie-talkie with OLED display
- **Physical PTT button** on hardware (BUTTON_PTT_PIN)
- Rotary encoder for menu navigation
- GPS, BLE, WiFi, SD card, BME280 sensor support
- Actual radio transmission (UHF/VHF analog FM)

### PTT Mechanism
```cpp
// Hardware PTT using AceButton library with GPIO
const uint8_t buttonPins[] = {
    ENCODER_OK_PIN,
    BUTTON_PTT_PIN,    // Physical PTT button
    BUTTON_DOWN_PIN
};

// Radio control:
radio.transmit();  // Key up radio TX
radio.receive();   // Switch to RX mode

// Mic routing:
twr.routingMicrophoneChannel(TWRClass::TWR_MIC_TO_ESP);   // Mic -> ESP ADC
twr.routingMicrophoneChannel(TWRClass::TWR_MIC_TO_SA868); // Mic -> Radio
```

### Audio Routing
```
Microphone -> ESP32 ADC (GPIO15) or SA868 audio input (GPIO18)
SA868 audio output -> ESP32 DAC or Speaker amplifier
// Switchable routing between ESP processing and direct radio
```

### Adaptable for AR Glasses
- **PTT state machine concept**: Press=TX, Release=RX is fundamental pattern
- **AceButton library**: Good debouncing/event model for gesture-based PTT
- **Audio routing concept**: Mic -> Processor -> Network is same pattern

### Limitations
- **Analog FM radio**: Not relevant for WiFi-based app
- **Hardware-specific**: SA868 radio module code not portable
- **No digital audio processing**: Analog audio path through radio

---

## SYNTHESIS: Best Patterns for AR Glasses Walkie-Talkie

### Recommended Architecture (Combining Best of Each)

```
┌──────────────────────────────────────────────────┐
│                AR Glasses App                     │
│                                                   │
│  [Temple Tap] ──> PTT State Machine               │
│       │              │                            │
│       │         ┌────▼─────┐                      │
│       │         │ RECORDING│                      │
│       │         └────┬─────┘                      │
│       │              │                            │
│  ┌────▼──────┐  ┌────▼──────┐  ┌───────────┐    │
│  │AudioRecord│  │ A-Law     │  │ UDP/TCP   │    │
│  │16kHz Mono │──│ Encoder   │──│ Sender    │────│──> Network
│  │PCM16      │  │ (50% BW)  │  │ (~250B)   │    │
│  └───────────┘  └───────────┘  └───────────┘    │
│                                                   │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐    │
│  │AudioTrack │  │ A-Law     │  │ UDP/TCP   │    │
│  │Bone Cond. │◄─│ Decoder   │◄─│ Receiver  │◄───│── Network
│  │Speaker    │  │           │  │           │    │
│  └───────────┘  └───────────┘  └───────────┘    │
│                                                   │
│  [NSD Discovery] ── Auto-find peer on LAN         │
└──────────────────────────────────────────────────┘
```

### Component Selection Matrix

| Component | Best Source | Why |
|-----------|-----------|-----|
| Audio Capture | LANwalkieTalkie | Android AudioRecord, ready-to-use Kotlin |
| Audio Playback | LANwalkieTalkie | AudioTrack with WRITE_NON_BLOCKING |
| Audio Codec | esp-walkie-talkie | A-law codec is simple, effective |
| PTT State Machine | LANwalkieTalkie | Compose gesture -> MVI action pattern |
| Network Discovery | LANwalkieTalkie | NSD (_wfwt._tcp) auto-discovery |
| Packet Format | esp-walkie-talkie | 8-byte header + audio payload |
| Echo Cancellation | Meshenger (WebRTC) | Hardware AEC via JavaAudioDeviceModule |
| Click Removal | esp-walkie-talkie | Filter temple-tap artifacts |
| Socket Management | LANwalkieTalkie | TCP with tcpNoDelay, reconnect logic |
| Stream Buffer | walkie-talkie | FreeRTOS StreamBuffer -> Kotlin Channel |

### Critical Parameters for AR Glasses

```
Audio Source: VOICE_RECOGNITION (not MIC - better for bone conduction)
Sample Rate: 16000 Hz
Bit Depth: 16-bit PCM
Channel: MONO
Chunk Size: 320 bytes (10ms at 16kHz/16-bit) for LOW latency
  - NOT 8192 bytes like LANwalkieTalkie (that's 256ms!)
  - NOT 250 bytes like walkie-talkie (that's 7.8ms, good but odd size)
  - 320 bytes = 10ms = clean boundary, good latency/overhead balance
With A-law: 160 bytes per 10ms chunk (50% compression)
Target latency: <100ms end-to-end
Discovery: NSD on shared WiFi network
Transport: UDP preferred (no HOL blocking), TCP fallback
```

### Key Code Snippets to Adapt

**1. AudioRecord Setup (from LANwalkieTalkie, modified)**
```kotlin
val audioRecord = AudioRecord(
    MediaRecorder.AudioSource.VOICE_RECOGNITION,  // Better for voice
    16000,                                          // 16 kHz
    AudioFormat.CHANNEL_IN_MONO,
    AudioFormat.ENCODING_PCM_16BIT,
    AudioRecord.getMinBufferSize(16000, CHANNEL_IN_MONO, ENCODING_PCM_16BIT) * 2
)
```

**2. PTT via Temple Tap (adapted from LANwalkieTalkie)**
```kotlin
// Map temple tap gesture to PTT
fun onTempleTapDown() {
    viewModel.onAction(PttAction.StartRecording)
}
fun onTempleTapUp() {
    viewModel.onAction(PttAction.StopRecording)
}
```

**3. Small-Chunk Streaming (adapted from walkie-talkie)**
```kotlin
// 10ms chunks for low latency
val CHUNK_SIZE = 320  // 10ms at 16kHz mono 16-bit
val buffer = ByteArray(CHUNK_SIZE)
while (recording) {
    val read = audioRecord.read(buffer, 0, CHUNK_SIZE)
    if (read > 0) {
        val encoded = alawEncode(buffer, read)  // 160 bytes
        udpSocket.send(DatagramPacket(encoded, encoded.size, peerAddr, PORT))
    }
}
```

**4. NSD Discovery (from LANwalkieTalkie)**
```kotlin
val SERVICE_TYPE = "_arwt._tcp"  // AR Walkie Talkie
nsdManager.registerService(serviceInfo, NsdManager.PROTOCOL_DNS_SD, listener)
nsdManager.discoverServices(SERVICE_TYPE, NsdManager.PROTOCOL_DNS_SD, discoveryListener)
```

**5. A-Law Codec (from esp-walkie-talkie, ported to Kotlin)**
```kotlin
fun alawEncode(sample: Int): Byte {
    val ALAW_MAX = 0xFFF
    var s = if (sample < 0) -sample else sample
    val sign: Int = if (sample < 0) 0x80 else 0
    if (s > ALAW_MAX) s = ALAW_MAX
    var mask = 0x800; var position = 11
    while ((s and mask) != mask && position >= 5) { mask = mask shr 1; position-- }
    val lsb = (s shr (if (position == 4) 1 else position - 4)) and 0x0f
    return ((sign or ((position - 4) shl 4) or lsb) xor 0x55).toByte()
}
```

### Risk Assessment

| Risk | Mitigation |
|------|------------|
| Temple tap creates audio artifacts | Click removal filter from esp-walkie-talkie |
| Bone conduction speaker echo | WebRTC JavaAudioDeviceModule HW AEC |
| WiFi latency spikes | Small chunks (10ms), UDP transport |
| Battery drain from always-listening | PTT mode (only transmit when pressed) |
| Discovery failures | NSD + fallback to hardcoded IP |
| Audio quality on bone conduction | VOICE_RECOGNITION source, AGC, noise suppression |
