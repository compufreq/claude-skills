# Fastlane Android Reference

## Table of Contents
1. Appfile
2. Complete Fastfile
3. supply (Play Store)
4. screengrab (Screenshots)
5. Firebase App Distribution
6. Keystore Management

---

## 1. Appfile

```ruby
# fastlane/Appfile
json_key_file("path/to/play-store-key.json")  # Play Store service account
package_name("com.example.myapp")
```

### Play Store Service Account Setup
1. Go to Google Play Console → Settings → API access
2. Create a service account (or link existing)
3. Grant "Release manager" role
4. Download the JSON key file
5. Store as CI secret (base64-encoded)

---

## 2. Complete Fastfile (Android)

```ruby
default_platform(:android)

platform :android do

  # ── Testing ──────────────────────────────────────────

  desc "Run unit tests"
  lane :test do
    gradle(
      task: "test",
      build_type: "Debug",
    )
  end

  desc "Run lint checks"
  lane :lint do
    gradle(task: "lintDebug")
  end

  desc "Run all checks (lint + test)"
  lane :check do
    lint
    test
  end

  # ── Building ─────────────────────────────────────────

  desc "Build debug APK"
  lane :build_debug do
    gradle(
      task: "assembleDebug",
    )
  end

  desc "Build release AAB"
  lane :build_release do
    gradle(
      task: "bundleRelease",
      properties: {
        "android.injected.signing.store.file" => ENV["KEYSTORE_PATH"],
        "android.injected.signing.store.password" => ENV["KEYSTORE_PASSWORD"],
        "android.injected.signing.key.alias" => ENV["KEY_ALIAS"],
        "android.injected.signing.key.password" => ENV["KEY_PASSWORD"],
      },
    )
  end

  # ── Version Management ───────────────────────────────

  desc "Increment version code"
  lane :bump_version_code do
    # Read current, increment, write back
    path = "../app/build.gradle.kts"
    content = File.read(path)
    current = content.match(/versionCode\s*=\s*(\d+)/)[1].to_i
    new_code = current + 1
    content.gsub!(/versionCode\s*=\s*\d+/, "versionCode = #{new_code}")
    File.write(path, content)
    UI.success("Version code bumped to #{new_code}")
    new_code
  end

  # ── Distribution ─────────────────────────────────────

  desc "Upload to Play Store Internal Testing"
  lane :beta do
    bump_version_code
    build_release
    supply(
      track: "internal",
      aab: lane_context[SharedValues::GRADLE_AAB_OUTPUT_PATH],
      skip_upload_metadata: true,
      skip_upload_images: true,
      skip_upload_screenshots: true,
      release_status: "draft",
    )
    git_commit(
      path: ["./app/build.gradle.kts"],
      message: "ci: bump version code [skip ci]",
    )
    push_to_git_remote
  end

  desc "Promote internal to production"
  lane :release do
    supply(
      track: "internal",
      track_promote_to: "production",
      rollout: "0.1",  # 10% staged rollout
      skip_upload_aab: true,
      skip_upload_metadata: true,
    )
  end

  desc "Full release (build + deploy to production)"
  lane :full_release do
    bump_version_code
    build_release
    supply(
      track: "production",
      aab: lane_context[SharedValues::GRADLE_AAB_OUTPUT_PATH],
      rollout: "0.1",
      release_status: "inProgress",
    )
    version_name = gradle(task: "-q printVersionName").strip rescue "unknown"
    git_commit(
      path: ["./app/build.gradle.kts"],
      message: "ci: release v#{version_name} [skip ci]",
    )
    add_git_tag(tag: "android/v#{version_name}")
    push_to_git_remote(tags: true)
  end

  # ── Screenshots ──────────────────────────────────────

  desc "Generate Play Store screenshots"
  lane :screenshots do
    gradle(task: "assembleDebug", build_type: "Debug")
    gradle(task: "assembleAndroidTest", build_type: "Debug")
    screengrab(
      app_package_name: "com.example.myapp",
      app_apk_path: "app/build/outputs/apk/debug/app-debug.apk",
      tests_apk_path: "app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk",
      locales: ["en-US", "de-DE"],
      output_directory: "./fastlane/screenshots",
      clear_previous_screenshots: true,
      use_adb_root: false,
    )
  end

  desc "Upload metadata and screenshots to Play Store"
  lane :metadata do
    supply(
      skip_upload_aab: true,
      skip_upload_apk: true,
    )
  end

  # ── Firebase Distribution ────────────────────────────

  desc "Distribute debug build via Firebase"
  lane :firebase do
    build_debug
    firebase_app_distribution(
      app: ENV["FIREBASE_APP_ID_ANDROID"],
      android_artifact_type: "APK",
      android_artifact_path: "app/build/outputs/apk/debug/app-debug.apk",
      groups: "internal-testers",
      release_notes: changelog_from_git_commits(commits_count: 5),
    )
  end

  # ── Error Handling ───────────────────────────────────

  error do |lane, exception|
    slack(
      message: "🔴 Android #{lane} failed: #{exception.message}",
      slack_url: ENV["SLACK_WEBHOOK_URL"],
      success: false,
    ) if ENV["SLACK_WEBHOOK_URL"]
  end

  after_all do |lane|
    slack(
      message: "✅ Android #{lane} succeeded",
      slack_url: ENV["SLACK_WEBHOOK_URL"],
    ) if ENV["SLACK_WEBHOOK_URL"]
  end
end
```

