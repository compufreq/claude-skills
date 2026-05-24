# State Management Reference

## Table of Contents
1. Unidirectional Data Flow (UDF)
2. Redux-Like Architecture
3. State Machines
4. Side Effect Management
5. State Restoration
6. Anti-Patterns

---

## 1. Unidirectional Data Flow (UDF)

The foundational principle: data flows in one direction.

```
┌──────────────────────────────────────────┐
│                                          │
│   State ──render──► View ──action──►     │
│     ▲                                │   │
│     │                                │   │
│     └──── reduce(state, action) ◄────┘   │
│                                          │
└──────────────────────────────────────────┘
```

### UDF Rules
1. The UI is a function of state: `UI = f(State)`
2. State is immutable — create a new instance for every change
3. Actions are the only way to trigger state changes
4. State changes are synchronous (side effects happen separately)
5. There is one canonical state for each screen

### State Design Guidelines

**State should be:**
- A single immutable object per screen/feature
- Contain everything the UI needs to render
- Serializable (for state restoration, debugging)
- Minimal — don't store derived data, compute it

**State should NOT contain:**
- Navigation events (use a separate effect channel)
- Transient UI state that doesn't survive rotation (toast visibility)
- References to platform objects (Context, UIViewController)

### State Composition

```
// Small app: single state per screen
data class ProfileState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val isEditing: Boolean = false,
)

// Large app: compose sub-states
data class HomeState(
    val feed: FeedState = FeedState(),
    val filters: FilterState = FilterState(),
    val search: SearchState = SearchState(),
)

data class FeedState(
    val items: List<FeedItem> = emptyList(),
    val isLoading: Boolean = false,
    val hasMore: Boolean = true,
)
```

---

## 2. Redux-Like Architecture

For apps with complex state that multiple components read and modify.

### Core Concepts

```
Action → Store.dispatch(action) → Reducer(state, action) → new State
                                         ↓
                                    Middleware (side effects)
```

| Concept | Definition |
|---------|-----------|
| **Store** | Holds the single source of truth (app state) |
| **Action** | Describes what happened (user tapped, data loaded) |
| **Reducer** | Pure function: `(State, Action) → State` |
| **Middleware** | Intercepts actions for side effects (API, analytics) |
| **Selector** | Derives view-specific data from state |

### Implementation Pattern (Platform-Agnostic)

```kotlin
// State
data class AppState(
    val auth: AuthState = AuthState(),
    val home: HomeState = HomeState(),
    val settings: SettingsState = SettingsState(),
)

// Actions
sealed interface AppAction {
    sealed interface Auth : AppAction {
        data class LoginSuccess(val user: User) : Auth
        data object Logout : Auth
        data class LoginFailed(val error: String) : Auth
    }
    sealed interface Home : AppAction {
        data class ItemsLoaded(val items: List<Item>) : Home
        data class ItemDeleted(val id: String) : Home
    }
}

// Reducer (pure function)
fun appReducer(state: AppState, action: AppAction): AppState = when (action) {
    is AppAction.Auth.LoginSuccess -> state.copy(
        auth = state.auth.copy(user = action.user, isLoggedIn = true)
    )
    is AppAction.Auth.Logout -> state.copy(
        auth = AuthState() // Reset to initial
    )
    is AppAction.Home.ItemsLoaded -> state.copy(
        home = state.home.copy(items = action.items, isLoading = false)
    )
    // ... exhaustive
}

// Store
class Store(
    initialState: AppState = AppState(),
    private val middlewares: List<Middleware> = emptyList(),
) {
    private val _state = MutableStateFlow(initialState)
    val state: StateFlow<AppState> = _state.asStateFlow()

    suspend fun dispatch(action: AppAction) {
        // Run middlewares
        middlewares.forEach { it.process(action, _state.value, ::dispatch) }
        // Reduce
        _state.update { appReducer(it, action) }
    }
}
```

### Selectors (Derived State)

