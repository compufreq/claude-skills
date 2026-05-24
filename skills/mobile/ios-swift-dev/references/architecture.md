# iOS Architecture Patterns Reference

## Table of Contents
1. MVVM (Model-View-ViewModel)
2. MV (Model-View — Apple's pattern)
3. TCA (The Composable Architecture)
4. Clean Architecture / VIPER
5. Choosing the Right Architecture
6. Dependency Injection

---

## 1. MVVM (Model-View-ViewModel)

The most common iOS architecture. Views observe ViewModels, which transform Model data.

```
View ←→ ViewModel → Model / Service
  |         |
  |    Business Logic
  |    State Management
  |    Data Transformation
  |
UI Only (SwiftUI/UIKit)
```

### Implementation (iOS 17+ with @Observable)

```swift
// Model
struct Task: Identifiable, Codable {
    let id: UUID
    var title: String
    var isCompleted: Bool
    var dueDate: Date?
}

// ViewModel
@Observable
@MainActor
final class TaskListViewModel {
    private(set) var tasks: [Task] = []
    private(set) var isLoading = false
    private(set) var error: AppError?
    
    var completedCount: Int { tasks.filter(\.isCompleted).count }
    var pendingTasks: [Task] { tasks.filter { !$0.isCompleted } }
    
    private let repository: TaskRepositoryProtocol
    
    init(repository: TaskRepositoryProtocol) {
        self.repository = repository
    }
    
    func loadTasks() async {
        isLoading = true
        defer { isLoading = false }
        do {
            tasks = try await repository.fetchAll()
        } catch {
            self.error = .networkFailure(underlying: error)
        }
    }
    
    func toggleCompletion(_ task: Task) async {
        guard let index = tasks.firstIndex(where: { $0.id == task.id }) else { return }
        tasks[index].isCompleted.toggle()
        do {
            try await repository.update(tasks[index])
        } catch {
            tasks[index].isCompleted.toggle() // Revert
            self.error = .networkFailure(underlying: error)
        }
    }
    
    func delete(_ task: Task) async {
        tasks.removeAll { $0.id == task.id }
        do {
            try await repository.delete(task.id)
        } catch {
            self.error = .networkFailure(underlying: error)
        }
    }
}

// View
struct TaskListView: View {
    @State private var viewModel: TaskListViewModel
    
    init(repository: TaskRepositoryProtocol) {
        _viewModel = State(initialValue: TaskListViewModel(repository: repository))
    }
    
    var body: some View {
        List {
            ForEach(viewModel.tasks) { task in
                TaskRow(task: task, onToggle: { Task { await viewModel.toggleCompletion(task) } })
            }
            .onDelete { indexSet in
                for index in indexSet {
                    Task { await viewModel.delete(viewModel.tasks[index]) }
                }
            }
        }
        .overlay { if viewModel.isLoading { ProgressView() } }
        .task { await viewModel.loadTasks() }
        .refreshable { await viewModel.loadTasks() }
        .navigationTitle("Tasks (\(viewModel.completedCount)/\(viewModel.tasks.count))")
    }
}
```

### MVVM Rules
1. Views don't contain business logic — only layout and display
2. ViewModels don't import SwiftUI (except for `@Observable` / `@MainActor`)
3. ViewModels expose computed properties for derived state
4. ViewModels expose methods for user actions
5. Models are plain data (structs, Codable, Identifiable)
6. Services/Repositories are injected via protocols

---

## 2. MV (Model-View — Apple's Pattern)

Apple's simpler approach for iOS 17+. Models are `@Observable` and views observe them directly.
No ViewModel layer — the model IS the observable.

```swift
@Observable
final class TaskStore {
    var tasks: [Task] = []
    var isLoading = false
    
    private let apiClient: APIClient
    
    init(apiClient: APIClient = .shared) {
        self.apiClient = apiClient
    }
    
    func load() async throws {
        isLoading = true
        defer { isLoading = false }
        tasks = try await apiClient.request(.tasks)
    }
}

struct TaskListView: View {
    @State private var store = TaskStore()
    
    var body: some View {
        List(store.tasks) { task in
            Text(task.title)
        }
        .task { try? await store.load() }
    }
}
```

**When to use MV:** Small to medium apps where a separate ViewModel layer adds complexity
without benefit. Works well when models are straightforward and don't need heavy transformation.

---

## 3. TCA (The Composable Architecture)

Point-Free's architecture for complex state management. Unidirectional data flow with
composable, testable reducers.

```
View → Action → Reducer → State (back to View)
                   ↓
               Effect (side effects)
```

### Core Concepts

```swift
import ComposableArchitecture

// Feature
@Reducer
struct TaskListFeature {
    @ObservableState
    struct State: Equatable {
        var tasks: [Task] = []
        var isLoading = false
        @Presents var alert: AlertState<Action.Alert>?
    }
    
    enum Action {
        case onAppear
        case tasksLoaded(Result<[Task], Error>)
        case toggleTask(Task)
        case deleteTask(IndexSet)
        case alert(PresentationAction<Alert>)
        
        enum Alert: Equatable {
            case confirmDelete(Task)
        }
    }
    
    @Dependency(\.taskClient) var taskClient
    
    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .onAppear:
                state.isLoading = true
                return .run { send in
                    let result = await Result { try await taskClient.fetchAll() }
                    await send(.tasksLoaded(result))
                }
                
            case .tasksLoaded(.success(let tasks)):
                state.isLoading = false
                state.tasks = tasks
                return .none
                
            case .tasksLoaded(.failure):
                state.isLoading = false
                state.alert = AlertState { TextState("Failed to load tasks") }
                return .none
                
            case .toggleTask(let task):
                guard let index = state.tasks.firstIndex(where: { $0.id == task.id }) else { return .none }
                state.tasks[index].isCompleted.toggle()
                return .run { [task = state.tasks[index]] _ in
                    try await taskClient.update(task)
                }
                
            case .deleteTask(let indexSet):
                state.tasks.remove(atOffsets: indexSet)
                return .none
                
            case .alert:
                return .none
            }
        }
        .ifLet(\.$alert, action: \.alert)
    }
}

// View
struct TaskListView: View {
    @Bindable var store: StoreOf<TaskListFeature>
    
    var body: some View {
        List {
            ForEach(store.tasks) { task in
                TaskRow(task: task) { store.send(.toggleTask(task)) }
            }
            .onDelete { store.send(.deleteTask($0)) }
        }
        .onAppear { store.send(.onAppear) }
        .alert($store.scope(state: \.alert, action: \.alert))
    }
}
```

### TCA Benefits
- **Testable**: Reducers are pure functions, easy to test
- **Composable**: Features can be composed from smaller features
- **Side effect management**: Effects are explicit and controllable
- **Time-travel debugging**: State changes are trackable

### TCA Trade-offs
- Steep learning curve
- Verbose boilerplate for simple features
- Third-party dependency (swift-composable-architecture)
- Performance overhead for very simple apps

---

## 4. Clean Architecture / VIPER

Separates concerns into distinct layers with strict dependency rules.

```
Presentation → Domain ← Data
     ↓            ↓        ↓
  Views       Use Cases   Repos
  ViewModels  Entities    API/DB
  Routers     Protocols   DTOs
```

**Dependency Rule:** Inner layers know nothing about outer layers. Domain has no framework imports.

### VIPER Components

| Component | Responsibility |
|-----------|---------------|
| **V**iew | Display data, capture user input |
| **I**nteractor | Business logic (use cases) |
| **P**resenter | Transform data for display, handle view events |
| **E**ntity | Data models |
| **R**outer | Navigation logic |

### Clean Architecture Implementation

```swift
// Domain Layer — no UIKit/SwiftUI imports
protocol UserRepositoryProtocol {
    func fetchUser(id: String) async throws -> User
    func updateUser(_ user: User) async throws
}

struct FetchUserProfileUseCase {
    private let userRepository: UserRepositoryProtocol
    private let analyticsService: AnalyticsServiceProtocol
    
    init(userRepository: UserRepositoryProtocol, analyticsService: AnalyticsServiceProtocol) {
        self.userRepository = userRepository
        self.analyticsService = analyticsService
    }
    
    func execute(userId: String) async throws -> UserProfile {
        let user = try await userRepository.fetchUser(id: userId)
        analyticsService.track(.profileViewed(userId: userId))
        return UserProfile(from: user) // Domain transformation
    }
}

// Data Layer
struct UserRepository: UserRepositoryProtocol {
    private let apiClient: APIClient
    private let cache: UserCache
    
    func fetchUser(id: String) async throws -> User {
        if let cached = cache.get(id: id) { return cached }
        let dto: UserDTO = try await apiClient.request(.user(id: id))
        let user = dto.toDomain() // DTO → Domain mapping
        cache.set(user)
        return user
    }
}

// Presentation Layer
@Observable @MainActor
final class ProfileViewModel {
    private(set) var profile: UserProfile?
    private(set) var isLoading = false
    
    private let fetchProfileUseCase: FetchUserProfileUseCase
    
    init(fetchProfileUseCase: FetchUserProfileUseCase) {
        self.fetchProfileUseCase = fetchProfileUseCase
    }
    
    func loadProfile(userId: String) async {
        isLoading = true
        defer { isLoading = false }
        profile = try? await fetchProfileUseCase.execute(userId: userId)
    }
}
```

---

## 5. Choosing the Right Architecture

| Criteria | MV | MVVM | TCA | Clean/VIPER |
|----------|-----|------|-----|-------------|
| Team size | 1-2 devs | 2-5 devs | 3-8 devs | 5+ devs |
| App complexity | Simple | Medium | Complex | Large/Enterprise |
| Learning curve | Low | Low-Medium | High | High |
| Testability | Fair | Good | Excellent | Excellent |
| Boilerplate | Minimal | Moderate | Significant | Significant |
| SwiftUI fit | Excellent | Excellent | Good | Fair |
| UIKit fit | N/A | Good | Good | Excellent |
| Best for | Prototypes, small apps | Most apps | Complex state, many features | Large teams, long-lived apps |

### Migration Path
```
MV (start simple) → MVVM (add ViewModels when needed) → Clean (if team/app grows)
                   → TCA (if state management becomes complex)
```

---

## 6. Dependency Injection

### Simple Container (no framework)

```swift
@Observable
final class AppContainer {
    // Singletons
    private(set) lazy var apiClient = APIClient(baseURL: Config.apiBaseURL)
    private(set) lazy var coreDataStack = CoreDataStack()
    
    // Factories
    func makeAuthViewModel() -> AuthViewModel {
        AuthViewModel(authService: AuthService(apiClient: apiClient))
    }
    
    func makeHomeViewModel() -> HomeViewModel {
        HomeViewModel(repository: ItemRepository(apiClient: apiClient, store: coreDataStack))
    }
}

// Usage in App
@main
struct MyApp: App {
    @State private var container = AppContainer()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(container)
        }
    }
}
```

### Protocol-Based Injection

```swift
// Define protocol
protocol NetworkServiceProtocol: Sendable {
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}

// Production implementation
final class NetworkService: NetworkServiceProtocol { /* real network calls */ }

// Mock for testing
final class MockNetworkService: NetworkServiceProtocol {
    var mockResult: Any?
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        guard let result = mockResult as? T else { throw AppError.decodingFailure }
        return result
    }
}
```

### Swift Testing with DI
```swift
import Testing

@Suite("TaskListViewModel Tests")
struct TaskListViewModelTests {
    @Test("loads tasks successfully")
    func loadTasks() async {
        let mockRepo = MockTaskRepository(tasks: [.sample])
        let viewModel = TaskListViewModel(repository: mockRepo)
        
        await viewModel.loadTasks()
        
        #expect(viewModel.tasks.count == 1)
        #expect(viewModel.isLoading == false)
        #expect(viewModel.error == nil)
    }
    
    @Test("handles load failure")
    func loadTasksFailure() async {
        let mockRepo = MockTaskRepository(error: .networkFailure(underlying: URLError(.notConnectedToInternet)))
        let viewModel = TaskListViewModel(repository: mockRepo)
        
        await viewModel.loadTasks()
        
        #expect(viewModel.tasks.isEmpty)
        #expect(viewModel.error != nil)
    }
}
```



---
