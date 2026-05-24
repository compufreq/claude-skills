# Modularization & Feature Flags Reference

## Table of Contents
1. Module Architecture
2. Module Types & Responsibilities
3. Dependency Rules
4. Feature Flags
5. A/B Testing Integration
6. Migration: Monolith → Modular

---

## 1. Module Architecture

### Why Modularize?
- **Build speed**: Parallel compilation, incremental builds
- **Code ownership**: Teams own modules, not random files
- **Encapsulation**: Internal implementation details are hidden
- **Testability**: Modules are independently testable
- **Reusability**: Modules can be shared across apps
- **Dynamic delivery**: Android supports on-demand modules

### Module Graph (Both Platforms)

```
                    ┌─────┐
                    │ app │ ← Wires everything together
                    └──┬──┘
          ┌────────┬───┴───┬────────┐
          ▼        ▼       ▼        ▼
    ┌──────────┐ ┌─────┐ ┌────────┐ ┌──────┐
    │feature-  │ │feat-│ │feature-│ │feat- │
    │home      │ │auth │ │search  │ │profile│
    └────┬─────┘ └──┬──┘ └───┬────┘ └───┬──┘
         │          │        │           │
    ┌────┴──────────┴────────┴───────────┴───┐
    │              domain                     │ ← Use cases, entities, interfaces
    └────┬──────────┬────────┬───────────┬───┘
         │          │        │           │
    ┌────┴───┐ ┌────┴───┐ ┌─┴──────┐ ┌──┴─────┐
    │core-   │ │core-   │ │core-   │ │core-   │
    │network │ │database│ │ui      │ │common  │
    └────────┘ └────────┘ └────────┘ └────────┘
```

### Key Rules
1. **Features never depend on other features** — prevents circular dependencies
2. **Features depend on domain and core** — but never on data directly
3. **Domain depends on nothing** (or only core-common)
4. **Core modules don't depend on features or domain**
5. **App module wires everything together** — only module that knows about all features

---

## 2. Module Types & Responsibilities

### Feature Modules
```
feature-home/
├── src/
│   ├── ui/           # Screens, composables/views
│   ├── viewmodel/    # Feature-specific ViewModels
│   ├── di/           # Feature-specific DI (Hilt module)
│   └── navigation/   # Feature routes/destinations
├── test/             # Unit tests
└── build.gradle.kts  # Module dependencies
```

**Responsibilities:**
- UI screens specific to this feature
- ViewModels for this feature
- Feature-local navigation
- Maps domain models to UI models

**Does NOT contain:**
- Business logic (belongs in domain)
- API calls (belongs in core-network)
- Database queries (belongs in core-database)
- Shared UI components (belongs in core-ui)

### Domain Module
```
domain/
├── model/            # Entities (User, Product, Order)
├── repository/       # Repository interfaces (protocols)
├── usecase/          # Use cases / interactors
└── error/            # Domain-specific error types
```

**Responsibilities:**
- Business entities (pure data models)
- Repository interfaces (contracts)
- Use cases that orchestrate business logic
- Business validation rules

**Does NOT contain:**
- Platform-specific code (no Android/iOS imports)
- UI code
- Network DTOs or database entities
- Implementation details

### Core Modules

| Module | Contains |
|--------|---------|
| `core-network` | API client, interceptors, DTOs, serialization |
| `core-database` | Database setup, DAOs/queries, entity types, migrations |
| `core-ui` | Shared composables/views, theme, design tokens, icons |
| `core-common` | Extensions, utilities, constants, result types |
| `core-testing` | Test utilities, fakes, fixture factories, test rules |

---

## 3. Dependency Rules

### Allowed Dependencies Matrix

| Module ↓ depends on → | app | feature-* | domain | core-* |
|------------------------|-----|-----------|--------|--------|
| **app** | — | ✅ | ✅ | ✅ |
| **feature-*** | ❌ | ❌ | ✅ | ✅ |
| **domain** | ❌ | ❌ | — | ✅ (common only) |
| **core-*** | ❌ | ❌ | ❌ | ✅ (other core) |

### Enforcing Rules

**Android (Gradle):**
```kotlin
// In feature module build.gradle.kts — this will fail if you add a feature dependency
dependencies {
    implementation(project(":domain"))
    implementation(project(":core:ui"))
    implementation(project(":core:network"))
    // implementation(project(":feature:auth")) // ← BUILD SHOULD FAIL
}
```

**iOS (Swift Package Manager):**
```swift
// Package.swift
.target(name: "FeatureHome", dependencies: ["Domain", "CoreUI", "CoreNetwork"]),
// NOT: .target(name: "FeatureHome", dependencies: ["FeatureAuth"]) ← violation
```

