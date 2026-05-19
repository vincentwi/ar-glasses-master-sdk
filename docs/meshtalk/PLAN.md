# MeshTalk Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build MeshTalk, an infrastructure-free walkie-talkie for two RayNeo X3 Pro AR glasses using WiFi Aware (NAN) for direct glasses-to-glasses voice communication with VOX (voice-activated transmission).

**Architecture:** Android app using Mercury SDK (BaseMirrorActivity, temple gestures) with a foreground service running the full audio pipeline. WiFi Aware handles peer discovery and direct data links. Mic → Speex AEC → Silero VAD → Opus encode → UDP → Opus decode → AudioTrack. Two channels (Alpha/Bravo), swipe gestures for channel switch and mute.

**Tech Stack:** Kotlin, Mercury SDK AAR, Silero VAD (android-vad), Opus (libopus JNI), SpeexDSP (JNI), WiFi Aware API, AudioRecord/AudioTrack, WebView HUD.

**Spec:** `docs/meshtalk/DESIGN.md` in ar-glasses-master-sdk repo.

**Hardware:**
- Glasses A: serial `A06B4A8FF4A1633`
- Glasses B: serial `A06B4A94CC51663`
- Build host: MacBook at `vinceroy@100.81.56.107` (JDK 21, Android SDK, ADB)
- Deploy host: Mac Mini (this machine), ADB at `/opt/homebrew/bin/adb`

**Build commands:**
```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@21
export ANDROID_HOME=/Users/vinceroy/Library/Android/sdk
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH"
./gradlew assembleDebug
```

---

## Parallelization Map

```
Task 1: Project Scaffold (SEQUENTIAL — must be first)
    │
    ├─── PARALLEL GROUP A ────────────────────────────┐
    │  Task 2: Native Libs — Opus JNI                  │
    │  Task 3: Native Libs — Speex AEC JNI             │
    │                                                   │
    ├─── PARALLEL GROUP B ────────────────────────────┐│
    │  Task 4: Audio Capture Engine                    ││
    │  Task 5: Audio Playback Engine                   ││
    │  Task 6: VAD Engine (Silero)                     ││
    │  Task 7: VOX State Machine                       ││
    │  Task 8: Click Removal + Audio Mixer             ││
    │                                                   ││
    ├─── PARALLEL GROUP C ────────────────────────────┐││
    │  Task 9: Packet Codec                            │││
    │  Task 10: WiFi Aware Transport                   │││
    │  Task 11: Peer Manager                           │││
    │  Task 12: Channel Manager                        │││
    │                                                   │││
    ├─── PARALLEL GROUP D ────────────────────────────┐│││
    │  Task 13: HUD (WebView HTML)                     ││││
    │                                                   ││││
    └───────────────────────────────────────────────────┘│││
                                                         │││
Task 14: Foreground Service + Boot Receiver (after 1-13) │││
Task 15: Activity Integration (after 1-14)               │││
Task 16: Deploy Scripts + On-Device Testing (after 15)   │││
```

**Tasks 2-13 can ALL run in parallel** after Task 1 completes.
Task 14 depends on transport + audio interfaces being defined (not implemented).
Task 15 wires everything together.
Task 16 deploys to both glasses and validates.

---

## Task 1: Project Scaffold

**Files:**
- Create: `meshtalk/settings.gradle`
- Create: `meshtalk/build.gradle` (project-level)
- Create: `meshtalk/app/build.gradle` (app-level)
- Create: `meshtalk/gradle.properties`
- Create: `meshtalk/gradle/wrapper/gradle-wrapper.properties`
- Create: `meshtalk/app/src/main/AndroidManifest.xml`
- Create: `meshtalk/app/src/main/java/com/meshtalk/app/MeshTalkApplication.kt`
- Create: `meshtalk/app/libs/` (Mercury SDK AAR)

- [ ] **Step 1: Create project directory structure**

```bash
mkdir -p ~/meshtalk/app/src/main/java/com/meshtalk/app/{audio,mesh,vox,service,hud}
mkdir -p ~/meshtalk/app/src/main/assets/hud
mkdir -p ~/meshtalk/app/src/main/cpp
mkdir -p ~/meshtalk/app/src/main/jniLibs/arm64-v8a
mkdir -p ~/meshtalk/app/src/test/java/com/meshtalk/app
mkdir -p ~/meshtalk/app/libs
mkdir -p ~/meshtalk/gradle/wrapper
```

- [ ] **Step 2: Create gradle-wrapper.properties**

Create `meshtalk/gradle/wrapper/gradle-wrapper.properties`:
```properties
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.11.1-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
```

- [ ] **Step 3: Create settings.gradle**

Create `meshtalk/settings.gradle`:
```groovy
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url 'https://jitpack.io' }
    }
}
rootProject.name = "MeshTalk"
include ':app'
```

- [ ] **Step 4: Create project-level build.gradle**

Create `meshtalk/build.gradle`:
```groovy
plugins {
    id 'com.android.application' version '8.7.3' apply false
    id 'org.jetbrains.kotlin.android' version '2.0.21' apply false
}
```

- [ ] **Step 5: Create gradle.properties**

Create `meshtalk/gradle.properties`:
```properties
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true
```

- [ ] **Step 6: Create app/build.gradle**

Create `meshtalk/app/build.gradle`:
```groovy
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.meshtalk.app'
    compileSdk 36

    defaultConfig {
        applicationId "com.meshtalk.app"
        minSdk 26
        targetSdk 36
        versionCode 1
        versionName "1.0"
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
        externalNativeBuild {
            cmake {
                cppFlags "-std=c++17"
                abiFilters "arm64-v8a"
            }
        }
    }

    buildTypes {
        debug {
            debuggable true
        }
        release {
            minifyEnabled false
        }
    }

    buildFeatures {
        viewBinding true
        buildConfig true
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_11
        targetCompatibility JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = '11'
    }

    externalNativeBuild {
        cmake {
            path "src/main/cpp/CMakeLists.txt"
            version "3.22.1"
        }
    }
}

dependencies {
    // Mercury SDK
    implementation fileTree(dir: 'libs', include: ['*.aar'])

    // Silero VAD
    implementation 'com.github.gkonovalov.android-vad:silero:2.0.10'

    // Coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'

    // Lifecycle
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.7.0'
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'
    implementation 'androidx.lifecycle:lifecycle-livedata-ktx:2.7.0'

    // Gson
    implementation 'com.google.code.gson:gson:2.10.1'

    // AndroidX
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'

    // Testing
    testImplementation 'junit:junit:4.13.2'
    testImplementation 'org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3'
}
```

- [ ] **Step 7: Create AndroidManifest.xml**

Create `meshtalk/app/src/main/AndroidManifest.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-feature android:name="android.hardware.wifi.aware" android:required="false" />
    <uses-feature android:name="android.hardware.wifi.direct" android:required="true" />

    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.NEARBY_WIFI_DEVICES" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <uses-permission android:name="android.permission.VIBRATE" />

    <application
        android:name=".MeshTalkApplication"
        android:label="MeshTalk"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Black.NoTitleBar.Fullscreen">

        <meta-data
            android:name="com.rayneo.mercury.app"
            android:value="true" />

        <activity
            android:name=".MeshTalkActivity"
            android:exported="true"
            android:screenOrientation="landscape"
            android:configChanges="orientation|screenSize|keyboardHidden">
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

- [ ] **Step 8: Create MeshTalkApplication.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/MeshTalkApplication.kt`:
```kotlin
package com.meshtalk.app

import android.app.Application
import com.ffalcon.mercury.android.sdk.MercurySDK

class MeshTalkApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        MercurySDK.init(this)
    }
}
```

- [ ] **Step 9: Copy Mercury SDK AAR**

```bash
# On MacBook — copy Mercury AAR to project
scp vinceroy@100.81.56.107:~/Desktop/APP/Glasses/hermes-glasses/app/libs/MercuryAndroidSDK-v0.2.5-release.aar ~/meshtalk/app/libs/
```

- [ ] **Step 10: Copy gradlew from a working project**

```bash
# On MacBook — copy gradle wrapper binary from an existing project
scp vinceroy@100.81.56.107:~/Desktop/APP/Glasses/hermes-glasses/gradlew ~/meshtalk/
scp vinceroy@100.81.56.107:~/Desktop/APP/Glasses/hermes-glasses/gradlew.bat ~/meshtalk/
scp vinceroy@100.81.56.107:~/Desktop/APP/Glasses/hermes-glasses/gradle/wrapper/gradle-wrapper.jar ~/meshtalk/gradle/wrapper/
chmod +x ~/meshtalk/gradlew
```

- [ ] **Step 11: Create stub Activity and verify build**

Create `meshtalk/app/src/main/java/com/meshtalk/app/MeshTalkActivity.kt`:
```kotlin
package com.meshtalk.app

import android.os.Bundle
import android.widget.FrameLayout
import com.ffalcon.mercury.android.sdk.view.BaseMirrorActivity
import com.meshtalk.app.databinding.ActivityMeshtalkBinding

class MeshTalkActivity : BaseMirrorActivity<ActivityMeshtalkBinding>() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
    }
}
```

Create `meshtalk/app/src/main/res/layout/activity_meshtalk.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#000000">

    <WebView
        android:id="@+id/wvHud"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

    <TextView
        android:id="@+id/tvStatus"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="MeshTalk"
        android:textColor="#FFFFFF"
        android:textSize="24sp" />
</FrameLayout>
```

- [ ] **Step 12: Create placeholder CMakeLists.txt for native build**

Create `meshtalk/app/src/main/cpp/CMakeLists.txt`:
```cmake
cmake_minimum_required(VERSION 3.22.1)
project("meshtalk_native")

# Opus JNI bridge
add_library(opus_jni SHARED opus_jni.cpp)
target_link_libraries(opus_jni log)

# Speex AEC JNI bridge
add_library(speex_aec_jni SHARED speex_aec_jni.cpp)
target_link_libraries(speex_aec_jni log)
```

Create empty placeholder files so CMake doesn't fail:
```bash
touch ~/meshtalk/app/src/main/cpp/opus_jni.cpp
touch ~/meshtalk/app/src/main/cpp/speex_aec_jni.cpp
```

- [ ] **Step 13: Verify build compiles**

```bash
cd ~/meshtalk && ./gradlew assembleDebug 2>&1 | tail -5
```

Expected: BUILD SUCCESSFUL

- [ ] **Step 14: Initialize git and commit**

