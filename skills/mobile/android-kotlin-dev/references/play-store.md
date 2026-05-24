# Play Store Submission Reference

## Table of Contents
1. Pre-Submission Checklist
2. Play Store Policies (Key Rules)
3. Common Rejection Reasons
4. Store Listing Metadata
5. Screenshots & Graphics
6. Internal/Closed/Open Testing
7. App Signing & Release
8. Release Strategies

---

## 1. Pre-Submission Checklist

### Technical
- [ ] App doesn't crash on target devices (test on 3+ device form factors)
- [ ] Tested on minSdk device/emulator
- [ ] ProGuard/R8 rules are correct (release build works)
- [ ] No debug logging in release build
- [ ] No hardcoded API keys or secrets in code
- [ ] Network security config allows only HTTPS in production
- [ ] All permissions requested are actually used
- [ ] App handles permission denials gracefully
- [ ] Back button behavior is correct throughout
- [ ] Deep links work correctly
- [ ] App size is reasonable (under 150MB for APK, AAB can be larger)

### Privacy & Compliance
- [ ] Privacy Policy URL is valid
- [ ] Data Safety section completed accurately in Play Console
- [ ] Permissions declarations match actual usage
- [ ] Ad SDK compliant (if using ads)
- [ ] COPPA compliant (if targeting children)
- [ ] Location usage properly justified (foreground/background)

### Content
- [ ] No placeholder text or images
- [ ] Content rating questionnaire completed
- [ ] All in-app purchases tested (production keys)
- [ ] Localization complete for all target markets

---

## 2. Play Store Policies (Key Rules)

### Restricted Content
- No misleading or deceptive content
- No malware, spyware, or deceptive behavior
- No unauthorized access to device data
- User-generated content requires moderation (reporting, blocking, filtering)
- Sexual content requires appropriate content rating
- No promotion of illegal activities

### Privacy & Data
- Must have a valid, accessible privacy policy
- Data Safety section must accurately reflect data collection
- Must disclose all data sharing with third parties
- Location access must be justified and minimal
- Background location requires additional review
- Cannot access SMS/Call Log without core app functionality justification

### Monetization
- Subscriptions must clearly show: price, billing period, cancellation terms
- Free trials must be genuinely free
- In-app purchases must be delivered as described
- Cannot use misleading pricing (fake discounts)
- Must use Google Play Billing for digital goods (with exceptions for certain apps)

### App Quality
- Must be stable and performant
- Must respond to system back button
- Must handle screen rotation (or explicitly lock orientation)
- Must not drain battery excessively
- Must handle interruptions (calls, notifications) gracefully

### Families Policy (if targeting children)
- Must comply with COPPA
- No behavioral advertising to children
- Must use approved ad SDKs (if showing ads)
- No login requirement for core functionality
- Additional review process

---

## 3. Common Rejection Reasons

### Policy Violation: Deceptive Behavior
**Reason:** App behavior doesn't match description, or hidden functionality.
**Fix:** Ensure store listing accurately describes all app functionality. Remove any hidden features.

### Policy Violation: Permissions
**Reason:** Requesting unnecessary permissions (CAMERA, LOCATION, etc.).
**Fix:** Only request permissions essential to core functionality. Request at the point of use,
not at launch. Provide rationale dialogs explaining why.

### Policy Violation: Data Safety
**Reason:** Data Safety section doesn't match actual data collection.
**Fix:** Audit all SDKs for data collection. Update Data Safety form accurately. Include
ALL third-party SDKs that collect data (Firebase, Analytics, Ads, Crash reporting).

### Policy Violation: Background Location
**Reason:** Using `ACCESS_BACKGROUND_LOCATION` without justification.
**Fix:** You must submit a video showing why background location is essential.
Most apps should use foreground location only.

### Metadata Policy Violation
**Reason:** Misleading title, description, or screenshots.
**Fix:** Don't include unrelated popular keywords. Screenshots must reflect actual app experience.
Don't claim features you don't have.

### App Not Responsive / Crashes
**Reason:** ANRs or crashes detected during review.
**Fix:** Test on multiple devices. Use Firebase Crashlytics to monitor. Fix all ANRs
(main thread blocked >5 seconds). Test with slow network conditions.

### Impersonation
**Reason:** App name or icon too similar to another app.
**Fix:** Use unique branding. Don't mimic Google, Samsung, or competitor apps.

---

## 4. Store Listing Metadata

### App Title
- 30 characters max
- Include primary keyword naturally
- Must be unique and not misleading

### Short Description
- 80 characters max
- One compelling sentence about the app's value
- Include a key benefit or differentiator

### Full Description
- 4000 characters max
- First 1-3 lines are critical (shown before "Read more")
- Structure: Hook → Features → Social Proof → CTA
- Use emoji and formatting for scanability
- Don't mention competitors by name
- Don't include pricing (varies by region)
- Don't promise specific results ("lose 10 lbs in a week")

