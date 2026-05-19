# Mesh Networking Deep-Dive Research for Phase 2 Planning
## Walkie-Talkie on AR Glasses - Mesh Network Migration

**Date:** May 19, 2026
**Purpose:** Comprehensive analysis of mesh networking stacks for real-time voice over mesh between AR glasses

---

## EXECUTIVE SUMMARY

**Winner for AR Glasses Walkie-Talkie: Reticulum + LXST**

After analyzing 11 sources across 6 distinct mesh networking ecosystems, the clear winner for Phase 2 is **Reticulum with LXST protocol**. Here's why:

1. **LXST is purpose-built for real-time voice over mesh** - sub-10ms end-to-end latency claims
2. **Already proven** - Sideband, MeshChat, rnphone all do voice calls over Reticulum
3. **User already has Reticulum experience** (mesh-vision with LXMF on Mac + Pi + glasses)
4. **Codec2 support** at 700bps-3200bps means voice works even over LoRa
5. **OPUS support** from 4.5kbps to 96kbps for higher quality when bandwidth allows
6. **Medium-agnostic** - same code works over WiFi, BLE, LoRa, serial, Internet
7. **Python stack** - easy integration with existing AR glasses software

---

## 1. RETICULUM NETWORK STACK (Core Platform)

### Architecture & Transport Layer
- **Type:** Message-oriented networking stack (not IP-based)
- **Addressing:** 128-bit destination hashes (truncated SHA-256), NOT traditional addresses
- **Key Innovation:** Destinations are cryptographically bound to public keys - no address coordination needed
- **Transport:** Fully medium-agnostic. Supports:
  - LoRa radio (RNode)
  - Packet radio
  - Serial lines
  - WiFi/Ethernet (AutoInterface for zero-config LAN)
  - TCP/UDP over Internet
  - I2P tunnels
  - Any medium that can carry a data stream
- **Minimum bandwidth:** Functions at 5 bits per second
- **Node Types:**
  - **Instance:** Standard endpoint (phones, glasses, laptops)
  - **Transport Node:** Forwards packets, maintains path tables, serves as distributed keystore
- **Routing:** Automatic topology discovery and convergence. No manual routing tables.
- **Config Location:** ~/.reticulum/config

### How Voice/Audio Works Over Reticulum
- **LXST Protocol** (see dedicated section below) - THE answer for voice
- **Links:** Reticulum "Link" destinations create persistent encrypted channels ideal for streaming
- **Link properties:** Forward secrecy, initiator anonymity, reliability layer, efficient for sustained data flow
- **Codec2 integration:** Already built into LXST at 700-3200bps for LoRa-grade links
- **OPUS integration:** Built into LXST at 4.5-96kbps for higher bandwidth links

### Discovery & Peer Management
- **Announces:** Nodes broadcast their destination hash + public key to the network
- **Zero-configuration:** AutoInterface discovers peers on local broadcast domains automatically
- **Path resolution:** Transport nodes cache and serve path information
- **Bootstrap connectivity:** Can use temporary connections to discover local infrastructure, then disconnect
- **Interface discovery:** Automatic discovery of new peering opportunities
- **No central directory:** Distributed cryptographic keystore across transport nodes

### Encryption & Security Model
- **Default encryption:** Elliptic curve crypto (Curve25519) + AES
- **Per-packet keys:** Every packet encrypted with derived ephemeral key
- **Links:** ECDH key exchange provides Forward Secrecy
- **Ratcheting:** Optional per-destination key ratcheting for forward secrecy without links
- **Initiator anonymity:** Packets don't include source addresses
- **IFAC:** Interface Access Codes for creating private networks on shared mediums
- **Unforgeable delivery proofs:** Signed with destination's identity key

### Latency Characteristics
- **Over WiFi/Ethernet:** Sub-millisecond for local network
- **Over LoRa:** Depends on spreading factor, but LXST claims <10ms end-to-end latency
- **Multi-hop:** Each hop adds latency proportional to medium speed
- **Link establishment:** Initial handshake takes longer, but sustained streaming is low-latency

### Hardware Requirements
- **Minimum:** Any device running Python 3 (Raspberry Pi, laptop, phone via Termux)
- **Radio:** RNode (open source LoRa transceiver) - ~$30-50
- **Reference setup:** Raspberry Pi + RNode for dedicated transport node
- **AR glasses integration:** Python runs on any companion device; BLE/USB/WiFi to glasses

