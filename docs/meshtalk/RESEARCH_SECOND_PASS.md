# Second Pass Research Addendum: Walkie-Talkie Repos + Android Always-On Audio Patterns
## Generated: 2026-05-19

---

# PART 1: Android Always-On Audio Receiver Patterns

## 1.1 Foreground Service Architecture for Always-On Audio

### Core Pattern (from LANwalkieTalkie + Meshenger)

The proven pattern combines THREE mechanisms:

1. **Foreground Service** with `FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK`
2. **Partial WakeLock** to prevent CPU sleep
3. **START_REDELIVER_INTENT** or **START_STICKY** return value

**From LANwalkieTalkie's WalkieService.kt (BEST REFERENCE):**
```kotlin
class WalkieService : Service() {
    private var wakeLock: PowerManager.WakeLock? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        notificationController.createNotificationChanel()
        ServiceCompat.startForeground(
            this,
            NOTIFICATION_ID,
            notificationController.createNotification(),
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            } else { 0 }
        )
        return START_REDELIVER_INTENT  // Redeliver intent if killed
    }

    private fun setWakeLock() {
        wakeLock = (getSystemService(POWER_SERVICE) as PowerManager).run {
            newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "WalkieTalkyApp::ServiceWakelockTag"
            ).apply { acquire(10*60*1000L) }
        }
    }
}
```

### Manifest Requirements (Android 12+):
```xml
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<service
    android:name=".service.WalkieService"
    android:exported="false"
    android:foregroundServiceType="mediaPlayback" />
```

**For Meshenger (which also uses mic + camera):**
```xml
<service
    android:name=".MainService"
    android:exported="false"
    android:foregroundServiceType="mediaPlayback|microphone|camera" />
```

And in code (Android 13+):
```kotlin
startForeground(NOTIFICATION_ID, notification,
    FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK or
    FOREGROUND_SERVICE_TYPE_MICROPHONE or
    FOREGROUND_SERVICE_TYPE_CAMERA)
```

## 1.2 BOOT_COMPLETED Auto-Start Pattern

**From Meshenger's BootUpReceiver.kt (PERFECT REFERENCE):**
```kotlin
class BootUpReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        if (intent?.action == Intent.ACTION_BOOT_COMPLETED) {
            val intent = Intent(context, StartActivity::class.java)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            intent.putExtra(IS_START_ON_BOOTUP, true)
            context.startActivity(intent)
        }
    }

    companion object {
        // Enable/disable receiver programmatically
        fun setEnabled(context: Context, enabled: Boolean) {
            val newState = if (enabled) {
                PackageManager.COMPONENT_ENABLED_STATE_ENABLED
            } else {
                PackageManager.COMPONENT_ENABLED_STATE_DISABLED
            }
            context.packageManager.setComponentEnabledSetting(
                ComponentName(context, BootUpReceiver::class.java),
                newState, PackageManager.DONT_KILL_APP)
        }
    }
}
```

**Manifest entry:**
```xml
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

<receiver
    android:name=".BootUpReceiver"
    android:enabled="false"   <!-- disabled by default, enabled programmatically -->
    android:exported="false">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</receiver>
```

**KEY INSIGHT from Meshenger:** The receiver is disabled by default and enabled
programmatically when user opts in. On boot, it starts an Activity (not
a Service directly) — this avoids Android 12+ background service start
restrictions. The Activity then starts the foreground service.

**Additional boot actions to handle for Chinese OEMs:**
```xml
<action android:name="com.htc.intent.action.QUICKBOOT_POWERON" />
<action android:name="android.intent.action.QUICKBOOT_POWERON" />
```

## 1.3 Surviving Mercury OS BackgroundAppManager Kill