```kotlin
// Don't expose the entire state to views — use selectors
val selectActiveUsers: (AppState) -> List<User> = { state ->
    state.home.users.filter { it.isActive }
}

val selectUnreadCount: (AppState) -> Int = { state ->
    state.notifications.items.count { !it.isRead }
}

// In ViewModel
class HomeViewModel(private val store: Store) : ViewModel() {
    val activeUsers = store.state
        .map(selectActiveUsers)
        .distinctUntilChanged()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
}
```

### When Redux Makes Sense
- Multiple screens read/write the same state
- Complex state transitions with many edge cases
- Need time-travel debugging or action replay
- Team is familiar with Redux concepts

### When Redux is Overkill
- Simple app with independent screens
- State is primarily screen-local
- Team doesn't know Redux patterns (steep learning curve)

---

## 3. State Machines

For states with strict, well-defined transitions (auth flows, payments, onboarding).

### Finite State Machine Pattern

```kotlin
sealed interface AuthMachineState {
    data object Unauthenticated : AuthMachineState
    data object Loading : AuthMachineState
    data class Authenticated(val user: User) : AuthMachineState
    data class Error(val message: String) : AuthMachineState
    data object TokenExpired : AuthMachineState
}

sealed interface AuthMachineEvent {
    data class Login(val email: String, val password: String) : AuthMachineEvent
    data object Logout : AuthMachineEvent
    data class LoginSuccess(val user: User) : AuthMachineEvent
    data class LoginFailed(val error: String) : AuthMachineEvent
    data object TokenRefreshFailed : AuthMachineEvent
    data object TokenRefreshed : AuthMachineEvent
}

// Valid transitions only
fun AuthMachineState.transition(event: AuthMachineEvent): AuthMachineState? = when (this) {
    is AuthMachineState.Unauthenticated -> when (event) {
        is AuthMachineEvent.Login -> AuthMachineState.Loading
        else -> null  // Invalid transition
    }
    is AuthMachineState.Loading -> when (event) {
        is AuthMachineEvent.LoginSuccess -> AuthMachineState.Authenticated(event.user)
        is AuthMachineEvent.LoginFailed -> AuthMachineState.Error(event.error)
        else -> null
    }
    is AuthMachineState.Authenticated -> when (event) {
        is AuthMachineEvent.Logout -> AuthMachineState.Unauthenticated
        is AuthMachineEvent.TokenRefreshFailed -> AuthMachineState.TokenExpired
        else -> null
    }
    is AuthMachineState.TokenExpired -> when (event) {
        is AuthMachineEvent.Login -> AuthMachineState.Loading
        is AuthMachineEvent.TokenRefreshed -> AuthMachineState.Authenticated((this as? AuthMachineState.Authenticated)?.user ?: return null)
        is AuthMachineEvent.Logout -> AuthMachineState.Unauthenticated
        else -> null
    }
    is AuthMachineState.Error -> when (event) {
        is AuthMachineEvent.Login -> AuthMachineState.Loading
        else -> null
    }
}
```

### Benefits of State Machines
- Impossible states are actually impossible (compile-time safety)
- Every valid transition is explicitly defined
- Easy to visualize and document
- Excellent for complex flows: auth, checkout, onboarding, media playback

---

## 4. Side Effect Management

Side effects are operations that interact with the outside world: API calls, database
operations, analytics, navigation.

### Categorizing Side Effects

| Category | Examples | Handling |
|----------|---------|---------|
| **Fire and forget** | Analytics, logging | Launch and don't await |
| **Result-producing** | API calls, DB queries | Await result, update state |
| **Long-running** | WebSocket, location updates | Collect flow, cancel on cleanup |
| **One-time** | Navigation, show toast | Channel/effect stream |

### Effect Pattern

```kotlin
// Separate effects from state
sealed interface Effect {
    data class Navigate(val route: Route) : Effect
    data class ShowSnackbar(val message: String) : Effect
    data class ShowDialog(val title: String, val message: String) : Effect
    data object HapticFeedback : Effect
}

// ViewModel emits effects through a channel
private val _effects = Channel<Effect>(Channel.BUFFERED)
val effects: Flow<Effect> = _effects.receiveAsFlow()

// View collects effects (one-time, not replayed)
LaunchedEffect(Unit) {
    viewModel.effects.collect { effect ->
        when (effect) {
            is Effect.Navigate -> navController.navigate(effect.route)
            is Effect.ShowSnackbar -> snackbarHostState.showSnackbar(effect.message)
            is Effect.ShowDialog -> { /* show dialog */ }
            is Effect.HapticFeedback -> { /* trigger haptic */ }
        }
    }
}
```

