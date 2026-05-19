# MeshTalk — Infrastructure-Free AR Glasses Mesh Walkie-Talkie

**Date:** 2025-05-19  
**Status:** Design Spec  
**Hardware:** 2x RayNeo X3 Pro (Android 12, Snapdragon XR2, Mercury OS)  
**Build Host:** Mac Mini → MacBook (vinceroy@100.81.56.107) via SSH  

---

## 1. Overview

MeshTalk is a walkie-talkie app for RayNeo X3 Pro AR glasses that enables voice communication between glasses in physical proximity — no WiFi network, no phone, no server, no internet required. You walk into a park, tap the temple to toggle on, and anyone else wearing MeshTalk glasses on the same channel within ~200ft hears you speak in real-time.

**Core principles:**
- Zero infrastructure — glasses talk directly to each other via WiFi Aware (NAN)
- VOX (voice-activated) — Silero VAD auto-detects speech, no hold-to-talk
- Non-consensual playback — incoming audio plays immediately through bone conduction speakers
- Channel-based — two channels (Alpha, Bravo), swipe to switch
- Always-on — foreground service starts on boot, persists through Mercury OS kills

## 2. Transport Layer — WiFi Aware (NAN)

WiFi Aware (Neighbor Awareness Networking) is an Android API built on the Wi-Fi NAN protocol (IEEE 802.11s-adjacent). It allows devices to discover and communicate directly using their WiFi radios, without associating to any access point.

### Why WiFi Aware (not WiFi Direct, not BLE)

| | WiFi Aware | WiFi Direct | BLE |
|---|---|---|---|
| Requires AP/router | No | No | No |
| User consent dialog | None | Yes (system popup) | None |
| Multi-peer | Yes (pub/sub) | Yes (group) | Yes (mesh) |
| Bandwidth | Full WiFi speed | Full WiFi speed | ~260kbps practical |
| Range | ~200ft outdoors | ~200ft outdoors | ~100ft |
| Coexists with WiFi | Yes (on most chipsets) | Often not | Yes |
| Power-efficient discovery | Yes (firmware offload) | No (active scanning) | Yes |
| API complexity | Medium | Medium | High for audio |
| Android version | 8.0+ | 4.0+ | 5.0+ |

WiFi Aware wins because: no consent dialogs (critical on glasses), coexists with regular WiFi, power-efficient discovery offloaded to firmware, and supports multiple peers natively via publish/subscribe.

**Fallback:** If WiFi Aware is unavailable on Mercury OS (`FEATURE_WIFI_AWARE` not present), fall back to WiFi Direct with auto-connect via pre-shared group credentials.

### Discovery Flow

```
Glass A                                          Glass B
   |                                                |
   |── Publish("meshtalk_alpha", info)             |
   |   ServiceType: PUBLISH_TYPE_UNSOLICITED       |
   |                                                |
   |              Subscribe("meshtalk_alpha") ─────|
   |              ServiceType: SUBSCRIBE_TYPE_PASSIVE|
   |                                                |
   |   <── onServiceDiscovered(peerHandle) ────────|
   |── onServiceDiscovered(peerHandle) ───>        |
   |                                                |
   |── requestNetwork(WifiAwareNetworkSpecifier) ──|
   |                  PSK: "meshtalk_shared_key"    |
   |                                                |
   |   <══════ NAN Data Path (L2 link) ═══════════>|
   |          IPv6 link-local addresses             |
   |          UDP audio streaming                   |
   |                                                |
```

Each glasses both publishes AND subscribes on its current channel name. When a match is found, either side can initiate the NAN data path. The data path gives them direct IPv6 link-local addresses for UDP streaming.

### WiFi Aware API Usage

