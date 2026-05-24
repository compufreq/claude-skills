# Fastlane iOS Reference

## Table of Contents
1. Appfile & Matchfile
2. Complete Fastfile
3. match (Code Signing)
4. gym (Build)
5. pilot (TestFlight)
6. deliver (App Store)
7. snapshot (Screenshots)
8. Error Handling & Notifications

---

## 1. Appfile & Matchfile

### Appfile
```ruby
# fastlane/Appfile
app_identifier("com.example.myapp")
apple_id("developer@example.com")
team_id("ABCDE12345")
itc_team_id("123456789")  # App Store Connect team ID

# For multiple targets
for_platform :ios do
  for_lane :beta do
    app_identifier("com.example.myapp.beta")
  end
end
```

### Matchfile
```ruby
# fastlane/Matchfile
git_url("https://github.com/example/certificates.git")
storage_mode("git")  # or "s3", "google_cloud"
type("appstore")     # "development", "adhoc", "appstore", "enterprise"
app_identifier(["com.example.myapp"])
username("developer@example.com")
team_id("ABCDE12345")
```

---

## 2. Complete Fastfile (iOS)

```ruby
default_platform(:ios)

XCODEPROJ = "MyApp.xcodeproj"
SCHEME = "MyApp"
OUTPUT_DIR = "./build"

platform :ios do

  before_all do
    setup_ci if ENV['CI']
  end

  # ── Testing ──────────────────────────────────────────

  desc "Run unit and UI tests"
  lane :test do
    scan(
      scheme: SCHEME,
      devices: ["iPhone 16"],
      clean: true,
      code_coverage: true,
      output_directory: OUTPUT_DIR,
      result_bundle: true,
    )
  end

  desc "Run SwiftLint"
  lane :lint do
    swiftlint(
      mode: :lint,
      strict: true,
      reporter: "json",
      output_file: "#{OUTPUT_DIR}/swiftlint.json",
    )
  end

  # ── Code Signing ─────────────────────────────────────

  desc "Sync development certificates"
  lane :certs_dev do
    match(type: "development", readonly: is_ci)
  end

  desc "Sync App Store certificates"
  lane :certs_release do
    match(type: "appstore", readonly: is_ci)
  end

  # ── Building ─────────────────────────────────────────

  desc "Build debug"
  lane :build_debug do
    certs_dev
    gym(
      scheme: SCHEME,
      configuration: "Debug",
      export_method: "development",
      output_directory: OUTPUT_DIR,
      output_name: "MyApp-Debug.ipa",
    )
  end

  desc "Build release"
  lane :build_release do
    certs_release
    gym(
      scheme: SCHEME,
      configuration: "Release",
      export_method: "app-store",
      output_directory: OUTPUT_DIR,
      output_name: "MyApp-Release.ipa",
      include_bitcode: false,
      xcargs: "-allowProvisioningUpdates",
    )
  end

  # ── Distribution ─────────────────────────────────────

  desc "Upload to TestFlight"
  lane :beta do
    ensure_git_status_clean
    increment_build_number(xcodeproj: XCODEPROJ)
    build_release
    pilot(
      skip_waiting_for_build_processing: true,
      distribute_external: false,
      notify_external_testers: false,
      changelog: changelog_from_git_commits(
        commits_count: 10,
        merge_commit_filtering: :exclude_merges,
      ),
    )
    commit_version_bump(xcodeproj: XCODEPROJ, message: "ci: bump build number [skip ci]")
    push_to_git_remote
  end

  desc "Deploy to App Store"
  lane :release do
    ensure_git_status_clean
    increment_version_number(bump_type: "patch", xcodeproj: XCODEPROJ)
    increment_build_number(xcodeproj: XCODEPROJ)
    build_release
    deliver(
      submit_for_review: true,
      automatic_release: false,
      force: true,
      skip_screenshots: true,
      precheck_include_in_app_purchases: false,
      submission_information: {
        add_id_info_uses_idfa: false,
      },
    )
    version = get_version_number(xcodeproj: XCODEPROJ)
    commit_version_bump(xcodeproj: XCODEPROJ, message: "ci: release v#{version} [skip ci]")
    add_git_tag(tag: "ios/v#{version}")
    push_to_git_remote(tags: true)
  end

  # ── Screenshots ──────────────────────────────────────

  desc "Generate App Store screenshots"
  lane :screenshots do
    snapshot(
      devices: [
        "iPhone 16 Pro Max",
        "iPhone 16",
        "iPad Pro (13-inch) (M4)",
      ],
      languages: ["en-US"],
      scheme: "MyAppUITests",
      output_directory: "./fastlane/screenshots",
      clear_previous_screenshots: true,
      override_status_bar: true,
      dark_mode: false,
    )
    frame_screenshots(
      path: "./fastlane/screenshots",
      white: true,
    )
  end

  desc "Upload screenshots and metadata"
  lane :metadata do
    deliver(
      skip_binary_upload: true,
      skip_app_version_update: true,
      force: true,
      overwrite_screenshots: true,
    )
  end

  # ── Firebase Distribution ────────────────────────────

  desc "Distribute to Firebase"
  lane :firebase do
    build_debug
    firebase_app_distribution(
      app: ENV["FIREBASE_APP_ID_IOS"],
      ipa_path: "#{OUTPUT_DIR}/MyApp-Debug.ipa",
      groups: "internal-testers",
      release_notes: changelog_from_git_commits(commits_count: 5),
    )
  end

  # ── Error Handling ───────────────────────────────────

  error do |lane, exception|
    slack(
      message: "🔴 iOS #{lane} failed: #{exception.message}",
      slack_url: ENV["SLACK_WEBHOOK_URL"],
      success: false,
    ) if ENV["SLACK_WEBHOOK_URL"]
  end

  after_all do |lane|
    slack(
      message: "✅ iOS #{lane} succeeded",
      slack_url: ENV["SLACK_WEBHOOK_URL"],
    ) if ENV["SLACK_WEBHOOK_URL"]
  end
end
```

