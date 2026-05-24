---
name: mobile-architecture
description: >-
  Mobile architecture patterns, modularization, state management, and Kotlin Multiplatform. Use when the user mentions mobile architecture, MVVM, MVI, Clean Architecture, Redux, modularization, feature modules, state management, unidirectional data flow, KMP, Kotlin Multiplatform, shared code, or designing scalable mobile app architecture for Android and iOS.
---

# Mobile Architecture

A production-grade skill for cross-platform mobile architecture covering patterns that apply to
both iOS (Swift/SwiftUI) and Android (Kotlin/Compose), plus Kotlin Multiplatform for shared logic.

## Quick Reference

| Area | Key Concepts | Reference File |
|------|-------------|----------------|
| Architecture Patterns | MVVM, Clean, MVI, Coordinator | `references/patterns.md` |
| State Management | UDF, Redux-like, state machines | `references/state-management.md` |
| Modularization & Feature Flags | Module structure, toggles, A/B testing | `references/modularization.md` |
| Kotlin Multiplatform (KMP) | Shared modules, expect/actual, architecture | `references/kmp.md` |

## Core Workflow

1. **Identify the concern:**
   - Architecture choice → Read `references/patterns.md`
   - State management → Read `references/state-management.md`
   - App structure / feature flags → Read `references/modularization.md`
   - Shared code iOS ↔ Android → Read `references/kmp.md`

2. **Consider both platforms** — Architecture decisions should work idiomatically on both iOS and
   Android. Avoid patterns that feel natural on one platform but alien on the other.

3. **Match complexity to scale:**
   - Small app (1-2 devs): MVVM + simple navigation
   - Medium app (3-6 devs): MVVM or MVI + Clean Architecture + basic modularization
   - Large app (7+ devs): Clean + multi-module + feature flags + possibly KMP

---

## Architecture Decision Framework

### Choosing an Architecture

| Factor | Recommendation |
|--------|---------------|
| Team < 3 devs | MVVM (simplest, well-supported on both platforms) |
| Complex UI state | MVI / UDF (predictable, debuggable state transitions) |
| Large team (5+ devs) | Clean Architecture (enforced layer separation) |
| Multiple feature teams | Multi-module + Clean (independent development) |
| Code sharing iOS ↔ Android | KMP + Clean Architecture (share domain layer) |
| Rapid prototyping | MV (Apple) or simple MVVM (minimal boilerplate) |

### The Golden Rule

> Architecture should reduce the cost of change, not increase it. If your architecture makes
> simple changes hard, it's wrong for your app — regardless of what the textbooks say.

### Platform-Idiomatic Mapping

| Concept | iOS (Swift) | Android (Kotlin) |
|---------|------------|-------------------|
| ViewModel | `@Observable` class | `ViewModel` (Jetpack) |
| State observation | `@State`, Combine | `StateFlow`, `collectAsStateWithLifecycle` |
| DI | Manual container or Swinject | Hilt / Koin |
| Navigation | `NavigationStack` + Coordinator | Navigation Component / Compose Navigation |
| Async | `async/await`, `Task` | Coroutines, `viewModelScope` |
| Reactive streams | Combine `Publisher` | Kotlin `Flow` |
| Persistence | SwiftData / Core Data | Room / DataStore |
| Networking | URLSession | Retrofit / Ktor |

---

## Cross-Platform Principles

These principles apply regardless of platform:

1. **Separation of concerns** — UI code doesn't contain business logic. Business logic
   doesn't know about the UI framework.

2. **Dependency inversion** — Depend on abstractions (protocols/interfaces), not concrete
   implementations. This enables testing and swappability.

3. **Single source of truth** — Each piece of state has exactly one owner. Other components
   observe or derive from it.

4. **Unidirectional data flow** — Data flows in one direction: State → View. User actions
   flow the other way: View → Action → State update.

5. **Immutable state** — State objects should be immutable (value types on iOS, `data class`
   on Android). Create new instances instead of mutating.

6. **Side effects at the edges** — Keep the core logic pure. Push I/O, network, and database
   operations to the boundaries (repositories, services).

7. **Test the logic, not the framework** — Business logic should be testable without any
   UI framework. If you need `@MainActor` or `Dispatchers.Main` in a test, something is wrong.

---

## Navigation Architecture

### Pattern Comparison

| Pattern | Best For | iOS | Android |
|---------|---------|-----|---------|
| **Stack-based** | Simple linear flows | `NavigationStack` | `NavHost` |
| **Coordinator** | Complex multi-flow apps | Custom coordinator | Navigation + nested graphs |
| **Tab + Stack** | Multi-section apps | `TabView` + `NavigationStack` | `Scaffold` + `NavHost` |
| **Deep linking** | External entry points | URL schemes + Universal Links | Intent filters + App Links |

### Deep Linking Architecture

```
URL → Router → Resolve destination → Navigate
         ↓
    Auth check → Login flow (if needed) → Resume navigation
```

Both platforms:
1. Register URL patterns (Universal Links on iOS, App Links on Android)
2. Parse URL into a typed route/destination
3. Check if user is authenticated (if route requires auth)
4. Navigate to the resolved screen with extracted parameters

---

## Best Practices

1. Mirror architecture decisions across iOS and Android — divergent architectures make
   cross-platform knowledge sharing impossible
2. Domain models should be identical across platforms (same fields, same naming)
3. API contracts (DTOs) should map to the same domain models on both platforms
4. Feature flags should use the same flag names and evaluation logic on both platforms
5. Use the same module/package naming conventions across platforms for easy mapping
6. Write architecture decision records (ADRs) for significant choices
7. Review architecture quarterly — what worked, what didn't, what to evolve



---