### Communication Between Features

Since features can't depend on each other, they communicate via:

1. **Navigation events** — Feature A emits a route, App module navigates to Feature B
2. **Domain events** — Shared event bus in domain layer
3. **Shared state** — State in domain layer observed by multiple features
4. **Deep links** — Each feature registers URL patterns, navigation resolves them

---

## 4. Feature Flags

### Flag Types

| Type | Purpose | Example |
|------|---------|---------|
| **Release flag** | Gate incomplete features | `enable_new_checkout` |
| **Experiment flag** | A/B testing | `checkout_button_color` |
| **Ops flag** | Kill switch for live issues | `disable_video_uploads` |
| **Permission flag** | Feature gating by user tier | `premium_analytics` |

### Feature Flag Architecture

```
┌──────────────────────┐
│  Remote Config       │  Firebase, LaunchDarkly, Flagsmith
│  (source of truth)   │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  FeatureFlagService  │  Fetches, caches, evaluates flags
│  (domain interface)  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  ViewModel / View    │  Checks flag before showing feature
└──────────────────────┘
```

### Implementation

```kotlin
// Domain interface
interface FeatureFlagService {
    fun isEnabled(flag: FeatureFlag): Boolean
    fun getString(flag: FeatureFlag): String
    fun getInt(flag: FeatureFlag): Int
    suspend fun refresh()
}

enum class FeatureFlag(val key: String, val defaultValue: Any) {
    NEW_CHECKOUT("enable_new_checkout", false),
    ONBOARDING_V2("enable_onboarding_v2", false),
    MAX_UPLOAD_SIZE_MB("max_upload_size_mb", 10),
    CHECKOUT_BUTTON_TEXT("checkout_button_text", "Buy Now"),
    DISABLE_VIDEO("disable_video_uploads", false),  // Ops kill switch
}

// Usage in ViewModel
class CheckoutViewModel @Inject constructor(
    private val featureFlags: FeatureFlagService,
) : ViewModel() {
    val useNewCheckout: Boolean get() = featureFlags.isEnabled(FeatureFlag.NEW_CHECKOUT)
    val buttonText: String get() = featureFlags.getString(FeatureFlag.CHECKOUT_BUTTON_TEXT)
}

// Usage in Compose
@Composable
fun CheckoutScreen(viewModel: CheckoutViewModel = hiltViewModel()) {
    if (viewModel.useNewCheckout) {
        NewCheckoutFlow()
    } else {
        LegacyCheckoutFlow()
    }
}
```

### Feature Flag Rules
1. Every flag has a **default value** (app works if remote config is unreachable)
2. Flags are evaluated at **app startup** and cached (not per-use)
3. Release flags are **removed** once the feature is fully rolled out
4. Flag names are **consistent across iOS and Android**
5. Ops flags can be toggled **without app update** (critical for incidents)
6. Flag changes are **logged** for debugging

### Flag Lifecycle
```
Created → Testing → Partial Rollout → Full Rollout → Cleanup (remove flag + old code)
```

Remove flags within 2 sprints of full rollout. Dead flags are tech debt.

---

## 5. A/B Testing Integration

### Structure
```kotlin
data class Experiment(
    val name: String,
    val variant: String,  // "control", "variant_a", "variant_b"
    val isEnabled: Boolean,
)

interface ExperimentService {
    fun getExperiment(name: String): Experiment
    fun trackExposure(experiment: Experiment)  // Record that user saw the variant
    fun trackConversion(experiment: Experiment, event: String)  // Record outcome
}

// Usage
val experiment = experimentService.getExperiment("checkout_redesign")
experimentService.trackExposure(experiment)

when (experiment.variant) {
    "control" -> LegacyCheckout()
    "variant_a" -> NewCheckoutA()
    "variant_b" -> NewCheckoutB()
}
```

---

## 6. Migration: Monolith → Modular

### Step-by-Step

1. **Create core modules first** — Extract `core-common`, `core-network`, `core-ui`
2. **Create domain module** — Move entities, repository interfaces, use cases
3. **Extract one feature** — Pick the most independent feature first
4. **Enforce dependency rules** — Build should fail if rules are violated
5. **Extract remaining features** — One at a time, starting with least coupled
6. **Clean up app module** — Should only contain DI wiring and navigation

### Migration Metrics
- Build time before/after (should decrease)
- Module count and dependency graph complexity
- Lines of code per module (flag modules > 10k LOC for splitting)
- Circular dependency count (should be 0)

### Common Pitfalls
- Extracting too many modules too fast → start with 3-5 modules
- Shared mutable state across modules → use domain events
- God module that everything depends on → keep core-common minimal
- Module boundaries don't match team boundaries → align with team structure



---
