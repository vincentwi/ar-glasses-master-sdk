# Silero VAD + Speex AEC: Comprehensive Android/Kotlin Implementation Guide
## For RayNeo X3 Pro AR Glasses Walkie-Talkie (Android 12, Snapdragon XR2)

---

## PART 1: SILERO VAD — COMPLETE ANALYSIS

### 1.1 Available Models and Files

From the repo (src/silero_vad/data/):

| Model File                    | Size       | Format | Notes |
|-------------------------------|-----------|--------|-------|
| silero_vad.onnx               | 2,327,524 (2.2MB) | ONNX opset 16 | Full model, 8kHz + 16kHz support |
| silero_vad.jit                | 2,272,526 (2.2MB) | PyTorch JIT | Full model, 8kHz + 16kHz support |
| silero_vad_16k_op15.onnx      | 1,289,603 (1.2MB) | ONNX opset 15 | 16kHz ONLY, smaller |
| silero_vad_half.onnx          | 1,280,395 (1.2MB) | ONNX half-precision | Smaller, may be faster |
| silero_vad_op18_ifless.onnx   | 2,845,718 (2.7MB) | ONNX opset 18 | "ifless" variant |
| silero_vad_16k.safetensors    | 1,239,748 (1.2MB) | Safetensors | For tinygrad model |

**RECOMMENDATION FOR ANDROID**: Use `silero_vad_16k_op15.onnx` (1.2MB) — smallest ONNX, 16kHz only 
(which is exactly what we need), opset 15 has widest ONNX Runtime compatibility.

### 1.2 Model Architecture (from tinygrad_model.py)

The model is a lightweight CNN + LSTM architecture:
- STFT convolution (n_fft=256, stride=128, pad=64)
- 4 Conv1d layers: 129→128→64→64→128 (kernel_size=3)
- LSTMCell(128, 128) — carries state between frames
- Final Conv1d(128, 1) → sigmoid → probability [0, 1]

State tensor: shape [2, 1, 128] (h and c states of LSTM)
Context: 64 samples (for 16kHz), prepended to each chunk

### 1.3 ONNX Model Input/Output Specification

**Inputs:**
- `input`: float32[1, 576] — audio chunk (512 samples + 64 context = 576)
- `state`: float32[2, 1, 128] — LSTM state (h, c)  
- `sr`: int64[1] — sample rate (8000 or 16000)

**Outputs:**
- `output`: float32[1, 1] — speech probability [0.0, 1.0]
- `stateN`: float32[2, 1, 128] — updated LSTM state

### 1.4 Audio Requirements

| Parameter | 16kHz | 8kHz |
|-----------|-------|------|
| Sample Rate | 16000 Hz | 8000 Hz |
| Window Size (samples) | 512 | 256 |
| Window Duration | 32 ms | 32 ms |
| Context Size (samples) | 64 | 32 |
| Effective Input Size | 576 | 288 |
| Format | 16-bit Mono PCM (converted to float32 [-1, 1]) | Same |

**CRITICAL**: The model ONLY accepts 512-sample chunks at 16kHz (or 256 at 8kHz). 
This is hardcoded. You cannot feed arbitrary sizes.

### 1.5 Running on Android — THREE Options

#### Option A: android-vad Library (RECOMMENDED — Easiest)

The `gkonovalov/android-vad` library wraps Silero VAD for Android using ONNX Runtime Mobile.

**Gradle setup:**
```groovy
// settings.gradle or root build.gradle
repositories {
    maven { url 'https://jitpack.io' }
}

// app/build.gradle
dependencies {
    implementation 'com.github.gkonovalov.android-vad:silero:2.0.10'
}
```

**Kotlin usage:**
```kotlin
val vad = VadSilero(
    context,  // Android Context for loading model from assets
    sampleRate = SampleRate.SAMPLE_RATE_16K,
    frameSize = FrameSize.FRAME_SIZE_512,
    mode = Mode.NORMAL,         // threshold ~0.5
    silenceDurationMs = 300,    // min silence to trigger end
    speechDurationMs = 50       // min speech to trigger start
)

// In audio processing loop:
val isSpeech: Boolean = vad.isSpeech(audioDataByteArray)

// When done:
vad.close()
```

**Valid frame sizes for Silero in android-vad:**
- 8kHz: 256, 512, 768
- 16kHz: 512, 1024, 1536

