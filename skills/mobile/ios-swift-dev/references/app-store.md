# App Store Submission Reference

## Table of Contents
1. Pre-Submission Checklist
2. App Store Review Guidelines (Key Rules)
3. Common Rejection Reasons & Fixes
4. App Store Connect Metadata
5. Screenshots & Previews
6. TestFlight & Beta Testing
7. Code Signing & Provisioning
8. Release Strategies

---

## 1. Pre-Submission Checklist

### Technical
- [ ] App runs without crashes on all supported devices
- [ ] Tested on oldest supported iOS version
- [ ] No private API usage
- [ ] No placeholder/test content in the app
- [ ] All APIs have proper error handling (no blank screens)
- [ ] Network requests handle offline gracefully
- [ ] App doesn't crash when permissions are denied
- [ ] Memory usage is reasonable (profile with Instruments)
- [ ] Battery usage is acceptable (no unnecessary background activity)
- [ ] App works with VoiceOver enabled
- [ ] Supports Dynamic Type
- [ ] Supports Dark Mode (or explicitly opts out)
- [ ] No unused frameworks linked
- [ ] Bitcode enabled (if required)
- [ ] Correct deployment target set

### Legal & Privacy
- [ ] Privacy Policy URL is valid and accessible
- [ ] App Privacy Nutrition Label is accurate in App Store Connect
- [ ] IDFA usage disclosed if applicable
- [ ] NSUserTrackingUsageDescription added if using ATT
- [ ] All third-party SDKs have valid licenses
- [ ] No copyrighted content without license
- [ ] Terms of Service available (if applicable)
- [ ] GDPR/CCPA compliance (if applicable)

### Content
- [ ] All text is finalized (no lorem ipsum)
- [ ] All images are final assets
- [ ] Localization is complete for all supported languages
- [ ] Onboarding flow is polished
- [ ] App icon meets guidelines (no alpha channel, 1024×1024)
- [ ] Launch screen is appropriate (not an ad, not just a logo with loading)

### App Store Connect
- [ ] App name (30 characters max)
- [ ] Subtitle (30 characters max)
- [ ] Description (4000 characters max)
- [ ] Keywords (100 characters max, comma-separated)
- [ ] Screenshots for all required device sizes
- [ ] App preview videos (optional but recommended)
- [ ] Privacy Policy URL
- [ ] Support URL
- [ ] Marketing URL (optional)
- [ ] Contact information
- [ ] Age rating questionnaire completed
- [ ] Pricing and availability configured

---

## 2. App Store Review Guidelines (Key Rules)

### Safety (Section 1)
- No objectionable content (hate speech, discrimination, violence)
- User-generated content requires: reporting, blocking, filtering
- Apps must have clear content moderation
- Medical apps must clearly disclaim: not a substitute for professional advice
- Kids category apps have strict privacy requirements (no tracking, no ads)

### Performance (Section 2)
- App must be complete and functional — no beta, demo, or trial versions
- App must work as described in metadata
- Must use latest SDK and support latest OS features
- No hidden features or undocumented functionality
- Minimum functionality: App must provide value beyond a website wrapper
- No apps that are essentially just a WebView of a website

### Business (Section 3)
- **In-App Purchase required** for digital content/features (not physical goods)
- Cannot link to external purchasing (for digital content)
- Subscriptions must clearly show: price, duration, auto-renewal terms
- Free trials must be genuinely free with no required purchase
- Apps cannot require unreasonable personal information
- Pricing must be consistent across all regions

### Design (Section 4)
- Follow Apple Human Interface Guidelines
- Must work on all supported device sizes
- Must handle orientations gracefully (or explicitly lock)
- No fake system UI elements (mock alerts, fake system buttons)
- App should use standard iOS controls where appropriate
- Icon must not mimic Apple's system icons
- Must have a unique name that doesn't mislead about functionality

### Legal (Section 5)
- Must comply with all laws in regions where distributed
- Must have a valid privacy policy
- Cannot collect unnecessary data
- Must implement App Tracking Transparency for tracking
- Gambling apps need appropriate licenses
- Health/finance apps may need regulatory compliance

