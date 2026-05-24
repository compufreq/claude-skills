# CI Pipeline Reference

## Table of Contents
1. GitHub Actions — iOS
2. GitHub Actions — Android
3. GitLab CI — iOS
4. GitLab CI — Android
5. Caching Strategies
6. Pipeline Optimization

---

## 1. GitHub Actions — iOS

### Complete iOS Workflow
```yaml
# .github/workflows/ios.yml
name: iOS CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: ios-${{ github.ref }}
  cancel-in-progress: true

env:
  DEVELOPER_DIR: /Applications/Xcode_16.0.app/Contents/Developer
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
          path: |
            ~/Library/Developer/Xcode/DerivedData
            .build
          key: spm-${{ hashFiles('**/Package.resolved') }}
          restore-keys: spm-

      - name: Cache CocoaPods
        if: hashFiles('Podfile.lock') != ''
        uses: actions/cache@v4
        with:
          path: Pods
          key: pods-${{ hashFiles('Podfile.lock') }}

      - name: Install CocoaPods
        if: hashFiles('Podfile.lock') != ''
        run: pod install

      - name: Setup Ruby & Fastlane
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Run tests
        run: bundle exec fastlane test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: build/

  beta:
    name: Deploy Beta
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for changelog

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Install CocoaPods
        if: hashFiles('Podfile.lock') != ''
        run: pod install

      - name: Deploy to TestFlight
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          MATCH_GIT_URL: ${{ secrets.MATCH_GIT_URL }}
          MATCH_GIT_BASIC_AUTHORIZATION: ${{ secrets.MATCH_GIT_BASIC_AUTHORIZATION }}
          ASC_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          ASC_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
          ASC_KEY_CONTENT: ${{ secrets.ASC_KEY_CONTENT }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: bundle exec fastlane beta

      - name: Upload IPA
        uses: actions/upload-artifact@v4
        with:
          name: ios-beta-ipa
          path: build/*.ipa
          retention-days: 30

  release:
    name: Deploy Release
    needs: test
    if: startsWith(github.ref, 'refs/tags/ios/v')
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.2', bundler-cache: true }
      - name: Deploy to App Store
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          MATCH_GIT_URL: ${{ secrets.MATCH_GIT_URL }}
          MATCH_GIT_BASIC_AUTHORIZATION: ${{ secrets.MATCH_GIT_BASIC_AUTHORIZATION }}
          ASC_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          ASC_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
          ASC_KEY_CONTENT: ${{ secrets.ASC_KEY_CONTENT }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
        run: bundle exec fastlane release
```

---

## 2. GitHub Actions — Android

### Complete Android Workflow
```yaml
# .github/workflows/android.yml
name: Android CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: android-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties', '**/libs.versions.toml') }}
          restore-keys: gradle-

      - name: Run lint
        run: ./gradlew lintDebug

      - name: Run tests
        run: ./gradlew testDebugUnitTest

      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: app/build/reports/

  beta:
    name: Deploy Beta
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }

      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.2', bundler-cache: true }

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

      - name: Decode keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 --decode > release.keystore

      - name: Create Play Store key
        run: echo "${{ secrets.PLAY_STORE_JSON_KEY }}" | base64 --decode > play-store-key.json

      - name: Deploy to Internal Testing
        env:
          KEYSTORE_PATH: ${{ github.workspace }}/release.keystore
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: bundle exec fastlane android beta

      - name: Upload AAB
        uses: actions/upload-artifact@v4
        with:
          name: android-beta-aab
          path: app/build/outputs/bundle/release/*.aab
          retention-days: 30

  release:
    name: Deploy Release
    needs: test
    if: startsWith(github.ref, 'refs/tags/android/v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.2', bundler-cache: true }
      - name: Decode keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 --decode > release.keystore
      - name: Create Play Store key
        run: echo "${{ secrets.PLAY_STORE_JSON_KEY }}" | base64 --decode > play-store-key.json
      - name: Deploy to Production
        env:
          KEYSTORE_PATH: ${{ github.workspace }}/release.keystore
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: bundle exec fastlane android release
```

---

## 3. GitLab CI — iOS

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
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
      - Pods/

ios:test:
  extends: .ios-base
  stage: test
  script:
    - pod install || true
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
    - pod install || true
    - bundle exec fastlane beta
  environment:
    name: ios-testflight
  artifacts:
    paths: [build/*.ipa]
    expire_in: 30 days
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: on_success

ios:release:
  extends: .ios-base
  stage: deploy
  script:
    - pod install || true
    - bundle exec fastlane release
  environment:
    name: ios-appstore
  rules:
    - if: '$CI_COMMIT_TAG =~ /^ios\/v\d+/'
      when: manual
```

---

## 4. GitLab CI — Android

```yaml
# .gitlab-ci.yml (append to above or separate file)

.android-base:
  image: cimg/android:2024.10
  before_script:
    - bundle install --path vendor/bundle
  cache:
    key: android-${CI_COMMIT_REF_SLUG}
    paths:
      - vendor/bundle
      - .gradle/
      - ~/.gradle/caches/

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
      when: on_success

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
    - if: '$CI_COMMIT_TAG =~ /^android\/v\d+/'
      when: manual
```

---

## 5. Caching Strategies

| Platform | What to Cache | Cache Key |
|----------|--------------|-----------|
| iOS (SPM) | `~/Library/Developer/Xcode/DerivedData` | `Package.resolved` hash |
| iOS (CocoaPods) | `Pods/` | `Podfile.lock` hash |
| Android (Gradle) | `~/.gradle/caches`, `~/.gradle/wrapper` | `*.gradle*` + `libs.versions.toml` hash |
| Ruby (Bundler) | `vendor/bundle` | `Gemfile.lock` hash |

### Cache Tips
- Use `restore-keys` for partial cache hits (faster than cold build)
- Clear caches monthly to avoid stale dependency issues
- Cache build outputs for dependent jobs in the same pipeline
- Android: cache `build/` between lint → test → build if same config

---

## 6. Pipeline Optimization

### Speed Improvements

| Optimization | Impact | How |
|-------------|--------|-----|
| Dependency caching | 30-60% faster | Cache SPM, CocoaPods, Gradle |
| Parallel jobs | 40-50% faster | Run iOS and Android in parallel |
| Skip unnecessary steps | 10-20% faster | Only build release on main/tags |
| Concurrency control | Saves money | Cancel redundant runs on same branch |
| Incremental builds | 20-40% faster | Gradle supports this natively |
| Selective testing | Variable | Only run tests for changed modules |

### Cost Optimization
- **GitHub Actions**: macOS runners cost 10x Linux. Run Android on Linux.
- **GitLab CI**: Use self-hosted macOS runners for iOS. Use shared runners for Android.
- **Caching**: Avoid rebuilding what hasn't changed.
- **Concurrency**: Cancel in-progress runs when a new commit pushes.
- **Artifacts**: Set short retention periods (7 days for test reports, 30 for builds).

### Timing Targets

| Stage | iOS Target | Android Target |
|-------|-----------|----------------|
| Lint | < 2 min | < 1 min |
| Unit tests | < 5 min | < 3 min |
| Build (debug) | < 5 min | < 3 min |
| Build (release) | < 10 min | < 5 min |
| Deploy to beta | < 15 min total | < 10 min total |
| Full pipeline (PR) | < 10 min | < 7 min |
| Full pipeline (deploy) | < 20 min | < 15 min |



---