```kotlin
// Attach to WiFi Aware
val wifiAwareManager = getSystemService(WifiAwareManager::class.java)
wifiAwareManager.attach(object : AttachCallback() {
    override fun onAttached(session: WifiAwareSession) {
        currentSession = session
        publishChannel("meshtalk_alpha")
        subscribeChannel("meshtalk_alpha")
    }
}, handler)

// Publish (advertise presence on channel)
fun publishChannel(channelName: String) {
    val config = PublishConfig.Builder()
        .setServiceName(channelName)
        .setServiceSpecificInfo(deviceId.toByteArray())
        .setPublishType(PublishConfig.PUBLISH_TYPE_UNSOLICITED)
        .build()
    session.publish(config, publishCallback, handler)
}

// Subscribe (discover others on channel)
fun subscribeChannel(channelName: String) {
    val config = SubscribeConfig.Builder()
        .setServiceName(channelName)
        .setSubscribeType(SubscribeConfig.SUBSCRIBE_TYPE_PASSIVE)
        .build()
    session.subscribe(config, subscribeCallback, handler)
}

// On peer discovered → create data path
fun onPeerDiscovered(peerHandle: PeerHandle) {
    val specifier = WifiAwareNetworkSpecifier.Builder(subscribeSession, peerHandle)
        .setPskPassphrase("meshtalk_shared_key")
        .build()
    val request = NetworkRequest.Builder()
        .addTransportType(NetworkCapabilities.TRANSPORT_WIFI_AWARE)
        .setNetworkSpecifier(specifier)
        .build()
    connectivityManager.requestNetwork(request, networkCallback)
}

// Once network available → get peer IPv6 address → start UDP audio
fun onNetworkAvailable(network: Network, peerIpv6: Inet6Address) {
    audioRelay.addPeer(peerIpv6, UDP_PORT)
    audioRelay.startStreaming()
}
```

### Channel-to-Service Mapping

| Channel | WiFi Aware Service Name | Display Name |
|---------|------------------------|--------------|
| 0 | `meshtalk_alpha` | Alpha |
| 1 | `meshtalk_bravo` | Bravo |

Switching channels = unsubscribe/unpublish old service, publish/subscribe new service, drop existing data paths, discover new peers.

### Runtime Feature Detection

```kotlin
fun getBestTransport(): TransportType {
    if (packageManager.hasSystemFeature(PackageManager.FEATURE_WIFI_AWARE)) {
        return TransportType.WIFI_AWARE
    }
    if (packageManager.hasSystemFeature(PackageManager.FEATURE_WIFI_DIRECT)) {
        return TransportType.WIFI_DIRECT
    }
    throw UnsupportedOperationException("No suitable transport available")
}
```

## 3. Audio Pipeline

### Capture Path (Mic → Network)

```
AudioRecord (16kHz, MONO, PCM16, VOICE_RECOGNITION)
  │  160-sample frames (10ms each)
  ▼
Speex AEC (echo cancellation)
  │  Input: mic frame (160 samples)
  │  Reference: current AudioTrack playback (160 samples)
  │  Output: echo-cancelled frame (160 samples)
  │  Filter length: 1600 samples (100ms tail for bone conduction)
  ▼
Accumulate to 512 samples (32ms)
  ▼
Silero VAD (silero_vad_16k_op15.onnx, 1.2MB)
  │  Input: float32[1, 576] (512 samples + 64 context)
  │  Output: speech probability [0.0, 1.0]
  │  Inference: <1ms on Snapdragon XR2
  ▼
VOX State Machine
  │  IDLE ──[prob > 0.45 for 200ms]──→ SPEAKING
  │  SPEAKING ──[prob < 0.30 for 700ms]──→ IDLE
  ▼
When SPEAKING:
  Opus Encode (20ms frames, 16kHz mono, VOIP, 16kbps)
  │  Output: ~40 bytes per 20ms frame
  ▼
UDP Send to all connected peers
  │  Packet: 6-byte header + Opus payload
  │  Total: ~46 bytes per 20ms = ~2.3 KB/s per peer
```

### Playback Path (Network → Speakers)

```
UDP Receive (from any peer)
  ▼
Opus Decode → PCM16 (320 samples per 20ms frame)
  ▼
Multi-peer Mixer (if 2+ peers sending simultaneously)
  │  Sum all decoded frames, clip at ±32767
  ▼
Click Removal Filter (transient detection, threshold 3500)
  │  Removes temple-tap artifacts from incoming audio
  ▼
Volume Boost (15x multiplication, hard clip ±32767)
  ▼
AudioTrack (USAGE_ASSISTANT, bone conduction, LOW_LATENCY mode)
  │  Also: feed PCM to Speex AEC as reference signal
```

