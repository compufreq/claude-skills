---
name: app-opportunity-scout
description: >
  End-to-end mobile app business opportunity finder and planner. Researches trending apps on App Store
  and Google Play growing fast in downloads and revenue, performs SWOT competitor analysis, identifies
  market gaps, designs the app with interactive UI/UX mockups for Android (Material Design), iOS (HIG),
  and React Native, then generates a production-ready Claude Code prompt to build it. Use whenever the
  user mentions app opportunities, trending apps, app market research, competitor analysis, mobile app
  ideas, app revenue, app store trends, or building an app to compete. Also trigger for analyzing
  fast-growing apps, finding market gaps, generating app concepts with mockups, creating Claude Code
  prompts for mobile apps, or even just "find me an app idea that makes money." Adapts to budget
  constraints, region-specific markets, and partial requests (research only, designs only, etc.).
---

# App Opportunity Scout

This skill walks through a structured pipeline to go from "what's hot on the app stores?" all the way to
"here's the full prompt to build it in Claude Code." Each phase builds on the last, and you should complete
them in order unless the user asks to skip or focus on a specific phase.

## The Pipeline

There are 5 phases. Complete them sequentially, checking in with the user at each transition.

```
Phase 1: Market Research → Phase 2: Competitive Analysis → Phase 3: App Concept →
Phase 4: UI/UX Design → Phase 5: Claude Code Prompt
```

### Smart Phase Detection

Not every request needs all 5 phases. Before starting, read the user's message carefully and decide
which phases to run:

**Skip Phase 1 (Market Research) when:**
- The user already has a specific app idea ("I want to build a habit tracker that...")
- The user names specific competitors they want analyzed
- The user only asks for designs or a build prompt
→ Jump to Phase 2 (competitive analysis of their idea's category) or later.

**Stop after Phase 2 (Competitive Analysis) when:**
- The user says "just the research" or "I'll decide what to build"
- The user explicitly asks NOT to design or build anything yet
→ Deliver Phases 1–2 and ask if they want to continue.

**Start at Phase 4 (UI/UX Design) when:**
- The user says "just show me designs" or "I already know what I'm building, I just need mockups"
- The user provides a clear app concept and only wants visual output
→ Ask a few clarifying questions about the app (features, target user, color preference) then jump to Phase 4.

**Start at Phase 5 (Claude Code Prompt) when:**
- The user has designs already and just needs the build prompt
→ Ask for app concept details and generate the prompt.

If unsure which phases the user wants, briefly ask: "I can do the full pipeline (research →
analysis → concept → design → build prompt) or focus on specific parts. Which do you need?"

### Context Adaptation

Detect these three contextual signals from the user's message and adapt throughout all phases:

**Budget Constraints:**
If the user mentions a budget limit, "free tier only," "solo developer," or "bootstrapping":
- Phase 1: Prioritize app categories with low infrastructure needs (offline-first, local-storage, 
  minimal backend). Flag apps requiring expensive services (ML APIs, real-time sync, video).
- Phase 3: Recommend free-tier services (Firebase Spark, Supabase free, Expo EAS free builds).
  Revenue model should focus on organic growth + IAP/subscriptions, not paid acquisition.
  Include a "Monthly Cost Estimate" table for each service.
- Phase 5: Specify free/cheap alternatives for every paid service. Use Expo, Firebase free tier,
  RevenueCat (free under 2500 MAU), Cloudflare Pages for landing pages.

**Region / Locale Focus:**
If the user targets a specific country or region:
- Phase 1: Add region-specific searches (e.g., `trending finance apps Germany 2026`,
  `top budgeting app Deutschland`). Search in both English and the local language.
- Phase 2: Include region-popular competitors, not just global ones. Note regulations
  (GDPR for EU, CCPA for California, PSD2 for EU finance apps).
- Phase 3: Include compliance requirements (data residency, consent flows, local payment
  methods). Note localization needs (language, currency, date formats).
- Phase 4: Use the local language for UI content in mockups. Show region-appropriate dummy
  data (€ not $, DD.MM.YYYY not MM/DD/YYYY, local names and addresses).
- Phase 5: Include i18n setup, compliance middleware, region-specific store submission notes.

**Developer Experience Level:**
If the user signals they're a beginner ("first app," "learning React Native"):
- Phase 3: Recommend simplest viable tech stack (Expo managed workflow, no ejection).
- Phase 5: Add more explanatory comments, break steps into smaller chunks, include
  links to relevant documentation and beginner tutorials.

---

## Phase 1: Market Research

**Goal:** Identify 5–10 simple apps that are trending upward in downloads and revenue on both stores.

Use `web_search` to find current trending and fast-growing apps. Run multiple searches to cover breadth:

**Search strategy (run all of these):**
1. `trending apps App Store 2026 fastest growing` 
2. `top growing apps Google Play downloads 2026`
3. `simple apps fastest growing in-app purchases revenue`
4. `new apps going viral App Store Google Play`
5. Category-specific searches based on what's trending (utilities, health, finance, entertainment, etc.)