---

## 3. match (Code Signing)

### Initial Setup
```bash
# Create new certificates repo and generate certs
fastlane match init
fastlane match development
fastlane match appstore

# On CI, use readonly mode
fastlane match appstore --readonly
```

### App Store Connect API Key (recommended for CI)
```ruby
# Instead of Apple ID/password, use API key
app_store_connect_api_key(
  key_id: ENV["ASC_KEY_ID"],
  issuer_id: ENV["ASC_ISSUER_ID"],
  key_content: ENV["ASC_KEY_CONTENT"],  # Base64-encoded .p8 file
  is_key_content_base64: true,
)
```

### match on CI
```ruby
lane :setup_signing do
  # For GitHub Actions / GitLab CI
  create_keychain(
    name: "ci_keychain",
    password: ENV["KEYCHAIN_PASSWORD"],
    default_keychain: true,
    unlock: true,
    timeout: 3600,
  )
  match(
    type: "appstore",
    readonly: true,
    keychain_name: "ci_keychain",
    keychain_password: ENV["KEYCHAIN_PASSWORD"],
  )
end
```

---

## 4. gym (Build)

### Key Options
```ruby
gym(
  scheme: "MyApp",
  workspace: "MyApp.xcworkspace",    # If using CocoaPods
  # project: "MyApp.xcodeproj",      # If no workspace
  configuration: "Release",
  export_method: "app-store",        # development, ad-hoc, app-store, enterprise
  output_directory: "./build",
  output_name: "MyApp.ipa",
  clean: true,
  include_bitcode: false,
  export_options: {
    compileBitcode: false,
    uploadBitcode: false,
    uploadSymbols: true,
  },
)
```

---

## 5. pilot (TestFlight)

```ruby
pilot(
  ipa: "./build/MyApp.ipa",
  skip_waiting_for_build_processing: true,  # Don't wait (faster CI)
  distribute_external: true,
  groups: ["External Beta Testers"],
  notify_external_testers: true,
  changelog: "Bug fixes and improvements",
  beta_app_review_info: {
    contact_email: "beta@example.com",
    contact_first_name: "Test",
    contact_last_name: "User",
    contact_phone: "+1234567890",
  },
)
```

---

## 6. deliver (App Store)

### Deliverfile
```ruby
# fastlane/Deliverfile
app_identifier("com.example.myapp")
username("developer@example.com")
screenshots_path("./fastlane/screenshots")
metadata_path("./fastlane/metadata")
submit_for_review(false)
automatic_release(false)
force(true)  # Skip HTML preview
price_tier(0)  # Free
```

### Metadata Directory Structure
```
fastlane/metadata/
├── en-US/
│   ├── name.txt              # App name (30 chars)
│   ├── subtitle.txt          # Subtitle (30 chars)
│   ├── description.txt       # Full description (4000 chars)
│   ├── keywords.txt          # Keywords (100 chars, comma-separated)
│   ├── release_notes.txt     # What's New
│   ├── privacy_url.txt       # Privacy policy URL
│   ├── support_url.txt       # Support URL
│   ├── marketing_url.txt     # Marketing URL
│   └── promotional_text.txt  # Promotional text (170 chars)
├── de-DE/                    # German localization
│   └── ...
├── copyright.txt             # "2025 Example Inc"
├── primary_category.txt      # e.g., "MZGenre.Productivity"
└── review_information/
    ├── first_name.txt
    ├── last_name.txt
    ├── phone_number.txt
    ├── email_address.txt
    ├── demo_user.txt
    ├── demo_password.txt
    └── notes.txt
```

---

## 7. snapshot (Screenshots)