### Audio Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Sample rate | 16000 Hz | Voice-optimized, matches Silero VAD |
| Channels | Mono | Sufficient for voice, halves bandwidth |
| Bit depth | 16-bit PCM | Standard, matches AudioRecord |
| AEC frame size | 160 samples (10ms) | Speex default for 16kHz |
| AEC filter length | 1600 samples (100ms) | Short tail — bone conduction echo path is mechanical, not acoustic |
| VAD window | 512 samples (32ms) | Silero requirement (hardcoded) |
| VAD threshold (start) | 0.45 | Slightly below default 0.5 for sensitivity |
| VAD threshold (stop) | 0.30 | Hysteresis prevents rapid toggling |
| VOX speech onset | 200ms | Min continuous speech before transmit starts |
| VOX hangover | 700ms | Keeps TX active during brief pauses |
| Opus frame size | 20ms | Good latency/efficiency balance |
| Opus bitrate | 16 kbps | Voice quality, low bandwidth |
| Opus application | VOIP (2048) | Optimized for speech |

### Latency Budget

| Stage | Duration |
|-------|----------|
| Mic capture (1 AEC frame) | 10ms |
| AEC processing | <1ms |
| VAD accumulation (to 512) | ~22ms (worst case, accumulating from partial) |
| Opus encode | ~2ms |
| UDP transmit (WiFi Aware direct link) | ~2-5ms |
| Opus decode | ~2ms |
| AudioTrack buffer | ~10ms |
| **Total one-way** | **~50-72ms** |

72ms worst case is excellent for walkie-talkie — human perception threshold for "real-time" conversation is ~150ms.

## 4. UDP Protocol

### Packet Format (6-byte header + payload)

```
Byte 0:     Packet type
              0x01 = audio data
              0x02 = control (JSON)
              0x03 = keepalive ping
              0x04 = keepalive pong
Byte 1:     Channel ID (0 = Alpha, 1 = Bravo)
Bytes 2-5:  Sequence number (uint32 big-endian)
Bytes 6+:   Payload
              For 0x01: Opus-encoded audio frame
              For 0x02: UTF-8 JSON control message
              For 0x03/0x04: empty (header only)
```

### Control Messages (type 0x02)

```json
// Announce presence (sent periodically + on channel join)
{"cmd": "announce", "user": "glass_A", "channel": 0, "muted": false}

// Speaking state change (sent on VOX transition)
{"cmd": "speaking", "user": "glass_A", "active": true}

// Mute state change
{"cmd": "mute", "user": "glass_A", "muted": true}

// Channel switch notification
{"cmd": "switch", "user": "glass_A", "from": 0, "to": 1}

// Presence query (to build user count)
{"cmd": "who", "channel": 0}

// Presence response
{"cmd": "here", "user": "glass_B", "channel": 0, "muted": false}
```

### Keepalive

- Send ping (0x03) every 5 seconds to each connected peer
- If no pong (0x04) received within 10 seconds, mark peer as disconnected
- Remove disconnected peer from user count and audio mixing

### Port

- UDP port: **18430** (fixed, both send and receive on this port)
- Each glasses binds to this port and sends to each peer's IPv6 address on the same port

## 5. VOX State Machine

```
          ┌──────────┐
          │   IDLE   │ (not transmitting, VAD running)
          └────┬─────┘
               │ speech_prob > 0.45 continuously for 200ms
               ▼
          ┌──────────┐
     ┌───>│ SPEAKING │ (recording, encoding, sending)
     │    └────┬─────┘
     │         │ speech_prob < 0.30
     │         ▼
     │    ┌──────────┐
     │    │ HANGOVER │ (still sending, waiting 700ms for speech to resume)
     │    └────┬─────┘
     │         │
     │    ┌────┴──── speech_prob > 0.45 before 700ms expires
     │    │         │
     │    │         │ 700ms elapsed with no speech
     │    ▼         ▼
     └────┘    ┌──────────┐
               │   IDLE   │
               └──────────┘

Mute override: When muted=true, VOX stays in IDLE regardless of speech_prob.
Toggle override: When active=false (app toggled off), entire pipeline paused.
```

