# Design Systems Reference

Quick reference for platform-specific design conventions when building interactive HTML mockups.

## Android — Material Design 3

### Layout & Navigation
- **Bottom navigation**: 3–5 destinations, icon + label, 80dp height
- **Top app bar**: 64dp height, left-aligned title, optional leading nav icon
- **FAB**: 56dp default, 96dp expanded; position bottom-right, 16dp margin
- **System bars**: Status bar 24dp, navigation bar 48dp (gesture) or variable (3-button)

### Visual Language
- **Corner radius**: Large (28dp) for cards/dialogs, Medium (16dp) for buttons/chips, Small (8dp) for text fields
- **Elevation**: Use tonal elevation (surface tint color) rather than shadow elevation
- **Color system**: Primary, Secondary, Tertiary, Surface, On-Surface, Outline, Error
- **Typography scale**: Display (large/medium/small), Headline, Title, Body, Label
- **Font**: Roboto as default; Google Fonts alternatives welcome if they match the brand

### Key Components
- Filled/outlined buttons (20dp corner radius, 40dp height)
- Cards with 12dp corner radius, 1dp outline or surface-tint fill
- Bottom sheets (modal and standard)
- Snackbars (bottom, above FAB/nav)
- Switches, checkboxes, radio buttons per Material 3 specs

### CSS Template (for HTML mockups)
```css
:root {
  --md-sys-color-primary: #6750A4;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-surface: #FFFBFE;
  --md-sys-color-on-surface: #1C1B1F;
  --md-sys-color-surface-variant: #E7E0EC;
  --md-sys-color-outline: #79747E;
  --md-sys-color-secondary: #625B71;
  --md-sys-color-tertiary: #7D5260;
  --md-sys-color-error: #B3261E;
}
```

---

## iOS — Human Interface Guidelines

### Layout & Navigation
- **Tab bar**: Bottom, 49pt height, up to 5 tabs (SF Symbols for icons)
- **Navigation bar**: 44pt height (collapsed), up to 96pt (large title), translucent background
- **Safe areas**: Top 47pt (notch) or 59pt (Dynamic Island), bottom 34pt (home indicator)
- **Screen width**: Design for 390pt (iPhone 14/15 standard)

### Visual Language
- **Corner radius**: Continuous (squircle), 10pt for small elements, 20pt for cards, 38.5pt for app icons
- **Typography**: SF Pro (use system font stack: `-apple-system, BlinkMacSystemFont, system-ui`)
  - Large Title: 34pt bold
  - Title 1: 28pt bold
  - Headline: 17pt semibold
  - Body: 17pt regular
  - Caption: 12pt regular
- **Colors**: Use semantic colors (systemBlue, systemGreen, etc.) and support light/dark mode
- **Blur/vibrancy**: Navigation bars and tab bars use `backdrop-filter: blur(20px) saturate(180%)`

### Key Components
- Grouped/inset table views (rounded rectangle sections)
- Toggle switches (31x51pt, green when on)
- Action sheets (bottom-anchored with cancel button)
- Segmented controls (rounded, filled selection)
- Pull-to-refresh (native spinner)
- Swipe actions on list rows

### CSS Template (for HTML mockups)
```css
:root {
  --ios-blue: #007AFF;
  --ios-green: #34C759;
  --ios-red: #FF3B30;
  --ios-orange: #FF9500;
  --ios-bg: #F2F2F7;
  --ios-card-bg: #FFFFFF;
  --ios-separator: rgba(60, 60, 67, 0.12);
  --ios-label: #000000;
  --ios-secondary-label: rgba(60, 60, 67, 0.6);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', system-ui, sans-serif;
}
```

---

## React Native — Cross-Platform Adaptive

### Navigation
- Use React Navigation's Bottom Tabs with platform-adaptive styling
- Android: Material-style bottom nav (filled icon, label below)
- iOS: Tab bar with outline icons, label below, translucent background
- Stack navigators per tab with platform-adaptive headers

### Typography Scale (shared)
```
Display:  32px / bold
Heading:  24px / bold
Title:    20px / semibold
Body:     16px / regular
Caption:  12px / regular
```

### Spacing Scale (shared)
```
xs: 4px | sm: 8px | md: 16px | lg: 24px | xl: 32px | xxl: 48px
```

### Platform Differences to Show
| Element | Android | iOS |
|---|---|---|
| Back button | ← arrow | < with label |
| Status bar | Colored/translucent | Light/dark content |
| Switches | Material switch | iOS toggle |
| Dialogs | Center of screen | Action sheets from bottom |
| Date pickers | Calendar or spinner | Scroll wheels |
| Haptics | Vibration API | Impact/notification feedback |

### Mockup Approach
Build one HTML page with a toggle or side-by-side view showing both platform renderings.
Use a shared color system but apply platform-specific chrome and component styles.