**Mode thresholds:**
- OFF: 0.0
- NORMAL: ~0.5 (recommended default)
- AGGRESSIVE: ~0.7
- VERY_AGGRESSIVE: ~0.9

**Minimum API**: Android API 24

#### Option B: Direct ONNX Runtime Integration

If you need more control (e.g., raw probability values instead of boolean):

```groovy
dependencies {
    implementation 'com.microsoft.onnxruntime:onnxruntime-android:1.17.0'
}
```

Place `silero_vad_16k_op15.onnx` in `assets/` folder.

```kotlin
class SileroVadOnnx(context: Context) {
    private val session: OrtSession
    private var state = Array(2) { Array(1) { FloatArray(128) } }
    private var context64 = FloatArray(64) // context buffer

    init {
        val env = OrtEnvironment.getEnvironment()
        val opts = OrtSession.SessionOptions().apply {
            setInterOpNumThreads(1)
            setIntraOpNumThreads(1)
            addCPU(true)
        }
        val modelBytes = context.assets.open("silero_vad_16k_op15.onnx").readBytes()
        session = env.createSession(modelBytes, opts)
    }

    fun resetStates() {
        state = Array(2) { Array(1) { FloatArray(128) } }
        context64 = FloatArray(64)
    }

    /**
     * Process 512 samples of 16kHz audio, return speech probability [0, 1]
     */
    fun call(audioChunk: FloatArray): Float {
        require(audioChunk.size == 512) { "Must be 512 samples" }
        
        // Prepend context (64 samples) to audio chunk (512 samples) = 576 total
        val inputData = FloatArray(576)
        System.arraycopy(context64, 0, inputData, 0, 64)
        System.arraycopy(audioChunk, 0, inputData, 64, 512)
        
        val env = OrtEnvironment.getEnvironment()
        val inputTensor = OnnxTensor.createTensor(env, arrayOf(inputData))
        val stateTensor = OnnxTensor.createTensor(env, state)
        val srTensor = OnnxTensor.createTensor(env, longArrayOf(16000))
        
        val inputs = mapOf(
            "input" to inputTensor,
            "state" to stateTensor,
            "sr" to srTensor
        )
        
        val results = session.run(inputs)
        val output = (results[0].value as Array<FloatArray>)[0][0]
        state = results[1].value as Array<Array<FloatArray>>
        
        // Update context: last 64 samples of the 576-sample input
        System.arraycopy(inputData, 512, context64, 0, 64)
        
        inputTensor.close()
        stateTensor.close()
        srTensor.close()
        results.close()
        
        return output  // speech probability 0.0 - 1.0
    }
}
```

#### Option C: JNI with C++ ONNX Runtime

For lowest latency, use the C++ ONNX Runtime directly via JNI. The repo's 
examples/cpp/silero-vad-onnx.cpp provides a complete reference implementation.
This adds complexity but eliminates Java/Kotlin overhead.

### 1.6 Performance

- **Inference time**: <1ms per 32ms chunk on a single CPU thread
- **ONNX can be 4-5x faster** than PyTorch JIT in some conditions
- **Model load time**: ~50-100ms
- With NNAPI acceleration on Snapdragon XR2: even faster (but unnecessary given <1ms)

### 1.7 VADIterator — Streaming Speech Detection Logic

The Python `VADIterator` class is the KEY reference for VOX-mode implementation.
Here's how it works, translated to our use case:

```
State variables:
  - triggered: bool = false       // currently detecting speech?
  - temp_end: int = 0             // candidate end position
  - current_sample: int = 0       // running sample counter
  - threshold: float = 0.5        // speech start threshold
  - neg_threshold: float = 0.35   // speech end threshold (threshold - 0.15)
  - min_silence_samples: int      // min silence to confirm end (100ms = 1600 samples)
  - speech_pad_samples: int       // padding for start/end (30ms = 480 samples)

For each 512-sample chunk:
  1. Get speech_prob from model
  2. If speech_prob >= threshold AND we have a temp_end: cancel the temp_end
  3. If speech_prob >= threshold AND NOT triggered:
     → triggered = true
     → Emit START event (sample position - speech_pad_samples)
  4. If speech_prob < neg_threshold AND triggered:
     → Set temp_end if not set
     → If (current_sample - temp_end) >= min_silence_samples:
       → Emit END event (temp_end + speech_pad_samples)
       → triggered = false, temp_end = 0
```