### Relevance for AR Glasses Walkie-Talkie
- **PERFECT FIT.** Reticulum is the transport layer, LXST is the voice protocol.
- User already runs mesh-vision with LXMF - can add LXST voice alongside existing setup
- Same Reticulum instance handles both messaging (LXMF) and voice (LXST)
- Can start with WiFi (already working), add LoRa later without code changes
- rnphone utility provides hardware telephone daemon - model for glasses integration

---

## 2. LXST - Real-Time Streaming Protocol (CRITICAL FOR VOICE)

### Architecture & Transport Layer
- **Built ON TOP of Reticulum** - inherits all transport capabilities
- **Purpose:** Real-time streaming format and delivery protocol
- **Status:** Early alpha but functional (Sideband and rnphone use it)
- **License:** CC BY-NC-ND 4.0 (important - non-commercial during alpha)

### Voice/Audio Capabilities (THIS IS THE KEY)
- **End-to-end latency:** Claims <10ms possible
- **Codec support:**
  - **Codec2:** 700bps to 3200bps - intelligible voice over LoRa!
  - **OPUS:** Multiple profiles from ~4.5kbps to ~96kbps
    - Low-bandwidth voice
    - Medium quality voice
    - High quality perceptually lossless voice
    - Media/podcast quality
    - Perceptually lossless stereo music
  - **Raw/lossless:** Up to 32 channels, 128-bit sample precision
- **Dynamic codec switching:** Can change codecs mid-stream without re-init or frame loss
- **In-band signalling:** Call signalling, metadata, stream management built in
- **Signal pipeline:** Fully staged, allows arbitrary stream routing
- **Signal mixing:** Built-in mixing for any number of channels

### Key Applications Using LXST
- **Sideband:** Full LXST client - voice calls, voice messaging
- **rnphone:** Command-line telephone utility/daemon
  - Supports GPIO keypads and LCD displays
  - Model for building hardware phones
  - Runs on Raspberry Pi
- **LXST Phone:** Cross-platform desktop voice call app
  - SAS verification, peer blocking, rate limiting
  - Encrypted call history, contact management
- **MeshChatX:** Fork of MeshChat with full LXST support, voicemail, phonebook

### What This Means for AR Glasses
- LXST is literally a walkie-talkie protocol for mesh networks
- Codec2 at 1200-3200bps would work over LoRa for emergency/basic voice
- OPUS at 8-16kbps would give good voice quality over WiFi mesh
- Dynamic codec switching lets quality adapt to available bandwidth
- rnphone daemon is the template - adapt for glasses hardware

---

## 3. MESHCHAT (Reticulum Ecosystem)

### Architecture
- **Python backend** (meshchat.py) runs Reticulum instance + WebSocket server
- **Web frontend** (Vue.js) connects via WebSocket
- **Electron wrapper** for desktop app
- **Flow:** Web Browser → WebSocket → Python Reticulum → configured interfaces → destination
- **Storage:** SQLite for messages and data

### Voice/Audio (Beta)
- Audio calls use **Codec2** for low-bandwidth LoRa links
- Uses Web Audio API (AudioWorklet) in browser
- Tested: two-way audio over LoRa single hop - "works well" with reasonable bitrate
- Requires localhost or HTTPS for microphone access (AudioWorklet secure context)
- Chromium-based browser recommended

### Key Code Patterns
- meshchat.py - main entry point, Reticulum + WebSocket server
- LXMF for messaging, LXST for audio
- Identity management via Reticulum Identity files
- Announce mechanism for peer discovery
- Propagation nodes for store-and-forward messaging

### Relevance for Glasses
- Proves voice-over-LoRa works in practice with Reticulum
- WebSocket architecture could work for glasses companion app
- Shows practical codec2 integration pattern

---

## 4. NOMADNET (Reticulum Ecosystem)

### Architecture
- **Terminal-based** encrypted communication suite
- Built on **LXMF** (messaging) and **Reticulum** (transport)
- Features: encrypted messaging, file sharing, text browser, page server
- **Propagation nodes:** Distributed encrypted message store for offline users
- Runs over 300bps radio links successfully

### Key Patterns
- Zero-configuration mesh communication model
- Dynamic page rendering (PHP, Python, bash on server-side)
- Node-side content hosting over mesh
- pip installable: `pip install nomadnet`

### Relevance
- Proves Reticulum works at extreme low bandwidth (300bps)
- Model for hosting services/content on mesh nodes
- Could host AR glasses configuration pages on mesh

---

## 5. MESHTASTIC (Alternative Stack)