### Snapfile
```ruby
# fastlane/Snapfile
devices([
  "iPhone 16 Pro Max",
  "iPhone 16",
  "iPad Pro (13-inch) (M4)",
])
languages(["en-US", "de-DE", "ja"])
scheme("MyAppUITests")
output_directory("./fastlane/screenshots")
clear_previous_screenshots(true)
override_status_bar(true)
dark_mode(false)
number_of_retries(1)
stop_after_first_error(false)
```

### UI Test for Screenshots
```swift
import XCTest

class ScreenshotTests: XCTestCase {
    let app = XCUIApplication()

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        setupSnapshot(app)  // Fastlane snapshot helper
        app.launch()
    }

    func testHomeScreen() {
        snapshot("01_HomeScreen")
    }

    func testSearchResults() {
        app.searchFields["Search"].tap()
        app.searchFields["Search"].typeText("coffee")
        snapshot("02_SearchResults")
    }

    func testItemDetail() {
        app.cells.firstMatch.tap()
        snapshot("03_ItemDetail")
    }

    func testSettings() {
        app.tabBars.buttons["Settings"].tap()
        snapshot("04_Settings")
    }
}
```

---

## 8. Error Handling & Notifications

### Slack Notifications
```ruby
slack(
  message: "New iOS build uploaded to TestFlight!",
  slack_url: ENV["SLACK_WEBHOOK_URL"],
  channel: "#mobile-releases",
  payload: {
    "Build Number" => get_build_number(xcodeproj: XCODEPROJ),
    "Version" => get_version_number(xcodeproj: XCODEPROJ),
    "Git Branch" => git_branch,
  },
  default_payloads: [:git_branch, :last_git_commit],
)
```

### Retry Logic
```ruby
lane :beta_with_retry do
  retry_count = 0
  begin
    beta
  rescue => e
    retry_count += 1
    if retry_count <= 2
      UI.message("Retrying... (attempt #{retry_count + 1})")
      retry
    else
      raise e
    end
  end
end
```



---

<!-- Script: scripts/generate_ci_pipeline.py -->

# Script: generate_ci_pipeline.py