```bash
cd ~/meshtalk
git init
echo -e ".gradle/\nbuild/\nlocal.properties\n*.iml\n.idea/\napp/build/" > .gitignore
git add -A
git commit -m "feat: project scaffold — Mercury SDK, gradle, manifest, stub activity"
```

---

## Task 2: Native Libs — Opus JNI (PARALLEL GROUP A)

**Files:**
- Create: `app/src/main/cpp/opus_jni.cpp`
- Create: `app/src/main/java/com/meshtalk/app/audio/OpusCodec.kt`
- Create: `app/src/test/java/com/meshtalk/app/audio/OpusCodecTest.kt`

**Prereqs:** Task 1 complete. Need libopus.so for arm64-v8a.

- [ ] **Step 1: Download prebuilt libopus for Android arm64-v8a**

```bash
# Build libopus from source for Android or download prebuilt
# Option A: Use prebuilt from Mozilla's libopus-android
cd /tmp
git clone --depth=1 https://github.com/nickarls/opus-android.git
# If no prebuilt available, compile from xiph/opus:
git clone --depth=1 https://github.com/xiph/opus.git /tmp/opus-src
cd /tmp/opus-src
# Cross-compile for arm64-v8a (requires NDK):
export NDK=$ANDROID_HOME/ndk/$(ls $ANDROID_HOME/ndk/ | head -1)
export TOOLCHAIN=$NDK/toolchains/llvm/prebuilt/darwin-x86_64
export TARGET=aarch64-linux-android26
export CC=$TOOLCHAIN/bin/$TARGET-clang
export AR=$TOOLCHAIN/bin/llvm-ar
./autogen.sh
./configure --host=aarch64-linux-android --prefix=/tmp/opus-out \
  CC=$CC AR=$AR --disable-doc --disable-extra-programs
make -j4
make install
cp /tmp/opus-out/lib/libopus.so ~/meshtalk/app/src/main/jniLibs/arm64-v8a/
cp -r /tmp/opus-out/include/opus ~/meshtalk/app/src/main/cpp/
```

- [ ] **Step 2: Write opus_jni.cpp**

Create `meshtalk/app/src/main/cpp/opus_jni.cpp`:
```cpp
#include <jni.h>
#include <android/log.h>
#include "opus/opus.h"
#include <cstring>

#define TAG "OpusJNI"
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

static OpusEncoder* encoder = nullptr;
static OpusDecoder* decoder = nullptr;

extern "C" {

JNIEXPORT jint JNICALL
Java_com_meshtalk_app_audio_OpusCodec_nativeInit(
    JNIEnv* env, jobject, jint sampleRate, jint channels) {
    int err;
    encoder = opus_encoder_create(sampleRate, channels, OPUS_APPLICATION_VOIP, &err);
    if (err != OPUS_OK) { LOGE("Encoder create failed: %d", err); return err; }
    opus_encoder_ctl(encoder, OPUS_SET_BITRATE(16000));
    opus_encoder_ctl(encoder, OPUS_SET_COMPLEXITY(5));
    opus_encoder_ctl(encoder, OPUS_SET_SIGNAL(OPUS_SIGNAL_VOICE));

    decoder = opus_decoder_create(sampleRate, channels, &err);
    if (err != OPUS_OK) { LOGE("Decoder create failed: %d", err); return err; }
    return 0;
}

JNIEXPORT jbyteArray JNICALL
Java_com_meshtalk_app_audio_OpusCodec_nativeEncode(
    JNIEnv* env, jobject, jshortArray pcmData, jint frameSize) {
    if (!encoder) return nullptr;
    jshort* pcm = env->GetShortArrayElements(pcmData, nullptr);
    unsigned char encoded[1024];
    int len = opus_encode(encoder, pcm, frameSize, encoded, sizeof(encoded));
    env->ReleaseShortArrayElements(pcmData, pcm, 0);
    if (len < 0) { LOGE("Encode failed: %d", len); return nullptr; }
    jbyteArray result = env->NewByteArray(len);
    env->SetByteArrayRegion(result, 0, len, (jbyte*)encoded);
    return result;
}

JNIEXPORT jshortArray JNICALL
Java_com_meshtalk_app_audio_OpusCodec_nativeDecode(
    JNIEnv* env, jobject, jbyteArray opusData, jint frameSize) {
    if (!decoder) return nullptr;
    jbyte* data = env->GetByteArrayElements(opusData, nullptr);
    int dataLen = env->GetArrayLength(opusData);
    short decoded[5760]; // max frame size
    int samples = opus_decode(decoder, (unsigned char*)data, dataLen, decoded, frameSize, 0);
    env->ReleaseByteArrayElements(opusData, data, 0);
    if (samples < 0) { LOGE("Decode failed: %d", samples); return nullptr; }
    jshortArray result = env->NewShortArray(samples);
    env->SetShortArrayRegion(result, 0, samples, decoded);
    return result;
}

JNIEXPORT void JNICALL
Java_com_meshtalk_app_audio_OpusCodec_nativeRelease(JNIEnv*, jobject) {
    if (encoder) { opus_encoder_destroy(encoder); encoder = nullptr; }
    if (decoder) { opus_decoder_destroy(decoder); decoder = nullptr; }
}

} // extern "C"
```

- [ ] **Step 3: Update CMakeLists.txt for Opus**

Update `meshtalk/app/src/main/cpp/CMakeLists.txt` to link libopus:
```cmake
cmake_minimum_required(VERSION 3.22.1)
project("meshtalk_native")

# Import prebuilt libopus
add_library(opus SHARED IMPORTED)
set_target_properties(opus PROPERTIES
    IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libopus.so)

# Opus JNI bridge
add_library(opus_jni SHARED opus_jni.cpp)
target_include_directories(opus_jni PRIVATE ${CMAKE_SOURCE_DIR})
target_link_libraries(opus_jni opus log)

# Speex AEC JNI bridge (placeholder)
add_library(speex_aec_jni SHARED speex_aec_jni.cpp)
target_link_libraries(speex_aec_jni log)
```

- [ ] **Step 4: Write OpusCodec.kt Kotlin wrapper**

Create `meshtalk/app/src/main/java/com/meshtalk/app/audio/OpusCodec.kt`:
```kotlin
package com.meshtalk.app.audio

import android.util.Log

class OpusCodec(
    private val sampleRate: Int = 16000,
    private val channels: Int = 1
) {
    companion object {
        private const val TAG = "OpusCodec"
        const val FRAME_SIZE_20MS = 320 // 16000 * 0.020

        init {
            System.loadLibrary("opus_jni")
        }
    }

    private var initialized = false

    fun init(): Boolean {
        val result = nativeInit(sampleRate, channels)
        initialized = result == 0
        if (!initialized) Log.e(TAG, "Init failed with code $result")
        return initialized
    }

    fun encode(pcm: ShortArray, frameSize: Int = FRAME_SIZE_20MS): ByteArray? {
        if (!initialized) return null
        return nativeEncode(pcm, frameSize)
    }

    fun decode(opusData: ByteArray, frameSize: Int = FRAME_SIZE_20MS): ShortArray? {
        if (!initialized) return null
        return nativeDecode(opusData, frameSize)
    }

    fun release() {
        if (initialized) {
            nativeRelease()
            initialized = false
        }
    }

    private external fun nativeInit(sampleRate: Int, channels: Int): Int
    private external fun nativeEncode(pcmData: ShortArray, frameSize: Int): ByteArray?
    private external fun nativeDecode(opusData: ByteArray, frameSize: Int): ShortArray?
    private external fun nativeRelease()
}
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: Opus JNI codec — encode/decode 16kHz mono VOIP"
```

---

## Task 3: Native Libs — Speex AEC JNI (PARALLEL GROUP A)

**Files:**
- Create: `app/src/main/cpp/speex_aec_jni.cpp`
- Create: `app/src/main/java/com/meshtalk/app/audio/SpeexAec.kt`

**Prereqs:** Task 1 complete. Need libspeexdsp.so for arm64-v8a.

- [ ] **Step 1: Build libspeexdsp for Android arm64-v8a**

```bash
cd /tmp
git clone --depth=1 https://github.com/xiph/speexdsp.git
cd speexdsp
export NDK=$ANDROID_HOME/ndk/$(ls $ANDROID_HOME/ndk/ | head -1)
export TOOLCHAIN=$NDK/toolchains/llvm/prebuilt/darwin-x86_64
export TARGET=aarch64-linux-android26
export CC=$TOOLCHAIN/bin/$TARGET-clang
export AR=$TOOLCHAIN/bin/llvm-ar
./autogen.sh
./configure --host=aarch64-linux-android --prefix=/tmp/speexdsp-out \
  CC=$CC AR=$AR --disable-examples
make -j4
make install
cp /tmp/speexdsp-out/lib/libspeexdsp.so ~/meshtalk/app/src/main/jniLibs/arm64-v8a/
cp -r /tmp/speexdsp-out/include/speex ~/meshtalk/app/src/main/cpp/
```

- [ ] **Step 2: Write speex_aec_jni.cpp**

Create `meshtalk/app/src/main/cpp/speex_aec_jni.cpp`:
```cpp
#include <jni.h>
#include <android/log.h>
#include "speex/speex_echo.h"
#include "speex/speex_preprocess.h"

#define TAG "SpeexAecJNI"
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

static SpeexEchoState* echoState = nullptr;
static SpeexPreprocessState* preprocState = nullptr;

extern "C" {

JNIEXPORT jint JNICALL
Java_com_meshtalk_app_audio_SpeexAec_nativeInit(
    JNIEnv*, jobject, jint frameSize, jint filterLength, jint sampleRate) {
    echoState = speex_echo_state_init(frameSize, filterLength);
    if (!echoState) { LOGE("Echo state init failed"); return -1; }
    speex_echo_ctl(echoState, SPEEX_ECHO_SET_SAMPLING_RATE, &sampleRate);

    preprocState = speex_preprocess_state_init(frameSize, sampleRate);
    speex_preprocess_ctl(preprocState, SPEEX_PREPROCESS_SET_ECHO_STATE, echoState);

    int denoise = 1;
    speex_preprocess_ctl(preprocState, SPEEX_PREPROCESS_SET_DENOISE, &denoise);
    int agc = 1;
    speex_preprocess_ctl(preprocState, SPEEX_PREPROCESS_SET_AGC, &agc);
    return 0;
}

JNIEXPORT jshortArray JNICALL
Java_com_meshtalk_app_audio_SpeexAec_nativeProcess(
    JNIEnv* env, jobject, jshortArray micData, jshortArray speakerData) {
    if (!echoState) return micData;
    int frameSize = env->GetArrayLength(micData);
    jshort* mic = env->GetShortArrayElements(micData, nullptr);
    jshort* spk = env->GetShortArrayElements(speakerData, nullptr);
    short* out = new short[frameSize];

    speex_echo_cancellation(echoState, mic, spk, out);
    speex_preprocess_run(preprocState, out);

    env->ReleaseShortArrayElements(micData, mic, 0);
    env->ReleaseShortArrayElements(speakerData, spk, 0);

    jshortArray result = env->NewShortArray(frameSize);
    env->SetShortArrayRegion(result, 0, frameSize, out);
    delete[] out;
    return result;
}

JNIEXPORT void JNICALL
Java_com_meshtalk_app_audio_SpeexAec_nativeRelease(JNIEnv*, jobject) {
    if (preprocState) { speex_preprocess_state_destroy(preprocState); preprocState = nullptr; }
    if (echoState) { speex_echo_state_destroy(echoState); echoState = nullptr; }
}

} // extern "C"
```