### Keywords Strategy
- Keywords are extracted from title, short description, and full description
- Repeat key terms 3-5 times naturally in the full description
- Use long-tail keywords (more specific = less competition)
- Research competitor keywords
- Update keywords based on search analytics in Play Console

### Categories
- Select the most accurate category (Play Console provides choices)
- Primary category determines where the app appears in browsing
- Tags help with discoverability (select up to 5)

---

## 5. Screenshots & Graphics

### Required Assets

| Asset | Size | Required? |
|-------|------|-----------|
| Phone screenshots | Min 320px, Max 3840px, 16:9 or 9:16 | Yes (min 2, max 8) |
| 7" tablet screenshots | Same ratio | If supporting tablets |
| 10" tablet screenshots | Same ratio | If supporting tablets |
| Feature graphic | 1024 × 500 px | Yes |
| App icon | 512 × 512 px | Yes (high-res) |
| Promo video | YouTube URL | Optional but recommended |

### Screenshot Best Practices
- 2-8 screenshots per device type per localization
- First 2 screenshots are most important (shown in search results)
- Show the app in use with real data
- Add text captions highlighting key features
- Use consistent branding and style across screenshots
- Show key user flows (onboarding → main feature → key actions)
- Include dark mode screenshots if supported
- Test screenshots on the Play Store listing preview

### Feature Graphic
- Required — shown at the top of the store listing
- 1024 × 500 pixels, landscape
- Should be visually compelling and represent the app's brand
- Don't include too much text (may be cropped on different devices)
- Consider both light and dark Play Store themes

---

## 6. Testing Tracks

### Internal Testing
- Up to 100 testers
- No review required
- Instant distribution after upload
- Best for: daily builds, development testing

### Closed Testing (Alpha/Beta)
- Unlimited testers via email lists or Google Groups
- First release requires review (~hours to days)
- Best for: QA team, stakeholders, beta users

### Open Testing (Beta)
- Anyone can join via Play Store listing
- Requires review
- Feedback visible in Play Console
- Best for: public beta before launch

### Production
- Available to all users
- Requires review (first submission: days; updates: hours to days)
- Staged rollout available

### Testing Checklist
- [ ] Internal testing for at least 1 week
- [ ] Closed testing with 20+ users for 2 weeks
- [ ] Monitor crash reports and ANRs in Play Console
- [ ] Test in-app purchases in test environment
- [ ] Verify deep links and App Links
- [ ] Test push notifications
- [ ] Review vitals dashboard (crash rate, ANR rate)

---

## 7. App Signing & Release

### App Bundle (AAB) — Required
Google Play requires Android App Bundles (AAB) instead of APKs since August 2021.

```kotlin
// build.gradle.kts
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}
```

### Play App Signing (Recommended)
- Google manages your app signing key
- You upload with an upload key (which can be rotated if compromised)
- Enables optimized APK delivery from AAB

### Build Signing Configuration
```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

### ProGuard/R8 Rules
```proguard
# Keep data classes used with Gson/Moshi
-keep class com.example.myapp.data.remote.dto.** { *; }
-keep class com.example.myapp.domain.model.** { *; }

# Retrofit
-keepattributes Signature
-keepattributes *Annotation*

# Hilt
-keep class dagger.hilt.** { *; }

# Room
-keep class * extends androidx.room.RoomDatabase
```

---

## 8. Release Strategies

### Staged Rollout
- Start at 1%, monitor for 24 hours
- Increase to 5%, 10%, 25%, 50%
- Full rollout after 3-5 days of monitoring
- Can halt and rollback at any stage
- Monitor: crash rate, ANR rate, uninstall rate, ratings

### Version Naming
```
versionCode — Integer, always incrementing (e.g., 42, 43, 44)
versionName — Human-readable (e.g., "2.3.1")

Major.Minor.Patch:
Major: Breaking changes, redesigns
Minor: New features
Patch: Bug fixes
```

### Release Notes (What's New)
- 500 characters max per language
- Lead with the most exciting change
- Be specific about improvements
- Don't just say "Bug fixes and improvements"
- Group: New Features, Improvements, Fixes

### Pre-Launch Report
- Google Play automatically tests your app on real devices
- Reviews: crashes, ANRs, security vulnerabilities, accessibility issues
- Check pre-launch report in Play Console before promoting to production
- Fix any critical issues before full rollout

### Monitoring Post-Release
- Android Vitals in Play Console (crash rate target: < 1.09%)
- ANR rate target: < 0.47%
- Firebase Crashlytics for detailed crash reports
- Monitor user reviews for new issues
- Watch uninstall rate for regression signals



---