## 6. Glasses App Architecture

### Package Structure

```
com.meshtalk.app/
├── MeshTalkApplication.kt         — MercurySDK.init(this)
├── MeshTalkActivity.kt            — BaseMirrorActivity, gestures, HUD orchestration
│
├── audio/
│   ├── AudioCaptureEngine.kt      — AudioRecord loop, 160-sample frames, coroutine
│   ├── AudioPlaybackEngine.kt     — AudioTrack, volume boost, LOW_LATENCY
│   ├── OpusCodec.kt               — Opus encode/decode via native library (libopus JNI)
│   ├── SpeexAec.kt                — JNI wrapper for speex_echo_cancellation()
│   ├── VadEngine.kt               — Silero VAD via android-vad library
│   ├── ClickRemovalFilter.kt      — Transient detection, threshold 3500, 32-sample window
│   └── AudioMixer.kt              — Sum multiple decoded streams, clip at ±32767
│
├── mesh/
│   ├── MeshTransport.kt           — Interface: connect, send, onReceive, getPeers
│   ├── WifiAwareTransport.kt      — WiFi Aware implementation (publish/subscribe/data path)
│   ├── WifiDirectTransport.kt     — WiFi Direct fallback implementation
│   ├── PeerManager.kt             — Track connected peers, keepalive, timeout (10s)
│   ├── ChannelManager.kt          — Channel state (Alpha/Bravo), user counts, switching
│   └── PacketCodec.kt             — Encode/decode 6-byte header + payload
│
├── vox/
│   └── VoxStateMachine.kt         — IDLE/SPEAKING/HANGOVER states + transitions
│
├── service/
│   ├── MeshTalkService.kt         — Foreground service, wake lock, lifecycle
│   └── BootReceiver.kt            — BOOT_COMPLETED → start service
│
└── hud/
    ├── HudRenderer.kt             — WebView setup + JS bridge
    └── assets/hud/meshtalk.html   — Single-file HUD (channel, users, status, mute)
```

### Dependencies (build.gradle)

```groovy
// Mercury SDK
implementation files('libs/MercuryAndroidSDK-v0.2.5-release.aar')

// Silero VAD (via android-vad wrapper)
implementation 'com.github.gkonovalov.android-vad:silero:2.0.10'

// OkHttp (for WiFi Direct fallback signaling)
implementation 'com.squareup.okhttp3:okhttp:4.12.0'

// Coroutines
implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'

// Lifecycle
implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.7.0'
implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'
implementation 'androidx.lifecycle:lifecycle-livedata-ktx:2.7.0'

// Gson (JSON control messages)
implementation 'com.google.code.gson:gson:2.10.1'

// Opus (native JNI — bundled in jniLibs/)
// SpeexDSP (native JNI — built via CMake NDK)
```

### Native Libraries (CMake/NDK)

```
app/src/main/
├── jniLibs/arm64-v8a/
│   ├── libopus.so              — Opus codec (prebuilt or compiled from xiph/opus)
│   └── libspeexdsp.so          — SpeexDSP (compiled from xiph/speexdsp)
├── cpp/
│   ├── CMakeLists.txt
│   ├── opus_jni.cpp            — JNI bridge for opus_encode/opus_decode
│   └── speex_aec_jni.cpp       — JNI bridge for speex_echo_cancellation
```

### Manifest

```xml
<manifest>
    <uses-feature android:name="android.hardware.wifi.aware" android:required="false" />
    <uses-feature android:name="android.hardware.wifi.direct" android:required="true" />

    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.NEARBY_WIFI_DEVICES" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <uses-permission android:name="android.permission.VIBRATE" />

    <application android:name=".MeshTalkApplication">
        <meta-data android:name="com.rayneo.mercury.app" android:value="true" />

        <activity
            android:name=".MeshTalkActivity"
            android:exported="true"
            android:screenOrientation="landscape">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".service.MeshTalkService"
            android:exported="false"
            android:foregroundServiceType="mediaPlayback|microphone" />

        <receiver
            android:name=".service.BootReceiver"
            android:exported="true"
            android:enabled="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.LOCKED_BOOT_COMPLETED" />
            </intent-filter>
        </receiver>
    </application>
</manifest>
```