---

## 3. Common Rejection Reasons & Fixes

### Guideline 2.1 — Performance: App Completeness
**Reason:** App crashes, has placeholder content, or is not fully functional.
**Fix:** Test on physical devices with the release build. Remove all test/placeholder content.
Use TestFlight for at least 1 week of beta testing before submission.

### Guideline 2.3.3 — Screenshots Don't Match
**Reason:** Screenshots show features not in the app, or use misleading imagery.
**Fix:** Capture screenshots from the actual app. Don't over-embellish mockups.

### Guideline 3.1.1 — In-App Purchase Required
**Reason:** App sells digital content/subscriptions via external payment.
**Fix:** Use StoreKit for ALL digital content purchases. Physical goods/services can
use external payment (Uber, Amazon, etc.).

### Guideline 4.0 — Design: Minimum Functionality
**Reason:** App is essentially a wrapper around a website or has no meaningful functionality.
**Fix:** Add native features: push notifications, offline support, widgets, Siri shortcuts,
camera/sensors, haptics — things a website can't do.

### Guideline 4.2.3 — Design: WebView App
**Reason:** App is just a WebView showing a responsive website.
**Fix:** Add significant native functionality. At minimum: native navigation, offline
capabilities, push notifications, or device integration.

### Guideline 5.1.1 — Data Collection and Storage
**Reason:** App collects more data than needed or lacks privacy policy.
**Fix:** Only request permissions when needed (just-in-time). Provide clear usage
descriptions in Info.plist. Ensure privacy policy URL works.

### Guideline 5.1.2 — Data Use and Sharing
**Reason:** App shares data with third parties without disclosure.
**Fix:** Accurately complete the App Privacy Nutrition Label. Implement ATT for tracking.

### Metadata Rejected
**Reason:** Description mentions other platforms, contains pricing, or uses trademarked terms.
**Fix:** Don't mention Android, Windows, or competing platforms. Don't include pricing in
description (it changes by region). Don't use Apple trademarks incorrectly.

### Binary Rejected — Missing Purpose String
**Reason:** App uses a framework requiring a usage description but Info.plist is missing it.
**Fix:** Add ALL required `NS*UsageDescription` keys to Info.plist:

| Permission | Info.plist Key |
|-----------|---------------|
| Camera | `NSCameraUsageDescription` |
| Photo Library | `NSPhotoLibraryUsageDescription` |
| Location (always) | `NSLocationAlwaysAndWhenInUseUsageDescription` |
| Location (in use) | `NSLocationWhenInUseUsageDescription` |
| Microphone | `NSMicrophoneUsageDescription` |
| Contacts | `NSContactsUsageDescription` |
| Calendar | `NSCalendarsUsageDescription` |
| Bluetooth | `NSBluetoothAlwaysUsageDescription` |
| Face ID | `NSFaceIDUsageDescription` |
| Health | `NSHealthShareUsageDescription` |
| Motion | `NSMotionUsageDescription` |
| Tracking | `NSUserTrackingUsageDescription` |

---

## 4. App Store Connect Metadata

### App Name Strategy
- 30 characters max
- Include primary keyword if natural
- Don't stuff keywords into the name
- Must be unique in the App Store

### Subtitle Strategy
- 30 characters max
- Complement the name (don't repeat it)
- Highlight a key benefit or feature

### Keywords Strategy
- 100 characters total (comma-separated, no spaces after commas)
- Don't repeat words from the app name or subtitle (they're already indexed)
- Include common misspellings of your app name
- Include competitor names (controversial but common)
- Use singular forms (Apple indexes both singular and plural)
- Don't waste characters on generic words like "app" or "free"

### Description
- First 3 lines are crucial (shown before "Read More")
- Lead with the strongest benefit
- Use short paragraphs, bullets, and emoji for scanability
- Include social proof if available (awards, press, user count)
- End with a call to action
- Don't mention pricing (varies by region)
- Don't mention specific iOS versions

### What's New (Release Notes)
- Lead with the most exciting new feature
- Group changes: New Features, Improvements, Bug Fixes
- Be specific: "Fixed crash when uploading photos" not "Bug fixes"
- Keep it concise — users skim these