```python
#!/usr/bin/env python3
"""
Generate CI pipeline configurations for GitHub Actions or GitLab CI.

Usage:
    python generate_ci_pipeline.py --config project.json --provider github --platform both --output .
    python generate_ci_pipeline.py --config project.json --provider gitlab --platform ios --output .

Config JSON: Same as generate_fastlane.py
"""

import json
import sys
import os
import argparse


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def generate_github_ios(config):
    name = config.get("project_name", "MyApp")
    return f"""# .github/workflows/ios.yml
name: iOS CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: ios-${{{{ github.ref }}}}
  cancel-in-progress: true

env:
  FASTLANE_SKIP_UPDATE_CHECK: "true"

jobs:
  test:
    name: Test
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4

      - name: Cache SPM
        uses: actions/cache@v4
        with:
          path: ~/Library/Developer/Xcode/DerivedData
          key: spm-${{{{ hashFiles('**/Package.resolved') }}}}
          restore-keys: spm-

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Run tests
        run: bundle exec fastlane test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: ios-test-results
          path: build/

  beta:
    name: Deploy to TestFlight
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{{{ secrets.GH_PAT }}}}

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Deploy to TestFlight
        env:
          MATCH_PASSWORD: ${{{{ secrets.MATCH_PASSWORD }}}}
          MATCH_GIT_URL: ${{{{ secrets.MATCH_GIT_URL }}}}
          MATCH_GIT_BASIC_AUTHORIZATION: ${{{{ secrets.MATCH_GIT_AUTH }}}}
          ASC_KEY_ID: ${{{{ secrets.ASC_KEY_ID }}}}
          ASC_ISSUER_ID: ${{{{ secrets.ASC_ISSUER_ID }}}}
          ASC_KEY_CONTENT: ${{{{ secrets.ASC_KEY_CONTENT }}}}
          KEYCHAIN_PASSWORD: ${{{{ secrets.KEYCHAIN_PASSWORD }}}}
          SLACK_WEBHOOK_URL: ${{{{ secrets.SLACK_WEBHOOK_URL }}}}
        run: bundle exec fastlane beta

      - name: Upload IPA
        uses: actions/upload-artifact@v4
        with:
          name: ios-beta-ipa
          path: build/*.ipa
          retention-days: 30

  release:
    name: Deploy to App Store
    needs: test
    if: startsWith(github.ref, 'refs/tags/ios/v')
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{{{ secrets.GH_PAT }}}}

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Deploy to App Store
        env:
          MATCH_PASSWORD: ${{{{ secrets.MATCH_PASSWORD }}}}
          MATCH_GIT_URL: ${{{{ secrets.MATCH_GIT_URL }}}}
          MATCH_GIT_BASIC_AUTHORIZATION: ${{{{ secrets.MATCH_GIT_AUTH }}}}
          ASC_KEY_ID: ${{{{ secrets.ASC_KEY_ID }}}}
          ASC_ISSUER_ID: ${{{{ secrets.ASC_ISSUER_ID }}}}
          ASC_KEY_CONTENT: ${{{{ secrets.ASC_KEY_CONTENT }}}}
          KEYCHAIN_PASSWORD: ${{{{ secrets.KEYCHAIN_PASSWORD }}}}
        run: bundle exec fastlane release
"""


def generate_github_android(config):
    return f"""# .github/workflows/android.yml
name: Android CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: android-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{{{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties', '**/libs.versions.toml') }}}}
          restore-keys: gradle-

      - name: Run lint
        run: ./gradlew lintDebug

      - name: Run tests
        run: ./gradlew testDebugUnitTest

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: android-test-reports
          path: app/build/reports/

  beta:
    name: Deploy to Internal Testing
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{{{ secrets.GH_PAT }}}}

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{{{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}}}

      - name: Decode keystore
        run: echo "${{{{ secrets.KEYSTORE_BASE64 }}}}" | base64 --decode > release.keystore

      - name: Create Play Store key
        run: echo "${{{{ secrets.PLAY_STORE_JSON_KEY }}}}" | base64 --decode > play-store-key.json

      - name: Deploy to Internal Testing
        env:
          KEYSTORE_PATH: ${{{{ github.workspace }}}}/release.keystore
          KEYSTORE_PASSWORD: ${{{{ secrets.KEYSTORE_PASSWORD }}}}
          KEY_ALIAS: ${{{{ secrets.KEY_ALIAS }}}}
          KEY_PASSWORD: ${{{{ secrets.KEY_PASSWORD }}}}
          SLACK_WEBHOOK_URL: ${{{{ secrets.SLACK_WEBHOOK_URL }}}}
        run: bundle exec fastlane android beta

      - name: Upload AAB
        uses: actions/upload-artifact@v4
        with:
          name: android-beta-aab
          path: app/build/outputs/bundle/release/*.aab
          retention-days: 30

  release:
    name: Deploy to Production
    needs: test
    if: startsWith(github.ref, 'refs/tags/android/v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Decode keystore
        run: echo "${{{{ secrets.KEYSTORE_BASE64 }}}}" | base64 --decode > release.keystore

      - name: Create Play Store key
        run: echo "${{{{ secrets.PLAY_STORE_JSON_KEY }}}}" | base64 --decode > play-store-key.json

      - name: Deploy to Production
        env:
          KEYSTORE_PATH: ${{{{ github.workspace }}}}/release.keystore
          KEYSTORE_PASSWORD: ${{{{ secrets.KEYSTORE_PASSWORD }}}}
          KEY_ALIAS: ${{{{ secrets.KEY_ALIAS }}}}
          KEY_PASSWORD: ${{{{ secrets.KEY_PASSWORD }}}}
        run: bundle exec fastlane android release
"""


def generate_gitlab_ios(config):
    return """# iOS stages for .gitlab-ci.yml
stages:
  - test
  - deploy

variables:
  FASTLANE_SKIP_UPDATE_CHECK: "true"

.ios-base:
  tags: [macos, xcode16]
  before_script:
    - bundle install --path vendor/bundle
  cache:
    key: ios-${CI_COMMIT_REF_SLUG}
    paths:
      - vendor/bundle

ios:test:
  extends: .ios-base
  stage: test
  script:
    - bundle exec fastlane test
  artifacts:
    when: always
    paths: [build/]
    expire_in: 7 days
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_BRANCH == "develop"'

ios:beta:
  extends: .ios-base
  stage: deploy
  script:
    - bundle exec fastlane beta
  environment:
    name: ios-testflight
  artifacts:
    paths: [build/*.ipa]
    expire_in: 30 days
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

ios:release:
  extends: .ios-base
  stage: deploy
  script:
    - bundle exec fastlane release
  environment:
    name: ios-appstore
  rules:
    - if: '$CI_COMMIT_TAG =~ /^ios\\/v\\d+/'
      when: manual
"""


def generate_gitlab_android(config):
    return """# Android stages for .gitlab-ci.yml
.android-base:
  image: cimg/android:2024.10
  before_script:
    - bundle install --path vendor/bundle
  cache:
    key: android-${CI_COMMIT_REF_SLUG}
    paths:
      - vendor/bundle
      - .gradle/

android:test:
  extends: .android-base
  stage: test
  script:
    - ./gradlew lintDebug testDebugUnitTest
  artifacts:
    when: always
    paths: [app/build/reports/]
    expire_in: 7 days
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

android:beta:
  extends: .android-base
  stage: deploy
  script:
    - echo "$KEYSTORE_BASE64" | base64 -d > release.keystore
    - echo "$PLAY_STORE_JSON_KEY" | base64 -d > play-store-key.json
    - bundle exec fastlane android beta
  environment:
    name: android-internal
  artifacts:
    paths: [app/build/outputs/bundle/release/*.aab]
    expire_in: 30 days
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

android:release:
  extends: .android-base
  stage: deploy
  script:
    - echo "$KEYSTORE_BASE64" | base64 -d > release.keystore
    - echo "$PLAY_STORE_JSON_KEY" | base64 -d > play-store-key.json
    - bundle exec fastlane android release
  environment:
    name: android-production
  rules:
    - if: '$CI_COMMIT_TAG =~ /^android\\/v\\d+/'
      when: manual
"""


def generate_secrets_checklist(config, platform, provider):
    """Generate a secrets setup checklist."""
    secrets = []

    if platform in ("ios", "both"):
        secrets.extend([
            ("MATCH_PASSWORD", "Encryption password for certificates repo"),
            ("MATCH_GIT_URL", "Git URL of certificates repository"),
            ("MATCH_GIT_AUTH", "Base64-encoded username:token for Git auth"),
            ("ASC_KEY_ID", "App Store Connect API Key ID"),
            ("ASC_ISSUER_ID", "App Store Connect Issuer ID"),
            ("ASC_KEY_CONTENT", "Base64-encoded .p8 key content"),
            ("KEYCHAIN_PASSWORD", "Temporary CI keychain password"),
        ])

    if platform in ("android", "both"):
        secrets.extend([
            ("KEYSTORE_BASE64", "Base64-encoded release keystore"),
            ("KEYSTORE_PASSWORD", "Keystore password"),
            ("KEY_ALIAS", "Key alias in keystore"),
            ("KEY_PASSWORD", "Key password"),
            ("PLAY_STORE_JSON_KEY", "Base64-encoded Play Store service account JSON"),
        ])

    if config.get("firebase_app_id_ios") or config.get("firebase_app_id_android"):
        secrets.append(("FIREBASE_TOKEN", "Firebase CLI token for app distribution"))

    if config.get("slack_webhook"):
        secrets.append(("SLACK_WEBHOOK_URL", "Slack webhook for build notifications"))

    secrets.append(("GH_PAT", "GitHub Personal Access Token (for pushing version bumps)"))

    where = "GitHub → Settings → Secrets → Actions" if provider == "github" else "GitLab → Settings → CI/CD → Variables"

    content = f"""# CI/CD Secrets Checklist — {config.get("project_name", "Project")}
## Provider: {provider.title()}
## Platform: {platform}

### Where to add: {where}

| Secret | Description | Added? |
|--------|------------|--------|
"""
    for name, desc in secrets:
        content += f"| `{name}` | {desc} | ☐ |\n"

    content += f"""
### How to generate:

#### iOS Secrets
1. **ASC API Key**: App Store Connect → Users → Keys → Generate
2. **match**: Run `fastlane match init` locally, note the password
3. **Keychain**: Generate a random password for CI keychain

#### Android Secrets
1. **Keystore**: `keytool -genkey -v -keystore release.keystore ...`
2. **Base64 encode**: `base64 -i release.keystore | tr -d '\\n'`
3. **Play Store key**: Play Console → Settings → API access → Service account → JSON key
4. **Base64 encode**: `base64 -i play-store-key.json | tr -d '\\n'`
"""
    return content


def generate_pipeline(config, provider, platform, output_dir):
    print(f"\n🔧 Generating {provider.title()} CI for {platform}\n")

    if provider == "github":
        if platform in ("ios", "both"):
            path = os.path.join(output_dir, ".github", "workflows", "ios.yml")
            create_file(path, generate_github_ios(config))
        if platform in ("android", "both"):
            path = os.path.join(output_dir, ".github", "workflows", "android.yml")
            create_file(path, generate_github_android(config))
    elif provider == "gitlab":
        content = ""
        if platform in ("ios", "both"):
            content += generate_gitlab_ios(config)
        if platform in ("android", "both"):
            content += "\n" + generate_gitlab_android(config)
        create_file(os.path.join(output_dir, ".gitlab-ci.yml"), content)

    # Secrets checklist
    checklist = generate_secrets_checklist(config, platform, provider)
    create_file(os.path.join(output_dir, "CI_SECRETS_CHECKLIST.md"), checklist)

    print(f"\n✅ CI pipeline generated for {provider.title()} ({platform})")
    print(f"   Don't forget to set up secrets — see CI_SECRETS_CHECKLIST.md")


def main():
    parser = argparse.ArgumentParser(description="Generate CI Pipeline Configuration")
    parser.add_argument("--config", help="JSON config path")
    parser.add_argument("--provider", choices=["github", "gitlab"], default="github")
    parser.add_argument("--platform", choices=["ios", "android", "both"], default="both")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    generate_pipeline(config, args.provider, args.platform, args.output)


if __name__ == "__main__":
    main()

```