### Temple Gesture Mapping

| Gesture | Action | Implementation |
|---------|--------|----------------|
| Tap (Click) | Toggle walkie-talkie on/off | Join/leave channel, start/stop audio pipeline |
| Swipe Right (SlideContinuous delta < -0.1) | Toggle mute | Set `muted=true/false`, broadcast to peers, VOX ignores speech when muted |
| Swipe Left (SlideContinuous delta > 0.1) | Switch channel | Alpha ↔ Bravo, teardown old peers, discover new peers |
| Double-tap | Exit app | `exitApp()` with full cleanup (stop service, release audio, kill process) |
| Triple-tap | Exit app (backup) | Same as double-tap |

### HUD Layout (640x480 per eye, WebView)

```
┌──────────────────────────────────────┐
│                                      │
│   MESHTALK                           │
│   ══════════════════                 │
│                                      │
│   Channel: ALPHA            2 on     │
│                                      │
│              ◉ LIVE                  │  <- green pulse when VOX active
│                                      │
│          🔇 MUTED                    │  <- red, only when muted
│                                      │
│   ← CH                     MUTE →   │  <- swipe hint, semi-transparent
│                                      │
└──────────────────────────────────────┘
```

- Background: fully transparent (camera/world visible behind)
- Text: white, 18px minimum for readability on 640px wide display
- VOX indicator: green circle that pulses when speech detected, gray when idle
- Mute indicator: red 🔇 icon, only visible when muted
- Channel name: top area, changes on swipe left
- User count: "N on" — number of peers on this channel + self
- Swipe hints: bottom corners, very low opacity, fade after 5 seconds

## 7. Foreground Service & Background Survival

### MeshTalkService

```kotlin
class MeshTalkService : Service() {
    // Foreground service with MEDIA_PLAYBACK + MICROPHONE type
    // Holds partial wake lock
    // Manages: AudioCaptureEngine, AudioPlaybackEngine, MeshTransport
    // Runs the full audio pipeline independently of Activity lifecycle
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification(),
            FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK or FOREGROUND_SERVICE_TYPE_MICROPHONE)
        acquireWakeLock()
        startMeshTransport()
        startAudioPipeline()
        return START_STICKY  // Auto-restart if killed
    }
}
```

### Boot Auto-Start

```kotlin
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        if (intent?.action in listOf(
            Intent.ACTION_BOOT_COMPLETED,
            Intent.ACTION_LOCKED_BOOT_COMPLETED
        )) {
            // Start Activity (not Service directly — Android 12 restriction)
            // Activity immediately starts the foreground service
            val launchIntent = Intent(context, MeshTalkActivity::class.java).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                putExtra("boot_start", true)
            }
            context.startActivity(launchIntent)
        }
    }
}
```

### Mercury OS Background Kill Mitigation

Mercury OS BackgroundAppManager has a hardcoded whitelist of ~40 packages. Non-whitelisted apps get killed 2s after backgrounding. Defense layers:

1. **Foreground service** — keeps app in foreground process state
2. **Persistent notification** — visible indicator that service is running
3. **START_STICKY** — system restarts service after kill
4. **Wake lock** — prevents CPU sleep during audio processing
5. **ADB deployment script** — pre-grants all permissions, sets `mercury_install_allowed`
6. **App stays in foreground** — BaseMirrorActivity is the main UI, user sees it on the display

If Mercury OS still kills the service despite foreground state, the BootReceiver + START_STICKY provide automatic recovery. Worst case: 2-5 second gap before service restarts and reconnects to peers.

## 8. Non-Consensual Auto-Play

When a glasses pair has MeshTalk running (service active), incoming audio plays immediately — no accept dialog, no notification prompt, no user action required.

**Flow:**
1. Service starts (boot or manual app open)
2. Service auto-joins default channel (Alpha)
3. WiFi Aware discovers peers on "meshtalk_alpha"
4. Data path established
5. Any audio received from peers → Opus decode → AudioTrack → bone conduction speakers