---

## 5. Screenshots & Previews

### Required Screenshot Sizes

| Device | Size (pixels) | Required? |
|--------|--------------|-----------|
| iPhone 6.9" (16 Pro Max) | 1320 × 2868 | Yes (new max) |
| iPhone 6.7" (15 Pro Max) | 1290 × 2796 | Yes |
| iPhone 6.5" (11 Pro Max) | 1242 × 2688 | Recommended |
| iPhone 5.5" (8 Plus) | 1242 × 2208 | If supporting |
| iPad Pro 13" | 2048 × 2732 | If iPad app |
| iPad Pro 11" | 1668 × 2388 | If iPad app |

### Screenshot Best Practices
- Up to 10 screenshots per localization
- First screenshot is most important (shown in search results)
- Show the app in use, not empty states
- Add brief text captions highlighting key features
- Use real data (not "Lorem ipsum" or test accounts)
- Show the most compelling features first
- Consider device frames for polish
- Dark/light variants show attention to detail

### App Preview Videos
- Up to 3 videos per localization, 30 seconds max each
- First 3 seconds are the poster frame (shown as thumbnail)
- No voiceover required (but add captions)
- Show the app in use — don't make a commercial
- 30 fps minimum

---

## 6. TestFlight & Beta Testing

### TestFlight Setup
1. Archive the build in Xcode (Product → Archive)
2. Upload to App Store Connect (Xcode → Distribute App)
3. Wait for processing (usually 10-30 minutes)
4. Add internal testers (up to 100, instant access)
5. Submit for beta review (external testers, up to 10,000)
6. Distribute to external testers after approval

### Internal vs External Testers

| | Internal | External |
|--|---------|----------|
| Limit | 100 | 10,000 |
| Review required | No | Yes (first build + major changes) |
| Must be team member | Yes (App Store Connect) | No (email invite or public link) |
| Access | Immediate | After beta review |

### Beta Testing Checklist
- [ ] Test for at least 1 week before App Store submission
- [ ] Test on oldest supported device/OS
- [ ] Test on latest device/OS
- [ ] Test with VoiceOver enabled
- [ ] Test with slow network / airplane mode
- [ ] Test all IAP flows (sandbox environment)
- [ ] Review crash reports in TestFlight/Xcode
- [ ] Collect feedback from testers
- [ ] Fix all P0/P1 bugs before submission

---

## 7. Code Signing & Provisioning

### Development vs Distribution

| | Development | Distribution |
|--|------------|-------------|
| Certificate | Apple Development | Apple Distribution |
| Profile | Development provisioning | App Store provisioning |
| Use | Running on device during development | TestFlight + App Store |
| Signing | Automatic (recommended) | Automatic or Manual |

### Automatic Signing (Recommended)
In Xcode → Target → Signing & Capabilities:
- Check "Automatically manage signing"
- Select your team
- Xcode handles certificates, profiles, and entitlements

### Common Signing Issues
- **"No profiles match"** → Ensure Bundle ID matches App Store Connect
- **"Certificate not found"** → Keychain → install from developer.apple.com
- **Expired profile** → Xcode → Preferences → Accounts → Download profiles
- **Multiple teams** → Ensure correct team is selected

---

## 8. Release Strategies

### Immediate Release
- App goes live as soon as Apple approves
- Fastest option but least control over timing
- Use when: patches, minor updates

### Manual Release
- You approve the release after Apple's review
- Control the exact moment it goes live
- Use when: coordinating with marketing, PR, or events

### Phased Release
- Roll out to 1%, 2%, 5%, 10%, 20%, 50%, 100% over 7 days
- Can pause or cancel if issues discovered
- Existing users can manually update during rollout
- Use when: major releases where monitoring is critical

### Version Strategy
```
Major.Minor.Patch (e.g., 2.3.1)
Major: Breaking changes, major redesigns
Minor: New features, significant improvements
Patch: Bug fixes, minor improvements
```

Build number: Increment with every TestFlight upload. Use date-based (20250115.1)
or sequential (42, 43, 44).



---