---

## 5. State Restoration

State must survive process death (Android) and scene disconnection (iOS).

### Android: SavedStateHandle
```kotlin
@HiltViewModel
class SearchViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle,
    private val repository: SearchRepository,
) : ViewModel() {
    val query = savedStateHandle.getStateFlow("query", "")

    fun updateQuery(newQuery: String) {
        savedStateHandle["query"] = newQuery
    }
}
```

### iOS: @SceneStorage / Codable state
```swift
// Simple values
@SceneStorage("selectedTab") private var selectedTab = 0

// Complex state — encode to JSON
@SceneStorage("searchState") private var searchStateData: Data?
var searchState: SearchState {
    get { searchStateData.flatMap { try? JSONDecoder().decode(SearchState.self, from: $0) } ?? .init() }
    set { searchStateData = try? JSONEncoder().encode(newValue) }
}
```

---

## 6. Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| God ViewModel | 500+ line ViewModel doing everything | Split into focused ViewModels or extract Use Cases |
| Bidirectional data flow | View modifies state directly | UDF: View sends actions, ViewModel updates state |
| State in multiple places | Same data in ViewModel and Fragment | Single source of truth (one StateFlow) |
| Derived state in state | Storing computed values | Use computed properties / selectors |
| Navigation in ViewModel | ViewModel imports UI navigation | Emit navigation effects, handle in View |
| Mutable state exposure | Exposing MutableStateFlow | Expose read-only StateFlow |
| Over-engineering | Redux for a todo app | Match complexity to app scale |
| Platform-specific state | Android-only state patterns in shared code | Abstract platform details behind interfaces |



---

<!-- Script: scripts/generate_architecture.py -->

# Script: generate_architecture.py