**To stop receiving:**
- Open app → tap temple to toggle OFF (leaves channel, stops service)
- Closing the app via double-tap also stops the service

**No opt-in for incoming audio.** If the service is running and you're on a channel, you hear everyone on that channel. This is the walkie-talkie model — you opted in by turning it on.

## 9. Multi-Peer Audio Mixing

When 3+ devices are on the same channel, each device receives audio from multiple peers and mixes locally:

```kotlin
class AudioMixer {
    private val peerBuffers = ConcurrentHashMap<String, ShortArray>()
    
    fun mixFrame(frameSize: Int): ShortArray {
        val mixed = ShortArray(frameSize)
        for ((_, buffer) in peerBuffers) {
            for (i in 0 until frameSize) {
                val sum = mixed[i].toInt() + buffer[i].toInt()
                mixed[i] = sum.coerceIn(Short.MIN_VALUE.toInt(), Short.MAX_VALUE.toInt()).toShort()
            }
        }
        return mixed
    }
}
```

## 10. Channel Switching

```kotlin
fun switchChannel(newChannelId: Int) {
    val oldChannelId = currentChannel
    if (oldChannelId == newChannelId) return
    
    // 1. Stop current audio streams
    audioRelay.stopAll()
    
    // 2. Teardown WiFi Aware sessions for old channel
    meshTransport.leaveChannel(CHANNEL_NAMES[oldChannelId])
    
    // 3. Join new channel
    currentChannel = newChannelId
    meshTransport.joinChannel(CHANNEL_NAMES[newChannelId])
    
    // 4. Update HUD
    hudRenderer.updateChannel(CHANNEL_NAMES[newChannelId], 1) // 1 = just us initially
    
    // 5. Broadcast arrival
    broadcastControl("""{"cmd":"announce","user":"$deviceId","channel":$newChannelId}""")
}

val CHANNEL_NAMES = arrayOf("meshtalk_alpha", "meshtalk_bravo")
val CHANNEL_DISPLAY = arrayOf("Alpha", "Bravo")
```

## 11. User Count Tracking

Each glasses tracks the number of peers on its channel via:

1. **Announce on join:** When joining a channel, broadcast `{"cmd":"announce"}` to all peers
2. **Periodic announce:** Every 15 seconds, re-broadcast announce (handles missed messages)
3. **Who query:** On channel join, send `{"cmd":"who"}` — all peers respond with `{"cmd":"here"}`
4. **Peer timeout:** If no announce/audio/keepalive from a peer for 15 seconds, remove from count
5. **Count = connected peers + 1 (self)**

HUD displays: "N on" where N = user count on current channel.

## 12. Build & Deploy

### Build Pipeline (Mac Mini → MacBook → Glasses)

```bash
# On Mac Mini:
# 1. Package source
cd ~/meshtalk && tar czf /tmp/meshtalk.tar.gz --exclude='.gradle' --exclude='build' --exclude='.git' .

# 2. Send to MacBook
scp /tmp/meshtalk.tar.gz vinceroy@100.81.56.107:/tmp/

# 3. SSH to MacBook, extract, build, deploy to BOTH glasses
ssh vinceroy@100.81.56.107 "bash /tmp/meshtalk_build_deploy.sh"
```

### Deploy Script (meshtalk_build_deploy.sh on MacBook)

