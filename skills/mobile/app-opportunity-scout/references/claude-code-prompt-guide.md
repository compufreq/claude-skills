# Claude Code Prompt Engineering Guide

Best practices for generating a production-ready Claude Code prompt that scaffolds a full mobile app.

## Prompt Structure

A great Claude Code prompt for app scaffolding follows this structure:

```
1. Project Overview (context + goals)
2. Tech Stack & Setup Instructions
3. Project Directory Structure
4. Core Architecture Decisions
5. Screen-by-Screen Implementation
6. Shared Components & Design System
7. API & Data Layer
8. Monetization Integration
9. Testing Strategy
10. Deployment & Submission
```

## Writing Effective Instructions

### Be explicit about file paths
Instead of: "Create a navigation system"
Write: "Create `src/navigation/AppNavigator.tsx` with a bottom tab navigator containing these tabs: ..."

### Use code blocks for schemas and structures
```
src/
├── app/                    # App entry, providers, theme
│   ├── App.tsx
│   ├── theme.ts
│   └── providers/
├── features/               # Feature-based modules
│   ├── home/
│   │   ├── screens/
│   │   ├── components/
│   │   └── hooks/
│   ├── profile/
│   └── settings/
├── shared/                 # Shared utilities
│   ├── components/         # Reusable UI components
│   ├── hooks/
│   ├── services/           # API, storage, analytics
│   ├── types/
│   └── utils/
├── navigation/             # Navigation config
└── assets/                 # Images, fonts
```

### Specify TypeScript types inline
Don't just say "create a user model." Write:
```typescript
// src/shared/types/user.ts
export interface User {
  id: string;
  email: string;
  displayName: string;
  subscription: 'free' | 'pro' | 'premium';
  createdAt: Date;
}
```

### Give context for architectural decisions
Don't just say "use Zustand." Say:
"Use Zustand for state management because the app has moderate complexity — fewer than 10 global
state slices, no deeply nested state, and the actions are straightforward. Redux would be overkill.
Configure with persist middleware for offline-first behavior."

### Include platform-specific instructions
```
For iOS:
- Configure Info.plist with NSUserTrackingUsageDescription for ATT
- Add SKPaymentQueue observer in AppDelegate for StoreKit
- Set minimum deployment target to iOS 16.0

For Android:
- Configure build.gradle with billing library dependency
- Add INTERNET and BILLING permissions to AndroidManifest.xml
- Set minSdkVersion to 26 (Android 8.0)
```

## Revenue Integration Patterns

### In-App Purchases (RevenueCat recommended)
```
1. Install: npx expo install react-native-purchases
2. Configure in app entry:
   - Initialize with API keys (separate for iOS/Android)
   - Identify user on login
   - Fetch offerings on app launch
3. Create PaywallScreen component:
   - Display available packages
   - Handle purchase flow
   - Restore purchases button
4. Gate premium features with entitlement checks
```

### Subscriptions
```
Define tiers:
- Free: [list features]
- Pro ($X.XX/month): [list features]
- Premium ($X.XX/month): [list features]

Implement:
- SubscriptionContext provider wrapping the app
- useSubscription() hook returning current tier and upgrade()
- PaywallModal component triggered at gate points
```

### Ads (Google AdMob)
```
Install: npx expo install react-native-google-mobile-ads
Place ads at natural break points:
- Banner: bottom of list screens (320x50)
- Interstitial: between major user flows (max 1 per 3 minutes)
- Rewarded: optional unlock for premium content
Remove ads for paid users.
```

## Testing Instructions
```
Include in prompt:
- Unit tests for business logic (Jest)
- Component tests for key screens (React Native Testing Library)
- E2E test outline (Detox or Maestro)
- At minimum: auth flow, core feature flow, purchase flow
```

## Prompt Formatting Tips

- Use markdown headers (##) to separate major sections
- Use numbered lists for sequential steps
- Use code blocks for every file path, command, or code snippet
- Bold the most critical requirements so they don't get missed
- End with a "Verification Checklist" — a list of things Claude Code should confirm work before finishing
- Include the specific app name, color scheme, and copy throughout — the prompt should feel like a spec doc,
  not a generic template
