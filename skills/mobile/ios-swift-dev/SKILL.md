---
name: ios-swift-dev
description: >-
  iOS development with Swift, SwiftUI, UIKit, Combine, async/await, and App Store submission. Use when the user mentions iOS, Swift, SwiftUI, UIKit, Storyboard, Combine, async/await, CoreData, URLSession, Alamofire, SPM, CocoaPods, Xcode, MVVM, MVC, VIPER, App Store Connect, TestFlight, provisioning profile, code signing, or building iPhone/iPad apps. Trigger even without saying "iOS" if describing Swift mobile development with Xcode or Apple's frameworks.
---

# iOS Swift Development

A production-grade skill for native iOS development with Swift 5.9+, SwiftUI, UIKit, and the
Apple ecosystem. Covers architecture, networking, persistence, reactive programming, and
App Store submission.

## Quick Reference

| Area | Key Technologies | Reference File |
|------|-----------------|----------------|
| UI Development | SwiftUI, UIKit, Hybrid | `references/swiftui-uikit.md` |
| Architecture | MVVM, TCA, Clean/VIPER, MV | `references/architecture.md` |
| Networking | URLSession, async/await, Combine | `references/networking-data.md` |
| Data Persistence | Core Data, SwiftData, UserDefaults | `references/networking-data.md` |
| Reactive Programming | Combine, RxSwift | `references/reactive.md` |
| App Store | Review guidelines, submission, metadata | `references/app-store.md` |

## Core Workflow

1. **Identify the request type:**
   - UI building → Read `references/swiftui-uikit.md`
   - Project structure / architecture → Read `references/architecture.md`
   - API calls / data layer → Read `references/networking-data.md`
   - Reactive patterns → Read `references/reactive.md`
   - App Store / distribution → Read `references/app-store.md`

2. **Identify deployment target** — If not stated, default to iOS 17+ for new projects
   (SwiftUI-first). For enterprise/legacy, ask about minimum target.

3. **Apply the right architecture** — Default to MVVM for most apps. Suggest TCA for
   complex state management, Clean/VIPER for large teams, MV for simple apps.

4. **Generate code** following Apple's conventions and Swift style guide.

---

## Project Structure

### Recommended File Organization (MVVM)

```
MyApp/
├── App/
│   ├── MyApp.swift                 // @main App entry point
│   ├── AppDelegate.swift           // UIKit lifecycle (if needed)
│   └── ContentView.swift           // Root view
├── Features/
│   ├── Auth/
│   │   ├── Views/
│   │   │   ├── LoginView.swift
│   │   │   └── SignUpView.swift
│   │   ├── ViewModels/
│   │   │   └── AuthViewModel.swift
│   │   └── Models/
│   │       └── User.swift
│   ├── Home/
│   │   ├── Views/
│   │   ├── ViewModels/
│   │   └── Models/
│   └── Settings/
├── Core/
│   ├── Networking/
│   │   ├── APIClient.swift
│   │   ├── Endpoint.swift
│   │   └── NetworkError.swift
│   ├── Persistence/
│   │   ├── CoreDataStack.swift     // or SwiftDataContainer
│   │   └── UserDefaultsManager.swift
│   ├── Services/
│   │   ├── AuthService.swift
│   │   └── AnalyticsService.swift
│   └── Extensions/
│       ├── View+Extensions.swift
│       └── Date+Extensions.swift
├── Shared/
│   ├── Components/
│   │   ├── LoadingView.swift
│   │   ├── ErrorView.swift
│   │   └── PrimaryButton.swift
│   ├── Modifiers/
│   │   └── CardModifier.swift
│   └── Resources/
│       ├── Assets.xcassets
│       ├── Localizable.xcstrings
│       └── Colors.swift
├── Tests/
│   ├── UnitTests/
│   └── UITests/
└── MyApp.xcodeproj
```

### Recommended File Organization (Clean Architecture)

```
MyApp/
├── App/
│   └── MyApp.swift
├── Domain/                         // Business logic (no UIKit/SwiftUI imports)
│   ├── Entities/
│   │   └── User.swift
│   ├── UseCases/
│   │   ├── LoginUseCase.swift
│   │   └── FetchProfileUseCase.swift
│   └── Repositories/              // Protocols only
│       └── UserRepositoryProtocol.swift
├── Data/                           // Repository implementations
│   ├── Repositories/
│   │   └── UserRepository.swift
│   ├── Network/
│   │   ├── APIClient.swift
│   │   └── DTOs/
│   │       └── UserDTO.swift
│   └── Persistence/
│       └── CoreDataUserStore.swift
├── Presentation/                   // UI layer
│   ├── Auth/
│   │   ├── LoginView.swift
│   │   └── LoginViewModel.swift
│   └── Home/
├── DI/                             // Dependency injection
│   └── Container.swift
└── Tests/
```