- [ ] **Step 3: Update CMakeLists.txt for SpeexDSP**

Update `meshtalk/app/src/main/cpp/CMakeLists.txt`:
```cmake
cmake_minimum_required(VERSION 3.22.1)
project("meshtalk_native")

# Import prebuilt libopus
add_library(opus SHARED IMPORTED)
set_target_properties(opus PROPERTIES
    IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libopus.so)

# Import prebuilt libspeexdsp
add_library(speexdsp SHARED IMPORTED)
set_target_properties(speexdsp PROPERTIES
    IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libspeexdsp.so)

# Opus JNI bridge
add_library(opus_jni SHARED opus_jni.cpp)
target_include_directories(opus_jni PRIVATE ${CMAKE_SOURCE_DIR})
target_link_libraries(opus_jni opus log)

# Speex AEC JNI bridge
add_library(speex_aec_jni SHARED speex_aec_jni.cpp)
target_include_directories(speex_aec_jni PRIVATE ${CMAKE_SOURCE_DIR})
target_link_libraries(speex_aec_jni speexdsp log)
```

- [ ] **Step 4: Write SpeexAec.kt Kotlin wrapper**

Create `meshtalk/app/src/main/java/com/meshtalk/app/audio/SpeexAec.kt`:
```kotlin
package com.meshtalk.app.audio

import android.util.Log

class SpeexAec(
    private val frameSize: Int = 160,       // 10ms at 16kHz
    private val filterLength: Int = 1600,   // 100ms tail for bone conduction
    private val sampleRate: Int = 16000
) {
    companion object {
        private const val TAG = "SpeexAec"
        init {
            System.loadLibrary("speex_aec_jni")
        }
    }

    private var initialized = false

    // Reference buffer: what's currently playing on speakers
    private var referenceBuffer = ShortArray(frameSize)

    fun init(): Boolean {
        val result = nativeInit(frameSize, filterLength, sampleRate)
        initialized = result == 0
        if (!initialized) Log.e(TAG, "Init failed")
        return initialized
    }

    /**
     * Feed speaker reference signal — call this every time AudioTrack plays a frame.
     */
    fun feedReference(speakerPcm: ShortArray) {
        if (speakerPcm.size == frameSize) {
            referenceBuffer = speakerPcm.copyOf()
        }
    }

    /**
     * Process mic frame — cancels echo from speaker reference.
     * Returns echo-cancelled PCM frame.
     */
    fun process(micPcm: ShortArray): ShortArray {
        if (!initialized) return micPcm
        return nativeProcess(micPcm, referenceBuffer) ?: micPcm
    }

    fun release() {
        if (initialized) {
            nativeRelease()
            initialized = false
        }
    }

    private external fun nativeInit(frameSize: Int, filterLength: Int, sampleRate: Int): Int
    private external fun nativeProcess(micData: ShortArray, speakerData: ShortArray): ShortArray?
    private external fun nativeRelease()
}
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: Speex AEC JNI — echo cancellation for bone conduction"
```

---

## Task 4: Audio Capture Engine (PARALLEL GROUP B)

**Files:**
- Create: `app/src/main/java/com/meshtalk/app/audio/AudioCaptureEngine.kt`

- [ ] **Step 1: Write AudioCaptureEngine.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/audio/AudioCaptureEngine.kt`:
```kotlin
package com.meshtalk.app.audio

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow

class AudioCaptureEngine {
    companion object {
        private const val TAG = "AudioCapture"
        const val SAMPLE_RATE = 16000
        const val AEC_FRAME_SIZE = 160  // 10ms for Speex AEC
    }

    private var audioRecord: AudioRecord? = null
    private var captureJob: Job? = null
    private val _audioFrames = MutableSharedFlow<ShortArray>(extraBufferCapacity = 64)
    val audioFrames: SharedFlow<ShortArray> = _audioFrames

    private val captureDispatcher = Dispatchers.Default.limitedParallelism(1)

    fun start() {
        val minBuf = AudioRecord.getMinBufferSize(
            SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        )
        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.VOICE_RECOGNITION,
            SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            minBuf * 2
        ).also {
            if (it.state != AudioRecord.STATE_INITIALIZED) {
                Log.e(TAG, "AudioRecord failed to initialize")
                return
            }
            it.startRecording()
        }

