# Architecture Patterns Reference

## Table of Contents
1. MVVM Cross-Platform
2. Clean Architecture Cross-Platform
3. MVI (Model-View-Intent) Cross-Platform
4. Coordinator / Router Pattern
5. Repository Pattern
6. Layered Architecture Rules

---

## 1. MVVM Cross-Platform

The most widely adopted mobile pattern. Works idiomatically on both platforms.

### Structure
```
View ←observes← ViewModel → Repository → DataSource (API / DB)
```

### iOS Implementation
```swift
@Observable @MainActor
final class UserListViewModel {
    private(set) var users: [User] = []
    private(set) var isLoading = false
    private(set) var error: AppError?

    private let repository: UserRepositoryProtocol

    init(repository: UserRepositoryProtocol) {
        self.repository = repository
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            users = try await repository.getUsers()
        } catch {
            self.error = .networkFailure(underlying: error)
        }
    }
}
```

### Android Implementation
```kotlin
@HiltViewModel
class UserListViewModel @Inject constructor(
    private val repository: UserRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(UserListState())
    val uiState: StateFlow<UserListState> = _uiState.asStateFlow()

    init { load() }

    private fun load() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            repository.getUsers()
                .catch { e -> _uiState.update { it.copy(isLoading = false, error = e.message) } }
                .collect { users -> _uiState.update { it.copy(isLoading = false, users = users) } }
        }
    }
}

data class UserListState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
)
```

### MVVM Rules (Both Platforms)
1. ViewModels expose **state** (observable properties) and **actions** (methods)
2. Views observe state and call actions — no business logic in views
3. ViewModels don't import UI frameworks (no SwiftUI, no Compose)
4. ViewModels receive dependencies via constructor injection
5. State should be **read-only** from the view's perspective

---

## 2. Clean Architecture Cross-Platform

### Layer Diagram
```
┌─────────────────────────────────────┐
│         Presentation Layer          │  SwiftUI Views / Compose Screens
│         ViewModels                  │  Platform-specific UI
├─────────────────────────────────────┤
│         Domain Layer                │  Use Cases, Entities
│         (Pure business logic)       │  Repository Interfaces
│         NO platform imports         │  Can be shared via KMP
├─────────────────────────────────────┤
│         Data Layer                  │  Repository Implementations
│         API clients, DAOs           │  DTOs, Entity mappers
│         Platform-specific I/O       │  Caching logic
└─────────────────────────────────────┘
```

### Dependency Rule
- **Presentation** depends on **Domain** only
- **Data** depends on **Domain** only
- **Domain** depends on **nothing** — it defines interfaces that Data implements
- Dependencies point inward (toward Domain)

### Use Case Pattern

A Use Case encapsulates a single business operation. It orchestrates repositories,
applies business rules, and returns results.

**iOS:**
```swift
struct GetActiveUsersUseCase {
    private let userRepository: UserRepositoryProtocol
    private let analytics: AnalyticsProtocol

    func execute() async throws -> [User] {
        let users = try await userRepository.getUsers()
        let active = users.filter { $0.isActive && !$0.isBanned }
        analytics.track(.activeUsersFetched(count: active.count))
        return active.sorted { $0.lastLoginDate > $1.lastLoginDate }
    }
}
```

**Android:**
```kotlin
class GetActiveUsersUseCase @Inject constructor(
    private val userRepository: UserRepository,
    private val analytics: AnalyticsTracker,
) {
    operator fun invoke(): Flow<List<User>> =
        userRepository.getUsers()
            .map { users ->
                users.filter { it.isActive && !it.isBanned }
                    .sortedByDescending { it.lastLoginDate }
            }
            .onEach { analytics.track(ActiveUsersFetched(it.size)) }
}
```

### When Use Cases Add Value
- Business logic shared across multiple ViewModels
- Complex orchestration involving multiple repositories
- Rules that need to be tested independently from the UI
- Analytics/tracking that should happen regardless of which screen triggers it

### When Use Cases Are Overkill
- Simple CRUD pass-through (just delegates to repository)
- Single-use logic only needed by one ViewModel
- In these cases, the ViewModel can call the repository directly

---

## 3. MVI (Model-View-Intent) Cross-Platform

### Structure
```
View → Intent (user action)
         ↓
      Reducer (pure function)
         ↓
      New State → View (re-render)
         ↓
      Side Effects (API calls, navigation)
```

### Generic MVI Base

**Concept (platform-agnostic):**
```
State: Immutable data class representing the entire screen state
Intent: Sealed type representing every possible user action
Reducer: (State, Intent) → State (pure function)
Effect: One-time events (navigation, toasts, dialogs)
```

**iOS:**
```swift
@Observable @MainActor
class MVIViewModel<State, Intent, Effect> {
    private(set) var state: State
    private let effectChannel = AsyncChannel<Effect>()
    var effects: AsyncStream<Effect> { effectChannel.stream }

    init(initialState: State) { self.state = initialState }

    func send(_ intent: Intent) {
        Task { await handle(intent) }
    }

    func handle(_ intent: Intent) async {
        // Override in subclass
    }

    func reduce(_ transform: (inout State) -> Void) {
        transform(&state)
    }

    func emit(_ effect: Effect) async {
        await effectChannel.send(effect)
    }
}
```