### Architecture & Transport Layer
- **Firmware-level** LoRa mesh networking
- **Hardware platforms:** ESP32, nRF52, RP2040/RP2350, Linux
- **Protocol:** Custom 4-layer stack
  - Layer 0: LoRa radio (preamble 16, sync word 0x2B)
  - Layer 1: Unreliable zero-hop (raw LoRa packets)
  - Layer 2: Reliable zero-hop (ACK/NAK with 3 retries)
  - Layer 3: Multi-hop (managed flooding + next-hop routing since v2.6)
- **Packet format:** 16-byte header + max 237 bytes payload
- **Serialization:** Protocol Buffers (protobuf)
- **Channel access:** CSMA/CA (like WiFi) with SNR-based priority

### Routing Algorithm
- **Broadcasts:** Managed flooding - nodes rebroadcast but listen first to avoid duplicates
- **Direct messages (v2.6+):** Next-hop routing learned from successful deliveries
- **SNR-based priority:** Farther nodes (lower SNR) rebroadcast first for maximum range
- **Hop limit:** 3 bits = max 7 hops
- **Scaling:** Auto-scales intervals for meshes >40 nodes

### Encryption
- **Channel encryption:** AES256-CTR per channel (shared key)
- **Direct messages (v2.5+):** PKC with per-node public/private key pairs
- **Weaknesses:**
  - No Perfect Forward Secrecy for channel messages
  - No message integrity verification for channels
  - No authentication for channel messages
  - Node IDs are MAC-based (spoofable)
- **Quantum resistance:** AES256 is quantum-resistant but PKC DM key exchange is NOT

### Voice/Audio Potential
- **NOT designed for voice** - text messaging and telemetry focused
- Max 237 bytes payload per packet
- LoRa data rates typically 0.3-37.5 kbps depending on settings
- Even at highest data rates, latency too high for real-time voice
- Would need significant custom work to add voice

### Hardware
- ESP32-based boards ($15-30): Heltec, TTGO, RAK WisBlock
- nRF52 boards: RAK WisBlock Core
- Record range: 331km
- Build system: PlatformIO
- Custom hardware: Create variant in /variants/ folder

### Relevance for AR Glasses
- **NOT recommended as primary voice transport** - wrong tool for real-time audio
- **Useful as backup/fallback** for text messaging when voice impossible
- Massive community and hardware ecosystem
- Could complement Reticulum (use Meshtastic for text alerts, Reticulum+LXST for voice)
- Hardware (ESP32+LoRa boards) could potentially run both Meshtastic AND Reticulum

---

## 6. BITCHAT (BLE Mesh + Nostr)

### Architecture & Transport Layer
- **Dual transport:** BLE mesh (offline) + Nostr protocol (internet)
- **Platform:** iOS/macOS native (Swift/SwiftUI)
- **Four-layer protocol stack:**
  1. Application Layer (BitchatMessage, DeliveryAck)
  2. Session Layer (BitchatPacket - routing, TTL, fragmentation)
  3. Encryption Layer (Noise Protocol Framework)
  4. Transport Layer (BLE, Wi-Fi Direct, etc.)

### BLE Mesh Details
- Multi-hop relay: max 7 hops
- No internet required
- Automatic peer discovery
- Adaptive power/battery optimization
- Binary protocol optimized for BLE constraints

### Nostr Protocol Details
- Location-based channels via geohash coordinates
- 290+ relay network globally
- NIP-17 gift-wrapped private messages
- Ephemeral keys per geohash area

### Encryption
- **Noise_XX_25519_ChaChaPoly_SHA256**
  - Mutual authentication
  - Forward secrecy
  - Deniability
- Identity: Curve25519 (Noise static) + Ed25519 (signing)
- Fingerprint: SHA256(StaticPublicKey)
- Packet padding to standard block sizes (256/512/1024/2048) for traffic analysis resistance
- Bloom filter for loop prevention in gossip protocol

### Message Routing
- Gossip/flooding with Bloom filter deduplication
- TTL-based hop limiting (8-bit field)
- Private messages: only recipient can decrypt (Noise session keys)
- Broadcast: special recipient ID 0xFFFFFFFFFFFFFFFF
- Fragmentation protocol for messages larger than BLE MTU
- Delivery acknowledgments and read receipts
- Automatic message retry service

### Voice/Audio Potential
- NOT designed for voice - text messaging only
- BLE bandwidth too limited for real-time audio
- Nostr could theoretically carry audio but adds latency
- Interesting privacy model but wrong transport for voice