**CRITICAL INSIGHT**: The neg_threshold is `threshold - 0.15`. This hysteresis 
prevents rapid start/stop oscillation. Speech starts at 0.5, but only ends 
when it drops below 0.35. This is PERFECT for walkie-talkie VOX.

### 1.8 Threshold Tuning for Walkie-Talkie

| Parameter | Default | Recommended for VOX |
|-----------|---------|---------------------|
| threshold | 0.5 | 0.4-0.5 (lower = more sensitive) |
| neg_threshold | threshold - 0.15 | 0.25-0.35 (auto-calculated) |
| min_silence_duration_ms | 100 | 500-800ms (walkie-talkie needs hangover) |
| speech_pad_ms | 30 | 100-200ms (avoid clipping start of speech) |
| min_speech_duration_ms | 250 | 200-300ms (avoid false triggers on clicks) |

**For VOX walkie-talkie specifically:**
- Set `min_silence_duration_ms = 700` — keeps transmitting during natural pauses
- Set `speech_pad_ms = 150` — don't clip the beginning/end of utterances
- Set `threshold = 0.45` — slightly more sensitive than default
- The hysteresis (0.15 gap) handles the speech→silence transition naturally

### 1.9 Integration with AudioRecord

```kotlin
// AudioRecord setup
val sampleRate = 16000
val channelConfig = AudioFormat.CHANNEL_IN_MONO
val audioFormat = AudioFormat.ENCODING_PCM_16BIT
val bufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)

val audioRecord = AudioRecord(
    MediaRecorder.AudioSource.VOICE_RECOGNITION, // Best for speech
    sampleRate,
    channelConfig,
    audioFormat,
    maxOf(bufferSize, 1024 * 2) // Ensure buffer is large enough
)

// Processing loop (on a background thread)
val chunkSizeBytes = 512 * 2  // 512 samples * 2 bytes per sample (PCM16)
val buffer = ShortArray(512)

audioRecord.startRecording()

while (isRecording) {
    val read = audioRecord.read(buffer, 0, 512)
    if (read == 512) {
        // Convert Short PCM16 to Float [-1, 1]
        val floatBuffer = FloatArray(512) { buffer[it] / 32767.0f }
        
        // Get speech probability
        val prob = vadModel.call(floatBuffer)
        
        // Apply VOX logic (see VADIterator pattern above)
        processVadResult(prob)
    }
}
```

**Key timing: at 16kHz, 512 samples = 32ms. So you get ~31 VAD decisions per second.**

### 1.10 Speech→Silence Transition (Hangover/Padding)

The model outputs per-frame probabilities. The transition logic:

1. **Speech START**: First frame where prob >= threshold
   - Pad backward by speech_pad_ms (include audio before detection)
   
2. **Speech CONTINUE**: As long as prob stays above neg_threshold
   - Even if prob briefly dips between threshold and neg_threshold, speech continues
   
3. **Tentative END**: When prob drops below neg_threshold
   - Start a timer (temp_end)
   - If speech resumes within min_silence_duration_ms → cancel the tentative end
   
4. **Confirmed END**: If silence persists for min_silence_duration_ms
   - End speech segment, pad forward by speech_pad_ms

**This means with 700ms min_silence_duration: speech continues through pauses up to 700ms.**

### 1.11 Fine-Tuning

The repo includes a tuning module (tuning/tune.py) that allows fine-tuning the model
on custom data using a .feather dataframe with audio_path and speech_ts columns.
This could be useful if the default model doesn't work well with bone conduction 
speaker echo or AR glasses microphone characteristics.

---

## PART 2: SPEEX AEC (SpeexDSP) — COMPLETE ANALYSIS

### 2.1 SpeexDSP Echo Cancellation API

From speex_echo.h — the core API:

```c
// Create echo canceller
// frame_size: samples per frame (10-20ms → 160-320 for 16kHz)  
// filter_length: echo tail length in samples (100-500ms → 1600-8000 for 16kHz)
SpeexEchoState *speex_echo_state_init(int frame_size, int filter_length);

// Multi-channel version
SpeexEchoState *speex_echo_state_init_mc(int frame_size, int filter_length, 
                                          int nb_mic, int nb_speakers);

// Main echo cancellation function
// rec: microphone signal (near-end + echo)
// play: speaker signal (reference / far-end)
// out: cleaned signal (near-end with echo removed)
void speex_echo_cancellation(SpeexEchoState *st, 
                              const spx_int16_t *rec,
                              const spx_int16_t *play, 
                              spx_int16_t *out);

// Alternative: separate capture/playback (for async paths)
void speex_echo_playback(SpeexEchoState *st, const spx_int16_t *play);
void speex_echo_capture(SpeexEchoState *st, const spx_int16_t *rec, spx_int16_t *out);

// Reset state
void speex_echo_state_reset(SpeexEchoState *st);

// Destroy
void speex_echo_state_destroy(SpeexEchoState *st);

// Control
int speex_echo_ctl(SpeexEchoState *st, int request, void *ptr);
// SPEEX_ECHO_SET_SAMPLING_RATE = 24
// SPEEX_ECHO_GET_FRAME_SIZE = 3
```