        captureJob = CoroutineScope(captureDispatcher).launch {
            val buffer = ShortArray(AEC_FRAME_SIZE)
            Log.i(TAG, "Capture started: ${SAMPLE_RATE}Hz, frame=$AEC_FRAME_SIZE")
            while (isActive) {
                val read = audioRecord?.read(buffer, 0, AEC_FRAME_SIZE) ?: break
                if (read == AEC_FRAME_SIZE) {
                    _audioFrames.emit(buffer.copyOf())
                }
            }
        }
    }

    fun stop() {
        captureJob?.cancel()
        captureJob = null
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        Log.i(TAG, "Capture stopped")
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: AudioCaptureEngine — 16kHz mono VOICE_RECOGNITION, 10ms frames"
```

---

## Task 5: Audio Playback Engine (PARALLEL GROUP B)

**Files:**
- Create: `app/src/main/java/com/meshtalk/app/audio/AudioPlaybackEngine.kt`

- [ ] **Step 1: Write AudioPlaybackEngine.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/audio/AudioPlaybackEngine.kt`:
```kotlin
package com.meshtalk.app.audio

import android.media.*
import android.util.Log

class AudioPlaybackEngine(
    private val sampleRate: Int = 16000,
    private val volumeBoost: Float = 15f
) {
    companion object {
        private const val TAG = "AudioPlayback"
    }

    private var audioTrack: AudioTrack? = null
    var onFramePlayed: ((ShortArray) -> Unit)? = null  // For AEC reference

    fun start() {
        val minBuf = AudioTrack.getMinBufferSize(
            sampleRate,
            AudioFormat.CHANNEL_OUT_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        )
        audioTrack = AudioTrack.Builder()
            .setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_ASSISTANT)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            .setAudioFormat(
                AudioFormat.Builder()
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                    .setSampleRate(sampleRate)
                    .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                    .build()
            )
            .setBufferSizeInBytes(minBuf * 4)
            .setPerformanceMode(AudioTrack.PERFORMANCE_MODE_LOW_LATENCY)
            .setTransferMode(AudioTrack.MODE_STREAM)
            .build()
            .also { it.play() }
        Log.i(TAG, "Playback started: ${sampleRate}Hz, boost=${volumeBoost}x")
    }

    fun play(pcm: ShortArray) {
        val boosted = applyVolumeBoost(pcm)
        audioTrack?.write(boosted, 0, boosted.size, AudioTrack.WRITE_NON_BLOCKING)
        onFramePlayed?.invoke(boosted)  // Feed to AEC as reference
    }

    private fun applyVolumeBoost(pcm: ShortArray): ShortArray {
        val result = ShortArray(pcm.size)
        for (i in pcm.indices) {
            val sample = (pcm[i].toInt() * volumeBoost).toInt()
            result[i] = sample.coerceIn(Short.MIN_VALUE.toInt(), Short.MAX_VALUE.toInt()).toShort()
        }
        return result
    }

    fun stop() {
        audioTrack?.stop()
        audioTrack?.release()
        audioTrack = null
        Log.i(TAG, "Playback stopped")
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: AudioPlaybackEngine — bone conduction, 15x boost, LOW_LATENCY"
```

---

## Task 6: VAD Engine — Silero (PARALLEL GROUP B)

**Files:**
- Create: `app/src/main/java/com/meshtalk/app/audio/VadEngine.kt`

- [ ] **Step 1: Write VadEngine.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/audio/VadEngine.kt`:
```kotlin
package com.meshtalk.app.audio

import android.content.Context
import android.util.Log
import com.konovalov.vad.silero.VadSilero
import com.konovalov.vad.silero.config.FrameSize
import com.konovalov.vad.silero.config.Mode
import com.konovalov.vad.silero.config.SampleRate
import java.nio.ByteBuffer
import java.nio.ByteOrder

class VadEngine(context: Context) {
    companion object {
        private const val TAG = "VadEngine"
        const val VAD_FRAME_SIZE = 512  // Required by Silero at 16kHz
    }

    private val vad = VadSilero(
        context,
        sampleRate = SampleRate.SAMPLE_RATE_16K,
        frameSize = FrameSize.FRAME_SIZE_512,
        mode = Mode.NORMAL,
        speechDurationMs = 50,
        silenceDurationMs = 300
    )

    // Accumulator: collect 160-sample AEC frames until we have 512 for VAD
    private val accumulator = ShortArray(VAD_FRAME_SIZE)
    private var accumulatedSamples = 0

    /**
     * Feed a 160-sample (10ms) AEC frame. Returns speech probability
     * when enough samples accumulated (512), or null if still accumulating.
     */
    fun feedFrame(aecFrame: ShortArray): Float? {
        val toCopy = minOf(aecFrame.size, VAD_FRAME_SIZE - accumulatedSamples)
        System.arraycopy(aecFrame, 0, accumulator, accumulatedSamples, toCopy)
        accumulatedSamples += toCopy

        if (accumulatedSamples >= VAD_FRAME_SIZE) {
            val isSpeech = vad.isSpeech(shortsToBytes(accumulator))
            accumulatedSamples = 0

            // If we had leftover samples from aecFrame, carry them over
            val leftover = aecFrame.size - toCopy
            if (leftover > 0) {
                System.arraycopy(aecFrame, toCopy, accumulator, 0, leftover)
                accumulatedSamples = leftover
            }

            return if (isSpeech) 1.0f else 0.0f
        }
        return null
    }

    private fun shortsToBytes(shorts: ShortArray): ByteArray {
        val buf = ByteBuffer.allocate(shorts.size * 2).order(ByteOrder.LITTLE_ENDIAN)
        for (s in shorts) buf.putShort(s)
        return buf.array()
    }

    fun release() {
        vad.close()
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: VadEngine — Silero VAD, 512-sample window, accumulates from AEC frames"
```

---

## Task 7: VOX State Machine (PARALLEL GROUP B)

**Files:**
- Create: `app/src/main/java/com/meshtalk/app/vox/VoxStateMachine.kt`
- Create: `app/src/test/java/com/meshtalk/app/vox/VoxStateMachineTest.kt`

- [ ] **Step 1: Write failing test**

Create `meshtalk/app/src/test/java/com/meshtalk/app/vox/VoxStateMachineTest.kt`:
```kotlin
package com.meshtalk.app.vox

import org.junit.Assert.*
import org.junit.Test

class VoxStateMachineTest {
    @Test
    fun startsIdle() {
        val vox = VoxStateMachine()
        assertEquals(VoxState.IDLE, vox.state)
        assertFalse(vox.shouldTransmit)
    }

    @Test
    fun transitionsToSpeakingAfterOnset() {
        val vox = VoxStateMachine(onsetMs = 100, hangoverMs = 500)
        // Feed speech for 150ms (> onset 100ms)
        // At 32ms per VAD frame, need 4-5 frames
        repeat(5) { vox.onVadResult(0.8f, 32) }
        assertEquals(VoxState.SPEAKING, vox.state)
        assertTrue(vox.shouldTransmit)
    }

    @Test
    fun staysIdleDuringBriefSpeech() {
        val vox = VoxStateMachine(onsetMs = 200, hangoverMs = 500)
        // Feed speech for only 64ms (< onset 200ms)
        repeat(2) { vox.onVadResult(0.8f, 32) }
        assertEquals(VoxState.IDLE, vox.state)
        assertFalse(vox.shouldTransmit)
    }

    @Test
    fun transitionsToHangoverOnSilence() {
        val vox = VoxStateMachine(onsetMs = 50, hangoverMs = 500)
        // Enter speaking
        repeat(3) { vox.onVadResult(0.8f, 32) }
        assertEquals(VoxState.SPEAKING, vox.state)
        // One silence frame → hangover
        vox.onVadResult(0.1f, 32)
        assertEquals(VoxState.HANGOVER, vox.state)
        assertTrue(vox.shouldTransmit) // still transmitting during hangover
    }

    @Test
    fun returnsToIdleAfterHangover() {
        val vox = VoxStateMachine(onsetMs = 50, hangoverMs = 100)
        // Enter speaking
        repeat(3) { vox.onVadResult(0.8f, 32) }
        // Silence for > hangover time
        repeat(5) { vox.onVadResult(0.1f, 32) }
        assertEquals(VoxState.IDLE, vox.state)
        assertFalse(vox.shouldTransmit)
    }

    @Test
    fun resumesSpeakingFromHangover() {
        val vox = VoxStateMachine(onsetMs = 50, hangoverMs = 500)
        // Enter speaking
        repeat(3) { vox.onVadResult(0.8f, 32) }
        // Brief silence
        vox.onVadResult(0.1f, 32)
        assertEquals(VoxState.HANGOVER, vox.state)
        // Speech returns
        vox.onVadResult(0.8f, 32)
        assertEquals(VoxState.SPEAKING, vox.state)
    }

    @Test
    fun mutePreventsTransmission() {
        val vox = VoxStateMachine(onsetMs = 50, hangoverMs = 500)
        vox.muted = true
        repeat(10) { vox.onVadResult(0.9f, 32) }
        assertEquals(VoxState.IDLE, vox.state)
        assertFalse(vox.shouldTransmit)
    }
}
```

- [ ] **Step 2: Run test, verify failure**

```bash
cd ~/meshtalk && ./gradlew test 2>&1 | tail -10
```
Expected: FAIL — VoxStateMachine class not found.

- [ ] **Step 3: Implement VoxStateMachine.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/vox/VoxStateMachine.kt`:
```kotlin
package com.meshtalk.app.vox

enum class VoxState { IDLE, SPEAKING, HANGOVER }

class VoxStateMachine(
    private val startThreshold: Float = 0.45f,
    private val stopThreshold: Float = 0.30f,
    private val onsetMs: Int = 200,
    private val hangoverMs: Int = 700
) {
    var state: VoxState = VoxState.IDLE
        private set

    var muted: Boolean = false

    val shouldTransmit: Boolean
        get() = !muted && (state == VoxState.SPEAKING || state == VoxState.HANGOVER)

    private var speechAccumulatorMs: Int = 0
    private var silenceAccumulatorMs: Int = 0

    var onStateChanged: ((VoxState) -> Unit)? = null

    /**
     * Feed VAD result. Called once per VAD window (e.g. every 32ms).
     * @param probability Speech probability [0.0, 1.0]
     * @param frameDurationMs Duration of the VAD window in ms
     */
    fun onVadResult(probability: Float, frameDurationMs: Int) {
        if (muted) {
            if (state != VoxState.IDLE) transition(VoxState.IDLE)
            return
        }

        val isSpeech = probability >= startThreshold
        val isSilence = probability < stopThreshold

        when (state) {
            VoxState.IDLE -> {
                if (isSpeech) {
                    speechAccumulatorMs += frameDurationMs
                    if (speechAccumulatorMs >= onsetMs) {
                        transition(VoxState.SPEAKING)
                        speechAccumulatorMs = 0
                    }
                } else {
                    speechAccumulatorMs = 0
                }
            }
            VoxState.SPEAKING -> {
                if (isSilence) {
                    silenceAccumulatorMs = frameDurationMs
                    transition(VoxState.HANGOVER)
                }
                // If still speaking, stay in SPEAKING
            }
            VoxState.HANGOVER -> {
                if (isSpeech) {
                    silenceAccumulatorMs = 0
                    transition(VoxState.SPEAKING)
                } else {
                    silenceAccumulatorMs += frameDurationMs
                    if (silenceAccumulatorMs >= hangoverMs) {
                        silenceAccumulatorMs = 0
                        transition(VoxState.IDLE)
                    }
                }
            }
        }
    }

    private fun transition(newState: VoxState) {
        if (state != newState) {
            state = newState
            onStateChanged?.invoke(newState)
        }
    }

    fun reset() {
        state = VoxState.IDLE
        speechAccumulatorMs = 0
        silenceAccumulatorMs = 0
    }
}
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
cd ~/meshtalk && ./gradlew test 2>&1 | tail -10
```
Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: VOX state machine — IDLE/SPEAKING/HANGOVER with hysteresis"
```

---

## Task 8: Click Removal + Audio Mixer (PARALLEL GROUP B)

**Files:**
- Create: `app/src/main/java/com/meshtalk/app/audio/ClickRemovalFilter.kt`
- Create: `app/src/main/java/com/meshtalk/app/audio/AudioMixer.kt`

- [ ] **Step 1: Write ClickRemovalFilter.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/audio/ClickRemovalFilter.kt`:
```kotlin
package com.meshtalk.app.audio

/**
 * Detects audio transients (clicks from temple taps) and replaces them
 * with interpolated values. Adapted from esp-walkie-talkie.
 */
class ClickRemovalFilter(
    private val threshold: Int = 3500,
    private val windowSize: Int = 32
) {
    private val history = ShortArray(windowSize)
    private var historyPos = 0

    fun process(frame: ShortArray): ShortArray {
        val result = frame.copyOf()
        for (i in result.indices) {
            val sample = result[i].toInt()
            val avg = history.map { it.toInt() }.sum() / windowSize
            val diff = kotlin.math.abs(sample - avg)
            if (diff > threshold) {
                // Replace transient with interpolated value
                result[i] = avg.toShort()
            }
            history[historyPos] = result[i]
            historyPos = (historyPos + 1) % windowSize
        }
        return result
    }
}
```

- [ ] **Step 2: Write AudioMixer.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/audio/AudioMixer.kt`:
```kotlin
package com.meshtalk.app.audio

import java.util.concurrent.ConcurrentHashMap

/**
 * Mixes audio from multiple peers. Each peer submits decoded PCM frames.
 * mix() returns the sum of all active peer buffers, clipped to ±32767.
 */
class AudioMixer {
    private val peerBuffers = ConcurrentHashMap<String, ShortArray>()

    fun submitFrame(peerId: String, pcm: ShortArray) {
        peerBuffers[peerId] = pcm
    }

    fun removePeer(peerId: String) {
        peerBuffers.remove(peerId)
    }

    fun mix(frameSize: Int): ShortArray? {
        if (peerBuffers.isEmpty()) return null
        val mixed = ShortArray(frameSize)
        for ((_, buffer) in peerBuffers) {
            val len = minOf(buffer.size, frameSize)
            for (i in 0 until len) {
                val sum = mixed[i].toInt() + buffer[i].toInt()
                mixed[i] = sum.coerceIn(Short.MIN_VALUE.toInt(), Short.MAX_VALUE.toInt()).toShort()
            }
        }
        return mixed
    }

    fun clear() {
        peerBuffers.clear()
    }

    val peerCount: Int get() = peerBuffers.size
}
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: ClickRemovalFilter + AudioMixer — transient filter, multi-peer mixing"
```

---

## Task 9: Packet Codec (PARALLEL GROUP C)

**Files:**
- Create: `app/src/main/java/com/meshtalk/app/mesh/PacketCodec.kt`
- Create: `app/src/test/java/com/meshtalk/app/mesh/PacketCodecTest.kt`

- [ ] **Step 1: Write failing test**

Create `meshtalk/app/src/test/java/com/meshtalk/app/mesh/PacketCodecTest.kt`:
```kotlin
package com.meshtalk.app.mesh

import org.junit.Assert.*
import org.junit.Test

class PacketCodecTest {
    @Test
    fun encodeDecodeAudioPacket() {
        val payload = byteArrayOf(1, 2, 3, 4, 5)
        val encoded = PacketCodec.encodeAudio(channelId = 0, seq = 42, payload = payload)
        assertEquals(6 + 5, encoded.size) // 6 header + 5 payload
        assertEquals(PacketCodec.TYPE_AUDIO, encoded[0])
        assertEquals(0.toByte(), encoded[1]) // channel

        val decoded = PacketCodec.decode(encoded)
        assertNotNull(decoded)
        assertEquals(PacketCodec.TYPE_AUDIO, decoded!!.type)
        assertEquals(0, decoded.channelId)
        assertEquals(42, decoded.seq)
        assertArrayEquals(payload, decoded.payload)
    }

    @Test
    fun encodeDecodeControlPacket() {
        val json = """{"cmd":"announce","user":"glass_A"}"""
        val encoded = PacketCodec.encodeControl(channelId = 1, seq = 7, json = json)
        val decoded = PacketCodec.decode(encoded)
        assertNotNull(decoded)
        assertEquals(PacketCodec.TYPE_CONTROL, decoded!!.type)
        assertEquals(1, decoded.channelId)
        assertEquals(json, String(decoded.payload))
    }

    @Test
    fun encodeDecodePingPong() {
        val ping = PacketCodec.encodePing(channelId = 0, seq = 99)
        assertEquals(6, ping.size) // header only, no payload
        val decoded = PacketCodec.decode(ping)
        assertEquals(PacketCodec.TYPE_PING, decoded!!.type)
        assertEquals(99, decoded.seq)
    }

    @Test
    fun rejectsShortPackets() {
        val tooShort = byteArrayOf(1, 2, 3)
        assertNull(PacketCodec.decode(tooShort))
    }
}
```

- [ ] **Step 2: Run test, verify failure**

```bash
cd ~/meshtalk && ./gradlew test 2>&1 | tail -10
```

- [ ] **Step 3: Implement PacketCodec.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/mesh/PacketCodec.kt`:
```kotlin
package com.meshtalk.app.mesh

import java.nio.ByteBuffer
import java.nio.ByteOrder

data class MeshPacket(
    val type: Byte,
    val channelId: Int,
    val seq: Int,
    val payload: ByteArray
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is MeshPacket) return false
        return type == other.type && channelId == other.channelId &&
            seq == other.seq && payload.contentEquals(other.payload)
    }
    override fun hashCode() = 31 * type.hashCode() + channelId + seq + payload.contentHashCode()
}

object PacketCodec {
    const val HEADER_SIZE = 6
    const val TYPE_AUDIO: Byte = 0x01
    const val TYPE_CONTROL: Byte = 0x02
    const val TYPE_PING: Byte = 0x03
    const val TYPE_PONG: Byte = 0x04

    fun encodeAudio(channelId: Int, seq: Int, payload: ByteArray): ByteArray {
        return encode(TYPE_AUDIO, channelId, seq, payload)
    }

    fun encodeControl(channelId: Int, seq: Int, json: String): ByteArray {
        return encode(TYPE_CONTROL, channelId, seq, json.toByteArray(Charsets.UTF_8))
    }

    fun encodePing(channelId: Int, seq: Int): ByteArray {
        return encode(TYPE_PING, channelId, seq, ByteArray(0))
    }

    fun encodePong(channelId: Int, seq: Int): ByteArray {
        return encode(TYPE_PONG, channelId, seq, ByteArray(0))
    }

    fun decode(data: ByteArray): MeshPacket? {
        if (data.size < HEADER_SIZE) return null
        val buf = ByteBuffer.wrap(data).order(ByteOrder.BIG_ENDIAN)
        val type = buf.get()
        val channelId = buf.get().toInt() and 0xFF
        val seq = buf.getInt()
        val payload = ByteArray(data.size - HEADER_SIZE)
        if (payload.isNotEmpty()) buf.get(payload)
        return MeshPacket(type, channelId, seq, payload)
    }

    private fun encode(type: Byte, channelId: Int, seq: Int, payload: ByteArray): ByteArray {
        val buf = ByteBuffer.allocate(HEADER_SIZE + payload.size).order(ByteOrder.BIG_ENDIAN)
        buf.put(type)
        buf.put(channelId.toByte())
        buf.putInt(seq)
        buf.put(payload)
        return buf.array()
    }
}
```

- [ ] **Step 4: Run tests, verify pass**

```bash
cd ~/meshtalk && ./gradlew test 2>&1 | tail -10
```
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: PacketCodec — 6-byte header, audio/control/ping/pong types"
```

---

## Task 10: WiFi Aware Transport (PARALLEL GROUP C)

**Files:**
- Create: `app/src/main/java/com/meshtalk/app/mesh/MeshTransport.kt` (interface)
- Create: `app/src/main/java/com/meshtalk/app/mesh/WifiAwareTransport.kt`

- [ ] **Step 1: Write MeshTransport interface**

Create `meshtalk/app/src/main/java/com/meshtalk/app/mesh/MeshTransport.kt`:
```kotlin
package com.meshtalk.app.mesh

import java.net.InetAddress

data class MeshPeer(
    val id: String,
    val address: InetAddress,
    val port: Int,
    val lastSeen: Long = System.currentTimeMillis()
)

interface MeshTransport {
    val peers: List<MeshPeer>

    fun start(channelName: String)
    fun stop()
    fun switchChannel(channelName: String)
    fun sendToAll(data: ByteArray)
    fun sendTo(peerId: String, data: ByteArray)

    var onPeerDiscovered: ((MeshPeer) -> Unit)?
    var onPeerLost: ((String) -> Unit)?
    var onDataReceived: ((String, ByteArray) -> Unit)?  // peerId, data
}
```

- [ ] **Step 2: Write WifiAwareTransport.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/mesh/WifiAwareTransport.kt`:
```kotlin
package com.meshtalk.app.mesh

import android.content.Context
import android.net.*
import android.net.wifi.aware.*
import android.os.Handler
import android.os.HandlerThread
import android.util.Log
import java.net.*
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.*

class WifiAwareTransport(
    private val context: Context,
    private val deviceId: String,
    private val udpPort: Int = 18430
) : MeshTransport {

    companion object {
        private const val TAG = "WifiAwareTransport"
        private const val PSK = "meshtalk_shared_key_2025"
    }

    private var awareSession: WifiAwareSession? = null
    private var publishSession: PublishDiscoverySession? = null
    private var subscribeSession: SubscribeDiscoverySession? = null
    private val connectedPeers = ConcurrentHashMap<String, MeshPeer>()
    private var udpSocket: DatagramSocket? = null
    private var receiveJob: Job? = null
    private val handlerThread = HandlerThread("WifiAware").also { it.start() }
    private val handler = Handler(handlerThread.looper)
    private val connectivityManager = context.getSystemService(ConnectivityManager::class.java)
    private val scope = CoroutineScope(Dispatchers.IO)
    private var currentChannel = ""

    override val peers: List<MeshPeer> get() = connectedPeers.values.toList()
    override var onPeerDiscovered: ((MeshPeer) -> Unit)? = null
    override var onPeerLost: ((String) -> Unit)? = null
    override var onDataReceived: ((String, ByteArray) -> Unit)? = null

    override fun start(channelName: String) {
        currentChannel = channelName
        val wifiAwareManager = context.getSystemService(WifiAwareManager::class.java)
        if (wifiAwareManager == null) {
            Log.e(TAG, "WiFi Aware not available")
            return
        }

        wifiAwareManager.attach(object : AttachCallback() {
            override fun onAttached(session: WifiAwareSession) {
                Log.i(TAG, "WiFi Aware attached")
                awareSession = session
                startUdpReceiver()
                publish(channelName)
                subscribe(channelName)
            }
            override fun onAttachFailed() {
                Log.e(TAG, "WiFi Aware attach failed")
            }
        }, handler)
    }

    private fun publish(channelName: String) {
        val config = PublishConfig.Builder()
            .setServiceName(channelName)
            .setServiceSpecificInfo(deviceId.toByteArray(Charsets.UTF_8))
            .setPublishType(PublishConfig.PUBLISH_TYPE_UNSOLICITED)
            .build()

        awareSession?.publish(config, object : DiscoverySessionCallback() {
            override fun onPublishStarted(session: PublishDiscoverySession) {
                publishSession = session
                Log.i(TAG, "Publishing on $channelName")
            }
            override fun onMessageReceived(peerHandle: PeerHandle, message: ByteArray) {
                val peerId = String(message, Charsets.UTF_8)
                Log.i(TAG, "Message from peer: $peerId, requesting network")
                requestNetwork(session, peerHandle, peerId)
            }
        }, handler)
    }

    private fun subscribe(channelName: String) {
        val config = SubscribeConfig.Builder()
            .setServiceName(channelName)
            .setSubscribeType(SubscribeConfig.SUBSCRIBE_TYPE_PASSIVE)
            .build()

        awareSession?.subscribe(config, object : DiscoverySessionCallback() {
            override fun onServiceDiscovered(
                peerHandle: PeerHandle,
                serviceSpecificInfo: ByteArray,
                matchFilter: List<ByteArray>
            ) {
                val peerId = String(serviceSpecificInfo, Charsets.UTF_8)
                if (peerId == deviceId) return // Ignore self
                Log.i(TAG, "Discovered peer: $peerId")
                // Send our ID so the publisher can identify us
                subscribeSession?.sendMessage(peerHandle, 0, deviceId.toByteArray(Charsets.UTF_8))
                requestNetwork(subscribeSession!!, peerHandle, peerId)
            }

            override fun onSubscribeStarted(session: SubscribeDiscoverySession) {
                subscribeSession = session
                Log.i(TAG, "Subscribed to $channelName")
            }
        }, handler)
    }

    private fun requestNetwork(session: DiscoverySession, peerHandle: PeerHandle, peerId: String) {
        if (connectedPeers.containsKey(peerId)) return

        val specifier = WifiAwareNetworkSpecifier.Builder(session, peerHandle)
            .setPskPassphrase(PSK)
            .build()

        val request = NetworkRequest.Builder()
            .addTransportType(NetworkCapabilities.TRANSPORT_WIFI_AWARE)
            .setNetworkSpecifier(specifier)
            .build()

        connectivityManager.requestNetwork(request, object : ConnectivityManager.NetworkCallback() {
            override fun onCapabilitiesChanged(network: Network, caps: NetworkCapabilities) {
                val peerInfo = caps.transportInfo as? WifiAwareNetworkInfo ?: return
                val peerAddr = peerInfo.peerIpv6Addr
                val scopeId = peerInfo.networkInterface?.let {
                    NetworkInterface.getByName(it)?.index ?: 0
                } ?: 0

                val addr = Inet6Address.getByAddress(
                    null, peerAddr.address, scopeId
                )
                val peer = MeshPeer(peerId, addr, udpPort)
                connectedPeers[peerId] = peer
                Log.i(TAG, "Connected to peer $peerId at $addr")
                onPeerDiscovered?.invoke(peer)
            }

            override fun onLost(network: Network) {
                connectedPeers.entries.removeIf { true } // simplified
                Log.w(TAG, "Network lost")
            }
        }, handler)
    }

    private fun startUdpReceiver() {
        udpSocket = DatagramSocket(udpPort)
        udpSocket?.soTimeout = 0 // blocking

        receiveJob = scope.launch {
            val buf = ByteArray(2048)
            Log.i(TAG, "UDP receiver started on port $udpPort")
            while (isActive) {
                try {
                    val packet = DatagramPacket(buf, buf.size)
                    udpSocket?.receive(packet)
                    val data = buf.copyOf(packet.length)
                    val senderAddr = packet.address
                    // Find peer by address
                    val peerId = connectedPeers.entries
                        .firstOrNull { it.value.address.address.contentEquals(senderAddr.address) }
                        ?.key ?: "unknown"
                    onDataReceived?.invoke(peerId, data)
                } catch (e: Exception) {
                    if (isActive) Log.e(TAG, "Receive error: ${e.message}")
                }
            }
        }
    }

    override fun sendToAll(data: ByteArray) {
        for ((_, peer) in connectedPeers) {
            sendTo(peer.id, data)
        }
    }

    override fun sendTo(peerId: String, data: ByteArray) {
        val peer = connectedPeers[peerId] ?: return
        scope.launch {
            try {
                val packet = DatagramPacket(data, data.size, peer.address, peer.port)
                udpSocket?.send(packet)
            } catch (e: Exception) {
                Log.e(TAG, "Send to $peerId failed: ${e.message}")
            }
        }
    }

    override fun switchChannel(channelName: String) {
        Log.i(TAG, "Switching from $currentChannel to $channelName")
        publishSession?.close()
        subscribeSession?.close()
        connectedPeers.clear()
        currentChannel = channelName
        publish(channelName)
        subscribe(channelName)
    }

    override fun stop() {
        receiveJob?.cancel()
        udpSocket?.close()
        publishSession?.close()
        subscribeSession?.close()
        awareSession?.close()
        connectedPeers.clear()
        scope.cancel()
        Log.i(TAG, "Transport stopped")
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: WiFi Aware transport — publish/subscribe, NAN data path, UDP audio"
```

---

## Task 11: Peer Manager (PARALLEL GROUP C)

**Files:**
- Create: `app/src/main/java/com/meshtalk/app/mesh/PeerManager.kt`

- [ ] **Step 1: Write PeerManager.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/mesh/PeerManager.kt`:
```kotlin
package com.meshtalk.app.mesh

import android.util.Log
import kotlinx.coroutines.*

class PeerManager(
    private val transport: MeshTransport,
    private val timeoutMs: Long = 15000,
    private val announceIntervalMs: Long = 15000,
    private val keepaliveIntervalMs: Long = 5000
) {
    companion object {
        private const val TAG = "PeerManager"
    }

    private val activePeers = mutableMapOf<String, Long>() // peerId → lastSeen
    private var keepaliveJob: Job? = null
    private var announceJob: Job? = null
    private var seq = 0

    var onPeerCountChanged: ((Int) -> Unit)? = null
    var deviceId: String = "unknown"
    var currentChannelId: Int = 0

    fun start(scope: CoroutineScope) {
        keepaliveJob = scope.launch {
            while (isActive) {
                delay(keepaliveIntervalMs)
                sendKeepalive()
                pruneStale()
            }
        }
        announceJob = scope.launch {
            while (isActive) {
                delay(announceIntervalMs)
                sendAnnounce()
            }
        }
    }

    fun onPeerDataReceived(peerId: String) {
        val isNew = !activePeers.containsKey(peerId)
        activePeers[peerId] = System.currentTimeMillis()
        if (isNew) {
            Log.i(TAG, "New peer: $peerId (total: ${activePeers.size + 1})")
            onPeerCountChanged?.invoke(activePeers.size + 1) // +1 for self
        }
    }

    fun onPeerLost(peerId: String) {
        activePeers.remove(peerId)
        Log.i(TAG, "Peer lost: $peerId (total: ${activePeers.size + 1})")
        onPeerCountChanged?.invoke(activePeers.size + 1)
    }

    private fun pruneStale() {
        val now = System.currentTimeMillis()
        val stale = activePeers.filter { now - it.value > timeoutMs }.keys
        for (id in stale) {
            activePeers.remove(id)
            Log.i(TAG, "Peer timed out: $id")
            onPeerCountChanged?.invoke(activePeers.size + 1)
        }
    }

    private fun sendKeepalive() {
        val packet = PacketCodec.encodePing(currentChannelId, seq++)
        transport.sendToAll(packet)
    }

    fun sendAnnounce() {
        val json = """{"cmd":"announce","user":"$deviceId","channel":$currentChannelId,"muted":false}"""
        val packet = PacketCodec.encodeControl(currentChannelId, seq++, json)
        transport.sendToAll(packet)
    }

    val peerCount: Int get() = activePeers.size + 1 // +1 for self

    fun stop() {
        keepaliveJob?.cancel()
        announceJob?.cancel()
        activePeers.clear()
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: PeerManager — keepalive, announce, timeout, peer count"
```

---

## Task 12: Channel Manager (PARALLEL GROUP C)

**Files:**
- Create: `app/src/main/java/com/meshtalk/app/mesh/ChannelManager.kt`

- [ ] **Step 1: Write ChannelManager.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/mesh/ChannelManager.kt`:
```kotlin
package com.meshtalk.app.mesh

import android.util.Log

data class Channel(
    val id: Int,
    val serviceName: String,
    val displayName: String
)

class ChannelManager(
    private val transport: MeshTransport,
    private val peerManager: PeerManager
) {
    companion object {
        private const val TAG = "ChannelManager"
        val CHANNELS = listOf(
            Channel(0, "meshtalk_alpha", "Alpha"),
            Channel(1, "meshtalk_bravo", "Bravo")
        )
    }

    var currentChannel: Channel = CHANNELS[0]
        private set

    var onChannelChanged: ((Channel) -> Unit)? = null

    fun joinChannel(channelId: Int) {
        val channel = CHANNELS.getOrNull(channelId) ?: return
        currentChannel = channel
        peerManager.currentChannelId = channelId
        transport.start(channel.serviceName)
        peerManager.sendAnnounce()
        onChannelChanged?.invoke(channel)
        Log.i(TAG, "Joined channel: ${channel.displayName}")
    }

    fun switchChannel() {
        val nextId = (currentChannel.id + 1) % CHANNELS.size
        val nextChannel = CHANNELS[nextId]
        Log.i(TAG, "Switching: ${currentChannel.displayName} → ${nextChannel.displayName}")
        currentChannel = nextChannel
        peerManager.currentChannelId = nextId
        transport.switchChannel(nextChannel.serviceName)
        peerManager.sendAnnounce()
        onChannelChanged?.invoke(nextChannel)
    }

    fun leaveChannel() {
        transport.stop()
        Log.i(TAG, "Left channel: ${currentChannel.displayName}")
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: ChannelManager — Alpha/Bravo channels, switch, join/leave"
```

---

## Task 13: HUD — WebView HTML (PARALLEL GROUP D)

**Files:**
- Create: `app/src/main/assets/hud/meshtalk.html`
- Create: `app/src/main/java/com/meshtalk/app/hud/HudRenderer.kt`

- [ ] **Step 1: Write meshtalk.html**

Create `meshtalk/app/src/main/assets/hud/meshtalk.html`:
```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=640,height=480,initial-scale=1">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 640px; height: 480px; background: transparent; overflow: hidden;
  font-family: 'Segoe UI', Arial, sans-serif; color: #fff; }

.container { width: 640px; height: 480px; position: relative; }

.header { position: absolute; top: 20px; left: 30px; right: 30px;
  display: flex; justify-content: space-between; align-items: center; }
.app-name { font-size: 28px; font-weight: 700; letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(0,200,255,0.5); }
.channel-info { text-align: right; }
.channel-name { font-size: 22px; font-weight: 600; color: #00d4ff; }
.user-count { font-size: 16px; color: #88ccff; margin-top: 2px; }

.vox-indicator { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  text-align: center; }
.vox-dot { width: 40px; height: 40px; border-radius: 50%; margin: 0 auto 10px;
  background: #444; transition: all 0.2s; }
.vox-dot.active { background: #00ff88; box-shadow: 0 0 20px #00ff88, 0 0 40px rgba(0,255,136,0.3);
  animation: pulse 1s infinite; }
.vox-label { font-size: 18px; font-weight: 600; color: #888; }
.vox-label.active { color: #00ff88; }

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

.mute-indicator { position: absolute; top: 55%; left: 50%; transform: translateX(-50%);
  margin-top: 40px; font-size: 20px; color: #ff4444; display: none;
  text-shadow: 0 0 8px rgba(255,68,68,0.5); }
.mute-indicator.visible { display: block; }

.swipe-hints { position: absolute; bottom: 30px; left: 30px; right: 30px;
  display: flex; justify-content: space-between; opacity: 0.3; font-size: 14px; }

.status-bar { position: absolute; bottom: 8px; left: 50%; transform: translateX(-50%);
  font-size: 11px; color: #555; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="app-name">MESHTALK</div>
    <div class="channel-info">
      <div class="channel-name" id="channelName">Alpha</div>
      <div class="user-count" id="userCount">1 on</div>
    </div>
  </div>

  <div class="vox-indicator">
    <div class="vox-dot" id="voxDot"></div>
    <div class="vox-label" id="voxLabel">IDLE</div>
  </div>

  <div class="mute-indicator" id="muteIndicator">🔇 MUTED</div>

  <div class="swipe-hints">
    <span>← CH</span>
    <span>MUTE →</span>
  </div>

  <div class="status-bar" id="statusBar">Scanning...</div>
</div>

<script>
window.HUD = {
  updateChannel: function(name) {
    document.getElementById('channelName').textContent = name;
  },
  updateUserCount: function(count) {
    document.getElementById('userCount').textContent = count + ' on';
  },
  updateVox: function(active) {
    var dot = document.getElementById('voxDot');
    var label = document.getElementById('voxLabel');
    if (active) {
      dot.classList.add('active');
      label.classList.add('active');
      label.textContent = 'LIVE';
    } else {
      dot.classList.remove('active');
      label.classList.remove('active');
      label.textContent = 'IDLE';
    }
  },
  updateMute: function(muted) {
    var el = document.getElementById('muteIndicator');
    if (muted) { el.classList.add('visible'); } else { el.classList.remove('visible'); }
  },
  updateStatus: function(text) {
    document.getElementById('statusBar').textContent = text;
  }
};

// Signal ready to Kotlin
if (window.NativeBridge) window.NativeBridge.onWebViewReady();
</script>
</body>
</html>
```

- [ ] **Step 2: Write HudRenderer.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/hud/HudRenderer.kt`:
```kotlin
package com.meshtalk.app.hud

import android.graphics.Color
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.util.Log

class HudRenderer(private val webView: WebView) {
    companion object {
        private const val TAG = "HudRenderer"
    }

    var onReady: (() -> Unit)? = null
    private var isReady = false
    private val pendingCalls = mutableListOf<String>()

    fun init() {
        webView.setBackgroundColor(Color.TRANSPARENT)
        webView.settings.javaScriptEnabled = true
        webView.addJavascriptInterface(Bridge(), "NativeBridge")
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                // Flush any pending JS calls
                isReady = true
                for (call in pendingCalls) {
                    webView.evaluateJavascript(call, null)
                }
                pendingCalls.clear()
            }
        }
        webView.loadUrl("file:///android_asset/hud/meshtalk.html")
    }

    private fun runJs(js: String) {
        if (isReady) {
            webView.evaluateJavascript(js, null)
        } else {
            pendingCalls.add(js)
        }
    }

    fun updateChannel(name: String) = runJs("window.HUD.updateChannel('$name')")
    fun updateUserCount(count: Int) = runJs("window.HUD.updateUserCount($count)")
    fun updateVox(active: Boolean) = runJs("window.HUD.updateVox($active)")
    fun updateMute(muted: Boolean) = runJs("window.HUD.updateMute($muted)")
    fun updateStatus(text: String) = runJs("window.HUD.updateStatus('$text')")

    inner class Bridge {
        @JavascriptInterface
        fun onWebViewReady() {
            Log.i(TAG, "WebView HUD ready")
            onReady?.invoke()
        }
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: HUD — WebView overlay, channel/vox/mute/status display"
```

---

## Task 14: Foreground Service + Boot Receiver (after Tasks 1-13)

**Files:**
- Create: `app/src/main/java/com/meshtalk/app/service/MeshTalkService.kt`
- Create: `app/src/main/java/com/meshtalk/app/service/BootReceiver.kt`

- [ ] **Step 1: Write MeshTalkService.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/service/MeshTalkService.kt`:
```kotlin
package com.meshtalk.app.service

import android.app.*
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.*
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import com.meshtalk.app.MeshTalkActivity
import com.meshtalk.app.audio.*
import com.meshtalk.app.mesh.*
import com.meshtalk.app.vox.VoxStateMachine
import com.meshtalk.app.vox.VoxState
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.collectLatest

class MeshTalkService : Service() {
    companion object {
        private const val TAG = "MeshTalkService"
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "meshtalk_service"
    }

    // Audio pipeline
    lateinit var captureEngine: AudioCaptureEngine
    lateinit var playbackEngine: AudioPlaybackEngine
    lateinit var opusCodec: OpusCodec
    lateinit var speexAec: SpeexAec
    lateinit var vadEngine: VadEngine
    lateinit var voxStateMachine: VoxStateMachine
    lateinit var clickFilter: ClickRemovalFilter
    lateinit var audioMixer: AudioMixer

    // Mesh
    lateinit var transport: MeshTransport
    lateinit var peerManager: PeerManager
    lateinit var channelManager: ChannelManager

    private var wakeLock: PowerManager.WakeLock? = null
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private var pipelineJob: Job? = null
    private var seq = 0
    var isActive = false
        private set
    var isMuted = false
        private set

    var onVoxStateChanged: ((VoxState) -> Unit)? = null
    var onPeerCountChanged: ((Int) -> Unit)? = null
    var onChannelChanged: ((String) -> Unit)? = null

    private val binder = LocalBinder()
    inner class LocalBinder : Binder() {
        fun getService(): MeshTalkService = this@MeshTalkService
    }
    override fun onBind(intent: Intent?) = binder

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        createNotificationChannel()
        ServiceCompat.startForeground(
            this, NOTIFICATION_ID, createNotification(),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK or
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE
        )
        acquireWakeLock()

        if (!isActive) {
            initPipeline()
        }

        return START_STICKY
    }

    private fun initPipeline() {
        val deviceId = Build.SERIAL.takeLast(6).ifEmpty { "glass" }

        // Audio components
        captureEngine = AudioCaptureEngine()
        playbackEngine = AudioPlaybackEngine()
        opusCodec = OpusCodec()
        speexAec = SpeexAec()
        vadEngine = VadEngine(this)
        voxStateMachine = VoxStateMachine()
        clickFilter = ClickRemovalFilter()
        audioMixer = AudioMixer()

        // Mesh components
        transport = WifiAwareTransport(this, deviceId)
        peerManager = PeerManager(transport)
        peerManager.deviceId = deviceId
        channelManager = ChannelManager(transport, peerManager)

        // Init native libs
        opusCodec.init()
        speexAec.init()

        // Callbacks
        voxStateMachine.onStateChanged = { state ->
            onVoxStateChanged?.invoke(state)
        }
        peerManager.onPeerCountChanged = { count ->
            onPeerCountChanged?.invoke(count)
        }
        channelManager.onChannelChanged = { channel ->
            onChannelChanged?.invoke(channel.displayName)
        }

        // Mesh data handler
        transport.onDataReceived = { peerId, data ->
            peerManager.onPeerDataReceived(peerId)
            handleIncomingPacket(peerId, data)
        }
        transport.onPeerDiscovered = { peer ->
            peerManager.onPeerDataReceived(peer.id)
            Log.i(TAG, "Peer connected: ${peer.id}")
        }
        transport.onPeerLost = { peerId ->
            peerManager.onPeerLost(peerId)
            audioMixer.removePeer(peerId)
        }

        // Playback feeds AEC reference
        playbackEngine.onFramePlayed = { frame ->
            speexAec.feedReference(frame)
        }

        // Start everything
        captureEngine.start()
        playbackEngine.start()
        peerManager.start(scope)
        channelManager.joinChannel(0) // Default: Alpha

        // Start capture pipeline
        pipelineJob = scope.launch {
            captureEngine.audioFrames.collectLatest { micFrame ->
                processCaptureFrame(micFrame)
            }
        }

        isActive = true
        Log.i(TAG, "Pipeline initialized, device=$deviceId")
    }

    private fun processCaptureFrame(micFrame: ShortArray) {
        // 1. AEC
        val aecFrame = speexAec.process(micFrame)

        // 2. VAD (accumulates 160→512)
        val vadResult = vadEngine.feedFrame(aecFrame)

        // 3. VOX state machine
        if (vadResult != null) {
            voxStateMachine.muted = isMuted
            voxStateMachine.onVadResult(vadResult, 32) // 32ms per VAD window
        }

        // 4. If speaking, encode and send
        if (voxStateMachine.shouldTransmit) {
            // Accumulate to 320 samples (20ms) for Opus
            // For simplicity, send every AEC frame through Opus
            // (Opus handles variable input sizes internally)
            val encoded = opusCodec.encode(aecFrame, aecFrame.size) ?: return
            val packet = PacketCodec.encodeAudio(
                channelManager.currentChannel.id, seq++, encoded
            )
            transport.sendToAll(packet)
        }
    }

    private fun handleIncomingPacket(peerId: String, data: ByteArray) {
        val packet = PacketCodec.decode(data) ?: return
        when (packet.type) {
            PacketCodec.TYPE_AUDIO -> {
                val decoded = opusCodec.decode(packet.payload) ?: return
                val filtered = clickFilter.process(decoded)
                audioMixer.submitFrame(peerId, filtered)
                val mixed = audioMixer.mix(filtered.size) ?: return
                playbackEngine.play(mixed)
            }
            PacketCodec.TYPE_CONTROL -> {
                // Handle control messages (announce, mute, etc.)
                Log.d(TAG, "Control from $peerId: ${String(packet.payload)}")
            }
            PacketCodec.TYPE_PING -> {
                val pong = PacketCodec.encodePong(packet.channelId, packet.seq)
                transport.sendTo(peerId, pong)
            }
            PacketCodec.TYPE_PONG -> { /* keepalive acknowledged */ }
        }
    }

    fun toggleActive(): Boolean {
        isActive = !isActive
        if (isActive) {
            initPipeline()
        } else {
            stopPipeline()
        }
        return isActive
    }

    fun toggleMute(): Boolean {
        isMuted = !isMuted
        voxStateMachine.muted = isMuted
        return isMuted
    }

    fun switchChannel() {
        audioMixer.clear()
        channelManager.switchChannel()
    }

    private fun stopPipeline() {
        pipelineJob?.cancel()
        captureEngine.stop()
        playbackEngine.stop()
        channelManager.leaveChannel()
        peerManager.stop()
        opusCodec.release()
        speexAec.release()
        vadEngine.release()
        audioMixer.clear()
        Log.i(TAG, "Pipeline stopped")
    }

    private fun acquireWakeLock() {
        wakeLock = (getSystemService(POWER_SERVICE) as PowerManager).run {
            newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "MeshTalk::ServiceLock")
                .apply { acquire(10 * 60 * 1000L) }
        }
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID, "MeshTalk Service",
            NotificationManager.IMPORTANCE_LOW
        ).apply { description = "MeshTalk walkie-talkie active" }
        (getSystemService(NOTIFICATION_SERVICE) as NotificationManager)
            .createNotificationChannel(channel)
    }

    private fun createNotification(): Notification {
        val intent = Intent(this, MeshTalkActivity::class.java)
        val pending = PendingIntent.getActivity(
            this, 0, intent, PendingIntent.FLAG_IMMUTABLE
        )
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("MeshTalk")
            .setContentText("Walkie-talkie active")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentIntent(pending)
            .setOngoing(true)
            .build()
    }

    override fun onDestroy() {
        stopPipeline()
        wakeLock?.release()
        scope.cancel()
        super.onDestroy()
    }
}
```

- [ ] **Step 2: Write BootReceiver.kt**

Create `meshtalk/app/src/main/java/com/meshtalk/app/service/BootReceiver.kt`:
```kotlin
package com.meshtalk.app.service

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import com.meshtalk.app.MeshTalkActivity

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        if (intent?.action in listOf(
                Intent.ACTION_BOOT_COMPLETED,
                Intent.ACTION_LOCKED_BOOT_COMPLETED
            )) {
            Log.i("BootReceiver", "Boot completed — starting MeshTalk")
            val launchIntent = Intent(context, MeshTalkActivity::class.java).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                putExtra("boot_start", true)
            }
            context.startActivity(launchIntent)
        }
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: MeshTalkService + BootReceiver — foreground service, full pipeline"
```

---

## Task 15: Activity Integration (after Tasks 1-14)

**Files:**
- Modify: `app/src/main/java/com/meshtalk/app/MeshTalkActivity.kt` (rewrite from stub)

- [ ] **Step 1: Rewrite MeshTalkActivity.kt with full integration**

Replace `meshtalk/app/src/main/java/com/meshtalk/app/MeshTalkActivity.kt`:
```kotlin
package com.meshtalk.app

import android.content.ComponentName
import android.content.Intent
import android.content.ServiceConnection
import android.os.*
import android.util.Log
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.ffalcon.mercury.android.sdk.temple.TempleAction
import com.ffalcon.mercury.android.sdk.view.BaseMirrorActivity
import com.meshtalk.app.databinding.ActivityMeshtalkBinding
import com.meshtalk.app.hud.HudRenderer
import com.meshtalk.app.service.MeshTalkService
import com.meshtalk.app.vox.VoxState
import kotlinx.coroutines.launch
import kotlin.math.abs

class MeshTalkActivity : BaseMirrorActivity<ActivityMeshtalkBinding>() {
    companion object {
        private const val TAG = "MeshTalkActivity"
    }

    private var hudRenderer: HudRenderer? = null
    private var meshService: MeshTalkService? = null
    private var serviceBound = false

    private val serviceConnection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            val service = (binder as MeshTalkService.LocalBinder).getService()
            meshService = service
            serviceBound = true
            setupServiceCallbacks(service)
            Log.i(TAG, "Service connected")
        }
        override fun onServiceDisconnected(name: ComponentName?) {
            meshService = null
            serviceBound = false
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Setup HUD
        mBindingPair.updateView {
            tvStatus.visibility = android.view.View.GONE
            hudRenderer = HudRenderer(wvHud).also { it.init() }
        }

        // Start and bind to service
        val serviceIntent = Intent(this, MeshTalkService::class.java)
        startForegroundService(serviceIntent)
        bindService(serviceIntent, serviceConnection, BIND_AUTO_CREATE)

        // Setup temple gestures
        setupGestures()

        Log.i(TAG, "Activity created")
    }

    private fun setupGestures() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.RESUMED) {
                templeActionViewModel.state.collect { action ->
                    when (action) {
                        is TempleAction.Click -> onTap()
                        is TempleAction.DoubleClick -> exitApp()
                        is TempleAction.TripleClick -> exitApp()
                        is TempleAction.SlideContinuous -> {
                            val delta = action.delta
                            if (abs(delta) > 0.1f) {
                                if (delta > 0.1f) onSwipeLeft()   // forward = channel switch
                                if (delta < -0.1f) onSwipeRight() // backward = mute toggle
                            }
                        }
                        else -> Unit
                    }
                }
            }
        }
    }

    private fun onTap() {
        val service = meshService ?: return
        val active = service.toggleActive()
        Log.i(TAG, "Toggle: active=$active")
        runOnUiThread {
            hudRenderer?.updateStatus(if (active) "Connected" else "OFF")
        }
    }

    private fun onSwipeRight() {
        val service = meshService ?: return
        val muted = service.toggleMute()
        Log.i(TAG, "Mute: $muted")
        runOnUiThread {
            hudRenderer?.updateMute(muted)
        }
        // Vibrate feedback
        val vibrator = getSystemService(Vibrator::class.java)
        vibrator?.vibrate(VibrationEffect.createOneShot(50, VibrationEffect.DEFAULT_AMPLITUDE))
    }

    private fun onSwipeLeft() {
        val service = meshService ?: return
        service.switchChannel()
        Log.i(TAG, "Channel switched")
        // Vibrate feedback
        val vibrator = getSystemService(Vibrator::class.java)
        vibrator?.vibrate(VibrationEffect.createOneShot(50, VibrationEffect.DEFAULT_AMPLITUDE))
    }

    private fun setupServiceCallbacks(service: MeshTalkService) {
        service.onVoxStateChanged = { state ->
            runOnUiThread {
                hudRenderer?.updateVox(state == VoxState.SPEAKING || state == VoxState.HANGOVER)
            }
        }
        service.onPeerCountChanged = { count ->
            runOnUiThread {
                hudRenderer?.updateUserCount(count)
            }
        }
        service.onChannelChanged = { name ->
            runOnUiThread {
                hudRenderer?.updateChannel(name)
            }
        }
    }

    private fun exitApp() {
        Log.i(TAG, "Exiting app")
        meshService?.toggleActive() // stop pipeline
        if (serviceBound) {
            unbindService(serviceConnection)
            serviceBound = false
        }
        stopService(Intent(this, MeshTalkService::class.java))
        (getSystemService(NOTIFICATION_SERVICE) as android.app.NotificationManager).cancelAll()
        finishAffinity()
        Handler(Looper.getMainLooper()).postDelayed({
            Process.killProcess(Process.myPid())
        }, 200)
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        exitApp()
    }

    override fun onDestroy() {
        if (serviceBound) {
            unbindService(serviceConnection)
            serviceBound = false
        }
        super.onDestroy()
    }
}
```

- [ ] **Step 2: Verify build compiles**

```bash
cd ~/meshtalk && ./gradlew assembleDebug 2>&1 | tail -10
```
Expected: BUILD SUCCESSFUL

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: MeshTalkActivity — gesture handling, service binding, HUD integration"
```

---

## Task 16: Deploy Scripts + On-Device Testing (after Task 15)

**Files:**
- Create: `meshtalk/scripts/deploy.sh`

- [ ] **Step 1: Write deploy.sh**

Create `meshtalk/scripts/deploy.sh`:
```bash
#!/bin/bash
set -e

ADB=/opt/homebrew/bin/adb
PKG=com.meshtalk.app
APK=app/build/outputs/apk/debug/app-debug.apk

echo "=== Building MeshTalk ==="
cd "$(dirname "$0")/.."
./gradlew assembleDebug 2>&1 | tail -3

SERIALS=($($ADB devices -l | grep 'ARGF20' | awk '{print $1}'))
echo "=== Found ${#SERIALS[@]} glasses ==="

for SERIAL in "${SERIALS[@]}"; do
    echo ""
    echo "=== Deploying to $SERIAL ==="
    $ADB -s $SERIAL shell settings put global mercury_install_allowed 1
    $ADB -s $SERIAL install -r $APK
    $ADB -s $SERIAL shell pm grant $PKG android.permission.RECORD_AUDIO 2>/dev/null || true
    $ADB -s $SERIAL shell pm grant $PKG android.permission.ACCESS_FINE_LOCATION 2>/dev/null || true
    $ADB -s $SERIAL shell pm grant $PKG android.permission.NEARBY_WIFI_DEVICES 2>/dev/null || true
    $ADB -s $SERIAL shell svc wifi enable
    sleep 2
    $ADB -s $SERIAL shell am start -n $PKG/.MeshTalkActivity
    echo "    ✓ Deployed and launched on $SERIAL"
done

echo ""
echo "=== All glasses deployed ==="
echo "Wait 10-15 seconds for WiFi Aware discovery..."
```

- [ ] **Step 2: Make executable and test deploy**

```bash
chmod +x ~/meshtalk/scripts/deploy.sh
~/meshtalk/scripts/deploy.sh
```

Expected: Both glasses get the APK installed, permissions granted, WiFi enabled, app launched.

- [ ] **Step 3: Verify on-device**

```bash
ADB=/opt/homebrew/bin/adb
# Check app is running on both
echo "=== Glasses A ==="
$ADB -s A06B4A8FF4A1633 shell "dumpsys activity activities | grep meshtalk | head -3"
echo "=== Glasses B ==="
$ADB -s A06B4A94CC51663 shell "dumpsys activity activities | grep meshtalk | head -3"

# Watch logs
$ADB -s A06B4A8FF4A1633 logcat -d -t 50 | grep "MeshTalk\|WifiAware\|AudioCapture\|AudioPlayback\|VoxState\|PeerManager"
```

Expected: Activity running, service started, WiFi Aware attached, scanning for peers.

- [ ] **Step 4: Test peer discovery**

```bash
# Wait 15 seconds for WiFi Aware discovery
sleep 15
# Check logs for peer discovery
ADB=/opt/homebrew/bin/adb
$ADB -s A06B4A8FF4A1633 logcat -d -t 100 | grep -i "peer\|discover\|connect\|aware"
$ADB -s A06B4A94CC51663 logcat -d -t 100 | grep -i "peer\|discover\|connect\|aware"
```

Expected: Both glasses discover each other, establish NAN data path.

- [ ] **Step 5: Test audio round-trip**

Speak near Glasses A → check Glasses B logcat for incoming audio packets:
```bash
ADB=/opt/homebrew/bin/adb
# Monitor Glasses B for incoming audio
$ADB -s A06B4A94CC51663 logcat -d -t 200 | grep "TYPE_AUDIO\|AudioPlayback\|OpusCodec\|mix"
```

Expected: Audio packets received, decoded, played through bone conduction speakers.

- [ ] **Step 6: Test gestures**

- Tap temple on Glasses A → should toggle off (HUD shows "OFF")
- Tap again → should toggle on
- Swipe right → should toggle mute (HUD shows 🔇 MUTED)
- Swipe left → should switch to Bravo (HUD shows "Bravo")
- Double-tap → should exit app

- [ ] **Step 7: Commit deploy script**

```bash
cd ~/meshtalk
git add -A && git commit -m "feat: deploy script — build, install, grant, launch on all glasses"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] WiFi Aware transport (Task 10)
- [x] Audio pipeline: capture → AEC → VAD → Opus (Tasks 2-6, 14)
- [x] VOX state machine (Task 7)
- [x] Playback with volume boost + click removal (Tasks 5, 8)
- [x] Two channels Alpha/Bravo (Task 12)
- [x] Temple gestures: tap=toggle, swipe R=mute, swipe L=channel, double=exit (Task 15)
- [x] HUD display: channel, user count, VOX, mute (Task 13)
- [x] Foreground service + boot receiver (Task 14)
- [x] Non-consensual auto-play (Task 14 — service auto-starts pipeline)
- [x] Mercury SDK integration (Tasks 1, 15)
- [x] Deploy to both glasses (Task 16)
- [x] Peer management + user count (Task 11)
- [x] Packet format (Task 9)
- [x] Multi-peer audio mixing (Task 8)

**Placeholder scan:** No TBD/TODO/placeholder found.

**Type consistency verified:** OpusCodec.encode/decode, SpeexAec.process/feedReference, VadEngine.feedFrame, VoxStateMachine.onVadResult, PacketCodec.encode*/decode, MeshTransport interface — all signatures match across Tasks 2-15.
