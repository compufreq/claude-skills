---
name: mobile-ci-cd
description: >-
  Mobile CI/CD with Fastlane, code signing, and app store deployment. Use when the user mentions mobile CI/CD, Fastlane, fastlane match, code signing, provisioning profiles, Bitrise, GitHub Actions for mobile, Codemagic, App Store Connect API, Google Play publishing, TestFlight, beta distribution, mobile build pipeline, or automating mobile app builds, testing, and store submissions.
---

# Mobile CI/CD

A production-grade skill for automating mobile app builds, signing, testing, screenshots, and
distribution across iOS and Android using Fastlane, GitHub Actions, and GitLab CI.

## Quick Reference

| Area | Tools | Reference File |
|------|-------|----------------|
| Fastlane (iOS) | match, gym, pilot, deliver, snapshot | `references/fastlane-ios.md` |
| Fastlane (Android) | gradle, supply, screengrab | `references/fastlane-android.md` |
| CI Pipelines | GitHub Actions, GitLab CI | `references/ci-pipelines.md` |
| Code Signing | match, cert, sigh, keystore management | `references/code-signing.md` |

## Core Workflow

1. **Identify the platform** — iOS, Android, or both?
2. **Identify the CI provider** — GitHub Actions or GitLab CI?
3. **Read relevant references:**
   - iOS Fastlane → `references/fastlane-ios.md`
   - Android Fastlane → `references/fastlane-android.md`
   - CI pipelines → `references/ci-pipelines.md`
   - Signing → `references/code-signing.md`
4. **Generate configuration** using the scripts in this skill.

---

## Pipeline Architecture

### Standard Mobile CI/CD Pipeline

```
Push/PR → Lint + Unit Tests → Build → Sign → Distribute
              ↓                  ↓        ↓
          Code quality       Screenshots  TestFlight / Firebase
          Static analysis    UI Tests     Play Internal Testing
```

### Pipeline Stages

| Stage | Trigger | iOS | Android |
|-------|---------|-----|---------|
| **Lint & Test** | Every PR | SwiftLint + XCTest | ktlint + JUnit |
| **Build Debug** | Every PR | `xcodebuild` (Debug) | `./gradlew assembleDebug` |
| **Build Release** | Merge to main | `gym` (Release) | `./gradlew bundleRelease` |
| **Sign** | Release build | `match` + `gym` | Keystore signing |
| **Screenshots** | Release/manual | `snapshot` | `screengrab` |
| **Beta Deploy** | Merge to main | `pilot` (TestFlight) | `supply` / Firebase |
| **Prod Deploy** | Tag/manual | `deliver` | `supply --track production` |
| **Store Metadata** | Manual/release | `deliver` | `supply` |

### Environment Variables (Secrets)

| Secret | iOS | Android | Where |
|--------|-----|---------|-------|
| Signing cert | `MATCH_PASSWORD`, `MATCH_GIT_URL` | `KEYSTORE_BASE64`, `KEYSTORE_PASSWORD` | CI secrets |
| Store credentials | `APP_STORE_CONNECT_API_KEY` | `PLAY_STORE_JSON_KEY` | CI secrets |
| Firebase | `FIREBASE_TOKEN` | `FIREBASE_TOKEN` | CI secrets |
| Code signing | `APPLE_ID`, `TEAM_ID` | `KEY_ALIAS`, `KEY_PASSWORD` | CI secrets |

---

## Fastlane Overview

### Directory Structure
```
project/
├── fastlane/
│   ├── Fastfile              # Lane definitions
│   ├── Appfile               # App identifiers
│   ├── Matchfile             # Code signing config (iOS)
│   ├── Deliverfile           # App Store metadata config (iOS)
│   ├── Pluginfile            # Fastlane plugins
│   ├── metadata/             # Store metadata (deliver/supply)
│   │   ├── en-US/
│   │   │   ├── title.txt
│   │   │   ├── subtitle.txt
│   │   │   ├── description.txt
│   │   │   ├── keywords.txt
│   │   │   ├── release_notes.txt
│   │   │   └── privacy_url.txt
│   │   └── default/
│   │       └── review_information/
│   ├── screenshots/          # Auto-generated screenshots
│   │   ├── en-US/
│   │   └── de-DE/
│   └── report.xml            # Build reports
├── Gemfile                   # Ruby dependencies
└── Gemfile.lock
```

### Installation
```bash
# macOS (recommended)
brew install fastlane

# Ruby (any platform)
gem install fastlane

# Bundler (CI recommended)
echo 'gem "fastlane"' > Gemfile
bundle install
bundle exec fastlane [lane]
```

---

## Common Lanes

### iOS Lanes Summary
```ruby
# Fastfile
default_platform(:ios)

platform :ios do
  desc "Run tests"
  lane :test do ... end

  desc "Build and distribute beta to TestFlight"
  lane :beta do ... end

  desc "Deploy to App Store"
  lane :release do ... end

  desc "Generate screenshots"
  lane :screenshots do ... end

  desc "Sync certificates"
  lane :certs do ... end
end
```

### Android Lanes Summary
```ruby
default_platform(:android)

platform :android do
  desc "Run tests"
  lane :test do ... end

  desc "Build and distribute beta"
  lane :beta do ... end

  desc "Deploy to Play Store"
  lane :release do ... end

  desc "Generate screenshots"
  lane :screenshots do ... end
end
```

---

## Scripts

### generate_fastlane.py
Generates complete Fastlane configuration for iOS, Android, or both.

```bash
python scripts/generate_fastlane.py \
  --config project.json \
  --platform ios|android|both \
  --output ./fastlane
```

### generate_ci_pipeline.py
Generates CI pipeline configuration for GitHub Actions or GitLab CI.

```bash
python scripts/generate_ci_pipeline.py \
  --config project.json \
  --provider github|gitlab \
  --platform ios|android|both \
  --output .
```

---

## Best Practices

1. **Never store secrets in code** — use CI secret variables, never commit keystores or API keys
2. **Use `match` for iOS signing** — centralized, automated, team-friendly
3. **Pin Fastlane version** in Gemfile — avoid CI failures from version changes
4. **Cache dependencies** — CocoaPods/SPM on iOS, Gradle on Android
5. **Separate test and release builds** — tests run on every PR, releases only on merge/tag
6. **Automate everything repeatable** — if you do it twice, automate it
7. **Screenshots on every release** — catches UI regressions in store listings
8. **Version bump automation** — use Fastlane `increment_build_number` / version code
9. **Slack/Teams notifications** — notify on build success/failure
10. **Artifact retention** — keep release builds for 90 days minimum



---