### 2.2 Parameter Selection for Bone Conduction Speakers

**Frame size**: 
- Must be 10-20ms of audio
- At 16kHz: frame_size = 160 (10ms) or 320 (20ms)
- **Recommendation**: 160 samples (10ms) for lowest latency

**Filter length (tail length)**:
- Represents echo path duration (speaker → room → mic)
- Normal speakers: 100-200ms (1600-3200 samples at 16kHz)
- Bone conduction speakers: Echo path is VERY SHORT because sound travels through skull
  - Bone conduction has minimal acoustic path — mostly mechanical coupling
  - **Recommendation**: Start with 100ms (1600 samples), may need only 50ms (800 samples)
  - If too short: residual echo; if too long: slower convergence, more CPU

**Sampling rate**: Set via speex_echo_ctl(st, SPEEX_ECHO_SET_SAMPLING_RATE, &rate)

### 2.3 Android NDK Integration

SpeexDSP is a pure C library. Integration pattern:

#### Step 1: Add SpeexDSP source to your project

```
app/
  src/main/
    cpp/
      speexdsp/           ← Clone from github.com/xiph/speexdsp
        include/speex/
          speex_echo.h
          speex_preprocess.h
          speexdsp_types.h
        libspeexdsp/
          mdf.c            ← Echo cancellation implementation
          preprocess.c     ← Preprocessor (noise suppression)
          fftwrap.c
          filterbank.c
          kiss_fft.c
          kiss_fftr.c
          ...
      speex_jni.cpp        ← Your JNI bridge
    CMakeLists.txt
```

#### Step 2: CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.18)
project(speex_aec)

# SpeexDSP source files
set(SPEEXDSP_SRC
    speexdsp/libspeexdsp/mdf.c
    speexdsp/libspeexdsp/preprocess.c
    speexdsp/libspeexdsp/kiss_fft.c
    speexdsp/libspeexdsp/kiss_fftr.c
    speexdsp/libspeexdsp/fftwrap.c
    speexdsp/libspeexdsp/filterbank.c
    speexdsp/libspeexdsp/buffer.c
    speexdsp/libspeexdsp/jitter.c
    speexdsp/libspeexdsp/resample.c
    speexdsp/libspeexdsp/scal.c
)

add_library(speex_aec SHARED
    speex_jni.cpp
    ${SPEEXDSP_SRC}
)

target_include_directories(speex_aec PRIVATE
    speexdsp/include
    speexdsp/include/speex
)

# Define FLOATING_POINT for better quality (XR2 has FPU)
# Use FIXED_POINT only if targeting very weak hardware
target_compile_definitions(speex_aec PRIVATE
    FLOATING_POINT
    EXPORT=
    HAVE_CONFIG_H=0
)

target_link_libraries(speex_aec
    android
    log
)
```

#### Step 3: build.gradle

```groovy
android {
    defaultConfig {
        externalNativeBuild {
            cmake {
                cppFlags ''
                arguments '-DANDROID_STL=c++_shared'
            }
        }
        ndk {
            abiFilters 'arm64-v8a'  // XR2 is arm64
        }
    }
    externalNativeBuild {
        cmake {
            path 'src/main/cpp/CMakeLists.txt'
        }
    }
}
```

#### Step 4: JNI Bridge (speex_jni.cpp)

```cpp
#include <jni.h>
#include <android/log.h>
#include "speex/speex_echo.h"
#include "speex/speex_preprocess.h"

#define TAG "SpeexAEC"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)

static SpeexEchoState *echo_state = nullptr;
static SpeexPreprocessState *preprocess_state = nullptr;