---

## 3. supply (Play Store)

### Track Hierarchy
```
internal → alpha → beta → production
```

### Upload to Internal Testing
```ruby
supply(
  track: "internal",
  aab: "app/build/outputs/bundle/release/app-release.aab",
  release_status: "completed",  # or "draft"
  skip_upload_metadata: true,
  skip_upload_images: true,
)
```

### Staged Rollout
```ruby
# Start at 10%
supply(track: "production", rollout: "0.1", release_status: "inProgress")

# Increase to 50%
supply(track: "production", rollout: "0.5", release_status: "inProgress", skip_upload_aab: true)

# Full rollout
supply(track: "production", rollout: "1.0", release_status: "completed", skip_upload_aab: true)

# Halt rollout (emergency)
supply(track: "production", release_status: "halted", skip_upload_aab: true)
```

### Metadata Directory (Play Store)
```
fastlane/metadata/android/
├── en-US/
│   ├── title.txt                   # App name (50 chars)
│   ├── short_description.txt       # Short description (80 chars)
│   ├── full_description.txt        # Full description (4000 chars)
│   ├── changelogs/
│   │   └── default.txt             # Release notes (500 chars)
│   └── images/
│       ├── phoneScreenshots/       # Phone screenshots
│       ├── sevenInchScreenshots/   # 7" tablet
│       ├── tenInchScreenshots/     # 10" tablet
│       ├── featureGraphic.png      # 1024x500
│       └── icon.png                # 512x512
├── de-DE/
│   └── ...
```

---

## 4. screengrab (Screenshots)

### Screengrabfile
```ruby
# fastlane/Screengrabfile
app_package_name("com.example.myapp")
locales(["en-US", "de-DE", "ja-JP"])
output_directory("./fastlane/metadata/android")
clear_previous_screenshots(true)
use_timestamp_suffix(false)
```

### Instrumentation Test for Screenshots
```kotlin
// app/src/androidTest/java/com/example/screenshots/ScreenshotTest.kt
@RunWith(JUnit4::class)
class ScreenshotTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @get:Rule
    val localeRule = LocaleTestRule()

    @Test
    fun homeScreen() {
        Screengrab.screenshot("01_HomeScreen")
    }

    @Test
    fun searchResults() {
        onView(withId(R.id.searchField)).perform(typeText("coffee"))
        Thread.sleep(1000)
        Screengrab.screenshot("02_SearchResults")
    }

    @Test
    fun itemDetail() {
        onView(withId(R.id.recyclerView))
            .perform(RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(0, click()))
        Screengrab.screenshot("03_ItemDetail")
    }

    @Test
    fun settingsScreen() {
        onView(withContentDescription("Settings")).perform(click())
        Screengrab.screenshot("04_Settings")
    }
}
```

---

## 5. Firebase App Distribution

### Setup
```bash
# Install plugin
fastlane add_plugin firebase_app_distribution

# Authenticate (one-time)
firebase login:ci
# Save the token as FIREBASE_TOKEN in CI secrets
```

### Distribution with Testers
```ruby
firebase_app_distribution(
  app: "1:123456789:android:abcdef",
  android_artifact_type: "APK",
  android_artifact_path: "app/build/outputs/apk/debug/app-debug.apk",
  testers: "user1@example.com, user2@example.com",
  groups: "internal-testers, qa-team",
  release_notes: "Build #{lane_context[:BUILD_NUMBER]}\n#{changelog_from_git_commits(commits_count: 5)}",
  firebase_cli_token: ENV["FIREBASE_TOKEN"],
)
```

---

## 6. Keystore Management

### Creating a Keystore
```bash
keytool -genkey -v \
  -keystore release.keystore \
  -alias myapp \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass [password] \
  -keypass [password] \
  -dname "CN=MyApp, OU=Mobile, O=Example Inc, L=SF, ST=CA, C=US"
```

### Storing Keystore in CI
```bash
# Encode to base64
base64 -i release.keystore -o keystore.base64

# In CI pipeline, decode:
echo "$KEYSTORE_BASE64" | base64 --decode > release.keystore
```

### Gradle Signing from Environment
```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "../release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }
}
```



---