### Relevance for AR Glasses
- **BLE mesh discovery pattern** is excellent for finding nearby glasses
- **Noise Protocol encryption** model is strong - could adopt similar approach
- **Geohash-based channels** interesting for location-aware features
- **Dual transport concept** (local mesh + internet fallback) is smart architecture
- Could use BitChat's BLE discovery to find peers, then hand off to LXST for voice

---

## 7. MESHCORE / POKEMESH (LoRa Mesh with Mobile Client)

### MeshCore Open - Flutter Client
- **Framework:** Flutter 3.38.5 / Dart 3.10.4
- **BLE Protocol:** Nordic UART Service (NUS) over BLE
  - Service UUID: 6e400001-b5a3-f393-e0a9-e50e24dcca9e
  - RX (write): 6e400002-...
  - TX (notify): 6e400003-...
- **State Management:** Provider pattern with ChangeNotifier
- **Storage:** SQLite local database
- **Encryption:** E2E for private messages via MeshCore protocol
- **Platform support:** Android, iOS, Linux, Windows, macOS, Web
- **Connection types:** BLE, USB, TCP

### MeshCore Device Settings
- Radio Power: 10-30 dBm
- Configurable frequency, bandwidth, spreading factor
- Network ID for mesh identification
- Signal metrics: real-time SNR tracking
- Path visualization and route management

### PokeMesh (Game Over MeshCore)
- Demonstrates MeshCore's capabilities: text-based communication over LoRa
- 138 character message limit (MeshCore constraint)
- 15-second polling intervals
- Shows MeshCore runs over decentralized mesh without internet
- Bot framework for automated MeshCore interaction

### Relevance for AR Glasses
- **Flutter client pattern** useful if building cross-platform companion app
- **Nordic UART Service** BLE protocol is standard - could use same for glasses
- **138 char limit** shows MeshCore's bandwidth constraints - NOT suitable for voice
- Device discovery via BLE advertisement name prefixes
- MeshCore is text/telemetry focused, not voice

---

## 8. OPEN SOURCE MESH PROJECT (WiFi DensePose)

The opensourceprojects.dev link was about WiFi DensePose (using WiFi CSI for human pose estimation), NOT mesh networking. While tangentially interesting for AR (using WiFi for body tracking without cameras), it's not relevant to mesh voice communication.

---

## COMPARATIVE ANALYSIS FOR AR GLASSES WALKIE-TALKIE

### Voice Capability Comparison

| Stack | Voice Support | Min Bandwidth | Latency | Encryption | Best For |
|-------|-------------|---------------|---------|------------|----------|
| Reticulum+LXST | EXCELLENT | 700bps (Codec2) | <10ms claimed | E2E + Forward Secrecy | **PRIMARY CHOICE** |
| Meshtastic | NONE (text only) | N/A | High | AES256-CTR (no PFS) | Text fallback |
| BitChat | NONE (text only) | N/A | N/A | Noise XX (excellent) | BLE discovery model |
| MeshCore | NONE (text only) | N/A | N/A | E2E basic | LoRa text |
| NomadNet | Via LXST | 700bps | <10ms | Same as Reticulum | Terminal comms |

### Recommended Architecture for Phase 2

```
AR Glasses (audio capture/playback)
    │
    ├── BLE/USB/WiFi ──→ Companion Device (phone/Pi)
    │                         │
    │                         ├── Reticulum Instance
    │                         │     ├── LXST (voice streaming)
    │                         │     ├── LXMF (text messaging)
    │                         │     └── Interfaces:
    │                         │           ├── AutoInterface (WiFi/LAN)
    │                         │           ├── RNodeInterface (LoRa)
    │                         │           ├── TCPInterface (Internet)
    │                         │           └── SerialInterface (direct)
    │                         │
    │                         └── Audio Pipeline:
    │                               ├── Mic → OPUS/Codec2 encode → LXST stream
    │                               └── LXST stream → OPUS/Codec2 decode → Speaker
    │
    └── Local Mesh Network
          ├── Other AR glasses users (via their companion devices)
          ├── Transport Nodes (Raspberry Pi + RNode)
          └── Internet gateways (optional)
```

### Implementation Roadmap

**Phase 2a: WiFi Mesh Voice (Immediate)**
- Add LXST to existing mesh-vision Reticulum setup
- Use OPUS codec at 8-16kbps over WiFi
- Test voice quality and latency on existing Mac + Pi + glasses setup
- Use rnphone as reference implementation

**Phase 2b: LoRa Voice (Medium-term)**
- Add RNode LoRa interface to Reticulum config
- Use Codec2 at 1200-3200bps for basic voice over LoRa
- Dynamic codec switching: OPUS when on WiFi, Codec2 when on LoRa
- Test range and reliability