extern "C" {

JNIEXPORT void JNICALL
Java_com_example_app_SpeexAEC_init(JNIEnv *env, jobject thiz,
                                    jint frame_size, jint filter_length,
                                    jint sample_rate) {
    if (echo_state) {
        speex_echo_state_destroy(echo_state);
    }
    if (preprocess_state) {
        speex_preprocess_state_destroy(preprocess_state);
    }
    
    echo_state = speex_echo_state_init(frame_size, filter_length);
    speex_echo_ctl(echo_state, SPEEX_ECHO_SET_SAMPLING_RATE, &sample_rate);
    
    // Optional: add noise suppression preprocessor
    preprocess_state = speex_preprocess_state_init(frame_size, sample_rate);
    speex_preprocess_ctl(preprocess_state, SPEEX_PREPROCESS_SET_ECHO_STATE, echo_state);
    
    LOGI("Speex AEC initialized: frame=%d, filter=%d, rate=%d", 
         frame_size, filter_length, sample_rate);
}

JNIEXPORT void JNICALL
Java_com_example_app_SpeexAEC_process(JNIEnv *env, jobject thiz,
                                       jshortArray mic_arr,
                                       jshortArray speaker_arr,
                                       jshortArray out_arr) {
    if (!echo_state) return;
    
    jshort *mic = env->GetShortArrayElements(mic_arr, nullptr);
    jshort *speaker = env->GetShortArrayElements(speaker_arr, nullptr);
    jshort *out = env->GetShortArrayElements(out_arr, nullptr);
    
    // Core echo cancellation
    speex_echo_cancellation(echo_state, mic, speaker, out);
    
    // Optional: noise suppression on the output
    if (preprocess_state) {
        speex_preprocess_run(preprocess_state, out);
    }
    
    env->ReleaseShortArrayElements(mic_arr, mic, 0);
    env->ReleaseShortArrayElements(speaker_arr, speaker, 0);
    env->ReleaseShortArrayElements(out_arr, out, 0);
}

JNIEXPORT void JNICALL
Java_com_example_app_SpeexAEC_reset(JNIEnv *env, jobject thiz) {
    if (echo_state) {
        speex_echo_state_reset(echo_state);
    }
}

JNIEXPORT void JNICALL
Java_com_example_app_SpeexAEC_destroy(JNIEnv *env, jobject thiz) {
    if (echo_state) {
        speex_echo_state_destroy(echo_state);
        echo_state = nullptr;
    }
    if (preprocess_state) {
        speex_preprocess_state_destroy(preprocess_state);
        preprocess_state = nullptr;
    }
}

} // extern "C"
```

#### Step 5: Kotlin Wrapper

```kotlin
class SpeexAEC {
    companion object {
        init { System.loadLibrary("speex_aec") }
    }
    
    external fun init(frameSize: Int, filterLength: Int, sampleRate: Int)
    external fun process(mic: ShortArray, speaker: ShortArray, out: ShortArray)
    external fun reset()
    external fun destroy()
}

// Usage:
val aec = SpeexAEC()
// 160 samples/frame (10ms), 1600 filter length (100ms tail), 16kHz
aec.init(160, 1600, 16000)

// In audio loop:
val micFrame = ShortArray(160)    // from AudioRecord
val speakerFrame = ShortArray(160) // what was played to speakers
val cleanFrame = ShortArray(160)   // output

aec.process(micFrame, speakerFrame, cleanFrame)
// cleanFrame now has echo removed
```

### 2.4 Getting the Reference Signal (Speaker/Playback)

This is the HARDEST part of AEC on Android. You need synchronized mic + speaker audio.

**Option A: AudioRecord + AudioTrack with shared buffer**
```kotlin
// When you play received audio through speakers:
audioTrack.write(playbackBuffer, 0, playbackBuffer.size)
// Save the same buffer as the reference signal for AEC
referenceQueue.offer(playbackBuffer.copyOf())

// When processing mic audio:
val micFrame = ... // from AudioRecord
val refFrame = referenceQueue.poll() ?: ShortArray(frameSize) // silent if no ref
aec.process(micFrame, refFrame, cleanFrame)
```

**Option B: speex_echo_playback/capture split**
```c
// When audio is sent to speaker:
speex_echo_playback(echo_state, speaker_data);

