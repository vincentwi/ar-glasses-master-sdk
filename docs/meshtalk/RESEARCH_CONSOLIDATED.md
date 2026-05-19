# AR Glasses Walkie-Talkie — Consolidated Research

**Date:** 2025-05-19
**Scope:** Two RayNeo X3 Pro glasses → tap-to-talk → voice over WiFi (Phase 1), mesh (Phase 2)

## Hardware Confirmed

- **Glasses A**: A06B4A8FF4A1633 (ARGF20, Android 12, clean — no apps)
- **Glasses B**: A06B4A94CC51663 (ARGF20, Android 12, has existing apps)
- **Build host**: Mac Mini with ADB at /opt/homebrew/bin/adb
- **Build target**: MacBook (vinceroy@100.81.56.107) has JDK 21 + Android SDK
- **WiFi**: Currently OFF on both — needs to be enabled and connected to same network
- **Display**: 1280x480 binocular (640x480 per eye)
- **Audio**: Mic via AudioRecord (VOICE_RECOGNITION source, 16kHz mono PCM16), bone conduction speakers
- **Gestures**: Temple tap (Click, DoubleClick, TripleClick, SlideContinuous)

## Research Summary (1500+ lines across 3 docs)

### Best Patterns Extracted

| Component | Best Source | Pattern |
|-----------|-----------|---------|
| **Audio capture** | LANwalkieTalkie | AudioRecord + VOICE_RECOGNITION, 16kHz mono PCM16 |
| **Audio playback** | LANwalkieTalkie + skill | AudioTrack LOW_LATENCY, USAGE_ASSISTANT for bone conduction, 15x volume boost |
| **Codec** | Zello + esp-walkie-talkie | Opus 16kHz/20ms for quality; A-law as fallback (simpler, 50% compression) |
| **PTT trigger** | Zello + LANwalkieTalkie | ACTION_DOWN→beginMessage, ACTION_UP→endMessage; temple Click for glasses |
| **State machine** | Zello | 5 states: IDLE → CONNECTING → TX → IDLE; IDLE → RX → IDLE; ANY → ERROR |
| **Network transport** | walkie-talkie (ESP32) | UDP preferred (no HOL blocking), 320-byte chunks (10ms at 16kHz) |
| **Discovery** | LANwalkieTalkie | NSD (mDNS/DNS-SD) for auto-discovery on LAN |
| **Relay protocol** | Zello | WebSocket JSON+Binary, 9-byte header: {type(1), stream_id(4), packet_id(4)} |
| **Echo cancellation** | meshenger + esp-walkie-talkie | WebRTC JavaAudioDeviceModule HW AEC, or LMS adaptive filter |
| **Click removal** | esp-walkie-talkie | Filter temple-tap transients from audio stream |
| **Time sync** | BeatSync | NTP 4-timestamp protocol, EMA (alpha=0.2), high-precision timing |
| **Architecture** | walkie-talkie (ESP32) | 3-task model: capture→send, recv→playback, control; maps to coroutines |
| **Reconnection** | Zello | 30s keepalive, exponential backoff, 5 retries |

### Latency Budget (Phase 1 — WiFi)
- Mic capture: ~10ms (320 samples at 16kHz)
- Opus encode: ~2ms
- Network (local WiFi UDP): ~5-10ms
- Opus decode: ~2ms
- Audio output buffer: ~10ms
- **Total one-way: ~30-45ms** (excellent for conversation)

### Phase 2 — Mesh Network
- **Winner: Reticulum + LXST** protocol
- LXST does voice-over-mesh natively (Opus + Codec2)
- Already proven in Sideband, rnphone, MeshChat, MeshChatX
- User already runs Reticulum (mesh-vision project)
- Codec2 at 1200-3200bps works over LoRa for basic voice
- Dynamic codec switching adapts to available bandwidth
- Meshtastic NOT suitable (text only, 237 byte max, no streaming)

## Key References
- Walkie-talkie repos: ~/walkie-research/ (6 cloned repos)
- Zello/BeatSync research: ~/walkie-research/DEEP_DIVE_RESEARCH.md
- Mesh research: ~/mesh-networking-research-phase2.md
- AR glasses skill: ar-glasses-app-development (comprehensive)
- SDK docs: /tmp/ar-glasses-master-sdk/
- Existing glasses apps: ~/Desktop/APP/Glasses/ (on MacBook)