Mercury OS (RayNeo's fork of Android 12) has a `BackgroundAppManager` with
a hardcoded whitelist. Apps NOT on that list get force-stopped.

### Multi-layered defense strategy:

**Layer 1: Request battery optimization exemption**
```xml
<uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" />
```
```kotlin
val pm = getSystemService(POWER_SERVICE) as PowerManager
if (!pm.isIgnoringBatteryOptimizations(packageName)) {
    val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
    intent.data = Uri.parse("package:$packageName")
    startActivity(intent)
}
```

**Layer 2: Use foreground service type mediaPlayback**
This is the STRONGEST signal to Android that your app should not be killed.
Audio apps with active playback are treated as user-facing.

**Layer 3: AccessibilityService (nuclear option)**
An AccessibilityService runs in a separate process and is EXTREMELY hard for
the system to kill. It also auto-restarts. This can be used as a watchdog
that re-launches the main service if killed.

**Layer 4: AlarmManager self-resurrection**
```kotlin
fun scheduleServiceRestart(context: Context) {
    val am = context.getSystemService(ALARM_SERVICE) as AlarmManager
    val intent = Intent(context, ServiceRestartReceiver::class.java)
    val pi = PendingIntent.getBroadcast(context, 0, intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
    am.setExactAndAllowWhileIdle(
        AlarmManager.ELAPSED_REALTIME_WAKEUP,
        SystemClock.elapsedRealtime() + 60000, pi)
}
```

**Layer 5: Use START_STICKY**
```kotlin
override fun onStartCommand(...): Int {
    return START_STICKY  // System will restart service if killed
}
```

**Layer 6: Device Admin (if user consents)**
A DeviceAdminReceiver makes the app much harder for the system to kill.
```kotlin
class WalkieDeviceAdmin : DeviceAdminReceiver() {
    override fun onEnabled(context: Context, intent: Intent) {}
}
```

**Layer 7: For Mercury OS specifically — ADB whitelist injection:**
```bash
adb shell settings put global background_app_manager_whitelist "com.your.app"
```
Or use RayNeo's developer API if available to register as a system-level app.

## 1.4 AudioTrack Playback from Foreground Service

**From LANwalkieTalkie's VoicePlayer.kt (EXACT PATTERN NEEDED):**
```kotlin
class VoicePlayer(private val socketServer: SocketServer) {
    private var audioTrack: AudioTrack? = null

    fun create() {
        val sampleRate = 8000  // or detected min rate
        val minBufferSize = AudioTrack.getMinBufferSize(
            sampleRate, AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT)
        val bufferSize = sampleRate * 2 * 4  // 4 seconds of buffer
        if (bufferSize < minBufferSize) bufferSize = minBufferSize

        audioTrack = AudioTrack(
            AudioManager.STREAM_MUSIC,
            sampleRate,
            AudioFormat.CHANNEL_OUT_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            bufferSize / 4,
            AudioTrack.MODE_STREAM,
            AudioTrack.WRITE_NON_BLOCKING
        )
        audioTrack?.play()  // Start immediately, writes will auto-play

        // Auto-play on receive
        socketServer.dataListener = { bytes -> play(bytes) }
    }

    private fun play(bytes: ByteArray) {
        audioTrack?.write(bytes, 0, bytes.size)  // Non-blocking write
    }
}
```

**KEY INSIGHTS:**
- Uses `STREAM_MUSIC` (not `STREAM_VOICE_CALL`) — plays through speaker
- `MODE_STREAM` + `WRITE_NON_BLOCKING` — writes don't block
- `play()` called BEFORE any data arrives — the AudioTrack sits in PLAYING
  state waiting for data
- Auto-play is just a callback: when data arrives, write to AudioTrack

## 1.5 Wake Lock Patterns for Audio Pipeline

**Combined wake lock strategy:**
```kotlin
// PARTIAL_WAKE_LOCK — keeps CPU running, screen can be off
val wakeLock = (getSystemService(POWER_SERVICE) as PowerManager)
    .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "WalkieTalkie::Audio")
    .apply { acquire() }  // No timeout for always-on

// WIFI_LOCK — keeps WiFi active (needed for receiving audio!)
val wifiLock = (getSystemService(WIFI_SERVICE) as WifiManager)
    .createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, "WalkieTalkie::Wifi")
    .apply { acquire() }
```

**For Meshenger's audio manager:**
Uses `AudioManager.MODE_IN_COMMUNICATION` and requests
`AUDIOFOCUS_GAIN_TRANSIENT` — this tells Android "I'm doing real-time
voice communication, don't interrupt me."

## 1.6 Notification Patterns for Always-On Services

**From LANwalkieTalkie's NotificationController.kt:**
```kotlin
fun createNotification(): Notification {
    return NotificationCompat.Builder(context, CHANNEL_ID)
        .setContentTitle("WalkieTalkie")
        .setSmallIcon(R.mipmap.ic_launcher)
        .setContentIntent(pendingIntent)
        .setOngoing(true)         // Cannot be swiped away
        .setOnlyAlertOnce(true)   // No repeated sounds
        .setAutoCancel(false)     // Cannot be auto-dismissed
        .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
        .setPriority(NotificationCompat.PRIORITY_HIGH)
        .setCategory(NotificationCompat.CATEGORY_REMINDER)
        .setSound(null)           // No sound for the notification itself
        .build()
}

fun createNotificationChanel() {
    val channel = NotificationChannel(
        CHANNEL_ID, CHANEL_NAME,
        NotificationManager.IMPORTANCE_LOW  // Low importance = collapsed
    )
    channel.setSound(null, null)
    channel.setShowBadge(false)
    notificationManager.createNotificationChannel(channel)
}
```

**From Meshenger's notification:**
```kotlin
NotificationCompat.Builder(applicationContext, channelId)
    .setSilent(true)
    .setOngoing(true)
    .setShowWhen(showSinceWhen)
    .setUsesChronometer(showSinceWhen)  // Shows elapsed time
    .setPriority(NotificationCompat.PRIORITY_MIN)
    .setCategory(Notification.CATEGORY_SERVICE)
```

**KEY: For RayNeo glasses, the notification should be MINIMAL:**
- IMPORTANCE_LOW or PRIORITY_MIN
- No sound, no vibration
- Show channel name and user count
- Ongoing (non-dismissible)

---

# PART 2: Second Pass Through Walkie-Talkie Repos

## 2.1 LANwalkieTalkie — Deep Dive

### Architecture (NEW FINDINGS)
This is a multi-module Kotlin project using MVI (Model-View-Intent):
- `app/` — Main app, service management, DI
- `feature-ptt/` — PTT UI and state management
- `service-voice/` — AudioRecord/AudioTrack abstraction
- `serivce-network/` — NSD discovery, socket client/server

### Channel Management (ChanelControllerImpl.kt — KEY FIND)
Uses **Android NSD (Network Service Discovery)** for LAN peer discovery:
- Service type: `_wfwt._tcp` (WiFi Walkie Talkie)
- Service name encodes: `Base64(channelName):deviceId:`
- On discovery, peers connect via TCP sockets
- **Channel is implicit** — all devices on the same NSD service type are
  in the same "channel"
- No explicit channel switching UI (single-channel design)

### Device Tracking (ConnectedDevicesRepository)
- Devices tracked by IP + NSD service name
- `onServiceFound()` adds devices; `onServiceLost()` removes them
- Periodic **ping every 5 seconds** to keep connections alive
- Device count = number of connected socket clients + server clients

### Background Service Pattern
- `WalkieService` uses Koin for DI injection
- Service lifecycle: `onCreate` -> starts NSD discovery + wake lock + VoicePlayer
- `onStartCommand` -> starts foreground with notification
- `onDestroy` -> stops recording, player, discovery, releases wake lock
- **Missing: No BOOT_COMPLETED receiver** (foreground-only app)

### VoicePlayer Auto-Play Pattern
- `socketServer.dataListener = { bytes -> play(bytes) }` — callback-driven
- AudioTrack started in `play()` state immediately on service create
- Data flows: Network -> SocketServer -> dataListener callback -> AudioTrack.write()
- **No mute functionality found** — always plays incoming audio
- Uses SharedFlow to also expose audio data for visualization

### VoiceRecorder
- Uses `MediaRecorder.AudioSource.MIC`
- Records in mono PCM 16-bit
- Reads in 8192-byte chunks in coroutine
- Sends via `chanelController.sendMessage(ByteBuffer)`
- **No VOX/voice detection** — PTT only

## 2.2 esp-walkie-talkie (ESP8266) — Deep Dive

### Full Duplex Always-On Audio
This is the MOST relevant hardware reference — it's an always-on duplex walkie:
- **Simultaneous capture + playback** via interrupt-driven I2S
- 12.5 kHz sample rate, A-law compression
- Runs in interrupt context at 12.5 kHz rate

### Multi-Peer Support (MAX_PEERS = 4)
```c
#define MAX_PEERS 4
static peer_t g_peers[MAX_PEERS];
```
- Tracks peers by IP:port
- Audio output **mixes all active peers**: `dac_val += expanded` for each peer
- Peers timeout after 10 seconds of silence
- Uses UDP broadcast for peer discovery (broadcast every 1 second)

### Echo Cancellation
- Built-in echo cancellation filter using feedback loop
- 12-tap FIR filter estimated from playback history
- Click removal filter for PTT artifacts
- **This is the ONLY repo with echo cancellation**

### Volume Control
- Hardware buttons control volume (GPIO-based)
- Volume range: 1-16, applied as `(dac_val * volume) / 16`
- **Volume up/down via physical buttons** — relevant for glasses touchpad

### Architecture Insights
- No concept of "channels" — single broadcast group
- Always transmitting (full duplex)
- Peer management via UDP keepalive broadcasts
- Audio packets: 8-byte header + 500 bytes of A-law audio data

## 2.3 walkie-talkie (ESP32/Rust-referenced C project) — Deep Dive

### Transport Layer (ESP-NOW based)
- Uses **ESP-NOW** for peer-to-peer communication (no WiFi AP needed)
- Fixed WiFi channel 12
- Broadcast to all peers simultaneously
- `esp_wifi_internal_set_fix_rate(WIFI_PHY_RATE_MCS7_SGI)` — max speed

### Audio Pipeline (Full Duplex)
- Separate I2S ports for mic (I2S_NUM_0) and speaker (I2S_NUM_1)
- 16 kHz, 16-bit mono
- **Stream buffers** connect mic -> network and network -> speaker
- `audio_capture_task` reads from I2S mic, writes to stream buffer
- `audio_playback_task` reads from network stream buffer, writes to I2S speaker
- **Always-on full duplex** — no PTT, no VOX

### Key Pattern for Android Port
```
MIC -> StreamBuffer -> ESP-NOW Send
ESP-NOW Recv -> StreamBuffer -> Speaker
```
This maps to Android as:
```
AudioRecord -> RingBuffer -> WebSocket/UDP Send
WebSocket/UDP Recv -> RingBuffer -> AudioTrack
```

## 2.4 meshenger-android — Deep Dive (GOLD MINE for Android patterns)

### Foreground Service (MainService.kt — COMPLETE PATTERN)
- `START_FOREGROUND_ACTION` / `STOP_FOREGROUND_ACTION` intents
- Creates notification channel with `IMPORTANCE_LOW`
- Runs a `ServerSocket` on port 10001 in background thread
- Accepts incoming connections -> creates RTCPeerConnection
- Uses `LocalBroadcastManager` for internal event communication
- **Binder pattern** for Activity<->Service communication

### Boot Receiver (BootUpReceiver.kt)
- Programmatically enable/disable via `setComponentEnabledSetting()`
- On boot: starts `StartActivity` with `FLAG_ACTIVITY_NEW_TASK`
- Activity checks if database password needed, then starts MainService
- **Best pattern for "start service on boot"**

### Audio Manager (RTCAudioManager.kt — COMPLETE REFERENCE)
Key features we should adopt:
- **Audio focus management**: `AUDIOFOCUS_GAIN_TRANSIENT` for voice calls
- **Audio mode**: `MODE_IN_COMMUNICATION` for VoIP
- **Speaker/earpiece/bluetooth switching** with auto-detection
- **Proximity sensor integration**: near ear -> earpiece, far -> speaker
- **Microphone mute**: `audioManager.isMicrophoneMute = !enabled`
- **Wired headset detection** via `AudioDeviceInfo`
- **Bluetooth manager** for BT headset support

### Call Activity Patterns (CallActivity.kt)
- Uses `WakeLock` for proximity screen control
- Vibrator + Ringtone for incoming calls
- Camera + microphone toggle buttons
- Speakerphone mode toggle
- **Call state machine**: WAITING -> CONNECTING -> RINGING -> CONNECTED -> ENDED

### WebRTC Integration (RTCCall.kt)
- Full WebRTC with data channels for signaling
- Camera enable/disable messages over DataChannel
- Hangup messages over DataChannel
- Microphone mute functionality: `isMicrophoneEnabled` toggle
- **Uses JavaAudioDeviceModule** — could be lighter weight for our use

## 2.5 Zello Android Client SDK — Deep Dive

### Channel/Contact Model (Contacts.java, Contact.java)
**Contact types** (ContactType enum):
- `USER` — individual user
- `CHANNEL` — radio-style channel (one-to-many)
- `GROUP` — group channel
- `GATEWAY` — radio gateway bridge
- `CONVERSATION` — direct conversation

**Per-contact fields:**
- `_usersCount` — online users in channel
- `_usersTotal` — total users in group
- `_muted` — boolean mute flag
- `_noDisconnect` — channel stays connected
- `_status` — online/offline/away

### Channel Operations (Zello.java)
```java
// Connect/disconnect to channels
connectChannel(String channel)
disconnectChannel(String channel)

// Select active contact for messaging
setSelectedContact(Contact contact)
setSelectedUserOrGateway(String name)
setSelectedChannelOrGroup(String name)
selectContact(title, tabs, activeTab, theme)  // Opens contact picker UI

// Messaging
beginMessage()  // Start PTT
endMessage()     // Stop PTT

// Mute
muteContact(Contact contact, boolean mute)

// Auto-connect channels
setAutoConnectChannels(boolean connect)
```

### Audio Mode (Audio.java)
```java
enum AudioMode { SPEAKER, EARPIECE, BLUETOOTH, WEARABLE }
isModeAvailable(AudioMode mode)
setMode(AudioMode mode)
setWearableMode(int wearableIndex)
getWearableCount()
```

### Events System (Events.java)
Key callbacks:
- `onSelectedContactChanged()` — channel switched
- `onMessageStateChanged()` — PTT state change
- `onContactsChanged()` — contact list updated (includes user counts)
- `onAudioStateChanged()` — audio output changed
- `onForegroundServiceStartFailed()` — service couldn't start
- `onBluetoothAccessoryStateChanged()` — BT headset connected/disconnected

### Power Management
```java
enterPowerSavingMode()  // Reduces server communication
leavePowerSavingMode()  // Full updates
```

## 2.6 Zello Channel API (sample-ride) — Deep Dive

### WebSocket-based Channel Communication
**From Zello.kt:**
- Session-based: `Session.Builder(context, server, token, channelName)`
- Voice streams: `IncomingVoiceStream` and `OutgoingVoiceStream`
- Custom audio sources via `VoiceSource` interface
- Channel status updates via `onChannelStatusUpdate()`

### Auto-Play Incoming Audio (ChannelMessage.kt — KEY PATTERN)
```kotlin
class ChannelMessageVoice : ChannelMessage, VoiceReceiver {
    var sampleRate: Int = 0
    val audioBuffers = ArrayList<ShortArray>()

    override fun prepare(stream: IncomingVoiceStream, sampleRate: Int) {
        this.sampleRate = sampleRate
        isRecording = true
    }

    override fun receive(audio: ShortArray, stream: IncomingVoiceStream) {
        if (audio.isNotEmpty()) audioBuffers.add(audio)
    }

    override fun onStreamStopped(stream: IncomingVoiceStream) {
        // Collect all buffers into one array
        audioData = ShortArray(audioBuffers.sumBy { it.size })
        // ... copy buffers
        isRecording = false
    }
}
```

**Pattern: The SDK handles playback internally. The VoiceReceiver just
collects audio data for recording/visualization. But on the receiving end,
audio auto-plays through the channel SDK.**

### Custom Audio Source (for honk/sound effects)
```kotlin
val voiceSource = object: VoiceSource {
    override fun startProvidingAudio(sink: VoiceSink, sampleRate: Int, ...) {
        // Read audio file and push to sink
        sink.provideAudio(samples)
    }
    override fun stopProvidingAudio(sink: VoiceSink) { ... }
}
session.startVoiceMessage(OutgoingVoiceConfiguration(voiceSource, sampleRate))
```

---

# PART 3: Consolidated Pattern Recommendations for RayNeo X3 Pro

## 3.1 Service Architecture
```
WalkieService (foreground, mediaPlayback|microphone)
  ├── AudioPlayer (AudioTrack, always in PLAYING state)
  ├── AudioRecorder (AudioRecord, started on PTT)
  ├── NetworkManager (WebSocket connection)
  ├── ChannelManager (current channel, user list)
  ├── WakeLockManager (PARTIAL_WAKE_LOCK + WIFI_LOCK)
  └── NotificationManager (ongoing, shows channel + users)

BootReceiver (BOOT_COMPLETED -> starts WalkieService)
ServiceWatchdog (AlarmManager, restarts if killed)
```

## 3.2 Auto-Play Architecture
```
Network Receive -> decode -> AudioTrack.write()
  - AudioTrack created in PLAYING state on service start
  - No user action needed to hear incoming audio
  - Mute = audioTrack.setVolume(0f) (keep track playing)
```

## 3.3 Channel Switching (from Zello patterns)
```kotlin
data class Channel(
    val name: String,
    val id: String,
    val usersOnline: Int,
    val usersTotal: Int,
    val isMuted: Boolean
)

interface ChannelManager {
    fun connectChannel(channelId: String)
    fun disconnectChannel(channelId: String)
    fun getCurrentChannel(): Channel
    fun getAvailableChannels(): List<Channel>
    fun muteChannel(channelId: String, mute: Boolean)
    fun onChannelUsersChanged(callback: (Channel) -> Unit)
}
```

## 3.4 Mercury OS Kill Defense Checklist
1. [x] Foreground service with mediaPlayback type
2. [x] Ongoing notification
3. [x] PARTIAL_WAKE_LOCK + WIFI_LOCK
4. [x] START_STICKY return value
5. [x] REQUEST_IGNORE_BATTERY_OPTIMIZATIONS
6. [x] BOOT_COMPLETED receiver (programmatically enabled)
7. [x] AlarmManager watchdog for self-resurrection
8. [ ] ADB whitelist injection (for development)
9. [ ] AccessibilityService watchdog (if all else fails)
10. [ ] Request RayNeo to add to BackgroundAppManager whitelist