// When mic data is captured (internally uses the buffered playback):
speex_echo_capture(echo_state, mic_data, out_data);
```
This adds 2 frames of internal delay but handles the synchronization.

**CRITICAL for bone conduction**: The acoustic path is very short and 
very consistent (skull vibration), so synchronization is less critical 
than with regular speakers. The filter should converge quickly.

### 2.5 Latency Impact

- Speex AEC processing: ~0.1-0.5ms per 10ms frame on Snapdragon XR2
- Adds negligible latency to the audio pipeline
- The 2-frame internal buffer delay (if using playback/capture API) adds ~20ms

### 2.6 Alternatives to Speex AEC

| Solution | Pros | Cons |
|----------|------|------|
| **Android AcousticEchoCanceler** | Built-in, zero setup, hardware-accelerated | Device-dependent, may not work on RayNeo; requires VOICE_COMMUNICATION AudioSource |
| **WebRTC AEC3** | State-of-art, well-tested, Google-maintained | Heavy dependency (entire WebRTC lib), complex build |
| **Speex AEC** | Lightweight, easy to integrate, well-documented | Older algorithm, may struggle with non-linear echo |
| **RNNoise** | ML-based noise suppression | Not AEC — only noise suppression |
| **PJSIP Echo Suppressor** | Supports both Speex and WebRTC backends | Complex framework |

**RECOMMENDATION**: 
1. First try Android's built-in AcousticEchoCanceler (free, no code needed)
2. If it doesn't work on RayNeo, use Speex AEC
3. For bone conduction specifically, echo is mostly linear → Speex handles this well

### 2.7 Testing Android Built-in AEC First

```kotlin
// Check if hardware AEC is available
val isAecAvailable = AcousticEchoCanceler.isAvailable()

// If available, try it:
val audioRecord = AudioRecord(
    MediaRecorder.AudioSource.VOICE_COMMUNICATION, // Required for AEC
    16000,
    AudioFormat.CHANNEL_IN_MONO,
    AudioFormat.ENCODING_PCM_16BIT,
    bufferSize
)

if (isAecAvailable) {
    val aec = AcousticEchoCanceler.create(audioRecord.audioSessionId)
    aec.enabled = true
}
```

**NOTE**: VOICE_COMMUNICATION source enables system AEC, NS, AGC. 
VOICE_RECOGNITION disables them (better for raw audio to process yourself).
You may want VOICE_RECOGNITION if using Speex AEC to avoid double-processing.

---

## PART 3: COMBINED PIPELINE — VAD + AEC for VOX Walkie-Talkie

### 3.1 Signal Flow

```
AudioRecord (16kHz, PCM16, VOICE_RECOGNITION)
         │
         ▼
┌────────────────┐      ┌────────────────┐
│ Reference Queue │◄─────│ AudioTrack     │
│ (speaker data)  │      │ (playback)     │
└───────┬────────┘      └────────────────┘
        │
        ▼
┌────────────────┐
│ Speex AEC      │ ← Process 160-sample frames (10ms)
│ (echo removal) │
└───────┬────────┘
        │
        ▼
┌────────────────────┐
│ Accumulate to 512  │ ← Buffer 3.2 frames of 160 → need 512
│ samples for VAD    │    Actually: process every 512 samples
└───────┬────────────┘
        │
        ▼
┌────────────────┐
│ Silero VAD     │ ← 512-sample chunks (32ms)
│ (ONNX Runtime) │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ VOX Decision   │ ← Start/stop transmission
│ (threshold +   │
│  hangover)     │
└───────┬────────┘
        │
        ▼
    TX on/off
```

### 3.2 Frame Size Alignment

- AEC works on 160-sample frames (10ms)
- VAD works on 512-sample frames (32ms)  
- Solution: Process AEC on 160-sample chunks, accumulate cleaned audio,
  run VAD every 512 samples

```kotlin
val aecFrameSize = 160
val vadFrameSize = 512
val accumulator = ShortArray(vadFrameSize)
var accumulatorPos = 0

fun processAudioChunk(micFrame: ShortArray, refFrame: ShortArray) {
    val cleanFrame = ShortArray(aecFrameSize)
    speexAec.process(micFrame, refFrame, cleanFrame)
    
    System.arraycopy(cleanFrame, 0, accumulator, accumulatorPos, aecFrameSize)
    accumulatorPos += aecFrameSize
    
    if (accumulatorPos >= vadFrameSize) {
        // Convert to float for VAD
        val floatBuf = FloatArray(vadFrameSize) { accumulator[it] / 32767f }
        val speechProb = vadModel.call(floatBuf)
        processVoxDecision(speechProb)
        
        // Shift remaining samples
        val remaining = accumulatorPos - vadFrameSize
        if (remaining > 0) {
            System.arraycopy(accumulator, vadFrameSize, accumulator, 0, remaining)
        }
        accumulatorPos = remaining
    }
}
```

### 3.3 Threading Model

```
Thread 1: AudioRecord → read 160 samples every 10ms
           → Queue to processing thread