```python
#!/usr/bin/env python3
"""
Generate mobile architecture artifacts:
1. Architecture Decision Records (ADRs)
2. Module dependency diagrams (HTML/SVG)
3. Feature flag configuration templates
4. KMP shared module scaffolding

Usage:
    python generate_architecture.py --type adr --config arch.json --output adr.md
    python generate_architecture.py --type module-diagram --config arch.json --output modules.html
    python generate_architecture.py --type feature-flags --config arch.json --output flags.json
    python generate_architecture.py --type kmp-scaffold --config arch.json --output ./shared

Config JSON:
{
    "project_name": "MyApp",
    "package_name": "com.example.myapp",
    "architecture": "mvvm",
    "modules": [
        {"name": "app", "type": "app", "depends_on": ["feature-home", "feature-auth", "domain", "core-network", "core-ui"]},
        {"name": "feature-home", "type": "feature", "depends_on": ["domain", "core-ui", "core-network"]},
        {"name": "feature-auth", "type": "feature", "depends_on": ["domain", "core-ui", "core-network"]},
        {"name": "domain", "type": "domain", "depends_on": ["core-common"]},
        {"name": "core-network", "type": "core", "depends_on": ["core-common"]},
        {"name": "core-database", "type": "core", "depends_on": ["core-common"]},
        {"name": "core-ui", "type": "core", "depends_on": ["core-common"]},
        {"name": "core-common", "type": "core", "depends_on": []}
    ],
    "feature_flags": [
        {"key": "enable_new_checkout", "type": "boolean", "default": false, "description": "New checkout flow"},
        {"key": "max_upload_mb", "type": "integer", "default": 10, "description": "Max file upload size"}
    ],
    "kmp_shared_layers": ["domain", "data", "networking"],
    "adr": {
        "number": 1,
        "title": "Use MVVM architecture for mobile apps",
        "context": "We need to choose an architecture pattern for our new mobile app",
        "decision": "We will use MVVM with Clean Architecture layers",
        "alternatives": ["MVI", "VIPER", "MV (Apple)"],
        "consequences": ["Consistent pattern across iOS and Android", "Learning curve for VIPER developers"]
    }
}
"""

import json
import sys
import os
import argparse
from datetime import datetime


def generate_adr(config, output_path):
    """Generate an Architecture Decision Record."""
    adr = config.get("adr", {})
    number = adr.get("number", 1)
    title = adr.get("title", "Architecture Decision")
    project = config.get("project_name", "Project")

    alternatives = adr.get("alternatives", [])
    alt_section = ""
    if alternatives:
        alt_list = "\n".join(f"- **{a}** — Considered but not chosen" for a in alternatives)
        alt_section = f"\n## Alternatives Considered\n\n{alt_list}\n"

    consequences = adr.get("consequences", [])
    cons_section = ""
    if consequences:
        cons_list = "\n".join(f"- {c}" for c in consequences)
        cons_section = f"\n## Consequences\n\n{cons_list}\n"

    content = f"""# ADR-{number:04d}: {title}

**Status:** Accepted
**Date:** {datetime.now().strftime("%Y-%m-%d")}
**Project:** {project}
**Deciders:** [Team]

## Context

{adr.get("context", "Describe the context and problem statement.")}

## Decision

{adr.get("decision", "Describe the decision and rationale.")}
{alt_section}{cons_section}
## Rationale

Explain why this decision was made over the alternatives.

## Notes

- This ADR was created on {datetime.now().strftime("%Y-%m-%d")}.
- Review this decision after [timeframe] or when [trigger condition].
"""

    with open(output_path, "w") as f:
        f.write(content)
    print(f"ADR saved to: {output_path}")


def generate_module_diagram(config, output_path):
    """Generate an interactive module dependency diagram as HTML/SVG."""
    modules = config.get("modules", [])
    project = config.get("project_name", "Project")

    if not modules:
        print("No modules defined in config.")
        return

    # Layout: group by type
    type_colors = {
        "app": "#e94560",
        "feature": "#4CAF50",
        "domain": "#2196F3",
        "core": "#FF9800",
    }

    type_y = {"app": 50, "feature": 180, "domain": 310, "core": 440}

    # Position nodes
    positions = {}
    type_counts = {}
    for m in modules:
        t = m.get("type", "core")
        if t not in type_counts:
            type_counts[t] = 0
        type_counts[t] += 1

    type_indices = {}
    for m in modules:
        t = m.get("type", "core")
        if t not in type_indices:
            type_indices[t] = 0
        idx = type_indices[t]
        total = type_counts[t]
        x = 100 + (idx + 1) * (800 / (total + 1))
        y = type_y.get(t, 300)
        positions[m["name"]] = {"x": x, "y": y}
        type_indices[t] += 1

    # Generate SVG
    width = 950
    height = 550

    # Edges
    edges_svg = ""
    for m in modules:
        for dep in m.get("depends_on", []):
            if dep in positions:
                p1 = positions[m["name"]]
                p2 = positions[dep]
                edges_svg += f'<line x1="{p1["x"]}" y1="{p1["y"]}" x2="{p2["x"]}" y2="{p2["y"]}" stroke="#444" stroke-width="1.5" marker-end="url(#arrowhead)" />\n'

    # Nodes
    nodes_svg = ""
    for m in modules:
        pos = positions[m["name"]]
        color = type_colors.get(m.get("type", "core"), "#888")
        name = m["name"]
        short_name = name.replace("feature-", "").replace("core-", "")

        nodes_svg += f"""
        <g transform="translate({pos["x"]},{pos["y"]})">
            <rect x="-55" y="-22" width="110" height="44" rx="8" fill="#1a1a2e" stroke="{color}" stroke-width="2" />
            <text x="0" y="2" text-anchor="middle" fill="#eee" font-size="11" font-weight="600">{short_name}</text>
            <text x="0" y="14" text-anchor="middle" fill="{color}" font-size="8">{m.get("type", "")}</text>
        </g>"""

    # Legend
    legend = ""
    for i, (t, c) in enumerate(type_colors.items()):
        legend += f'<rect x="{20 + i * 120}" y="{height - 30}" width="12" height="12" rx="3" fill="{c}" />'
        legend += f'<text x="{38 + i * 120}" y="{height - 20}" fill="#aaa" font-size="11">{t.title()}</text>'

    html = f"""<!DOCTYPE html>
<html><head><title>{project} Module Diagram</title>
<style>
    body {{ font-family: -apple-system, sans-serif; background: #0f0f23; color: #eee; padding: 2rem; }}
    h1 {{ color: #e94560; font-size: 1.4rem; margin-bottom: 0.5rem; }}
    .subtitle {{ color: #888; margin-bottom: 1rem; font-size: 0.85rem; }}
    svg {{ background: #1a1a2e; border-radius: 12px; border: 1px solid #333; }}
    .stats {{ display: flex; gap: 2rem; margin-bottom: 1rem; font-size: 0.85rem; color: #aaa; }}
    .stats strong {{ color: #e94560; }}
</style>
</head><body>
    <h1>📦 {project} — Module Dependency Diagram</h1>
    <div class="subtitle">{len(modules)} modules | {sum(len(m.get("depends_on", [])) for m in modules)} dependencies</div>
    <div class="stats">
        <span>App: <strong>{type_counts.get("app", 0)}</strong></span>
        <span>Features: <strong>{type_counts.get("feature", 0)}</strong></span>
        <span>Domain: <strong>{type_counts.get("domain", 0)}</strong></span>
        <span>Core: <strong>{type_counts.get("core", 0)}</strong></span>
    </div>
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <defs>
            <marker id="arrowhead" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#444"/>
            </marker>
        </defs>
        {edges_svg}
        {nodes_svg}
        {legend}
    </svg>
</body></html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"Module diagram saved to: {output_path}")


def generate_feature_flags_template(config, output_path):
    """Generate a feature flags configuration template."""
    flags = config.get("feature_flags", [])
    project = config.get("project_name", "Project")

    output = {
        "project": project,
        "generated": datetime.now().isoformat(),
        "flags": {}
    }

    for flag in flags:
        output["flags"][flag["key"]] = {
            "type": flag.get("type", "boolean"),
            "default_value": flag.get("default", False),
            "description": flag.get("description", ""),
            "enabled_for": {
                "internal_testers": True,
                "beta_users": False,
                "production": False,
            },
            "rollout_percentage": 0,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "owner": "",
            "jira_ticket": "",
        }

    # Kotlin enum
    kotlin_enum = f"package {config.get('package_name', 'com.example')}.util\n\n"
    kotlin_enum += "enum class FeatureFlag(\n    val key: String,\n    val defaultValue: Any,\n    val description: String,\n) {\n"
    for flag in flags:
        default_val = str(flag.get("default", False)).lower() if flag.get("type") == "boolean" else str(flag.get("default", ""))
        if flag.get("type") == "string":
            default_val = f'"{default_val}"'
        kotlin_enum += f'    {flag["key"].upper()}("{flag["key"]}", {default_val}, "{flag.get("description", "")}"),\n'
    kotlin_enum += "}\n"

    # Swift enum
    swift_enum = "import Foundation\n\nenum FeatureFlag: String, CaseIterable {\n"
    for flag in flags:
        swift_case = flag["key"].replace("_", "")
        swift_case = swift_case[0].lower() + swift_case[1:]
        swift_enum += f'    case {swift_case} = "{flag["key"]}"\n'
    swift_enum += "\n    var defaultValue: Any {\n        switch self {\n"
    for flag in flags:
        swift_case = flag["key"].replace("_", "")
        swift_case = swift_case[0].lower() + swift_case[1:]
        default_val = str(flag.get("default", False)).lower() if flag.get("type") == "boolean" else str(flag.get("default", ""))
        if flag.get("type") == "string":
            default_val = f'"{default_val}"'
        swift_enum += f"        case .{swift_case}: return {default_val}\n"
    swift_enum += "        }\n    }\n}\n"

    # Write JSON config
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    # Write Kotlin file
    kotlin_path = output_path.replace(".json", "_android.kt")
    with open(kotlin_path, "w") as f:
        f.write(kotlin_enum)

    # Write Swift file
    swift_path = output_path.replace(".json", "_ios.swift")
    with open(swift_path, "w") as f:
        f.write(swift_enum)

    print(f"Feature flags config: {output_path}")
    print(f"Kotlin enum: {kotlin_path}")
    print(f"Swift enum: {swift_path}")


def generate_kmp_scaffold(config, output_path):
    """Generate KMP shared module scaffolding."""
    pkg = config.get("package_name", "com.example.shared")
    pkg_path = pkg.replace(".", "/")
    project = config.get("project_name", "shared")

    files = {
        f"src/commonMain/kotlin/{pkg_path}/domain/model/User.kt": f"""package {pkg}.domain.model

data class User(
    val id: String,
    val name: String,
    val email: String,
    val isActive: Boolean = true,
)
""",
        f"src/commonMain/kotlin/{pkg_path}/domain/repository/UserRepository.kt": f"""package {pkg}.domain.repository

import {pkg}.domain.model.User

interface UserRepository {{
    suspend fun getUsers(): List<User>
    suspend fun getUser(id: String): User
    suspend fun createUser(user: User): User
    suspend fun deleteUser(id: String)
}}
""",
        f"src/commonMain/kotlin/{pkg_path}/domain/usecase/GetUsersUseCase.kt": f"""package {pkg}.domain.usecase

import {pkg}.domain.model.User
import {pkg}.domain.repository.UserRepository

class GetUsersUseCase(private val repository: UserRepository) {{
    suspend operator fun invoke(): List<User> =
        repository.getUsers().filter {{ it.isActive }}.sortedBy {{ it.name }}
}}
""",
        f"src/commonMain/kotlin/{pkg_path}/data/remote/dto/UserDto.kt": f"""package {pkg}.data.remote.dto

import {pkg}.domain.model.User
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class UserDto(
    @SerialName("id") val id: String,
    @SerialName("full_name") val fullName: String,
    @SerialName("email") val email: String,
    @SerialName("is_active") val isActive: Boolean,
) {{
    fun toDomain(): User = User(id = id, name = fullName, email = email, isActive = isActive)
}}
""",
        f"src/commonMain/kotlin/{pkg_path}/util/Platform.kt": f"""package {pkg}.util

expect class Platform() {{
    val name: String
    val version: String
}}
""",
        f"src/androidMain/kotlin/{pkg_path}/util/Platform.android.kt": f"""package {pkg}.util

actual class Platform actual constructor() {{
    actual val name: String = "Android"
    actual val version: String = "${{android.os.Build.VERSION.SDK_INT}}"
}}
""",
        f"src/iosMain/kotlin/{pkg_path}/util/Platform.ios.kt": f"""package {pkg}.util

import platform.UIKit.UIDevice

actual class Platform actual constructor() {{
    actual val name: String = UIDevice.currentDevice.systemName
    actual val version: String = UIDevice.currentDevice.systemVersion
}}
""",
        f"src/commonTest/kotlin/{pkg_path}/domain/usecase/GetUsersUseCaseTest.kt": f"""package {pkg}.domain.usecase

import {pkg}.domain.model.User
import {pkg}.domain.repository.UserRepository
import kotlin.test.Test
import kotlin.test.assertEquals

class GetUsersUseCaseTest {{
    @Test
    fun `returns active users sorted by name`() {{
        // TODO: Implement with runTest
    }}
}}
""",
    }

    base = output_path
    print(f"\n📦 Scaffolding KMP shared module: {project}\n")
    for path, content in files.items():
        full_path = os.path.join(base, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        print(f"  Created: {full_path}")

    print(f"\n✅ KMP scaffold at: {base}")
    print(f"   Package: {pkg}")
    print(f"   Source sets: commonMain, androidMain, iosMain, commonTest")


GENERATORS = {
    "adr": generate_adr,
    "module-diagram": generate_module_diagram,
    "feature-flags": generate_feature_flags_template,
    "kmp-scaffold": generate_kmp_scaffold,
}


def main():
    parser = argparse.ArgumentParser(description="Generate Mobile Architecture Artifacts")
    parser.add_argument("--type", choices=GENERATORS.keys(), required=True)
    parser.add_argument("--config", help="JSON config path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    GENERATORS[args.type](config, args.output)


if __name__ == "__main__":
    main()

```