---

## Swift Conventions

### Naming
- Types & protocols: `UpperCamelCase` — `UserProfile`, `Fetchable`
- Functions, variables, parameters: `lowerCamelCase` — `fetchUser()`, `userName`
- Constants: `lowerCamelCase` — `let maxRetryCount = 3`
- Enums cases: `lowerCamelCase` — `case loading`, `case loaded(Data)`
- Boolean properties: Read as assertions — `isLoading`, `hasContent`, `canSubmit`

### Swift Style
- Prefer `let` over `var` — immutability by default
- Use `guard` for early returns: `guard let user = user else { return }`
- Use `async/await` over completion handlers for new code
- Prefer value types (`struct`, `enum`) over reference types (`class`) where possible
- Use `@Observable` (iOS 17+) over `ObservableObject` for view models
- Use Swift concurrency (`Task`, `actor`, `async let`) over GCD
- Mark classes as `final` unless designed for inheritance
- Use `private` / `private(set)` to restrict access by default

### Error Handling Pattern
```swift
enum AppError: LocalizedError {
    case networkFailure(underlying: Error)
    case decodingFailure
    case unauthorized
    case notFound
    case serverError(statusCode: Int)
    
    var errorDescription: String? {
        switch self {
        case .networkFailure(let error): "Network error: \(error.localizedDescription)"
        case .decodingFailure: "Failed to process server response"
        case .unauthorized: "Please sign in again"
        case .notFound: "The requested resource was not found"
        case .serverError(let code): "Server error (\(code))"
        }
    }
}
```

---

## Key Patterns

### View Model Pattern (iOS 17+ with @Observable)
```swift
@Observable
final class HomeViewModel {
    private(set) var items: [Item] = []
    private(set) var isLoading = false
    private(set) var error: AppError?
    
    private let repository: ItemRepositoryProtocol
    
    init(repository: ItemRepositoryProtocol) {
        self.repository = repository
    }
    
    func loadItems() async {
        isLoading = true
        error = nil
        do {
            items = try await repository.fetchItems()
        } catch {
            self.error = .networkFailure(underlying: error)
        }
        isLoading = false
    }
}
```

### View Pattern (SwiftUI)
```swift
struct HomeView: View {
    @State private var viewModel: HomeViewModel
    
    init(repository: ItemRepositoryProtocol) {
        _viewModel = State(initialValue: HomeViewModel(repository: repository))
    }
    
    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else if let error = viewModel.error {
                ErrorView(error: error, retry: { Task { await viewModel.loadItems() } })
            } else {
                List(viewModel.items) { item in
                    ItemRow(item: item)
                }
            }
        }
        .task { await viewModel.loadItems() }
        .navigationTitle("Home")
    }
}
```

### Dependency Injection
```swift
// Protocol
protocol ItemRepositoryProtocol: Sendable {
    func fetchItems() async throws -> [Item]
}

// Implementation
final class ItemRepository: ItemRepositoryProtocol {
    private let apiClient: APIClient
    
    init(apiClient: APIClient) {
        self.apiClient = apiClient
    }
    
    func fetchItems() async throws -> [Item] {
        try await apiClient.request(.items)
    }
}

// Container
@Observable
final class AppContainer {
    let apiClient = APIClient()
    lazy var itemRepository: ItemRepositoryProtocol = ItemRepository(apiClient: apiClient)
}
```

---

## Testing Strategy

### Unit Tests
- Test ViewModels with mocked repositories
- Test business logic (use cases, models, transformations)
- Test networking with URLProtocol mocking
- Aim for 70%+ coverage on business logic

### UI Tests
- Test critical user flows (login, onboarding, main features)
- Use accessibility identifiers for reliable element lookup
- Keep UI tests fast — mock the network layer

### Snapshot Tests
- Use swift-snapshot-testing for visual regression
- Capture screenshots for multiple device sizes and appearances (light/dark)

---

## Best Practices

1. Use `@MainActor` on ViewModels and UI-bound code
2. Prefer SwiftUI for new screens; use UIKit via `UIViewRepresentable` when needed
3. Use `NavigationStack` (iOS 16+) over `NavigationView`
4. Handle all loading states: idle, loading, loaded, error
5. Support Dynamic Type, Dark Mode, and VoiceOver from day one
6. Use `Localizable.xcstrings` for all user-facing strings
7. Profile with Instruments before optimizing — measure, don't guess
8. Use Swift Package Manager over CocoaPods for new dependencies
9. Enable strict concurrency checking in Xcode build settings
10. Follow Apple Human Interface Guidelines for platform consistency



---