**Phase 2c: Full Mesh (Long-term)**
- Deploy transport nodes for multi-hop coverage
- Enable interface discovery for automatic peering
- Add Meshtastic as text-only fallback channel
- Implement PTT (push-to-talk) with visual indicators on glasses

### Key Code References

| Component | Source | What to Study |
|-----------|--------|---------------|
| LXST voice | github.com/markqvist/LXST | Core streaming protocol, codec integration |
| rnphone | Part of LXST package | Hardware telephone daemon, GPIO integration |
| Sideband | github.com/markqvist/Sideband | Full LXST client, voice calls, Android |
| MeshChat | github.com/liamcottle/reticulum-meshchat | WebSocket pattern, Codec2 over LoRa |
| MeshChatX | git.quad4.io/RNS-Things/MeshChatX | Enhanced LXST support, voicemail |
| LXST Phone | github.com/kc1awv/lxst_phone | Desktop voice app, SAS verification |
| Reticulum | github.com/markqvist/Reticulum | Core networking stack |
| BitChat | github.com/permissionlesstech/bitchat | BLE discovery, Noise crypto model |

### Critical Technical Details for Implementation

**Audio Pipeline (from LXST):**
- LXST handles codec negotiation, streaming, and in-band signalling
- Install: `pip install lxst`
- Dependencies on Pi: python3-pyaudio, codec2
- LXST can dynamically switch codecs mid-stream

**Reticulum Configuration for Voice:**
```ini
# ~/.reticulum/config
[reticulum]
  enable_transport = False  # True only for dedicated transport nodes

[interfaces]
  [[Default Interface]]
    type = AutoInterface
    enabled = yes

  # Add for LoRa:
  [[RNode LoRa Interface]]
    type = RNodeInterface
    port = /dev/ttyUSB0
    frequency = 867200000
    bandwidth = 125000
    spreading_factor = 7
    coding_rate = 5
    txpower = 7
```

**Voice Quality vs Bandwidth Trade-offs:**
- Codec2 700bps: Barely intelligible, emergency only
- Codec2 1200bps: Intelligible but robotic
- Codec2 3200bps: Good quality for voice comms
- OPUS 6kbps: Near-telephone quality
- OPUS 16kbps: Excellent voice quality
- OPUS 32kbps: Broadcast quality
- OPUS 64kbps: Studio quality

**Latency Budget (target <250ms for walkie-talkie feel):**
- Audio capture: ~20ms (frame size)
- Codec encoding: ~5ms
- LXST framing: ~1ms
- Reticulum processing: ~1ms
- Transport (WiFi): ~5ms per hop
- Transport (LoRa): ~50-500ms per hop depending on SF/BW
- Codec decoding: ~5ms
- Audio playback buffer: ~20ms
- **Total WiFi:** ~57ms (excellent for walkie-talkie)
- **Total LoRa single hop:** ~100-550ms (acceptable for walkie-talkie)
- **Total LoRa multi-hop:** May exceed 1s (push-to-talk only)

---

## APPENDIX: Security Model Comparison

| Feature | Reticulum | Meshtastic | BitChat |
|---------|-----------|------------|---------|
| E2E Encryption | Yes (ECDH + AES) | AES256-CTR (channel), PKC (DM) | Noise XX |
| Forward Secrecy | Yes (per-link ECDH) | No (channel), Partial (DM) | Yes |
| Initiator Anonymity | Yes | No | Partial |
| Authentication | Cryptographic (public key) | MAC-based (spoofable) | Mutual (Noise XX) |
| Traffic Analysis Resistance | IFAC | No | Packet padding |
| Quantum Resistance | Under consideration | AES256 yes, PKC no | No |
| Key Management | Automatic, distributed | Shared channel keys | Noise session mgmt |

---

## CONCLUSION

**For the AR glasses walkie-talkie Phase 2, the path is clear:**

1. **Use Reticulum as the networking stack** (already in use for mesh-vision)
2. **Add LXST for real-time voice streaming** (purpose-built for this exact use case)
3. **Start with OPUS over WiFi** (best quality, lowest latency)
4. **Add Codec2 over LoRa** for off-grid/extended range scenarios
5. **Study rnphone daemon** as the implementation template
6. **Borrow BitChat's BLE discovery** pattern for finding nearby glasses users
7. **Keep Meshtastic as optional text-only fallback** for ultra-long-range alerts

The Reticulum+LXST combination is literally designed for exactly what Phase 2 needs:
encrypted, low-latency, mesh-routed voice communication that works over any transport medium.