Thread 2: Processing loop
           → Dequeue mic frame
           → Get corresponding speaker reference frame
           → Speex AEC process
           → Accumulate for VAD
           → Run VAD every 512 samples
           → Update VOX state
           → If transmitting: send audio to network

Thread 3: AudioTrack playback (received audio)
           → Also copy to reference queue for AEC
```

### 3.4 Complete VOX State Machine

```kotlin
enum class VoxState { IDLE, SPEAKING, HANGOVER }

class VoxController(
    private val startThreshold: Float = 0.45f,
    private val endThreshold: Float = 0.30f,     // startThreshold - 0.15
    private val hangoverMs: Int = 700,            // min silence before stopping TX
    private val minSpeechMs: Int = 200,           // min speech before starting TX
    private val speechPadMs: Int = 150            // pad start/end
) {
    private var state = VoxState.IDLE
    private var speechStartTime = 0L
    private var silenceStartTime = 0L
    private var consecutiveSpeechFrames = 0
    
    fun processFrame(speechProb: Float): Boolean /* isTransmitting */ {
        val now = System.currentTimeMillis()
        
        when (state) {
            VoxState.IDLE -> {
                if (speechProb >= startThreshold) {
                    consecutiveSpeechFrames++
                    if (consecutiveSpeechFrames * 32 >= minSpeechMs) {
                        state = VoxState.SPEAKING
                        speechStartTime = now
                        return true // Start TX
                    }
                } else {
                    consecutiveSpeechFrames = 0
                }
                return false
            }
            VoxState.SPEAKING -> {
                if (speechProb < endThreshold) {
                    state = VoxState.HANGOVER
                    silenceStartTime = now
                }
                return true // Continue TX
            }
            VoxState.HANGOVER -> {
                if (speechProb >= startThreshold) {
                    state = VoxState.SPEAKING // Resume
                    return true
                }
                if (now - silenceStartTime >= hangoverMs) {
                    state = VoxState.IDLE
                    consecutiveSpeechFrames = 0
                    return false // Stop TX
                }
                return true // Still transmitting during hangover
            }
        }
    }
}
```

---

## PART 4: QUICK REFERENCE

### Model File to Use
`silero_vad_16k_op15.onnx` (1.2MB) — place in assets/

### Key Parameters Summary

| Parameter | Value | Why |
|-----------|-------|-----|
| Sample Rate | 16000 Hz | Matches VOICE_RECOGNITION, model supports it |
| VAD Frame Size | 512 samples (32ms) | Required by Silero |
| AEC Frame Size | 160 samples (10ms) | Standard for Speex |
| AEC Filter Length | 1600 samples (100ms) | Bone conduction has short echo path |
| VAD Threshold | 0.45 | Slightly sensitive for walkie-talkie |
| VAD Neg Threshold | 0.30 | Auto: threshold - 0.15 |
| Hangover Duration | 700ms | Covers natural speech pauses |
| Speech Pad | 150ms | Don't clip utterance edges |
| Min Speech Duration | 200ms | Avoid false triggers |

### Gradle Dependencies

```groovy
// Option A: Use android-vad library
implementation 'com.github.gkonovalov.android-vad:silero:2.0.10'

// Option B: Direct ONNX Runtime
implementation 'com.microsoft.onnxruntime:onnxruntime-android:1.17.0'

// Speex: No Gradle dep — compile from source via NDK/CMake
```

### Critical Files from Silero VAD Repo
- `src/silero_vad/utils_vad.py` — OnnxWrapper class, VADIterator, get_speech_timestamps
- `src/silero_vad/model.py` — load_silero_vad() function
- `src/silero_vad/tinygrad_model.py` — Model architecture reference
- `examples/java-example/` — Java ONNX Runtime integration
- `examples/java-wav-file-example/` — File-based VAD with segments
- `examples/cpp/silero-vad-onnx.cpp` — Full C++ ONNX reference
- `examples/c++/silero.h + silero.cc` — C++ with both ONNX and libtorch
- `tuning/` — Fine-tuning scripts if needed