**Android:**
```kotlin
abstract class MVIViewModel<State, Intent, Effect>(
    initialState: State,
) : ViewModel() {
    private val _state = MutableStateFlow(initialState)
    val state: StateFlow<State> = _state.asStateFlow()

    private val _effects = Channel<Effect>(Channel.BUFFERED)
    val effects: Flow<Effect> = _effects.receiveAsFlow()

    fun send(intent: Intent) { viewModelScope.launch { handleIntent(intent) } }

    abstract suspend fun handleIntent(intent: Intent)

    protected fun reduce(block: State.() -> State) { _state.update(block) }
    protected suspend fun emit(effect: Effect) { _effects.send(effect) }
}
```

### MVI vs MVVM Decision

| Choose MVI when... | Choose MVVM when... |
|--------------------|--------------------|
| Complex state with many interdependencies | Simple, independent state properties |
| Need to track state history (undo/redo) | No need for state history |
| Multiple sources of state change | Straightforward user actions |
| Want exhaustive intent handling | Prefer simpler, less boilerplate |
| Debugging state transitions is critical | State is simple enough to reason about |

---

## 4. Coordinator / Router Pattern

Separates navigation logic from views and ViewModels.

### Why Coordinators?
- Views shouldn't know about other views
- ViewModels shouldn't trigger navigation directly
- Navigation logic is testable when separated
- Complex flows (onboarding, checkout) are manageable

### iOS Coordinator
```swift
@Observable
final class AppCoordinator {
    var navigationPath = NavigationPath()
    var presentedSheet: Sheet?
    var presentedFullScreen: FullScreen?

    enum Destination: Hashable {
        case userDetail(userId: String)
        case settings
        case editProfile
    }

    enum Sheet: Identifiable {
        case addItem
        case filter
        var id: Int { hashValue }
    }

    func navigate(to destination: Destination) { navigationPath.append(destination) }
    func pop() { navigationPath.removeLast() }
    func popToRoot() { navigationPath = NavigationPath() }
    func present(_ sheet: Sheet) { presentedSheet = sheet }
    func dismiss() { presentedSheet = nil }
}
```

### Android Navigation with Sealed Routes
```kotlin
sealed interface AppRoute {
    @Serializable data object Home : AppRoute
    @Serializable data class UserDetail(val userId: String) : AppRoute
    @Serializable data object Settings : AppRoute
    @Serializable data object EditProfile : AppRoute
}

// Navigation events from ViewModel
sealed interface NavigationEffect {
    data class Navigate(val route: AppRoute) : NavigationEffect
    data object PopBack : NavigationEffect
    data object PopToRoot : NavigationEffect
}
```

---

## 5. Repository Pattern

The repository is the single source of truth for data. It abstracts the data source
(network, database, cache) from the rest of the app.

### Interface (shared concept)
```
interface UserRepository {
    fun getUsers(): Flow<List<User>>       // Stream of users (live updates)
    suspend fun getUser(id: String): User  // Single user
    suspend fun createUser(user: User)     // Create
    suspend fun updateUser(user: User)     // Update
    suspend fun deleteUser(id: String)     // Delete
    suspend fun sync()                     // Force refresh from remote
}
```

### Implementation Strategy
```
getUsers() {
    1. Return local database flow (immediate data)
    2. Fetch from API in background
    3. Update local database
    4. Flow automatically emits updated data
}

getUser(id) {
    1. Try local cache
    2. If miss, fetch from API
    3. Store in local cache/db
    4. Return
}
```

### Offline-First Decision Tree
```
Does the user need this data offline?
├── Yes → Cache in local database (Room / SwiftData)
│         ├── Is the data frequently updated? → Sync strategy (background refresh)
│         └── Is the data large? → Paginate and cache incrementally
└── No → In-memory cache (with TTL) or no cache
```

---

## 6. Layered Architecture Rules

### What Goes Where

| Layer | Contains | Does NOT Contain |
|-------|---------|-----------------|
| **Presentation** | Views, ViewModels, UI models, formatters | Business rules, API calls, DB queries |
| **Domain** | Use Cases, entities, repository interfaces, business rules | UI code, framework imports, DTOs |
| **Data** | Repository implementations, API services, DAOs, DTOs, mappers | UI code, business rules |

### Mapping Between Layers

```
API Response (DTO) → Data Layer mapper → Domain Entity → Presentation formatter → UI Model

Example:
UserDto { "full_name": "Alice Smith", "created_at": "2025-01-15T10:00:00Z" }
    ↓ mapper
User(name: "Alice Smith", createdAt: Date(...))
    ↓ formatter
UserDisplayModel(name: "Alice Smith", joinDate: "Jan 15, 2025", initials: "AS")
```

### Testing by Layer

| Layer | Test Type | What to Mock |
|-------|----------|-------------|
| Presentation (ViewModel) | Unit test | Repository / Use Case |
| Domain (Use Case) | Unit test | Repository interface |
| Data (Repository) | Unit + Integration | API client, DAO |
| Data (API) | Integration | Mock server (WireMock, MockWebServer) |
| UI | UI test / Snapshot | ViewModel (inject fake) |



---
