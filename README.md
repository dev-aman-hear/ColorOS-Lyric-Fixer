# ColorOS Native Lyric Fixer 🎵

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Android](https://img.shields.io/badge/Android-14%20%7C%2015%20%7C%2016-green.svg)](https://developer.android.com)
[![ColorOS](https://img.shields.io/badge/ColorOS-14%20%7C%2015%20%7C%2016-orange.svg)](https://www.oppo.com/en/coloros/)
[![OxygenOS](https://img.shields.io/badge/OxygenOS-14%20%7C%2015%20%7C%2016-red.svg)](https://www.oneplus.com)


> [!IMPORTANT]
> **Compatibility Notice (Tested on ColorOS 16):**  
> This method and allowlist architecture have been reverse-engineered, deployed, and **verified on ColorOS 16 (Android 16)** on Realme GT Neo 3T (Realme UI 7.0 / OxygenOS 16).  
> **Please Note:** Major future firmware updates (such as **ColorOS 17 / Android 17**) may alter internal SystemUI class implementations, SharedPreferences keys, or RomUpdate database schemas, and may require a different procedure or updated patch points.

Unlock native **ColorOS / OxygenOS / Realme UI Lock-Screen Lyrics, Dynamic Island / Capsule Alerts, and Panoramic AOD Lyrics** for custom music players (such as **AuraMusic**, **ViMusic**, **Spotube**, **Innertune**, etc.) without spoofing package identities or renaming applications.

---

## 🌟 What This Project Does

On ColorOS and OxygenOS, native synchronized lyrics are displayed across three surfaces:
1. **Native Lock-Screen Dynamic Capsule / Live Alert**
2. **Panoramic Always-On Display (AOD)**
3. **Quick Settings Expanded Media Control Panel**

By default, ColorOS firmware restricts native lyric rendering to a hardcoded OEM allowlist (`com.heytap.music`, `com.tencent.qqmusic`, `com.netease.cloudmusic`, `com.kugou.android`).

This repository provides:
- **For ROM Developers:** The exact method to bake any custom music player natively into custom ColorOS / OxygenOS ROMs (zero root required).
- **For Rooted Users:** A 1-click injector and Magisk/KernelSU module that enables native lyrics dynamically on running devices.
- **For Android Music App Developers:** Code guides on how to format the `lyricInfo` payload in `MediaMetadata`.

---

## 🔬 How It Works (Deep Technical Architecture)

### 1. The Decoupled Lyric Pipeline
Reverse-engineering of `SystemUI.apk` (`OplusMediaDataManagerExImpl.java` and `OplusMediaLyricData.java`) revealed that lyric processing is split into two phases:

- **Ingestion (`loadLyricInBg`):**  
  SystemUI extracts the string key `"lyricInfo"` from Android's standard `MediaMetadata`. It parses the JSON payload containing the song name, artist, song ID, and `.lrc` formatted lyrics.  
  *No signature, UID, or SELinux permission checks exist at this stage—any app can submit lyrics.*

- **Display Authorization Bitmask (`OplusMediaLyricData.isEnabled`):**  
  SystemUI assigns `this.displayPolicy` using `MediaActionPrioritySelectorImpl.getLyricEntrance(packageName)`.  
  Rendering is guarded by:
  ```java
  public boolean isEnabled(int flag) {
      return !this.lines.isEmpty() && ((this.displayPolicy & flag) != 0);
  }
  ```
  | Bit Flag | Value | Target Surface |
  |---|:---:|---|
  | `0x04` | `4` | **Lock-Screen Capsule / Live Alert & Panoramic AOD** |
  | `0x10` | `16` | **Quick Settings Expanded Media Panel Lyrics** |
  | `0x20` | `32` | **Notification / Auxiliary Surface** |
  | **Combined** | **`52`** (`0x34`) | **Full OEM Lyric Entrance** |

For unlisted third-party players, `getLyricEntrance()` returns `0`. Even though SystemUI parses the lyrics into memory, `(0 & 4)` and `(0 & 16)` evaluate to `false`, suppressing all on-screen rendering.

### 2. Persistent Configuration System (`OplusMediaRusUpdateManager`)
Directly editing `/data/user_de/0/com.android.systemui/shared_prefs/oplus_media_controller_config_sp.xml` **does not survive a reboot**.  
On startup, SystemUI queries ColorOS's RomUpdate provider (`content://com.oplus.romupdate.provider.db/update_list`). If no update record is found or its version is lower than the embedded asset (`1610260810`), SystemUI reverts to its stock XML asset and overwrites shared preferences.

By setting `version > 1610260810` (e.g. `2026102401`) and adding `lyricEntrance="52"`:
- SystemUI loads the configuration on boot.
- The policy persists across reboots and SystemUI restarts.

---

## 🛠️ Method 1: For Custom ROM Developers (Permanent ROM Integration)

If you are building a custom ColorOS / OxygenOS ROM (e.g., using CRB Kitchen or APKTool):

### 1. Locate the Configuration Asset
Inside your unpacked ROM:
```
system_ext/priv-app/SystemUI/SystemUI.apk
```
Open `SystemUI.apk` with 7-Zip, Archive Manager, or APKTool and navigate to:
```
assets/app_systemui_oplus_media_controller_config.xml
```
*(Files in `assets/` are raw plaintext XML, not binary-compiled resources).*

### 2. Add Your Music Player
Add your app package (e.g., `com.aman.auramusic`) into the two sections:

1. **Under `<whitelist>`:**
   ```xml
   <packageName name="com.heytap.music"/>
   <packageName name="com.aman.auramusic"/>
   ```

2. **Under `<policy>`:**
   ```xml
   <packageName name="com.heytap.music" actionPriority="1" actionPriorityQs="2" lyricEntrance="52"/>
   <packageName name="com.aman.auramusic" actionPriority="1" actionPriorityQs="2" lyricEntrance="52"/>
   ```

### 3. Unified Diff
```diff
--- a/assets/app_systemui_oplus_media_controller_config.xml
+++ b/assets/app_systemui_oplus_media_controller_config.xml
@@ -112,6 +112,7 @@
         <packageName name="com.tencent.qqmusic"/>
         <packageName name="com.netease.cloudmusic"/>
         <packageName name="com.heytap.music"/>
+        <packageName name="com.aman.auramusic"/>
         <packageName name="com.kugou.android"/>
         <packageName name="com.tencent.karaoke"/>
         <packageName name="cn.kuwo.player"/>
@@ -184,6 +185,7 @@
             oplusActionConfig='[{"key":"oplusLike"}]'
             lyricEntrance="52"/>
         <packageName name="com.heytap.music" actionPriority="1" actionPriorityQs="2" lyricEntrance="52"/>
+        <packageName name="com.aman.auramusic" actionPriority="1" actionPriorityQs="2" lyricEntrance="52"/>
         <packageName name="com.kugou.android" actionPriority="0" actionPriorityQs="2" oplusActionConfig='[{"key":"oplusLike"}]' lyricEntrance="52"/>
         <packageName name="com.kugou.android.lite" actionPriority="0" actionPriorityQs="0" oplusActionConfig='[{"key":"oplusLike"}]'
             lyricEntrance="52" lyricEnable="1"/>
```

Re-pack `SystemUI.apk` into your ROM image. The ROM will now support native lock-screen lyrics out-of-the-box on first boot without any user setup.

---

## ⚡ Method 2: For Rooted Users (KernelSU / Magisk / APatch)

If you are running an existing stock or custom ROM and have root access:

### Option A: Using the Automated Device Injector (Python)
1. Clone this repository:
   ```bash
   git clone https://github.com/dev-aman-hear/ColorOS-Lyric-Fixer.git
   cd ColorOS-Lyric-Fixer
   ```
2. Connect your device via USB with ADB debugging enabled.
3. Run the injector tool:
   ```bash
   python tools/inject_device.py -x examples/app_systemui_oplus_media_controller_config.patched.xml
   ```
The tool will automatically inject the configuration into `rom_update.db`, set correct permissions and SELinux contexts, and restart SystemUI.

---

### Option B: Using the Magisk / KernelSU Module
1. Zip the `magisk-module/` folder:
   ```bash
   cd magisk-module
   zip -r ../ColorOS-Lyric-Fixer.zip *
   ```
2. Flash `ColorOS-Lyric-Fixer.zip` in **KernelSU**, **Magisk**, or **APatch**.
3. Reboot. The module automatically protects and applies the configuration across device wipes and updates.

---

## 📱 For Music Player Developers: Sending Lyrics to ColorOS

If you are developing an Android music player, pass the `lyricInfo` JSON string to Android's standard `MediaMetadata`:

```kotlin
// 1. Build timestamped LRC text
val lrcContent = """
[00:12.30]First line of lyrics
[00:16.45]Second line of lyrics
""".trimIndent()

// 2. Build the JSON structure required by ColorOS
val lyricJson = JSONObject().apply {
    put("songName", currentTrack.title)
    put("artist", currentTrack.artist)
    put("songId", currentTrack.id.toString())
    put("lyric", lrcContent)
}.toString()

// 3. Put into MediaMetadata and update your MediaSession
val metadata = MediaMetadata.Builder()
    .putString(MediaMetadata.METADATA_KEY_TITLE, currentTrack.title)
    .putString(MediaMetadata.METADATA_KEY_ARTIST, currentTrack.artist)
    .putString("lyricInfo", lyricJson) // <-- ColorOS consumes this key
    .build()

mediaSession.setMetadata(metadata)
```

*(See [`examples/ColorOSLyricPayload.kt`](examples/ColorOSLyricPayload.kt) for a complete drop-in Kotlin utility).*

---

## 🧪 Verification Commands

To check if your package is currently authorized on the live device:

```bash
adb shell su -c "cat /data/user_de/0/com.android.systemui/shared_prefs/oplus_media_controller_config_sp.xml" | grep rus_lyric_entrance_key
```

You should see your package mapped to `"52"`:
```json
{"com.heytap.music":"52","com.aman.auramusic":"52", ...}
```

Check the live SystemUI media pipeline:
```bash
adb logcat -d | grep "MediaDataCombineLatest"
```
It should end with `,52` indicating that the entrance policy has been applied.

---

## 🤝 Contributing

Contributions, additional package requests, and PRs are welcome! Feel free to open an issue or pull request.

## 📄 License

Licensed under the [Apache License, Version 2.0](LICENSE).