```bash
#!/bin/bash
set -e
export JAVA_HOME=/opt/homebrew/opt/openjdk@21
export ANDROID_HOME=/Users/vinceroy/Library/Android/sdk
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH"

cd /tmp && rm -rf meshtalk && mkdir meshtalk && cd meshtalk && tar xzf /tmp/meshtalk.tar.gz
echo "sdk.dir=$ANDROID_HOME" > local.properties

./gradlew assembleDebug

PKG=com.meshtalk.app
APK=app/build/outputs/apk/debug/app-debug.apk

# Deploy to BOTH glasses
for SERIAL in A06B4A8FF4A1633 A06B4A94CC51663; do
    echo "=== Deploying to $SERIAL ==="
    adb -s $SERIAL shell settings put global mercury_install_allowed 1
    adb -s $SERIAL install -r $APK
    adb -s $SERIAL shell pm grant $PKG android.permission.RECORD_AUDIO || true
    adb -s $SERIAL shell pm grant $PKG android.permission.ACCESS_FINE_LOCATION || true
    adb -s $SERIAL shell pm grant $PKG android.permission.NEARBY_WIFI_DEVICES || true
    adb -s $SERIAL shell pm grant $PKG android.permission.CAMERA || true
    adb -s $SERIAL shell svc wifi enable
    sleep 2
    adb -s $SERIAL shell am start -n $PKG/.MeshTalkActivity
done

echo "=== Both glasses deployed and launched ==="
```

### WiFi Enable Requirement

WiFi Aware requires the WiFi radio to be ON (but not connected to any AP). The deploy script enables WiFi on both glasses. The app checks WiFi state on startup and displays a HUD warning if disabled:

```kotlin
val wifiManager = getSystemService(WifiManager::class.java)
if (!wifiManager.isWifiEnabled) {
    // On Android 12, can't programmatically enable WiFi
    // Show HUD message: "Enable WiFi to use MeshTalk"
    // Or use ADB: adb shell svc wifi enable
}
```

## 13. Testing Strategy

### Unit Tests
- VoxStateMachine: state transitions with mocked VAD probabilities
- PacketCodec: encode/decode round-trip
- AudioMixer: clipping behavior, multi-peer mixing
- ChannelManager: join/leave/switch, user count tracking
- PeerManager: keepalive timeout, peer lifecycle

### Integration Tests (on device)
- Two glasses discover each other on same channel (WiFi Aware)
- Audio round-trip: speak on A → plays on B (measure latency)
- Channel switch: A switches to Bravo → A disappears from B's peer count
- Mute: A mutes → A's audio stops reaching B, B still reaches A
- VOX: silence → no packets sent; speech → packets flow
- Kill recovery: force-stop service → verify auto-restart
- Boot start: reboot glasses → verify service starts automatically

### Latency Measurement
- Add timestamps to audio packets (sequence number + send time)
- Log receive time on other glasses
- Report one-way latency in logcat: `adb logcat | grep "MeshTalk latency"`

## 14. Future Extensions (Phase 2+)

These require NO changes to the app architecture — only adding transport implementations:

| Extension | Transport Change | App Change |
|-----------|-----------------|------------|
| LoRa range extension | Add LoRa RNode to a Pi, run rnsd | Add ReticuumTransport.kt implementing MeshTransport |
| BLE fallback | BLE GATT mesh transport | Add BleTransport.kt implementing MeshTransport |
| Phone gateway | Phone runs Reticulum + WiFi Aware relay | None — phone appears as a peer |
| Internet bridge | Reticulum TCP transport to cloud rnsd | Add TcpTransport.kt |
| More channels | Add entries to CHANNEL_NAMES array | None |
| Codec2 for LoRa | Add Codec2 codec alongside Opus | Codec selection based on transport bandwidth |
| Encryption | Replace PSK with per-channel Curve25519 keys | Key exchange in control messages |
| Voice messages | Store Opus frames to file, send as LXMF | Add voicemail feature |

## 15. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| WiFi Aware not available on Mercury OS | Medium | High | WiFi Direct fallback transport ready |
| Mercury OS kills foreground service | Medium | Medium | START_STICKY + BootReceiver + wake lock |
| Bone conduction echo not fully cancelled by Speex | Low | Medium | Tune filter length; try Android built-in AEC as alternative |
| Silero VAD false triggers (wind, ambient noise) | Low | Low | Tune threshold up (0.50-0.60); add min speech duration |
| Opus JNI library crashes on XR2 | Low | High | Use pure Java Opus encoder (Concentus) as fallback |
| WiFi Aware discovery latency > 10s | Medium | Low | Acceptable for walkie-talkie — show "Scanning..." in HUD |
| AudioRecord VOICE_RECOGNITION source silence when glasses off-head | Known | Low | Expected behavior — document as feature, not bug |