After gathering results, compile a **Trending App Report** with this structure:

```
### Trending App Report

For each app (aim for 5–10):

**[App Name]** — [Category]
- Stores: App Store / Google Play / Both
- Growth signal: [what data suggests it's growing — rankings, reviews, coverage]
- Revenue model: [IAP / Subscription / Ads / Freemium / Combo]
- Core value proposition: [one sentence — what does it do for the user?]
- Simplicity factor: [Low / Medium / High — how simple is the core mechanic?]
```

Present this report to the user and ask: *"These are the trending apps I found. Want me to focus the
competitive analysis on a specific category, or should I pick the most promising cluster?"*

---

## Phase 2: Competitive Analysis

**Goal:** Full SWOT + competitor matrix + market positioning for the top 3–5 apps from Phase 1.

**If the user already has an app idea (Phase 1 was skipped):**
Search for competitors in that idea's category instead. For example, if the user wants to build a
habit tracker, search for `top habit tracker apps 2026`, `best habit apps App Store Google Play`,
and `habit tracker app reviews complaints`. The rest of Phase 2 proceeds identically — you're just
sourcing competitors from the user's category rather than from Phase 1's report.

For each competitor, search for deeper info:
- `"[App Name]" app review features criticism`
- `"[App Name]" vs alternatives competitors`
- `"[App Name]" negative reviews complaints`

### Deliverable: Competitive Analysis Document

**2A. Competitor Matrix** — A comparison table:

| Feature | App A | App B | App C | App D |
|---|---|---|---|---|
| Core feature | ... | ... | ... | ... |
| Price / monetization | ... | ... | ... | ... |
| User rating | ... | ... | ... | ... |
| Key differentiator | ... | ... | ... | ... |
| Biggest weakness | ... | ... | ... | ... |
| Platform | ... | ... | ... | ... |

**2B. SWOT for each competitor:**
- **Strengths**: What they do well, market position, brand
- **Weaknesses**: Common user complaints, missing features, poor UX areas
- **Opportunities**: Gaps they haven't filled, adjacent markets, emerging trends
- **Threats**: New entrants, platform policy changes, user fatigue

**2C. Market Positioning Map:**
Create an interactive HTML visualization (using the Visualizer tool if available) showing competitors
plotted on two axes. Choose axes that reveal a gap — common pairs:
- Simplicity vs Feature richness
- Free-focused vs Premium-focused
- Casual users vs Power users

Highlight the empty quadrant — that's where the opportunity lives.

Present findings to the user and confirm the identified gap before moving on.

---

## Phase 3: App Concept

**Goal:** Define a concrete app concept that fills the competitive gap and has a clear revenue path.

**If the user already has an app idea:**
Don't invent a new concept — refine theirs. Use their idea as the starting point and fill in the
concept brief around it. The competitive analysis from Phase 2 should inform how to position their
idea against existing apps. Suggest improvements or differentiators based on competitor weaknesses,
but respect the user's core vision.

### Deliverable: App Concept Brief

```
## App Concept Brief

### The Idea
- **App name** (suggest 3 options)
- **One-liner**: [What it does in ≤15 words]
- **Target user**: [Who specifically — be precise]
- **Core problem solved**: [The pain point competitors miss]

### Competitive Edge
- **Primary differentiator**: [The #1 thing that makes this better than alternatives]
- **Feature comparison**: [What we do that they don't, and what we deliberately skip]
- **Positioning statement**: For [target user] who [need], [App Name] is the [category]
  that [key benefit], unlike [competitors] which [limitation].

### Revenue Strategy
Outline ALL applicable models and recommend a primary + secondary:
- In-app purchases: [what would users buy?]
- Subscriptions: [what tiers? what's in free vs paid?]
- Ads: [where? interstitial, banner, rewarded?]
- Freemium: [what's the hook? what's behind the paywall?]

Include a rough estimate of revenue potential:
- Target: [X] users in first 6 months
- Conversion rate assumption: [Y]%
- Estimated monthly revenue at target: $[Z]

### Core Features (MVP)
List 5–8 features for the minimum viable product. For each:
- Feature name
- One-sentence description
- Priority: Must-have / Nice-to-have
- Revenue impact: Direct / Indirect / None

### Tech Stack Recommendation
- **React Native** as primary (cross-platform)
- Backend: [recommendation based on app type]
- Key third-party services: [analytics, payments, auth, etc.]
```

Get user approval on the concept before designing.

---

## Phase 4: UI/UX Design

**Goal:** Create interactive HTML mockups for the app concept — three versions.

Read the `references/design-systems.md` file for platform-specific design patterns before starting.