---

<!-- Script: scripts/generate_fastlane.py -->

# Script: generate_fastlane.py

```python
#!/usr/bin/env python3
"""
Generate complete Fastlane configuration for iOS, Android, or both.

Usage:
    python generate_fastlane.py --config project.json --platform ios --output ./fastlane
    python generate_fastlane.py --config project.json --platform android --output ./fastlane
    python generate_fastlane.py --config project.json --platform both --output ./fastlane

Config JSON:
{
    "project_name": "MyApp",
    "bundle_id": "com.example.myapp",
    "apple_id": "developer@example.com",
    "team_id": "ABCDE12345",
    "itc_team_id": "123456789",
    "match_git_url": "https://github.com/example/certs.git",
    "scheme": "MyApp",
    "xcodeproj": "MyApp.xcodeproj",
    "workspace": null,
    "android_package": "com.example.myapp",
    "play_store_json": "play-store-key.json",
    "firebase_app_id_ios": "1:123:ios:abc",
    "firebase_app_id_android": "1:123:android:def",
    "slack_webhook": true,
    "screenshots": true,
    "metadata": true
}
"""

import json
import sys
import os
import argparse


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def generate_gemfile(output_dir):
    content = """source "https://rubygems.org"

gem "fastlane"

plugins_path = File.join(File.dirname(__FILE__), 'fastlane', 'Pluginfile')
eval_gemfile(plugins_path) if File.exist?(plugins_path)
"""
    create_file(os.path.join(output_dir, "Gemfile"), content)


def generate_pluginfile(config, output_dir):
    plugins = []
    if config.get("firebase_app_id_ios") or config.get("firebase_app_id_android"):
        plugins.append('gem "fastlane-plugin-firebase_app_distribution"')
    content = "# Autogenerated by fastlane\n\n" + "\n".join(plugins) + "\n"
    create_file(os.path.join(output_dir, "fastlane", "Pluginfile"), content)


def generate_ios_appfile(config, output_dir):
    content = f"""app_identifier("{config.get("bundle_id", "com.example.myapp")}")
apple_id("{config.get("apple_id", "developer@example.com")}")
team_id("{config.get("team_id", "REPLACE_ME")}")
itc_team_id("{config.get("itc_team_id", "REPLACE_ME")}")
"""
    create_file(os.path.join(output_dir, "fastlane", "Appfile"), content)


def generate_ios_matchfile(config, output_dir):
    content = f"""git_url("{config.get("match_git_url", "https://github.com/example/certs.git")}")
storage_mode("git")
type("appstore")
app_identifier(["{config.get("bundle_id", "com.example.myapp")}"])
username("{config.get("apple_id", "developer@example.com")}")
team_id("{config.get("team_id", "REPLACE_ME")}")
"""
    create_file(os.path.join(output_dir, "fastlane", "Matchfile"), content)


def generate_ios_fastfile(config, output_dir):
    name = config.get("project_name", "MyApp")
    scheme = config.get("scheme", name)
    xcodeproj = config.get("xcodeproj", f"{name}.xcodeproj")
    workspace = config.get("workspace")
    build_target = f'workspace: "{workspace}"' if workspace else f'project: "{xcodeproj}"'

    slack_error = ""
    slack_success = ""
    if config.get("slack_webhook"):
        slack_error = '''
  error do |lane, exception|
    slack(message: "🔴 iOS #{lane} failed: #{exception.message}", slack_url: ENV["SLACK_WEBHOOK_URL"], success: false) if ENV["SLACK_WEBHOOK_URL"]
  end'''
        slack_success = '''
  after_all do |lane|
    slack(message: "✅ iOS #{lane} succeeded", slack_url: ENV["SLACK_WEBHOOK_URL"]) if ENV["SLACK_WEBHOOK_URL"]
  end'''

    screenshot_lane = ""
    if config.get("screenshots"):
        screenshot_lane = f'''
  desc "Generate App Store screenshots"
  lane :screenshots do
    snapshot(
      devices: ["iPhone 16 Pro Max", "iPhone 16"],
      languages: ["en-US"],
      scheme: "{scheme}UITests",
      output_directory: "./fastlane/screenshots",
      clear_previous_screenshots: true,
      override_status_bar: true,
    )
    frame_screenshots(path: "./fastlane/screenshots", white: true)
  end
'''

    metadata_lane = ""
    if config.get("metadata"):
        metadata_lane = '''
  desc "Upload metadata and screenshots"
  lane :metadata do
    deliver(skip_binary_upload: true, force: true, overwrite_screenshots: true)
  end
'''

    firebase_lane = ""
    if config.get("firebase_app_id_ios"):
        firebase_lane = f'''
  desc "Distribute to Firebase"
  lane :firebase do
    build_debug
    firebase_app_distribution(
      app: ENV["FIREBASE_APP_ID_IOS"],
      ipa_path: "./build/{name}-Debug.ipa",
      groups: "internal-testers",
      release_notes: changelog_from_git_commits(commits_count: 5),
    )
  end
'''

    content = f'''default_platform(:ios)

XCODEPROJ = "{xcodeproj}"
SCHEME = "{scheme}"
OUTPUT_DIR = "./build"

platform :ios do
  before_all do
    setup_ci if ENV["CI"]
  end

  desc "Run tests"
  lane :test do
    scan(scheme: SCHEME, devices: ["iPhone 16"], clean: true, code_coverage: true, output_directory: OUTPUT_DIR)
  end

  desc "Sync certificates"
  lane :certs do
    app_store_connect_api_key(
      key_id: ENV["ASC_KEY_ID"],
      issuer_id: ENV["ASC_ISSUER_ID"],
      key_content: ENV["ASC_KEY_CONTENT"],
      is_key_content_base64: true,
    ) if ENV["ASC_KEY_ID"]
    create_keychain(name: "ci_keychain", password: ENV["KEYCHAIN_PASSWORD"], default_keychain: true, unlock: true, timeout: 3600) if ENV["CI"]
    match(type: "appstore", readonly: is_ci, keychain_name: ENV["CI"] ? "ci_keychain" : nil, keychain_password: ENV["KEYCHAIN_PASSWORD"])
  end

  desc "Build debug"
  lane :build_debug do
    match(type: "development", readonly: is_ci)
    gym(scheme: SCHEME, configuration: "Debug", export_method: "development", output_directory: OUTPUT_DIR, output_name: "{name}-Debug.ipa")
  end

  desc "Build release"
  lane :build_release do
    certs
    gym(scheme: SCHEME, configuration: "Release", export_method: "app-store", output_directory: OUTPUT_DIR, output_name: "{name}-Release.ipa", include_bitcode: false)
  end

  desc "Deploy beta to TestFlight"
  lane :beta do
    ensure_git_status_clean
    increment_build_number(xcodeproj: XCODEPROJ)
    build_release
    pilot(skip_waiting_for_build_processing: true, distribute_external: false, changelog: changelog_from_git_commits(commits_count: 10, merge_commit_filtering: :exclude_merges))
    commit_version_bump(xcodeproj: XCODEPROJ, message: "ci: bump build number [skip ci]")
    push_to_git_remote
  end

  desc "Deploy to App Store"
  lane :release do
    ensure_git_status_clean
    increment_version_number(bump_type: "patch", xcodeproj: XCODEPROJ)
    increment_build_number(xcodeproj: XCODEPROJ)
    build_release
    deliver(submit_for_review: true, automatic_release: false, force: true, skip_screenshots: true)
    version = get_version_number(xcodeproj: XCODEPROJ)
    commit_version_bump(xcodeproj: XCODEPROJ, message: "ci: release v#{{version}} [skip ci]")
    add_git_tag(tag: "ios/v#{{version}}")
    push_to_git_remote(tags: true)
  end
{screenshot_lane}{metadata_lane}{firebase_lane}{slack_error}{slack_success}
end
'''
    create_file(os.path.join(output_dir, "fastlane", "Fastfile"), content)


def generate_android_fastfile(config, output_dir):
    name = config.get("project_name", "MyApp")

    slack_error = ""
    slack_success = ""
    if config.get("slack_webhook"):
        slack_error = '''
  error do |lane, exception|
    slack(message: "🔴 Android #{lane} failed: #{exception.message}", slack_url: ENV["SLACK_WEBHOOK_URL"], success: false) if ENV["SLACK_WEBHOOK_URL"]
  end'''
        slack_success = '''
  after_all do |lane|
    slack(message: "✅ Android #{lane} succeeded", slack_url: ENV["SLACK_WEBHOOK_URL"]) if ENV["SLACK_WEBHOOK_URL"]
  end'''

    screenshot_lane = ""
    if config.get("screenshots"):
        screenshot_lane = f'''
  desc "Generate Play Store screenshots"
  lane :screenshots do
    gradle(task: "assembleDebug")
    gradle(task: "assembleAndroidTest")
    screengrab(
      app_package_name: "{config.get("android_package", config.get("bundle_id", "com.example.myapp"))}",
      locales: ["en-US"],
      output_directory: "./fastlane/screenshots",
      clear_previous_screenshots: true,
    )
  end
'''

    firebase_lane = ""
    if config.get("firebase_app_id_android"):
        firebase_lane = '''
  desc "Distribute to Firebase"
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
'''

    content = f'''default_platform(:android)

platform :android do

  desc "Run tests"
  lane :test do
    gradle(task: "testDebugUnitTest")
  end

  desc "Run lint"
  lane :lint do
    gradle(task: "lintDebug")
  end

  desc "Build debug APK"
  lane :build_debug do
    gradle(task: "assembleDebug")
  end

  desc "Build release AAB"
  lane :build_release do
    gradle(
      task: "bundleRelease",
      properties: {{
        "android.injected.signing.store.file" => ENV["KEYSTORE_PATH"],
        "android.injected.signing.store.password" => ENV["KEYSTORE_PASSWORD"],
        "android.injected.signing.key.alias" => ENV["KEY_ALIAS"],
        "android.injected.signing.key.password" => ENV["KEY_PASSWORD"],
      }},
    )
  end

  desc "Deploy to Play Store Internal Testing"
  lane :beta do
    build_release
    supply(
      track: "internal",
      aab: lane_context[SharedValues::GRADLE_AAB_OUTPUT_PATH],
      skip_upload_metadata: true,
      skip_upload_images: true,
      skip_upload_screenshots: true,
    )
  end

  desc "Deploy to Play Store Production (staged)"
  lane :release do
    build_release
    supply(
      track: "production",
      aab: lane_context[SharedValues::GRADLE_AAB_OUTPUT_PATH],
      rollout: "0.1",
      release_status: "inProgress",
    )
  end
{screenshot_lane}{firebase_lane}{slack_error}{slack_success}
end
'''
    # If both platforms, append to existing Fastfile
    fastfile_path = os.path.join(output_dir, "fastlane", "Fastfile")
    if os.path.exists(fastfile_path):
        with open(fastfile_path, "a") as f:
            f.write("\n" + content)
        print(f"  Appended Android lanes to: {fastfile_path}")
    else:
        create_file(fastfile_path, content)


def generate_android_appfile(config, output_dir):
    appfile_path = os.path.join(output_dir, "fastlane", "Appfile")
    content = f'\njson_key_file("{config.get("play_store_json", "play-store-key.json")}")\n'
    content += f'package_name("{config.get("android_package", config.get("bundle_id", "com.example.myapp"))}")\n'

    if os.path.exists(appfile_path):
        with open(appfile_path, "a") as f:
            f.write(content)
        print(f"  Appended Android config to: {appfile_path}")
    else:
        create_file(appfile_path, content)


def generate_metadata_dirs(config, output_dir, platform):
    """Create metadata directory structure with placeholder files."""
    name = config.get("project_name", "MyApp")
    if platform in ("ios", "both"):
        base = os.path.join(output_dir, "fastlane", "metadata", "en-US")
        files = {
            "name.txt": name,
            "subtitle.txt": f"{name} — Your tagline here",
            "description.txt": f"Description of {name}.\n\nKey features:\n- Feature 1\n- Feature 2\n- Feature 3",
            "keywords.txt": "keyword1,keyword2,keyword3",
            "release_notes.txt": "What's new in this version:\n- Bug fixes and improvements",
            "privacy_url.txt": "https://example.com/privacy",
            "support_url.txt": "https://example.com/support",
            "promotional_text.txt": f"Try {name} today!",
        }
        for fname, content in files.items():
            create_file(os.path.join(base, fname), content)

    if platform in ("android", "both"):
        base = os.path.join(output_dir, "fastlane", "metadata", "android", "en-US")
        files = {
            "title.txt": name,
            "short_description.txt": f"{name} — Your short description here",
            "full_description.txt": f"Full description of {name}.\n\nKey features:\n- Feature 1\n- Feature 2",
        }
        for fname, content in files.items():
            create_file(os.path.join(base, fname), content)
        create_file(os.path.join(base, "changelogs", "default.txt"), "Bug fixes and improvements")


def scaffold_fastlane(config, platform, output_dir):
    print(f"\n⚡ Generating Fastlane config for {platform}\n")

    generate_gemfile(output_dir)
    generate_pluginfile(config, output_dir)

    if platform in ("ios", "both"):
        generate_ios_appfile(config, output_dir)
        generate_ios_matchfile(config, output_dir)
        generate_ios_fastfile(config, output_dir)

    if platform in ("android", "both"):
        generate_android_appfile(config, output_dir)
        generate_android_fastfile(config, output_dir)

    if config.get("metadata"):
        generate_metadata_dirs(config, output_dir, platform)

    print(f"\n✅ Fastlane configuration generated at: {output_dir}/fastlane/")
    print(f"   Platform: {platform}")
    print(f"   Next steps:")
    print(f"   1. cd {output_dir} && bundle install")
    print(f"   2. Review and customize fastlane/Fastfile")
    print(f"   3. Set up CI secrets (see references/code-signing.md)")


def main():
    parser = argparse.ArgumentParser(description="Generate Fastlane Configuration")
    parser.add_argument("--config", help="JSON config path")
    parser.add_argument("--platform", choices=["ios", "android", "both"], default="both")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    scaffold_fastlane(config, args.platform, args.output)


if __name__ == "__main__":
    main()

```