For each platform version, create a **separate interactive HTML artifact** that the user can click through.
Each mockup should include at minimum:
- Onboarding / first launch screen
- Main/home screen
- Core feature screen (the primary user action)
- Settings or profile screen
- Monetization touchpoint (paywall, IAP prompt, or ad placement)

### 4A. Android Version (Material Design 3)
Build with Material Design 3 conventions:
- Bottom navigation bar with 3–5 destinations
- FAB (floating action button) for primary action if applicable
- Top app bar with title
- Material color system (surface, primary, secondary, tertiary)
- Rounded corners (28dp for cards, 16dp for buttons)
- Typography: Roboto or a Material-approved typeface
- System navigation bar at bottom (gesture indicator)
- Status bar with Android styling

### 4B. iOS Version (Human Interface Guidelines)
Build with Apple HIG conventions:
- Tab bar at bottom (SF Symbols style icons)
- Large title navigation bar that collapses on scroll
- SF Pro or system font stack
- iOS-style segmented controls, toggles, and action sheets
- Vibrancy and translucency effects where appropriate
- Safe area awareness (notch/Dynamic Island at top, home indicator at bottom)
- Rounded rectangle cards (continuous corner radius)

### 4C. React Native Version (Cross-platform)
Build a unified design that works on both platforms:
- Adaptive components that feel native on each platform
- Shared color system and typography scale
- Platform-adaptive navigation (bottom tabs)
- Consistent spacing and layout grid
- Show both iOS and Android rendering side-by-side where behaviors differ

Each mockup must be a self-contained interactive HTML file with:
- Clickable navigation between screens
- Smooth transitions / animations
- Realistic content (not lorem ipsum — use contextually appropriate dummy data)
- Correct platform chrome (status bar, navigation bar)
- Dark mode toggle if the app concept warrants it

Present all three mockups to the user for feedback before generating the final prompt.

---

## Phase 5: Claude Code Prompt

**Goal:** Generate a comprehensive, production-ready prompt for Claude Code that scaffolds the entire app.

Read `references/claude-code-prompt-guide.md` for prompt engineering best practices before writing.

### Deliverable: A single markdown file containing the full Claude Code prompt

The prompt must cover:

**Project Setup:**
- React Native (Expo or bare workflow — recommend based on app needs)
- TypeScript configuration
- Directory structure with feature-based organization
- ESLint, Prettier, and testing setup

**Architecture:**
- State management approach (Zustand, Redux Toolkit, or React Context — pick based on complexity)
- Navigation structure (React Navigation with typed routes)
- API layer (Axios or fetch with interceptors)
- Authentication flow
- Error handling and offline support patterns

**Screen-by-Screen Build Plan:**
For each screen from Phase 4, provide:
- Screen name and route
- Component hierarchy
- State requirements
- API endpoints it needs
- User interactions and their handlers
- Platform-specific adaptations

**Monetization Integration:**
- In-app purchase setup (RevenueCat or react-native-iap)
- Subscription management
- Ad integration (Google AdMob via react-native-google-mobile-ads)
- Paywall component design

**Backend Requirements:**
- API schema (REST or GraphQL endpoints)
- Database schema
- Authentication service
- Payment webhook handlers

**Deployment Checklist:**
- App Store submission requirements
- Google Play submission requirements
- Environment configuration (dev, staging, production)
- CI/CD pipeline suggestion

Format the prompt so it can be copy-pasted directly into Claude Code. Use clear section headers,
code blocks for file structures, and explicit instructions for each step. The prompt should be
self-contained — someone with no context about the previous phases should be able to use it.

Save the final prompt as a markdown file and present it to the user.

---

## General Guidelines

- **Always search the web** — this skill depends on current market data. Never rely on training
  knowledge alone for app rankings, revenue data, or trend information.
- **Check in between phases** — don't barrel through all 5 phases without user input. Present each
  phase's deliverable and ask for feedback or direction changes.
- **Respect partial requests** — if the user only wants research, only deliver research. If they
  only want mockups, only deliver mockups. Don't upsell phases they didn't ask for. You can mention
  what other phases are available, but don't run them without permission.
- **Adapt to context signals** — budget constraints, region focus, and developer experience should
  visibly affect every phase's output. A budget-constrained recommendation should look noticeably
  different from an unlimited-budget one. A Germany-focused analysis should have German-language
  mockups and GDPR compliance notes. Make the adaptation obvious, not subtle.
- **Be specific, not generic** — every recommendation should reference the actual competitors found
  in Phase 1 or 2. Generic advice like "make the UX intuitive" is useless. Instead: "Unlike
  [Competitor], which buries the export feature 3 taps deep, put it on the main screen."
- **Revenue realism** — don't oversell. Acknowledge risks and include conservative estimates alongside
  optimistic ones. For budget-constrained users, be especially honest about what's achievable.
- **Design quality matters** — the HTML mockups should look polished and professional. Use the
  frontend-design skill's aesthetic guidelines. These mockups might be shown to investors or
  co-founders.
